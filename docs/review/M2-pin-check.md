# M2 - Symbol and footprint pin check

Every imported symbol is compared with the manufacturer datasheet pin table (`scripts/pin_tables.py`, each entry names its source), and with its footprint pad numbers. Re-run with `python3 -I scripts/pincheck.py --md docs/review/M2-pin-check.md`.

**42 symbols checked, 42 clean, 0 with problems.**

| LCSC | Symbol | Pins | Pads | Datasheet check | Result |
|---|---|---|---|---|---|
| C15742 | STM32F405RGT6 | 64 | 64 | yes | OK |
| C2595919 | ECS-3225MVQ-250-CN-TR | 4 | 4 | yes | OK |
| C3975188 | PZ127-2-05-S | 10 | 10 | no table (generic part) | OK |
| C2937625 | PZ254V-11-03P_C2937625 | 3 | 3 | no table (generic part) | OK |
| C80933 | LAN9252I_PT | 65 | 65 | yes | OK |
| C615715 | 24LC32AT-I_SN | 8 | 8 | yes | OK |
| C69427 | HY911105AE | 14 | 14 | yes | OK |
| C5369843 | URB2403S-6WR3_C5369843 | 7 | 7 | yes | OK |
| C3031185 | URB2405S-6WR3_C3031185 | 7 | 7 | yes | OK |
| C5369844 | URB2415S-6WR3_C5369844 | 7 | 7 | yes | OK |
| C320242 | SMBJ33A_C320242 | 2 | 2 | yes | OK |
| C22452 | SS54_C22452 | 2 | 2 | yes | OK |
| C58066 | Fusetransparentseat | 2 | 2 | no table (generic part) | OK |
| C3116 | 1A250VAC | 0 | - | no table (generic part) | OK |
| C3118 | 3A250VACGlasstubefuse | 0 | - | no table (generic part) | OK |
| C970679 | RVT1H470M060747UF50V | 2 | 2 | yes | OK |
| C2960285 | 100V100UFCD288 | 2 | 2 | yes | OK |
| C39031 | TLP290-4 | 16 | 16 | yes | OK |
| C441205 | KF2EDGR-5.08-3P | 3 | 3 | no table (generic part) | OK |
| C151168 | 1812L050_30PR | 2 | 2 | no table (generic part) | OK |
| C5305 | 2.54短路帽开口 | 0 | - | no table (generic part) | OK |
| C6180 | AM26LS32ACDR | 16 | 16 | yes | OK |
| C5347249 | CA-IS3742LN | 16 | 16 | yes | OK |
| C441208 | KF2EDGR-5.08-6P | 6 | 6 | no table (generic part) | OK |
| C70068 | nSMD025 | 2 | 2 | no table (generic part) | OK |
| C32677 | PSM712-LF-T7 | 3 | 3 | yes | OK |
| C428888 | CA-IS3740LN | 16 | 16 | yes | OK |
| C845537 | ULN2803A_C845537 | 18 | 18 | yes | OK |
| C1524860 | P2R-05P | 5 | 5 | yes | OK |
| C528653 | CA-IS3740HW | 16 | 16 | yes | OK |
| C16040 | MCP4822-E_SN | 8 | 8 | yes | OK |
| C7934 | LM2904DR | 8 | 8 | yes | OK |
| C42738 | L78L05ABUTR | 3 | 3 | yes | OK |
| C83571 | 2N7002DW-7-F | 6 | 6 | yes | OK |
| C148216 | SMAJ15A-C148216 | 2 | 2 | yes | OK |
| C441204 | KF2EDGR-5.08-2P | 2 | 2 | no table (generic part) | OK |
| C440880 | KF2EDGK-5.08-2P-AA | 0 | - | no table (generic part) | OK |
| C441206 | KF2EDGR-5.08-4P | 4 | 4 | no table (generic part) | OK |
| C440882 | KF2EDGK-5.08-4P-AA | 0 | - | no table (generic part) | OK |
| C440881 | KF2EDGK-5.08-3P-AA | 0 | - | no table (generic part) | OK |
| C440884 | KF2EDGK-5.08-6P | 0 | - | no table (generic part) | OK |
| C5272782 | Keystone-7770 | 1 | 1 | no table (generic part) | OK |

## Pin-by-pin tables

### C15742 STM32F405RGT6 (LQFP-64)

