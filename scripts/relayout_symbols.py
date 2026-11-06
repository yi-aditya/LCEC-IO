#!/usr/bin/env python3
"""Re-lay imported symbols functionally for readable schematics. No pin is ever on the top or bottom edge:
KiCad prints top and bottom pin names and numbers sideways, and the schematics allow no vertical text.

STM32F405VGT6 (C56621), two units:
  unit 1 'signals'  all GPIO, NRST and BOOT0 on the left and right in functional groups (scripts/pinmap.py);
                    pins that need a pull resistor or capacitor beside them have blank rows around them
  unit 2 'power'    left: VBAT, six VDD (12.7 mm apart so a 100 nF capacitor fits beside each), VDDA, VREF+;
                    right: four VSS, VSSA, VCAP_1, VCAP_2

URB2403S/2405S/2415S-6WR3 (C5369843, C3031185, C5369844): input pins left, isolated output right
(NC pins on the right too), so the isolation barrier can be drawn through the middle of the symbol.

Pin numbers and names are unchanged apart from a short alternate function after the port name, so
scripts/pincheck.py still verifies every pin against the datasheet. Run after fix_symbols.py. Safe to re-run.
"""
import copy
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import libio  # noqa: E402
from kiutils.items.common import Effects, Font, Position  # noqa: E402
from kiutils.items.syitems import SyRect  # noqa: E402
from kiutils.symbol import SymbolLib  # noqa: E402

import pinmap  # noqa: E402
from pin_tables import T  # noqa: E402

LIB = os.path.join(ROOT, "lib", "lcsc.kicad_sym")
CODE = "C56621"
PITCH = 2.54
PIN_LEN = 5.08
SIG_HALF_W = 20.32           # signal unit body half width
PWR_HALF_W = 10.16

def pin_obj(template, num, name, x, y, angle, ptype):
    p = copy.deepcopy(template)
    p.number, p.name = str(num), name
    p.position = Position(round(x, 4), round(y, 4), angle)
    p.length = PIN_LEN
    p.electricalType = ptype
    p.graphicalStyle = "line"
    p.nameEffects = Effects(font=Font(height=1.27, width=1.27))
    p.numberEffects = Effects(font=Font(height=1.0, width=1.0))
    return p


