#!/usr/bin/env python3
"""Search the JLCPCB/LCSC parts catalogue by keyword (read-only).

Usage:
    jlc_search.py "SS54" [--basic] [--n 10] [--instock]

Prints LCSC number, model, brand, package, library type (base/expand),
stock and qty-1 price, then the description. Use lcsc_lookup.py afterwards
to confirm ratings on the chosen part.
"""
import argparse
import json
import urllib.request

URL = "https://jlcpcb.com/api/overseas-pcb-order/v1/shoppingCart/smtGood/selectSmtComponentList"


def search(keyword, n=10, basic=False):
    body = {
        "keyword": keyword,
        "currentPage": 1,
        "pageSize": n,
        "searchSource": "search",
    }
    if basic:
        body["componentLibraryType"] = "base"
    req = urllib.request.Request(
        URL,
        data=json.dumps(body).encode(),
        headers={"User-Agent": "Mozilla/5.0", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        d = json.load(r)
    info = (d.get("data") or {}).get("componentPageInfo") or {}
    return info.get("list") or []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("keyword")
    ap.add_argument("--n", type=int, default=10)
    ap.add_argument("--basic", action="store_true")
    ap.add_argument("--instock", action="store_true")
    a = ap.parse_args()
    for c in search(a.keyword, a.n, a.basic):
        if a.instock and not c.get("stockCount"):
            continue
        print(
            f"{c['componentCode']:>10}  {c['componentModelEn']:<28} "
            f"{(c['componentBrandEn'] or '')[:22]:<22} {c['componentSpecificationEn']:<18} "
            f"{c['componentLibraryType']:<6} stock={c['stockCount']:<7} ${c['initialPrice']}"
        )
        print(f"{'':>12}{c['describe']}")


if __name__ == "__main__":
    main()
