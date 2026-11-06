#!/usr/bin/env python3
"""Post-process lib/lcsc.kicad_sym after easyeda2kicad has imported it.

EasyEDA symbols are generic: unnamed pins, every pin 'unspecified', odd field
names, Chinese manufacturer names. This script, which is safe to re-run:
  * renames pins whose datasheet function is known (see PIN_RENAMES)
  * sets electrical pin types so ERC means something
  * normalises fields: LCSC (not 'LCSC Part'), MPN, Manufacturer (English,
    from bom/parts.csv), Datasheet (direct LCSC PDF link), Value, Reference
  * turns accessories that are not on the PCB (cable plugs, shunt, glass
    fuses) into pin-less 'not on board' symbols
Every change is written to docs/review/M2-symbol-fixes.md.
"""
import csv
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kiutils.symbol import SymbolLib  # noqa: E402
from lcsc_lookup import fetch  # noqa: E402

LIB = os.path.join(ROOT, "lib", "lcsc.kicad_sym")
META = os.path.join(ROOT, "lib", "datasheets.json")
LOG = None  # only written when --log is given (run it on lib/raw/lcsc.imported.kicad_sym)

# pin renames by LCSC number: {pin number: new name}; sources in scripts/pin_tables.py
PIN_RENAMES = {
    "C2595919": {"1": "OE"},
    "C80933": {"5": "VDD33"},
    "C69427": {"4": "TD_CT", "5": "RD_CT", "9": "LEDG_A", "10": "LEDG_K", "11": "LEDY_K", "12": "LEDY_A"},
    "C320242": {"1": "K", "2": "A"},
    "C970679": {"1": "+", "2": "-"},
    "C2960285": {"1": "+", "2": "-"},
    "C39031": {**{str(2 * k - 1): f"IN{k}A" for k in range(1, 5)}, **{str(2 * k): f"IN{k}B" for k in range(1, 5)},
               "16": "C1", "15": "E1", "14": "C2", "13": "E2", "12": "C3", "11": "E3", "10": "C4", "9": "E4"},
    "C32677": {"1": "IO1", "2": "IO2", "3": "COM"},
    "C1524860": {"1": "COIL1", "2": "COM", "3": "NO", "4": "NC", "5": "COIL2"},
}

# parts that are accessories, not placed on the PCB
NOT_ON_BOARD = {"C440880", "C440881", "C440882", "C440884", "C5305", "C3116", "C3118", "C187509", "C357543"}

REFERENCE = {
    "C56621": "U", "C80933": "U", "C615715": "U", "C16040": "U", "C7934": "U", "C42738": "U", "C6180": "U",
    "C428888": "U", "C528653": "U", "C5347249": "U", "C845537": "U", "C5369843": "U", "C3031185": "U",
    "C5369844": "U", "C39031": "U", "C2595919": "X", "C3975188": "J", "C2937625": "J", "C69427": "J",
    "C441204": "J", "C441205": "J", "C441206": "J", "C441208": "J", "C5272782": "J",
    "C440880": "P", "C440881": "P", "C440882": "P", "C440884": "P", "C5305": "JP",
    "C320242": "D", "C22452": "D", "C148216": "D", "C32677": "D", "C83571": "Q",
    "C206887": "F", "C187509": "F", "C357543": "H", "C3116": "F", "C3118": "F", "C151168": "RT", "C70068": "RT",
    "C970679": "C", "C2960285": "C", "C1524860": "K",
}

IC_PARTS = {"C56621", "C80933", "C2595919", "C615715", "C16040", "C7934", "C42738", "C6180", "C428888",
            "C528653", "C5347249", "C845537", "C5369843", "C3031185", "C5369844"}
POWER_IN = re.compile(r"^(VDD|VCC|VBAT|VDDA|VDDB|VDDIO|VDDCR|VDD33|VDD12TX\d|VDD33TXRX\d|VDD33BIAS|OSCVDD12|VIN|VCAP_\d|"
                      r"GND|GNDA|GNDB|VSS|VSSA|OSCVSS)$")