def relayout_stm32(lib):
    sym = None
    for s in lib.symbols:
        pr = {p.key: p.value for p in s.properties}
        if (pr.get("LCSC") or pr.get("LCSC Part")) == CODE:
            sym = s
    if sym is None:
        sys.exit("STM32 symbol not in library")
    old = {}
    for u in sym.units:
        for p in u.pins:
            old[p.number] = p
    template = next(iter(old.values()))
    by_name = {}
    for num, names in T[CODE]["pins"].items():
        by_name.setdefault(names[0], []).append(str(num))
    used = set()

    def take(n):
        for num in by_name[n]:
            if num not in used:
                used.add(num)
                return num
        raise KeyError(n)

    # ------------------------------------------------------------------ unit 1: signals
    layout = {"left": [], "right": []}
    for side, title, items in pinmap.LEFT_RIGHT:
        if layout[side]:
            layout[side].append(None)                      # one blank row between groups
        for it in items:
            if it[0] in pinmap.GAP_BEFORE:
                layout[side] += [None] * pinmap.GAP_ROWS
            layout[side].append(it)
            if it[0] in pinmap.GAP_AFTER:
                layout[side] += [None] * pinmap.GAP_ROWS
    nrows = max(len(v) for v in layout.values())
    top_y = (nrows + 1) * PITCH / 2
    pins1 = []
    for side, items in layout.items():
        for i, it in enumerate(items):
            if it is None:
                continue
            net, pname = it
            y = top_y - PITCH * (i + 1)
            num = take(pname)
            fn = pinmap.FUNCTIONS.get(pname)
            name = f"{pname}/{fn}" if fn else pname
            ptype = "input" if pname == "BOOT0" else "bidirectional"
            if side == "left":
                pins1.append(pin_obj(template, num, name, -SIG_HALF_W - PIN_LEN, y, 0, ptype))
            else:
                pins1.append(pin_obj(template, num, name, SIG_HALF_W + PIN_LEN, y, 180, ptype))
    # ------------------------------------------------------------------ unit 2: power
    pins2 = []
    left_rows = [("VBAT", 38.1)] + [("VDD", 25.4 - 12.7 * k) for k in range(6)] + [("VDDA", -58.42), ("VREF+", -71.12)]
    right_rows = [("VSS", 38.1 - 2.54 * k) for k in range(4)] + [("VSSA", 27.94), ("VCAP_1", 12.7), ("VCAP_2", 0.0)]
    for n, y in left_rows:
        pins2.append(pin_obj(template, take(n), n, -PWR_HALF_W - PIN_LEN, y, 0, "power_in"))
    for n, y in right_rows:
        pins2.append(pin_obj(template, take(n), n, PWR_HALF_W + PIN_LEN, y, 180,
                             "passive" if n.startswith("VCAP") else "power_in"))
    assert len(pins1) + len(pins2) == 100 and len(used) == 100, (len(pins1), len(pins2), len(used))
    u1 = sym.units[0]
    u1.pins = pins1
    u1.graphicItems = [SyRect(start=Position(-SIG_HALF_W, top_y), end=Position(SIG_HALF_W, -top_y))]
    u1.unitId, u1.styleId = 1, 1
    u2 = copy.deepcopy(u1)
    u2.unitId, u2.styleId = 2, 1
    u2.pins = pins2
    u2.graphicItems = [SyRect(start=Position(-PWR_HALF_W, 43.18), end=Position(PWR_HALF_W, -76.2))]
    sym.units = [u1, u2]
    print(f"STM32: unit 1 signals {len(pins1)} pins ({2 * SIG_HALF_W:g} x {2 * top_y:g} mm), unit 2 power {len(pins2)} pins")


URB = {"C5369843", "C3031185", "C5369844"}


def relayout_urb(lib):
    n = 0
    for sym in lib.symbols:
        pr = {p.key: p.value for p in sym.properties}
        if (pr.get("LCSC") or pr.get("LCSC Part")) not in URB:
            continue
        unit = sym.units[0]
        old = {p.number: p for p in unit.pins}
        spec = [("2", -15.24, 5.08, 0, "VIN", "power_in"), ("3", -15.24, 0, 0, "CTRL", "input"),
                ("1", -15.24, -5.08, 0, "GND", "power_in"),
                ("6", 15.24, 5.08, 180, "+VO", "power_out"), ("7", 15.24, -5.08, 180, "-VO", "power_out"),
                ("5", 15.24, -10.16, 180, "NC", "no_connect"), ("8", 15.24, -12.7, 180, "NC", "no_connect")]
        pins = []
        for num, x, y, a, name, ptype in spec:
            p = copy.deepcopy(old[num])
            p.name, p.position = name, Position(x, y, a)
            p.length, p.electricalType, p.graphicalStyle = PIN_LEN, ptype, "line"
            p.nameEffects = Effects(font=Font(height=1.27, width=1.27))
            p.numberEffects = Effects(font=Font(height=1.0, width=1.0))
            pins.append(p)
        unit.pins = pins
        unit.graphicItems = [SyRect(start=Position(-10.16, 10.16), end=Position(10.16, -15.24))]
        sym.units = [unit]
        n += 1
    print(f"URB symbols re-laid out: {n}")


