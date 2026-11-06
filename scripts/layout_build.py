#!/usr/bin/env python3
"""Build the PCB from the schematic: footprints, nets, outline, 4-layer stackup and a scripted trial placement.

    python3 -I scripts/layout_build.py v1      # hardware/lcec-io-v1.kicad_pcb  (260 x 160 mm, single terminal row)
    python3 -I scripts/layout_build.py v2      # hardware/lcec-io-v2.kicad_pcb  (220 x 140 mm, stacked terminals)

Uses KiCad's own Python module (pcbnew). Footprints come from lib/lcsc.pretty and KiCad's standard libraries, nets from the netlist that
kicad-cli exports from the schematic, so the board always matches the schematic. Placement is a scripted first pass for review, not routed.
"""
import math
import os
import subprocess
import sys
import tempfile

import pcbnew
from pcbnew import FromMM, VECTOR2I

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import schgen as G  # noqa: E402

STD_FP = os.environ.get("KICAD10_FOOTPRINT_DIR", "/usr/share/kicad/footprints")
SCH = os.path.join(ROOT, "hardware", "lcec-io.kicad_sch")


def mm(v):
    return FromMM(v)


def read_netlist():
    out = os.path.join(tempfile.mkdtemp(), "n.net")
    subprocess.run(["kicad-cli", "sch", "export", "netlist", "--format", "kicadsexpr", "-o", out, SCH], check=True, capture_output=True)
    tree, _ = G.parse(G.tokenize(open(out).read()))
    comps = {}
    for c in G.find(G.find(tree, "components")[0], "comp"):
        ref = G.unq(G.find(c, "ref")[0][1])
        fp = G.unq(G.find(c, "footprint")[0][1]) if G.find(c, "footprint") else ""
        val = G.unq(G.find(c, "value")[0][1])
        comps[ref] = dict(fp=fp, value=val)
    nets = {}
    for n in G.find(G.find(tree, "nets")[0], "net"):
        name = G.unq(G.find(n, "name")[0][1])
        nets[name] = [(G.unq(G.find(nd, "ref")[0][1]), G.unq(G.find(nd, "pin")[0][1])) for nd in G.find(n, "node")]
    return comps, nets


def load_fp(libid):
    lib, name = libid.split(":", 1)
    path = os.path.join(ROOT, "lib", "lcsc.pretty") if lib == "lcsc" else os.path.join(STD_FP, lib + ".pretty")
    fp = pcbnew.FootprintLoad(path, name)
    if fp is None:
        raise SystemExit(f"footprint {libid} not found")
    return fp


def build_board():
    comps, nets = read_netlist()
    board = pcbnew.BOARD()
    board.SetCopperLayerCount(4)
    netitems = {}
    for name in nets:
        it = pcbnew.NETINFO_ITEM(board, name)
        board.Add(it)
        netitems[name] = it
    pinnet = {}
    for name, nodes in nets.items():
        for ref, pin in nodes:
            pinnet[(ref, pin)] = name
    fps = {}
    for ref, c in sorted(comps.items()):
        if not c["fp"] or ref.startswith("#"):
            continue
        fp = load_fp(c["fp"])
        fp.SetReference(ref)
        fp.SetValue(c["value"])
        for pad in fp.Pads():
            n = pinnet.get((ref, pad.GetNumber()))
            if n:
                pad.SetNet(netitems[n])
        pads = {pd.GetNumber(): pd for pd in fp.Pads()}
        if "65" in pads and pads["65"].GetNet() is not None and ref == "U401":         # thermal vias under the exposed pad join its net
            for pd in fp.Pads():
                if pd.GetNumber() == "":
                    pd.SetNet(pads["65"].GetNet())
        board.Add(fp)
        fps[ref] = fp
    return board, fps, comps, nets, pinnet


# ------------------------------------------------------------------ geometry helpers
def bbox_mm(fp):
    """(x1, y1, x2, y2) of the courtyard (or the pads and body when there is none) in mm."""
    bb = fp.GetBoundingBox(False)                  # pads, courtyard and drawings; the imported courtyards are sometimes smaller than the pads
    return (pcbnew.ToMM(bb.GetLeft()), pcbnew.ToMM(bb.GetTop()), pcbnew.ToMM(bb.GetRight()), pcbnew.ToMM(bb.GetBottom()))