Source: DocID022152 Rev 4: Fig. 12 'LQFP64 pinout' (pins 1-16, 33-48 read from the figure; the rest from Table 7 LQFP64 column, PB3/JTDO row 55)

| Pin | Symbol name | Datasheet | OK |
|---|---|---|---|
| 1 | VBAT | VBAT | yes |
| 2 | PC13 | PC13 | yes |
| 3 | PC14-OSC32_IN(PC14) | PC14 | yes |
| 4 | PC15-OSC32_OUT(PC15) | PC15 | yes |
| 5 | PH0-OSC_IN(PH0) | PH0 | yes |
| 6 | PH1-OSC_OUT(PH1) | PH1 | yes |
| 7 | NRST | NRST | yes |
| 8 | PC0 | PC0 | yes |
| 9 | PC1 | PC1 | yes |
| 10 | PC2 | PC2 | yes |
| 11 | PC3 | PC3 | yes |
| 12 | VSSA | VSSA | yes |
| 13 | VDDA | VDDA | yes |
| 14 | PA0-WKUP(PA0) | PA0 | yes |
| 15 | PA1 | PA1 | yes |
| 16 | PA2 | PA2 | yes |
| 17 | PA3 | PA3 | yes |
| 18 | VSS | VSS | yes |
| 19 | VDD | VDD | yes |
| 20 | PA4 | PA4 | yes |
| 21 | PA5 | PA5 | yes |
| 22 | PA6 | PA6 | yes |
| 23 | PA7 | PA7 | yes |
| 24 | PC4 | PC4 | yes |
| 25 | PC5 | PC5 | yes |
| 26 | PB0 | PB0 | yes |
| 27 | PB1 | PB1 | yes |
| 28 | PB2-BOOT1(PB2) | PB2 | yes |
| 29 | PB10 | PB10 | yes |
| 30 | PB11 | PB11 | yes |
| 31 | VCAP_1 | VCAP_1 | yes |
| 32 | VDD | VDD | yes |
| 33 | PB12 | PB12 | yes |
| 34 | PB13 | PB13 | yes |
| 35 | PB14 | PB14 | yes |
| 36 | PB15 | PB15 | yes |
| 37 | PC6 | PC6 | yes |
| 38 | PC7 | PC7 | yes |
| 39 | PC8 | PC8 | yes |
| 40 | PC9 | PC9 | yes |
| 41 | PA8 | PA8 | yes |
| 42 | PA9 | PA9 | yes |
| 43 | PA10 | PA10 | yes |
| 44 | PA11 | PA11 | yes |
| 45 | PA12 | PA12 | yes |
| 46 | PA13(JTMS-SWDIO) | PA13 | yes |
| 47 | VCAP_2 | VCAP_2 | yes |
| 48 | VDD | VDD | yes |
| 49 | PA14(JTCK-SWCLK) | PA14 | yes |
| 50 | PA15(JTDI) | PA15 | yes |
| 51 | PC10 | PC10 | yes |
| 52 | PC11 | PC11 | yes |
| 53 | PC12 | PC12 | yes |
| 54 | PD2 | PD2 | yes |
| 55 | PB3(JTDOTRACESWO) | PB3 | yes |
| 56 | PB4(NJTRST) | PB4 | yes |
| 57 | PB5 | PB5 | yes |
| 58 | PB6 | PB6 | yes |
| 59 | PB7 | PB7 | yes |
| 60 | BOOT0 | BOOT0 | yes |
| 61 | PB8 | PB8 | yes |
| 62 | PB9 | PB9 | yes |
| 63 | VSS | VSS | yes |
| 64 | VDD | VDD | yes |

### C2595919 ECS-3225MVQ-250-CN-TR (3.2x2.5 mm, 4-pin)

Source: ECS-3225MVQ datasheet pin table: 1 tri-state (OE, NC = active), 2 GND, 3 output, 4 VDD

| Pin | Symbol name | Datasheet | OK |
|---|---|---|---|
| 1 | OE | TRISTATE/OE/ST | yes |
| 2 | Gnd | GND | yes |
| 3 | Output | OUTPUT | yes |
| 4 | Vdd | VDD | yes |

### C80933 LAN9252I/PT (64-TQFP-EP)

