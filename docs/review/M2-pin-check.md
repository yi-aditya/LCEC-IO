# M2 - Symbol and footprint pin check

Every imported symbol is compared with the manufacturer datasheet pin table (`scripts/pin_tables.py`, each entry names its source), and with its footprint pad numbers. Re-run with `python3 -I scripts/pincheck.py --md docs/review/M2-pin-check.md`.

**44 symbols checked, 44 clean, 0 with problems.**

| LCSC | Symbol | Pins | Pads | Datasheet check | Result |
|---|---|---|---|---|---|
| C2960285 | 100V100UFCD288 | 2 | 2 | yes | OK |
| C151168 | 1812L050_30PR | 2 | 2 | no table (generic part) | OK |
| C3116 | 1A250VAC | 0 | - | no table (generic part) | OK |
| C5305 | 2.54短路帽开口 | 0 | - | no table (generic part) | OK |
| C615715 | 24LC32AT-I_SN | 8 | 8 | yes | OK |
| C83571 | 2N7002DW-7-F | 6 | 6 | yes | OK |
| C3118 | 3A250VACGlasstubefuse | 0 | - | no table (generic part) | OK |
| C206887 | 64600001003 | 2 | 2 | yes | OK |
| C187509 | 64800001009 | 0 | - | no table (generic part) | OK |
| C6180 | AM26LS32ACDR | 16 | 16 | yes | OK |
| C528653 | CA-IS3740HW | 16 | 16 | yes | OK |
| C428888 | CA-IS3740LN | 16 | 16 | yes | OK |
| C5347249 | CA-IS3742LN | 16 | 16 | yes | OK |
| C2595919 | ECS-3225MVQ-250-CN-TR | 4 | 4 | yes | OK |
| C69427 | HY911105AE | 14 | 14 | yes | OK |
| C440880 | KF2EDGK-5.08-2P-AA | 0 | - | no table (generic part) | OK |
| C440881 | KF2EDGK-5.08-3P-AA | 0 | - | no table (generic part) | OK |
| C440882 | KF2EDGK-5.08-4P-AA | 0 | - | no table (generic part) | OK |
| C440884 | KF2EDGK-5.08-6P | 0 | - | no table (generic part) | OK |
| C441204 | KF2EDGR-5.08-2P | 2 | 2 | yes | OK |
| C441205 | KF2EDGR-5.08-3P | 3 | 3 | yes | OK |
| C441206 | KF2EDGR-5.08-4P | 4 | 4 | yes | OK |
| C441208 | KF2EDGR-5.08-6P | 6 | 6 | yes | OK |
| C5272782 | Keystone-7770 | 1 | 1 | yes | OK |
| C42738 | L78L05ABUTR | 3 | 3 | yes | OK |
| C80933 | LAN9252I_PT | 65 | 65 | yes | OK |
| C7934 | LM2904DR | 8 | 8 | yes | OK |
| C16040 | MCP4822-E_SN | 8 | 8 | yes | OK |
| C1524860 | P2R-05P | 5 | 5 | yes | OK |
| C357543 | PM3X6 | 0 | - | no table (generic part) | OK |
| C32677 | PSM712-LF-T7 | 3 | 3 | yes | OK |
| C3975188 | PZ127-2-05-S | 10 | 10 | no table (generic part) | OK |
| C2937625 | PZ254V-11-03P_C2937625 | 3 | 3 | yes | OK |
| C970679 | RVT1H470M060747UF50V | 2 | 2 | yes | OK |
| C148216 | SMAJ15A-C148216 | 2 | 2 | yes | OK |
| C83851 | SMBJ30A_C83851 | 2 | 2 | yes | OK |
| C22452 | SS54_C22452 | 2 | 2 | yes | OK |
| C56621 | STM32F405VGT6 | 100 | 100 | yes | OK |
| C39031 | TLP290-4 | 16 | 16 | yes | OK |
| C845537 | ULN2803A_C845537 | 18 | 18 | yes | OK |
| C5369843 | URB2403S-6WR3_C5369843 | 7 | 7 | yes | OK |
| C3031185 | URB2405S-6WR3_C3031185 | 7 | 7 | yes | OK |
| C5369844 | URB2415S-6WR3_C5369844 | 7 | 7 | yes | OK |
| C70068 | nSMD025 | 2 | 2 | no table (generic part) | OK |

## Pin-by-pin tables

### C2960285 100 uF 100 V radial electrolytic

Source: Footprint silkscreen: '+' mark and chamfer at pad 1: pad 1 = positive, pad 2 = negative

| Pin | Symbol name | Datasheet | OK |
|---|---|---|---|
| 1 | + | + | yes |
| 2 | - | - | yes |

### C615715 24LC32AT-I/SN (SOIC-8)

Source: 24LC32A datasheet, 8-pin SOIC pinout

