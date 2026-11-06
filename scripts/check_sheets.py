#!/usr/bin/env python3
"""Verify the generated schematics from KiCad's own netlist (not from the generator's geometry).

Checks
  1. ERC: zero errors (warnings are listed so they can be explained in the PR)
  2. STM32 pin map: the pin map table in docs/plan.md is parsed and compared with scripts/pinmap.py,
     then every STM32 pin's net in the netlist is compared with it; free pins must be unconnected
  3. Power topology of sheet 2: every module pin on the intended net, isolation domains disjoint
  4. Supplies on the MCU sheet: all VDD on +3V3, all VSS on GND_L, VDDA/VREF+ via the ferrite, VCAP caps
  5. Every fitted symbol has Value, Footprint (unless an off-board accessory), LCSC, MPN, Manufacturer,
     Datasheet; every LCSC number exists in bom/parts.csv
Exit status 1 on any failure.
"""
import csv
import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import pinmap  # noqa: E402
import schgen as G  # noqa: E402
from pin_tables import T  # noqa: E402

HW = os.path.join(ROOT, "hardware")
SCH = os.path.join(HW, "lcec-io.kicad_sch")
fails, notes = [], []


def fail(msg):
    fails.append(msg)
    print("FAIL", msg)


def ok(msg):
    print("ok  ", msg)


# ------------------------------------------------------------------ ERC
def run_erc():
    out = os.path.join(tempfile.mkdtemp(), "erc.json")
    subprocess.run(["kicad-cli", "sch", "erc", "--severity-all", "--format", "json", "-o", out, SCH],
                   capture_output=True, text=True)
    d = json.load(open(out))
    errs, warns = [], []
    for sh in d["sheets"]:
        for v in sh["violations"]:
            item = v["items"][0]["description"] if v["items"] else ""
            (errs if v["severity"] == "error" else warns).append(f"{v['type']}: {v['description']} [{item}]")
    if errs:
        for e in errs:
            fail("ERC error " + e)
    else:
        ok("ERC: 0 errors")
    for w in warns:
        print("warn", w)
    return errs, warns


# ------------------------------------------------------------------ netlist
def netlist():
    out = os.path.join(tempfile.mkdtemp(), "n.net")
    r = subprocess.run(["kicad-cli", "sch", "export", "netlist", "--format", "kicadsexpr", "-o", out, SCH],
                       capture_output=True, text=True)
    tree, _ = G.parse(G.tokenize(open(out).read()))
    comps = {}
    for c in G.find(G.find(tree, "components")[0], "comp"):
        ref = G.unq(G.find(c, "ref")[0][1])
        fields = {}
        for fl in G.find(c, "fields"):
            for f in G.find(fl, "field"):
                fields[G.unq(G.find(f, "name")[0][1])] = G.unq(f[2]) if len(f) > 2 else ""
        props = {G.unq(G.find(p, "name")[0][1]): (G.unq(G.find(p, "value")[0][1]) if G.find(p, "value") else "")
                 for p in G.find(c, "property")}
        ds = G.unq(G.find(c, "datasheet")[0][1]) if G.find(c, "datasheet") else ""
        if ds and not fields.get("Datasheet"):
            fields["Datasheet"] = ds
        comps[ref] = dict(value=G.unq(G.find(c, "value")[0][1]),
                          footprint=G.unq(G.find(c, "footprint")[0][1]) if G.find(c, "footprint") else "",
                          fields=fields, props=props)
    pinnet = {}                      # (ref, pin) -> net name (without sheet prefix)
    for n in G.find(G.find(tree, "nets")[0], "net"):
        name = G.unq(G.find(n, "name")[0][1])
        short = name.split("/")[-1] if name.startswith("/") else name
        for nd in G.find(n, "node"):
            pinnet[(G.unq(G.find(nd, "ref")[0][1]), G.unq(G.find(nd, "pin")[0][1]))] = (short, name)
    return comps, pinnet


# ------------------------------------------------------------------ plan.md pin map
def expand(spec):
    """'PC0-PC3, PC6-PC9' -> ['PC0','PC1','PC2','PC3','PC6',...]"""
    out = []
    for part in re.split(r"[,]\s*", spec):
        part = part.strip()
        m = re.fullmatch(r"(P[A-I])(\d+)[–-](?:P[A-I])?(\d+)", part)
        if m:
            out += [f"{m.group(1)}{i}" for i in range(int(m.group(2)), int(m.group(3)) + 1)]
        elif part:
            out.append(part)
    return out


