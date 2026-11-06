#!/usr/bin/env python3
"""Redrawn concept floor plan (M6): real footprint sizes from lib/lcsc.pretty, one terminal per I/O, four isolation domains.

Writes docs/review/M6-floorplan.svg and prints the numbers used in docs/review/M6-review.md (terminal edge length, relay strip,
component area against board area). Footprint sizes are read from the courtyards in lib/lcsc.pretty (see scripts/pincheck.py);
standard SMD sizes use typical courtyards.
"""
import csv
import glob
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W1, H1 = 260.0, 160.0                   # v1: one row of terminals
W, H = 220.0, 140.0                     # v2: two stacked rows of terminals
S = 4                                    # px per mm


def bbox(path):
    t = open(path, encoding="utf-8").read()
    xs, ys = [], []
    for m in re.finditer(r"\(fp_line \(start ([-\d.]+) ([-\d.]+)\) \(end ([-\d.]+) ([-\d.]+)\)[^\n]*F\.CrtYd", t):
        a, b, c, d = map(float, m.groups())
        xs += [a, c]; ys += [b, d]
    return (max(xs) - min(xs), max(ys) - min(ys)) if xs else None


FP = {os.path.basename(f)[:-10]: bbox(f) for f in glob.glob(os.path.join(ROOT, "lib", "lcsc.pretty", "*.kicad_mod"))}
STD = {"R_0603": (3.0, 1.6), "C_0603": (3.0, 1.6), "R_1206": (4.6, 2.6), "R_2512": (7.2, 3.6), "C_0805": (3.8, 2.2), "C_1206": (4.6, 2.6),
       "L_0603": (3.0, 1.6), "LED_0603": (3.0, 1.6), "R_Array_Convex_4x0603": (4.0, 3.0), "TestPoint": (3.0, 3.0), "C_Rect_L18.0mm": (19.0, 9.0)}


def size_of(fp):
    name = fp.split(":")[-1]
    if name in FP and FP[name]:
        return FP[name]
    for k, v in STD.items():
        if name.startswith(k) or k in name:
            return v
    return (2.0, 2.0)


def component_area():
    total, bylib = 0.0, {}
    for r in csv.DictReader(open(os.path.join(ROOT, "docs", "review", "M6-bom.csv"), encoding="utf-8")):
        if r["Fit"] not in ("Y", "DNP") or not r["Footprint"]:
            continue
        w, h = size_of(r["Footprint"])
        a = w * h * int(r["Qty"])
        total += a
        bylib[r["Footprint"]] = bylib.get(r["Footprint"], 0) + a
    return total, bylib


