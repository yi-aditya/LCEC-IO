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
SHEET_UUID = {"inputs": G.uid("sheet", "inputs"), "in4": [G.uid("sheet", "in4", k) for k in range(5)], "analog": G.uid("sheet", "analog"), "relays": G.uid("sheet", "relays"), "mpg": G.uid("sheet", "mpg"), "power": G.uid("sheet", "power"), "mcu": G.uid("sheet", "mcu"), "ethercat": G.uid("sheet", "ethercat")}
from drawing import GND, TP_FP, hpart, note, testpoint, tp_at_net, vpart  # noqa: E402
MCU_HLABELS = {}                    # hierarchical labels of the MCU sheet: name -> shape (drives the root sheet pins)


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


# =============================================================== sheet 4: EtherCAT
# nets that cross between the MCU sheet (3) and the EtherCAT sheet (4): name -> shape seen from the EtherCAT sheet
ETH_NETS = {"CLK_ESC": "input", "ESC_CS": "input", "ESC_SCK": "input", "ESC_MOSI": "input", "ESC_RST": "bidirectional",
            "ESC_MISO": "output", "ESC_IRQ": "output", "ESC_SYNC0": "output", "ESC_SYNC1": "output", "ERR_LED": "input"}


def build_ethercat(libs):
    s = G.Sch(libs, "04_ethercat.kicad_sch", "LCEC-IO - 4 EtherCAT", "4", ROOT_UUID, SHEET_UUID["ethercat"],
              comment="LAN9252 in SPI mode, 24LC32A ESI EEPROM, two RJ45 jacks, RUN and ERR LEDs")
    cn, rn = [0], [0]

    def cref():
        cn[0] += 1
        return f"C4{cn[0]:02d}"

    def rref():
        rn[0] += 1
        return f"R4{rn[0]:02d}"

    note(s, "4  ETHERCAT  -  LAN9252 (SPI), ESI EEPROM, two RJ45 jacks with magnetics, RUN and ERR LEDs", g(10), g(8), 2.54, True)
    note(s, "Chip mode 00 = 2 ports (PHY A = port 0 = J401, PHY B = port 1 = J402). The PDI is chosen by the ESI EEPROM content (SPI slave). "
            "Rows and values follow the LAN9252 datasheet DS00001909A (sections 3, 4, 7, 12.10 and 14).", g(10), g(13))

    # ============================================================ U401 unit 1: signals (centre of the sheet)
    UX, UY = g(185), g(100)
    U = s.place("lcsc:C80933", "U401", UX, UY, value="LAN9252I/PT", lcsc="C80933", unit=1,
                ref_at=(UX - g(8), UY - g(68)), val_at=(UX + g(8), UY - g(68)), justify="center")
    P = U.pin
    HX = g(116)                                            # x of the hierarchical labels, left of the chip

    for num, net, shape in (("1", "CLK_ESC", "input"), ("11", "ESC_RST", "bidirectional"), ("50", "ESC_CS", "input"),
                            ("19", "ESC_SCK", "input"), ("17", "ESC_MOSI", "input"), ("13", "ESC_MISO", "output"),
                            ("44", "ESC_IRQ", "output"), ("34", "ESC_SYNC0", "output"), ("18", "ESC_SYNC1", "output")):
        x, y = P(num)
        s.wire((x, y), (HX, y))
        s.hlabel(net, shape, HX, y, 180)
    s.stub(P("42"), (-1, 0), g(8), net="EESDA")
    s.stub(P("43"), (-1, 0), g(8), net="EESCL")

    # RUN LED (open drain, active low because E2PSIZE is strapped high for the 32 Kbit EEPROM): +3V3 > 1k > LED > pin
    x, y = P("45")
    xn = x - g(4)
    s.wire((x, y), (xn, y))
    Lr = hpart(s, "lcec:LED_AK_H", "LED401", xn - g(6), y, "RUN", "C89809")
    s.wire(Lr.pin("1"), (xn, y))
    Rr = hpart(s, "lcec:R_H", rref(), Lr.pin("2")[0] - g(10), y, "1k", "C21190")
    s.wire(Rr.pin("2"), Lr.pin("2"))
    e = s.stub(Rr.pin("1"), (-1, 0), g(3)); s.power("power:+3V3", "+3V3", *e)
    Rp = vpart(s, "Device:R", rref(), xn, y - g(6), "10k", "C25804")                # E2PSIZE strap high
    s.power("power:+3V3", "+3V3", *Rp.pin("1"))

    # port LEDs: the pins are also the chip-mode straps, held low by 10 k = chip mode 00 and active-high LED outputs
    for num, net, port in (("46", "LNK_ACT1", 1), ("48", "LNK_ACT0", 0)):
        x, y = P(num)
        xn = x - g(4)
        s.wire((x, y), (xn, y))
        Rd = vpart(s, "Device:R", rref(), xn, y, "10k", "C25804")
        s.power(GND, "GND_L", *Rd.pin("2"))
        Rl = hpart(s, "lcec:R_H", rref(), xn - g(12), y, "1k", "C21190")
        s.wire(Rl.pin("2"), (xn, y))
        s.stub(Rl.pin("1"), (-1, 0), g(3), net=net)

    # tied low: TESTMODE (must be VSS) and the FX (fibre) strap inputs = copper mode
    ys = [P(n) for n in ("41", "8", "9", "10")]
    for pt in ys:
        s.wire(pt, (pt[0] - g(4), pt[1]))
    s.wire((ys[0][0] - g(4), ys[0][1]), (ys[-1][0] - g(4), ys[-1][1]))
    s.power(GND, "GND_L", ys[-1][0] - g(4), ys[-1][1])
    for num in ("2", "12", "15", "16", "21", "22", "23", "25", "26", "27", "28", "29", "30", "31", "33", "35", "36", "39", "40", "49"):
        s.no_connect(*P(num))                                  # OSCO (OSCI is driven by a single-ended oscillator) and unused host-bus / digital I/O pins

    # ---- right side: PHY A (port 0) and PHY B (port 1) lines to the jacks, each with a 49.9 ohm termination to the port's own
    # ferrite-filtered 3.3 V (as in the EVB-LAN9252-SPI reference)
    jacks = {}
    for ref, sup, (p_tx, n_tx, p_rx, n_rx) in (("J401", "+3V3_TXRX1", ("53", "52", "55", "54")), ("J402", "+3V3_TXRX2", ("62", "63", "60", "61"))):
        x0, y0 = P(p_tx)
        JX = x0 + g(44)
        J = s.place("lcsc:C69427", ref, JX, y0 + g(18), value="HY911105AE", lcsc="C69427",
                    ref_at=(JX, y0 - g(8)), val_at=(JX, y0 + g(42)), justify="center")
        jacks[ref] = (J, sup)
        for chip, jack in ((p_tx, "1"), (n_tx, "2"), (p_rx, "3"), (n_rx, "6")):
            cx, cy = P(chip)
            s.wire((cx, cy), J.pin(jack))
            Rt = vpart(s, "Device:R", rref(), cx + g(10), cy - g(6), "49.9R", "C23185")
            s.power("power:+3V3", sup, *Rt.pin("1"))
            s.wire(Rt.pin("2"), (cx + g(10), cy))
    x, y = P("57")
    s.wire((x, y), (x + g(6), y))
    Rb = vpart(s, "Device:R", rref(), x + g(6), y, "12.1k 1%", "C22864")
    s.power(GND, "GND_L", *Rb.pin("2"))

    # ---- jack right sides: centre taps, link LEDs, shield
    for ref, net in (("J401", "LNK_ACT0"), ("J402", "LNK_ACT1")):
        J, sup = jacks[ref]
        t1, t2 = J.pin("4"), J.pin("5")
        xb = t1[0] + g(6)
        s.wire(t1, (xb, t1[1])); s.wire(t2, (xb, t2[1]))
        s.wire((xb, t1[1]), (xb, t1[1] - g(3)))
        s.wire((xb, t1[1]), (xb, t2[1]))
        s.power("power:+3V3", sup, xb, t1[1] - g(3))
        s.wire((xb, t2[1]), (xb + g(8), t2[1]))
        Cc = vpart(s, "Device:C", cref(), xb + g(8), t2[1], "22nF 50V", "C106222")
        s.power(GND, "GND_L", *Cc.pin("2"))
        s.stub(J.pin("9"), (1, 0), g(4), net=net)                               # green LED anode
        e = s.stub(J.pin("10"), (1, 0), g(4)); s.power(GND, "GND_L", *e)       # cathode
        s.no_connect(*J.pin("12")); s.no_connect(*J.pin("11")); s.no_connect(*J.pin("7"))
        sp = [J.pin("8"), J.pin("SH1"), J.pin("SH2")]
        xs = sp[0][0] + g(4)
        for pt in sp:
            s.wire(pt, (xs, pt[1]))
        s.wire((xs, sp[0][1]), (xs, sp[-1][1]))
        s.stub((xs, sp[-1][1]), (1, 0), g(2), net="SHIELD")

    # ---- shield to PE: 1 nF / 2 kV in parallel with 1 M
    sx, sy = g(298), g(150)
    s.wire((sx - g(8), sy), (sx, sy))
    s.label("SHIELD", sx - g(8), sy, 180)
    Cs = vpart(s, "Device:C", cref(), sx, sy, "1nF 2kV", "C9196")
    Rs = vpart(s, "Device:R", rref(), sx + g(16), sy, "1M", "C22935")
    s.wire(Cs.pin("1"), Rs.pin("1"))
    s.wire(Cs.pin("2"), Rs.pin("2"))
    s.power("power:Earth_Protective", "PE", *Cs.pin("2"))
    s.pwr_flag(sx + g(11), Cs.pin("2")[1])

    # ============================================================ U401 unit 2: power pins (left) with their decoupling
    PX, PY = g(66), g(94)
    UP = s.place("lcsc:C80933", "U401", PX, PY, value="LAN9252I/PT", lcsc="C80933", unit=2,
                 ref_at=(PX - g(6), PY - g(58)), val_at=(PX + g(6), PY - g(58)), justify="center")
    Q = UP.pin
    x5 = Q("5")[0]
    rail_a = x5 - g(24)
    s.power("power:+3V3", "+3V3", rail_a, Q("5")[1] - g(3))
    s.wire((rail_a, Q("5")[1] - g(3)), (rail_a, Q("58")[1]))
    for num in ("5", "14", "20", "32", "37", "47", "7"):
        px, py = Q(num)
        s.wire((px, py), (rail_a, py))
        if num != "7":
            Cd = vpart(s, "Device:C", cref(), px - g(6), py, "100nF", "C1591")
            s.power(GND, "GND_L", *Cd.pin("2"))
    # the three PHY supplies each come through their own ferrite bead (EVB reference): FB > node (100 nF) > pin
    for num, net, fb in (("51", "+3V3_TXRX1", "FB401"), ("64", "+3V3_TXRX2", "FB402"), ("58", "+3V3_BIAS", "FB403")):
        px, py = Q(num)
        F = hpart(s, "lcec:FerriteBead_H", fb, px - g(19), py, "220R@100MHz", "C85827")
        s.wire((rail_a, py), F.pin("1"))
        s.wire(F.pin("2"), (px, py))
        Cd = vpart(s, "Device:C", cref(), px - g(9), py, "100nF", "C1591")
        s.power(GND, "GND_L", *Cd.pin("2"))
        s.wire((px - g(5), py), (px - g(5), py - g(4)))
        s.power("power:+3V3", net, px - g(5), py - g(4))
        s.pwr_flag(px - g(2), py)
    # core: VDDCR (internal regulator output) feeds the PHY 1.2 V pins through a ferrite bead (EVB reference)
    rail_r = Q("6")[0] + g(26)
    y_fb = Q("38")[1] + g(5)
    s.wire((rail_r, Q("6")[1]), (rail_r, y_fb))
    for num in ("6", "24", "38"):
        px, py = Q(num)
        s.wire((px, py), (rail_r, py))
    s.label("VDDCR", rail_r, y_fb, 180)
    for num, caps in (("6", (("1uF", "C559769"), ("470pF", "C1620"))), ("24", (("100nF", "C1591"),)), ("38", (("100nF", "C1591"),))):
        px, py = Q(num)
        for k, (val, code) in enumerate(caps):
            Cd = vpart(s, "Device:C", cref(), px + g(6) + g(10) * k, py, val, code)
            s.power(GND, "GND_L", *Cd.pin("2"))
    F4 = hpart(s, "lcec:FerriteBead_H", "FB404", rail_r, y_fb, "220R@100MHz", "C85827")
    rail_o = F4.pin("2")[0] + g(4)
    s.wire(F4.pin("2"), (rail_o, y_fb))
    s.wire((rail_o, y_fb), (rail_o, Q("59")[1] + g(3)))
    s.label("VDD12TX", rail_o, Q("59")[1] + g(3), 0)
    for num in ("56", "59"):
        px, py = Q(num)
        s.wire((px, py), (rail_o, py))
    for k in range(2):
        px, py = Q("56")
        Cd = vpart(s, "Device:C", cref(), px + g(6) + g(12) * k, py, "100nF", "C1591")
        s.power(GND, "GND_L", *Cd.pin("2"))
    s.no_connect(*Q("3"))                                           # OSCVDD12: internal regulator output, no external capacitor required
    g1, g2 = Q("4"), Q("65")
    s.wire(g1, (g1[0] + g(4), g1[1])); s.wire(g2, (g2[0] + g(4), g2[1]))
    s.wire((g1[0] + g(4), g1[1]), (g2[0] + g(4), g2[1]))
    s.power(GND, "GND_L", g2[0] + g(4), g2[1])

    # ============================================================ U402 ESI EEPROM
    ex, ey = g(124), g(128)
    E = s.place("lcsc:C615715", "U402", ex, ey, value="24LC32AT-I/SN", lcsc="C615715",
                ref_at=(ex, ey - g(11)), val_at=(ex, ey + g(11)), justify="center")
    gp = [E.pin(n) for n in ("1", "2", "3", "7", "4")]            # A0, A1, A2, WP, VSS all to ground
    xg = gp[0][0] - g(4)
    for pt in gp:
        s.wire(pt, (xg, pt[1]))
    s.wire((xg, gp[0][1]), (xg, gp[-1][1]))
    s.power(GND, "GND_L", xg, gp[-1][1])
    vc = E.pin("8")
    xv = vc[0] - g(12)
    s.wire(vc, (xv, vc[1]))
    s.wire((xv, vc[1]), (xv, vc[1] - g(3)))
    s.power("power:+3V3", "+3V3", xv, vc[1] - g(3))
    Ce = vpart(s, "Device:C", cref(), xv, vc[1], "100nF", "C1591")
    s.power(GND, "GND_L", *Ce.pin("2"))
    for num, net in (("6", "EESCL"), ("5", "EESDA")):
        pt = E.pin(num)
        xp = pt[0] + g(8)
        s.wire(pt, (xp, pt[1]))
        Rp = vpart(s, "Device:R", rref(), xp, pt[1] - g(6), "4.7k", "C23162")
        s.power("power:+3V3", "+3V3", *Rp.pin("1"))
        s.stub((xp, pt[1]), (1, 0), g(4), net=net)

    # ============================================================ ERR LED (driven by the STM32, PD3)
    ex2, ey2 = g(20), g(30)
    s.wire((ex2, ey2), (ex2 + g(8), ey2))
    s.hlabel("ERR_LED", "input", ex2, ey2, 180)
    Re = hpart(s, "lcec:R_H", rref(), ex2 + g(8), ey2, "1k", "C21190")
    Le = hpart(s, "lcec:LED_AK_H", "LED402", Re.pin("2")[0] + g(4), ey2, "ERR", "C2286")
    s.wire(Re.pin("2"), Le.pin("2"))
    e = s.stub(Le.pin("1"), (1, 0), g(3)); s.power(GND, "GND_L", *e)
    note(s, "EtherCAT ERR LED, red: driven by STM32 pin PD3 (the LAN9252 has no ERR output)", ex2, ey2 - g(5))

    ny = g(184)
    note(s, "Design notes", g(10), ny, 1.27, True)
    for i, txt in enumerate((
            "RUNLED / E2PSIZE: 10 k pull-up = EEPROM size strap high (32 Kbit and up, 2-byte addressing). The pin is open drain, so the RUN LED is +3V3 > 1 k > LED > pin.",
            "LINKACTLED0 / CHIP_MODE0 and LINKACTLED1 / CHIP_MODE1: 10 k pull-downs = chip mode 00 (2 ports) and active-high LED outputs; 1 k to the green LED in each jack.",
            "TESTMODE to ground (required). FXLOSEN, FXSDENA and FXSDENB to ground = copper twisted pair. REG_EN to 3.3 V = internal 1.2 V regulators. OSCO open (single-ended oscillator on OSCI).",
            "Pins 12, 15 to 16, 21 to 23, 25 to 31, 33, 35, 36, 39, 40 and 49 (host bus, MII, digital I/O) are unused in SPI mode and left open.",
            "As in the EVB-LAN9252-SPI reference: VDD33TXRX1, VDD33TXRX2 and VDD33BIAS each come from +3V3 through a 220 R ferrite bead with 100 nF; VDD12TX1/2 come from VDDCR through a ferrite bead with 2 x 100 nF.",
            "Each twisted-pair line has 49.9 R to its port's filtered 3.3 V; the magnetics centre taps (TXCT and RXCT together) are on the same net with 22 nF. RBIAS 12.1 k 1 % to ground. VDDCR: 1 uF + 470 pF at pin 6, 100 nF at pins 24 and 38.",
            "The ESI EEPROM must hold PDI = SPI before the first run. WP is low so the master can write it (the EVB ties WP high).")):
        note(s, txt, g(10), ny + g(4 + 3 * i))
    return s