OUTPUT = re.compile(r"^(\dY|VO\d|\dOUT|VOUT[AB]|OUTPUT)$")
INPUT = re.compile(r"^(\d[AB]|~?G|VI\d|EN[AB]|A[0-2]|WP|SCL|~?CS|SCK|SDI|~?LDAC|INPUT|OE|CTRL|BOOT0|OSCI|REG_EN|TESTMODE)$")
NC = re.compile(r"^NC$")


def pin_type(lcsc, name):
    n = name.upper().replace("~{", "~").replace("}", "")
    nn = n.lstrip("~")
    if lcsc in ("C5369843", "C3031185", "C5369844"):
        if nn in ("+VO", "-VO"):
            return "power_out"
    if lcsc == "C42738" and nn == "VOUT":
        return "power_out"
    if lcsc == "C845537" and nn == "OUTPUT":
        return "open_collector"
    if NC.match(nn):
        return "no_connect"
    if POWER_IN.match(nn):
        return "power_in"
    if lcsc == "C80933" and nn == "RST":
        return "input"
    if OUTPUT.match(nn):
        return "output"
    if INPUT.match(nn) or INPUT.match(n):
        return "input"
    if lcsc == "C615715" and nn == "SDA":
        return "bidirectional"
    if lcsc in ("C56621", "C80933"):
        return "bidirectional"
    if lcsc in IC_PARTS:
        return "passive"
    return "passive"


def load_meta(codes):
    meta = json.load(open(META)) if os.path.exists(META) else {}
    for c in codes:
        if c not in meta:
            r = fetch(c)
            meta[c] = (r or {}).get("pdfUrl") or f"https://www.lcsc.com/datasheet/{c}.pdf"
    json.dump(meta, open(META, "w"), indent=1, sort_keys=True)
    return meta


def fix_footprints():
    """3D model paths: the KiCad project lives in hardware/, the library in lib/."""
    import glob
    n = 0
    for f in glob.glob(os.path.join(ROOT, "lib", "lcsc.pretty", "*.kicad_mod")):
        t = open(f, encoding="utf-8").read()
        u = t.replace("${KIPRJMOD}/lib/", "${KIPRJMOD}/../lib/")
        if u != t:
            open(f, "w", encoding="utf-8").write(u)
            n += 1
    return n


def remove_orphans(lib):
    """Delete footprints no symbol uses (accessory placeholders) and 3D models no footprint uses."""
    import glob
    used = set()
    for sym in lib.symbols:
        for p in sym.properties:
            if p.key == "Footprint" and p.value:
                used.add(p.value.split(":", 1)[-1])
    removed = []
    pretty = os.path.join(ROOT, "lib", "lcsc.pretty")
    for f in glob.glob(os.path.join(pretty, "*.kicad_mod")):
        if os.path.basename(f)[:-len(".kicad_mod")] not in used:
            os.remove(f)
            removed.append(os.path.basename(f))
    models = set()
    for f in glob.glob(os.path.join(pretty, "*.kicad_mod")):
        for m in re.findall(r'\(model "([^"]+)"', open(f, encoding="utf-8").read()):
            models.add(os.path.basename(m))
    for f in glob.glob(os.path.join(ROOT, "lib", "lcsc.3dshapes", "*")):
        base = os.path.basename(f)
        stem = os.path.splitext(base)[0]
        if not any(os.path.splitext(m)[0] == stem for m in models):
            os.remove(f)
            removed.append(base)
    return removed