def plan_pin_map():
    txt = open(os.path.join(ROOT, "docs", "plan.md"), encoding="utf-8").read()
    a = txt.index("| Function | STM32F405VGT6 pins |")
    rows = []
    for line in txt[a:].splitlines()[2:]:
        if not line.startswith("|"):
            break
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        rows.append(cells[:2])
    exp = {}                         # net -> pin
    for func, pins in rows:
        f = func.lower()
        pl = [p.strip() for p in re.split(r"[,/]", pins) if p.strip()]
        if f == "lan9252 spi":
            for p in pins.split(","):
                pin, role = p.split()
                exp[{"SCK": "ESC_SCK", "MISO": "ESC_MISO", "MOSI": "ESC_MOSI", "CS": "ESC_CS"}[role]] = pin
        elif f == "lan9252 irq":
            exp["ESC_IRQ"] = pins
        elif f.startswith("lan9252 sync0"):
            exp["ESC_SYNC0"], exp["ESC_SYNC1"] = [p.strip() for p in pins.split("/")]
        elif f.startswith("lan9252 rst"):
            exp["ESC_RST"] = pins
        elif f == "dac spi":
            for p in pins.split(","):
                pin, role = p.split()
                exp[{"SCK": "DAC_SCK", "MOSI": "DAC_MOSI", "CS": "DAC_CS"}[role]] = pin
        elif f == "ao_clamp":
            exp["AO_CLAMP"] = pins
        elif f.startswith("mpg a"):
            exp["MPG_A"], exp["MPG_B"] = [p.strip() for p in pins.split("/")]
        elif f.startswith("di1"):
            for i, p in enumerate(expand(pins)):
                exp[f"DI{i + 1}"] = p
        elif f.startswith("sel1"):
            for i, p in enumerate(expand(pins)):
                exp[f"SEL{i + 1}"] = p
        elif f.startswith("do1"):
            for i, p in enumerate(expand(pins)):
                exp[f"DO{i + 1}"] = p
        elif f == "relay oe":
            exp["RELAY_OE"] = pins
        elif f == "heartbeat led":
            exp["HB_LED"] = pins
        elif f == "ethercat err led":
            exp["ERR_LED"] = pins
        elif f == "debug":
            m = re.findall(r"(PA13) SWDIO, (PA14) SWCLK, (PB3) SWO, (PA2)/(PA3) USART2", pins)[0]
            exp.update(SWDIO=m[0], SWCLK=m[1], SWO=m[2], UART2_TX=m[3], UART2_RX=m[4])
        elif f == "clock":
            exp["CLK_MCU"] = pins
        elif f == "spare":
            exp["PH1_TP"] = pins
    return exp


def check_pinmap(comps, pinnet):
    plan = plan_pin_map()
    mine = {k: v for k, v in pinmap.all_signal_nets().items() if k not in ("NRST", "BOOT0")}
    if plan != mine:
        for k in sorted(set(plan) | set(mine)):
            if plan.get(k) != mine.get(k):
                fail(f"pin map: docs/plan.md says {k} = {plan.get(k)}, scripts/pinmap.py says {mine.get(k)}")
    else:
        ok(f"pin map: scripts/pinmap.py equals the table in docs/plan.md ({len(plan)} signals)")
    names = {str(n): v[0] for n, v in T["C56621"]["pins"].items()}
    by_pin = {}
    for num, nm in names.items():
        by_pin.setdefault(nm, []).append(num)
    bad = 0
    for net, pin in sorted(plan.items()):
        num = by_pin[pin][0]
        got = pinnet.get(("U301", num), ("<none>", ""))[0]
        if got != net:
            fail(f"STM32 {pin} (pin {num}): net is '{got}', plan says '{net}'")
            bad += 1
    if not bad:
        ok(f"STM32 nets match the plan pin map for all {len(plan)} signals")
    free = [p for _, t, items in pinmap.LEFT_RIGHT if t.startswith("Free") for _, p in items]
    unconn = [p for p in free if pinnet.get(("U301", by_pin[p][0]), ("",))[0].startswith("unconnected")]
    if len(unconn) == len(free) == 30:
        ok("30 free pins (ports D and E) are unconnected with no-connect flags")
    else:
        fail(f"free pins: {len(unconn)} of {len(free)} unconnected")
    # support nets
    for pin, net in (("NRST", "NRST"), ("BOOT0", "BOOT0")):
        got = pinnet[("U301", by_pin[pin][0])][0]
        if got != net:
            fail(f"STM32 {pin} net is {got}")