def relayout_osc(lib):
    """ECS-3225MVQ oscillator (C2595919): OE and GND on the left, VDD and OUTPUT on the right 12.7 mm apart."""
    for sym in lib.symbols:
        pr = {p.key: p.value for p in sym.properties}
        if (pr.get("LCSC") or pr.get("LCSC Part")) != "C2595919":
            continue
        unit = sym.units[0]
        old = {p.number: p for p in unit.pins}
        spec = [("1", -17.78, 6.35, 0, "OE", "input"), ("2", -17.78, -6.35, 0, "GND", "power_in"),
                ("4", 17.78, 6.35, 180, "VDD", "power_in"), ("3", 17.78, -6.35, 180, "OUTPUT", "output")]
        pins = []
        for num, x, y, a, name, ptype in spec:
            p = copy.deepcopy(old[num])
            p.name, p.position = name, Position(x, y, a)
            p.length, p.electricalType, p.graphicalStyle = PIN_LEN, ptype, "line"
            p.nameEffects = Effects(font=Font(height=1.27, width=1.27))
            p.numberEffects = Effects(font=Font(height=1.0, width=1.0))
            pins.append(p)
        unit.pins = pins
        unit.graphicItems = [SyRect(start=Position(-12.7, 10.16), end=Position(12.7, -10.16))]
        sym.units = [unit]
        print("oscillator symbol re-laid out")


# ---------------------------------------------------------------------------------------------- LAN9252
LAN = "C80933"
# unit 1, left side, top to bottom; None = blank row. (pin number, name, electrical type)
# Blank rows leave room for the parts that hang from a pin: a pull-up above RUNLED/E2PSIZE, pull-downs below the two
# LINKACTLED/CHIP_MODE straps, and the strap-to-ground bar.
LAN_LEFT = (
    [("1", "OSCI", "input"), ("11", "~{RST}", "input"), None,
     ("50", "~{SCS}", "input"), ("19", "SCK", "input"), ("17", "SI/SIO0", "input"), ("13", "SO/SIO1", "output"), None,
     ("44", "IRQ", "output"), ("34", "SYNC0", "output"), ("18", "SYNC1", "output"), None,
     ("42", "EESDA", "bidirectional"), ("43", "EESCL", "bidirectional")]
    + [None] * 5
    + [("45", "RUNLED/E2PSIZE", "output"), None, None, None,
       ("46", "LINKACTLED1/CHIP_MODE1", "output")] + [None] * 4
    + [("48", "LINKACTLED0/CHIP_MODE0", "output")] + [None] * 5
    + [("41", "TESTMODE", "input"), ("8", "FXLOSEN", "input"), ("9", "FXSDENA", "input"), ("10", "FXSDENB", "input"), None, None, None]
    + [("2", "OSCO", "bidirectional"), ("12", "SIO2", "bidirectional"), ("15", "DIGIO8", "bidirectional"),
       ("16", "DIGIO7", "bidirectional"), ("21", "DIGIO6", "bidirectional"), ("22", "DIGIO5", "bidirectional"),
       ("23", "DIGIO4", "bidirectional"), ("25", "MII_CLK25", "bidirectional"), ("26", "DIGIO11", "bidirectional"),
       ("27", "DIGIO12", "bidirectional"), ("28", "DIGIO13", "bidirectional"), ("29", "DIGIO10", "bidirectional"),
       ("30", "DIGIO14", "bidirectional"), ("31", "DIGIO15", "bidirectional"), ("33", "DIGIO9", "bidirectional"),
       ("35", "SIO3", "bidirectional"), ("36", "DIGIO0", "bidirectional"), ("39", "DIGIO1", "bidirectional"),
       ("40", "DIGIO2", "bidirectional"), ("49", "DIGIO3", "bidirectional")]
)
# right side: the eight twisted-pair lines six rows (15.24 mm) apart so a 49.9 ohm termination can hang above each one
LAN_RIGHT = {6: ("53", "TXPA"), 12: ("52", "TXNA"), 18: ("55", "RXPA"), 24: ("54", "RXNA"),
             32: ("62", "TXPB"), 38: ("63", "TXNB"), 44: ("60", "RXPB"), 50: ("61", "RXNB"), 57: ("57", "RBIAS")}
LAN_HALF_W = 22.86