def put(fp, cx, cy, rot=0):
    """Rotate and move so the centre of the courtyard is at (cx, cy) mm."""
    fp.SetOrientationDegrees(rot)
    fp.SetPosition(VECTOR2I(0, 0))
    x1, y1, x2, y2 = bbox_mm(fp)
    fp.SetPosition(VECTOR2I(mm(cx - (x1 + x2) / 2), mm(cy - (y1 + y2) / 2)))


def pad_side(fp, pin, rot):
    """Where pad `pin` ends up relative to the courtyard centre for this rotation: (dx, dy) in mm."""
    fp.SetOrientationDegrees(rot)
    fp.SetPosition(VECTOR2I(0, 0))
    x1, y1, x2, y2 = bbox_mm(fp)
    for pad in fp.Pads():
        if pad.GetNumber() == str(pin):
            p = pad.GetPosition()
            return pcbnew.ToMM(p.x) - (x1 + x2) / 2, pcbnew.ToMM(p.y) - (y1 + y2) / 2
    raise KeyError(pin)


def place_with_pin(fp, cx, cy, pin, side):
    """Pick the rotation (0/90/180/270) that puts pad `pin` on the given side ('left', 'right', 'top', 'bottom') and place there."""
    best = None
    for rot in (0, 90, 180, 270):
        dx, dy = pad_side(fp, pin, rot)
        score = {"left": -dx, "right": dx, "top": -dy, "bottom": dy}[side]
        if best is None or score > best[0] + 1e-6:
            best = (score, rot)
    put(fp, cx, cy, best[1])
    return best[1]


class Layout:
    def __init__(self, fps, pinnet, nets, W, H, regions):
        self.fps, self.pinnet, self.nets, self.W, self.H, self.regions = fps, pinnet, nets, W, H, regions
        self.occ = []                      # occupied rectangles with margin
        self.placed = set()

    def rect(self, fp, margin=0.3):
        x1, y1, x2, y2 = bbox_mm(fp)
        return (x1 - margin, y1 - margin, x2 + margin, y2 + margin)

    def anchor(self, ref, cx, cy, rot=0, pin=None, side=None):
        fp = self.fps[ref]
        if pin:
            place_with_pin(fp, cx, cy, pin, side)
        else:
            put(fp, cx, cy, rot)
        self.occ.append(self.rect(fp))
        self.placed.add(ref)

    def free(self, r, region):
        x1, y1, x2, y2 = r
        rx1, ry1, rx2, ry2 = region
        if x1 < rx1 or y1 < ry1 or x2 > rx2 or y2 > ry2:
            return False
        return all(x2 <= o[0] or x1 >= o[2] or y2 <= o[1] or y1 >= o[3] for o in self.occ)

    def auto(self, ref, target, region, rot=0, quiet=True):
        """Put the part at the free position nearest to target (x, y) inside region, searching outward in a spiral."""
        fp = self.fps[ref]
        put(fp, target[0], target[1], rot)
        x1, y1, x2, y2 = bbox_mm(fp)
        w, h = x2 - x1, y2 - y1
        step = 0.5
        for k in range(0, 400):
            ring = [(0, 0)] if k == 0 else [(dx, dy) for dx in range(-k, k + 1) for dy in range(-k, k + 1) if max(abs(dx), abs(dy)) == k]
            ring.sort(key=lambda d: d[0] ** 2 + d[1] ** 2)
            for dx, dy in ring:
                cx, cy = target[0] + dx * step, target[1] + dy * step
                r = (cx - w / 2 - 0.3, cy - h / 2 - 0.3, cx + w / 2 + 0.3, cy + h / 2 + 0.3)
                if self.free(r, region):
                    put(fp, cx, cy, rot)
                    self.occ.append(self.rect(fp))
                    self.placed.add(ref)
                    return True
        return False

    def pad_pos(self, ref, pin):
        for pad in self.fps[ref].Pads():
            if pad.GetNumber() == str(pin):
                p = pad.GetPosition()
                return pcbnew.ToMM(p.x), pcbnew.ToMM(p.y)
        return None

    def attractor(self, ref):
        """Average position of the placed pads this part connects to through small (signal) nets."""
        pts = []
        for pad in self.fps[ref].Pads():
            name = self.pinnet.get((ref, pad.GetNumber()))
            if not name or len(self.nets[name]) > 8:
                continue
            for r2, p2 in self.nets[name]:
                if r2 != ref and r2 in self.placed:
                    pp = self.pad_pos(r2, p2)
                    if pp:
                        pts.append(pp)
        if not pts:
            return None
        return (sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts))