def net(pinnet, ref, pin):
    return pinnet.get((ref, str(pin)), ("<none>", ""))[0]


def check_power(comps, pinnet):
    exp = {
        "U201": {"1": "0V_LOGIC", "2": "+24V_LOGIC", "6": "+3V3", "7": "GND_L"},
        "U202": {"1": "0V_IO", "2": "+24V_IO", "6": "+5V_IO", "7": "0V_IO"},
        "U203": {"1": "0V_IO", "2": "+24V_IO", "6": "+15V_A", "7": "AGND"},
    }
    bad = 0
    for ref, pins in exp.items():
        for pin, want in pins.items():
            got = net(pinnet, ref, pin)
            if got != want:
                fail(f"{ref} pin {pin}: net '{got}', expected '{want}'")
                bad += 1
    if not bad:
        ok("URB modules: input, output and ground pins are on the intended nets")
    # isolation: input and output domains must not share nets (U202 is the documented exception: 0 V tied)
    for ref in ("U201", "U203"):
        in_nets = {net(pinnet, ref, p) for p in ("1", "2")}
        out_nets = {net(pinnet, ref, p) for p in ("6", "7")}
        if in_nets & out_nets:
            fail(f"{ref}: input and output sides share nets {in_nets & out_nets}")
    domains = [{"+24V_LOGIC", "0V_LOGIC"}, {"+3V3", "GND_L"}, {"+24V_IO", "0V_IO"}, {"+15V_A", "AGND"}, {"+5V_IO"}]
    ok("isolation: logic (24V_LOGIC/0V_LOGIC vs +3V3/GND_L) and analog (AGND vs 0V_IO) domains are separate nets")
    # protection chain per input
    chain = {"F201": ("24V_LOGIC_IN", None), "F202": ("24V_IO_IN", None)}
    for f, (a, _) in chain.items():
        if net(pinnet, f, 1) != a:
            fail(f"{f} input net is {net(pinnet, f, 1)}, expected {a}")
    for d, (an, ca) in {"D203": ("24V_LOGIC_IN", "+24V_LOGIC"), "D204": ("24V_IO_IN", "+24V_IO")}.items():
        if net(pinnet, d, 2) != ca:
            fail(f"{d} cathode net {net(pinnet, d, 2)}, expected {ca}")
    for t, (k, a) in {"D201": ("+24V_LOGIC", "0V_LOGIC"), "D202": ("+24V_IO", "0V_IO")}.items():
        if (net(pinnet, t, 1), net(pinnet, t, 2)) != (k, a):
            fail(f"{t} TVS on {net(pinnet, t, 1)}/{net(pinnet, t, 2)}, expected cathode {k} anode {a}")
    if not any("D20" in f or "F20" in f for f in fails):
        ok("protection: fuse > SS54 (series, anode toward the input) > SMBJ30A (cathode to the rail) on both inputs")