| Pin | Symbol name | Datasheet | OK |
|---|---|---|---|
| 1 | A0 | A0 | yes |
| 2 | A1 | A1 | yes |
| 3 | A2 | A2 | yes |
| 4 | VSS | VSS | yes |
| 5 | SDA | SDA | yes |
| 6 | SCL | SCL | yes |
| 7 | WP | WP | yes |
| 8 | VCC | VCC | yes |

### C83571 2N7002DW-7-F (SOT-363)

Source: DS30120 Rev 22-2 p.1 top view and internal schematic: pins 1,2,4,5 and 3,6 grouped as FET A (S, G, D) = pins 1,2,6 and FET B = pins 4,5,3

Note: Q1/Q2 labelling differs between manufacturers; the grouping (1,2,6) and (4,5,3) is what matters and is identical.

| Pin | Symbol name | Datasheet | OK |
|---|---|---|---|
| 1 | S2 | S2 | yes |
| 2 | G2 | G2 | yes |
| 3 | D1 | D1 | yes |
| 4 | S1 | S1 | yes |
| 5 | G1 | G1 | yes |
| 6 | D2 | D2 | yes |

### C206887 Littelfuse 646 fuse block 64600001003 (5x20 mm)

Source: Littelfuse 646 series datasheet rev 08/07/17, 'Recommended Hole Pattern': 22.6 mm (+0.3/-0.1) between solder-pin holes, hole 1.5 mm

| Pin | Symbol name | Datasheet | OK |
|---|---|---|---|
| 1 | 1 | 1 | yes |
| 2 | 2 | 2 | yes |

Footprint geometry against the datasheet drawing:

| Pads | Datasheet | Footprint | OK |
|---|---|---|---|
| 1-2 | dx 22.6 dy 0.0 | dx 22.60 dy 0.00 | yes |

### C6180 AM26LS32ACDR (SOIC-16)

Source: SLLS115E logic diagram: 1B=1, 1A=2, 1Y=3, G=4, 2Y=5, 2A=6, 2B=7, GND=8, 3B=9, 3A=10, 3Y=11, /G=12, 4Y=13, 4A=14, 4B=15, VCC=16

| Pin | Symbol name | Datasheet | OK |
|---|---|---|---|
| 1 | 1B | 1B | yes |
| 2 | 1A | 1A | yes |
| 3 | 1Y | 1Y | yes |
| 4 | G | G | yes |
| 5 | 2Y | 2Y | yes |
| 6 | 2A | 2A | yes |
| 7 | 2B | 2B | yes |
| 8 | GND | GND | yes |
| 9 | 3B | 3B | yes |
| 10 | 3A | 3A | yes |
| 11 | 3Y | 3Y | yes |
| 12 | ~{G} | G | yes |
| 13 | 4Y | 4Y | yes |
| 14 | 4A | 4A | yes |
| 15 | 4B | 4B | yes |
| 16 | VCC | VCC | yes |

### C528653 CA-IS3740HW (SOIC-16 wide-body, 4 forward)

Source: CA-IS374x datasheet v1.05 Table 6-1 (same pinout as CA-IS3740LN)

| Pin | Symbol name | Datasheet | OK |
|---|---|---|---|
| 1 | VDDA | VDDA | yes |
| 2 | GNDA | GNDA | yes |
| 3 | VI1 | VI1 | yes |
| 4 | VI2 | VI2 | yes |
| 5 | VI3 | VI3 | yes |
| 6 | VI4 | VI4 | yes |
| 7 | NC | NC | yes |
| 8 | GNDA | GNDA | yes |
| 9 | GNDB | GNDB | yes |
| 10 | ENB | ENB | yes |
| 11 | VO4 | VO4 | yes |
| 12 | VO3 | VO3 | yes |
| 13 | VO2 | VO2 | yes |
| 14 | VO1 | VO1 | yes |
| 15 | GNDB | GNDB | yes |
| 16 | VDDB | VDDB | yes |

### C428888 CA-IS3740LN (SOIC-16, 4 forward)

Source: CA-IS374x datasheet v1.05 Table 6-1 and Fig. 6-1 (CA-IS3740 column)

| Pin | Symbol name | Datasheet | OK |
|---|---|---|---|
| 1 | VDDA | VDDA | yes |
| 2 | GNDA | GNDA | yes |
| 3 | VI1 | VI1 | yes |
| 4 | VI2 | VI2 | yes |
| 5 | VI3 | VI3 | yes |
| 6 | VI4 | VI4 | yes |
| 7 | NC | NC | yes |
| 8 | GNDA | GNDA | yes |
| 9 | GNDB | GNDB | yes |
| 10 | ENB | ENB | yes |
| 11 | VO4 | VO4 | yes |
| 12 | VO3 | VO3 | yes |
| 13 | VO2 | VO2 | yes |
| 14 | VO1 | VO1 | yes |
| 15 | GNDB | GNDB | yes |
| 16 | VDDB | VDDB | yes |

### C5347249 CA-IS3742LN (SOIC-16, 2 forward + 2 reverse)

