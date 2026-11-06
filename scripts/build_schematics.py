#!/usr/bin/env python3
"""Generate the KiCad schematics for M3: root sheet, 2 Power and 3 MCU.

    python3 -I scripts/build_schematics.py

Writes hardware/*.kicad_sch (native KiCad 10 format via `kicad-cli sch upgrade`). Deterministic:
re-running produces identical files. Checks live in scripts/check_sheets.py.
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


def testpoint(s, ref, net, x, y):
    s.place("Connector:TestPoint", ref, x, y, 0, value=net, footprint=TP_FP, in_bom=False,
            props={"LCSC": "n/a (bare pad)"}, show_value=False, ref_at=(x + g(2), y - g(2)), val_at=(x + g(2), y - g(4)))


def note(s, text, x, y, size=1.27, bold=False):
    s.text(text, x, y, size=size, bold=bold)


# =============================================================== sheet 2: power
def build_power(libs):
    s = G.Sch(libs, "02_power.kicad_sch", "LCEC-IO - 2 Power", "2", ROOT_UUID, SHEET_UUID["power"],
              comment="Two 24 V entries, protection, three isolated DC-DC modules")
    TVS = "C320242"      # SMBJ33A (approved plan part; see the M3 PR for the proposed SMBJ30A swap)
    OX = g(190)           # module origin x; the isolation barrier is drawn here

    note(s, "2  POWER  -  24 V entries, protection, three isolated DC-DC modules", g(12), g(12), 2.54, True)
    note(s, "Input 24 VDC +/-20 % = 19.2 ... 28.8 V. Chain per input: fuse > SS54 reverse-polarity diode > SMBJ33A TVS "
            "> 47 uF + 1 uF > 100 uF/100 V at each module (URB datasheet Cin).", g(12), g(18))

    # ---- entry connector: pins 4..1 top to bottom after the 180 degree turn, fanned out so labels never collide
    jx, jy = g(22), g(100)
    J = s.place("lcsc:C441206", "J201", jx, jy, 180, value="24 V entry", lcsc="C441206",
                ref_at=(jx, jy - g(9)), val_at=(jx, jy - g(7)), justify="center")

    def fan(pin, x_off, dy, kind, net):
        p0 = J.pin(pin)
        xe = p0[0] + g(x_off)
        end = (xe, p0[1] + g(dy))
        s.wire(p0, (xe, p0[1]), end)
        if kind == "label":
            s.label(net, end[0], end[1], 0)
        else:
            s.power("power:GND", net, *end)
        return end

    fan("4", 4, -20, "gnd", "0V_IO")
    fan("3", 8, -10, "label", "24V_IO_IN")
    e2 = fan("2", 8, 10, "gnd", "0V_LOGIC")
    s.pwr_flag(e2[0], e2[1] - g(5))                                  # 0V_LOGIC has no output power pin
    fan("1", 4, 20, "label", "24V_LOGIC_IN")
    note(s, "pin 1 +24V_LOGIC, 2 0V_LOGIC, 3 +24V_IO, 4 0V_IO", g(10), g(128))

    def protection(y, net_in, rail_net, ret_net, ref_f, ref_tvs, ref_d, ref_c47, ref_c1, amps):
        x0 = g(52)
        F = s.place2("lcsc:C206887", ref_f, "1", "2", (x0, y), "right", value=f"{amps} A 5x20 fuse", lcsc="C206887")
        s.stub(F.pin("1"), (-1, 0), g(6), net=net_in, label_rot=180)
        D = s.place2("lcsc:C22452", ref_d, "1", "2", (x0 + g(18), y), "right", value="SS54", lcsc="C22452")
        s.wire(F.pin("2"), D.pin("1"))
        rail_end = (g(150), y)
        s.wire(D.pin("2"), rail_end)
        T = s.place2("lcsc:" + TVS, ref_tvs, "1", "2", (g(84), y), "down", value="SMBJ33A", lcsc=TVS)
        s.power("power:GND", ret_net, *T.pin("2"))
        C = s.place2("lcsc:C970679", ref_c47, "1", "2", (g(100), y), "down", value="47uF 50V", lcsc="C970679")
        s.power("power:GND", ret_net, *C.pin("2"))
        C1 = s.place2("Device:C", ref_c1, "1", "2", (g(116), y), "down", value="1uF 50V", lcsc="C91185")
        s.power("power:GND", ret_net, *C1.pin("2"))
        s.power("power:+24V", rail_net, g(128), y)           # names the protected rail
        s.pwr_flag(g(137), y)
        return rail_end

    y_io, y_lg = g(50), g(150)
    protection(y_io, "24V_IO_IN", "+24V_IO", "0V_IO", "F202", "D202", "D204", "C205", "C206", 3)
    protection(y_lg, "24V_LOGIC_IN", "+24V_LOGIC", "0V_LOGIC", "F201", "D201", "D203", "C201", "C202", 1)
    testpoint(s, "TP201", "+24V_IO", g(144), y_io)
    testpoint(s, "TP202", "+24V_LOGIC", g(144), y_lg)

    def module(ref, code, oy, vin_y, rail_x, out_pos, out_neg, cin_ref, cout_ref, ret_net, tp_ref, tp_net, mpn, cout_val, cout_code):
        """URB module with VIN wired to the rail at y=vin_y."""
        U = s.place("lcsc:" + code, ref, OX, oy, 0, value=mpn, lcsc=code,
                    ref_at=(OX + g(4), oy - g(11)), val_at=(OX + g(4), oy + g(14)), justify="left")
        s.wire((rail_x, vin_y), U.pin("2"))
        s.no_connect(*U.pin("3"))                      # Ctrl open = module on
        s.no_connect(*U.pin("5")); s.no_connect(*U.pin("8"))
        g1 = U.pin("1")
        e = s.stub(g1, (-1, 0), g(5)); s.stub(e, (0, 1), g(4)); s.power("power:GND", ret_net, e[0], e[1] + g(4))
        Cin = s.place2("lcsc:C2960285", cin_ref, "1", "2", (OX - g(34), vin_y), "down", value="100uF 100V", lcsc="C2960285")
        s.power("power:GND", ret_net, *Cin.pin("2"))
        vp, vn = U.pin("6"), U.pin("7")
        xo = vp[0] + g(26)
        s.wire(vp, (xo, vp[1]))
        s.power(out_pos[0], out_pos[1], xo, vp[1])
        Co = s.place2("Device:C", cout_ref, "1", "2", (vp[0] + g(8), vp[1]), "down", value=cout_val, lcsc=cout_code)
        s.power(out_neg[0], out_neg[1], *Co.pin("2"))
        n = s.stub(vn, (1, 0), g(5)); s.power(out_neg[0], out_neg[1], *n)
        testpoint(s, tp_ref, tp_net, vp[0] + g(17), vp[1])
        return U

    rail_x = g(150)
    oy202, oy203 = y_io + g(4), y_io + g(36)
    s.wire((rail_x, y_io), (rail_x, oy203 - g(4)))          # rail drop to the second module
    module("U202", "C3031185", oy202, y_io, rail_x, ("power:+5V", "+5V_IO"), ("power:GND", "0V_IO"),
           "C207", "C208", "0V_IO", "TP203", "+5V_IO", "URB2405S-6WR3", "22uF 25V", "C45783")
    module("U203", "C5369844", oy203, oy203 - g(4), rail_x, ("power:+15V", "+15V_A"), ("power:GNDA", "AGND"),
           "C209", "C210", "0V_IO", "TP204", "+15V_A", "URB2415S-6WR3", "22uF 25V", "C45783")
    module("U201", "C5369843", y_lg + g(4), y_lg, g(150), ("power:+3V3", "+3V3"), ("power:GND", "GND_L"),
           "C203", "C204", "0V_LOGIC", "TP205", "+3V3", "URB2403S-6WR3", "22uF 25V", "C45783")
    testpoint(s, "TP206", "0V_IO", g(22), g(60)); s.power("power:GND", "0V_IO", g(22), g(60))
    testpoint(s, "TP207", "0V_LOGIC", g(22), g(160)); s.power("power:GND", "0V_LOGIC", g(22), g(160))

    # ---- isolation barrier and domain captions
    s.dashed_line(OX, g(30), OX, g(190))
    s.text("24V_IO domain  (0V_IO)", OX - g(3), g(32), justify="right bottom")
    s.text("isolated outputs", OX + g(3), g(32), justify="left bottom")
    s.text("U202: +5V_IO, its 0 V is tied to 0V_IO at the module (not isolated)", OX + g(3), g(34), justify="left bottom")
    s.text("U203: +15V_A on its own isolated AGND", OX + g(3), g(36), justify="left bottom")
    s.text("24V_LOGIC domain  (0V_LOGIC)", OX - g(3), g(132), justify="right bottom")
    s.text("U201: +3V3 on isolated GND_L", OX + g(3), g(132), justify="left bottom")

    # ---- notes with the key numbers
    note(s, "Loads: +3V3 about 0.4 A of the module's 1.35 A (30 %). 24V_LOGIC input about 0.3 A at full module load: 1 A fuse.", g(12), g(210))
    note(s, "24V_IO: 5 V module 7.3 W + 15 V module 7 W at full load = 0.75 A, plus relay coils 0.18 A and sensors via PTC: 3 A fuse.", g(12), g(213))
    note(s, "URB input 9-36 V (40 V absolute max, 50 V for 1 s surge). SMBJ33A clamps 53.3 V at 11.3 A: see the PR for the proposed SMBJ30A (48.4 V).", g(12), g(216))
    note(s, "CTRL pin left open = module on. NC pins are not connected inside the module.", g(12), g(219))

    # ---- accessories that are in the BOM but not on the PCB (pin-less symbols), in the empty middle of the sheet
    bx, by = g(52), g(80)
    s.box(bx, by, bx + g(96), by + g(30), dashed=True)
    note(s, "BOM accessories (not on the PCB)", bx + g(2), by + g(3), bold=True)
    acc = [("FU201", "C3116", "1 A 5x20 glass fuse (in F201)", 0, 0), ("FU202", "C3118", "3 A 5x20 glass fuse (in F202)", 0, 1),
           ("FC201", "C187509", "clear cover for F201", 0, 2), ("FC202", "C187509", "clear cover for F202", 0, 3),
           ("P201", "C440882", "4-pole cable plug (for J201)", 0, 4)]
    for ref, code, txt, col, row in acc:
        ax, ay = bx + g(4 + 48 * col), by + g(8 + 4 * row)
        s.place("lcsc:" + code, ref, ax, ay, 0, value=txt, lcsc=code, in_bom=True, on_board=False,
                ref_at=(ax + g(22), ay), val_at=(ax + g(30), ay), justify="left")
    return s


# =============================================================== sheet 3: MCU
MCU_X, MCU_Y = g(166), g(115)
HX_LEFT, HX_RIGHT = g(22), g(300)          # x of hierarchical labels at the left and right sheet edges

# hierarchical labels of the MCU sheet: name -> shape (also drives the root sheet pins)
MCU_HLABELS = {}


def build_mcu(libs):
    from pin_tables import T
    s = G.Sch(libs, "03_mcu.kicad_sch", "LCEC-IO - 3 MCU", "3", ROOT_UUID,
              SHEET_UUID["mcu"], comment="STM32F405VGT6 (LQFP-100), shared clock, SWD, UART, heartbeat LED")
    byname = {}
    for num, nm in T["C56621"]["pins"].items():
        byname.setdefault(nm[0], []).append(str(num))

    note(s, "3  MCU  -  STM32F405VGT6, shared 25 MHz clock, SWD, UART2, heartbeat LED", g(12), g(12), 2.54, True)
    note(s, "Pin map: docs/plan.md (MCU sheet). 51 signals used, PH1 is a test pad, the 30 pins of ports D and E are free for future use (no-connect flags).", g(12), g(18))
    note(s, "Firmware: HSE bypass with the 25 MHz oscillator, PLLM 25 / PLLN 336 / PLLP 2 = 168 MHz. IWDG enabled in option bytes (fail-safe).", g(12), g(21))

    U = s.place("lcsc:C56621", "U301", MCU_X, MCU_Y, 0, value="STM32F405VGT6", lcsc="C56621",
                ref_at=(MCU_X, MCU_Y - g(3)), val_at=(MCU_X, MCU_Y + g(3)), justify="center")
    P = lambda name, i=0: U.pin(byname[name][i])   # noqa: E731
    cap_n = [0]

    def cref(): cap_n[0] += 1; return f"C3{cap_n[0]:02d}"   # noqa: E702
    res_n = [0]

    def rref(): res_n[0] += 1; return f"R3{res_n[0]:02d}"   # noqa: E702

    # ------------------------------------------------------------ supplies, top
    rail_y, tap_y = g(40), g(50)
    vbat, vdds = P("VBAT"), [P("VDD", i) for i in range(6)]
    x_left = vbat[0] - g(14)
    vdda, vref = P("VDDA"), P("VREF+")
    x_fb = vref[0] + g(10)
    s.wire((x_left, rail_y), (x_fb, rail_y))
    s.power("power:+3V3", "+3V3", x_left, rail_y)
    for pt in [vbat] + vdds:
        s.wire(pt, (pt[0], rail_y))
        C = s.place2("Device:C", cref(), "1", "2", (pt[0] - g(4), tap_y), "down", value="100nF", lcsc="C1591",
                     show_value=False, ref_at=(pt[0] - g(6), tap_y + g(3)), ref_rot=90, justify="center")
        s.wire((pt[0], tap_y), (pt[0] - g(4), tap_y))
        s.power("power:GND", "GND_L", *C.pin("2"))
    note(s, "100 nF at VBAT and at each VDD pin, drawn beside the pin it serves", vbat[0] - g(10), g(34))
    # bulk 4.7 uF
    Cb = s.place2("Device:C", cref(), "1", "2", (x_left + g(8), rail_y), "down", value="4.7uF", lcsc="C19666",
                  ref_at=(x_left + g(11), rail_y + g(2)), val_at=(x_left + g(11), rail_y + g(4)))
    s.power("power:GND", "GND_L", *Cb.pin("2"))
    # VDDA through a ferrite, 1 uF + 100 nF; VREF+ tied to VDDA
    va_y = g(52)
    FB = s.place2("Device:FerriteBead", "FB301", "1", "2", (x_fb, rail_y), "down", value="600R@100MHz", lcsc="C19330",
                  ref_at=(x_fb + g(3), rail_y + g(2)), val_at=(x_fb + g(3), rail_y + g(4)))
    s.wire(vdda, (vdda[0], va_y)); s.wire(vref, (vref[0], va_y))
    s.wire(FB.pin("2"), (x_fb, va_y))
    s.wire((vdda[0], va_y), (x_fb + g(18), va_y))
    s.label("VDDA", vdda[0] + g(2), va_y, 90)
    s.pwr_flag(vdda[0] + g(5), va_y)              # VDDA/VREF+ are fed through a passive ferrite
    for k, (val, code) in enumerate((("1uF", "C559769"), ("100nF", "C1591"))):
        cx = x_fb + g(8) + k * g(10)
        Cv = s.place2("Device:C", cref(), "1", "2", (cx, va_y), "down", value=val, lcsc=code,
                      ref_at=(cx + g(3), va_y + g(2)), val_at=(cx + g(3), va_y + g(4)))
        s.power("power:GND", "GND_L", *Cv.pin("2"))
    # ------------------------------------------------------------ supplies, bottom
    vss = [P("VSS", i) for i in range(4)] + [P("VSSA")]
    gy = vss[0][1] + g(4)
    for pt in vss:
        s.wire(pt, (pt[0], gy))
    s.wire((vss[0][0], gy), (vss[-1][0], gy))
    s.power("power:GND", "GND_L", vss[0][0], gy)
    for nm in ("VCAP_1", "VCAP_2"):
        pt = P(nm)
        C = s.place2("Device:C", cref(), "1", "2", pt, "down", value="2.2uF", lcsc="C23630",
                     ref_at=(pt[0] + g(3), pt[1] + g(3)), val_at=(pt[0] + g(3), pt[1] + g(5)))
        s.power("power:GND", "GND_L", *C.pin("2"))
    note(s, "VCAP_1 and VCAP_2: 2.2 uF each (low ESR)", vss[-1][0] + g(8), vss[0][1] + g(15))

    # ------------------------------------------------------------ signal sides
    def hl(name, shape, x, y, rot):
        MCU_HLABELS[name] = shape
        s.hlabel(name, shape, x, y, rot)

    bus_info = {}
    for side, title, items in pinmap.LEFT_RIGHT:
        if title.startswith("Free"):
            for net, pname in items:
                s.no_connect(*P(pname))
            continue
        is_bus = title in ("DI1-8", "SEL1-12", "DO1-8")
        for idx, (net, pname) in enumerate(items):
            pt = P(pname)
            d = (-1, 0) if side == "left" else (1, 0)
            if is_bus:
                x_e = pt[0] + d[0] * g(12)
                s.wire(pt, (x_e, pt[1]))
                s.label(net, pt[0] + d[0] * g(2), pt[1], 180 if side == "left" else 0)
                # 45 degree entry up and away from the pin
                if side == "left":
                    s.bus_entry(x_e - g(2), pt[1] - g(2), g(2), g(2))
                    xb = x_e - g(2)
                else:
                    s.bus_entry(x_e, pt[1], g(2), -g(2))
                    xb = x_e + g(2)
                bus_info.setdefault(title, {"x": xb, "ys": [], "side": side})["ys"].append(pt[1] - g(2))
            elif net in ("NRST", "BOOT0", "CLK_MCU", "PH1_TP", "HB_LED", "SWDIO", "SWCLK", "SWO", "UART2_TX", "UART2_RX"):
                s.stub(pt, d, g(8), net=net)
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

    # ------------------------------------------------------------ 25 MHz oscillator block (top left)
    ox, oy = g(40), g(32)
    X = s.place("lcsc:C2595919", "X301", ox, oy, 0, value="25 MHz", lcsc="C2595919",
                ref_at=(ox, oy - g(7)), val_at=(ox, oy + g(7)), justify="center")
    e = s.stub(X.pin("1"), (-1, 0), g(6)); s.power("power:+3V3", "+3V3", *e)            # OE high = running
    e = s.stub(X.pin("2"), (-1, 0), g(6)); s.power("power:GND", "GND_L", *e)
    vd = X.pin("4")
    n = s.stub(vd, (1, 0), g(6)); s.power("power:+3V3", "+3V3", *n)
    Cx = s.place2("Device:C", cref(), "1", "2", n, "down", value="100nF", lcsc="C1591",
                  ref_at=(n[0] + g(3), n[1] + g(2)), val_at=(n[0] + g(3), n[1] + g(4)))
    s.power("power:GND", "GND_L", *Cx.pin("2"))
    out = X.pin("3")
    xo = out[0] + g(8)
    yo = out[1] + g(8)
    s.wire(out, (xo, out[1]), (xo, yo))
    R1 = s.place2("Device:R", rref(), "1", "2", (xo + g(4), yo), "right", value="22R", lcsc="C23345")
    s.wire((xo, yo), R1.pin("1"))
    s.stub(R1.pin("2"), (1, 0), g(5), net="CLK_MCU")
    R2 = s.place2("Device:R", rref(), "1", "2", (xo + g(4), yo + g(14)), "right", value="22R", lcsc="C23345")
    s.wire((xo, yo), (xo, yo + g(14)), R2.pin("1"))
    e2 = s.stub(R2.pin("2"), (1, 0), g(5))
    hl("CLK_ESC", "output", e2[0], e2[1], 0)
    note(s, "OE high = oscillator running. 22 R series resistors: PH0 (HSE bypass) and LAN9252 OSCI (sheet 4).", g(12), g(64))

    # ------------------------------------------------------------ reset, boot and fail-safe pull resistors (bottom left)
    by = g(178)
    s.box(g(14), by - g(8), g(70), by + g(36), dashed=False)
    note(s, "Boot, reset and fail-safe pull resistors", g(16), by - g(5), bold=True)

    def pull(x, net, code, rail, caption):
        R = s.place2("Device:R", rref(), "1", "2", (x, by + g(12)), "down", value="10k", lcsc=code,
                     ref_at=(x + g(3), by + g(14)), val_at=(x + g(3), by + g(16)))
        if rail == "down":          # pull-down: net on top, ground below
            s.stub(R.pin("1"), (0, -1), g(3), net=net, label_rot=90)
            s.power("power:GND", "GND_L", *R.pin("2"))
        else:                       # pull-up: +3V3 above, net below
            s.power("power:+3V3", "+3V3", *R.pin("1"))
            s.stub(R.pin("2"), (0, 1), g(3), net=net, label_rot=270)

    pull(g(20), "BOOT0", "C25804", "down", "BOOT0 low")
    C = s.place2("Device:C", cref(), "1", "2", (g(30), by + g(12)), "down", value="100nF", lcsc="C1591",
                 ref_at=(g(33), by + g(14)), val_at=(g(33), by + g(16)))
    s.stub(C.pin("1"), (0, -1), g(3), net="NRST", label_rot=90)
    s.power("power:GND", "GND_L", *C.pin("2"))
    pull(g(40), "RELAY_OE", "C25804", "down", "OE pull-down")
    pull(g(50), "AO_CLAMP", "C25804", "up", "clamp pull-up")
    pull(g(60), "ESC_RST", "C25804", "up", "RST# pull-up")
    note(s, "Fail-safe: PD2 low = relays off, PB14 high = analog outputs clamped, PC5 high = LAN9252 not in reset.", g(16), by + g(33))

    # ------------------------------------------------------------ debug and heartbeat (bottom right)
    jx, jy = g(256), g(135)
    J = s.place("lcsc:C3975188", "J301", jx, jy, 0, value="SWD 2x5 1.27 mm", lcsc="C3975188",
                ref_at=(jx, jy - g(8)), val_at=(jx, jy + g(8)), justify="center")
    e = s.stub(J.pin("1"), (-1, 0), g(4)); s.power("power:+3V3", "+3V3", *e)
    e3 = s.stub(J.pin("3"), (-1, 0), g(4)); e5 = s.stub(J.pin("5"), (-1, 0), g(4))
    s.wire(e3, e5); s.power("power:GND", "GND_L", *e5)          # pins 3 and 5 share one ground symbol
    e9 = s.stub(J.pin("9"), (-1, 0), g(4)); s.power("power:GND", "GND_L", *e9)
    s.no_connect(*J.pin("7")); s.no_connect(*J.pin("8"))
    s.stub(J.pin("2"), (1, 0), g(4), net="SWDIO")
    s.stub(J.pin("4"), (1, 0), g(4), net="SWCLK")
    s.stub(J.pin("6"), (1, 0), g(4), net="SWO")
    s.stub(J.pin("10"), (1, 0), g(4), net="NRST")
    note(s, "SWD (Cortex 10-pin): 1 VTref, 2 SWDIO, 3/5/9 GND, 4 SWCLK, 6 SWO, 7/8 not used, 10 NRST", g(236), g(122))
    ux, uy = g(256), g(157)
    Uj = s.place("lcsc:C2937625", "J302", ux, uy, 0, value="USART2", lcsc="C2937625",
                 ref_at=(ux, uy - g(5)), val_at=(ux, uy + g(5)), justify="center")
    s.stub(Uj.pin("1"), (-1, 0), g(4), net="UART2_TX")
    s.stub(Uj.pin("2"), (-1, 0), g(4), net="UART2_RX")
    e = s.stub(Uj.pin("3"), (-1, 0), g(4)); s.power("power:GND", "GND_L", *e)
    note(s, "USART2: 1 TX (PA2), 2 RX (PA3), 3 GND", g(236), g(147))

    hx, hy = g(282), g(157)
    Rh = s.place2("Device:R", rref(), "1", "2", (hx + g(6), hy), "right", value="1k", lcsc="C21190")
    s.stub(Rh.pin("1"), (-1, 0), g(6), net="HB_LED")
    Lh = s.place2("Device:LED", "LED301", "2", "1", (Rh.pin("2")[0] + g(4), hy), "right", value="heartbeat", lcsc="C2287")
    s.wire(Rh.pin("2"), Lh.pin("2"))
    e = s.stub(Lh.pin("1"), (1, 0), g(4)); s.power("power:GND", "GND_L", *e)
    note(s, "Heartbeat LED (PA1)", hx + g(6), hy - g(5))

    # ------------------------------------------------------------ test points
    tx0, ty = g(80), g(196)
    for k, net in enumerate(("ESC_SCK", "ESC_MISO", "ESC_MOSI", "ESC_CS", "DAC_SCK", "DAC_MOSI", "DAC_CS", "RELAY_OE",
                             "AO_CLAMP", "MPG_A", "MPG_B", "PH1_TP")):
        x = tx0 + k * g(10)
        s.place("Connector:TestPoint", f"TP3{k + 1:02d}", x, ty, 0, value=net, footprint=TP_FP, in_bom=False,
                props={"LCSC": "n/a (bare pad)"}, show_value=False, ref_at=(x, ty - g(6)), val_at=(x, ty - g(4)), justify="center")
        s.stub((x, ty), (0, 1), g(4), net=net, label_rot=270)
    note(s, "Test points: SPI1 (LAN9252), SPI2 (DAC), relay OE, analog clamp, MPG A/B and the spare pin PH1", tx0, ty - g(9))
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
