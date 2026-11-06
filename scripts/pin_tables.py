"""Expected pin tables, taken from the manufacturers' datasheets.

Keyed by LCSC number. Each entry: source (datasheet and table/figure) and
`pins` mapping pin number -> list of accepted names (any one must match a
'/'-separated piece of the symbol pin name, ignoring case, '~{}' and punctuation),
plus optional `footprint_pads` (expected pad numbers) and `notes`.

Verified by scripts/pincheck.py; results are written to docs/review/M2-pin-check.md.
"""


def nums(prefix, rng):
    return {i: [f"{prefix}{i}"] for i in rng}


# LAN9252I/PT 64-TQFP-EP, generated from datasheet DS00001909A Table 3-2
LAN9252 = {1: ['OSCI'],
 2: ['OSCO'],
 3: ['OSCVDD12'],
 4: ['OSCVSS'],
 5: ['VDD33'],
 6: ['VDDCR'],
 7: ['REG_EN'],
 8: ['FXLOSEN'],
 9: ['FXLOSA', 'FXSDA', 'FXSDENA'],
 10: ['FXLOSB', 'FXSDB', 'FXSDENB'],
 11: ['RST#'],
 12: ['AD2', 'D2', 'SIO2', 'SOF'],
 13: ['AD1', 'D1', 'EOF', 'SIO1', 'SO'],
 14: ['VDDIO'],
 15: ['AD14', 'D14', 'DIGIO8', 'GPI8', 'GPO8', 'MII_TXD3', 'TX_SHIFT1'],
 16: ['AD13', 'D13', 'DIGIO7', 'GPI7', 'GPO7', 'MII_TXD2', 'TX_SHIFT0'],
 17: ['AD0', 'D0', 'SI', 'SIO0', 'WD_STATE'],
 18: ['LATCH1', 'SYNC1'],
 19: ['AD9', 'D9', 'LATCH_IN', 'SCK'],
 20: ['VDDIO'],
 21: ['AD12', 'D12', 'DIGIO6', 'GPI6', 'GPO6', 'MII_TXD1'],
 22: ['AD11', 'D11', 'DIGIO5', 'GPI5', 'GPO5', 'MII_TXD0'],
 23: ['AD10', 'D10', 'DIGIO4', 'GPI4', 'GPO4', 'MII_TXEN'],
 24: ['VDDCR'],
 25: ['A1', 'ALELO', 'MII_CLK25', 'OE_EXT'],
 26: ['A3', 'DIGIO11', 'GPI11', 'GPO11', 'MII_RXDV'],
 27: ['A4', 'DIGIO12', 'GPI12', 'GPO12', 'MII_RXD0'],
 28: ['CS', 'DIGIO13', 'GPI13', 'GPO13', 'MII_RXD1'],
 29: ['A2', 'ALEHI', 'DIGIO10', 'GPI10', 'GPO10', 'LINKACTLED2', 'MII_LINKPOL'],
 30: ['DIGIO14', 'ENB', 'GPI14', 'GPO14', 'MII_RXD2', 'WR'],
 31: ['DIGIO15', 'GPI15', 'GPO15', 'MII_RXD3', 'RD', 'RD_WR'],
 32: ['VDDIO'],
 33: ['A0', 'AD15', 'D15', 'DIGIO9', 'GPI9', 'GPO9', 'MII_RXER'],
 34: ['LATCH0', 'SYNC0'],
 35: ['AD3', 'D3', 'SIO3', 'WD_TRIG'],
 36: ['AD6', 'D6', 'DIGIO0', 'GPI0', 'GPO0', 'MII_RXCLK'],
 37: ['VDDIO'],
 38: ['VDDCR'],
 39: ['AD7', 'D7', 'DIGIO1', 'GPI1', 'GPO1', 'MII_MDC'],
 40: ['AD8', 'D8', 'DIGIO2', 'GPI2', 'GPO2', 'MII_MDIO'],
 41: ['TESTMODE'],
 42: ['EESDA', 'TMS'],
 43: ['EESCL', 'TCK'],
 44: ['IRQ'],
 45: ['E2PSIZE', 'RUNLED'],
 46: ['CHIP_MODE1', 'LINKACTLED1', 'TDI'],
 47: ['VDDIO'],
 48: ['CHIP_MODE0', 'LINKACTLED0', 'TDO'],
 49: ['AD4', 'D4', 'DIGIO3', 'GPI3', 'GPO3', 'MII_LINK'],
 50: ['AD5', 'D5', 'OUTVALID', 'SCS#'],
 51: ['VDD33TXRX1'],
 52: ['TXNA'],
 53: ['TXPA'],
 54: ['RXNA'],
 55: ['RXPA'],
 56: ['VDD12TX1'],
 57: ['RBIAS'],
 58: ['VDD33BIAS'],
 59: ['VDD12TX2'],
 60: ['RXPB'],
 61: ['RXNB'],
 62: ['TXPB'],
 63: ['TXNB'],
 64: ['VDD33TXRX2'],
 65: ['VSS']}


