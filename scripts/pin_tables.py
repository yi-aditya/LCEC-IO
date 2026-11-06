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


def stm32_lqfp64():
    names = {
        1: "VBAT", 2: "PC13", 3: "PC14", 4: "PC15", 5: "PH0", 6: "PH1", 7: "NRST",
        8: "PC0", 9: "PC1", 10: "PC2", 11: "PC3", 12: "VSSA", 13: "VDDA", 14: "PA0",
        15: "PA1", 16: "PA2", 17: "PA3", 18: "VSS", 19: "VDD", 20: "PA4", 21: "PA5",
        22: "PA6", 23: "PA7", 24: "PC4", 25: "PC5", 26: "PB0", 27: "PB1", 28: "PB2",
        29: "PB10", 30: "PB11", 31: "VCAP_1", 32: "VDD", 33: "PB12", 34: "PB13",
        35: "PB14", 36: "PB15", 37: "PC6", 38: "PC7", 39: "PC8", 40: "PC9", 41: "PA8",
        42: "PA9", 43: "PA10", 44: "PA11", 45: "PA12", 46: "PA13", 47: "VCAP_2",
        48: "VDD", 49: "PA14", 50: "PA15", 51: "PC10", 52: "PC11", 53: "PC12",
        54: "PD2", 55: "PB3", 56: "PB4", 57: "PB5", 58: "PB6", 59: "PB7", 60: "BOOT0",
        61: "PB8", 62: "PB9", 63: "VSS", 64: "VDD",
    }
    return {k: [v] for k, v in names.items()}


T = {}

T["C15742"] = dict(
    part="STM32F405RGT6 (LQFP-64)",
    source="DocID022152 Rev 4: Fig. 12 'LQFP64 pinout' (pins 1-16, 33-48 read from the figure; the rest from Table 7 LQFP64 column, PB3/JTDO row 55)",
    match="token",
    pins=stm32_lqfp64(),
)
T["C80933"] = dict(
    part="LAN9252I/PT (64-TQFP-EP)",
    source="DS00001909A Table 3-2 '64-TQFP-EP package pin assignments' (all five mode columns); pin 65 = exposed pad VSS",
    match="set",
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
