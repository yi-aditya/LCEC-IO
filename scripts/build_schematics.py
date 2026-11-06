#!/usr/bin/env python3
"""Generate the KiCad schematics for M3: root sheet, 2 Power and 3 MCU.

    python3 -I scripts/make_std_symbols.py     # once: lib/lcec.kicad_sym (oriented standard symbols)
    python3 -I scripts/build_schematics.py     # writes hardware/*.kicad_sch (native KiCad 10 format)
    python3 -I scripts/check_sheets.py         # ERC, pin map, netlist and drawing-style checks

Drawing rules (enforced in schgen.py and checked by check_sheets.py):
  * every symbol instance is at rotation 0: never rotated, never mirrored; the symbol graphics are drawn in the
    orientation the circuit needs (scripts/make_std_symbols.py, scripts/relayout_symbols.py)
  * all text (references, values, net labels, pin names) is horizontal
  * signals flow left to right, supplies up, grounds down; wires are orthogonal and run straight to their pins
  * decoupling and pull parts sit beside the pin they serve
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pinmap  # noqa: E402
import schgen as G  # noqa: E402
from schgen import g  # noqa: E402

HW = os.path.join(G.ROOT, "hardware")
ROOT_UUID = G.uid("root")
SHEET_UUID = {"power": G.uid("sheet", "power"), "mcu": G.uid("sheet", "mcu")}
TP_FP = "TestPoint:TestPoint_Pad_D2.0mm"
GND = "power:GND"
MCU_HLABELS = {}                    # hierarchical labels of the MCU sheet: name -> shape (drives the root sheet pins)


# ------------------------------------------------------------------ small drawing helpers
def note(s, text, x, y, size=1.27, bold=False):
    s.text(text, x, y, size=size, bold=bold)


def vpart(s, libid, ref, x, y_top, value, lcsc, **kw):
    """Vertical two-pin part (pins 3.81 mm above and below its centre) with its TOP pin at (x, y_top).
    Returns the part; its bottom pin is at y_top + 7.62."""
    return s.place(libid, ref, x, y_top + g(3), value=value, lcsc=lcsc, **kw)


def hpart(s, libid, ref, x_left, y, value, lcsc, **kw):
    """Horizontal two-pin part with its LEFT pin at (x_left, y); the right pin is 7.62 mm further right."""
    return s.place(libid, ref, x_left + g(3), y, value=value, lcsc=lcsc, **kw)


def testpoint(s, ref, net, x, y, **kw):
    """Test point with its pin at (x, y) and the pad drawn above it; the value (net name) is not repeated."""
    return s.place("Connector:TestPoint", ref, x, y, value=net, footprint=TP_FP, in_bom=False,
                   props={"LCSC": "n/a (bare pad)"}, show_value=False, ref_at=(x + g(2), y - g(3)), justify="left", **kw)


def tp_at_net(s, ref, net, x, y):
    """Test point whose pin is wired down 2.54 mm to a net label (row of test points at the bottom of a sheet)."""
    testpoint(s, ref, net, x, y)
    s.wire((x, y), (x, y + g(2)))
    s.label(net, x, y + g(2), 0)


# =============================================================== sheet 2: power
def build_power(libs):
    s = G.Sch(libs, "02_power.kicad_sch", "LCEC-IO - 2 Power", "2", ROOT_UUID, SHEET_UUID["power"],
              comment="Two 24 V entries, protection, three isolated DC-DC modules")
    TVS = "C83851"       # SMBJ30A (owner decision 2026-11-06, replaces the plan's SMBJ33A)
    OX = g(228)           # module centre x; the isolation barrier is the vertical line through it

    note(s, "2  POWER  -  24 V entries, protection, three isolated DC-DC modules", g(10), g(8), 2.54, True)
    note(s, "Input 24 VDC +/-20 % = 19.2 ... 28.8 V.  Per input: fuse > SS54 reverse-polarity diode > SMBJ30A TVS > 47 uF + 1 uF, "
            "then a 100 uF/100 V input capacitor at each URB module (URB datasheet Cin).", g(10), g(13))

    # ---- entry connector, pins 1..4 top to bottom: +24V_LOGIC, 0V_LOGIC, +24V_IO, 0V_IO
    jx, jy = g(30), g(66)
    J = s.place("lcec:Conn_R_01x04_P7", "J201", jx, jy, value="24 V entry", lcsc="C441206",
                ref_at=(jx - g(2), jy + g(2)), val_at=(jx - g(2), jy + g(5)), justify="right")
    note(s, "1  +24V_LOGIC", g(10), jy + g(11), 1.27); note(s, "2  0V_LOGIC", g(10), jy + g(13))
    note(s, "3  +24V_IO", g(10), jy + g(15)); note(s, "4  0V_IO", g(10), jy + g(17))
    y_lg, y_io = g(56), g(110)
    xa = J.pin("1")[0] + g(8)                                       # x of the two vertical runs
    p1, p2, p3, p4 = (J.pin(n) for n in "1234")
    s.wire(p1, (xa, p1[1]), (xa, y_lg))                             # +24V_LOGIC up to its channel
    s.wire(p3, (xa, p3[1]), (xa, y_io))                             # +24V_IO down to its channel
    e = s.stub(p2, (1, 0), g(4)); s.power(GND, "0V_LOGIC", *e)
    s.pwr_flag(e[0] - g(2), e[1])                                   # 0V_LOGIC has no output power pin
    e = s.stub(p4, (1, 0), g(4)); s.power(GND, "0V_IO", *e)

    def protection(y, net_in, rail_net, ret_net, ref_f, ref_tvs, ref_d, ref_c47, ref_c1, amps, title):
        note(s, title, xa + g(4), y - g(8), 1.27, True)
        F = hpart(s, "lcec:Fuse_H", ref_f, g(60), y, f"{amps} A 5x20", "C206887")
        s.wire((xa, y), F.pin("1"))
        s.label(net_in, xa + g(3), y, 0)
        D = hpart(s, "lcec:D_Schottky_AK_H", ref_d, g(72), y, "SS54", "C22452")
        s.wire(F.pin("2"), D.pin("1"))
        rail_end = (OX - g(12), y)
        s.wire(D.pin("2"), rail_end)
        T = vpart(s, "lcec:D_TVS_KA_V", ref_tvs, g(92), y, "SMBJ30A", TVS)
        s.power(GND, ret_net, *T.pin("2"))
        C = vpart(s, "Device:C_Polarized", ref_c47, g(112), y, "47uF 50V", "C970679")
        s.power(GND, ret_net, *C.pin("2"))
        C1 = vpart(s, "Device:C", ref_c1, g(132), y, "1uF 50V", "C91185")
        s.power(GND, ret_net, *C1.pin("2"))
        s.power("power:+24V", rail_net, g(150), y)                   # names the protected rail
        s.pwr_flag(g(157), y)
        return rail_end

    protection(y_lg, "24V_LOGIC_IN", "+24V_LOGIC", "0V_LOGIC", "F201", "D201", "D203", "C201", "C202", 1, "24V_LOGIC input protection")
    protection(y_io, "24V_IO_IN", "+24V_IO", "0V_IO", "F202", "D202", "D204", "C205", "C206", 3, "24V_IO input protection")
    testpoint(s, "TP201", "+24V_LOGIC", g(166), y_lg)
    testpoint(s, "TP202", "+24V_IO", g(166), y_io)

    def module(ref, code, vin_y, out_pos, out_neg, cin_ref, cout_ref, ret_net, tp_ref, tp_net, mpn):
        """URB module with VIN on the rail at y = vin_y. Returns the placed module."""
        oy = vin_y + g(4)
        U = s.place("lcsc:" + code, ref, OX, oy, value=mpn, lcsc=code,
                    ref_at=(OX - g(2), oy - g(10)), val_at=(OX + g(2), oy - g(10)), justify="right", val_justify="left")
        vin, ctrl, gnd = U.pin("2"), U.pin("3"), U.pin("1")
        s.wire((OX - g(12), vin_y), vin)
        s.no_connect(*ctrl)                                          # CTRL open = module on
        s.no_connect(*U.pin("5")); s.no_connect(*U.pin("8"))
        e = s.stub(gnd, (-1, 0), g(4)); s.power(GND, ret_net, *e)
        Cin = vpart(s, "Device:C_Polarized", cin_ref, g(188), vin_y, "100uF 100V", "C2960285")
        s.power(GND, ret_net, *Cin.pin("2"))
        vp, vn = U.pin("6"), U.pin("7")
        xo = vp[0] + g(24)
        s.wire(vp, (xo, vp[1]))
        s.power(out_pos[0], out_pos[1], xo, vp[1])
        Co = vpart(s, "Device:C", cout_ref, vp[0] + g(8), vp[1], "22uF 25V", "C45783")
        xc = vp[0] + g(8)
        s.wire((vp[0], vn[1]), (xc, vn[1]))                          # -VO to the bottom of the output capacitor
        s.wire(Co.pin("2"), (xc, vn[1]))
        s.power(out_neg[0], out_neg[1], xc, vn[1])
        testpoint(s, tp_ref, tp_net, vp[0] + g(14), vp[1])
        return U

    module("U201", "C5369843", y_lg, ("power:+3V3", "+3V3"), ("power:GND", "GND_L"), "C203", "C204", "0V_LOGIC", "TP205", "+3V3", "URB2403S-6WR3")
    y_u203 = y_io + g(40)
    module("U202", "C3031185", y_io, ("power:+5V", "+5V_IO"), ("power:GND", "0V_IO"), "C207", "C208", "0V_IO", "TP203", "+5V_IO", "URB2405S-6WR3")
    module("U203", "C5369844", y_u203, ("power:+15V", "+15V_A"), ("power:GNDA", "AGND"), "C209", "C210", "0V_IO", "TP204", "+15V_A", "URB2415S-6WR3")
    xd = g(176)                                                      # rail drop to the third module
    s.wire((xd, y_io), (xd, y_u203))
    s.wire((xd, y_u203), (OX - g(12), y_u203))
    # ground test points, beside the channels
    for ref, net, y in (("TP206", "0V_LOGIC", y_lg + g(14)), ("TP207", "0V_IO", y_io + g(14))):
        testpoint(s, ref, net, g(12), y); s.power(GND, net, g(12), y)

    # ---- isolation barrier and domain captions
    s.dashed_line(OX, g(30), OX, g(172))
    s.text("24V_LOGIC domain", OX - g(2), g(46), justify="right bottom"); s.text("U201: +3V3 on isolated GND_L", OX + g(2), g(46), justify="left bottom")
    s.text("24V_IO domain", OX - g(2), g(100), justify="right bottom"); s.text("U202: +5V_IO, 0 V tied to 0V_IO at the module (not isolated)", OX + g(2), g(100), justify="left bottom")
    s.text("24V_IO domain", OX - g(2), g(140), justify="right bottom"); s.text("U203: +15V_A on its own isolated AGND", OX + g(2), g(140), justify="left bottom")

    # ---- BOM accessories (pin-less symbols: in the BOM, not on the PCB)
    bx, by = g(48), g(135)
    s.box(bx, by, bx + g(110), by + g(30), dashed=True)
    note(s, "BOM accessories (not on the PCB)", bx + g(2), by + g(4), 1.27, True)
    acc = [("FU201", "C3116", "1 A 5x20 glass fuse, in F201"), ("FU202", "C3118", "3 A 5x20 glass fuse, in F202"),
           ("FC201", "C187509", "clear cover for F201"), ("FC202", "C187509", "clear cover for F202"),
           ("P201", "C440882", "4-pole cable plug for J201")]
    for i, (ref, code, txt) in enumerate(acc):
        ay = by + g(9 + 4 * i)
        s.place("lcec:Accessory", ref, bx + g(8), ay, value=txt, lcsc=code, in_bom=True, on_board=False, footprint="",
                ref_at=(bx + g(16), ay), val_at=(bx + g(30), ay), justify="left")

    # ---- design notes
    ny = g(172)
    note(s, "Design notes", g(10), ny, 1.27, True)
    for i, t in enumerate((
            "Loads: +3V3 about 0.4 A of the module's 1.35 A (30 %). 24V_LOGIC input about 0.3 A at full module load: 1 A fuse.",
            "24V_IO: 5 V module 7.3 W + 15 V module 7 W at full load = 0.75 A, plus relay coils 0.21 A and sensors through the PTCs 1 A: 3 A fuse.",
            "Input inrush I2t into the input capacitors stays below 1.1 A2s; the fuses are rated 4.26 A2s (1 A) and 12.5 A2s (3 A).",
            "URB input 9-36 V (40 V continuous, 50 V for 1 s). SMBJ30A: 30 V stand-off above the 28.8 V maximum input, clamps 48.4 V at 12.4 A.",
            "CTRL left open = module on. NC pins are not connected inside the module.")):
        note(s, t, g(10), ny + g(4 + 3 * i))
    return s


# =============================================================== sheet 3: MCU
HX_LEFT, HX_RIGHT = g(150), g(240)            # x of the hierarchical labels at the left and right of the signal unit


def build_mcu(libs):
    from pin_tables import T
    s = G.Sch(libs, "03_mcu.kicad_sch", "LCEC-IO - 3 MCU", "3", ROOT_UUID, SHEET_UUID["mcu"],
              comment="STM32F405VGT6 (LQFP-100), shared clock, SWD, UART, heartbeat LED")
    byname = {}
    for num, nm in T["C56621"]["pins"].items():
        byname.setdefault(nm[0], []).append(str(num))

    note(s, "3  MCU  -  STM32F405VGT6, shared 25 MHz clock, SWD, UART2, heartbeat LED", g(10), g(8), 2.54, True)
    note(s, "51 signals used (pin map in docs/plan.md), PH1 is a test pad, the 30 pins of ports D and E are free for future use (no-connect flags).  "
            "Firmware: HSE bypass, PLLM 25 / PLLN 336 / PLLP 2 = 168 MHz, IWDG enabled in option bytes.", g(10), g(13))

    cn = [0]

    def cref():
        cn[0] += 1
        return f"C3{cn[0]:02d}"

    rn = [0]

    def rref():
        rn[0] += 1
        return f"R3{rn[0]:02d}"

    # ======================================================== U301 unit 2: power pins and their decoupling
    PX, PY = g(60), g(80)
    UP = s.place("lcsc:C56621", "U301", PX, PY, value="STM32F405VGT6", lcsc="C56621", unit=2,
                 ref_at=(PX, PY + g(35)), val_at=(PX, PY + g(38)), justify="center")
    note(s, "U301 power: 100 nF beside each VDD pin and VBAT, 4.7 uF bulk, VDDA through a ferrite, 2.2 uF on each VCAP", g(10), g(24), 1.27, True)
    pw = lambda name, i=0: UP.pin(byname[name][i])        # noqa: E731
    rail_x = g(24)
    rows = [pw("VBAT")] + [pw("VDD", i) for i in range(6)]
    s.power("power:+3V3", "+3V3", rail_x, rows[0][1] - g(4))
    s.wire((rail_x, rows[0][1] - g(4)), (rail_x, rows[-1][1]))
    for pt in rows:
        s.wire((rail_x, pt[1]), pt)
        Cd = vpart(s, "Device:C", cref(), pt[0] - g(14), pt[1], "100nF", "C1591")
        s.power(GND, "GND_L", *Cd.pin("2"))
    # bulk capacitor on the rail, left of it
    Cb = vpart(s, "Device:C", cref(), rail_x - g(8), rows[0][1] + g(2), "4.7uF", "C19666", ref_at=(rail_x - g(11), rows[0][1] + g(4)),
               val_at=(rail_x - g(11), rows[0][1] + g(7)), justify="right")
    s.wire((rail_x, rows[0][1] + g(2)), (rail_x - g(8), rows[0][1] + g(2)))
    s.power(GND, "GND_L", *Cb.pin("2"))
    # VDDA: ferrite from +3V3, then 1 uF and 100 nF; VREF+ tied to VDDA
    vda, vrf = pw("VDDA"), pw("VREF+")
    s.wire((rail_x, rows[-1][1]), (rail_x, vda[1]))
    FB = hpart(s, "lcec:FerriteBead_H", "FB301", rail_x + g(4), vda[1], "600R@100MHz", "C19330")
    xa = vda[0] - g(10)
    s.wire((rail_x, vda[1]), FB.pin("1"))
    s.wire(FB.pin("2"), vda)
    s.wire(vrf, (xa, vrf[1]), (xa, vda[1]))
    s.pwr_flag(xa - g(2), vda[1])                     # VDDA/VREF+ are fed through a passive ferrite
    for k, (val, code, y) in enumerate((("1uF", "C559769", vda[1]), ("100nF", "C1591", vrf[1]))):
        Cv = vpart(s, "Device:C", cref(), vda[0] - g(6), y, val, code)
        s.power(GND, "GND_L", *Cv.pin("2"))
    s.label("VDDA", xa + g(1), vda[1], 0)
    note(s, "VDDA / VREF+", xa - g(2), vrf[1] + g(13))
    # ground pins (right side): one common ground, 2.2 uF on each VCAP
    vss = [pw("VSS", i) for i in range(4)] + [pw("VSSA")]
    xg = vss[0][0] + g(4)
    for pt in vss:
        s.wire(pt, (xg, pt[1]))
    s.wire((xg, vss[0][1]), (xg, vss[-1][1]))
    s.power(GND, "GND_L", xg, vss[-1][1])
    for nm in ("VCAP_1", "VCAP_2"):
        pt = pw(nm)
        s.wire(pt, (xg, pt[1]))
        Cv = vpart(s, "Device:C", cref(), xg, pt[1], "2.2uF", "C23630")
        s.power(GND, "GND_L", *Cv.pin("2"))

    # ======================================================== U301 unit 1: signals
    SX, SY = g(195), g(120)
    U = s.place("lcsc:C56621", "U301", SX, SY, value="STM32F405VGT6", lcsc="C56621", unit=1,
                ref_at=(SX - g(8), SY - g(65)), val_at=(SX + g(8), SY - g(65)), justify="center")
    P = lambda name, i=0: U.pin(byname[name][i])         # noqa: E731

    def hl(name, shape, x, y, rot):
        MCU_HLABELS[name] = shape
        s.hlabel(name, shape, x, y, rot)

    bus_info = {}
    for side, title, items in pinmap.LEFT_RIGHT:
        for net, pname in items:
            pt = P(pname)
            sign = -1 if side == "left" else 1
            if title.startswith("Free"):
                s.no_connect(*pt)
            elif title in ("DI1-8", "SEL1-12", "DO1-8"):
                x_e = pt[0] + sign * g(12)
                s.wire(pt, (x_e, pt[1]))
                s.label(net, pt[0] + sign * g(2), pt[1], 180 if side == "left" else 0)
                if side == "left":
                    s.bus_entry(x_e - g(2), pt[1] - g(2), g(2), g(2))
                    xb = x_e - g(2)
                else:
                    s.bus_entry(x_e, pt[1], g(2), -g(2))
                    xb = x_e + g(2)
                bus_info.setdefault(title, {"x": xb, "ys": [], "side": side})["ys"].append(pt[1] - g(2))
            elif net == "NRST":
                s.wire(pt, (pt[0] - g(24), pt[1]))
                s.label("NRST", pt[0] - g(24), pt[1], 180)
                Cn = vpart(s, "Device:C", cref(), pt[0] - g(10), pt[1], "100nF", "C1591")
                s.power(GND, "GND_L", *Cn.pin("2"))
            elif net == "BOOT0":
                s.wire(pt, (pt[0] - g(24), pt[1]))
                s.label("BOOT0", pt[0] - g(24), pt[1], 180)
                Rb = vpart(s, "Device:R", rref(), pt[0] - g(10), pt[1], "10k", "C25804")
                s.power(GND, "GND_L", *Rb.pin("2"))
            elif net in ("CLK_MCU", "PH1_TP", "SWDIO", "SWCLK", "SWO", "UART2_TX", "UART2_RX"):
                s.stub(pt, (sign, 0), g(10), net=net)
            elif net == "HB_LED":
                s.stub(pt, (1, 0), g(10), net="HB_LED")                  # the LED chain is drawn clear of the pin rows, bottom right
                hx, hy = g(262), g(185)
                s.label("HB_LED", hx - g(2), hy, 180)
                s.wire((hx - g(2), hy), (hx, hy))
                Rh = hpart(s, "lcec:R_H", rref(), hx, hy, "1k", "C21190")
                Lh = hpart(s, "lcec:LED_AK_H", "LED301", Rh.pin("2")[0] + g(4), hy, "heartbeat", "C2287")
                s.wire(Rh.pin("2"), Lh.pin("2"))
                e = s.stub(Lh.pin("1"), (1, 0), g(3)); s.power(GND, "GND_L", *e)
            elif net in ("RELAY_OE", "ESC_RST", "AO_CLAMP"):
                xr = pt[0] + g(10)
                s.wire(pt, (HX_RIGHT, pt[1]))
                hl(net, "output", HX_RIGHT, pt[1], 0)
                if net == "RELAY_OE":                                   # pull-down hangs below the wire
                    R = vpart(s, "Device:R", rref(), xr, pt[1], "10k", "C25804")
                    s.power(GND, "GND_L", *R.pin("2"))
                else:                                                   # pull-up hangs above the wire
                    R = vpart(s, "Device:R", rref(), xr, pt[1] - g(6), "10k", "C25804")
                    s.power("power:+3V3", "+3V3", *R.pin("1"))
                    s.wire(R.pin("2"), (xr, pt[1]))
            else:
                shape = "input" if net in ("MPG_A", "MPG_B", "ESC_IRQ", "ESC_SYNC0", "ESC_SYNC1", "ESC_MISO") else "output"
                if side == "left":
                    s.wire(pt, (HX_LEFT, pt[1]))
                    hl(net, shape, HX_LEFT, pt[1], 180)
                else:
                    s.wire(pt, (HX_RIGHT, pt[1]))
                    hl(net, shape, HX_RIGHT, pt[1], 0)
    for title, b in bus_info.items():
        name = {"DI1-8": "DI[1..8]", "SEL1-12": "SEL[1..12]", "DO1-8": "DO[1..8]"}[title]
        y0, y1 = min(b["ys"]), max(b["ys"])
        if b["side"] == "left":
            s.bus((b["x"], y1), (b["x"], y0), (HX_LEFT, y0))
            hl(name, "input", HX_LEFT, y0, 180)
        else:
            s.bus((b["x"], y1), (b["x"], y0), (HX_RIGHT, y0))
            hl(name, "output", HX_RIGHT, y0, 0)

    # ======================================================== 25 MHz oscillator
    ox, oy = g(105), g(26)
    X = s.place("lcsc:C2595919", "X301", ox, oy, value="25 MHz", lcsc="C2595919", ref_at=(ox, oy - g(10)), val_at=(ox, oy + g(10)), justify="center")
    e = s.stub(X.pin("1"), (-1, 0), g(4)); s.power("power:+3V3", "+3V3", *e)           # OE high = running
    e = s.stub(X.pin("2"), (-1, 0), g(4)); s.power(GND, "GND_L", *e)
    vd = X.pin("4")
    n = s.stub(vd, (1, 0), g(30)); s.power("power:+3V3", "+3V3", *n)
    Cx = vpart(s, "Device:C", cref(), n[0], n[1], "100nF", "C1591")
    s.power(GND, "GND_L", *Cx.pin("2"))
    out = X.pin("3")
    xj = out[0] + g(4)
    R1 = hpart(s, "lcec:R_H", rref(), out[0] + g(8), out[1], "22R", "C23345")
    s.wire(out, R1.pin("1"))
    s.stub(R1.pin("2"), (1, 0), g(3), net="CLK_MCU")
    R2 = hpart(s, "lcec:R_H", rref(), out[0] + g(8), out[1] + g(10), "22R", "C23345")
    s.wire((xj, out[1]), (xj, R2.pin("1")[1]), R2.pin("1"))
    e = s.stub(R2.pin("2"), (1, 0), g(3))
    hl("CLK_ESC", "output", e[0], e[1], 0)
    note(s, "OE tied high = oscillator running. 22 R series resistors to PH0 (HSE bypass) and to the LAN9252 (sheet 4).", g(10), g(40))

    # ======================================================== debug, UART, test points
    jx, jy = g(285), g(115)
    J = s.place("Connector_Generic:Conn_01x10", "J301", jx, jy, value="SWD 2x5 1.27 mm", lcsc="C3975188",
                ref_at=(jx + g(2), jy - g(11)), val_at=(jx + g(2), jy + g(13)), justify="left")
    s.stub(J.pin("2"), (-1, 0), g(8), net="SWDIO")
    s.stub(J.pin("4"), (-1, 0), g(8), net="SWCLK")
    s.stub(J.pin("6"), (-1, 0), g(8), net="SWO")
    s.stub(J.pin("10"), (-1, 0), g(8), net="NRST")
    e = s.stub(J.pin("1"), (-1, 0), g(4)); s.power("power:+3V3", "+3V3", *e)
    e3 = s.stub(J.pin("3"), (-1, 0), g(4)); e5 = s.stub(J.pin("5"), (-1, 0), g(4)); s.wire(e3, e5); s.power(GND, "GND_L", *e5)
    e9 = s.stub(J.pin("9"), (-1, 0), g(4)); s.power(GND, "GND_L", *e9)
    s.no_connect(*J.pin("7")); s.no_connect(*J.pin("8"))
    note(s, "SWD (Cortex 10-pin): 1 VTref, 2 SWDIO, 3/5/9 GND,", g(258), jy - g(20)); note(s, "4 SWCLK, 6 SWO, 7/8 not used, 10 NRST", g(258), jy - g(17))
    ux, uy = g(285), g(150)
    Uj = s.place("Connector_Generic:Conn_01x03", "J302", ux, uy, value="USART2", lcsc="C2937625",
                 ref_at=(ux + g(2), uy - g(5)), val_at=(ux + g(2), uy + g(7)), justify="left")
    s.stub(Uj.pin("1"), (-1, 0), g(8), net="UART2_TX")
    s.stub(Uj.pin("2"), (-1, 0), g(8), net="UART2_RX")
    e = s.stub(Uj.pin("3"), (-1, 0), g(4)); s.power(GND, "GND_L", *e)
    note(s, "USART2: 1 TX (PA2), 2 RX (PA3), 3 GND", g(258), uy - g(9))
    ty = g(190)
    nets = ("ESC_SCK", "ESC_MISO", "ESC_MOSI", "ESC_CS", "DAC_SCK", "DAC_MOSI", "DAC_CS", "RELAY_OE", "AO_CLAMP", "MPG_A", "MPG_B", "PH1_TP")
    for k, net in enumerate(nets):
        tp_at_net(s, f"TP3{k + 1:02d}", net, g(20) + k * g(11), ty)
    note(s, "Test points: SPI1 (LAN9252), SPI2 (DAC), relay OE, analog clamp, MPG A/B and the spare pin PH1", g(20), ty - g(7))
    return s


# =============================================================== root sheet
def build_root(libs):
    s = G.Sch(libs, "lcec-io.kicad_sch", "LCEC-IO - EtherCAT slave I/O board", "1", ROOT_UUID, ROOT_UUID,
              comment="Root sheet: milestone M3 holds the Power and MCU sheets; sheets 4-8 follow in M4 and M5")
    s.text("LCEC-IO  -  EtherCAT slave I/O board", g(12), g(12), 3.0, justify="left bottom")
    s.text("Root sheet, milestone M3: Power (2) and MCU (3). Sheets 4 to 8 (EtherCAT, digital inputs, MPG, relay outputs, analog outputs) "
           "are added in M4 and M5; the full root sheet follows in M6.", g(12), g(18))
    s.sheet("Power", "02_power.kicad_sch", g(20), g(40), g(40), g(24), [], 2, SHEET_UUID["power"])
    ins = [n for n, sh in MCU_HLABELS.items() if sh == "input"]
    outs = [n for n, sh in MCU_HLABELS.items() if sh == "output"]
    h = max(len(ins), len(outs)) * g(2) + g(8)
    pins = [(n, "input", "left", g(4) + i * g(2)) for i, n in enumerate(ins)] + \
           [(n, "output", "right", g(4) + i * g(2)) for i, n in enumerate(outs)]
    pos = s.sheet("MCU", "03_mcu.kicad_sch", g(100), g(40), g(40), h, pins, 3, SHEET_UUID["mcu"])
    for n, (x, y) in pos.items():
        s.no_connect(x, y)
    s.text("No-connect flags on the MCU sheet pins are placeholders: they are replaced by wires to sheets 4 to 8 in M4 and M5.",
           g(100), g(40) + h + g(6))
    return s


def main():
    libs = G.Libs()
    os.makedirs(HW, exist_ok=True)
    out = [build_power(libs).write(HW)]
    out.append(build_mcu(libs).write(HW))
    out.append(build_root(libs).write(HW))
    print("wrote", *[os.path.basename(p) for p in out])


if __name__ == "__main__":
    main()