def main():
    global LIB, LOG
    if "--lib" in sys.argv:
        LIB = os.path.abspath(sys.argv[sys.argv.index("--lib") + 1])
    if "--log" in sys.argv:
        LOG = os.path.abspath(sys.argv[sys.argv.index("--log") + 1])
    nfp = fix_footprints()
    bom = {}
    for r in csv.DictReader(open(os.path.join(ROOT, "bom", "parts.csv"), encoding="utf-8")):
        if r["LCSC"] and r["LCSC"] not in bom:
            bom[r["LCSC"]] = r
    lib = SymbolLib.from_file(LIB)
    log = []
    # drop symbols for parts that are no longer in the BOM (e.g. after a part is replaced)
    def _code(sym):
        pr = {q.key: q.value for q in sym.properties}
        return pr.get("LCSC") or pr.get("LCSC Part")
    gone = [sym.entryName for sym in lib.symbols if _code(sym) not in bom]
    lib.symbols = [sym for sym in lib.symbols if _code(sym) in bom]
    if gone:
        log.append(f"| {', '.join(gone)} | removed: part no longer in bom/parts.csv |")

    def note(sym, msg):
        log.append(f"| {sym} | {msg} |")

    codes = []
    for s in lib.symbols:
        props = {p.key: p for p in s.properties}
        c = (props.get("LCSC") or props.get("LCSC Part")).value
        codes.append(c)
    meta = load_meta(codes)

    for s in lib.symbols:
        props = {p.key: p for p in s.properties}
        lcsc = (props.get("LCSC") or props.get("LCSC Part")).value
        b = bom.get(lcsc, {})
        # fields ---------------------------------------------------------
        if "LCSC Part" in props:
            props["LCSC Part"].key = "LCSC"
            note(s.entryName, "field 'LCSC Part' renamed to 'LCSC'")
        for key, val in (("MPN", b.get("MPN") or props["MPN"].value),
                         ("Manufacturer", b.get("Manufacturer") or props["Manufacturer"].value),
                         ("Datasheet", meta.get(lcsc, ""))):
            if props[key].value != val:
                if key != "MPN":
                    note(s.entryName, f"{key}: '{props[key].value[:40]}' -> '{val[:60]}'")
                props[key].value = val
        v = re.sub(r"_C\d+$", "", s.entryName)
        if props["Value"].value != v:
            props["Value"].value = v
        if lcsc in REFERENCE and props["Reference"].value != REFERENCE[lcsc]:
            note(s.entryName, f"Reference '{props['Reference'].value}' -> '{REFERENCE[lcsc]}'")
            props["Reference"].value = REFERENCE[lcsc]
        # not-on-board accessories --------------------------------------------
        if lcsc in NOT_ON_BOARD:
            had = sum(len(u.pins) for u in s.units)
            for u in s.units:
                u.pins = []
            s.onBoard = False
            s.inBom = True
            props["Footprint"].value = ""
            note(s.entryName, f"accessory, not on the PCB: {had} placeholder pin(s) and footprint removed, set 'exclude from board'")
            continue
        # pin renames and types -------------------------------------------------
        ren = PIN_RENAMES.get(lcsc, {})
        for u in s.units:
            for p in u.pins:
                if p.number in ren and p.name != ren[p.number]:
                    note(s.entryName, f"pin {p.number}: '{p.name}' -> '{ren[p.number]}' (datasheet)")
                    p.name = ren[p.number]
                t = pin_type(lcsc, p.name)
                if p.electricalType != t:
                    p.electricalType = t
    lib.to_file(LIB)
    if os.path.abspath(LIB) == os.path.join(ROOT, "lib", "lcsc.kicad_sym"):
        gone = remove_orphans(lib)
        print(f"removed {len(gone)} unused footprint/3D files: {gone[:6]}...")
    if not LOG:
        print(f"{len(log)} changes applied (no --log given, log not written)")
        return
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    with open(LOG, "w", encoding="utf-8") as f:
        f.write("# M2 - Fixes applied to the imported symbols\n\n"
                "easyeda2kicad output is generic. `scripts/fix_symbols.py` corrects it from the datasheets "
                "(re-runnable). Pin electrical types are also set on every symbol (power in/out, input, output, "
                "bidirectional, open collector, no connect, passive); before this every pin was 'unspecified', "
                "which would make ERC silent.\n\n"
                "The log below is produced by running the fixer on the raw EasyEDA import "
                "(`python3 -I scripts/fix_symbols.py --lib <raw copy> --log docs/review/M2-symbol-fixes.md`). "
                "Three parts have no EasyEDA data (404) and were made by `scripts/make_manual_parts.py`: "
                "C5272782 Keystone 7770 (footprint drawn from the Keystone drawing) and the cable plugs C440881 and C440884.\n\n"
                "| Symbol | Change |\n|---|---|\n")
        f.write("\n".join(l for l in log if "type" not in l) + "\n")
    print(f"{len(log)} symbol changes logged -> {LOG}; 3D model path fixed in {nfp} footprints")


if __name__ == "__main__":
    main()