def stm32_lqfp100():
    names = {
        1: "PE2", 2: "PE3", 3: "PE4", 4: "PE5", 5: "PE6", 6: "VBAT", 7: "PC13", 8: "PC14",
        9: "PC15", 10: "VSS", 11: "VDD", 12: "PH0", 13: "PH1", 14: "NRST", 15: "PC0", 16: "PC1",
        17: "PC2", 18: "PC3", 19: "VDD", 20: "VSSA", 21: "VREF+", 22: "VDDA", 23: "PA0", 24: "PA1",
        25: "PA2", 26: "PA3", 27: "VSS", 28: "VDD", 29: "PA4", 30: "PA5", 31: "PA6", 32: "PA7",
        33: "PC4", 34: "PC5", 35: "PB0", 36: "PB1", 37: "PB2", 38: "PE7", 39: "PE8", 40: "PE9",
        41: "PE10", 42: "PE11", 43: "PE12", 44: "PE13", 45: "PE14", 46: "PE15", 47: "PB10",
        48: "PB11", 49: "VCAP_1", 50: "VDD", 51: "PB12", 52: "PB13", 53: "PB14", 54: "PB15",
        55: "PD8", 56: "PD9", 57: "PD10", 58: "PD11", 59: "PD12", 60: "PD13", 61: "PD14",
        62: "PD15", 63: "PC6", 64: "PC7", 65: "PC8", 66: "PC9", 67: "PA8", 68: "PA9", 69: "PA10",
        70: "PA11", 71: "PA12", 72: "PA13", 73: "VCAP_2", 74: "VSS", 75: "VDD", 76: "PA14",
        77: "PA15", 78: "PC10", 79: "PC11", 80: "PC12", 81: "PD0", 82: "PD1", 83: "PD2", 84: "PD3",
        85: "PD4", 86: "PD5", 87: "PD6", 88: "PD7", 89: "PB3", 90: "PB4", 91: "PB5", 92: "PB6",
        93: "PB7", 94: "BOOT0", 95: "PB8", 96: "PB9", 97: "PE0", 98: "PE1", 99: "VSS", 100: "VDD",
    }
    return {k: [v] for k, v in names.items()}


T = {}