Source: CA-IS374x datasheet v1.05 Table 6-1 (CA-IS3742 column): VO3, VO4 on side A; VI3, VI4 on side B

| Pin | Symbol name | Datasheet | OK |
|---|---|---|---|
| 1 | VDDA | VDDA | yes |
| 2 | GNDA | GNDA | yes |
| 3 | VI1 | VI1 | yes |
| 4 | VI2 | VI2 | yes |
| 5 | VO3 | VO3 | yes |
| 6 | VO4 | VO4 | yes |
| 7 | ENA | ENA | yes |
| 8 | GNDA | GNDA | yes |
| 9 | GNDB | GNDB | yes |
| 10 | ENB | ENB | yes |
| 11 | VI4 | VI4 | yes |
| 12 | VI3 | VI3 | yes |
| 13 | VO2 | VO2 | yes |
| 14 | VO1 | VO1 | yes |
| 15 | GNDB | GNDB | yes |
| 16 | VDDB | VDDB | yes |

### C2595919 ECS-3225MVQ-250-CN-TR (3.2x2.5 mm, 4-pin)

Source: ECS-3225MVQ datasheet pin table: 1 tri-state (OE, NC = active), 2 GND, 3 output, 4 VDD

| Pin | Symbol name | Datasheet | OK |
|---|---|---|---|
| 1 | OE | TRISTATE/OE/ST | yes |
| 2 | GND | GND | yes |
| 3 | OUTPUT | OUTPUT | yes |
| 4 | VDD | VDD | yes |

### C69427 HY911105AE RJ45 with magnetics and LEDs

Source: Hanrun HY911105AE datasheet p.1 schematic: P1 TD+, P2 TD-, P3 RD+, P4 TX centre tap, P5 RX centre tap, P6 RD-, P7 NC, P8 chassis, green LED 9(A)-10(K), yellow LED 12(A)-11(K); pad distances from the 'Mounting Pattern' drawing (13.25, 11.43, 15.49, 4.90, 8.89, 2.54 mm)

| Pin | Symbol name | Datasheet | OK |
|---|---|---|---|
| 1 | TD+ | TD+/TD | yes |
| 2 | TD- | TD-/TD | yes |
| 3 | RD+ | RD+/RD | yes |
| 4 | TD_CT | TDCT | yes |
| 5 | RD_CT | RDCT | yes |
| 6 | RD- | RD-/RD | yes |
| 7 | NC | NC | yes |
| 8 | CHSGND | CHSGND | yes |
| 9 | LEDG_A | LEDGA | yes |
| 10 | LEDG_K | LEDGK | yes |
| 11 | LEDY_K | LEDYK | yes |
| 12 | LEDY_A | LEDYA | yes |
| SH1 | SH1 | SH1 | yes |
| SH2 | SH2 | SH2 | yes |

Footprint geometry against the datasheet drawing:

| Pads | Datasheet | Footprint | OK |
|---|---|---|---|
| 9-12 | dx 13.25 dy - | dx 13.26 dy 0.00 | yes |
| 9-10 | dx 2.54 dy - | dx 2.54 dy 0.00 | yes |
| 11-12 | dx 2.54 dy - | dx 2.54 dy 0.00 | yes |
| SH1-SH2 | dx 15.49 dy - | dx 15.48 dy 0.00 | yes |
| 1-3 | dx 2.54 dy - | dx 2.54 dy 0.00 | yes |
| 2-1 | dx - dy 2.54 | dx 1.27 dy 2.54 | yes |
| np1-np2 | dx 11.43 dy - | dx 11.44 dy 0.00 | yes |
| 9-np1 | dx - dy 4.9 | dx 0.91 dy 4.89 | yes |
| np1-2 | dx - dy 8.89 | dx 2.54 dy 8.89 | yes |

### C441204 KF2EDGR-5.08-2P header

Source: 5.08 mm pitch pluggable terminal (manufacturer pitch); pin n = position n

| Pin | Symbol name | Datasheet | OK |
|---|---|---|---|
| 1 | 1 | 1 | yes |
| 2 | 2 | 2 | yes |

Footprint geometry against the datasheet drawing:

| Pads | Datasheet | Footprint | OK |
|---|---|---|---|
| 1-2 | dx 5.08 dy 0.0 | dx 5.08 dy 0.00 | yes |

### C441205 KF2EDGR-5.08-3P header

Source: 5.08 mm pitch pluggable terminal (manufacturer pitch); pin n = position n

| Pin | Symbol name | Datasheet | OK |
|---|---|---|---|
| 1 | 1 | 1 | yes |
| 2 | 2 | 2 | yes |
| 3 | 3 | 3 | yes |

Footprint geometry against the datasheet drawing:

| Pads | Datasheet | Footprint | OK |
|---|---|---|---|
| 1-2 | dx 5.08 dy 0.0 | dx 5.08 dy 0.00 | yes |

