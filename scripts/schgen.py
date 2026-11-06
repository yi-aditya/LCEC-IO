#!/usr/bin/env python3
"""Small KiCad schematic generator (writes .kicad_sch text, then `kicad-cli sch upgrade` makes it native).

Design rules it enforces
  * every coordinate is snapped to the 1.27 mm (50 mil) grid
  * symbol pin positions are read from the symbol libraries, so wires meet pins exactly
  * junctions are added automatically (>= 3 connections, or a wire end on a wire)
  * UUIDs are derived from names, so regenerating gives identical files (clean diffs)
  * power symbols reuse KiCad's glyphs; the net name is the Value field

Connectivity is verified afterwards from KiCad's own netlist (scripts/check_sheets.py), not trusted
from this file's geometry maths.
"""
import csv
import math
import os
import subprocess
import tempfile
import uuid

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GRID = 1.27
NS = uuid.UUID("6f1c3d52-8e1a-4a54-9d63-0c0e1e0c10c0")
PROJECT = "lcec-io"
STD_SYM = os.environ.get("KICAD10_SYMBOL_DIR", "/usr/share/kicad/symbols")


def g(n):
    """n grid units -> mm."""
    return round(n * GRID, 4)


def snap(v):
    return round(round(v / GRID) * GRID, 4)


def uid(*key):
    return str(uuid.uuid5(NS, "/".join(str(k) for k in key)))


def fmt(v):
    s = f"{v:.4f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


# ---------------------------------------------------------------- s-expressions
def tokenize(s):
    i, n, out = 0, len(s), []
    while i < n:
        c = s[i]
        if c in " \t\r\n":
            i += 1
        elif c in "()":
            out.append(c)
            i += 1
        elif c == '"':
            j = i + 1
            while s[j] != '"':
                if s[j] == "\\":
                    j += 1
                j += 1
            out.append(s[i:j + 1])
            i = j + 1
        else:
            j = i
            while j < n and s[j] not in ' \t\r\n()"':
                j += 1
            out.append(s[i:j])
            i = j
    return out


def parse(tokens, i=0):
    lst, i = [], i + 1
    while tokens[i] != ")":
        if tokens[i] == "(":
            sub, i = parse(tokens, i)
            lst.append(sub)
        else:
            lst.append(tokens[i])
            i += 1
    return lst, i + 1


def dump(x):
    return x if isinstance(x, str) else "(" + " ".join(dump(e) for e in x) + ")"


def q(s):
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"') + '"'


def unq(s):
    return s[1:-1] if s.startswith('"') else s


def find(tree, key):
    return [e for e in tree if isinstance(e, list) and e and e[0] == key]


# ---------------------------------------------------------------- symbol libraries
class SymDef:
    def __init__(self, libid, tree):
        self.libid = libid
        self.tree = tree
        self.pins = {}          # number -> (x, y, angle, length, name, type)
        self.unit_of = {}       # pin number -> unit (0 = common to all units)
        self.units = set()
        for sub in find(tree, "symbol"):
            parts = unq(sub[1]).rsplit("_", 2)
            unit = int(parts[1]) if len(parts) == 3 and parts[1].isdigit() else 1
            self.units.add(unit)
            for p in find(sub, "pin"):
                at = find(p, "at")[0]
                ln = find(p, "length")[0]
                nm = find(p, "name")[0]
                nb = find(p, "number")[0]
                self.pins[unq(nb[1])] = (float(at[1]), float(at[2]), float(at[3]), float(ln[1]), unq(nm[1]), p[1])
                self.unit_of[unq(nb[1])] = unit
        self.props = {unq(p[1]): unq(p[2]) for p in find(tree, "property")}
        self.units.discard(0)

    def embedded(self):
        t = list(self.tree)
        t[1] = q(self.libid)
        return t