Source: DS00001909A Table 3-2 '64-TQFP-EP package pin assignments' (all five mode columns); pin 65 = exposed pad VSS

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
| 9 | FXSDA/FXLOSA/FXSDENA | FXLOSA/FXSDA/FXSDENA | yes |
| 10 | FXSDB/FXLOSB/FXSDENB | FXLOSB/FXSDB/FXSDENB | yes |
| 11 | ~{RST} | RST# | yes |
| 12 | D2/AD2/SOF/SIO2 | AD2/D2/SIO2/SOF | yes |
| 13 | D1/AD1/EOF/SO/SIO1 | AD1/D1/EOF/SIO1/SO | yes |
| 14 | VDDIO | VDDIO | yes |
| 15 | D14/AD14/DIGIO8/GPI8/GPO8/MII_TXD3/TX_SHIFT1 | AD14/D14/DIGIO8/GPI8/GPO8/MII_TXD3/TX_SHIFT1 | yes |
| 16 | D13/AD13/DIGIO7/GPI7/GPO7/MII_TXD2/TX_SHIFT0 | AD13/D13/DIGIO7/GPI7/GPO7/MII_TXD2/TX_SHIFT0 | yes |
| 17 | D0/AD0/WD_STATE/SI/SIO0 | AD0/D0/SI/SIO0/WD_STATE | yes |
| 18 | SYNC1/LATCH1 | LATCH1/SYNC1 | yes |
| 19 | D9/AD9/LATCH_IN/SCK | AD9/D9/LATCH_IN/SCK | yes |
| 20 | VDDIO | VDDIO | yes |
| 21 | D12/AD12/DIGIO6/GPI6/GPO6/MII_TXD1 | AD12/D12/DIGIO6/GPI6/GPO6/MII_TXD1 | yes |
| 22 | D11/AD11/DIGIO5/GPI5/GPO5/MII_TXD0 | AD11/D11/DIGIO5/GPI5/GPO5/MII_TXD0 | yes |
| 23 | D10/AD10/DIGIO4/GPI4/GPO4/MII_TXEN | AD10/D10/DIGIO4/GPI4/GPO4/MII_TXEN | yes |
| 24 | VDDCR | VDDCR | yes |
| 25 | A1/ALELO/OE_EXT/MII_CLK25 | A1/ALELO/MII_CLK25/OE_EXT | yes |
| 26 | A3/DIGIO11/GPI11/GPO11/MII_RXDV | A3/DIGIO11/GPI11/GPO11/MII_RXDV | yes |
| 27 | A4/DIGIO12/GPI12/GPO12/MII_RXD0 | A4/DIGIO12/GPI12/GPO12/MII_RXD0 | yes |
| 28 | CS/DIGIO13/GPI13/GPO13/MII_RXD1 | CS/DIGIO13/GPI13/GPO13/MII_RXD1 | yes |
| 29 | A2/ALEHI/DIGIO10/GPI10/GPO10/LINKACTLED2/MII_LINKPOL | A2/ALEHI/DIGIO10/GPI10/GPO10/LINKACTLED2/MII_LINKPOL | yes |
| 30 | WR/ENB/DIGIO14/GPI14/GPO14/MII_RXD2 | DIGIO14/ENB/GPI14/GPO14/MII_RXD2/WR | yes |
| 31 | RD/RD_WR/DIGIO15/GPI15/GPO15/MII_RXD3 | DIGIO15/GPI15/GPO15/MII_RXD3/RD/RD_WR | yes |
| 32 | VDDIO | VDDIO | yes |
| 33 | A0/D15/AD15/DIGIO9/GPI9/GPO9/MII_RXER | A0/AD15/D15/DIGIO9/GPI9/GPO9/MII_RXER | yes |
| 34 | SYNC0/LATCH0 | LATCH0/SYNC0 | yes |
| 35 | D3/AD3/WD_TRIG/SIO3 | AD3/D3/SIO3/WD_TRIG | yes |
| 36 | D6/AD6/DIGIO0/GPI0/GPO0/MII_RXCLK | AD6/D6/DIGIO0/GPI0/GPO0/MII_RXCLK | yes |
| 37 | VDDIO | VDDIO | yes |
| 38 | VDDCR | VDDCR | yes |
| 39 | D7/AD7/DIGIO1/GPI1/GPO1/MII_MDC | AD7/D7/DIGIO1/GPI1/GPO1/MII_MDC | yes |
| 40 | D8/AD8/DIGIO2/GPI2/GPO2/MII_MDIO | AD8/D8/DIGIO2/GPI2/GPO2/MII_MDIO | yes |
| 41 | TESTMODE | TESTMODE | yes |
| 42 | EESDA/TMS | EESDA/TMS | yes |
| 43 | EESCL/TCK | EESCL/TCK | yes |
| 44 | IRQ | IRQ | yes |
| 45 | RUNLED/E2PSIZE | E2PSIZE/RUNLED | yes |
| 46 | LINKACTLED1/TDI/CHIP_MODE1 | CHIP_MODE1/LINKACTLED1/TDI | yes |
| 47 | VDDIO | VDDIO | yes |
| 48 | LINKACTLED0/TDO/CHIP_MODE0 | CHIP_MODE0/LINKACTLED0/TDO | yes |
| 49 | D4/AD4/DIGIO3/GPI3/GPO3/MII_LINK | AD4/D4/DIGIO3/GPI3/GPO3/MII_LINK | yes |
| 50 | D5/AD5/OUTVALID/~{SCS} | AD5/D5/OUTVALID/SCS# | yes |
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

