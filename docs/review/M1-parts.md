# M1 - Parts list for review

Stock and prices checked live on LCSC on 2026-11-06 (qty-1 USD). Source of truth: `bom/parts.csv`, rebuilt and re-validated by `scripts/build_bom.py`. ERC and PDF do not apply to M1 (no schematic yet).

## Still needs your decision

| Part | Plan LCSC | Proposed LCSC | Why |
|---|---|---|---|

## Other things the checks found

Decided by the owner on 2026-11-05 (status CHANGED in the list, recorded in `docs/plan.md` Decisions log):

- MPG receiver: C2671811 (zero stock) replaced by **C6180 AM26LS32ACDR**.
- Relay driver: C181731 (zero stock) replaced by **C845537 UMW ULN2803A**.
- Module input capacitors: **3 x 100 uF/100 V** added, per the URB datasheet.
- Status LEDs: **yellow-green NCD0603C3** accepted in place of green.
- 24 V input fuses: **replaceable 5x20 mm fuses** (same covered holder as the relay fuses, 1 A and 3 A glass fuses on LCSC) instead of SMD fuses.
- Relay fuse holder: C58066 kept (superseded on 2026-11-06, see below).
- Terminals: **one connector per I/O** (supersedes the 7-sets answer): 20 inputs and 8 relays on 3-pole 5.08 mm, 2 analog outputs on 2-pole, MPG 6-pole and power 4-pole unchanged. No 8-, 10- or 14-pole terminals remain.
- SMBJ33A vs the URB 40 V input maximum: **parts kept, module-side limiting designed in M3** and brought for approval.

Changed during the M2 review (2026-11-06):

- MCU: **STM32F405VGT6 (LQFP-100, C56621)** replaces the 64-pin part. The EtherCAT ERR LED goes on a spare pin.
- Fuse holders: **Littelfuse 646 block (C206887) + 648 clear cover (C187509)** replace C58066, which had no dimensioned drawing.
- PE terminal: Keystone 7770 kept and an **M3 x 6 screw (C357543)** added.
- Sourcing: **PCBPower buys every component from lcsc.com**, so lcsc.com stock is the only stock that counts. Four capacitors that lcsc.com showed at 0 were replaced by C1591, C1589, C559769 and C91185. JLCPCB is not used for sourcing or stock.

Still open:

1. **STM32F405VGT6 price.** About $7.6 at qty 1 on lcsc.com (plan: about $3.2 for the 64-pin part), about 900 in stock. Information only.
2. **PTC margins.** The 0.5 A sensor PTC is rated 30 V against a 28.8 V maximum input. Information only.
3. **Estimated counts.** Rows with Qty_basis = est (100 nF, 10 uF, 4.7 uF, 10 k, 1 k, 49.9 R, 1 uF) are estimates; exact counts come from the schematic sheets.

## Part-level flags

| Part | LCSC | Stock | Note |
|---|---|---|---|
| 25 MHz CMOS oscillator, 3.2x2.5 mm | C2595919 | 45 | Ordering code -CN decodes to +/-25 ppm, -40..+85 C (datasheet ordering table), meets the <= +/-50 ppm target. Datasheet note says +/-25 ppm is 'contact ECS for availability' and LCSC stock is under 100: confirm before ordering. |
| URB2403S-6WR3 isolated DC-DC 24V to 3.3V 1.35 A | C5369843 | 182 | Datasheet: absolute max input 40 V ('exceeding may cause permanent damage'). The plan's SMBJ33A clamped at 53.3 V; replaced by the SMBJ30A (48.4 V) on 2026-11-06. |
| URB2405S-6WR3 isolated DC-DC 24V to 5V 1.2 A | C3031185 | 6188 | Same 40 V input maximum. |
| URB2415S-6WR3 isolated DC-DC 24V to 15V 0.4 A | C5369844 | 109 | LCSC rates -40..+105 C (plan said 'check datasheet'). Same 40 V input maximum; stock about 100. |
| PTC 0.5 A hold, 30 V, 1812 (sensor +24 V) | C151168 | 10620 | 0.5 A hold / 1 A trip, 30 V max vs 28.8 V input, thin margin. One per input terminal (DI, SEL). |
| Omron P2R-05P PCB relay socket | C1524860 | 44 | Stock 44 (need 8 per board). Plan allows Mouser/DigiKey if LCSC runs out. |

