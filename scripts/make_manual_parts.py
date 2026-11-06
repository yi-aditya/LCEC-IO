#!/usr/bin/env python3
"""Add the parts EasyEDA has no data for (404 'Component not found').

  C5272782  Keystone 7770 PE terminal: footprint drawn from the Keystone drawing
            (four 1.52 mm square pins on a 5.00 x 7.01 mm rectangle, 1.85 mm holes),
            one electrical pin 'PE' on all four pads. No 3D model.
  C440881   KF2EDGK-5.08-3P-AA cable plug  } accessories, no pins, not on the PCB:
  C440884   KF2EDGK-5.08-6P cable plug     } cloned from the sibling plug symbol.
  C187509   Littelfuse 648 clear cover for the fuse block   } accessories, no pins,
  C357543   M3 x 6 screw for the PE terminal                  } not on the PCB.

Run after import_lcsc.py and before fix_symbols.py. Safe to re-run.
"""
import copy
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kiutils.footprint import Footprint  # noqa: E402
from kiutils.items.common import Position  # noqa: E402
from kiutils.items.fpitems import FpRect  # noqa: E402
from kiutils.symbol import SymbolLib  # noqa: E402

LIB = os.path.join(ROOT, "lib", "lcsc.kicad_sym")
PRETTY = os.path.join(ROOT, "lib", "lcsc.pretty")
FP_NAME = "Keystone_7770_M3_PCB_Terminal"


def keystone_footprint():
    donor = Footprint.from_file(os.path.join(PRETTY, "HDR-TH_3P-P2.54-V-M_PZ254V-11-03P.kicad_mod"))
    fp = copy.deepcopy(donor)
    fp.entryName = FP_NAME
    fp.models = []
    pad0 = donor.pads[0]
    pads = []
    for dx, dy in ((-2.5, -3.505), (2.5, -3.505), (-2.5, 3.505), (2.5, 3.505)):
        p = copy.deepcopy(pad0)
        p.number = "1"
        p.position = Position(dx, dy, 0)
        p.shape = "circle"
        p.size.X = p.size.Y = 3.2
        p.drill.diameter = 1.85
        pads.append(p)
    fp.pads = pads
    fp.graphicItems = []
    # silkscreen body 7.87 x 7.87 (datasheet .310 in) and courtyard
    fp.graphicItems.append(FpRect(start=Position(-3.935, -3.935), end=Position(3.935, 3.935), layer="F.SilkS", width=0.15))
    fp.graphicItems.append(FpRect(start=Position(-4.6, -4.6), end=Position(4.6, 4.6), layer="F.CrtYd", width=0.05))
    fp.tags = "Keystone 7770 M3 PCB screw terminal"
    fp.description = ("Keystone 7770 (metric M3, vertical, press-in). Drawn from the Keystone drawing: four 1.52 mm "
                      "square pins, 5.00 x 7.01 mm, holes 1.85 mm. All pads are one terminal. Check against a sample "
                      "before layout is frozen.")
    fp.to_file(os.path.join(PRETTY, FP_NAME + ".kicad_mod"))
    return FP_NAME


MANUAL = {"C440881", "C440884", "C5272782", "C187509", "C357543"}


def rename_units(sym, old, new):
    """KiCad requires unit names to start with the parent symbol name."""
    for u in sym.units:
        u.entryName = u.entryName.replace(old, new, 1)


def main():
    lib = SymbolLib.from_file(LIB)

    def code(sym):
        pr = {p.key: p.value for p in sym.properties}
        return pr.get("LCSC") or pr.get("LCSC Part")

    lib.symbols = [x for x in lib.symbols if code(x) not in MANUAL]  # always regenerate
    have = {}
    for s in lib.symbols:
        props = {p.key: p for p in s.properties}
        c = (props.get("LCSC") or props.get("LCSC Part")).value
        have[c] = s
    added = []

    def clone(donor_code, new_code, name, mpn, ref):
        d = have[donor_code]
        s = copy.deepcopy(d)
        rename_units(s, d.entryName, name)
        s.entryName = name
        for p in s.properties:
            if p.key in ("LCSC", "LCSC Part"):
                p.value = new_code
            elif p.key == "Value":
                p.value = name
            elif p.key == "MPN":
                p.value = mpn
            elif p.key == "Datasheet":
                p.value = f"https://www.lcsc.com/datasheet/{new_code}.pdf"
        lib.symbols.append(s)
        have[new_code] = s
        added.append(new_code)
        return s

    if "C440881" not in have:
        clone("C440880", "C440881", "KF2EDGK-5.08-3P-AA", "KF2EDGK-5.08-3P-AA", "P")
    if "C440884" not in have:
        clone("C440880", "C440884", "KF2EDGK-5.08-6P", "KF2EDGK-5.08-6P", "P")
    if "C187509" not in have:
        clone("C440880", "C187509", "64800001009", "64800001009", "F")
    if "C357543" not in have:
        clone("C440880", "C357543", "PM3X6", "PM3X6", "H")
    if "C5272782" not in have:
        d = have["C441204"]  # 2-pole header symbol as the graphic donor
        s = copy.deepcopy(d)
        rename_units(s, d.entryName, "Keystone-7770")
        s.entryName = "Keystone-7770"
        pins = [p for u in s.units for p in u.pins]
        keep = pins[0]
        for u in s.units:
            u.pins = []
        keep.number, keep.name, keep.electricalType = "1", "PE", "passive"
        s.units[0].pins = [keep]
        for p in s.properties:
            if p.key in ("LCSC", "LCSC Part"):
                p.value = "C5272782"
            elif p.key == "Value":
                p.value = "Keystone-7770"
            elif p.key == "MPN":
                p.value = "7770"
            elif p.key == "Footprint":
                p.value = "lcsc:" + keystone_footprint()
            elif p.key == "Datasheet":
                p.value = "https://www.lcsc.com/datasheet/C5272782.pdf"
        lib.symbols.append(s)
        added.append("C5272782")
    if added:
        lib.to_file(LIB)
    print("added:", added or "nothing (already present)")


if __name__ == "__main__":
    main()
