#!/usr/bin/env python3
"""Build lib/lcec.kicad_sym: KiCad's own symbol graphics, turned into the orientation the schematics need.

Why: every component instance in the schematics sits at rotation 0 (never rotated or mirrored), with all
text horizontal. A series fuse or diode on a horizontal supply rail therefore needs a symbol that is drawn
horizontally; a shunt TVS or capacitor one that is drawn vertically. Instead of rotating instances, the
graphics are rotated or mirrored once, here, from KiCad's standard symbols, so they look standard.

Pin NUMBERS are chosen to match the LCSC footprints (verified in M2): SS54 pad 1 = anode, pad 2 = cathode;
SMBJ/SMAJ pad 1 = cathode, pad 2 = anode; electrolytic pad 1 = plus.

Run before build_schematics.py. Safe to re-run.
"""
import copy
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import schgen as G  # noqa: E402

STD = os.environ.get("KICAD10_SYMBOL_DIR", "/usr/share/kicad/symbols")
OUT = os.path.join(ROOT, "lib", "lcec.kicad_sym")

# point transforms in symbol space (y up)
OPS = {
    "mx": lambda x, y: (-x, y),          # mirror left-right
    "r90": lambda x, y: (-y, x),         # rotate 90 degrees counter-clockwise
    "r270": lambda x, y: (y, -x),        # rotate 90 degrees clockwise
}


def f(v):
    s = f"{v:.4f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def apply(ops, x, y):
    for o in ops:
        x, y = OPS[o](x, y)
    return x, y


def xy_list(lst, ops):
    for p in lst:
        if isinstance(p, list) and p and p[0] == "xy":
            x, y = apply(ops, float(p[1]), float(p[2]))
            p[1], p[2] = f(x), f(y)


def transform(tree, ops, name, renumber=None, reference=None, value=None):
    t = copy.deepcopy(tree)
    old = G.unq(t[1])
    t[1] = G.q(name)
    for sub in G.find(t, "symbol"):
        sub[1] = G.q(G.unq(sub[1]).replace(old, name, 1))
        for it in sub[2:]:
            if not isinstance(it, list):
                continue
            if it[0] in ("polyline",):
                xy_list(G.find(it, "pts")[0], ops)
            elif it[0] in ("rectangle",):
                for k in ("start", "end"):
                    e = G.find(it, k)[0]
                    x, y = apply(ops, float(e[1]), float(e[2]))
                    e[1], e[2] = f(x), f(y)
            elif it[0] == "circle":
                e = G.find(it, "center")[0]
                x, y = apply(ops, float(e[1]), float(e[2]))
                e[1], e[2] = f(x), f(y)
            elif it[0] == "arc":
                for k in ("start", "mid", "end"):
                    e = G.find(it, k)[0]
                    x, y = apply(ops, float(e[1]), float(e[2]))
                    e[1], e[2] = f(x), f(y)
            elif it[0] == "pin":
                at = G.find(it, "at")[0]
                x, y = apply(ops, float(at[1]), float(at[2]))
                a = math.radians(float(at[3]))
                vx, vy = apply(ops, math.cos(a), math.sin(a))
                ang = round(math.degrees(math.atan2(vy, vx))) % 360
                at[1], at[2], at[3] = f(x), f(y), str(ang)
                num = G.find(it, "number")[0]
                if renumber and G.unq(num[1]) in renumber:
                    num[1] = G.q(renumber[G.unq(num[1])])
    for p in G.find(t, "property"):
        if reference and G.unq(p[1]) == "Reference":
            p[2] = G.q(reference)
        if value and G.unq(p[1]) == "Value":
            p[2] = G.q(value)
    return t


def std(libname, name):
    tree, _ = G.parse(G.tokenize(open(os.path.join(STD, libname + ".kicad_sym"), encoding="utf-8").read()))
    return [e for e in tree if isinstance(e, list) and e[:1] == ["symbol"] and G.unq(e[1]) == name][0]


