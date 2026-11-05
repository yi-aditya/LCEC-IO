#!/usr/bin/env python3
"""Look up LCSC part data (model, package, stock, price, parameters).

Usage:
    lcsc_lookup.py C15742 C2595919 ...        # human-readable summary
    lcsc_lookup.py --json C15742              # raw selected fields as JSON

Uses the public LCSC product-detail endpoint. Stock changes daily; always
re-run before ordering.
"""
import json
import sys
import time
import urllib.request

URL = "https://wmsc.lcsc.com/ftps/wm/product/detail?productCode={}"
UA = {"User-Agent": "Mozilla/5.0"}


def fetch(code, retries=3):
    last = None
    for i in range(retries):
        try:
            req = urllib.request.Request(URL.format(code), headers=UA)
            with urllib.request.urlopen(req, timeout=30) as r:
                d = json.load(r)
            if d.get("code") != 200 or not d.get("result"):
                return None
            return d["result"]
        except Exception as e:  # network hiccup: retry
            last = e
            time.sleep(2 * (i + 1))
    raise RuntimeError(f"{code}: {last}")


def summarise(code):
    r = fetch(code)
    if r is None:
        return {"code": code, "found": False}
    ladder = r.get("productPriceList") or []
    price1 = ladder[0]["usdPrice"] if ladder else None
    return {
        "code": code,
        "found": True,
        "model": r.get("productModel"),
        "brand": r.get("brandNameEn"),
        "package": r.get("encapStandard"),
        "category": r.get("catalogName"),
        "description": r.get("productIntroEn"),
        "stock": r.get("stockNumber"),
        "price_usd_qty1": price1,
        "min_buy": r.get("minBuyNumber"),
        "lib": r.get("smtLabel"),  # EXPAND = extended, else basic/preferred
        "datasheet": r.get("pdfUrl"),
        "params": {
            p.get("paramNameEn"): p.get("paramValueEn")
            for p in (r.get("paramVOList") or [])
        },
    }


def main(argv):
    as_json = "--json" in argv
    codes = [a for a in argv if not a.startswith("--")]
    out = [summarise(c) for c in codes]
    if as_json:
        json.dump(out, sys.stdout, indent=2, ensure_ascii=False)
        print()
        return
    for s in out:
        if not s["found"]:
            print(f"{s['code']}: NOT FOUND")
            continue
        print(f"{s['code']}  {s['model']}  [{s['brand']}]  {s['package']}")
        print(f"   {s['description']}")
        print(f"   stock={s['stock']}  $%s@1  lib={s['lib']}" % s["price_usd_qty1"])
        for k, v in s["params"].items():
            print(f"   - {k}: {v}")


if __name__ == "__main__":
    main(sys.argv[1:])