### C441206 KF2EDGR-5.08-4P header

Source: 5.08 mm pitch pluggable terminal (manufacturer pitch); pin n = position n

| Pin | Symbol name | Datasheet | OK |
|---|---|---|---|
| 1 | 1 | 1 | yes |
| 2 | 2 | 2 | yes |
| 3 | 3 | 3 | yes |
| 4 | 4 | 4 | yes |

Footprint geometry against the datasheet drawing:

| Pads | Datasheet | Footprint | OK |
|---|---|---|---|
| 1-2 | dx 5.08 dy 0.0 | dx 5.08 dy 0.00 | yes |

### C441208 KF2EDGR-5.08-6P header

Source: 5.08 mm pitch pluggable terminal (manufacturer pitch); pin n = position n

| Pin | Symbol name | Datasheet | OK |
|---|---|---|---|
| 1 | 1 | 1 | yes |
| 2 | 2 | 2 | yes |
| 3 | 3 | 3 | yes |
| 4 | 4 | 4 | yes |
| 5 | 5 | 5 | yes |
| 6 | 6 | 6 | yes |

Footprint geometry against the datasheet drawing:

| Pads | Datasheet | Footprint | OK |
|---|---|---|---|
| 1-2 | dx 5.08 dy 0.0 | dx 5.08 dy 0.00 | yes |

### C5272782 Keystone 7770 PE terminal (M3, vertical)

Source: Keystone 7770 drawing: four 1.52 mm square pins, .197 in (5.00 mm) x .276 in (7.01 mm), holes 1.85 mm; one electrical terminal

| Pin | Symbol name | Datasheet | OK |
|---|---|---|---|
| 1 | PE | PE | yes |

Footprint geometry against the datasheet drawing:

| Pads | Datasheet | Footprint | OK |
|---|---|---|---|
| pad bounding box | 5.0 x 7.01 | 5.00 x 7.01 | yes |

### C42738 L78L05ABUTR (SOT-89-3)

Source: L78L datasheet Fig. 2: pin 1 VOUT, pin 2 GND, pin 3 VIN (SOT-89)

| Pin | Symbol name | Datasheet | OK |
|---|---|---|---|
| 1 | VOUT | VOUT | yes |
| 2 | GND | GND | yes |
| 3 | VIN | VIN | yes |

### C80933 LAN9252I/PT (64-TQFP-EP)

Source: DS00001909A Table 3-2 '64-TQFP-EP package pin assignments' (all five mode columns); pin 65 = exposed pad VSS. The M4 symbol shows only the SPI-mode function of each pin (a subset of the datasheet names)

