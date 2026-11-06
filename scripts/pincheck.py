#!/usr/bin/env python3
"""Check imported symbols and footprints against the datasheet pin tables.

For every symbol in the library whose LCSC number has an entry in
scripts/pin_tables.py:
  1. every expected pin number exists on the symbol, and no extra pins exist
  2. each pin name matches the datasheet name (see `match` in pin_tables.py)
  3. +/- polarity where it matters (op-amp inputs, module outputs, RJ45 pairs)
  4. every symbol pin number has a footprint pad with the same number, and
     every footprint pad has a symbol pin (footprints named in the Footprint field)
Also checks that every symbol has Value, Footprint, LCSC, MPN, Manufacturer and
Datasheet fields (CLAUDE.md) and that no pin is left as 'unspecified'.

Usage: pincheck.py [lib/lcsc.kicad_sym] [--md docs/review/M2-pin-check.md]
Exit status 1 if anything fails.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kiutils.symbol import SymbolLib  # noqa: E402
from pin_tables import T  # noqa: E402

REQUIRED = ["Value", "Footprint", "LCSC", "MPN", "Manufacturer", "Datasheet"]


def tokens(name):
    n = name.upper().replace("~{", "").replace("}", "").replace("_", "")
    return set(re.findall(r"[A-Z0-9]+", n))


def pieces(name):
    out = set()
    for p in name.upper().replace("~{", "").replace("}", "").split("/"):
        p = re.sub(r"[^A-Z0-9]", "", p)
        if p:
            out.add(p)
    return out


def alias_norm(a):
    return re.sub(r"[^A-Z0-9]", "", a.upper().replace("_", ""))


def pad_list(fp_dir, fp_name):
    """[(number, x, y)] in file order; unnumbered pads are np1, np2, ..."""
    path = os.path.join(fp_dir, fp_name.split(":", 1)[-1] + ".kicad_mod")
    if not os.path.exists(path):
        return None
    s = open(path, encoding="utf-8").read()
    out, n = [], 0
    for m in re.finditer(r'\(pad "?([A-Za-z0-9_]*)"?\s+\w+\s+\w+\s+\(at ([-\d.]+) ([-\d.]+)', s):
        num = m.group(1)
        if not num:
            n += 1
            num = f"np{n}"
        out.append((num, float(m.group(2)), float(m.group(3))))
    return out


def geometry_errors(exp, pads, tol=0.15):
    errs, rows = [], []
    first = {}
    for num, x, y in pads:
        first.setdefault(num, (x, y))
    for a, b, dx, dy in exp.get("geometry", []):
        if a not in first or b not in first:
            errs.append(f"geometry: pad {a} or {b} not found")
            continue
        gx, gy = abs(first[a][0] - first[b][0]), abs(first[a][1] - first[b][1])
        ok = (dx is None or abs(gx - dx) <= tol) and (dy is None or abs(gy - dy) <= tol)
        rows.append((f"{a}-{b}", f"dx {dx if dx is not None else '-'} dy {dy if dy is not None else '-'}",
                     f"dx {gx:.2f} dy {gy:.2f}", ok))
        if not ok:
            errs.append(f"geometry pads {a}-{b}: footprint dx {gx:.2f} dy {gy:.2f} vs datasheet dx {dx} dy {dy}")
    if exp.get("bbox"):
        xs = [x for _, x, _ in pads]
        ys = [y for _, _, y in pads]
        w, h = max(xs) - min(xs), max(ys) - min(ys)
        bw, bh = exp["bbox"]
        ok = abs(w - bw) <= 0.05 and abs(h - bh) <= 0.05
        rows.append(("pad bounding box", f"{bw} x {bh}", f"{w:.2f} x {h:.2f}", ok))
        if not ok:
            errs.append(f"bounding box {w:.2f} x {h:.2f} vs datasheet {bw} x {bh}")
    return errs, rows


def pad_numbers(fp_dir, fp_name):
    path = os.path.join(fp_dir, fp_name.split(":", 1)[-1] + ".kicad_mod")
    if not os.path.exists(path):
        return None
    s = open(path, encoding="utf-8").read()
    return set(re.findall(r'\(pad "?([A-Za-z0-9_]+)"?\s+\w+', s))


def check(libpath):
    lib = SymbolLib.from_file(libpath)
    fp_dir = os.path.join(os.path.dirname(libpath), "lcsc.pretty")
    results = []
    for s in lib.symbols:
        props = {p.key: p.value for p in s.properties}
        lcsc = props.get("LCSC") or props.get("LCSC Part") or ""
        errs = []
        for k in REQUIRED:
            if k not in props or not props[k].strip():
                if not (k == "Footprint" and s.onBoard is False):
                    errs.append(f"missing field {k}")
        pins = {}
        for u in s.units:
            for p in u.pins:
                pins[p.number] = p
        for num, p in pins.items():
            if p.electricalType == "unspecified":
                errs.append(f"pin {num} ({p.name}) type unspecified")
        exp = T.get(lcsc)
        rows = []
        if exp:
            epins = {str(k): v for k, v in exp["pins"].items()}
            for num in sorted(set(epins) | set(pins), key=lambda x: (not x.isdigit(), int(x) if x.isdigit() else 0, x)):
                if num not in pins:
                    errs.append(f"pin {num} missing on symbol (datasheet: {epins[num][0]})")
                    rows.append((num, "-", "/".join(epins[num]), False))
                    continue
                if num not in epins:
                    errs.append(f"extra pin {num} ({pins[num].name}) not in datasheet")
                    rows.append((num, pins[num].name, "-", False))
                    continue
                name = pins[num].name
                if all(a in ("+", "-") for a in epins[num]):
                    ok = name.strip() in epins[num]  # polarity-only names compare literally
                elif exp.get("match") == "set":
                    ok = pieces(name) == {alias_norm(a) for a in epins[num]}
                else:
                    ok = bool(tokens(name) & {alias_norm(a) for a in epins[num]})
                pol = (exp.get("polarity") or {}).get(int(num) if num.isdigit() else num)
                if ok and pol:
                    ok = pol in name
                if not ok:
                    errs.append(f"pin {num}: symbol '{name}' vs datasheet '{'/'.join(epins[num])}'")
                rows.append((num, name, "/".join(epins[num]), ok))
        fp = props.get("Footprint", "")
        pads = pad_numbers(fp_dir, fp) if fp else None
        if fp:
            if pads is None:
                errs.append(f"footprint '{fp}' not found in lib/lcsc.pretty")
            else:
                sp, fpp = set(pins), pads
                if sp != fpp:
                    errs.append(f"symbol pins {sorted(sp - fpp)} have no pad; pads {sorted(fpp - sp)} have no pin")
        grows = []
        if exp and (exp.get("geometry") or exp.get("bbox")) and fp:
            pl = pad_list(fp_dir, fp)
            if pl is None:
                errs.append("geometry: footprint file not found")
            else:
                gerrs, grows = geometry_errors(exp, pl)
                errs += gerrs
        results.append(dict(symbol=s.entryName, lcsc=lcsc, rows=rows, grows=grows, errs=errs, exp=exp,
                            npins=len(pins), fp=fp, npads=None if pads is None else len(pads)))
    return results


def render_md(results):
    L = ["# M2 - Symbol and footprint pin check\n",
         "Every imported symbol is compared with the manufacturer datasheet pin table (`scripts/pin_tables.py`, "
         "each entry names its source), and with its footprint pad numbers. Re-run with `python3 -I scripts/pincheck.py --md docs/review/M2-pin-check.md`.\n"]
    bad = [r for r in results if r["errs"]]
    L.append(f"**{len(results)} symbols checked, {len(results) - len(bad)} clean, {len(bad)} with problems.**\n")
    L.append("| LCSC | Symbol | Pins | Pads | Datasheet check | Result |\n|---|---|---|---|---|---|")
    for r in results:
        src = "yes" if r["exp"] else "no table (generic part)"
        L.append(f"| {r['lcsc']} | {r['symbol']} | {r['npins']} | {r['npads'] if r['npads'] is not None else '-'} | {src} | "
                 f"{'OK' if not r['errs'] else 'FAIL: ' + '; '.join(r['errs'])} |")
    L.append("\n## Pin-by-pin tables\n")
    for r in results:
        if not r["exp"]:
            continue
        L.append(f"### {r['lcsc']} {r['exp']['part']}\n\nSource: {r['exp']['source']}\n")
        if r["exp"].get("notes"):
            L.append(f"Note: {r['exp']['notes']}\n")
        L.append("| Pin | Symbol name | Datasheet | OK |\n|---|---|---|---|")
        for num, sym, ds, ok in r["rows"]:
            L.append(f"| {num} | {sym} | {ds} | {'yes' if ok else '**NO**'} |")
        L.append("")
        if r.get("grows"):
            L.append("Footprint geometry against the datasheet drawing:\n")
            L.append("| Pads | Datasheet | Footprint | OK |\n|---|---|---|---|")
            for a, b, c, ok in r["grows"]:
                L.append(f"| {a} | {b} | {c} | {'yes' if ok else '**NO**'} |")
            L.append("")
    return "\n".join(L)


def main(argv):
    libpath = next((a for a in argv if a.endswith(".kicad_sym")), os.path.join(ROOT, "lib", "lcsc.kicad_sym"))
    md = argv[argv.index("--md") + 1] if "--md" in argv else None
    results = check(libpath)
    for r in results:
        status = "OK  " if not r["errs"] else "FAIL"
        print(f"{status} {r['lcsc']:<10} {r['symbol']}")
        for e in r["errs"]:
            print("      -", e)
    bad = [r for r in results if r["errs"]]
    print(f"\n{len(results)} symbols, {len(bad)} with problems")
    if md:
        os.makedirs(os.path.dirname(os.path.join(ROOT, md)), exist_ok=True)
        open(os.path.join(ROOT, md), "w", encoding="utf-8").write(render_md(results))
        print("wrote", md)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