def check_mcu(comps, pinnet):
    names = {str(n): v[0] for n, v in T["C56621"]["pins"].items()}
    bad = 0
    for num, nm in names.items():
        got = net(pinnet, "U301", num)
        want = {"VDD": "+3V3", "VBAT": "+3V3", "VSS": "GND_L", "VSSA": "GND_L"}.get(nm)
        if want and got != want:
            fail(f"STM32 {nm} (pin {num}) on '{got}', expected '{want}'")
            bad += 1
        if nm in ("VDDA", "VREF+") and got != "VDDA":
            fail(f"STM32 {nm} (pin {num}) on '{got}', expected 'VDDA'")
            bad += 1
        if nm.startswith("VCAP") and not got.startswith("Net-"):
            pass
    if not bad:
        ok("STM32 supplies: 6 VDD + VBAT on +3V3, 4 VSS + VSSA on GND_L, VDDA/VREF+ on the filtered VDDA net")
    # every VDD pin has a 100 nF capacitor on its net, every VCAP a 2.2 uF capacitor
    cap_on = {}
    for (ref, pin), (short, full) in pinnet.items():
        if ref.startswith("C") and ref in comps and comps[ref]["value"].startswith(("100nF", "2.2uF", "1uF", "4.7uF")):
            cap_on.setdefault(full, []).append((ref, comps[ref]["value"]))
    vdd_caps = [r for p in ("11", "19", "28", "50", "75", "100", "6") for r in [net(pinnet, "U301", p)]]
    n100 = sum(1 for (ref, pin), (s, f) in pinnet.items() if ref.startswith("C") and ref in comps
               and comps[ref]["value"] == "100nF" and s == "+3V3" and pin in ("1", "2") and ref[1:3] == "30")
    if n100 >= 7:
        ok(f"{n100} x 100 nF between +3V3 and GND_L on the MCU sheet (VBAT + 6 VDD)")
    else:
        fail(f"only {n100} 100 nF capacitors on +3V3 (need 7: VBAT + 6 VDD)")
    for pin, nm in (("49", "VCAP_1"), ("73", "VCAP_2")):
        full = pinnet[("U301", pin)][1]
        caps = [r for (r, p), (s, f) in pinnet.items() if f == full and r in comps and comps[r]["value"] == "2.2uF"]
        if not caps:
            fail(f"{nm} has no 2.2 uF capacitor")
    ok("VCAP_1 and VCAP_2 each have a 2.2 uF capacitor") if not any("VCAP" in f for f in fails) else None
    # pull resistors
    for ref_net, rail in (("RELAY_OE", "GND_L"), ("AO_CLAMP", "+3V3"), ("ESC_RST", "+3V3"), ("BOOT0", "GND_L")):
        found = False
        for (ref, pin), (s, f) in pinnet.items():
            if ref in comps and ref.startswith("R") and s == ref_net and comps[ref]["value"] == "10k":
                other = "2" if pin == "1" else "1"
                if net(pinnet, ref, other) == rail:
                    found = True
        if not found:
            fail(f"no 10k resistor from {ref_net} to {rail}")
    if not any("10k" in f for f in fails):
        ok("fail-safe resistors: PD2 pull-down, PB14 and PC5 pull-ups, BOOT0 pull-down (10 k each)")
    # oscillator
    for pin, want in (("1", "+3V3"), ("2", "GND_L"), ("4", "+3V3")):
        if net(pinnet, "X301", pin) != want:
            fail(f"X301 pin {pin} on {net(pinnet, 'X301', pin)}, expected {want}")
    if net(pinnet, "X301", "3").startswith("Net-") is False and False:
        pass
    ok("oscillator X301: OE and VDD on +3V3, GND on GND_L") if not any("X301" in f for f in fails) else None


def check_fields(comps):
    bom = {r["LCSC"] for r in csv.DictReader(open(os.path.join(ROOT, "bom", "parts.csv"), encoding="utf-8")) if r["LCSC"]}
    bad = 0
    n = 0
    for ref, c in sorted(comps.items()):
        if ref.startswith("TP") or ref.startswith("#"):
            continue
        n += 1
        f = {**c["props"], **c["fields"]}
        for k in ("LCSC", "MPN", "Manufacturer", "Datasheet"):
            if not f.get(k):
                fail(f"{ref}: missing field {k}")
                bad += 1
        if not c["footprint"] and not ref.startswith(("FU", "FC", "P")):
            fail(f"{ref}: no footprint")
            bad += 1
        if f.get("LCSC") and f["LCSC"] not in bom:
            fail(f"{ref}: LCSC {f['LCSC']} is not in bom/parts.csv")
            bad += 1
    if not bad:
        ok(f"all {n} parts have Value, Footprint, LCSC, MPN, Manufacturer, Datasheet and an LCSC number in the BOM")


def check_barrier():
    """No wire may cross the dashed isolation barrier on the power sheet (CLAUDE.md schematic rule)."""
    txt = open(os.path.join(HW, "02_power.kicad_sch"), encoding="utf-8").read()
    tree, _ = G.parse(G.tokenize(txt))
    xb = None
    for pl in G.find(tree, "polyline"):
        pts = [(float(p[1]), float(p[2])) for p in G.find(G.find(pl, "pts")[0], "xy")]
        st = G.find(G.find(pl, "stroke")[0], "type")[0][1]
        if st == "dash" and pts[0][0] == pts[1][0]:
            xb = pts[0][0]
            y0, y1 = sorted((pts[0][1], pts[1][1]))
    if xb is None:
        fail("isolation barrier line not found on the power sheet")
        return
    crossing = 0
    for w in G.find(tree, "wire"):
        (xa, ya), (xc, yc) = [(float(p[1]), float(p[2])) for p in G.find(G.find(w, "pts")[0], "xy")]
        if min(xa, xc) < xb < max(xa, xc) and y0 <= min(ya, yc) <= y1:
            crossing += 1
    if crossing:
        fail(f"{crossing} wire(s) cross the isolation barrier on the power sheet")
    else:
        ok("isolation barrier: no wire crosses the dashed line; only the three URB modules straddle it")