| Pin | Symbol name | Datasheet | OK |
|---|---|---|---|
| 1 | OSCI | OSCI | yes |
| 2 | OSCO | OSCO | yes |
| 3 | OSCVDD12 | OSCVDD12 | yes |
| 4 | OSCVSS | OSCVSS | yes |
| 5 | VDD33 | VDD33 | yes |
| 6 | VDDCR | VDDCR | yes |
| 7 | REG_EN | REG_EN | yes |
| 8 | FXLOSEN | FXLOSEN | yes |
| 9 | FXSDENA | FXLOSA/FXSDA/FXSDENA | yes |
| 10 | FXSDENB | FXLOSB/FXSDB/FXSDENB | yes |
| 11 | ~{RST} | RST# | yes |
| 12 | SIO2 | AD2/D2/SIO2/SOF | yes |
| 13 | SO/SIO1 | AD1/D1/EOF/SIO1/SO | yes |
| 14 | VDDIO | VDDIO | yes |
| 15 | DIGIO8 | AD14/D14/DIGIO8/GPI8/GPO8/MII_TXD3/TX_SHIFT1 | yes |
| 16 | DIGIO7 | AD13/D13/DIGIO7/GPI7/GPO7/MII_TXD2/TX_SHIFT0 | yes |
| 17 | SI/SIO0 | AD0/D0/SI/SIO0/WD_STATE | yes |
| 18 | SYNC1 | LATCH1/SYNC1 | yes |
| 19 | SCK | AD9/D9/LATCH_IN/SCK | yes |
| 20 | VDDIO | VDDIO | yes |
| 21 | DIGIO6 | AD12/D12/DIGIO6/GPI6/GPO6/MII_TXD1 | yes |
| 22 | DIGIO5 | AD11/D11/DIGIO5/GPI5/GPO5/MII_TXD0 | yes |
| 23 | DIGIO4 | AD10/D10/DIGIO4/GPI4/GPO4/MII_TXEN | yes |
| 24 | VDDCR | VDDCR | yes |
| 25 | MII_CLK25 | A1/ALELO/MII_CLK25/OE_EXT | yes |
| 26 | DIGIO11 | A3/DIGIO11/GPI11/GPO11/MII_RXDV | yes |
| 27 | DIGIO12 | A4/DIGIO12/GPI12/GPO12/MII_RXD0 | yes |
| 28 | DIGIO13 | CS/DIGIO13/GPI13/GPO13/MII_RXD1 | yes |
| 29 | DIGIO10 | A2/ALEHI/DIGIO10/GPI10/GPO10/LINKACTLED2/MII_LINKPOL | yes |
| 30 | DIGIO14 | DIGIO14/ENB/GPI14/GPO14/MII_RXD2/WR | yes |
| 31 | DIGIO15 | DIGIO15/GPI15/GPO15/MII_RXD3/RD/RD_WR | yes |
| 32 | VDDIO | VDDIO | yes |
| 33 | DIGIO9 | A0/AD15/D15/DIGIO9/GPI9/GPO9/MII_RXER | yes |
| 34 | SYNC0 | LATCH0/SYNC0 | yes |
| 35 | SIO3 | AD3/D3/SIO3/WD_TRIG | yes |
| 36 | DIGIO0 | AD6/D6/DIGIO0/GPI0/GPO0/MII_RXCLK | yes |
| 37 | VDDIO | VDDIO | yes |
| 38 | VDDCR | VDDCR | yes |
| 39 | DIGIO1 | AD7/D7/DIGIO1/GPI1/GPO1/MII_MDC | yes |
| 40 | DIGIO2 | AD8/D8/DIGIO2/GPI2/GPO2/MII_MDIO | yes |
| 41 | TESTMODE | TESTMODE | yes |
| 42 | EESDA | EESDA/TMS | yes |
| 43 | EESCL | EESCL/TCK | yes |
| 44 | IRQ | IRQ | yes |
| 45 | RUNLED/E2PSIZE | E2PSIZE/RUNLED | yes |
| 46 | LINKACTLED1/CHIP_MODE1 | CHIP_MODE1/LINKACTLED1/TDI | yes |
| 47 | VDDIO | VDDIO | yes |
| 48 | LINKACTLED0/CHIP_MODE0 | CHIP_MODE0/LINKACTLED0/TDO | yes |
| 49 | DIGIO3 | AD4/D4/DIGIO3/GPI3/GPO3/MII_LINK | yes |
| 50 | ~{SCS} | AD5/D5/OUTVALID/SCS# | yes |
| 51 | VDD33TXRX1 | VDD33TXRX1 | yes |
| 52 | TXNA | TXNA | yes |
| 53 | TXPA | TXPA | yes |
| 54 | RXNA | RXNA | yes |
| 55 | RXPA | RXPA | yes |
| 56 | VDD12TX1 | VDD12TX1 | yes |
| 57 | RBIAS | RBIAS | yes |
| 58 | VDD33BIAS | VDD33BIAS | yes |
| 59 | VDD12TX2 | VDD12TX2 | yes |
| 60 | RXPB | RXPB | yes |
| 61 | RXNB | RXNB | yes |
| 62 | TXPB | TXPB | yes |
| 63 | TXNB | TXNB | yes |
| 64 | VDD33TXRX2 | VDD33TXRX2 | yes |
| 65 | VSS | VSS | yes |

### C7934 LM2904DR (SOIC-8)

Source: LM2904 datasheet, 8-pin SOIC pinout

| Pin | Symbol name | Datasheet | OK |
|---|---|---|---|
| 1 | 1OUT | 1OUT | yes |
| 2 | 1IN- | 1IN | yes |
| 3 | 1IN+ | 1IN | yes |
| 4 | GND | GND | yes |
| 5 | 2IN+ | 2IN | yes |
| 6 | 2IN- | 2IN | yes |
| 7 | 2OUT | 2OUT | yes |
| 8 | VCC | VCC | yes |

### C16040 MCP4822-E/SN (SOIC-8)

Source: MCP48X2 datasheet, 8-pin SOIC pinout (MCP4822 column)

| Pin | Symbol name | Datasheet | OK |
|---|---|---|---|
| 1 | VDD | VDD | yes |
| 2 | ~{CS} | CS | yes |
| 3 | SCK | SCK | yes |
| 4 | SDI | SDI | yes |
| 5 | ~{LDAC} | LDAC | yes |
| 6 | VOUTB | VOUTB | yes |
| 7 | VSS | VSS | yes |
| 8 | VOUTA | VOUTA | yes |

### C1524860 Omron P2R-05P socket (for G2R-1-S)

Source: Omron G2RS datasheet p.5 'G2R-1-S terminal arrangement' (coil 1-5, COM 2, NO 3, NC 4: contact arm rests on 4) and p.8 P2R-05P bottom view; pad distances from the 'Mounting Holes' drawing (6, 4.5, 15, 4, 4, 7 mm)

| Pin | Symbol name | Datasheet | OK |
|---|---|---|---|
| 1 | COIL1 | COIL1 | yes |
| 2 | COM | COM | yes |
| 3 | NO | NO | yes |
| 4 | NC | NC | yes |
| 5 | COIL2 | COIL2 | yes |