T["C56621"] = dict(
    part="STM32F405VGT6 (LQFP-100)",
    source="DocID022152 Rev 4 Table 7 'pin and ball definitions', LQFP100 column (pins whose names wrap over two lines read from the next line: PC14, PH0, PH1, PA0, PB2, PA13, PA14, PA15, PB3, PB4) cross-checked with Fig. 13 'LQFP100 pinout'",
    match="token",
    pins=stm32_lqfp100(),
)
T["C80933"] = dict(
    part="LAN9252I/PT (64-TQFP-EP)",
    source="DS00001909A Table 3-2 '64-TQFP-EP package pin assignments' (all five mode columns); pin 65 = exposed pad VSS. "
           "The M4 symbol shows only the SPI-mode function of each pin (a subset of the datasheet names)",
    match="token",
    pins=LAN9252,
)
T["C2595919"] = dict(
    part="ECS-3225MVQ-250-CN-TR (3.2x2.5 mm, 4-pin)",
    source="ECS-3225MVQ datasheet pin table: 1 tri-state (OE, NC = active), 2 GND, 3 output, 4 VDD",
    match="token",
    pins={1: ["TRISTATE", "OE", "ST"], 2: ["GND"], 3: ["OUTPUT"], 4: ["VDD"]},
)
T["C615715"] = dict(
    part="24LC32AT-I/SN (SOIC-8)",
    source="24LC32A datasheet, 8-pin SOIC pinout",
    match="token",
    pins={1: ["A0"], 2: ["A1"], 3: ["A2"], 4: ["VSS"], 5: ["SDA"], 6: ["SCL"], 7: ["WP"], 8: ["VCC"]},
)
T["C16040"] = dict(
    part="MCP4822-E/SN (SOIC-8)",
    source="MCP48X2 datasheet, 8-pin SOIC pinout (MCP4822 column)",
    match="token",
    pins={1: ["VDD"], 2: ["CS"], 3: ["SCK"], 4: ["SDI"], 5: ["LDAC"], 6: ["VOUTB"], 7: ["VSS"], 8: ["VOUTA"]},
)
T["C7934"] = dict(
    part="LM2904DR (SOIC-8)",
    source="LM2904 datasheet, 8-pin SOIC pinout",
    match="token",
    pins={1: ["1OUT"], 2: ["1IN"], 3: ["1IN"], 4: ["GND"], 5: ["2IN"], 6: ["2IN"], 7: ["2OUT"], 8: ["VCC"]},
    polarity={2: "-", 3: "+", 5: "+", 6: "-"},
)
T["C42738"] = dict(
    part="L78L05ABUTR (SOT-89-3)",
    source="L78L datasheet Fig. 2: pin 1 VOUT, pin 2 GND, pin 3 VIN (SOT-89)",
    match="token",
    pins={1: ["VOUT"], 2: ["GND"], 3: ["VIN"]},
)
T["C83571"] = dict(
    part="2N7002DW-7-F (SOT-363)",
    source="DS30120 Rev 22-2 p.1 top view and internal schematic: pins 1,2,4,5 and 3,6 grouped as FET A (S, G, D) = pins 1,2,6 and FET B = pins 4,5,3",
    match="token",
    pins={1: ["S2"], 2: ["G2"], 3: ["D1"], 4: ["S1"], 5: ["G1"], 6: ["D2"]},
    notes="Q1/Q2 labelling differs between manufacturers; the grouping (1,2,6) and (4,5,3) is what matters and is identical.",
)
T["C6180"] = dict(
    part="AM26LS32ACDR (SOIC-16)",
    source="SLLS115E logic diagram: 1B=1, 1A=2, 1Y=3, G=4, 2Y=5, 2A=6, 2B=7, GND=8, 3B=9, 3A=10, 3Y=11, /G=12, 4Y=13, 4A=14, 4B=15, VCC=16",
    match="token",
    pins={1: ["1B"], 2: ["1A"], 3: ["1Y"], 4: ["G"], 5: ["2Y"], 6: ["2A"], 7: ["2B"], 8: ["GND"],
          9: ["3B"], 10: ["3A"], 11: ["3Y"], 12: ["G"], 13: ["4Y"], 14: ["4A"], 15: ["4B"], 16: ["VCC"]},
)
_CAIS_COMMON = {1: ["VDDA"], 2: ["GNDA"], 8: ["GNDA"], 9: ["GNDB"], 13: ["VO2"], 14: ["VO1"], 15: ["GNDB"], 16: ["VDDB"]}
T["C428888"] = dict(
    part="CA-IS3740LN (SOIC-16, 4 forward)",
    source="CA-IS374x datasheet v1.05 Table 6-1 and Fig. 6-1 (CA-IS3740 column)",
    match="token",
    pins={**_CAIS_COMMON, 3: ["VI1"], 4: ["VI2"], 5: ["VI3"], 6: ["VI4"], 7: ["NC"], 10: ["ENB"], 11: ["VO4"], 12: ["VO3"]},
)
T["C528653"] = dict(
    part="CA-IS3740HW (SOIC-16 wide-body, 4 forward)",
    source="CA-IS374x datasheet v1.05 Table 6-1 (same pinout as CA-IS3740LN)",
    match="token",
    pins={**_CAIS_COMMON, 3: ["VI1"], 4: ["VI2"], 5: ["VI3"], 6: ["VI4"], 7: ["NC"], 10: ["ENB"], 11: ["VO4"], 12: ["VO3"]},
)
T["C5347249"] = dict(
    part="CA-IS3742LN (SOIC-16, 2 forward + 2 reverse)",
    source="CA-IS374x datasheet v1.05 Table 6-1 (CA-IS3742 column): VO3, VO4 on side A; VI3, VI4 on side B",
    match="token",
    pins={**_CAIS_COMMON, 3: ["VI1"], 4: ["VI2"], 5: ["VO3"], 6: ["VO4"], 7: ["ENA"], 10: ["ENB"], 11: ["VI4"], 12: ["VI3"]},
)
T["C845537"] = dict(
    part="ULN2803A UMW (SOP-18)",
    source="UMW ULN2803 datasheet 'Pin descriptions (DIP/SOP-18)': inputs 1-8, outputs 18-11 (ch1 = pin 18), GND 9, COM 10",
    match="token",
    pins={**{i: ["INPUT"] for i in range(1, 9)}, 9: ["GND"], 10: ["COM"], **{i: ["OUTPUT"] for i in range(11, 19)}},
)
T["C39031"] = dict(
    part="TLP290-4 (SOP-16)",
    source="TLP290-4 datasheet rev 5.0 section 4 figure: ch1 LED 1-2 / C16 E15, ch2 3-4 / C14 E13, ch3 5-6 / C12 E11, ch4 7-8 / C10 E9",
    match="token",
    pins={1: ["IN1A"], 2: ["IN1B"], 3: ["IN2A"], 4: ["IN2B"], 5: ["IN3A"], 6: ["IN3B"], 7: ["IN4A"], 8: ["IN4B"],
          9: ["E4"], 10: ["C4"], 11: ["E3"], 12: ["C3"], 13: ["E2"], 14: ["C2"], 15: ["E1"], 16: ["C1"]},
    renamed=True,
)
T["C1524860"] = dict(
    part="Omron P2R-05P socket (for G2R-1-S)",
    source="Omron G2RS datasheet p.5 'G2R-1-S terminal arrangement' (coil 1-5, COM 2, NO 3, NC 4: contact arm rests on 4) and p.8 P2R-05P bottom view",
    match="token",
    pins={1: ["COIL1"], 2: ["COM"], 3: ["NO"], 4: ["NC"], 5: ["COIL2"]},
    renamed=True,
)
_URB = {1: ["GND"], 2: ["VIN"], 3: ["CTRL"], 5: ["NC"], 6: ["VO"], 7: ["VO"], 8: ["NC"]}
for _c, _n in (("C5369843", "URB2403S-6WR3"), ("C3031185", "URB2405S-6WR3"), ("C5369844", "URB2415S-6WR3")):
    T[_c] = dict(
        part=f"{_n} (SIP-8, pin 4 absent)",
        source="URB_S-6WR3 datasheet p.5 Pin-Out: 1 GND (input), 2 Vin, 3 Ctrl, 5 NC, 6 +Vo, 7 0V (output), 8 NC",
        match="token",
        pins=_URB,
        polarity={6: "+", 7: "-"},
    )
