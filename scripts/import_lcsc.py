#!/usr/bin/env python3
"""Import every non-passive LCSC part from bom/parts.csv into the project library.

Writes lib/lcsc.kicad_sym, lib/lcsc.pretty/ and lib/lcsc.3dshapes/ using
easyeda2kicad (always the project library, never a global one).

The EasyEDA API sits behind CloudFront and answers 403 intermittently from
cloud IPs, so each part is retried with backoff. Parts already imported are
skipped (re-run safely). Resistors, capacitors, LEDs, ferrite beads and resistor
arrays are NOT imported: they use KiCad's standard symbols and footprints with
the LCSC field filled (CLAUDE.md).

Usage:  python3 -I scripts/import_lcsc.py [--only C56621 C80933 ...]
"""
import csv
import os
import re
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SYM = os.path.join(ROOT, "lib", "lcsc.kicad_sym")
BOM = os.path.join(ROOT, "bom", "parts.csv")
STATE = os.path.join(ROOT, "lib", ".imported")

# Descriptions that mean "standard KiCad symbol/footprint, no import".
STANDARD = re.compile(
    r"^(\d|LED|Heartbeat LED|Relay ON LED|EtherCAT (RUN|ERR) LED|Input state LED|Ferrite)|"
    r"resistor array|^\d+(\.\d+)? ?[kMR] |^\d+(\.\d+)? ?(nF|uF|pF|k|R)\b|thin film",
    re.I,
)
PASSIVE_WORDS = ("resistor", " R 1%", " k 1%", " M 1%", " nF ", " uF ", "LED", "Ferrite bead", "x4 resistor")


# EasyEDA has no data for these (404): added by scripts/make_manual_parts.py
MANUAL = {"C440881", "C440884", "C5272782", "C187509", "C357543"}


def wanted_codes():
    codes = []
    for r in csv.DictReader(open(BOM, encoding="utf-8")):
        c, d = r["LCSC"], r["Description"]
        if not c or c in codes:
            continue
        low = d.lower()
        is_passive = (
            "led" in low.split()[-3:] or " led " in low or low.startswith(("led", "ferrite"))
            or "ferrite bead" in low
            or re.match(r"^[\d.]+ ?(k|m|r|nf|uf|pf)\b", low)
            or "resistor array" in low
            or "thin film" in low
        )
        # electrolytic caps and PTC/fuses are NOT plain passives: they need
        # non-standard footprints, so they are imported.
        if re.match(r"^[\d.]+ ?(nf|uf)\b", low) and "electrolytic" not in low and "2 kv" not in low:
            is_passive = True
        if "1 nf 2 kv" in low:
            is_passive = True
        if is_passive and "electrolytic" not in low:
            continue
        if c in MANUAL:
            continue
        codes.append(c)
    return codes


def done():
    return set(open(STATE).read().split()) if os.path.exists(STATE) else set()


def import_one(code, tries=8):
    delay = 8
    for attempt in range(1, tries + 1):
        p = subprocess.run(
            ["easyeda2kicad", "--lcsc_id", code, "--full", "--output", SYM,
             "--project-relative", "--use-cache", "--overwrite", "--debug"],
            cwd=ROOT, capture_output=True, text=True,
        )
        out = p.stdout + p.stderr
        if p.returncode == 0 and "[ERROR]" not in out and "Created" in out + "Created":
            if "Failed" not in out:
                return True, out
        if "not found" in out.lower() or "404" in out:
            return False, out + "\n(EasyEDA has no data for this part: permanent, not retried)"
        if "403" in out or "Forbidden" in out or "Failed to fetch" in out:
            time.sleep(delay)
            delay = min(delay * 2, 90)
            continue
        return False, out
    return False, out


def main():
    only = sys.argv[sys.argv.index("--only") + 1:] if "--only" in sys.argv else None
    codes = only or wanted_codes()
    os.makedirs(os.path.join(ROOT, "lib"), exist_ok=True)
    have = done()
    failed = []
    for c in codes:
        if c in have:
            print(f"{c}: already imported")
            continue
        ok, out = import_one(c)
        print(f"{c}: {'OK' if ok else 'FAILED'}")
        if ok:
            with open(STATE, "a") as f:
                f.write(c + "\n")
        else:
            failed.append(c)
            print("   ", out.strip().splitlines()[-1] if out.strip() else "")
    print(f"\nimported {len(codes) - len(failed)}/{len(codes)}; failed: {failed}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