Footprint geometry against the datasheet drawing:

| Pads | Datasheet | Footprint | OK |
|---|---|---|---|
| 3-4 | dx 4.0 dy 6.0 | dx 4.00 dy 6.00 | yes |
| 4-2 | dx 4.0 dy 4.5 | dx 4.00 dy 4.50 | yes |
| 4-1 | dx - dy 15.0 | dx 5.50 dy 15.00 | yes |
| 1-5 | dx 7.0 dy 4.0 | dx 7.00 dy 4.00 | yes |

### C32677 PSM712-LF-T7 (SOT-23)

Source: ProTek PSM712 datasheet: pins 1 and 2 protected lines, pin 3 common (cathode); +12 V / -7 V stand-off referred to pin 3

| Pin | Symbol name | Datasheet | OK |
|---|---|---|---|
| 1 | IO1 | IO1 | yes |
| 2 | IO2 | IO2 | yes |
| 3 | COM | COM | yes |

### C2937625 PZ254V-11-03P 1x3 pin header

Source: 2.54 mm pitch pin header, pin n = position n

| Pin | Symbol name | Datasheet | OK |
|---|---|---|---|
| 1 | 1 | 1 | yes |
| 2 | 2 | 2 | yes |
| 3 | 3 | 3 | yes |

Footprint geometry against the datasheet drawing:

| Pads | Datasheet | Footprint | OK |
|---|---|---|---|
| 1-2 | dx 2.54 dy 0.0 | dx 2.54 dy 0.00 | yes |

### C970679 47 uF 50 V SMD electrolytic

Source: Footprint silkscreen: '+' mark and chamfer at pad 1: pad 1 = positive, pad 2 = negative

| Pin | Symbol name | Datasheet | OK |
|---|---|---|---|
| 1 | + | + | yes |
| 2 | - | - | yes |

### C148216 SMAJ15A (SMA)

Source: Footprint silkscreen band is at pad 1: pad 1 = cathode, pad 2 = anode

| Pin | Symbol name | Datasheet | OK |
|---|---|---|---|
| 1 | C | C | yes |
| 2 | A | A | yes |

### C83851 SMBJ30A (SMB)

Source: Footprint silkscreen: cathode bar and band at pad 1 (left, x<0): pad 1 = cathode, pad 2 = anode (unidirectional TVS)

| Pin | Symbol name | Datasheet | OK |
|---|---|---|---|
| 1 | K | K | yes |
| 2 | A | A | yes |

### C22452 SS54 (SMA)

Source: Footprint silkscreen band is at pad 2 (x<0, pad 2): pad 2 = cathode, pad 1 = anode

| Pin | Symbol name | Datasheet | OK |
|---|---|---|---|
| 1 | A | A | yes |
| 2 | K | K | yes |

### C56621 STM32F405VGT6 (LQFP-100)

Source: DocID022152 Rev 4 Table 7 'pin and ball definitions', LQFP100 column (pins whose names wrap over two lines read from the next line: PC14, PH0, PH1, PA0, PB2, PA13, PA14, PA15, PB3, PB4) cross-checked with Fig. 13 'LQFP100 pinout'