ACCESSORY = """(symbol "Accessory" (pin_numbers (hide yes)) (pin_names (offset 0) (hide yes)) (exclude_from_sim no) (in_bom yes) (on_board no)
 (property "Reference" "A" (at 0 3.81 0) (effects (font (size 1.27 1.27))))
 (property "Value" "Accessory" (at 0 -3.81 0) (effects (font (size 1.27 1.27))))
 (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
 (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
 (property "Description" "Part that is in the BOM but not on the PCB (cable plug, glass fuse, cover, screw)" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))
 (symbol "Accessory_0_1"
  (rectangle (start -3.81 1.27) (end 3.81 -1.27) (stroke (width 0.254) (type default)) (fill (type background))))
 (embedded_fonts no))"""


def conn_right(name, n, pitch):
    """Single-row connector with its pins on the RIGHT, pin 1 at the top, pins `pitch` apart."""
    ys = [-pitch * i for i in range(n)]                      # symbol space, y up; first pin at y = 0
    top, bot = ys[0] + pitch / 2, ys[-1] - pitch / 2
    ticks = "".join(f"(rectangle (start 1.27 {f(y + 0.127)}) (end 0 {f(y - 0.127)}) (stroke (width 0.1524) (type default)) (fill (type none)))" for y in ys)
    pins = "".join(f'(pin passive line (at 5.08 {f(y)} 180) (length 3.81) (name "Pin_{i + 1}" (effects (font (size 1.27 1.27)))) '
                   f'(number "{i + 1}" (effects (font (size 1.27 1.27)))))' for i, y in enumerate(ys))
    txt = (f'(symbol "{name}" (pin_names (offset 1.016) (hide yes)) (exclude_from_sim no) (in_bom yes) (on_board yes)'
           f' (property "Reference" "J" (at 0 {f(top + 2.54)} 0) (effects (font (size 1.27 1.27))))'
           f' (property "Value" "{name}" (at 0 {f(bot - 2.54)} 0) (effects (font (size 1.27 1.27))))'
           f' (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))'
           f' (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) hide))'
           f' (symbol "{name}_1_1" (rectangle (start 1.27 {f(top)}) (end -1.27 {f(bot)}) (stroke (width 0.254) (type default)) (fill (type background)))'
           f' {ticks} {pins}) (embedded_fonts no))')
    return G.parse(G.tokenize(txt))[0]


def build():
    out = []
    out.append(transform(std("Device", "D_Schottky"), ["mx"], "D_Schottky_AK_H", {"1": "2", "2": "1"}, "D", "SS54"))
    out.append(transform(std("Device", "D_Zener"), ["r270"], "D_TVS_KA_V", None, "D", "TVS"))
    out.append(transform(std("Device", "Fuse"), ["r90"], "Fuse_H", None, "F", "Fuse"))
    out.append(transform(std("Device", "R"), ["r90"], "R_H", None, "R", "R"))
    out.append(transform(std("Device", "FerriteBead"), ["r90"], "FerriteBead_H", None, "FB", "FerriteBead"))
    out.append(transform(std("Device", "LED"), ["mx"], "LED_AK_H", None, "LED", "LED"))
    for n in (2, 3, 4, 6):
        out.append(conn_right(f"Conn_R_01x0{n}", n, 2.54))
    out.append(conn_right("Conn_R_01x04_P7", 4, 7.62))     # wide pitch for the 24 V entry: room to fan out each pole
    acc, _ = G.parse(G.tokenize(ACCESSORY))
    out.append(acc)
    text = ("(kicad_symbol_lib (version 20251024) (generator \"kicad_symbol_editor\") (generator_version \"10.0\")\n"
            + "\n".join(G.dump(s) for s in out) + "\n)\n")
    open(OUT, "w", encoding="utf-8").write(text)
    r = subprocess.run(["kicad-cli", "sym", "upgrade", "--force", OUT], capture_output=True, text=True)
    print((r.stdout + r.stderr).strip(), "|", len(out), "symbols ->", os.path.relpath(OUT, ROOT))
    return r.returncode


if __name__ == "__main__":
    sys.exit(build())