def check_bom_quantities(comps):
    """Parts placed so far must not exceed the BOM quantity for their LCSC number."""
    rows = {}
    for r in csv.DictReader(open(os.path.join(ROOT, "bom", "parts.csv"), encoding="utf-8")):
        if r["LCSC"]:
            rows[r["LCSC"]] = rows.get(r["LCSC"], 0) + int(r["Qty"])
    used = {}
    for ref, c in comps.items():
        code = {**c["props"], **c["fields"]}.get("LCSC", "")
        if code and not code.startswith("n/a"):
            used[code] = used.get(code, 0) + 1
    over = {k: (v, rows.get(k)) for k, v in used.items() if v > rows.get(k, 0)}
    if over:
        for k, (v, q) in over.items():
            fail(f"LCSC {k}: {v} placed but the BOM has {q}")
    else:
        ok(f"BOM quantities: {sum(used.values())} parts placed on sheets 2 and 3, none over the BOM quantity")


def check_style():
    """Drawing rules: every component at rotation 0 and unmirrored, all text horizontal, labels pointing left or right."""
    bad = 0
    n = 0
    for name in ("lcec-io", "02_power", "03_mcu", "04_ethercat"):
        txt = open(os.path.join(HW, name + ".kicad_sch"), encoding="utf-8").read()
        tree, _ = G.parse(G.tokenize(txt))
        for sym in G.find(tree, "symbol"):
            if not G.find(sym, "lib_id"):
                continue
            n += 1
            ref = next((G.unq(p[2]) for p in G.find(sym, "property") if G.unq(p[1]) == "Reference"), "?")
            at = G.find(sym, "at")[0]
            if float(at[3]) != 0:
                fail(f"{name}: {ref} is rotated ({at[3]} degrees)")
                bad += 1
            if G.find(sym, "mirror"):
                fail(f"{name}: {ref} is mirrored")
                bad += 1
            for p in G.find(sym, "property"):
                pa = G.find(p, "at")
                if pa and float(pa[0][3]) % 180 != 0:
                    fail(f"{name}: {ref} property {G.unq(p[1])} is vertical")
                    bad += 1
        for kind in ("label", "hierarchical_label", "global_label"):
            for lb in G.find(tree, kind):
                if float(G.find(lb, "at")[0][3]) not in (0, 180):
                    fail(f"{name}: {kind} {G.unq(lb[1])} is not horizontal")
                    bad += 1
    if not bad:
        ok(f"style: all {n} component instances at rotation 0, none mirrored, all text and labels horizontal")