class Libs:
    """Reads symbols from the project library (upgraded to KiCad 10 syntax) and KiCad's standard libraries."""

    def __init__(self):
        self._trees = {}
        self._tmp = tempfile.mkdtemp(prefix="schgen_")
        up = os.path.join(self._tmp, "lcsc.kicad_sym")
        subprocess.run(["cp", os.path.join(ROOT, "lib", "lcsc.kicad_sym"), up], check=True)
        subprocess.run(["kicad-cli", "sym", "upgrade", up], check=True, capture_output=True)
        self.paths = {"lcsc": up, "lcec": os.path.join(ROOT, "lib", "lcec.kicad_sym")}
        self.cache = {}

    def _load(self, nick):
        if nick not in self._trees:
            path = self.paths.get(nick) or os.path.join(STD_SYM, nick + ".kicad_sym")
            tree, _ = parse(tokenize(open(path, encoding="utf-8").read()))
            self._trees[nick] = {unq(e[1]): e for e in tree if isinstance(e, list) and e[:1] == ["symbol"]}
        return self._trees[nick]

    def get(self, libid):
        """libid = 'Device:R' or 'lcsc:<entry name>' or 'lcsc:C22452' (looked up by LCSC number)."""
        if libid not in self.cache:
            nick, name = libid.split(":", 1)
            syms = self._load(nick)
            real = name
            if name not in syms and nick == "lcsc":
                for ename, tree in syms.items():
                    props = {unq(p[1]): unq(p[2]) for p in find(tree, "property")}
                    if props.get("LCSC") == name:
                        real = ename
                        break
            if real not in syms:
                raise KeyError(f"{libid} not found")
            sd = SymDef(f"{nick}:{real}", syms[real])
            self.cache[libid] = sd
            self.cache[sd.libid] = sd
        return self.cache[libid]


_BOM = None


def bom():
    global _BOM
    if _BOM is None:
        _BOM = {}
        for r in csv.DictReader(open(os.path.join(ROOT, "bom", "parts.csv"), encoding="utf-8")):
            if r["LCSC"] and r["LCSC"] not in _BOM:
                _BOM[r["LCSC"]] = r
    return _BOM


# ---------------------------------------------------------------- geometry
def rot_point(x, y, rot):
    """Symbol-space (y up) point -> offset in schematic space (y down) for a counter-clockwise rotation."""
    y = -y
    c, s = round(math.cos(math.radians(rot))), round(math.sin(math.radians(rot)))
    return (x * c + y * s, -x * s + y * c)


class Placed:
    """A placed symbol. Every instance sits at rotation 0 (never rotated or mirrored)."""

    def __init__(self, sch, libid, ref, x, y, sd, unit=1):
        self.sch, self.libid, self.ref, self.x, self.y, self.sd, self.unit = sch, libid, ref, x, y, sd, unit

    def pin(self, number):
        px, py = self.sd.pins[str(number)][:2]
        return (snap(self.x + px), snap(self.y - py))

    def pin_dir(self, number):
        """Unit vector pointing away from the symbol body at this pin."""
        a = math.radians(self.sd.pins[str(number)][2])   # direction the pin line runs toward the body
        return (-round(math.cos(a)), round(math.sin(a)))