T["C69427"] = dict(
    part="HY911105AE RJ45 with magnetics and LEDs",
    source="Hanrun HY911105AE datasheet p.1 schematic: P1 TD+, P2 TD-, P3 RD+, P4 TX centre tap, P5 RX centre tap, P6 RD-, P7 NC, P8 chassis, green LED 9(A)-10(K), yellow LED 12(A)-11(K)",
    match="token",
    pins={1: ["TD+", "TD"], 2: ["TD-", "TD"], 3: ["RD+", "RD"], 4: ["TDCT"], 5: ["RDCT"], 6: ["RD-", "RD"], 7: ["NC"], 8: ["CHSGND"],
          9: ["LEDGA"], 10: ["LEDGK"], 11: ["LEDYK"], 12: ["LEDYA"], "SH1": ["SH1"], "SH2": ["SH2"]},
    polarity={1: "+", 2: "-", 3: "+", 6: "-"},
    renamed=True,
)
T["C32677"] = dict(
    part="PSM712-LF-T7 (SOT-23)",
    source="ProTek PSM712 datasheet: pins 1 and 2 protected lines, pin 3 common (cathode); +12 V / -7 V stand-off referred to pin 3",
    match="token",
    pins={1: ["IO1"], 2: ["IO2"], 3: ["COM"]},
    renamed=True,
)
T["C320242"] = dict(
    part="SMBJ33A (SMB)",
    source="Footprint silkscreen band is at pad 1 (left, x<0): pad 1 = cathode, pad 2 = anode (unidirectional TVS)",
    match="token",
    pins={1: ["K"], 2: ["A"]},
    renamed=True,
)
T["C83851"] = dict(
    part="SMBJ30A (SMB)",
    source="Footprint silkscreen: cathode bar and band at pad 1 (left, x<0): pad 1 = cathode, pad 2 = anode (unidirectional TVS)",
    match="token",
    pins={1: ["K"], 2: ["A"]},
    renamed=True,
)
T["C148216"] = dict(
    part="SMAJ15A (SMA)",
    source="Footprint silkscreen band is at pad 1: pad 1 = cathode, pad 2 = anode",
    match="token",
    pins={1: ["C"], 2: ["A"]},
)
T["C22452"] = dict(
    part="SS54 (SMA)",
    source="Footprint silkscreen band is at pad 2 (x<0, pad 2): pad 2 = cathode, pad 1 = anode",
    match="token",
    pins={1: ["A"], 2: ["K"]},
)
for _c, _n in (("C970679", "47 uF 50 V SMD electrolytic"), ("C2960285", "100 uF 100 V radial electrolytic")):
    T[_c] = dict(
        part=_n,
        source="Footprint silkscreen: '+' mark and chamfer at pad 1: pad 1 = positive, pad 2 = negative",
        match="token",
        pins={1: ["+"], 2: ["-"]},
        renamed=True,
    )