DOMAIN = {}
for _d, _names in (("logic", {"+3V3", "GND_L", "VDDA", "+3V3_TXRX1", "+3V3_TXRX2", "+3V3_BIAS", "VDDCR", "VDD12TX"}),
                   ("logic24", {"+24V_LOGIC", "0V_LOGIC", "24V_LOGIC_IN"}),
                   ("field", {"+24V_IO", "0V_IO", "+5V_IO", "24V_IO_IN", "SENSE_DI", "SENSE_SEL", "COM_DI", "COM_SEL"}),
                   ("analog", {"+15V_A", "AGND", "+5V_A"}), ("earth", {"PE", "SHIELD"})):
    for _n in _names:
        DOMAIN[_n] = _d


def short(name):
    return name.split("/")[-1]


def part_domain(ref, pinnet, nets, known):
    """Domain of a part from the nets it touches; None when it touches none (resolved from neighbours)."""
    ds = {}
    for (r, pin), name in pinnet.items():
        if r == ref and short(name) in DOMAIN:
            ds[DOMAIN[short(name)]] = ds.get(DOMAIN[short(name)], 0) + 1
    if ds:
        return max(ds, key=ds.get)
    for (r, pin), name in pinnet.items():
        if r == ref and len(nets[name]) <= 8:
            for r2, p2 in nets[name]:
                if r2 in known:
                    return known[r2]
    return None


def variant_geometry(v):
    """Board size, domain regions (mm, x1 y1 x2 y2) and explicit anchor positions for each variant, from the floor plans."""
    if v == "v1":
        W, H = 260.0, 160.0
        reg = {"analog": (14, 1, 99, 43), "field": (14, 47, 99, 146), "logic": (101, 22, 149, 159), "logic24": (101, 100, 149, 159),
               "relay": (151, 1, 185, 159), "mains": (187, 1, 259, 135), "earth": (101, 100, 149, 159)}
        left = [(7.25, 6 + 7.75 + 15.5 * i) for i in range(9)]                      # J501..J509 (left edge, rotated)
        bottom = []
        x = 17.0
        ents = [("J201", 20.6), ("J601", 30.7)]
        pos = {}
        for ref, w in ents:
            pos[ref] = (x + w / 2, H - 7.25); x += w + 2.4
        for i in range(11):
            pos[f"J5{10 + i}"] = (x + 7.75, H - 7.25); x += 15.5
        left_pos = {f"J5{i + 1:02d}": left[i] for i in range(9)}
        relay = dict(sock_x=204.0, fuse_x=234.6, term_x=W - 6.25, y0=10.0)
        holes = [(66, 4), (146, 4), (66, 142), (146, 142)]
        top = {"J401": (112, 10.65), "J402": (132, 10.65), "J801": (36.2, 7.25), "J802": (48.2, 7.25)}
        key = {"U301": (125, 70), "U401": (125, 42), "U201": (125, 125), "U602": (100, 134), "U801": (100, 22), "U202": (80, 122), "U203": (60, 30),
               "U701": (150, 22), "U702": (150, 36), "J101": (W - 12, H - 20)}
        key["_opto_x"] = 100.0
    else:
        W, H = 220.0, 140.0
        reg = {"analog": (26, 1, 89, 40), "field": (26, 42, 89, 114), "logic": (91, 22, 125, 139), "logic24": (91, 90, 125, 139),
               "relay": (127, 1, 145, 139), "mains": (147, 1, 219, 135), "earth": (91, 90, 125, 139)}
        left_pos = {}
        n = 1
        for row in (0, 1):
            for i in range(7):
                left_pos[f"J5{n:02d}"] = (7.25 + row * 12.5, 3 + 7.75 + 15.5 * i); n += 1
        pos = {}
        x = 27.0
        for ref, w in (("J201", 20.6), ("J601", 30.7)):
            pos[ref] = (x + w / 2, H - 7.25); x += w + 2
        for i in range(3):
            pos[f"J5{n:02d}"] = (x + 7.75, H - 7.25); x += 15.5; n += 1
        x = 27.0
        for i in range(3):
            pos[f"J5{n:02d}"] = (x + 7.75, H - 19.75); x += 15.5; n += 1
        relay = dict(sock_x=W - 74 + 17.75, fuse_x=W - 38.3 + 12.9, term_x=W - 6.25, y0=3.0)
        holes = [(70, 4), (135, 4), (80, 108), (135, 108)]
        top = {"J401": (97.5, 10.65), "J402": (117.5, 10.65), "J801": (32.2, 7.25), "J802": (44.2, 7.25)}
        key = {"U301": (108, 70), "U401": (108, 42), "U201": (108, 125), "U602": (90, 108), "U801": (90, 32), "U202": (50, 104), "U203": (50, 30),
               "U701": (126, 36), "U702": (126, 50), "J101": (W - 15, H - 8)}
        key["_opto_x"] = 90.0
    return W, H, reg, left_pos, pos, relay, holes, top, key