def relayout_lan9252(lib):
    sym = next((s for s in lib.symbols if {p.key: p.value for p in s.properties}.get("LCSC") == LAN), None)
    if sym is None:
        sys.exit("LAN9252 symbol not in library")
    old = {}
    for u in sym.units:
        for p in u.pins:
            old[p.number] = p
    template = next(iter(old.values()))
    nrows = max(len(LAN_LEFT), max(LAN_RIGHT) + 5)
    top_y = round((nrows + 1) * PITCH / 2 / PITCH) * PITCH            # keep pins on the 2.54 mm grid
    top_y = (nrows + 1) * PITCH / 2
    used = set()
    pins1 = []
    for i, it in enumerate(LAN_LEFT):
        if it is None:
            continue
        num, name, pt = it
        used.add(num)
        pins1.append(pin_obj(template, num, name, -LAN_HALF_W - PIN_LEN, top_y - PITCH * (i + 1), 0, pt))
    for i, (num, name) in LAN_RIGHT.items():
        used.add(num)
        pins1.append(pin_obj(template, num, name, LAN_HALF_W + PIN_LEN, top_y - PITCH * (i + 1), 180, "bidirectional"))
    # unit 2: power. 12.7 mm pitch where a 100 nF capacitor sits beside the pin
    left = [("5", "VDD33", 63.5)] + [(n, "VDDIO", 50.8 - 12.7 * k) for k, n in enumerate(("14", "20", "32", "37", "47"))] \
        + [("7", "REG_EN", -25.4), ("51", "VDD33TXRX1", -38.1), ("64", "VDD33TXRX2", -63.5), ("58", "VDD33BIAS", -88.9)]
    right = [("6", "VDDCR", 63.5), ("24", "VDDCR", 50.8), ("38", "VDDCR", 38.1), ("56", "VDD12TX1", 25.4),
             ("59", "VDD12TX2", 12.7), ("3", "OSCVDD12", 0.0), ("4", "OSCVSS", -12.7), ("65", "VSS", -15.24)]
    pins2 = []
    for num, name, y in left:
        used.add(num)
        pins2.append(pin_obj(template, num, name, -10.16 - PIN_LEN, y, 0, "input" if name == "REG_EN" else "power_in"))
    for num, name, y in right:
        used.add(num)
        pins2.append(pin_obj(template, num, name, 10.16 + PIN_LEN, y, 180,
                             "passive" if name.startswith(("VDDCR", "VDD12")) else "power_in"))
    assert len(used) == 65 and len(pins1) + len(pins2) == 65, (len(used), len(pins1), len(pins2))
    u1 = sym.units[0]
    u1.pins = pins1
    u1.graphicItems = [SyRect(start=Position(-LAN_HALF_W, top_y), end=Position(LAN_HALF_W, -top_y))]
    u1.unitId, u1.styleId = 1, 1
    u2 = copy.deepcopy(u1)
    u2.unitId, u2.styleId = 2, 1
    u2.pins = pins2
    u2.graphicItems = [SyRect(start=Position(-10.16, 69.85), end=Position(10.16, -95.25))]
    sym.units = [u1, u2]
    print(f"LAN9252: unit 1 signals {len(pins1)} pins ({2 * LAN_HALF_W:g} x {2 * top_y:g} mm), unit 2 power {len(pins2)} pins")


def relayout_rj45(lib):
    """HY911105AE: the four twisted-pair pins on the left 15.24 mm apart (in line with the LAN9252 lines), everything else right."""
    for sym in lib.symbols:
        if {p.key: p.value for p in sym.properties}.get("LCSC") != "C69427":
            continue
        unit = sym.units[0]
        old = {p.number: p for p in unit.pins}
        spec = [("1", -17.78, 22.86, 0, "TD+"), ("2", -17.78, 7.62, 0, "TD-"), ("3", -17.78, -7.62, 0, "RD+"), ("6", -17.78, -22.86, 0, "RD-"),
                ("4", 17.78, 20.32, 180, "TD_CT"), ("5", 17.78, 17.78, 180, "RD_CT"),
                ("9", 17.78, 12.7, 180, "LEDG_A"), ("10", 17.78, 10.16, 180, "LEDG_K"),
                ("12", 17.78, 5.08, 180, "LEDY_A"), ("11", 17.78, 2.54, 180, "LEDY_K"),
                ("8", 17.78, -2.54, 180, "CHSGND"), ("SH1", 17.78, -5.08, 180, "SH1"), ("SH2", 17.78, -7.62, 180, "SH2"),
                ("7", 17.78, -12.7, 180, "NC")]
        pins = []
        for num, x, y, a, name in spec:
            p = copy.deepcopy(old[num])
            p.name, p.position = name, Position(x, y, a)
            p.length, p.graphicalStyle = PIN_LEN, "line"
            p.nameEffects = Effects(font=Font(height=1.27, width=1.27))
            p.numberEffects = Effects(font=Font(height=1.0, width=1.0))
            pins.append(p)
        unit.pins = pins
        unit.graphicItems = [SyRect(start=Position(-12.7, 30.48), end=Position(12.7, -27.94))]
        sym.units = [unit]
        print("RJ45 symbol re-laid out")


