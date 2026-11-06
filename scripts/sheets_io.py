"""Sheets 5 to 8 (M5): digital inputs, MPG, relay outputs and analog outputs. Same drawing rules as the other sheets:
every symbol at rotation 0, all text horizontal, no vertical pins, supplies up and grounds down."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import schgen as G  # noqa: E402
from schgen import g  # noqa: E402
from drawing import GND, decap, hpart, note, tie, tie_bar, vpart  # noqa: E402

P5, P33, P15 = "power:+5V", "power:+3V3", "power:+15V"


def lrefs(base):
    return base


# =============================================================== sheet 6: MPG
def build_mpg(libs, root_uuid, sheet_uuid):
    s = G.Sch(libs, "06_mpg.kicad_sch", "LCEC-IO - 6 MPG", "6", root_uuid, sheet_uuid,
              comment="MPG 5 V differential receiver, isolated to the MCU; also carries the relay output enable")
    note(s, "6  MPG  -  5 V differential pulse generator input, isolated", g(10), g(8), 2.54, True)
    note(s, "A / A-bar / B / B-bar from the pendant are received by an AM26LS32A, isolated by a CA-IS3742LN and sent to PB4 / PB5 (TIM3 encoder). "
            "The same isolator carries the relay output enable (forward channel 1).", g(10), g(13))

    # ---- field connector: +5V_IO through a PTC, 0V_IO, A, A-bar, B, B-bar
    J = s.place("lcec:Conn_R_01x06", "J601", g(24), g(50), value="MPG", lcsc="C441208",
                ref_at=(g(20), g(44)), val_at=(g(20), g(66)), justify="right")
    p1 = J.pin("1")
    PT = s.place("lcsc:C70068", "RT601", p1[0] + g(11), p1[1] - g(1), value="0.25A PTC", lcsc="C70068",
                 ref_at=(p1[0] + g(11), p1[1] - g(7)), val_at=(p1[0] + g(11), p1[1] - g(5)), justify="center")
    s.wire(p1, PT.pin("1"))
    tie(s, PT.pin("2"), (1, 0), P5, "+5V_IO", 3)
    tie(s, J.pin("2"), (1, 0), GND, "0V_IO", 16)
    for pin, net in (("3", "ENC_A_P"), ("4", "ENC_A_N"), ("5", "ENC_B_P"), ("6", "ENC_B_N")):
        s.stub(J.pin(pin), (1, 0), g(6), net=net)
    note(s, "1 +5V_IO   2 0V_IO   3 A   4 A-bar   5 B   6 B-bar", g(10), g(70))

    # ---- TVS pair and 120 R termination (not fitted) per channel
    for k, (ref_d, ref_r, pa, pn, y) in enumerate((("D601", "R601", "ENC_A_P", "ENC_A_N", g(90)), ("D602", "R602", "ENC_B_P", "ENC_B_N", g(120)))):
        D = s.place("lcsc:C32677", ref_d, g(80), y, value="PSM712", lcsc="C32677",
                    ref_at=(g(80), y - g(9)), val_at=(g(80), y + g(9)), justify="center")
        a, b = D.pin("1"), D.pin("2")
        xn = a[0] - g(8)
        s.wire(a, (xn, a[1])); s.wire(b, (xn, b[1]))
        Rt = s.place("Device:R", ref_r, xn - g(8), a[1] + g(4), value="120R", lcsc="C22787", dnp=True,
                     ref_at=(xn - g(11), a[1] + g(3)), val_at=(xn - g(11), a[1] + g(5)), justify="right")
        s.wire((xn, a[1]), (xn - g(8), a[1])); s.wire((xn - g(8), a[1]), Rt.pin("1"))
        s.wire((xn, b[1]), (xn - g(8), b[1])); s.wire((xn - g(8), b[1]), Rt.pin("2"))
        s.stub((xn - g(8), a[1]), (-1, 0), g(6), net=pa)
        s.stub((xn - g(8), b[1]), (-1, 0), g(6), net=pn)
        tie(s, D.pin("3"), (1, 0), GND, "0V_IO", 4)
    note(s, "TVS pairs and unfitted 120 R terminations (20 kHz over 5 m does not need them)", g(30), g(75))

    # ---- U601 AM26LS32A
    U = s.place("lcsc:C6180", "U601", g(150), g(60), value="AM26LS32A", lcsc="C6180",
                ref_at=(g(150), g(40)), val_at=(g(150), g(82)), justify="center")
    for pin, net in (("2", "ENC_A_P"), ("1", "ENC_A_N"), ("6", "ENC_B_P"), ("7", "ENC_B_N")):
        s.stub(U.pin(pin), (-1, 0), g(6), net=net)
    tie_bar(s, [U.pin(n) for n in ("10", "9", "14", "15")], (-1, 0), GND, "0V_IO", 4)         # unused receivers 3 and 4
    tie_bar(s, [U.pin("16"), U.pin("4")], (1, 0), P5, "+5V_IO", 4)                              # VCC, G (active high) = enabled
    tie_bar(s, [U.pin("12"), U.pin("8")], (1, 0), GND, "0V_IO", 4)                              # ~G low, GND
    s.stub(U.pin("3"), (1, 0), g(6), net="ENC_A_R")
    s.stub(U.pin("5"), (1, 0), g(6), net="ENC_B_R")
    s.no_connect(*U.pin("11")); s.no_connect(*U.pin("13"))
    decap(s, g(172), g(88), P5, "+5V_IO", GND, "0V_IO", "C601")

    # ---- U602 CA-IS3742LN: field side left, logic side right
    ux, uy = g(240), g(60)
    I = s.place("lcsc:C5347249", "U602", ux, uy, value="CA-IS3742LN", lcsc="C5347249",
                ref_at=(ux - g(2), uy - g(20)), val_at=(ux + g(2), uy - g(20)), justify="right", val_justify="left")
    tie_bar(s, [I.pin("16"), I.pin("10")], (-1, 0), P5, "+5V_IO", 4)
    s.stub(I.pin("12"), (-1, 0), g(6), net="ENC_A_R")
    s.stub(I.pin("11"), (-1, 0), g(6), net="ENC_B_R")
    e = s.stub(I.pin("14"), (-1, 0), g(6))
    s.hlabel("OE_FIELD", "output", e[0], e[1], 180)
    s.no_connect(*I.pin("13"))
    tie_bar(s, [I.pin("15"), I.pin("9")], (-1, 0), GND, "0V_IO", 4)
    tie_bar(s, [I.pin("1"), I.pin("7")], (1, 0), P33, "+3V3", 4)
    for pin, name, shape in (("5", "MPG_A", "output"), ("6", "MPG_B", "output"), ("3", "RELAY_OE", "input")):
        e = s.stub(I.pin(pin), (1, 0), g(10))
        s.hlabel(name, shape, e[0], e[1], 0)
    tie(s, I.pin("4"), (1, 0), GND, "GND_L", 4)                                                  # spare channel input tied low
    tie_bar(s, [I.pin("2"), I.pin("8")], (1, 0), GND, "GND_L", 4)
    decap(s, ux - g(30), g(88), P5, "+5V_IO", GND, "0V_IO", "C602")
    decap(s, ux + g(26), g(88), P33, "+3V3", GND, "GND_L", "C603")
    s.dashed_line(ux, g(30), ux, g(105))
    s.text("FIELD side (0V_IO)", ux - g(2), g(34), justify="right bottom")
    s.text("LOGIC side (GND_L)", ux + g(2), g(34), justify="left bottom")

    # ---- accessory: pendant cable plug
    s.place("lcec:Accessory", "P601", g(30), g(165), value="6-pole cable plug for J601", lcsc="C440884", in_bom=True, on_board=False, footprint="",
            ref_at=(g(38), g(165)), val_at=(g(50), g(165)), justify="left")
    note(s, "Design notes", g(10), g(176), 1.27, True)
    for i, txt in enumerate((
            "AM26LS32A (0 to 70 C, SOIC-16) supplied from +5V_IO; G high and ~G low enable all receivers; the unused receivers 3 and 4 have their inputs grounded.",
            "RT601 limits the pendant supply to 0.25 A hold. PSM712 clamps each line pair (-7 V / +12 V). The 120 R terminations are not fitted.",
            "CA-IS3742LN: reverse channels 3 and 4 carry A and B to PB4 / PB5 (default output low). Forward channel 1 carries the relay output enable; channel 2 is spare, input tied low.")):
        note(s, txt, g(10), g(180) + g(3 * i))
    return s


# =============================================================== helpers shared by the sheets below
def accessory(s, ref, code, text, x, y, props=None, dnp=False):
    """Pin-less 'not on the PCB' symbol so the part appears in the BOM."""
    return s.place("lcec:Accessory", ref, x, y, value=text, lcsc=code, props=props, in_bom=True, on_board=False, footprint="", dnp=dnp,
                   ref_at=(x + g(5), y), val_at=(x + g(13), y), justify="left")


def bus_in(s, pins_nets, hx, hname, shape="input"):
    """Bus coming in from the left: pins_nets = [(pin point, net name)]. Wires with net labels, bus entries, one bus label."""
    ys = []
    xb = None
    for pt, net in pins_nets:
        x_e = pt[0] - g(12)
        s.wire(pt, (x_e, pt[1]))
        s.label(net, pt[0] - g(2), pt[1], 180)
        s.bus_entry(x_e - g(2), pt[1] - g(2), g(2), g(2))
        xb = x_e - g(2)
        ys.append(pt[1] - g(2))
    s.bus((xb, max(ys)), (xb, min(ys)), (hx, min(ys)))
    s.hlabel(hname, shape, hx, min(ys), 180)


# =============================================================== sheet 7: relay outputs
def build_relays(libs, root_uuid, sheet_uuid):
    s = G.Sch(libs, "07_relays.kicad_sch", "LCEC-IO - 7 Relays", "7", root_uuid, sheet_uuid,
              comment="8 relay outputs: isolated drive, ULN2803A, plug-in relays, fuse and ON LED per channel")
    note(s, "7  RELAY OUTPUTS  -  8 x Omron G2R-1-S DC24 in P2R-05P sockets, fuse and ON LED per channel", g(10), g(8), 2.54, True)
    note(s, "DO1 to DO8 pass two CA-IS3740LN isolators (output enable OE_FIELD from the MPG sheet) to one ULN2803A. All outputs are off when OE is low, "
            "the MCU resets or the logic supply is lost.", g(10), g(13))
    ux = g(60)
    do_pins = []
    # ---- isolators U701 (DO1-4) and U702 (DO5-8)
    for n, (ref, uy) in enumerate((("U701", g(50)), ("U702", g(100)))):
        U = s.place("lcsc:C428888", ref, ux, uy, value="CA-IS3740LN", lcsc="C428888",
                    ref_at=(ux - g(2), uy - g(17)), val_at=(ux + g(2), uy - g(17)), justify="right", val_justify="left")
        tie(s, U.pin("1"), (-1, 0), P33, "+3V3", 4)
        s.no_connect(*U.pin("7"))
        tie_bar(s, [U.pin("2"), U.pin("8")], (-1, 0), GND, "GND_L", 4)
        tie(s, U.pin("16"), (1, 0), P5, "+5V_IO", 4)
        e = s.stub(U.pin("10"), (1, 0), g(8))
        if n == 0:
            s.hlabel("OE_FIELD", "input", e[0], e[1], 0)
        else:
            s.label("OE_FIELD", e[0], e[1], 0)
        tie_bar(s, [U.pin("15"), U.pin("9")], (1, 0), GND, "0V_IO", 4)
        for k in range(4):
            s.stub(U.pin(str(14 - k)), (1, 0), g(6), net=f"IN{4 * n + k + 1}")
            do_pins.append((U.pin(str(3 + k)), f"DO{4 * n + k + 1}"))
        decap(s, ux - g(20), uy - g(30), P33, "+3V3", GND, "GND_L", f"C{701 + 2 * n}")
        decap(s, ux + g(32), uy - g(10), P5, "+5V_IO", GND, "0V_IO", f"C{702 + 2 * n}")
    bus_in(s, do_pins, g(16), "DO[1..8]")
    s.dashed_line(ux, g(28), ux, g(125))
    s.text("LOGIC (GND_L)", ux - g(2), g(30), justify="right bottom")
    s.text("DRIVER (0V_IO)", ux + g(2), g(30), justify="left bottom")

    # ---- ULN2803A
    U3 = s.place("lcsc:C845537", "U703", g(125), g(75), value="ULN2803A", lcsc="C845537",
                 ref_at=(g(125), g(61)), val_at=(g(125), g(90)), justify="center")
    for k in range(8):
        s.stub(U3.pin(str(k + 1)), (-1, 0), g(6), net=f"IN{k + 1}")
        s.stub(U3.pin(str(18 - k)), (1, 0), g(6), net=f"DRV{k + 1}")
    tie(s, U3.pin("9"), (-1, 0), GND, "0V_IO", 4)
    e = s.stub(U3.pin("10"), (1, 0), g(4))                                                  # COM: the flyback diodes return to +24V_IO
    e2 = (e[0], e[1] + g(6))
    s.wire(e, e2)
    s.power("power:+24V", "+24V_IO", *e2)
    # pull-downs: OE low = isolator outputs high-impedance = ULN inputs held low (2 x 4 x 100 k)
    for n, (ref, rx) in enumerate((("RN703", g(100)), ("RN704", g(124)))):
        RN = s.place("lcec:R_Pack04_H", ref, rx, g(112), value="4x100k", lcsc="C1996", text="above",
                     ref_at=(rx, g(104)), val_at=(rx, g(122)), justify="center")
        for k, (lp, rp) in enumerate((("5", "4"), ("6", "3"), ("7", "2"), ("8", "1"))):
            s.stub(RN.pin(lp), (-1, 0), g(6), net=f"IN{4 * n + k + 1}")
        tie_bar(s, [RN.pin(n_) for n_ in ("4", "3", "2", "1")], (1, 0), GND, "0V_IO", 4)
    note(s, "RN703 / RN704: 100 k pull-downs on the ULN2803A inputs", g(92), g(124))
    # ON LED resistors (22 k to +24V_IO), one array per four channels; the LEDs sit under the relays
    for n, (ref, ry) in enumerate((("RN701", g(132)), ("RN702", g(152)))):
        RN = s.place("lcec:R_Pack04_H", ref, g(40), ry, value="4x22k", lcsc="C25729", text="above",
                     ref_at=(g(40), ry - g(7)), val_at=(g(40), ry + g(7)), justify="center")
        tie_bar(s, [RN.pin(n_) for n_ in ("5", "6", "7", "8")], (-1, 0), "power:+24V", "+24V_IO", 4)
        for k, (rp) in enumerate(("4", "3", "2", "1")):
            s.stub(RN.pin(rp), (1, 0), g(6), net=f"LR{4 * n + k + 1}")

    # ---- relays: two columns of four
    for k in range(8):
        col, i = divmod(k, 4)
        x0, y = g(168) + col * g(78), g(40) + i * g(34)
        n = k + 1
        K = s.place("lcsc:C1524860", f"XK70{n}", x0, y, value="P2R-05P", lcsc="C1524860",
                    ref_at=(x0 - g(2), y - g(11)), val_at=(x0 + g(2), y - g(11)), justify="right", val_justify="left")
        tie(s, K.pin("1"), (-1, 0), "power:+24V", "+24V_IO", 4)
        s.stub(K.pin("5"), (-1, 0), g(6), net=f"DRV{n}")
        # ON LED under the coil: +24V_IO > 22 k (RN70x) > LED > coil driver
        Ld = s.place("lcec:LED_AK_H", f"LED70{n}", x0 - g(14), y + g(18), value="ON", lcsc="C89809",
                     ref_at=(x0 - g(14), y + g(22)), val_at=(x0 - g(14), y + g(14)), justify="center")
        s.stub(Ld.pin("2"), (-1, 0), g(6), net=f"LR{n}")
        s.stub(Ld.pin("1"), (1, 0), g(6), net=f"DRV{n}")
        # contacts: COM through a fuse, NO and NC to a 3-pole terminal
        F = s.place("lcsc:C206887", f"F70{n}", x0 + g(30), y - g(6), value="T5A 5x20", lcsc="C206887",
                    ref_at=(x0 + g(30), y - g(10)), val_at=(x0 + g(30), y - g(2)), justify="center")
        s.wire(K.pin("2"), F.pin("1"))
        xs = x0 + g(12)
        R = vpart(s, "Device:R", f"R70{n}", xs, y - g(6), "100R", None, footprint="Resistor_SMD:R_2512_6332Metric", dnp=True,
                  props={"LCSC": "DNP (footprint only)", "MPN": "RC snubber, value set at layout"}, show_value=False)
        C = vpart(s, "Device:C", f"C71{n}", xs, y, "47nF X2", None, footprint="Capacitor_THT:C_Rect_L18.0mm_W8.0mm_P15.00mm_FKS3_FKP3", dnp=True,
                  props={"LCSC": "DNP (footprint only)", "MPN": "RC snubber, value set at layout"}, show_value=False)
        s.wire(R.pin("2"), C.pin("1"))
        J = s.place("lcsc:C441205", f"J70{n}", x0 + g(48), y + g(6), value="DO%d" % n, lcsc="C441205",
                    ref_at=(x0 + g(52), y + g(2)), val_at=(x0 + g(52), y + g(10)), justify="left")
        xa, xc = x0 + g(38), x0 + g(40)
        s.wire(F.pin("2"), (xa, y - g(6)), (xa, J.pin("1")[1]), J.pin("1"))
        s.wire(K.pin("3"), J.pin("2"))
        s.wire(K.pin("4"), (xc, y + g(12)), (xc, J.pin("3")[1]), J.pin("3"))
    for col in range(2):
        s.dashed_line(g(168) + col * g(78), g(26), g(168) + col * g(78), g(160))
    s.text("COIL side (24 V)", g(166), g(26), justify="right bottom")
    s.text("CONTACT side (mains)", g(170), g(26), justify="left bottom")

    # ---- accessories (not on the PCB): relays and fuses bought in India, fuse covers, cable plugs
    note(s, "Accessories, not on the PCB (in the BOM)", g(10), g(168), 1.27, True)
    for i in range(8):
        n = i + 1
        y = g(172) + i * g(3)
        accessory(s, f"K70{n}", None, "G2R-1-S DC24 relay (local)", g(16), y, dnp=True,
                  props={"LCSC": "LOCAL (India)", "MPN": "G2R-1-S DC24", "Manufacturer": "Omron", "Datasheet": "https://www.omron.com/ecb/products/pdf/en-g2r.pdf"})
        accessory(s, f"FU70{n}", None, "T5A 5x20 ceramic fuse (local)", g(58), y, dnp=True,
                  props={"LCSC": "LOCAL (India)", "MPN": "T5A 250 V 5x20 ceramic", "Manufacturer": "local", "Datasheet": "n/a"})
        accessory(s, f"FC70{n}", "C187509", "clear cover for F70%d" % n, g(104), y)
        accessory(s, f"P70{n}", "C440881", "3-pole plug for J70%d" % n, g(144), y)
    return s


# =============================================================== sheet 8: analog outputs
def build_analog(libs, root_uuid, sheet_uuid):
    s = G.Sch(libs, "08_analog.kicad_sch", "LCEC-IO - 8 Analog", "8", root_uuid, sheet_uuid,
              comment="2 x 0-10 V outputs: isolated SPI, MCP4822 DAC, LM2904 gain stage, power-up clamp")
    A5, AGND = "+5V_A", "AGND"
    GNDA = "power:GNDA"
    note(s, "8  ANALOG OUTPUTS  -  2 x 0 to 10 V, 12 bit, isolated, 0 V at power-up and on loss", g(10), g(8), 2.54, True)
    note(s, "SPI and the clamp signal pass a CA-IS3740HW (default high: DAC deselected, outputs clamped) to an MCP4822 on +5V_A (78L05 from +15V_A). "
            "A clamp MOSFET holds both op-amp inputs at AGND until firmware releases AO_CLAMP.", g(10), g(13))

    # ---- U801 isolator
    ux, uy = g(55), g(60)
    U = s.place("lcsc:C528653", "U801", ux, uy, value="CA-IS3740HW", lcsc="C528653",
                ref_at=(ux - g(2), uy - g(17)), val_at=(ux + g(2), uy - g(17)), justify="right", val_justify="left")
    for k, name in enumerate(("DAC_SCK", "DAC_MOSI", "DAC_CS", "AO_CLAMP")):
        e = s.stub(U.pin(str(3 + k)), (-1, 0), g(8))
        s.hlabel(name, "input", e[0], e[1], 180)
    for k, net in enumerate(("SCK_A", "SDI_A", "CS_A", "CLAMP_A")):
        s.stub(U.pin(str(14 - k)), (1, 0), g(6), net=net)
    tie(s, U.pin("1"), (-1, 0), P33, "+3V3", 4)
    s.no_connect(*U.pin("7"))
    tie_bar(s, [U.pin("2"), U.pin("8")], (-1, 0), GND, "GND_L", 4)
    tie_bar(s, [U.pin("16"), U.pin("10")], (1, 0), P5, A5, 4)                                   # VDDB and ENB (enabled)
    tie_bar(s, [U.pin("15"), U.pin("9")], (1, 0), GNDA, AGND, 4)
    decap(s, ux - g(26), uy - g(30), P33, "+3V3", GND, "GND_L", "C801")
    decap(s, ux + g(26), uy - g(30), P5, A5, GNDA, AGND, "C802")
    s.dashed_line(ux, g(28), ux, g(82))
    s.text("LOGIC (GND_L)", ux - g(2), g(30), justify="right bottom")
    s.text("ANALOG (AGND)", ux + g(2), g(30), justify="left bottom")

    # ---- U802 DAC
    dx, dy = g(125), g(60)
    D = s.place("lcsc:C16040", "U802", dx, dy, value="MCP4822-E/SN", lcsc="C16040",
                ref_at=(dx, dy - g(18)), val_at=(dx, dy + g(10)), justify="center")
    tie(s, D.pin("1"), (-1, 0), P5, A5, 4)
    for pin, net in (("4", "SDI_A"), ("3", "SCK_A"), ("2", "CS_A")):
        s.stub(D.pin(pin), (-1, 0), g(6), net=net)
    tie(s, D.pin("5"), (-1, 0), GNDA, AGND, 4)                                                    # LDAC low: outputs update on CS rising edge
    s.stub(D.pin("8"), (1, 0), g(6), net="DAC_A")
    s.stub(D.pin("6"), (1, 0), g(6), net="DAC_B")
    tie(s, D.pin("7"), (1, 0), GNDA, AGND, 4)
    decap(s, dx + g(30), dy - g(14), P5, A5, GNDA, AGND, "C803")

    # ---- two gain stages: LM2904 units 1 and 2
    for ch, (unit, xa, ya, dac, tag, rin, rg, rf, rs, dref, cref) in enumerate((
            (1, g(205), g(50), "DAC_A", "AO1", "R801", "R803", "R805", "R807", "D801", "C805"),
            (2, g(205), g(105), "DAC_B", "AO2", "R802", "R804", "R806", "R808", "D802", "C806"))):
        A = s.place("lcsc:C7934", "U803", xa, ya, value="LM2904", lcsc="C7934", unit=unit,
                    ref_at=(xa, ya - g(9)), val_at=(xa, ya - g(7)), justify="center")
        ip, im, out = A.pin("3" if unit == 1 else "5"), A.pin("2" if unit == 1 else "6"), A.pin("1" if unit == 1 else "7")
        # input: DAC > 1 k > IN+ ; node carries the clamp and the 100 k to AGND
        m = s.stub(ip, (-1, 0), g(6))
        Ri = hpart(s, "Device:R", "x", m[0] - g(16), m[1], "1k", "C21190") if False else None
        Ri = s.place("lcec:R_H", f"R8{ch * 2 + 1 if False else 0}", 0, 0, value="1k", lcsc="C21190") if False else None
        Rin = hpart(s, "lcec:R_H", f"R81{ch + 1}", m[0] - g(16), m[1], "1k", "C21190")
        s.wire(Rin.pin("2"), m)
        s.stub(Rin.pin("1"), (-1, 0), g(3), net=dac)
        s.label(f"{tag}_P", m[0] - g(2), m[1], 180)
        # IN- node: 10 k to AGND and 14.7 k feedback from the output node
        n = s.stub(im, (-1, 0), g(4))
        gnode = (n[0], n[1] + g(6))
        s.wire(n, gnode)
        Rg = vpart(s, "Device:R", f"R81{ch + 3}", gnode[0], gnode[1], "10.0k 0.1%", "C95204",
                   ref_at=(gnode[0] - g(2), gnode[1] + g(2)), val_at=(gnode[0] - g(2), gnode[1] + g(4)), justify="right")
        s.power(GNDA, AGND, *Rg.pin("2"))
        # output: OUT > 100 R (inside the loop) > output node
        o1 = s.stub(out, (1, 0), g(4))
        Ro = hpart(s, "lcec:R_H", f"R81{ch + 5}", o1[0], o1[1], "100R", "C22775")
        s.wire(o1, Ro.pin("1"))
        x2 = Ro.pin("2")[0] + g(4)
        s.wire(Ro.pin("2"), (x2, ya))
        Rf = hpart(s, "lcec:R_H", f"R81{ch + 7}", gnode[0] + g(10), gnode[1], "14.7k 0.1%", "C705725")
        s.wire(gnode, Rf.pin("1"))
        s.wire(Rf.pin("2"), (x2, gnode[1]), (x2, ya))
        # TVS and 10 nF to AGND, then the terminal
        s.wire((x2, ya), (x2 + g(36), ya))
        T = vpart(s, "lcec:D_TVS_KA_V", dref, x2 + g(8), ya, "SMAJ15A", "C148216")
        s.power(GNDA, AGND, *T.pin("2"))
        C = vpart(s, "Device:C", cref, x2 + g(22), ya, "10nF", "C1589")
        s.power(GNDA, AGND, *C.pin("2"))
        J = s.place("lcsc:C441204", f"J80{ch + 1}", x2 + g(40), ya + g(1), value=f"AO{ch + 1}", lcsc="C441204",
                    ref_at=(x2 + g(44), ya - g(3)), val_at=(x2 + g(44), ya + g(5)), justify="left")
        s.wire((x2 + g(36), ya), J.pin("1"))
        tie(s, J.pin("2"), (-1, 0), GNDA, AGND, 4)
        accessory(s, f"P80{ch + 1}", "C440880", f"2-pole plug for J80{ch + 1}", g(150), g(150) + ch * g(4))
    A = s.place("lcsc:C7934", "U803", g(205), g(150), value="LM2904", lcsc="C7934", unit=3,
                ref_at=(g(205), g(143)), val_at=(g(205), g(157)), justify="center")
    tie(s, A.pin("8"), (-1, 0), P15, "+15V_A", 4)
    tie(s, A.pin("4"), (-1, 0), GNDA, AGND, 4)
    decap(s, g(185), g(140), P15, "+15V_A", GNDA, AGND, "C804")

    # ---- clamp: both op-amp + inputs to AGND while AO_CLAMP is high; 100 k keeps them at 0 V if the DAC is unpowered
    qx, qy = g(130), g(112)
    Q = s.place("lcsc:C83571", "Q801", qx, qy, value="2N7002DW", lcsc="C83571",
                ref_at=(qx, qy - g(10)), val_at=(qx, qy + g(10)), justify="center")
    g1, g2 = Q.pin("5"), Q.pin("2")
    s.wire(g1, (g1[0] - g(4), g1[1])); s.wire(g2, (g2[0] - g(4), g2[1]))
    s.wire((g1[0] - g(4), g1[1]), (g2[0] - g(4), g2[1]))
    s.stub((g2[0] - g(4), g2[1]), (-1, 0), g(4), net="CLAMP_A")
    s.stub(Q.pin("3"), (1, 0), g(6), net="AO1_P")
    s.stub(Q.pin("6"), (1, 0), g(6), net="AO2_P")
    tie_bar(s, [Q.pin("4"), Q.pin("1")], (1, 0), GNDA, AGND, 4)
    for k, (tag, y) in enumerate((("AO1_P", g(130)), ("AO2_P", g(146)))):
        Rp = vpart(s, "Device:R", f"R82{k + 1}", g(175), y, "100k", "C25803")
        s.wire((g(175) - g(10), y), (g(175), y))
        s.label(tag, g(175) - g(10), y, 180)
        s.power(GNDA, AGND, *Rp.pin("2"))

    # ---- 5 V supply for the DAC
    lx, ly = g(60), g(135)
    L = s.place("lcsc:C42738", "U804", lx, ly, value="L78L05", lcsc="C42738", ref_at=(lx, ly - g(8)), val_at=(lx, ly + g(8)), justify="center")
    tie(s, L.pin("3"), (-1, 0), P15, "+15V_A", 6)
    tie(s, L.pin("2"), (-1, 0), GNDA, AGND, 4)
    e = s.stub(L.pin("1"), (1, 0), g(6)); s.power(P5, A5, *e)
    decap(s, lx - g(26), ly - g(2), P15, "+15V_A", GNDA, AGND, "C807", "1uF", "C559769")
    decap(s, lx + g(22), ly - g(2), P5, A5, GNDA, AGND, "C808", "1uF", "C559769")
    note(s, "Design notes", g(10), g(172), 1.27, True)
    for i, txt in enumerate((
            "Gain 1 + 14.7 k / 10.0 k = 2.47 (0.1 % resistors): DAC full scale 4.095 V gives 10.11 V; firmware calibrates the 0 V and 10 V points of each channel.",
            "Output 100 R inside the feedback loop, SMAJ15A and 10 nF to AGND. At 10 V into 2 k the op-amp swings to 10.6 V, below its 13.5 V limit on 15 V.",
            "Accuracy after calibration: reference drift 125 ppm/C x 55 C = 0.7 %, offset 3 mV = 0.03 %, resistors 0.2 %: about +/-0.9 % FS worst case over 0 to 80 C.",
            "CA-IS3740HW outputs default high: CS_A high deselects the DAC and CLAMP_A high turns the clamp MOSFET on, so both outputs sit at 0 V at power-up and when logic power is lost.")):
        note(s, txt, g(10), g(176) + g(3 * i))
    return s


# =============================================================== sheet 5: digital inputs
IN_PAGES = ["5.1", "5.2", "5.3", "5.4", "5.5"]
IN_NAMES = ["DI1-4", "DI5-8", "SEL1-4", "SEL5-8", "SEL9-12"]


def build_input4(libs, root_uuid, parent_uuid, child_uuids):
    """One 4-channel input sheet (one TLP290-4), placed five times by the Inputs sheet. References are per instance:
    channel c of instance k is number 4k + c (R5nn, C5nn, LED5nn, J5nn; U50k, RN50k)."""
    paths = ["/" + root_uuid + "/" + parent_uuid + "/" + cu for cu in child_uuids]
    s = G.Sch(libs, "05b_input4.kicad_sch", "LCEC-IO - 5 Inputs (4 channels)", "5", root_uuid, child_uuids[0], paths=paths,
              comment="4 x 24 V input: TLP290-4 AC-input optocoupler, 4.7 k + 10 nF filter, state LED; placed 5 times")
    note(s, "5  INPUTS  -  4 channels (one TLP290-4); DI1-4, DI5-8, SEL1-4, SEL5-8 and SEL9-12 use this sheet", g(10), g(8), 2.54, True)
    note(s, "AC-input optocoupler: one COM jumper per group (parent sheet) selects PNP (COM = 0V_IO) or NPN (COM = +24V_IO) sensors. "
            "Per channel 4.7 k in series and 10 nF across the optocoupler input (47 us filter).", g(10), g(13))
    ux, uy = g(110), g(75)
    U = s.place("lcsc:C39031", lambda k: f"U50{k + 1}", ux, uy, value="TLP290-4", lcsc="C39031",
                ref_at=(ux - g(2), uy - g(19)), val_at=(ux + g(2), uy - g(19)), justify="right", val_justify="left")
    s.dashed_line(ux, g(48), ux, g(104))
    s.text("FIELD (0V_IO)", ux - g(2), g(50), justify="right bottom")
    s.text("LOGIC (GND_L)", ux + g(2), g(50), justify="left bottom")
    xj = g(36)
    e_bar = []
    for c in range(4):
        nref = lambda k, c=c: 4 * k + c + 1                       # channel number 1..20
        a, b = U.pin(str(2 * c + 1)), U.pin(str(2 * c + 2))       # IN{c}A, IN{c}B
        cp, ep = U.pin(str(16 - 2 * c)), U.pin(str(15 - 2 * c))    # C{c}, E{c}
        # field terminal (rows 14 mm apart, fanned in to the optocoupler pins by a staircase): pin 1 +24V (group PTC), pin 2 IN, pin 3 0V_IO
        rc = U.pin("1")[1] + g(14) * c
        J = s.place("lcec:Conn_R_01x03", lambda k, c=c: f"J5{4 * k + c + 1:02d}", xj, rc - g(2), value="IN", lcsc="C441205",
                    ref_at=(xj - g(3), rc - g(3)), val_at=(xj - g(3), rc + g(3)), justify="right")
        s.stub(J.pin("1"), (1, 0), g(4), net="SENSE24")
        tie(s, J.pin("3"), (1, 0), GND, "0V_IO", 4)
        Rr = hpart(s, "lcec:R_H", lambda k, c=c: f"R5{4 * k + c + 1:02d}", J.pin("2")[0] + g(16), rc, "4.7k", "C17936",
                   ref_at=(J.pin("2")[0] + g(19), rc - g(4)), val_at=(J.pin("2")[0] + g(19), rc + g(4)), justify="center")
        s.wire(J.pin("2"), Rr.pin("1"))
        xc = ux - g(24)
        xv = xc - g(16) + g(4) * c
        if c == 0:
            s.wire(Rr.pin("2"), (xc, a[1]), a)
        else:
            s.wire(Rr.pin("2"), (xv, rc), (xv, a[1]), (xc, a[1]), a)
        Cc = vpart(s, "Device:C", lambda k, c=c: f"C5{4 * k + c + 1:02d}", xc, a[1], "10nF", "C1589")
        s.wire(b, (xc, b[1]))
        s.label("COM", xc + g(8), b[1], 0)
        # logic side: collector > LED > 1 k (array) > +3V3, output on label OUTc; emitter to GND_L
        lx = cp[0] + g(14)
        Ld = s.place("lcsc:C89809" if False else "Device:LED", lambda k, c=c: f"LED5{4 * k + c + 1:02d}", lx, cp[1], value="IN", lcsc="C89809",
                     ref_at=(lx, cp[1] - g(4)), val_at=(lx, cp[1] + g(4)), justify="center", show_value=False)
        s.wire(cp, Ld.pin("1"))
        s.label(f"OUT{c + 1}", cp[0] + g(3), cp[1], 0)
        s.stub(Ld.pin("2"), (1, 0), g(4), net=f"LA{c + 1}")
        xe = cp[0] + g(40)
        s.wire(ep, (xe, ep[1]))
        e_bar.append((xe, ep[1]))
        # exported signal: label wire to the hierarchical label at the right edge
        yh = cp[1] + g(3)
        s.wire((cp[0] + g(52), yh), (cp[0] + g(66), yh))
        s.label(f"OUT{c + 1}", cp[0] + g(52), yh, 180)
        s.hlabel(f"OUT{c + 1}", "output", cp[0] + g(66), yh, 0)
    s.wire(e_bar[0], e_bar[-1])
    s.power(GND, "GND_L", *e_bar[-1])
    # LED resistors: 1 k x4 array, one per sheet instance
    RN = s.place("lcec:R_Pack04_H", lambda k: f"RN50{k + 1}", g(170), g(140), value="4x1k", lcsc="C20197", text="above",
                 ref_at=(g(170), g(133)), val_at=(g(170), g(147)), justify="center")
    for k2, (lp, rp) in enumerate((("5", "4"), ("6", "3"), ("7", "2"), ("8", "1"))):
        s.stub(RN.pin(lp), (-1, 0), g(6), net=f"LA{k2 + 1}")
    tie_bar(s, [RN.pin(n_) for n_ in ("4", "3", "2", "1")], (1, 0), P33, "+3V3", 4)
    decap(s, g(200), g(135), P33, "+3V3", GND, "GND_L", lambda k: f"C5{21 + 2 * k}" if False else f"C5{21 + k}")
    # parent connections: sheet pins as hierarchical labels with local nets
    for name, shape, y in (("SENSE24", "input", g(30)), ("COM", "input", g(38))):
        s.wire((g(14), y), (g(24), y))
        s.label(name, g(24), y, 0)
        s.hlabel(name, shape, g(14), y, 180)
    return s


def build_inputs(libs, root_uuid, sheet_uuid, child_uuids):
    s = G.Sch(libs, "05_inputs.kicad_sch", "LCEC-IO - 5 Inputs", "5", root_uuid, sheet_uuid,
              comment="8 digital inputs and 12 selector inputs: sensor supply PTCs, COM jumpers, five 4-channel sheets")
    note(s, "5  INPUTS  -  8 digital inputs (DI) and 12 MPG selector inputs (SEL), 24 VDC, PNP or NPN", g(10), g(8), 2.54, True)
    note(s, "Five copies of the 4-channel sheet. Per group: sensor +24 V through a 0.5 A PTC and one COM jumper (1-2: COM to +24V_IO for NPN sensors, "
            "2-3: COM to 0V_IO for PNP sensors, the default). Dry-contact switches wire between +24 V and the input.", g(10), g(13))
    # ---- group supplies
    for g_i, (grp, y, rt, jp, sh, sense, com) in enumerate((("DI", g(40), "RT501", "JP501", "JS501", "SENSE_DI", "COM_DI"),
                                                            ("SEL", g(100), "RT502", "JP502", "JS502", "SENSE_SEL", "COM_SEL"))):
        e = s.stub((g(20), y), (1, 0), g(0))
        PT = s.place("lcsc:C151168", rt, g(34), y, value="0.5A PTC", lcsc="C151168", ref_at=(g(34), y - g(5)), val_at=(g(34), y - g(3)), justify="center")
        tie(s, PT.pin("1"), (-1, 0), "power:+24V", "+24V_IO", 4)
        s.stub(PT.pin("2"), (1, 0), g(6), net=sense)
        J = s.place("lcsc:C2937625", jp, g(34), y + g(14), value="COM", lcsc="C2937625", ref_at=(g(40), y + g(11)), val_at=(g(40), y + g(18)), justify="left")
        tie(s, J.pin("1"), (-1, 0), "power:+24V", "+24V_IO", 6)
        s.stub(J.pin("2"), (-1, 0), g(6), net=com)
        tie(s, J.pin("3"), (-1, 0), GND, "0V_IO", 6)
        accessory(s, sh, "C5305", "jumper shunt on JP50%d (2-3 = PNP)" % (g_i + 1), g(70), y + g(14))
        note(s, f"{grp} group sensor supply", g(14), y - g(8), 1.27, True)
    # ---- five instances of the 4-channel sheet
    spec = ((child_uuids[0], 0, g(40)), (child_uuids[1], 1, g(66)), (child_uuids[2], 2, g(100)), (child_uuids[3], 3, g(126)), (child_uuids[4], 4, g(152)))
    di_pts, sel_pts = [], []
    for cu, k, y in spec:
        sense, com = ("SENSE_DI", "COM_DI") if k < 2 else ("SENSE_SEL", "COM_SEL")
        pins = [("SENSE24", "input", "left", g(4)), ("COM", "input", "left", g(8))] + \
               [(f"OUT{c + 1}", "output", "right", g(4) + c * g(3)) for c in range(4)]
        pos = s.sheet(IN_NAMES[k], "05b_input4.kicad_sch", g(130), y, g(36), g(20), pins, IN_PAGES[k], cu)
        s.stub(pos["SENSE24"], (-1, 0), g(8), net=sense)
        s.stub(pos["COM"], (-1, 0), g(8), net=com)
        for c in range(4):
            base = 4 * k + c + 1 if k < 2 else 4 * (k - 2) + c + 1
            net = f"DI{4 * k + c + 1}" if k < 2 else f"SEL{4 * (k - 2) + c + 1}"
            (di_pts if k < 2 else sel_pts).append((pos[f"OUT{c + 1}"], net))
    for pts, name, hx in ((di_pts, "DI[1..8]", g(230)), (sel_pts, "SEL[1..12]", g(230))):
        ys = []
        xb = None
        for pt, net in pts:
            x_e = pt[0] + g(12)
            s.wire(pt, (x_e, pt[1]))
            s.label(net, pt[0] + g(2), pt[1], 0)
            s.bus_entry(x_e, pt[1], g(2), -g(2))
            xb = x_e + g(2)
            ys.append(pt[1] - g(2))
        s.bus((xb, max(ys)), (xb, min(ys)), (hx, min(ys)))
        s.hlabel(name, "output", hx, min(ys), 0)
    # ---- terminal plugs (accessories)
    note(s, "Accessories, not on the PCB: 3-pole plugs for J501 to J520", g(10), g(176), 1.27, True)
    for i in range(20):
        accessory(s, f"P5{i + 1:02d}", "C440881", "3-pole plug for J5%02d" % (i + 1), g(14) + (i // 5) * g(46), g(180) + (i % 5) * g(3))
    return s