class Sch:
    def __init__(self, libs, filename, title, page, root_uuid, sheet_uuid, rev="A", paper="A3", comment="", paths=None):
        self.libs, self.filename, self.title, self.page = libs, filename, title, page
        self.root_uuid, self.sheet_uuid = root_uuid, sheet_uuid
        # instance paths of this sheet file: one per place it is used (a reused sheet has several)
        self.paths = paths or (["/" + root_uuid] if page == "1" else ["/" + root_uuid + "/" + sheet_uuid])
        self.rev, self.paper, self.comment = rev, paper, comment
        self.items, self.used_libs, self.refs = [], {}, {}
        self.wires, self.pins_at, self.counter = [], [], 0
        self.uuid_root = filename

    # -- helpers
    def _u(self, kind):
        self.counter += 1
        return uid(self.uuid_root, kind, self.counter)

    def _stroke(self, t="default", w=0):
        return f"(stroke (width {w}) (type {t}))"

    def _eff(self, size=1.27, justify=None, hide=False):
        j = f" (justify {justify})" if justify and justify != "center" else ""   # centred = no justify clause
        h = " hide" if hide else ""
        return f"(effects (font (size {size} {size})){j}{h})"

    # -- primitives
    def wire(self, *pts):
        pts = [(snap(x), snap(y)) for x, y in pts]
        for a, b in zip(pts, pts[1:]):
            if a == b:
                continue
            self.wires.append((a, b))
            self.items.append(f"(wire (pts (xy {fmt(a[0])} {fmt(a[1])}) (xy {fmt(b[0])} {fmt(b[1])})) {self._stroke()} (uuid {q(self._u('w'))}))")

    def bus(self, *pts):
        pts = [(snap(x), snap(y)) for x, y in pts]
        for a, b in zip(pts, pts[1:]):
            self.items.append(f"(bus (pts (xy {fmt(a[0])} {fmt(a[1])}) (xy {fmt(b[0])} {fmt(b[1])})) {self._stroke()} (uuid {q(self._u('b'))}))")

    def bus_entry(self, x, y, dx=GRID * 2, dy=GRID * 2):
        self.items.append(f"(bus_entry (at {fmt(snap(x))} {fmt(snap(y))}) (size {fmt(dx)} {fmt(dy)}) {self._stroke()} (uuid {q(self._u('be'))}))")

    def junction(self, x, y):
        self.items.append(f"(junction (at {fmt(x)} {fmt(y)}) (diameter 0) (color 0 0 0 0) (uuid {q(self._u('j'))}))")

    def no_connect(self, x, y):
        x, y = snap(x), snap(y)
        self.pins_at.append((x, y))
        self.items.append(f"(no_connect (at {fmt(x)} {fmt(y)}) (uuid {q(self._u('nc'))}))")

    def label(self, name, x, y, rot=0):
        assert rot in (0, 180), "labels are horizontal only"
        x, y = snap(x), snap(y)
        just = "left bottom" if rot in (0, 90) else "right bottom"
        self.items.append(f"(label {q(name)} (at {fmt(x)} {fmt(y)} {rot}) (fields_autoplaced yes) {self._eff(justify=just)} (uuid {q(self._u('l'))}))")

    def hlabel(self, name, shape, x, y, rot=0):
        assert rot in (0, 180), "hierarchical labels are horizontal only"
        x, y = snap(x), snap(y)
        just = "left" if rot in (0, 90) else "right"
        self.items.append(f"(hierarchical_label {q(name)} (shape {shape}) (at {fmt(x)} {fmt(y)} {rot}) {self._eff(justify=just)} (uuid {q(self._u('hl'))}))")

    def text(self, s, x, y, size=1.27, bold=False, justify="left bottom"):
        b = " bold" if bold else ""
        self.items.append(f"(text {q(s)} (exclude_from_sim no) (at {fmt(snap(x))} {fmt(snap(y))} 0) (effects (font (size {size} {size}){b}) (justify {justify})) (uuid {q(self._u('t'))}))")

    def dashed_line(self, x1, y1, x2, y2):
        self.items.append(f"(polyline (pts (xy {fmt(x1)} {fmt(y1)}) (xy {fmt(x2)} {fmt(y2)})) (stroke (width 0.25) (type dash)) (uuid {q(self._u('pl'))}))")

    def box(self, x1, y1, x2, y2, dashed=True):
        t = "dash" if dashed else "default"
        self.items.append(f"(rectangle (start {fmt(x1)} {fmt(y1)}) (end {fmt(x2)} {fmt(y2)}) (stroke (width 0.15) (type {t})) (fill (type none)) (uuid {q(self._u('rc'))}))")

    # -- symbols
    def next_ref(self, prefix):
        self.refs[prefix] = self.refs.get(prefix, 0) + 1
        return f"{prefix}{self.page}{self.refs[prefix]:02d}"

    def place(self, libid, ref, x, y, value=None, lcsc=None, unit=1, props=None, text="auto", ref_at=None,
              val_at=None, justify=None, val_justify=None, in_bom=True, on_board=True, show_value=True,
              footprint=None, dnp=False):
        """Place a symbol at rotation 0. All text is horizontal.

        text: 'auto' puts the reference above and the value below a horizontal part, and both to the right of a
        vertical one; 'right' / 'above' force one of those; ref_at / val_at override the positions."""
        sd = self.libs.get(libid)
        libid = sd.libid
        x, y = snap(x), snap(y)
        self.used_libs[libid] = sd
        refs = [ref(k) if callable(ref) else ref for k in range(len(self.paths))]
        ref = refs[0]
        P = Placed(self, libid, ref, x, y, sd, unit)
        fields = {}
        d = bom().get(lcsc, {}) if lcsc else {}
        fields["Footprint"] = footprint if footprint is not None else (d.get("Footprint") or sd.props.get("Footprint", ""))
        if fields["Footprint"].startswith("n/a"):
            fields["Footprint"] = ""                      # accessories: the BOM text is not a footprint
        if lcsc:
            fields["LCSC"] = lcsc
            fields["MPN"] = d.get("MPN", sd.props.get("MPN", ""))
            fields["Manufacturer"] = d.get("Manufacturer", sd.props.get("Manufacturer", ""))
            fields["Datasheet"] = sd.props.get("Datasheet") or f"https://www.lcsc.com/datasheet/{lcsc}.pdf"
        else:
            fields["Datasheet"] = sd.props.get("Datasheet", "")
        fields.update(props or {})
        val = value if value is not None else sd.props.get("Value", sd.libid.split(":")[1])
        mine = [n for n in sd.pins if sd.unit_of[n] in (0, unit)]
        xs = [sd.pins[n][0] for n in mine] or [0]
        ys = [sd.pins[n][1] for n in mine] or [0]
        horizontal = (max(xs) - min(xs)) > (max(ys) - min(ys)) and len(mine) <= 2
        if text == "auto":
            text = "above" if horizontal else "right"
        if text == "above":
            ref_at = ref_at or (x, y - g(4)); val_at = val_at or (x, y + g(4)); just = justify or "center"
        else:
            half = max(max(xs), 0) + g(1)
            ref_at = ref_at or (x + half + g(1), y - g(1)); val_at = val_at or (x + half + g(1), y + g(1)); just = justify or "left"
        lines = [f"(symbol (lib_id {q(libid)}) (at {fmt(x)} {fmt(y)} 0) (unit {unit}) (exclude_from_sim no) "
                 f"(in_bom {'yes' if in_bom else 'no'}) (on_board {'yes' if on_board else 'no'}) (dnp {'yes' if dnp else 'no'}) "
                 f"(uuid {q(uid(self.uuid_root, 'sym', ref, unit))})",
                 f" (property \"Reference\" {q(ref)} (at {fmt(ref_at[0])} {fmt(ref_at[1])} 0) {self._eff(justify=just)})",
                 f" (property \"Value\" {q(val)} (at {fmt(val_at[0])} {fmt(val_at[1])} 0) {self._eff(justify=val_justify or just, hide=not show_value)})"]
        for k, v in fields.items():
            lines.append(f" (property {q(k)} {q(v)} (at {fmt(x)} {fmt(y)} 0) {self._eff(hide=True)})")
        for n in mine:
            lines.append(f" (pin {q(n)} (uuid {q(uid(self.uuid_root, 'pin', ref, unit, n))}))")
            self.pins_at.append(P.pin(n))
        paths = " ".join(f"(path {q(pp)} (reference {q(rr)}) (unit {unit}))" for pp, rr in zip(self.paths, refs))
        lines.append(f" (instances (project {q(PROJECT)} {paths})))")
        self.items.append("\n".join(lines))
        return P

    def power(self, glyph, net, x, y, ref=None, show_value=True):
        rot = 0
        """Power symbol (glyph = e.g. 'power:GND'); the net name is the Value field."""
        self.counter += 1
        ref = ref or f"#PWR{self.page}{self.counter:03d}"
        sd = self.libs.get(glyph)
        self.used_libs[glyph] = sd
        x, y = snap(x), snap(y)
        down = sd.pins["1"][2] == 270
        vy = y + g(3) if down else y - g(3)
        self.items.append(
            f"(symbol (lib_id {q(glyph)}) (at {fmt(x)} {fmt(y)} {rot}) (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no) (uuid {q(uid(self.uuid_root, 'pwr', ref))})\n"
            f" (property \"Reference\" {q(ref)} (at {fmt(x)} {fmt(y)} 0) {self._eff(hide=True)})\n"
            f" (property \"Value\" {q(net)} (at {fmt(x)} {fmt(vy)} 0) {self._eff(hide=not show_value)})\n"
            f" (property \"Footprint\" \"\" (at {fmt(x)} {fmt(y)} 0) {self._eff(hide=True)})\n"
            f" (property \"Datasheet\" \"\" (at {fmt(x)} {fmt(y)} 0) {self._eff(hide=True)})\n"
            f" (pin \"1\" (uuid {q(uid(self.uuid_root, 'pwrpin', ref))}))\n"
            f" (instances (project {q(PROJECT)} " + " ".join(f"(path {q(pp)} (reference {q(ref)}) (unit 1))" for pp in self.paths) + ")))")
        self.pins_at.append((x, y))

    def sheet(self, name, filename, x, y, w, h, pins, page, sheet_uuid, parent_path=None):
        """Hierarchical sheet symbol. pins = [(name, shape, side, y_offset_mm)], side 'left' or 'right'.
        Returns {pin name: (x, y)} so callers can wire or no-connect them."""
        x, y, w, h = snap(x), snap(y), snap(w), snap(h)
        out, lines = {}, []
        for pname, shape, side, dy in pins:
            py = snap(y + dy)
            px, rot = (x, 180) if side == "left" else (x + w, 0)
            just = "right" if side == "left" else "left"
            out[pname] = (px, py)
            lines.append(f" (pin {q(pname)} {shape} (at {fmt(px)} {fmt(py)} {rot}) {self._eff(justify=just)} (uuid {q(uid(self.uuid_root, 'sp', pname))}))")
        self.items.append(
            f"(sheet (at {fmt(x)} {fmt(y)}) (size {fmt(w)} {fmt(h)}) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no) (fields_autoplaced yes)\n"
            f" (stroke (width 0.1524) (type solid)) (fill (color 0 0 0 0.0)) (uuid {q(sheet_uuid)})\n"
            f" (property \"Sheetname\" {q(name)} (at {fmt(x)} {fmt(y - 1.27)} 0) {self._eff(justify='left bottom')})\n"
            f" (property \"Sheetfile\" {q(filename)} (at {fmt(x)} {fmt(y + h + 1.27)} 0) {self._eff(justify='left top')})\n"
            + "\n".join(lines) + "\n"
            f" (instances (project {q(PROJECT)} (path {q(parent_path or self.paths[0])} (page {q(str(page))}))))\n)")
        return out

    def pwr_flag(self, x, y):
        self.power("power:PWR_FLAG", "PWR_FLAG", x, y, ref=f"#FLG{self.page}{self.counter + 1:03d}", show_value=False)

    # -- connection helpers
    def stub(self, pt, direction, length, net=None):
        """Wire from pt in `direction` for `length` mm; an optional net label at the end (horizontal wires only,
        because labels are never rotated). Returns the end point."""
        end = (snap(pt[0] + direction[0] * length), snap(pt[1] + direction[1] * length))
        self.wire(pt, end)
        if net:
            assert direction[1] == 0, "net labels go on horizontal wires"
            self.label(net, end[0], end[1], 0 if direction[0] > 0 else 180)
        return end

    def autojunctions(self):
        pts = {}
        for (a, b) in self.wires:
            for p in (a, b):
                pts[p] = pts.get(p, 0) + 1
        for p in self.pins_at:
            pts[p] = pts.get(p, 0) + 1
        done = set()
        for p, cnt in pts.items():
            on_wire = False
            for (a, b) in self.wires:
                if p in (a, b):
                    continue
                if a[0] == b[0] == p[0] and min(a[1], b[1]) < p[1] < max(a[1], b[1]):
                    on_wire = True
                if a[1] == b[1] == p[1] and min(a[0], b[0]) < p[0] < max(a[0], b[0]):
                    on_wire = True
            if (cnt >= 3 or (on_wire and cnt >= 1)) and p not in done:
                self.junction(*p)
                done.add(p)

    # -- output
    def render(self, extra_items=None):
        self.autojunctions()
        libsyms = "\n".join(dump(sd.embedded()) for sd in self.used_libs.values())
        tb = (f"(title_block (title {q(self.title)}) (date \"2026-11-06\") (rev {q(self.rev)}) "
              f"(company \"Yantra Innovation - LCEC-IO\") (comment 1 {q(self.comment)}))")
        body = "\n".join(self.items + (extra_items or []))
        return (f"(kicad_sch (version 20231120) (generator \"eeschema\") (generator_version \"8.0\")\n"
                f"(uuid {q(self.root_uuid if self.page == '1' else self.sheet_uuid)}) (paper {q(self.paper)})\n{tb}\n"
                f"(lib_symbols\n{libsyms}\n)\n{body}\n"
                f"(sheet_instances (path \"/\" (page {q(self.page)}))))\n")

    def write(self, outdir, extra_items=None):
        path = os.path.join(outdir, self.filename)
        open(path, "w", encoding="utf-8").write(self.render(extra_items))
        subprocess.run(["kicad-cli", "sch", "upgrade", path], check=True, capture_output=True)
        return path