def relayout_eeprom(lib):
    """24LC32A: supply and the five pins that are tied to ground or supply on the left, SCL and SDA on the right 15.24 mm
    apart so each can have its own pull-up hanging above it."""
    for sym in lib.symbols:
        if {p.key: p.value for p in sym.properties}.get("LCSC") != "C615715":
            continue
        unit = sym.units[0]
        old = {p.number: p for p in unit.pins}
        spec = [("8", -12.7, 7.62, 0, "VCC", "power_in"), ("1", -12.7, 2.54, 0, "A0", "input"), ("2", -12.7, 0, 0, "A1", "input"),
                ("3", -12.7, -2.54, 0, "A2", "input"), ("7", -12.7, -5.08, 0, "WP", "input"), ("4", -12.7, -7.62, 0, "VSS", "power_in"),
                ("6", 12.7, 7.62, 180, "SCL", "input"), ("5", 12.7, -7.62, 180, "SDA", "bidirectional")]
        pins = []
        for num, x, y, a, name, ptype in spec:
            p = copy.deepcopy(old[num])
            p.name, p.position = name, Position(x, y, a)
            p.length, p.electricalType, p.graphicalStyle = PIN_LEN, ptype, "line"
            p.nameEffects = Effects(font=Font(height=1.27, width=1.27))
            p.numberEffects = Effects(font=Font(height=1.0, width=1.0))
            pins.append(p)
        unit.pins = pins
        unit.graphicItems = [SyRect(start=Position(-7.62, 10.16), end=Position(7.62, -10.16))]
        sym.units = [unit]
        print("EEPROM symbol re-laid out")


def _sym_by_lcsc(lib, code):
    for sym in lib.symbols:
        if {p.key: p.value for p in sym.properties}.get("LCSC") == code:
            return sym
    sys.exit(f"{code} not in library")


def _relay_pins(sym):
    old = {}
    for u in sym.units:
        for p in u.pins:
            old[p.number] = p
    return old, next(iter(old.values()))


def _set_pins(sym, spec, rect, unit_id=1):
    """spec: [(number, name, x, y, angle, type)], rect: (x1, y1, x2, y2). Replaces all units with one unit."""
    old, template = _relay_pins(sym)
    pins = [pin_obj(old[num], num, name, x, y, ang, ptype) for num, name, x, y, ang, ptype in spec]
    unit = sym.units[0]
    unit.pins = pins
    unit.graphicItems = [SyRect(start=Position(rect[0], rect[1]), end=Position(rect[2], rect[3]))]
    unit.unitId, unit.styleId = unit_id, 1
    sym.units = [unit]


