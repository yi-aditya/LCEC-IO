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
        + [("7", "REG_EN", -25.4), ("51", "VDD33TXRX1", -38.1), ("64", "VDD33TXRX2", -50.8), ("58", "VDD33BIAS", -63.5)]
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
    u2.graphicItems = [SyRect(start=Position(-10.16, 69.85), end=Position(10.16, -69.85))]
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


def main():
    lib = SymbolLib.from_file(LIB)
    relayout_osc(lib)
    relayout_stm32(lib)
    relayout_urb(lib)
    relayout_lan9252(lib)
    relayout_rj45(lib)
    relayout_eeprom(lib)
    libio.save(lib, LIB)


if __name__ == "__main__":
    main()