def svg_v1():
    o = []
    col = {"logic": "#dbe8ff", "field": "#ffe9c9", "analog": "#d9f2d9", "mains": "#ffd6d6", "part": "#ffffff"}

    def rect(x, y, w, h, fill, label="", stroke="#333", sw=0.25, fs=2.6, dash=False, anchor="middle"):
        d = ' stroke-dasharray="1.5 1"' if dash else ""
        o.append(f'<rect x="{x * S:.1f}" y="{y * S:.1f}" width="{w * S:.1f}" height="{h * S:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw * S:.1f}"{d}/>')
        if label:
            tx = x + w / 2 if anchor == "middle" else x + 1
            o.append(f'<text x="{tx * S:.1f}" y="{(y + h / 2) * S + fs * S / 3:.1f}" font-size="{fs * S:.1f}" text-anchor="{anchor}" font-family="sans-serif" fill="#111">{label}</text>')

    def line(x1, y1, x2, y2, color="#c00", dash=True, sw=0.5):
        d = ' stroke-dasharray="3 2"' if dash else ""
        o.append(f'<line x1="{x1 * S:.1f}" y1="{y1 * S:.1f}" x2="{x2 * S:.1f}" y2="{y2 * S:.1f}" stroke="{color}" stroke-width="{sw * S:.1f}"{d}/>')

    def text(x, y, s, fs=3.0, bold=False, color="#111", anchor="start"):
        b = ' font-weight="bold"' if bold else ""
        o.append(f'<text x="{x * S:.1f}" y="{y * S:.1f}" font-size="{fs * S:.1f}" font-family="sans-serif" fill="{color}" text-anchor="{anchor}"{b}>{s}</text>')

    pad = 14
    o.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{(W1 + 2 * pad) * S:.0f}" height="{(H1 + 2 * pad + 28) * S:.0f}" viewBox="{-pad * S} {-pad * S} {(W1 + 2 * pad) * S:.0f} {(H1 + 2 * pad + 28) * S:.0f}">')
    o.append(f'<rect x="{-pad * S}" y="{-pad * S}" width="{(W1 + 2 * pad) * S:.0f}" height="{(H1 + 2 * pad + 28) * S:.0f}" fill="#fafafa"/>')
    text(0, -6, f"LCEC-IO concept floor plan, top view, {W1:.0f} x {H1:.0f} mm, one terminal per I/O, single row (footprints to scale)", 4.0, True)
    # domains
    rect(14, 0, 86, 44, col["analog"], "", sw=0.3)
    text(16, 20, "ANALOG  AGND  (sheet 8)", 3.0, True)
    rect(14, 46, 86, 101.5, col["field"], "", sw=0.3)
    text(16, 50.5, "FIELD I/O  0V_IO  (sheets 5, 6, 2)", 3.0, True)
    rect(100, 0, 50, H1, col["logic"], "", sw=0.3)
    text(102, 24, "LOGIC  GND_L (sheets 2, 3, 4)", 2.6, True)
    rect(150, 0, 110 - 0, H1, col["field"], "", sw=0.3)
    text(152, 4.5, "FIELD  (relay driver)", 3.0, True)
    rect(186, 8, 74, 128, col["mains"], "", sw=0.3)
    text(188, 6.5, "MAINS side (contacts, fuses, terminals)", 2.6, True)
    # barriers
    line(100, 0, 100, H1); line(150, 0, 150, H1); line(14, 45, 100, 45)
    text(14, H1 + 4, "barrier at x = 100 mm: U501-U505, U602, U801", 2.4, color="#c00")
    text(14, H1 + 8, "barrier at x = 150 mm: U701, U702", 2.4, color="#c00")
    # terminals: left edge inputs 1-9, bottom: entry, MPG, inputs 10-20, right edge relays, top edge AO and RJ45
    for i in range(9):
        rect(0, 6 + i * 15.5, 12.5, 15.5, col["part"], f"J5{i + 1:02d}", fs=2.4)
    x = 17.0
    for lab, w in (("J201 entry", 20.6), ("J601 MPG", 30.7)):
        rect(x, H1 - 12.5, w, 12.5, col["part"], lab, fs=2.4); x += w + 2.4
    for i in range(11):
        rect(x, H1 - 12.5, 15.5, 12.5, col["part"], f"J5{i + 10:02d}", fs=2.4); x += 15.5
    rect(243.6, 139, 8.2, 10.2, col["part"], "PE", fs=2.2)
    for i in range(8):
        y = 10 + i * 15.5
        rect(247.5, y, 12.5, 15.5, col["part"], f"J70{i + 1}", fs=2.4)
        rect(221.7, y + 3.25, 25.8, 9, col["part"], f"F70{i + 1}", fs=2.2)
        rect(186.2, y + 0.5, 35.5, 14.5, col["part"], f"XK70{i + 1}", fs=2.4, anchor="start")
    line(204, 8, 204, 136, "#900", True, 0.8)
    text(205, 140.5, "routed slot (coil | contacts)", 2.4, color="#900")
    rect(16, 0, 10.4, 12.5, col["part"], "J801", fs=2.2); rect(28, 0, 10.4, 12.5, col["part"], "J802", fs=2.2)
    rect(104, 0, 16, 21.3, col["part"], "J401 RJ45", fs=2.2); rect(122, 0, 16, 21.3, col["part"], "J402 RJ45", fs=2.2)
    # circuits
    rect(104, 26, 42, 36, col["part"], "LAN9252, EEPROM", fs=2.6)
    rect(104, 66, 42, 46, col["part"], "STM32F405, clock, SWD, UART, LEDs", fs=2.4)
    rect(104, 116, 42, 30, col["part"], "2403S + 3V3 rail (U201)", fs=2.4)
    rect(154, 12, 30, 20, col["part"], "U701 U702", fs=2.4)
    rect(154, 36, 30, 20, col["part"], "ULN2803A + arrays", fs=2.4)
    rect(154, 60, 30, 76, col["part"], "ON LED arrays, spare", fs=2.4)
    rect(54, 14, 44, 28, col["part"], "DAC, op-amps, U801, 2415S", fs=2.4)
    for k in range(5):
        rect(18 + (k % 2) * 41, 56 + (k // 2) * 22, 39, 20, col["part"], f"inputs group {k + 1} (U50{k + 1})", fs=2.3)
    rect(18, 100, 39, 22, col["part"], "MPG: AM26LS32 + U602", fs=2.3)
    rect(59, 100, 39, 22, col["part"], "2405S + input protection", fs=2.3)
    rect(18, 125, 80, 20, col["part"], "24 V entry protection (fuses, SS54, SMBJ30A, 47 uF)", fs=2.3)
    # scale bar
    line(150, H1 + 10, 200, H1 + 10, "#000", False, 0.6)
    text(202, H1 + 11, "50 mm", 2.6)
    o.append("</svg>")
    return "\n".join(o)


def svg_v2():
    o = []
    col = {"logic": "#dbe8ff", "field": "#ffe9c9", "analog": "#d9f2d9", "mains": "#ffd6d6", "part": "#ffffff"}

    def rect(x, y, w, h, fill, label="", stroke="#333", sw=0.25, fs=2.6, anchor="middle"):
        o.append(f'<rect x="{x * S:.1f}" y="{y * S:.1f}" width="{w * S:.1f}" height="{h * S:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw * S:.1f}"/>')
        if label:
            tx = x + w / 2 if anchor == "middle" else x + 1
            o.append(f'<text x="{tx * S:.1f}" y="{(y + h / 2) * S + fs * S / 3:.1f}" font-size="{fs * S:.1f}" text-anchor="{anchor}" font-family="sans-serif" fill="#111">{label}</text>')

    def line(x1, y1, x2, y2, color="#c00", dash=True, sw=0.5):
        d = ' stroke-dasharray="3 2"' if dash else ""
        o.append(f'<line x1="{x1 * S:.1f}" y1="{y1 * S:.1f}" x2="{x2 * S:.1f}" y2="{y2 * S:.1f}" stroke="{color}" stroke-width="{sw * S:.1f}"{d}/>')

    def text(x, y, s, fs=3.0, bold=False, color="#111", anchor="start"):
        b = ' font-weight="bold"' if bold else ""
        o.append(f'<text x="{x * S:.1f}" y="{y * S:.1f}" font-size="{fs * S:.1f}" font-family="sans-serif" fill="{color}" text-anchor="{anchor}"{b}>{s}</text>')

    pad = 14
    o.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{(W + 2 * pad) * S:.0f}" height="{(H + 2 * pad + 20) * S:.0f}" viewBox="{-pad * S} {-pad * S} {(W + 2 * pad) * S:.0f} {(H + 2 * pad + 20) * S:.0f}">')
    o.append(f'<rect x="{-pad * S}" y="{-pad * S}" width="{(W + 2 * pad) * S:.0f}" height="{(H + 2 * pad + 20) * S:.0f}" fill="#fafafa"/>')
    text(0, -6, f"LCEC-IO concept floor plan v2, top view, {W:.0f} x {H:.0f} mm, one terminal per I/O in two stacked rows (footprints to scale)", 3.6, True)
    rx = W - 74.0                                   # relay strip starts here
    lx = 25.0                                       # terminals: two rows 12.5 mm deep on the left and bottom edges
    by = H - 25.0
    # domains
    rect(lx, 0, 65 - lx + 25, 40, col["analog"]); text(lx + 2, 39, "ANALOG  AGND  (sheet 8)", 2.8, True)
    rect(lx, 42, 65, by - 42, col["field"]); text(lx + 2, 47, "FIELD I/O  0V_IO  (5, 6, 2)", 2.8, True)
    rect(90, 0, 36, by, col["logic"]); text(92, 25, "LOGIC  GND_L  (2, 3, 4)", 2.6, True)
    rect(126, 0, rx - 126, by, col["field"]); text(127, 5, "relay driver", 2.6, True)
    rect(rx, 3, 74, 125, col["mains"])
    line(90, 0, 90, by); line(126, 0, 126, by); line(lx, 41, 90, 41)
    text(lx, H + 4, "barriers: x = 90 mm: U501-U505, U602, U801;  x = 126 mm: U701, U702;  routed slot in the relays", 2.4, color="#c00")
    # left terminals: front row x 0..12.5, back row x 12.5..25
    n = 1
    for row in (0, 1):
        for i in range(7):
            rect(row * 12.5, 3 + i * 15.5, 12.5, 15.5, col["part"], f"J5{n:02d}", fs=2.2); n += 1
    # bottom: front row y H-12.5.., back row y H-25..
    x = lx + 2
    for lab, w in (("J201", 20.6), ("J601 MPG", 30.7)):
        rect(x, H - 12.5, w, 12.5, col["part"], lab, fs=2.2); x += w + 2
    for i in range(3):
        rect(x, H - 12.5, 15.5, 12.5, col["part"], f"J5{n:02d}", fs=2.2); x += 15.5; n += 1
    x = lx + 2
    for i in range(3):
        rect(x, H - 25, 15.5, 12.5, col["part"], f"J5{n:02d}", fs=2.2); x += 15.5; n += 1
    rect(rx - 12, H - 22, 8.2, 10.2, col["part"], "PE", fs=2.0)
    # relay strip
    for i in range(8):
        y = 3 + i * 15.5
        rect(W - 12.5, y, 12.5, 15.5, col["part"], f"J70{i + 1}", fs=2.2)
        rect(W - 38.3, y + 3.25, 25.8, 9, col["part"], f"F70{i + 1}", fs=2.0)
        rect(rx, y + 0.5, 35.5, 14.5, col["part"], f"XK70{i + 1}", fs=2.2, anchor="start")
    line(rx + 17.75, 3, rx + 17.75, 127, "#900", True, 0.8)
    text(rx + 19, H - 14, "routed slot (coil | contacts)", 2.2, color="#900")
    # top edge
    rect(lx + 2, 0, 10.4, 12.5, col["part"], "J801", fs=2.0); rect(lx + 14, 0, 10.4, 12.5, col["part"], "J802", fs=2.0)
    rect(92, 0, 16, 21.3, col["part"], "J401", fs=2.0); rect(109, 0, 16, 21.3, col["part"], "J402", fs=2.0)
    # circuits
    rect(92, 27, 32, 26, col["part"], "LAN9252, EEPROM", fs=2.4)
    rect(92, 56, 32, 30, col["part"], "STM32, clock, SWD", fs=2.4)
    rect(92, 89, 32, by - 91, col["part"], "2403S (U201)", fs=2.4)
    rect(128, 8, 16, 26, col["part"], "U701 U702", fs=2.2)
    rect(128, 38, 16, 22, col["part"], "ULN2803A", fs=2.2)
    rect(128, 64, 16, 40, col["part"], "LED arrays", fs=2.2)
    rect(lx + 28, 6, 36, 31, col["part"], "DAC, op-amps, U801, 2415S", fs=2.3)
    for k in range(5):
        rect(lx + 2 + (k % 2) * 31.5, 50 + (k // 2) * 18, 30, 16, col["part"], f"inputs {k + 1} (U50{k + 1})", fs=2.1)
    rect(lx + 33.5, 86, 30, 16, col["part"], "MPG, U602", fs=2.1)
    rect(lx + 2, 103, 62, 10, col["part"], "2405S, 24 V protection", fs=2.1)
    line(150, H + 12, 200, H + 12, "#000", False, 0.6)
    text(202, H + 13, "50 mm", 2.6)
    o.append("</svg>")
    return "\n".join(o)


def main():
    out = os.path.join(ROOT, "docs", "review")
    open(os.path.join(out, "M6-floorplan-v1-260x160.svg"), "w").write(svg_v1())
    open(os.path.join(out, "M6-floorplan-v2-220x140.svg"), "w").write(svg_v2())
    inputs = 20 * 15.5 + 8 * 15.5
    edge = inputs + 30.7 + 20.6 + 2 * 10.4
    print(f"terminal edge needed: 28 x 3-pole 15.5 = {inputs:.0f} mm, plus MPG 30.7, entry 20.6, 2 x AO 10.4 = {edge:.0f} mm")
    print(f"relay strip: 8 rows of 15.5 mm = {8 * 15.5:.0f} mm; socket 35.5 + fuse 25.8 + terminal 12.5 = {35.5 + 25.8 + 12.5:.1f} mm deep")
    if os.path.exists(os.path.join(out, "M6-bom.csv")):
        a, by = component_area()
        print(f"component footprint area about {a:.0f} mm2: {100 * a / (W1 * H1):.0f} % of v1 ({W1:.0f} x {H1:.0f}), {100 * a / (W * H):.0f} % of v2 ({W:.0f} x {H:.0f})")


if __name__ == "__main__":
    main()