### C69427 HY911105AE RJ45 with magnetics and LEDs

Source: Hanrun HY911105AE datasheet p.1 schematic: P1 TD+, P2 TD-, P3 RD+, P4 TX centre tap, P5 RX centre tap, P6 RD-, P7 NC, P8 chassis, green LED 9(A)-10(K), yellow LED 12(A)-11(K)

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

### C3031185 URB2405S-6WR3 (SIP-8, pin 4 absent)

Source: URB_S-6WR3 datasheet p.5 Pin-Out: 1 GND (input), 2 Vin, 3 Ctrl, 5 NC, 6 +Vo, 7 0V (output), 8 NC

| Pin | Symbol name | Datasheet | OK |
|---|---|---|---|
| 1 | GND | GND | yes |
| 2 | VIN | VIN | yes |
| 3 | CTRL | CTRL | yes |
| 5 | NC | NC | yes |
| 6 | +Vo | VO | yes |
| 7 | -Vo | VO | yes |
| 8 | NC | NC | yes |

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

### C320242 SMBJ33A (SMB)

Source: Footprint silkscreen band is at pad 1 (left, x<0): pad 1 = cathode, pad 2 = anode (unidirectional TVS)

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

### C970679 47 uF 50 V SMD electrolytic

Source: Footprint silkscreen: '+' mark and chamfer at pad 1: pad 1 = positive, pad 2 = negative

| Pin | Symbol name | Datasheet | OK |
|---|---|---|---|
| 1 | + | + | yes |
| 2 | - | - | yes |

### C2960285 100 uF 100 V radial electrolytic

Source: Footprint silkscreen: '+' mark and chamfer at pad 1: pad 1 = positive, pad 2 = negative

| Pin | Symbol name | Datasheet | OK |
|---|---|---|---|
| 1 | + | + | yes |
| 2 | - | - | yes |

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

### C32677 PSM712-LF-T7 (SOT-23)

Source: ProTek PSM712 datasheet: pins 1 and 2 protected lines, pin 3 common (cathode); +12 V / -7 V stand-off referred to pin 3

| Pin | Symbol name | Datasheet | OK |
|---|---|---|---|
| 1 | IO1 | IO1 | yes |
| 2 | IO2 | IO2 | yes |
| 3 | COM | COM | yes |

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

### C1524860 Omron P2R-05P socket (for G2R-1-S)

Source: Omron G2RS datasheet p.5 'G2R-1-S terminal arrangement' (coil 1-5, COM 2, NO 3, NC 4: contact arm rests on 4) and p.8 P2R-05P bottom view

| Pin | Symbol name | Datasheet | OK |
|---|---|---|---|
| 1 | COIL1 | COIL1 | yes |
| 2 | COM | COM | yes |
| 3 | NO | NO | yes |
| 4 | NC | NC | yes |
| 5 | COIL2 | COIL2 | yes |

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

### C42738 L78L05ABUTR (SOT-89-3)

Source: L78L datasheet Fig. 2: pin 1 VOUT, pin 2 GND, pin 3 VIN (SOT-89)

| Pin | Symbol name | Datasheet | OK |
|---|---|---|---|
| 1 | VOUT | VOUT | yes |
| 2 | GND | GND | yes |
| 3 | VIN | VIN | yes |

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

### C148216 SMAJ15A (SMA)

Source: Footprint silkscreen band is at pad 1: pad 1 = cathode, pad 2 = anode

| Pin | Symbol name | Datasheet | OK |
|---|---|---|---|
| 1 | C | C | yes |
| 2 | A | A | yes |