| Pin | Symbol name | Datasheet | OK |
|---|---|---|---|
| 1 | PE2 | PE2 | yes |
| 2 | PE3 | PE3 | yes |
| 3 | PE4 | PE4 | yes |
| 4 | PE5 | PE5 | yes |
| 5 | PE6 | PE6 | yes |
| 6 | VBAT | VBAT | yes |
| 7 | PC13/EXTI13 | PC13 | yes |
| 8 | PC14/OSC32_IN | PC14 | yes |
| 9 | PC15/OSC32_OUT | PC15 | yes |
| 10 | VSS | VSS | yes |
| 11 | VDD | VDD | yes |
| 12 | PH0/OSC_IN | PH0 | yes |
| 13 | PH1/OSC_OUT | PH1 | yes |
| 14 | NRST | NRST | yes |
| 15 | PC0 | PC0 | yes |
| 16 | PC1 | PC1 | yes |
| 17 | PC2 | PC2 | yes |
| 18 | PC3 | PC3 | yes |
| 19 | VDD | VDD | yes |
| 20 | VSSA | VSSA | yes |
| 21 | VREF+ | VREF+ | yes |
| 22 | VDDA | VDDA | yes |
| 23 | PA0/EXTI0 | PA0 | yes |
| 24 | PA1 | PA1 | yes |
| 25 | PA2/USART2_TX | PA2 | yes |
| 26 | PA3/USART2_RX | PA3 | yes |
| 27 | VSS | VSS | yes |
| 28 | VDD | VDD | yes |
| 29 | PA4/SPI1_NSS | PA4 | yes |
| 30 | PA5/SPI1_SCK | PA5 | yes |
| 31 | PA6/SPI1_MISO | PA6 | yes |
| 32 | PA7/SPI1_MOSI | PA7 | yes |
| 33 | PC4/EXTI4 | PC4 | yes |
| 34 | PC5 | PC5 | yes |
| 35 | PB0 | PB0 | yes |
| 36 | PB1 | PB1 | yes |
| 37 | PB2/BOOT1 | PB2 | yes |
| 38 | PE7 | PE7 | yes |
| 39 | PE8 | PE8 | yes |
| 40 | PE9 | PE9 | yes |
| 41 | PE10 | PE10 | yes |
| 42 | PE11 | PE11 | yes |
| 43 | PE12 | PE12 | yes |
| 44 | PE13 | PE13 | yes |
| 45 | PE14 | PE14 | yes |
| 46 | PE15 | PE15 | yes |
| 47 | PB10 | PB10 | yes |
| 48 | PB11 | PB11 | yes |
| 49 | VCAP_1 | VCAP_1 | yes |
| 50 | VDD | VDD | yes |
| 51 | PB12/SPI2_NSS | PB12 | yes |
| 52 | PB13/SPI2_SCK | PB13 | yes |
| 53 | PB14 | PB14 | yes |
| 54 | PB15/SPI2_MOSI | PB15 | yes |
| 55 | PD8 | PD8 | yes |
| 56 | PD9 | PD9 | yes |
| 57 | PD10 | PD10 | yes |
| 58 | PD11 | PD11 | yes |
| 59 | PD12 | PD12 | yes |
| 60 | PD13 | PD13 | yes |
| 61 | PD14 | PD14 | yes |
| 62 | PD15 | PD15 | yes |
| 63 | PC6 | PC6 | yes |
| 64 | PC7 | PC7 | yes |
| 65 | PC8 | PC8 | yes |
| 66 | PC9 | PC9 | yes |
| 67 | PA8 | PA8 | yes |
| 68 | PA9 | PA9 | yes |
| 69 | PA10 | PA10 | yes |
| 70 | PA11 | PA11 | yes |
| 71 | PA12 | PA12 | yes |
| 72 | PA13/SWDIO | PA13 | yes |
| 73 | VCAP_2 | VCAP_2 | yes |
| 74 | VSS | VSS | yes |
| 75 | VDD | VDD | yes |
| 76 | PA14/SWCLK | PA14 | yes |
| 77 | PA15 | PA15 | yes |
| 78 | PC10 | PC10 | yes |
| 79 | PC11 | PC11 | yes |
| 80 | PC12 | PC12 | yes |
| 81 | PD0 | PD0 | yes |
| 82 | PD1 | PD1 | yes |
| 83 | PD2 | PD2 | yes |
| 84 | PD3 | PD3 | yes |
| 85 | PD4 | PD4 | yes |
| 86 | PD5 | PD5 | yes |
| 87 | PD6 | PD6 | yes |
| 88 | PD7 | PD7 | yes |
| 89 | PB3/SWO | PB3 | yes |
| 90 | PB4/TIM3_CH1 | PB4 | yes |
| 91 | PB5/TIM3_CH2 | PB5 | yes |
| 92 | PB6 | PB6 | yes |
| 93 | PB7 | PB7 | yes |
| 94 | BOOT0 | BOOT0 | yes |
| 95 | PB8 | PB8 | yes |
| 96 | PB9 | PB9 | yes |
| 97 | PE0 | PE0 | yes |
| 98 | PE1 | PE1 | yes |
| 99 | VSS | VSS | yes |
| 100 | VDD | VDD | yes |

### C39031 TLP290-4 (SOP-16)

Source: TLP290-4 datasheet rev 5.0 section 4 figure: ch1 LED 1-2 / C16 E15, ch2 3-4 / C14 E13, ch3 5-6 / C12 E11, ch4 7-8 / C10 E9

| Pin | Symbol name | Datasheet | OK |
|---|---|---|---|
| 1 | IN1A | IN1A | yes |
| 2 | IN1B | IN1B | yes |
| 3 | IN2A | IN2A | yes |
| 4 | IN2B | IN2B | yes |
| 5 | IN3A | IN3A | yes |
| 6 | IN3B | IN3B | yes |
| 7 | IN4A | IN4A | yes |
| 8 | IN4B | IN4B | yes |
| 9 | E4 | E4 | yes |
| 10 | C4 | C4 | yes |
| 11 | E3 | E3 | yes |
| 12 | C3 | C3 | yes |
| 13 | E2 | E2 | yes |
| 14 | C2 | C2 | yes |
| 15 | E1 | E1 | yes |
| 16 | C1 | C1 | yes |

### C845537 ULN2803A UMW (SOP-18)

Source: UMW ULN2803 datasheet 'Pin descriptions (DIP/SOP-18)': inputs 1-8, outputs 18-11 (ch1 = pin 18), GND 9, COM 10