def relayout_small(lib):
    """P2R-05P socket: coil left, contacts right (the isolation barrier runs through the body); CA-IS3742LN with the field side
    (side B) on the left and the logic side (side A) on the right, so the MPG sheet flows left to right; the dual MOSFET and the
    78L05 without pins on the top or bottom edge."""
    s = _sym_by_lcsc(lib, "C1524860")
    _set_pins(s, [("1", "COIL1", -10.16, 2.54, 0, "passive"), ("5", "COIL2", -10.16, -2.54, 0, "passive"),
                  ("2", "COM", 10.16, 7.62, 180, "passive"), ("3", "NO", 10.16, -7.62, 180, "passive"), ("4", "NC", 10.16, -15.24, 180, "passive")],
              (-5.08, 10.16, 5.08, -17.78))
    # digital isolators: supply and enable pins grouped at the top, grounds at the bottom, signals aligned across the barrier
    for code in ("C428888", "C528653"):                               # CA-IS3740LN / HW: four forward channels, logic side left
        s = _sym_by_lcsc(lib, code)
        spec = [("1", "VDDA", -16.51, 15.24, 0, "power_in"), ("7", "NC", -16.51, 12.7, 0, "no_connect"),
                ("3", "VI1", -16.51, 7.62, 0, "input"), ("4", "VI2", -16.51, 5.08, 0, "input"),
                ("5", "VI3", -16.51, 2.54, 0, "input"), ("6", "VI4", -16.51, 0, 0, "input"),
                ("2", "GNDA", -16.51, -5.08, 0, "power_in"), ("8", "GNDA", -16.51, -7.62, 0, "power_in"),
                ("16", "VDDB", 16.51, 15.24, 180, "power_in"), ("10", "ENB", 16.51, 12.7, 180, "input"),
                ("14", "VO1", 16.51, 7.62, 180, "output"), ("13", "VO2", 16.51, 5.08, 180, "output"),
                ("12", "VO3", 16.51, 2.54, 180, "output"), ("11", "VO4", 16.51, 0, 180, "output"),
                ("15", "GNDB", 16.51, -5.08, 180, "power_in"), ("9", "GNDB", 16.51, -7.62, 180, "power_in")]
        _set_pins(s, spec, (-11.43, 17.78, 11.43, -10.16))
    s = _sym_by_lcsc(lib, "C5347249")                                  # CA-IS3742LN: field side (B) left, logic side (A) right
    _set_pins(s, [("16", "VDDB", -16.51, 15.24, 0, "power_in"), ("10", "ENB", -16.51, 12.7, 0, "input"),
                  ("12", "VI3", -16.51, 7.62, 0, "input"), ("11", "VI4", -16.51, 5.08, 0, "input"),
                  ("14", "VO1", -16.51, 2.54, 0, "output"), ("13", "VO2", -16.51, 0, 0, "output"),
                  ("15", "GNDB", -16.51, -5.08, 0, "power_in"), ("9", "GNDB", -16.51, -7.62, 0, "power_in"),
                  ("1", "VDDA", 16.51, 15.24, 180, "power_in"), ("7", "ENA", 16.51, 12.7, 180, "input"),
                  ("5", "VO3", 16.51, 7.62, 180, "output"), ("6", "VO4", 16.51, 5.08, 180, "output"),
                  ("3", "VI1", 16.51, 2.54, 180, "input"), ("4", "VI2", 16.51, 0, 180, "input"),
                  ("2", "GNDA", 16.51, -5.08, 180, "power_in"), ("8", "GNDA", 16.51, -7.62, 180, "power_in")],
              (-11.43, 17.78, 11.43, -10.16))
    s = _sym_by_lcsc(lib, "C6180")                                     # AM26LS32A: inputs left, outputs and controls right
    _set_pins(s, [("2", "1A", -12.7, 12.7, 0, "input"), ("1", "1B", -12.7, 10.16, 0, "input"),
                  ("6", "2A", -12.7, 7.62, 0, "input"), ("7", "2B", -12.7, 5.08, 0, "input"),
                  ("10", "3A", -12.7, 2.54, 0, "input"), ("9", "3B", -12.7, 0, 0, "input"),
                  ("14", "4A", -12.7, -2.54, 0, "input"), ("15", "4B", -12.7, -5.08, 0, "input"),
                  ("16", "VCC", 12.7, 17.78, 180, "power_in"), ("4", "G", 12.7, 15.24, 180, "input"),
                  ("3", "1Y", 12.7, 11.43, 180, "output"), ("5", "2Y", 12.7, 6.35, 180, "output"),
                  ("11", "3Y", 12.7, 1.27, 180, "output"), ("13", "4Y", 12.7, -3.81, 180, "output"),
                  ("12", "~{G}", 12.7, -7.62, 180, "input"), ("8", "GND", 12.7, -10.16, 180, "power_in")],
              (-7.62, 20.32, 7.62, -12.7))
    s = _sym_by_lcsc(lib, "C83571")
    _set_pins(s, [("5", "G1", -10.16, 2.54, 0, "input"), ("2", "G2", -10.16, 0, 0, "input"),
                  ("3", "D1", 10.16, 7.62, 180, "passive"), ("6", "D2", 10.16, 5.08, 180, "passive"),
                  ("4", "S1", 10.16, -2.54, 180, "passive"), ("1", "S2", 10.16, -5.08, 180, "passive")],
              (-5.08, 10.16, 5.08, -7.62))
    s = _sym_by_lcsc(lib, "C16040")                                    # MCP4822: supply and LDAC at the top/bottom of the left side
    _set_pins(s, [("1", "VDD", -13.97, 15.24, 0, "power_in"), ("4", "SDI", -13.97, 7.62, 0, "input"),
                  ("3", "SCK", -13.97, 5.08, 0, "input"), ("2", "~{CS}", -13.97, 2.54, 0, "input"),
                  ("5", "~{LDAC}", -13.97, -2.54, 0, "input"),
                  ("8", "VOUTA", 13.97, 7.62, 180, "output"), ("6", "VOUTB", 13.97, 2.54, 180, "output"),
                  ("7", "VSS", 13.97, -5.08, 180, "power_in")], (-8.89, 17.78, 8.89, -7.62))
    s = _sym_by_lcsc(lib, "C42738")
    _set_pins(s, [("3", "VIN", -10.16, 2.54, 0, "power_in"), ("2", "GND", -10.16, -2.54, 0, "power_in"),
                  ("1", "VOUT", 10.16, 2.54, 180, "power_out")], (-5.08, 5.08, 5.08, -5.08))
    print("socket, isolator (field side left), MOSFET and LDO symbols re-laid out")