# =============================================================== root sheet
def build_root(libs):
    s = G.Sch(libs, "lcec-io.kicad_sch", "LCEC-IO - EtherCAT slave I/O board", "1", ROOT_UUID, ROOT_UUID,
              comment="Root sheet: all eight sheets; the block diagram, mounting holes and PE follow in M6")
    s.text("LCEC-IO  -  EtherCAT slave I/O board", g(12), g(12), 3.0, justify="left bottom")
    s.text("Root sheet: Power (2), MCU (3), EtherCAT (4), Inputs (5), MPG (6), Relays (7), Analog (8), the PE terminal, "
           "the four M3 mounting holes and a block diagram of the isolation domains.", g(12), g(18))
    s.sheet("Power", "02_power.kicad_sch", g(20), g(30), g(40), g(24), [], 2, SHEET_UUID["power"])
    my = g(70)
    mx, mw = g(120), g(40)
    left = [("MPG_A", 4), ("MPG_B", 8), ("RELAY_OE", 12), ("DI[1..8]", 36), ("SEL[1..12]", 44)]
    right = [(n, 4 + 2 * i) for i, n in enumerate(ETH_NETS)] + [("DO[1..8]", 40), ("DAC_SCK", 60), ("DAC_MOSI", 62), ("DAC_CS", 64), ("AO_CLAMP", 66)]
    assert {n for n, _ in left + right} == set(MCU_HLABELS), set(MCU_HLABELS) ^ {n for n, _ in left + right}
    pins = [(n, MCU_HLABELS[n], "left", g(d)) for n, d in left] + [(n, MCU_HLABELS[n], "right", g(d)) for n, d in right]
    pos = s.sheet("MCU", "03_mcu.kicad_sch", mx, my, mw, g(76), pins, 3, SHEET_UUID["mcu"])

    def bus_or_wire(a, b, name):
        (s.bus if "[" in name else s.wire)(a, b)

    # left of the MCU: MPG (6) and Inputs (5)
    sh = {"output": "output", "input": "input"}
    mp = s.sheet("MPG", "06_mpg.kicad_sch", g(50), my, g(40), g(24),
                 [("MPG_A", "output", "right", g(4)), ("MPG_B", "output", "right", g(8)), ("RELAY_OE", "input", "right", g(12)),
                  ("OE_FIELD", "output", "right", g(16))], 6, SHEET_UUID["mpg"])
    for n in ("MPG_A", "MPG_B", "RELAY_OE"):
        s.wire(mp[n], pos[n])
    s.stub(mp["OE_FIELD"], (1, 0), g(8), net="OE_FIELD")
    ip = s.sheet("Inputs", "05_inputs.kicad_sch", g(50), my + g(32), g(40), g(20),
                 [("DI[1..8]", "output", "right", g(4)), ("SEL[1..12]", "output", "right", g(12))], 5, SHEET_UUID["inputs"])
    for n in ("DI[1..8]", "SEL[1..12]"):
        s.bus(ip[n], pos[n])
    # right of the MCU: EtherCAT (4), Relays (7) and Analog (8)
    ex = g(180)
    epins = [(n, ETH_NETS[n], "left", g(4) + i * g(2)) for i, n in enumerate(ETH_NETS)]
    epos = s.sheet("EtherCAT", "04_ethercat.kicad_sch", ex, my, g(40), g(4) + len(ETH_NETS) * g(2) + g(4), epins, 4, SHEET_UUID["ethercat"])
    for n in ETH_NETS:
        s.wire(pos[n], epos[n])
    rp = s.sheet("Relays", "07_relays.kicad_sch", ex, my + g(36), g(40), g(16),
                 [("DO[1..8]", "input", "left", g(4)), ("OE_FIELD", "input", "left", g(8))], 7, SHEET_UUID["relays"])
    s.bus(pos["DO[1..8]"], rp["DO[1..8]"])
    s.stub(rp["OE_FIELD"], (-1, 0), g(8), net="OE_FIELD")
    ap = s.sheet("Analog", "08_analog.kicad_sch", ex, my + g(56), g(40), g(16),
                 [("DAC_SCK", "input", "left", g(4)), ("DAC_MOSI", "input", "left", g(6)), ("DAC_CS", "input", "left", g(8)),
                  ("AO_CLAMP", "input", "left", g(10))], 8, SHEET_UUID["analog"])
    for n in ("DAC_SCK", "DAC_MOSI", "DAC_CS", "AO_CLAMP"):
        s.wire(pos[n], ap[n])

    # ---- protective earth: screw terminal J101 (the EtherCAT jack shields come here through 1 nF / 1 M, sheet 4)
    J = s.place("lcsc:C5272782", "J101", g(40), g(155), value="PE", lcsc="C5272782",
                ref_at=(g(44), g(152)), val_at=(g(44), g(158)), justify="left")
    e = s.stub(J.pin("1"), (-1, 0), g(10))
    s.power("power:Earth_Protective", "PE", *e)
    s.place("lcec:Accessory", "SC101", g(60), g(155), value="M3 x 6 screw for J101", lcsc="C357543", in_bom=True, on_board=False, footprint="",
            ref_at=(g(66), g(155)), val_at=(g(78), g(155)), justify="left")
    s.text("PE terminal (M3 ring lug). The Keystone 7770 ships without its screw, so the screw is a separate part.", g(22), g(148))
    # ---- mounting holes (M3, not connected)
    for i, (hx, hy) in enumerate(((g(12), g(20)), (g(12), g(190)), (g(310), g(20)), (g(310), g(190)))):
        s.place("Mechanical:MountingHole", f"H10{i + 1}", hx, hy, value="M3", footprint="MountingHole:MountingHole_3.2mm_M3", in_bom=False,
                props={"LCSC": "n/a (mechanical)"}, ref_at=(hx + g(3), hy - g(1)), val_at=(hx + g(3), hy + g(1)), justify="left")

    # ---- block diagram: the four isolation domains and what straddles each barrier
    bx = g(232)
    s.text("Block diagram: isolation domains", bx, g(26), size=1.8, bold=True)
    boxes = (("LOGIC  GND_L", bx, ("3 MCU: STM32F405", "4 EtherCAT: LAN9252, 2 x RJ45", "2 Power: URB2403S", "logic side of the isolators")),
             ("FIELD I/O  0V_IO", bx + g(30), ("5 Inputs: 20 x TLP290", "6 MPG: receiver", "7 Relays: driver, coils", "2 Power: URB2405S")),
             ("MAINS  load return", bx + g(60), ("7 Relays: 8 contacts", "8 x T5A fuse", "8 x 3-pole terminal", "(behind a routed slot)")))
    for title, x0, lines in boxes:
        s.box(x0, g(32), x0 + g(26), g(62), dashed=False)
        s.text(title, x0 + g(1), g(35), bold=True)
        for i, ln in enumerate(lines):
            s.text(ln, x0 + g(1), g(40) + i * g(4))
    s.box(bx + g(30), g(78), bx + g(56), g(100), dashed=False)
    s.text("ANALOG  AGND", bx + g(31), g(81), bold=True)
    s.text("8 Analog: DAC, op-amps", bx + g(31), g(86))
    s.text("2 Power: URB2415S", bx + g(31), g(90))
    s.text("AO terminals", bx + g(31), g(94))
    s.dashed_line(bx + g(28), g(30), bx + g(28), g(66))
    s.dashed_line(bx + g(58), g(30), bx + g(58), g(66))
    s.dashed_line(bx + g(28), g(70), bx + g(58), g(70)) if False else None
    note(s, "Every signal that crosses a barrier goes through one of these parts:", bx, g(108), 1.27, True)
    for i, ln in enumerate(("logic | field:  U501 to U505 (optocouplers), U602, U701, U702 (isolators)",
                            "logic | analog: U801 (isolator)",
                            "logic | 24V_LOGIC: U201 (DC-DC);  field | 24V_IO: U202, U203 (DC-DC)",
                            "field | analog: U203 (DC-DC, isolated AGND)",
                            "field | mains: K701 to K708 (coil side to contact side)")):
        s.text(ln, bx, g(113) + i * g(4))
    return s


def main():
    libs = G.Libs()
    os.makedirs(HW, exist_ok=True)
    out = [build_power(libs).write(HW)]
    out.append(build_mcu(libs).write(HW))
    out.append(build_ethercat(libs).write(HW))
    import sheets_io
    out.append(sheets_io.build_input4(libs, ROOT_UUID, SHEET_UUID["inputs"], SHEET_UUID["in4"]).write(HW))
    out.append(sheets_io.build_inputs(libs, ROOT_UUID, SHEET_UUID["inputs"], SHEET_UUID["in4"]).write(HW))
    out.append(sheets_io.build_mpg(libs, ROOT_UUID, SHEET_UUID["mpg"]).write(HW))
    out.append(sheets_io.build_relays(libs, ROOT_UUID, SHEET_UUID["relays"]).write(HW))
    out.append(sheets_io.build_analog(libs, ROOT_UUID, SHEET_UUID["analog"]).write(HW))
    out.append(build_root(libs).write(HW))
    print("wrote", *[os.path.basename(p) for p in out])


if __name__ == "__main__":
    main()
