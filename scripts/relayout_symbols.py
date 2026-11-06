#!/usr/bin/env python3
"""Re-lay imported symbols functionally for readable schematics.

STM32F405VGT6 (C56621): EasyEDA lists pins in package order, so power pins are scattered between
GPIOs and a decoupling capacitor cannot sit beside the pin it serves. The layout is rebuilt from
scripts/pinmap.py: supplies grouped on top and bottom (12.7 mm apart so a capacitor fits beside
each), signals on the sides in functional groups, free pins last.

URB2403S/2405S/2415S-6WR3 (C5369843, C3031185, C5369844): EasyEDA puts all seven pins on one side.
Rebuilt with the input pins on the left and the isolated output on the right, so the isolation
barrier can be drawn through the middle of the symbol.

Pin numbers and names are unchanged apart from a short alternate function after the port
name, so scripts/pincheck.py still verifies every pin against the datasheet.
Run after fix_symbols.py. Safe to re-run.
"""
import copy
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kiutils.items.common import Effects, Font, Position  # noqa: E402
from kiutils.items.syitems import SyRect  # noqa: E402
import libio  # noqa: E402
from kiutils.symbol import SymbolLib  # noqa: E402

import pinmap  # noqa: E402
from pin_tables import T  # noqa: E402

LIB = os.path.join(ROOT, "lib", "lcsc.kicad_sym")
CODE = "C56621"
PITCH = 2.54
BODY_HALF_W = 55.88
PIN_LEN = 5.08


def relayout_stm32(lib):
    sym = None
    for s in lib.symbols:
        pr = {p.key: p.value for p in s.properties}
        if (pr.get("LCSC") or pr.get("LCSC Part")) == CODE:
            sym = s
    if sym is None:
        sys.exit("STM32 symbol not in library")
    pins_by_name = {}
    old = {}
    for u in sym.units:
        for p in u.pins:
            old[p.number] = p
    for num, names in T[CODE]["pins"].items():
        pins_by_name.setdefault(names[0], []).append(str(num))
    template = next(iter(old.values()))
    unit = sym.units[0]

    def make(num, name, x, y, angle, ptype):
        p = copy.deepcopy(template)
        p.number, p.name = str(num), name
        p.position = Position(round(x, 4), round(y, 4), angle)
        p.length = PIN_LEN
        p.electricalType = ptype
        p.graphicalStyle = "line"
        p.nameEffects = Effects(font=Font(height=1.27, width=1.27))
        p.numberEffects = Effects(font=Font(height=1.0, width=1.0))
        return p

    pins = []
    used = set()

    def take(pin_name):
        for n in pins_by_name[pin_name]:
            if n not in used:
                used.add(n)
                return n
        raise KeyError(pin_name)

    # signal sides ---------------------------------------------------------------
    rows = {"left": 0, "right": 0}
    layout = {"left": [], "right": []}
    for side, title, items in pinmap.LEFT_RIGHT:
        if layout[side]:
            layout[side].append(None)            # blank row between groups
        layout[side] += items
    nrows = max(len(v) for v in layout.values())
    top_y = (nrows + 1) * PITCH / 2
    body_h = (nrows + 1) * PITCH
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
                pins.append(make(num, name, -BODY_HALF_W - PIN_LEN, y, 0, ptype))
            else:
                pins.append(make(num, name, BODY_HALF_W + PIN_LEN, y, 180, ptype))
    # supplies ---------------------------------------------------------------------
    def supply_row(names, y, angle, start):
        for k, n in enumerate(names):
            num = take(n)
            x = start + k * 5 * PITCH
            pins.append(make(num, n, x, y, angle, "passive" if n.startswith("VCAP") else "power_in"))

    top_start = -(len(pinmap.TOP) - 1) * 2.5 * PITCH
    bot_start = -(len(pinmap.BOTTOM) - 1) * 2.5 * PITCH
    supply_row(pinmap.TOP, top_y + PIN_LEN, 270, top_start)
    supply_row(pinmap.BOTTOM, -top_y - PIN_LEN, 90, bot_start)
    assert len(pins) == 100 and len(used) == 100, (len(pins), len(used))
    unit.pins = pins
    unit.graphicItems = [SyRect(start=Position(-BODY_HALF_W, top_y), end=Position(BODY_HALF_W, -top_y))]
    sym.units = [unit]
    print(f"STM32 symbol re-laid out: {len(pins)} pins, body {2 * BODY_HALF_W} x {2 * top_y} mm, "
          f"left {len(layout['left'])} rows, right {len(layout['right'])} rows")


URB = {"C5369843", "C3031185", "C5369844"}


def relayout_urb(lib):
    n = 0
    for sym in lib.symbols:
        pr = {p.key: p.value for p in sym.properties}
        if (pr.get("LCSC") or pr.get("LCSC Part")) not in URB:
            continue
        unit = sym.units[0]
        old = {p.number: p for p in unit.pins}
        # (pin number, x, y, angle, name, type)
        spec = [("2", -15.24, 5.08, 0, "VIN", "power_in"), ("3", -15.24, 0, 0, "CTRL", "input"),
                ("1", -15.24, -5.08, 0, "GND", "power_in"),
                ("6", 15.24, 5.08, 180, "+VO", "power_out"), ("7", 15.24, -5.08, 180, "-VO", "power_out"),
                ("5", -2.54, -15.24, 90, "NC", "no_connect"), ("8", 2.54, -15.24, 90, "NC", "no_connect")]
        pins = []
        for num, x, y, a, name, ptype in spec:
            p = copy.deepcopy(old[num])
            p.name, p.position = name, Position(x, y, a)
            p.length, p.electricalType, p.graphicalStyle = PIN_LEN, ptype, "line"
            p.nameEffects = Effects(font=Font(height=1.27, width=1.27))
            p.numberEffects = Effects(font=Font(height=1.0, width=1.0))
            pins.append(p)
        unit.pins = pins
        unit.graphicItems = [SyRect(start=Position(-10.16, 10.16), end=Position(10.16, -10.16))]
        sym.units = [unit]
        n += 1
    print(f"URB symbols re-laid out: {n}")


def main():
    lib = SymbolLib.from_file(LIB)
    relayout_stm32(lib)
    relayout_urb(lib)
    libio.save(lib, LIB)


if __name__ == "__main__":
    main()