def outline(board, W, H, x0=0.0, y0=0.0):
    pts = [(0, 0), (W, 0), (W, H), (0, H), (0, 0)]
    for a, b in zip(pts, pts[1:]):
        seg = pcbnew.PCB_SHAPE(board)
        seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
        seg.SetLayer(pcbnew.Edge_Cuts)
        seg.SetStart(VECTOR2I(mm(a[0] + x0), mm(a[1] + y0)))
        seg.SetEnd(VECTOR2I(mm(b[0] + x0), mm(b[1] + y0)))
        seg.SetWidth(mm(0.1))
        board.Add(seg)


def place_all(board, fps, comps, nets, pinnet, v):
    W, H, reg, left_pos, pos, relay, holes, top, key = variant_geometry(v)
    L = Layout(fps, pinnet, nets, W, H, reg)
    whole = (0.0, 0.0, W, H)
    # --- terminals: left edge rotated so the pins run along the edge, bottom edge as drawn
    for ref, (cx, cy) in left_pos.items():
        L.anchor(ref, cx, cy, 90)
    for ref, (cx, cy) in pos.items():
        L.anchor(ref, cx, cy, 0)
    for ref, (cx, cy) in top.items():
        L.anchor(ref, cx, cy, 0)
    # --- relay strip: socket, fuse block, terminal per row
    for i in range(8):
        y = relay["y0"] + 7.75 + 15.5 * i
        widths = {}
        for ref, rot in ((f"J70{i + 1}", 90), (f"F70{i + 1}", 0), (f"XK70{i + 1}", 90)):
            put(fps[ref], 0, 0, rot)
            b = bbox_mm(fps[ref])
            widths[ref] = b[2] - b[0]
        xt = W - 1.0 - widths[f"J70{i + 1}"] / 2
        xf = xt - widths[f"J70{i + 1}"] / 2 - 0.4 - widths[f"F70{i + 1}"] / 2
        xs = xf - widths[f"F70{i + 1}"] / 2 - 0.4 - widths[f"XK70{i + 1}"] / 2
        L.anchor(f"J70{i + 1}", xt, y, 90)
        L.anchor(f"F70{i + 1}", xf, y, 0)
        L.anchor(f"XK70{i + 1}", xs, y, 90)
    # --- key parts
    for ref, xy in key.items():
        if ref.startswith("_") or ref in ("U602", "U801", "U701", "U702") or ref not in fps:
            continue
        L.anchor(ref, xy[0], xy[1], 0)
    for i, (hx, hy) in enumerate(holes):
        L.anchor(f"H10{i + 1}", hx, hy, 0)
    # --- optocouplers straddle the field | logic barrier; their pins 1-8 (LED side) face the field
    ox = key["_opto_x"]
    for k in range(5):
        L.anchor(f"U50{k + 1}", ox, 56 + k * 14 if v == "v1" else 50 + k * 11, pin=1, side="left")
    # the field | logic isolators: U602 (field side = pins 9-16 left), U701/U702 (logic = pins 1-8 left), U801 (logic left)
    L.anchor("U602", *key["U602"], pin=16, side="left")
    L.anchor("U801", *key["U801"], pin=1, side="left")
    L.anchor("U701", *key["U701"], pin=1, side="left")
    L.anchor("U702", *key["U702"], pin=1, side="left")
    # --- everything else: nearest free spot to the parts it connects to, inside its domain region
    known = {}
    order = [r for r in fps if r not in L.placed]
    dom = {}
    for r in order:
        dom[r] = part_domain(r, pinnet, nets, known)
        if dom[r]:
            known[r] = dom[r]
    for r in order:
        if dom[r] is None:
            dom[r] = part_domain(r, pinnet, nets, known) or "logic"
            known[r] = dom[r]
    area = lambda r: -(lambda b: (b[2] - b[0]) * (b[3] - b[1]))(bbox_mm(fps[r]))
    for r in sorted(order, key=area):
        d = dom[r]
        region = reg.get(d, reg["logic"])
        if r.startswith(("LED70", "RN70", "U703", "C70")) or (r[:1] in "RC" and r[1:3] == "71") or r.startswith("R70"):
            region = reg["relay"] if not (r.startswith("R70") or r[1:3] == "71") else reg["mains"]
        if r.startswith(("LED5", "RN50", "C52")):
            region = reg["logic"]
        tgt = L.attractor(r) or ((region[0] + region[2]) / 2, (region[1] + region[3]) / 2)
        tgt = (min(max(tgt[0], region[0] + 1), region[2] - 1), min(max(tgt[1], region[1] + 1), region[3] - 1))
        L.auto(r, tgt, region)
    # parts that found no room are staged beside the board, to be placed by hand (the unfitted relay snubbers need about 1600 mm2)
    staged = [r for r in fps if r not in L.placed]
    for i, r in enumerate(staged):
        put(fps[r], W + 14 + (i % 2) * 24, 12 + (i // 2) * 12, 0)
        L.placed.add(r)
    L.staged = staged
    outline(board, W, H)
    return L


def metrics(board, nets, L):
    """Half-perimeter wirelength of every signal net (power and ground nets excluded) and the board fill, for comparing variants."""
    total, count = 0.0, 0
    pos = {}
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            p = pad.GetPosition()
            pos[(fp.GetReference(), pad.GetNumber())] = (pcbnew.ToMM(p.x), pcbnew.ToMM(p.y))
    for name, nodes in nets.items():
        if short(name) in DOMAIN or name.startswith("unconnected"):
            continue
        pts = [pos[n] for n in nodes if n in pos and n[0] not in L.staged]
        if len(pts) < 2:
            continue
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        total += (max(xs) - min(xs)) + (max(ys) - min(ys))
        count += 1
    return total, count


def main(variant):
    board, fps, comps, nets, pinnet = build_board()
    L = place_all(board, fps, comps, nets, pinnet, variant)
    out = os.path.join(ROOT, "hardware", f"lcec-io-{variant}.kicad_pcb")
    pcbnew.SaveBoard(out, board)
    wl, nn = metrics(board, nets, L)
    print(f"{variant}: signal nets {nn}, estimated wirelength {wl / 1000:.1f} m")
    print(f"{variant}: {len(fps)} footprints, {len(nets)} nets, staged outside the board: {sorted(L.staged)} -> {os.path.relpath(out, ROOT)}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "v1")