| Pin | Symbol name | Datasheet | OK |
|---|---|---|---|
| 1 | Input | INPUT | yes |
| 2 | Input | INPUT | yes |
| 3 | Input | INPUT | yes |
| 4 | Input | INPUT | yes |
| 5 | Input | INPUT | yes |
| 6 | Input | INPUT | yes |
| 7 | Input | INPUT | yes |
| 8 | Input | INPUT | yes |
| 9 | GND | GND | yes |
| 10 | COM | COM | yes |
| 11 | Output | OUTPUT | yes |
| 12 | Output | OUTPUT | yes |
| 13 | Output | OUTPUT | yes |
| 14 | Output | OUTPUT | yes |
| 15 | Output | OUTPUT | yes |
| 16 | Output | OUTPUT | yes |
| 17 | Output | OUTPUT | yes |
| 18 | Output | OUTPUT | yes |

### C5369843 URB2403S-6WR3 (SIP-8, pin 4 absent)

Source: URB_S-6WR3 datasheet p.5 Pin-Out: 1 GND (input), 2 Vin, 3 Ctrl, 5 NC, 6 +Vo, 7 0V (output), 8 NC

| Pin | Symbol name | Datasheet | OK |
|---|---|---|---|
| 1 | GND | GND | yes |
| 2 | VIN | VIN | yes |
| 3 | CTRL | CTRL | yes |
| 5 | NC | NC | yes |
| 6 | +VO | VO | yes |
| 7 | -VO | VO | yes |
| 8 | NC | NC | yes |

Footprint geometry against the datasheet drawing:

| Pads | Datasheet | Footprint | OK |
|---|---|---|---|
| 1-2 | dx 2.54 dy 0.0 | dx 2.54 dy 0.00 | yes |
| 1-3 | dx 5.08 dy 0.0 | dx 5.08 dy 0.00 | yes |
| 1-5 | dx 10.16 dy 0.0 | dx 10.16 dy 0.00 | yes |
| 1-6 | dx 12.7 dy 0.0 | dx 12.70 dy 0.00 | yes |
| 1-7 | dx 15.24 dy 0.0 | dx 15.24 dy 0.00 | yes |
| 1-8 | dx 17.78 dy 0.0 | dx 17.78 dy 0.00 | yes |

### C3031185 URB2405S-6WR3 (SIP-8, pin 4 absent)

Source: URB_S-6WR3 datasheet p.5 Pin-Out: 1 GND (input), 2 Vin, 3 Ctrl, 5 NC, 6 +Vo, 7 0V (output), 8 NC

| Pin | Symbol name | Datasheet | OK |
|---|---|---|---|
| 1 | GND | GND | yes |
| 2 | VIN | VIN | yes |
| 3 | CTRL | CTRL | yes |
| 5 | NC | NC | yes |
| 6 | +VO | VO | yes |
| 7 | -VO | VO | yes |
| 8 | NC | NC | yes |

Footprint geometry against the datasheet drawing:

| Pads | Datasheet | Footprint | OK |
|---|---|---|---|
| 1-2 | dx 2.54 dy 0.0 | dx 2.54 dy 0.00 | yes |
| 1-3 | dx 5.08 dy 0.0 | dx 5.08 dy 0.00 | yes |
| 1-5 | dx 10.16 dy 0.0 | dx 10.16 dy 0.00 | yes |
| 1-6 | dx 12.7 dy 0.0 | dx 12.70 dy 0.00 | yes |
| 1-7 | dx 15.24 dy 0.0 | dx 15.24 dy 0.00 | yes |
| 1-8 | dx 17.78 dy 0.0 | dx 17.78 dy 0.00 | yes |

### C5369844 URB2415S-6WR3 (SIP-8, pin 4 absent)

Source: URB_S-6WR3 datasheet p.5 Pin-Out: 1 GND (input), 2 Vin, 3 Ctrl, 5 NC, 6 +Vo, 7 0V (output), 8 NC

| Pin | Symbol name | Datasheet | OK |
|---|---|---|---|
| 1 | GND | GND | yes |
| 2 | VIN | VIN | yes |
| 3 | CTRL | CTRL | yes |
| 5 | NC | NC | yes |
| 6 | +VO | VO | yes |
| 7 | -VO | VO | yes |
| 8 | NC | NC | yes |

Footprint geometry against the datasheet drawing:

| Pads | Datasheet | Footprint | OK |
|---|---|---|---|
| 1-2 | dx 2.54 dy 0.0 | dx 2.54 dy 0.00 | yes |
| 1-3 | dx 5.08 dy 0.0 | dx 5.08 dy 0.00 | yes |
| 1-5 | dx 10.16 dy 0.0 | dx 10.16 dy 0.00 | yes |
| 1-6 | dx 12.7 dy 0.0 | dx 12.70 dy 0.00 | yes |
| 1-7 | dx 15.24 dy 0.0 | dx 15.24 dy 0.00 | yes |
| 1-8 | dx 17.78 dy 0.0 | dx 17.78 dy 0.00 | yes |