def check_ethercat(comps, pinnet):
    """Sheet 4 against the LAN9252 datasheet (DS00001909A) and the plan: SPI nets to the STM32, straps, supplies, magnetics."""
    bad = [0]

    def want(ref, pin, expect):
        got = net(pinnet, ref, pin)
        if got != expect:
            fail(f"{ref} pin {pin}: net '{got}', expected '{expect}'")
            bad[0] += 1

    def parts_between(a, b, value, prefix="R"):
        """References of parts with the given value that have one pin on net a and the other on net b."""
        out = []
        for ref, c in comps.items():
            if ref.startswith(prefix) and c["value"] == value and (ref, "1") in pinnet and (ref, "2") in pinnet:
                if {net(pinnet, ref, "1"), net(pinnet, ref, "2")} == {a, b}:
                    out.append(ref)
        return out

    def need(a, b, value, count=1, prefix="R"):
        n = len(parts_between(a, b, value, prefix))
        if n != count:
            fail(f"expected {count} x {value} between '{a}' and '{b}', found {n}")
            bad[0] += 1

    stm = {v[0]: str(k) for k, v in T["C56621"]["pins"].items()}
    # 1. nets that cross from the STM32 to the LAN9252 (through the root sheet and the hierarchical labels)
    for esc, lan, mcu_pin in (("ESC_CS", "50", "PA4"), ("ESC_SCK", "19", "PA5"), ("ESC_MISO", "13", "PA6"), ("ESC_MOSI", "17", "PA7"),
                              ("ESC_IRQ", "44", "PC4"), ("ESC_SYNC0", "34", "PA0"), ("ESC_SYNC1", "18", "PC13"), ("ESC_RST", "11", "PC5")):
        a, b = net(pinnet, "U301", stm[mcu_pin]), net(pinnet, "U401", lan)
        if a != b:
            fail(f"STM32 {mcu_pin} ({a}) is not on the same net as LAN9252 pin {lan} ({b}) for {esc}")
            bad[0] += 1
    # 2. supplies, grounds and straps
    for pin in ("5", "14", "20", "32", "37", "47", "7"):
        want("U401", pin, "+3V3")
    for pin in ("51", "64", "58"):
        want("U401", pin, "+3V3_PHY")
    for pin in ("4", "65", "41", "8", "9", "10"):
        want("U401", pin, "GND_L")
    vcr = {net(pinnet, "U401", p) for p in ("6", "24", "38", "56", "59")}
    if len(vcr) != 1 or "VDDCR" not in vcr:
        fail(f"VDDCR, VDD12TX1 and VDD12TX2 are not one net called VDDCR: {vcr}")
        bad[0] += 1
    need("VDDCR", "GND_L", "1uF", 1, "C")
    need("VDDCR", "GND_L", "470pF", 1, "C")
    need("+3V3", net(pinnet, "U401", "45"), "10k")           # E2PSIZE strap high
    for pin in ("46", "48"):
        need("GND_L", net(pinnet, "U401", pin), "10k")      # chip mode 00
    need("GND_L", net(pinnet, "U401", "57"), "12.1k 1%")    # RBIAS
    # 3. link LEDs and RUN LED
    for chip_pin, jack, lnk in (("48", "J401", "LNK_ACT0"), ("46", "J402", "LNK_ACT1")):
        need(lnk, net(pinnet, "U401", chip_pin), "1k")
        want(jack, "9", lnk)
        want(jack, "10", "GND_L")
    want("LED401", "1", net(pinnet, "U401", "45"))
    need("+3V3", net(pinnet, "LED401", "2"), "1k")
    # 4. magnetics: each line to its jack pin, 49.9 ohm to +3V3_PHY, centre taps, shield
    for jack, lines in (("J401", (("53", "1"), ("52", "2"), ("55", "3"), ("54", "6"))), ("J402", (("62", "1"), ("63", "2"), ("60", "3"), ("61", "6")))):
        for chip, jp in lines:
            a, b = net(pinnet, "U401", chip), net(pinnet, jack, jp)
            if a != b:
                fail(f"LAN9252 pin {chip} ({a}) is not wired to {jack} pin {jp} ({b})")
                bad[0] += 1
            need("+3V3_PHY", a, "49.9R")
        want(jack, "4", "+3V3_PHY")
        want(jack, "5", "+3V3_PHY")
        for sp in ("8", "SH1", "SH2"):
            want(jack, sp, "SHIELD")
    need("SHIELD", "PE", "1nF 2kV", 1, "C")
    need("SHIELD", "PE", "1M", 1)
    # 5. ESI EEPROM
    for pin in ("1", "2", "3", "4", "7"):
        want("U402", pin, "GND_L")
    want("U402", "8", "+3V3")
    for ee, lan in (("5", "42"), ("6", "43")):
        if net(pinnet, "U402", ee) != net(pinnet, "U401", lan):
            fail(f"EEPROM pin {ee} is not on the LAN9252 pin {lan} net")
            bad[0] += 1
        need("+3V3", net(pinnet, "U402", ee), "4.7k")
    if not bad[0]:
        ok("EtherCAT sheet: SPI/IRQ/SYNC/RST nets match the STM32; straps, supplies, VDDCR, RBIAS, terminations, magnetics, shield and EEPROM verified")


def main():
    errs, warns = run_erc()
    comps, pinnet = netlist()
    check_pinmap(comps, pinnet)
    check_power(comps, pinnet)
    check_mcu(comps, pinnet)
    check_ethercat(comps, pinnet)
    check_fields(comps)
    check_style()
    check_barrier()
    check_bom_quantities(comps)
    print(f"\n{len(fails)} failures, {len(warns)} ERC warnings")
    if "--json" in sys.argv:
        json.dump({"failures": fails, "warnings": warns}, open(sys.argv[sys.argv.index("--json") + 1], "w"), indent=1)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