def relayout_opamp(lib):
    """LM2904: two op-amp triangles (units 1 and 2) and a power unit (3); no pin on the top or bottom edge."""
    from kiutils.items.syitems import SyPolyLine
    from kiutils.items.common import Stroke, Fill
    s = _sym_by_lcsc(lib, "C7934")
    old, _ = _relay_pins(s)

    def tri():
        return SyPolyLine(points=[Position(-5.08, 7.62), Position(-5.08, -7.62), Position(7.62, 0), Position(-5.08, 7.62)],
                          stroke=Stroke(width=0.254), fill=Fill(type="none"))

    units = []
    for uid, (num_n, num_p, num_o, tag) in enumerate((("2", "3", "1", "1"), ("6", "5", "7", "2")), start=1):
        u = copy.deepcopy(s.units[0])
        u.unitId, u.styleId = uid, 1
        u.pins = [pin_obj(old[num_p], num_p, f"{tag}IN+", -10.16, 2.54, 0, "input"),
                  pin_obj(old[num_n], num_n, f"{tag}IN-", -10.16, -2.54, 0, "input"),
                  pin_obj(old[num_o], num_o, f"{tag}OUT", 12.7, 0, 180, "output")]
        u.graphicItems = [tri()]
        units.append(u)
    u = copy.deepcopy(s.units[0])
    u.unitId, u.styleId = 3, 1
    u.pins = [pin_obj(old["8"], "8", "VCC", -10.16, 2.54, 0, "power_in"), pin_obj(old["4"], "4", "GND", -10.16, -2.54, 0, "power_in")]
    u.graphicItems = [SyRect(start=Position(-5.08, 5.08), end=Position(5.08, -5.08))]
    units.append(u)
    s.units = units
    print("LM2904 re-laid out as two op-amps and a power unit")


def main():
    lib = SymbolLib.from_file(LIB)
    relayout_osc(lib)
    relayout_stm32(lib)
    relayout_urb(lib)
    relayout_lan9252(lib)
    relayout_rj45(lib)
    relayout_eeprom(lib)
    relayout_small(lib)
    relayout_opamp(lib)
    libio.save(lib, LIB)


if __name__ == "__main__":
    main()