## Not on LCSC (bought locally in India or unfitted)

- Omron G2R-1-S DC24 relay (buy locally in India) x8: Not on the assembly line. Rating: -40..+70 C per plan, confirm against the Omron datasheet.
- Fuse 5x20 mm T5A 250 VAC ceramic (buy locally in India) x8: Not on the assembly line.
- RC snubber across each contact (not fitted) x8: Footprint only (resistor + X-class capacitor). Values chosen in M5/layout.
- Test points (rails, OE, AO_CLAMP, SPI, MPG A/B, PH1) and mounting holes are bare pads/holes: no part, no LCSC number.

## Full list

Status: PLAN = exactly as in the plan, verified; NEW = commodity part chosen in M1; *-FLAG = see flags above; CHANGED = approved deviation from the plan; DECISION = still needs approval; LOCAL / FOOTPRINT = not purchased through LCSC.

| Sheet | Refs | Description | Qty | LCSC | MPN | Mfr | Temp | Stock | $ | Lib | Fit | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 3 MCU | U301 | STM32F405VGT6 MCU LQFP-100 | 1 | C56621 | STM32F405VGT6 | ST | -40℃~+85℃ | 920 | 7.6428 | extended | Y | CHANGED |
| 3 MCU | X301 | 25 MHz CMOS oscillator, 3.2x2.5 mm | 1 | C2595919 | ECS-3225MVQ-250-CN-TR | ECS | -40℃~+85℃ | 45 | 2.028 | extended | Y | PLAN-FLAG |
| 3 MCU | J301 | SWD header 2x5 1.27 mm SMD | 1 | C3975188 | PZ127-2-05-S | HCTL | -40℃~+105℃ | 14970 | 0.1472 | extended | Y | NEW |
| 3 MCU | J302 | USART2 header 1x3 2.54 mm | 1 | C2937625 | PZ254V-11-03P | XFCN | -40℃~+105℃ | 1011340 | 0.0201 | extended | Y | NEW |
| 3 MCU | FB301 | Ferrite bead 600R@100MHz 0603 (VDDA) | 1 | C19330 | BLM18AG601SN1D | muRata | -55℃~+125℃ | 431100 | 0.0122 | extended | Y | NEW |
| 3 MCU | LED301 | Heartbeat LED yellow 0603 | 1 | C2287 | KT-0603Y | Hubei KENTO Elec | -40℃~+85℃ | 91350 | 0.0108 | extended | Y | NEW |
| 4 EtherCAT | U401 | LAN9252I/PT EtherCAT slave controller TQFP-64 | 1 | C80933 | LAN9252I/PT | MICROCHIP | -40℃~+85℃ | 4189 | 8.6354 | extended | Y | PLAN |
| 4 EtherCAT | U402 | 24LC32AT-I/SN EEPROM 32 Kbit SOIC-8 | 1 | C615715 | 24LC32AT-I/SN | MICROCHIP | -40℃~+85℃ | 2185 | 0.4696 | extended | Y | PLAN |
| 4 EtherCAT | J401-J402 | RJ45 jack with integrated magnetics and LEDs | 2 | C69427 | HY911105AE | HANRUN(Zhongshan HanRu | -40℃~+85℃ | 3023 | 2.8377 | extended | Y | PLAN |
| 4 EtherCAT | LED401 | EtherCAT RUN LED (yellow-green) 0603 | 1 | C89809 | NCD0603C3 | NATIONSTAR | -30℃~+85℃ | 20640 | 0.0261 | extended | Y | CHANGED |
| 4 EtherCAT | LED402 | EtherCAT ERR LED red 0603 | 1 | C2286 | KT-0603R | Hubei KENTO Elec | -40℃~+85℃ | 4158200 | 0.0077 | basic | Y | NEW |
| 4 EtherCAT | R4xx | 49.9 R 1% 0603 (LAN9252 TX/RX termination) | 8 | C23185 | 0603WAF499JT5E | UNI-ROYAL | -55℃~+155℃ | 555100 | 0.002 | basic | Y | NEW |
| 4 EtherCAT | R4xx | 12.1 k 1% 0603 (RBIAS) | 1 | C22864 | 0603WAF1212T5E | UNI-ROYAL | -55℃~+155℃ | 154400 | 0.0016 | extended | Y | NEW |
| 4 EtherCAT | R4xx | 4.7 k 1% 0603 (EEPROM pull-ups) | 2 | C23162 | 0603WAF4701T5E | UNI-ROYAL | -55℃~+155℃ | 4065700 | 0.0028 | basic | Y | NEW |
| 4 EtherCAT | R4xx | 1 M 1% 0603 (shield bleed) | 1 | C22935 | 0603WAF1004T5E | UNI-ROYAL | -55℃~+155℃ | 1542400 | 0.0018 | basic | Y | NEW |
| 4 EtherCAT | FB401-FB404 | Ferrite bead 220R@100MHz 0603 (LAN9252 PHY supplies, VDD12TX) | 4 | C85827 | BLM18EG221SN1D | muRata | -55℃~+125℃ | 186860 | 0.0597 | extended | Y | NEW |
| 4 EtherCAT | C4xx | 22 nF 50 V X7R 0603 (magnetics centre taps) | 2 | C106222 | CC0603KRX7R9BB223 | YAGEO | see MPN datasheet | 246600 | 0.0032 | extended | Y | NEW |
| 4 EtherCAT | C4xx | 470 pF 50 V X7R 0603 (LAN9252 VDDCR) | 1 | C1620 | 0603B471K500NT | FH | see MPN datasheet | 77100 | 0.0058 | basic | Y | NEW |
| 4 EtherCAT | C4xx | 1 nF 2 kV X7R 1206 (shield to PE) | 1 | C9196 | 1206B102K202NT | FH | see MPN datasheet | 219120 | 0.0229 | basic | Y | NEW |
| 2 Power | U201 | URB2403S-6WR3 isolated DC-DC 24V to 3.3V 1.35 A | 1 | C5369843 | URB2403S-6WR3 | YLPTEC | -40℃~+105℃ | 182 | 5.6911 | extended | Y | PLAN-FLAG |
| 2 Power | U202 | URB2405S-6WR3 isolated DC-DC 24V to 5V 1.2 A | 1 | C3031185 | URB2405S-6WR3 | YLPTEC | -40℃~+105℃ | 6188 | 4.8336 | extended | Y | PLAN-FLAG |
| 2 Power | U203 | URB2415S-6WR3 isolated DC-DC 24V to 15V 0.4 A | 1 | C5369844 | URB2415S-6WR3 | YLPTEC | -40℃~+105℃ | 109 | 5.7982 | extended | Y | PLAN-FLAG |
| 2 Power | D201-D202 | SMBJ30A TVS 600 W, 30 V stand-off, SMB | 2 | C83851 | SMBJ30A | Littelfuse | -65℃~+150℃ | 17085 | 0.1279 | extended | Y | CHANGED |
| 2 Power | D203-D204 | SS54 Schottky 40 V 5 A SMA (reverse polarity) | 2 | C22452 | SS54 | MDD(Microdiode Semicon | see MPN datasheet | 1462890 | 0.045 | basic | Y | NEW |
| 2 Power | F201-F202 | Fuse block 5x20 mm PCB, Littelfuse 646 (24V_LOGIC, 24V_IO) | 2 | C206887 | 64600001003 | Littelfuse | see MPN datasheet | 963 | 0.9428 | extended | Y | CHANGED |
| 2 Power | F201 | Fuse 5x20 mm 1 A 250 V glass (24V_LOGIC) | 1 | C3116 | 5F.1000210000R1 | Xucheng Elec | -40℃~+125℃ | 10940 | 0.0648 | extended | Y | CHANGED |
| 2 Power | F202 | Fuse 5x20 mm 3 A 250 V glass (24V_IO) | 1 | C3118 | 5G.3000210000S1 | Xucheng Elec | -40℃~+125℃ | 1830 | 0.0648 | extended | Y | CHANGED |
| 2 Power | C2xx | 47 uF 50 V aluminium electrolytic SMD 6.3x7.7 | 2 | C970679 | RVT1H470M0607 47UF 50V | DMBJ | -55℃~+105℃ | 31920 | 0.0378 | extended | Y | NEW |
| 2 Power | C2xx | 1 uF 50 V X7R 0805 | 2 | C91185 | CC0805KKX7R9BB105 | YAGEO | see MPN datasheet | 154860 | 0.035 | extended | Y | CHANGED |
| 2 Power | C2xx | 22 uF 25 V X5R 0805 (URB output capacitor) | 3 | C45783 | CL21A226MAQNNNE | Samsung Electro-Mechan | see MPN datasheet | 118800 | 0.1851 | basic | Y | NEW |
| 2 Power | C2xx | 100 uF 100 V electrolytic radial (URB input capacitor) | 3 | C2960285 | 100V100uF CD288 | HRK | -40℃~+105℃ | 2075 | 0.094 | extended | Y | CHANGED |
| 3 MCU | C3xx | 2.2 uF 16 V X5R 0603 (VCAP) | 2 | C23630 | CL10A225KO8NNNC | Samsung Electro-Mechan | see MPN datasheet | 225750 | 0.012 | basic | Y | NEW |
| 3 MCU | C3xx | 4.7 uF 16 V X5R 0603 (bulk) | 1 | C19666 | CL10A475KO8NNNC | Samsung Electro-Mechan | see MPN datasheet | 1103370 | 0.0151 | basic | Y | NEW |
| 3 MCU | R3xx | 22 R 1% 0603 (clock series) | 2 | C23345 | 0603WAF220JT5E | UNI-ROYAL | -55℃~+155℃ | 2563300 | 0.0017 | basic | Y | NEW |
| 3 MCU | R3xx | 10 k 1% 0603 | 7 | C25804 | 0603WAF1002T5E | UNI-ROYAL | -55℃~+155℃ | 4409600 | 0.0024 | basic | Y | NEW |
| 3 MCU | R3xx | 1 k 1% 0603 (status LED resistors) | 5 | C21190 | 0603WAF1001T5E | UNI-ROYAL | -55℃~+155℃ | 2407100 | 0.0017 | basic | Y | NEW |
| all | C xx | 100 nF 50 V X7R 0603 | 40 | C1591 | CL10B104KB8NNNC | Samsung Electro-Mechan | see MPN datasheet | 1328900 | 0.0072 | extended | Y | CHANGED |
| 5 Inputs | U501-U505 | TLP290-4(GB) AC-input quad optocoupler SOP-16 | 5 | C39031 | TLP290-4(GB-TP,E | TOSHIBA | -55℃~+110℃ | 15749 | 0.545 | extended | Y | PLAN |
| 5 Inputs | R501-R520 | 4.7 k 1% 1206 (24 V input resistor) | 20 | C17936 | 1206W4F4701T5E | UNI-ROYAL | -55℃~+155℃ | 1252900 | 0.0078 | basic | Y | NEW |
| 5 Inputs | C501-C520 | 10 nF 50 V X7R 0603 (input filter) | 20 | C1589 | CL10B103KB8NNNC | Samsung Electro-Mechan | see MPN datasheet | 1850750 | 0.0075 | extended | Y | CHANGED |
| 5 Inputs | LED501-LED520 | Input state LED (yellow-green) 0603 | 20 | C89809 | NCD0603C3 | NATIONSTAR | -30℃~+85℃ | 20640 | 0.0261 | extended | Y | CHANGED |
| 5 Inputs | RN501-RN505 | 1 k x4 resistor array 0603 (LED resistors) | 5 | C20197 | 4D03WGJ0102T5E | UNI-ROYAL | see MPN datasheet | 336800 | 0.0096 | basic | Y | NEW |
| 5 Inputs | J501-J520 | Terminal header 3-pole 5.08 mm, one per input (+24V via PTC, IN, 0V) | 20 | C441205 | KF2EDGR-5.08-3P | Cixi Kefa Elec | -40℃~+105℃ | 23010 | 0.0634 | extended | Y | CHANGED |
| 5 Inputs | P501-P520 | Terminal plug 3-pole 5.08 mm | 20 | C440881 | KF2EDGK-5.08-3P-AA | Cixi Kefa Elec | -40℃~+105℃ | 25375 | 0.2848 | extended | Y | CHANGED |
| 5 Inputs | RT501-RT502 | PTC 0.5 A hold, 30 V, 1812 (sensor +24 V) | 2 | C151168 | 1812L050/30PR | Littelfuse | -40℃~+85℃ | 10620 | 0.1214 | extended | Y | NEW-FLAG |
| 5 Inputs | JP501-JP502 | COM jumper header 1x3 2.54 mm | 2 | C2937625 | PZ254V-11-03P | XFCN | -40℃~+105℃ | 1011340 | 0.0201 | extended | Y | NEW |
| 5 Inputs | JP501-JP502 | Jumper shunt 2.54 mm | 2 | C5305 | 2.54 | BOOMELE(Boom Precision | see MPN datasheet | 892550 | 0.0099 | extended | Y | NEW |
| 6 MPG | U601 | AM26LS32ACDRG4 quad line receiver SOIC-16 (0..70 C) | 1 | C6180 | AM26LS32ACDR | TI | 0℃~+70℃ | 49432 | 0.4765 | extended | Y | CHANGED |
| 6 MPG | U602 | CA-IS3742LN digital isolator 2 fwd + 2 rev SOIC-16 | 1 | C5347249 | CA-IS3742LN | Chipanalog | -40℃~+125℃ | 3174 | 0.8184 | extended | Y | PLAN |
| 6 MPG | J601 | Terminal header 6-pole 5.08 mm | 1 | C441208 | KF2EDGR-5.08-6P | Cixi Kefa Elec | -40℃~+105℃ | 2565 | 0.1251 | extended | Y | NEW |
| 6 MPG | P601 | Terminal plug 6-pole 5.08 mm | 1 | C440884 | KF2EDGK-5.08-6P | Cixi Kefa Elec | -40℃~+105℃ | 5698 | 0.5051 | extended | Y | NEW |
| 6 MPG | RT601 | PTC 0.25 A hold, 16 V, 1206 (+5V_IO to MPG) | 1 | C70068 | nSMD025 | TECHFUSE | -40℃~+85℃ | 11320 | 0.0403 | extended | Y | NEW |
| 6 MPG | D601-D602 | PSM712 TVS pair SOT-23 (one per A and B pair) | 2 | C32677 | PSM712-LF-T7 | PROTEK | -55℃~+150℃ | 60690 | 0.347 | basic | Y | NEW |
| 6 MPG | R6xx | 120 R 1% 0603 (line termination, not fitted) | 2 | C22787 | 0603WAF1200T5E | UNI-ROYAL | -55℃~+155℃ | 1002600 | 0.0017 | basic | DNP | NEW |
| 7 Relays | U701-U702 | CA-IS3740LN digital isolator 4 fwd SOIC-16 | 2 | C428888 | CA-IS3740LN | Chipanalog | -40℃~+125℃ | 2086 | 0.8184 | extended | Y | PLAN |
| 7 Relays | U703 | ULN2803A 8-ch Darlington driver SOP-18 | 1 | C845537 | ULN2803A | UMW | -40℃~+85℃ | 209205 | 0.2123 | extended | Y | CHANGED |
| 7 Relays | XK701-XK708 | Omron P2R-05P PCB relay socket | 8 | C1524860 | P2R-05P | OMRON | see MPN datasheet | 44 | 6.4839 | extended | Y | PLAN-FLAG |
| 7 Relays | K701-K708 | Omron G2R-1-S DC24 relay (buy locally in India) | 8 |  |  | Omron | -40..+70 C (plan, check) |  |  |  | DNP | LOCAL |
| 7 Relays | F701-F708 | Fuse block 5x20 mm PCB, Littelfuse 646 | 8 | C206887 | 64600001003 | Littelfuse | see MPN datasheet | 963 | 0.9428 | extended | Y | CHANGED |
| 7 Relays | F701-F708 + F201-F202 (cover) | Clear cover for the 646 fuse block (Littelfuse 648, polycarbonate) | 10 | C187509 | 64800001009 | Littelfuse | see MPN datasheet | 595 | 0.3258 | extended | Y | CHANGED |
| 7 Relays | F701-F708 (fuse) | Fuse 5x20 mm T5A 250 VAC ceramic (buy locally in India) | 8 |  |  | (local India) |  |  |  |  | DNP | LOCAL |
| 7 Relays | J701-J708 | Terminal header 3-pole 5.08 mm, one per relay (COM via fuse, NO, NC) | 8 | C441205 | KF2EDGR-5.08-3P | Cixi Kefa Elec | -40℃~+105℃ | 23010 | 0.0634 | extended | Y | CHANGED |
| 7 Relays | P701-P708 | Terminal plug 3-pole 5.08 mm | 8 | C440881 | KF2EDGK-5.08-3P-AA | Cixi Kefa Elec | -40℃~+105℃ | 25375 | 0.2848 | extended | Y | CHANGED |
| 7 Relays | LED701-LED708 | Relay ON LED (yellow-green) 0603 | 8 | C89809 | NCD0603C3 | NATIONSTAR | -30℃~+85℃ | 20640 | 0.0261 | extended | Y | CHANGED |
| 7 Relays | RN701-RN702 | 22 k x4 resistor array 0603 (LED series) | 2 | C25729 | 4D03WGJ0223T5E | UNI-ROYAL | see MPN datasheet | 8800 | 0.0076 | extended | Y | NEW |
| 7 Relays | RN703-RN704 | 100 k x4 resistor array 0603 (driver pull-downs) | 2 | C1996 | 4D03WGJ0104T5E | UNI-ROYAL | see MPN datasheet | 12650 | 0.0104 | extended | Y | NEW |
| 7 Relays | R7xx/C7xx | RC snubber across each contact (not fitted) | 8 |  |  |  |  |  |  |  | DNP | FOOTPRINT |
| 8 Analog | U801 | CA-IS3740HW wide-body isolator 4 fwd, default high | 1 | C528653 | CA-IS3740HW | Chipanalog | -40℃~+125℃ | 1872 | 0.913 | extended | Y | PLAN |
| 8 Analog | U802 | MCP4822-E/SN dual 12-bit DAC SOIC-8 | 1 | C16040 | MCP4822-E/SN | MICROCHIP | -40℃~+125℃ | 5994 | 2.4525 | extended | Y | PLAN |
| 8 Analog | U803 | LM2904DR dual op-amp SOIC-8 | 1 | C7934 | LM2904DR | TI | -40℃~+125℃ | 65350 | 0.0854 | extended | Y | PLAN |
| 8 Analog | U804 | L78L05ABUTR 5 V LDO SOT-89 (DAC supply) | 1 | C42738 | L78L05ABUTR | ST | -40℃~+125℃@(Tj) | 170580 | 0.0752 | extended | Y | NEW |
| 8 Analog | Q801 | 2N7002DW dual N-MOSFET SOT-363 (clamp) | 1 | C83571 | 2N7002DW-7-F | DIODES | -55℃~+150℃ | 97005 | 0.1146 | extended | Y | NEW |
| 8 Analog | D801-D802 | SMAJ15A TVS 15 V SMA (AO outputs) | 2 | C148216 | SMAJ15A | Littelfuse | -65℃~+150℃ | 15335 | 0.1533 | extended | Y | NEW |
| 8 Analog | R8xx | 14.7 k 0.1% thin film 0603 (gain) | 2 | C705725 | RT0603BRD0714K7L | YAGEO | -55℃~+155℃ | 35840 | 0.0423 | extended | Y | NEW |
| 8 Analog | R8xx | 10.0 k 0.1% thin film 0603 (gain) | 2 | C95204 | RT0603BRD0710KL | YAGEO | -55℃~+155℃ | 498980 | 0.0305 | extended | Y | NEW |
| 8 Analog | R8xx | 100 k 1% 0603 (input pull-down) | 2 | C25803 | 0603WAF1003T5E | UNI-ROYAL | -55℃~+155℃ | 7501200 | 0.003 | basic | Y | NEW |
| 8 Analog | R8xx | 100 R 1% 0603 (output series) | 2 | C22775 | 0603WAF1000T5E | UNI-ROYAL | -55℃~+155℃ | 1063000 | 0.0021 | basic | Y | NEW |
| 8 Analog | R8xx | 1 k 1% 0603 (DAC to op-amp) | 2 | C21190 | 0603WAF1001T5E | UNI-ROYAL | -55℃~+155℃ | 2407100 | 0.0017 | basic | Y | NEW |
| 8 Analog | C8xx | 1 uF 50 V X7R 0603 | 4 | C559769 | CC0603KRX7R9BB105 | YAGEO | see MPN datasheet | 609740 | 0.0569 | extended | Y | CHANGED |
| 8 Analog | C8xx | 10 nF 50 V X7R 0603 (AO output) | 2 | C1589 | CL10B103KB8NNNC | Samsung Electro-Mechan | see MPN datasheet | 1850750 | 0.0075 | extended | Y | CHANGED |
| 8 Analog | J801-J802 | Terminal header 2-pole 5.08 mm, one per output (AO, AGND) | 2 | C441204 | KF2EDGR-5.08-2P | Cixi Kefa Elec | -40℃~+105℃ | 47950 | 0.0468 | extended | Y | CHANGED |
| 8 Analog | P801-P802 | Terminal plug 2-pole 5.08 mm | 2 | C440880 | KF2EDGK-5.08-2P-AA | Cixi Kefa Elec | -40℃~+105℃ | 52875 | 0.1568 | extended | Y | CHANGED |
| 2 Power | J201 | Terminal header 4-pole 5.08 mm (24V entry) | 1 | C441206 | KF2EDGR-5.08-4P | Cixi Kefa Elec | -40℃~+105℃ | 6825 | 0.0861 | extended | Y | NEW |
| 2 Power | P201 | Terminal plug 4-pole 5.08 mm | 1 | C440882 | KF2EDGK-5.08-4P-AA | Cixi Kefa Elec | -40℃~+105℃ | 8450 | 0.3608 | extended | Y | NEW |
| 1 Root | J101 | PE screw terminal M3 PCB (Keystone 7770) | 1 | C5272782 | 7770 | Keystone | see MPN datasheet | 281 | 0.803 | extended | Y | NEW |
| 1 Root | J101 (screw) | M3 x 6 pan-head cross-slot screw for the PE terminal (M3 x 0.5) | 1 | C357543 | PM3X6 | Shuntian | see MPN datasheet | 34400 | 0.0027 | extended | Y | CHANGED |

`~` after a quantity = estimate. Temp is the LCSC 'Operating Temperature' field.
