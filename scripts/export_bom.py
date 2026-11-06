#!/usr/bin/env python3
"""Export the BOM from the finished schematic (KiCad's own export, all hierarchical instances) to docs/review/.

  M6-bom.csv           every line, grouped by LCSC number, with the fit column
  M6-bom-assembly.csv  what PCBPower assembles and buys on lcec.com: fitted parts only (no DNP, no locally bought parts,
                       no accessories that are not on the PCB)

Fit: Y = placed on the board; ACC = accessory in the BOM but not on the PCB (plugs, covers, shunts, screw);
LOCAL = bought in India, not on LCSC (relays, T5A fuses); DNP = footprint only, not fitted (relay snubbers, 120 R terminations).
"""
import csv
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCH = os.path.join(ROOT, "hardware", "lcec-io.kicad_sch")
OUT = os.path.join(ROOT, "docs", "review")


def export(group_by, path):
    subprocess.run(["kicad-cli", "sch", "export", "bom", "-o", path, "--fields", "Reference,Value,Footprint,${QUANTITY},LCSC,MPN,Manufacturer,${DNP},${EXCLUDE_FROM_BOARD}",
                    "--labels", "Refs,Value,Footprint,Qty,LCSC,MPN,Manufacturer,DNP,NotOnBoard", "--group-by", group_by,
                    "--ref-range-delimiter", "", SCH], check=True, capture_output=True)
    return list(csv.DictReader(open(path, encoding="utf-8")))


def fit(r):
    lc = r["LCSC"]
    if lc.startswith("LOCAL"):
        return "LOCAL"
    if lc.startswith("DNP") or r["DNP"] == "DNP":
        return "DNP"
    if r["NotOnBoard"]:
        return "ACC"
    return "Y"


def main():
    rows = export("LCSC,Value,Footprint", os.path.join(OUT, "_bom_raw.csv"))
    os.remove(os.path.join(OUT, "_bom_raw.csv"))
    cols = ["Refs", "Qty", "Value", "Footprint", "LCSC", "MPN", "Manufacturer", "Fit"]
    out = []
    for r in rows:
        r["Fit"] = fit(r)
        out.append(r)
    out.sort(key=lambda r: (r["Fit"] != "Y", r["Refs"].split(",")[0][0], int("".join(c for c in r["Refs"].split(",")[0] if c.isdigit()) or 0)))
    with open(os.path.join(OUT, "M6-bom.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(out)
    asm = [r for r in out if r["Fit"] == "Y" and r["LCSC"].startswith("C")]
    with open(os.path.join(OUT, "M6-bom-assembly.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["Refs", "Qty", "Value", "Footprint", "LCSC", "MPN", "Manufacturer"], extrasaction="ignore")
        w.writeheader()
        w.writerows(asm)
    n = {k: sum(int(r["Qty"]) for r in out if r["Fit"] == k) for k in ("Y", "ACC", "LOCAL", "DNP")}
    print(f"{len(out)} BOM lines; pieces fitted {n['Y']}, accessories {n['ACC']}, bought locally {n['LOCAL']}, not fitted {n['DNP']}; "
          f"{len(asm)} assembly lines")
    return 0


if __name__ == "__main__":
    sys.exit(main())