# ---------------------------------------------------------------------------
# Footprint geometry from the printed dimensions on each datasheet drawing.
# geometry: (pad A, pad B, |dx| mm, |dy| mm); None = not given on the drawing.
# bbox: (width, height) of the bounding box of all pad centres.
# Pads without a number are called np1, np2, ... in file order.
# ---------------------------------------------------------------------------
T["C206887"] = dict(
    part="Littelfuse 646 fuse block 64600001003 (5x20 mm)",
    source="Littelfuse 646 series datasheet rev 08/07/17, 'Recommended Hole Pattern': 22.6 mm (+0.3/-0.1) between solder-pin holes, hole 1.5 mm",
    match="token",
    pins={1: ["1"], 2: ["2"]},
    geometry=[("1", "2", 22.6, 0.0)],
)
T["C5272782"] = dict(
    part="Keystone 7770 PE terminal (M3, vertical)",
    source="Keystone 7770 drawing: four 1.52 mm square pins, .197 in (5.00 mm) x .276 in (7.01 mm), holes 1.85 mm; one electrical terminal",
    match="token",
    pins={1: ["PE"]},
    bbox=(5.00, 7.01),
)
for _c in ("C5369843", "C3031185", "C5369844"):
    T[_c]["geometry"] = [("1", "2", 2.54, 0.0), ("1", "3", 5.08, 0.0), ("1", "5", 10.16, 0.0),
                         ("1", "6", 12.70, 0.0), ("1", "7", 15.24, 0.0), ("1", "8", 17.78, 0.0)]
T["C1524860"]["geometry"] = [("3", "4", 4.0, 6.0), ("4", "2", 4.0, 4.5), ("4", "1", None, 15.0), ("1", "5", 7.0, 4.0)]
T["C1524860"]["source"] += "; pad distances from the 'Mounting Holes' drawing (6, 4.5, 15, 4, 4, 7 mm)"
T["C69427"]["geometry"] = [("9", "12", 13.25, None), ("9", "10", 2.54, None), ("11", "12", 2.54, None),
                           ("SH1", "SH2", 15.49, None), ("1", "3", 2.54, None), ("2", "1", None, 2.54),
                           ("np1", "np2", 11.43, None), ("9", "np1", None, 4.90), ("np1", "2", None, 8.89)]
T["C69427"]["source"] += "; pad distances from the 'Mounting Pattern' drawing (13.25, 11.43, 15.49, 4.90, 8.89, 2.54 mm)"
for _c, _n in (("C441204", 2), ("C441205", 3), ("C441206", 4), ("C441208", 6)):
    T[_c] = dict(
        part=f"KF2EDGR-5.08-{_n}P header",
        source="5.08 mm pitch pluggable terminal (manufacturer pitch); pin n = position n",
        match="token",
        pins={i: [str(i)] for i in range(1, _n + 1)},
        geometry=[("1", "2", 5.08, 0.0)],
    )
T["C2937625"] = dict(
    part="PZ254V-11-03P 1x3 pin header",
    source="2.54 mm pitch pin header, pin n = position n",
    match="token",
    pins={1: ["1"], 2: ["2"], 3: ["3"]},
    geometry=[("1", "2", 2.54, 0.0)],
)
