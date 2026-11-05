#!/usr/bin/env python3
"""Build bom/parts.csv from the row table below, checking every LCSC number live.

For each row with an LCSC number the script fetches the LCSC product page data
(scripts/lcsc_lookup.py) and fills Manufacturer, MPN, package, temperature
rating, stock, qty-1 price and basic/extended library flag. It then checks that
the number really is the part we meant (`expect` substring must appear in the
LCSC model name) and prints every problem: unknown number, stock below the
quantity needed, or mismatch.

Usage:  python3 -I scripts/build_bom.py            # rewrite bom/parts.csv
        python3 -I scripts/build_bom.py --check    # validate only

Status column:
  PLAN       part and LCSC number exactly as in docs/plan.md, verified
  PLAN-FLAG  as in plan, but the check found something the owner should know
  CHANGED    deviation from docs/plan.md approved by the owner on 2026-11-05
             (recorded in the plan's Decisions log)
  DECISION   needs owner approval. Either a plan part with a problem (LCSC holds
             the PLAN number, Proposed_LCSC the replacement), or an addition that
             deviates from the plan (LCSC holds the proposed part). Nothing in
             docs/plan.md changes until approved.
  NEW        commodity part chosen in M1 (plan left it to M1)
  NEW-FLAG   commodity part chosen in M1 with an open question
  LOCAL      bought locally in India, not on LCSC (DNP in assembly BOM)
  FOOTPRINT  unfitted footprint only, value fixed at layout
"""
import csv
import datetime
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lcsc_lookup import fetch  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "bom", "parts.csv")

R0603 = "Resistor_SMD:R_0603_1608Metric"
R1206 = "Resistor_SMD:R_1206_3216Metric"
C0603 = "Capacitor_SMD:C_0603_1608Metric"
C0805 = "Capacitor_SMD:C_0805_2012Metric"
C1206 = "Capacitor_SMD:C_1206_3216Metric"
L0603 = "LED_SMD:LED_0603_1608Metric"
RA4 = "Resistor_SMD:R_Array_Convex_4x0603"

# Row fields:
# sheet, refs, description, qty, basis, footprint, lcsc, expect, fit, status,
# proposed, notes
#   basis: "fixed" (set by plan/sheet) or "est" (estimate, final count at schematic)
#   proposed: "LCSC-number" proposed replacement for DECISION rows
ROWS = [
    # ---------------------------------------------------------------- MCU
    ("3 MCU", "U301", "STM32F405RGT6 MCU LQFP-64", 1, "fixed", "Package_QFP:LQFP-64_10x10mm_P0.5mm",
     "C15742", "STM32F405RGT6", "Y", "PLAN-FLAG", "",
     "Plan says about $3.2; LCSC lists about $6.9 at qty 1 and only a few dozen in stock. Check price breaks and stock before the PCB order."),
    ("3 MCU", "X301", "25 MHz CMOS oscillator, 3.2x2.5 mm", 1, "fixed", "Oscillator:Oscillator_SMD_3.2x2.5mm",
     "C2595919", "ECS-3225MVQ-250-CN", "Y", "PLAN-FLAG", "",
     "Ordering code -CN decodes to +/-25 ppm, -40..+85 C (datasheet ordering table), meets the <= +/-50 ppm target. Datasheet note says +/-25 ppm is 'contact ECS for availability' and LCSC stock is under 100: confirm before ordering."),
    ("3 MCU", "J301", "SWD header 2x5 1.27 mm SMD", 1, "fixed", "Connector_PinHeader_1.27mm:PinHeader_2x05_P1.27mm_Vertical_SMD",
     "C3975188", "PZ127-2-05-S", "Y", "NEW", "", "PA13, PA14, PB3 SWO, NRST, 3V3, GND."),
    ("3 MCU", "J302", "USART2 header 1x3 2.54 mm", 1, "fixed", "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical",
     "C2937625", "PZ254V-11-03P", "Y", "NEW", "", "PA2/PA3 + GND. Same part as the two COM jumper headers."),
    ("3 MCU", "FB301", "Ferrite bead 600R@100MHz 0603 (VDDA)", 1, "fixed", "Inductor_SMD:L_0603_1608Metric",
     "C19330", "BLM18AG601SN1D", "Y", "NEW", "",
     "VDDA filter. Murata, 500 mA. (Sunlord C1002 is basic but has no LCSC product page, so its stock cannot be checked.)"),
    ("3 MCU", "LED301", "Heartbeat LED yellow 0603", 1, "fixed", L0603,
     "C2287", "KT-0603Y", "Y", "NEW", "", "PA1."),
    # ----------------------------------------------------------- EtherCAT
    ("4 EtherCAT", "U401", "LAN9252I/PT EtherCAT slave controller TQFP-64", 1, "fixed", "Package_QFP:TQFP-64_10x10mm_P0.5mm",
     "C80933", "LAN9252I", "Y", "PLAN", "", ""),
    ("4 EtherCAT", "U402", "24LC32AT-I/SN EEPROM 32 Kbit SOIC-8", 1, "fixed", "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm",
     "C615715", "24LC32AT-I/SN", "Y", "PLAN", "", "ESI EEPROM."),
    ("4 EtherCAT", "J401-J402", "RJ45 jack with integrated magnetics and LEDs", 2, "fixed", "TBD lcsc.pretty (M2)",
     "C69427", "HY911105AE", "Y", "PLAN", "",
     "Datasheet checked: 1CT:1CT magnetics, green + yellow LEDs, 1500 Vrms, -40..+85 C. Image-only PDF, so magnetics wiring is re-read in M2/M4."),
    ("4 EtherCAT", "LED401-LED402", "EtherCAT RUN LED (yellow-green) 0603", 1, "fixed", L0603,
     "C89809", "NCD0603C3", "Y", "CHANGED", "",
     "Yellow-green accepted 2026-11-05 in place of 'green': no ~2 V green exists on LCSC and emerald-green (Vf 2.6-3.6 V) may not light from 3.3 V through 1 kOhm."),
    ("4 EtherCAT", "LED403", "EtherCAT ERR LED red 0603", 1, "fixed", L0603,
     "C2286", "KT-0603R", "Y", "NEW", "", ""),
    ("4 EtherCAT", "R4xx", "49.9 R 1% 0603 (LAN9252 TX/RX termination)", 8, "est", R0603,
     "C23185", "0603WAF499JT5E", "Y", "NEW", "", "Estimate; exact count set in M4 against the EVB-LAN9252-SPI reference."),
    ("4 EtherCAT", "R4xx", "12.1 k 1% 0603 (RBIAS)", 1, "fixed", R0603,
     "C22864", "0603WAF1212T5E", "Y", "NEW", "", "Extended part (no basic 12.1 k)."),
    ("4 EtherCAT", "R4xx", "4.7 k 1% 0603 (EEPROM pull-ups)", 2, "fixed", R0603,
     "C23162", "0603WAF4701T5E", "Y", "NEW", "", ""),
    ("4 EtherCAT", "R4xx", "1 M 1% 0603 (shield bleed)", 1, "fixed", R0603,
     "C22935", "0603WAF1004T5E", "Y", "NEW", "", "In parallel with the 1 nF/2 kV cap, shield to PE."),
    ("4 EtherCAT", "C4xx", "1 nF 2 kV X7R 1206 (shield to PE)", 1, "fixed", C1206,
     "C9196", "1206B102K202NT", "Y", "NEW", "", ""),
    # -------------------------------------------------------------- Power
    ("2 Power", "U201", "URB2403S-6WR3 isolated DC-DC 24V to 3.3V 1.35 A", 1, "fixed", "TBD lcsc.pretty (M2)",
     "C5369843", "URB2403S-6WR3", "Y", "PLAN-FLAG", "",
     "Datasheet: absolute max input 40 V ('exceeding may cause permanent damage'). SMBJ33A clamps at 53.3 V, above that. See PR notes."),
    ("2 Power", "U202", "URB2405S-6WR3 isolated DC-DC 24V to 5V 1.2 A", 1, "fixed", "TBD lcsc.pretty (M2)",
     "C3031185", "URB2405S-6WR3", "Y", "PLAN-FLAG", "", "Same 40 V input maximum."),
    ("2 Power", "U203", "URB2415S-6WR3 isolated DC-DC 24V to 15V 0.4 A", 1, "fixed", "TBD lcsc.pretty (M2)",
     "C5369844", "URB2415S-6WR3", "Y", "PLAN-FLAG", "",
     "LCSC rates -40..+105 C (plan said 'check datasheet'). Same 40 V input maximum; stock about 100."),
    ("2 Power", "D201-D202", "SMBJ33A TVS 600 W, 33 V stand-off, SMB", 2, "fixed", "Diode_SMD:D_SMB",
     "C320242", "SMBJ33A", "Y", "PLAN-FLAG", "",
     "Vc = 53.3 V at 11.3 A, above the URB modules' 40 V input maximum. Decision 2026-11-05: keep the part, design module-side limiting on the power sheet in M3 and bring it for approval."),
    ("2 Power", "D203-D204", "SS54 Schottky 40 V 5 A SMA (reverse polarity)", 2, "fixed", "Diode_SMD:D_SMA",
     "C22452", "SS54", "Y", "NEW", "", "Basic part. 40 V reverse rating vs 28.8 V max input."),
    ("2 Power", "F201-F202", "Fuse holder 5x20 mm PCB with cover (24V_LOGIC, 24V_IO)", 2, "fixed", "TBD lcsc.pretty (M2)",
     "C58066", "C58066", "Y", "CHANGED", "",
     "Owner chose replaceable 5x20 fuses for the two 24 V inputs (2026-11-05). Same holder as the relay fuses; 80 C limit accepted."),
    ("2 Power", "F201", "Fuse 5x20 mm 1 A 250 V glass (24V_LOGIC)", 1, "fixed", "n/a (in holder)",
     "C3116", "5F.1000210000R1", "Y", "CHANGED", "",
     "Fitted at assembly (cheap, on LCSC). 5F series = fast-acting; confirm blow characteristic vs inrush into 47 uF at M3."),
    ("2 Power", "F202", "Fuse 5x20 mm 3 A 250 V glass (24V_IO)", 1, "fixed", "n/a (in holder)",
     "C3118", "5G.3000210000S1", "Y", "CHANGED", "",
     "Fitted at assembly. Confirm blow characteristic at M3."),
    ("2 Power", "C2xx", "47 uF 50 V aluminium electrolytic SMD 6.3x7.7", 2, "fixed", "Capacitor_SMD:CP_Elec_6.3x7.7",
     "C970679", "RVT1H470M0607", "Y", "NEW", "", "One per 24 V input."),
    ("2 Power", "C2xx", "1 uF 50 V X7R 0805", 2, "fixed", C0805,
     "C28323", "CL21B105KBFNNNE", "Y", "NEW", "", "One per 24 V input."),
    ("2 Power", "C2xx", "22 uF 25 V X5R 0805 (URB output capacitor)", 3, "fixed", C0805,
     "C45783", "CL21A226MAQNNNE", "Y", "NEW", "",
     "Datasheet Cout: 22 uF/16 V for 3.3 V and 5 V, 22 uF/25 V for 15 V. One 25 V part covers all three."),
    ("2 Power", "C2xx", "100 uF 100 V electrolytic radial (URB input capacitor)", 3, "fixed", "Capacitor_THT:CP_Radial_D10.0mm_P5.00mm",
     "C2960285", "100V100uF", "Y", "CHANGED", "",
     "Approved 2026-11-05. URB datasheet (Fig. 2/3) recommends Cin 100 uF/100 V per module on a 24 V input. 10 mm diameter radial: reserve layout space."),
    # ---------------------------------------------------------------- MCU passives
    ("3 MCU", "C3xx", "2.2 uF 16 V X5R 0603 (VCAP)", 2, "fixed", C0603,
     "C23630", "CL10A225KO8NNNC", "Y", "NEW", "", ""),
    ("3 MCU", "C3xx", "4.7 uF 16 V X5R 0603 (bulk)", 3, "est", C0603,
     "C19666", "CL10A475KO8NNNC", "Y", "NEW", "", "STM32 bulk plus LAN9252 supply; final count at schematic."),
    ("3 MCU", "C3xx", "10 uF 10 V X5R 0603", 4, "est", C0603,
     "C19702", "CL10A106KP8NNNC", "Y", "NEW", "", "Per LAN9252 reference in M4."),
    ("3 MCU", "R3xx", "22 R 1% 0603 (clock series)", 2, "fixed", R0603,
     "C23345", "0603WAF220JT5E", "Y", "NEW", "", "Oscillator to PH0 and to LAN9252 OSCI."),
    ("3 MCU", "R3xx", "10 k 1% 0603", 10, "est", R0603,
     "C25804", "0603WAF1002T5E", "Y", "NEW", "",
     "BOOT0, PD2 pull-down, PB14 and PC5 pull-ups, LAN9252 straps. Final count at schematic."),
    ("3 MCU", "R3xx", "1 k 1% 0603 (status LED resistors)", 7, "est", R0603,
     "C21190", "0603WAF1001T5E", "Y", "NEW", "", "Heartbeat, RUN, ERR and four jack LEDs."),
    ("all", "C xx", "100 nF 50 V X7R 0603", 45, "est", C0603,
     "C14663", "CC0603KRX7R9BB104", "Y", "NEW", "",
     "Estimate: 6 on STM32, 1 NRST, about 10 LAN9252, 2 per isolator package x4, oscillator, EEPROM, DAC, op-amp, 78L05. Exact count at schematic."),
    # ------------------------------------------------------ Digital inputs (x5)
    ("5 Inputs", "U501-U505", "TLP290-4(GB) AC-input quad optocoupler SOP-16", 5, "fixed", "Package_SO:SOP-16_4.4x10.4mm_P1.27mm",
     "C39031", "TLP290-4", "Y", "PLAN", "", "Datasheet input type AC/DC, -55..+110 C, 2.5 kV."),
    ("5 Inputs", "R501-R520", "4.7 k 1% 1206 (24 V input resistor)", 20, "fixed", R1206,
     "C17936", "1206W4F4701T5E", "Y", "NEW", "", "0.16 W worst case of 0.25 W."),
    ("5 Inputs", "C501-C520", "10 nF 50 V X7R 0603 (input filter)", 20, "fixed", C0603,
     "C57112", "0603B103K500NT", "Y", "NEW", "", "Basic part."),
    ("5 Inputs", "LED501-LED520", "Input state LED (yellow-green) 0603", 20, "fixed", L0603,
     "C89809", "NCD0603C3", "Y", "CHANGED", "", "Yellow-green accepted (see RUN LED)."),
    ("5 Inputs", "RN501-RN505", "1 k x4 resistor array 0603 (LED resistors)", 5, "fixed", RA4,
     "C20197", "4D03WGJ0102T5E", "Y", "NEW", "", "Basic part."),
    ("5 Inputs", "J501", "Terminal header 10-pole 5.08 mm (DI1-8)", 1, "fixed", "TBD lcsc.pretty (M2)",
     "C441201", "KF2EDGR-5.08-10P", "Y", "PLAN-FLAG", "", "Stock under 100: order early or use a second source."),
    ("5 Inputs", "P501", "Terminal plug 10-pole 5.08 mm", 1, "fixed", "TBD lcsc.pretty (M2)",
     "C440877", "KF2EDGK-5.08-10P", "Y", "NEW", "", ""),
    ("5 Inputs", "J502", "Terminal header 14-pole 5.08 mm (SEL1-12), Dorabo", 1, "fixed", "TBD lcsc.pretty (M2)",
     "C430493", "DB2ER-5.08-14P", "Y", "DECISION", "C430493",
     "Plan family (Cixi KF2EDG) has the 14-pole plug at stock 1 (C976408). Proposal: use the Dorabo DB2 14-pole pair for this one size so plug and header are the same family."),
    ("5 Inputs", "P502", "Terminal plug 14-pole 5.08 mm, Dorabo", 1, "fixed", "TBD lcsc.pretty (M2)",
     "C430477", "DB2EK-5.08-14P", "Y", "DECISION", "C430477", "See J502."),
    ("5 Inputs", "RT501-RT502", "PTC 0.5 A hold, 30 V, 1812 (sensor +24 V)", 2, "fixed", "Fuse:Fuse_1812_4532Metric",
     "C151168", "1812L050/30PR", "Y", "NEW-FLAG", "",
     "0.5 A hold / 1 A trip, 30 V max vs 28.8 V input, thin margin. One per input terminal (DI, SEL)."),
    ("5 Inputs", "JP501-JP502", "COM jumper header 1x3 2.54 mm", 2, "fixed", "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical",
     "C2937625", "PZ254V-11-03P", "Y", "NEW", "", "One for DI, one for SEL."),
    ("5 Inputs", "JP501-JP502", "Jumper shunt 2.54 mm", 2, "fixed", "n/a (loose)",
     "C5305", "2.54", "Y", "NEW", "", "Fitted shunt on each COM header."),
    # ----------------------------------------------------------------- MPG
    ("6 MPG", "U601", "AM26LS32ACDRG4 quad line receiver SOIC-16 (0..70 C)", 1, "fixed", "Package_SO:SOIC-16_3.9x9.9mm_P1.27mm",
     "C6180", "AM26LS32ACDR", "Y", "CHANGED", "",
     "Approved 2026-11-05. Plan number C2671811 (AM26LS32ACDRG4) has zero stock; C6180 is the same TI part and pinout, 0..70 C, SOIC-16."),
    ("6 MPG", "U602", "CA-IS3742LN digital isolator 2 fwd + 2 rev SOIC-16", 1, "fixed", "Package_SO:SOIC-16_3.9x9.9mm_P1.27mm",
     "C5347249", "CA-IS3742LN", "Y", "PLAN", "", "Default output low, -40..+125 C."),
    ("6 MPG", "J601", "Terminal header 6-pole 5.08 mm", 1, "fixed", "TBD lcsc.pretty (M2)",
     "C441208", "KF2EDGR-5.08-6P", "Y", "NEW", "", ""),
    ("6 MPG", "P601", "Terminal plug 6-pole 5.08 mm", 1, "fixed", "TBD lcsc.pretty (M2)",
     "C440884", "KF2EDGK-5.08-6P", "Y", "NEW", "", ""),
    ("6 MPG", "RT601", "PTC 0.25 A hold, 16 V, 1206 (+5V_IO to MPG)", 1, "fixed", "Fuse:Fuse_1206_3216Metric",
     "C70068", "nSMD025", "Y", "NEW", "", "0.25 A hold / 0.5 A trip."),
    ("6 MPG", "D601-D602", "PSM712 TVS pair SOT-23 (one per A and B pair)", 2, "fixed", "Package_TO_SOT_SMD:SOT-23",
     "C32677", "PSM712-LF-T7", "Y", "NEW", "", "RS-485 class asymmetric clamp (-7/+12 V), basic part."),
    ("6 MPG", "R6xx", "120 R 1% 0603 (line termination, not fitted)", 2, "fixed", R0603,
     "C22787", "0603WAF1200T5E", "DNP", "NEW", "", "Footprints left unfitted per plan."),
    # --------------------------------------------------------------- Relays
    ("7 Relays", "U701-U702", "CA-IS3740LN digital isolator 4 fwd SOIC-16", 2, "fixed", "Package_SO:SOIC-16_3.9x9.9mm_P1.27mm",
     "C428888", "CA-IS3740LN", "Y", "PLAN", "", "Default output low."),
    ("7 Relays", "U703", "ULN2803A 8-ch Darlington driver SOP-18", 1, "fixed", "Package_SO:SOIC-18W_7.5x11.6mm_P1.27mm",
     "C845537", "ULN2803A", "Y", "CHANGED", "",
     "Approved 2026-11-05. Plan number C181731 (Mixic) has zero stock; C845537 is UMW ULN2803A, SOP-18-300mil, -40..+85 C. Pin-check against its datasheet in M2."),
    ("7 Relays", "XK701-XK708", "Omron P2R-05P PCB relay socket", 8, "fixed", "TBD lcsc.pretty (M2)",
     "C1524860", "P2R-05P", "Y", "PLAN-FLAG", "", "Stock 44 (need 8 per board). Plan allows Mouser/DigiKey if LCSC runs out."),
    ("7 Relays", "K701-K708", "Omron G2R-1-S DC24 relay (buy locally in India)", 8, "fixed", "n/a (plugs into socket)",
     "", "G2R-1-S DC24", "DNP", "LOCAL", "", "Not on the assembly line. Rating: -40..+70 C per plan, confirm against the Omron datasheet."),
    ("7 Relays", "F701-F708", "Fuse holder 5x20 mm PCB with cover", 8, "fixed", "TBD lcsc.pretty (M2)",
     "C58066", "C58066", "Y", "PLAN-FLAG", "",
     "Datasheet: ABS base, polystyrene cover, 6-10 A 250 VAC, and 'temperature resistance 80 C'. That equals the top of the enclosure range and a 5 A fuse adds self-heating. Fallback in plan: Littelfuse 649 series (Mouser). Owner: accept or switch."),
    ("7 Relays", "F701-F708 (fuse)", "Fuse 5x20 mm T5A 250 VAC ceramic (buy locally in India)", 8, "fixed", "n/a (in holder)",
     "", "T5A 250V 5x20 ceramic", "DNP", "LOCAL", "", "Not on the assembly line."),
    ("7 Relays", "J701-J702", "Terminal header 8-pole 5.08 mm (relay contacts)", 2, "fixed", "TBD lcsc.pretty (M2)",
     "C441210", "KF2EDGR-5.08-8P", "Y", "NEW", "", "300 V rated; mains clearance handled at layout."),
    ("7 Relays", "P701-P702", "Terminal plug 8-pole 5.08 mm", 2, "fixed", "TBD lcsc.pretty (M2)",
     "C440886", "KF2EDGK-5.08-8P", "Y", "PLAN", "", ""),
    ("7 Relays", "LED701-LED708", "Relay ON LED (yellow-green) 0603", 8, "fixed", L0603,
     "C89809", "NCD0603C3", "Y", "CHANGED", "", "Yellow-green accepted (see RUN LED)."),
    ("7 Relays", "RN701-RN702", "22 k x4 resistor array 0603 (LED series)", 2, "fixed", RA4,
     "C25729", "4D03WGJ0223T5E", "Y", "NEW", "", ""),
    ("7 Relays", "RN703-RN704", "100 k x4 resistor array 0603 (driver pull-downs)", 2, "fixed", RA4,
     "C1996", "4D03WGJ0104T5E", "Y", "NEW", "", ""),
    ("7 Relays", "R7xx/C7xx", "RC snubber across each contact (not fitted)", 8, "fixed", "TBD at layout",
     "", "", "DNP", "FOOTPRINT", "", "Footprint only (resistor + X-class capacitor). Values chosen in M5/layout."),
    # --------------------------------------------------------------- Analog
    ("8 Analog", "U801", "CA-IS3740HW wide-body isolator 4 fwd, default high", 1, "fixed", "Package_SO:SOIC-16W_7.5x10.3mm_P1.27mm",
     "C528653", "CA-IS3740HW", "Y", "PLAN", "", "Default output HIGH (verified on LCSC page); 5 kVrms."),
    ("8 Analog", "U802", "MCP4822-E/SN dual 12-bit DAC SOIC-8", 1, "fixed", "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm",
     "C16040", "MCP4822", "Y", "PLAN", "", ""),
    ("8 Analog", "U803", "LM2904DR dual op-amp SOIC-8", 1, "fixed", "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm",
     "C7934", "LM2904", "Y", "PLAN", "", ""),
    ("8 Analog", "U804", "L78L05ABUTR 5 V LDO SOT-89 (DAC supply)", 1, "fixed", "Package_TO_SOT_SMD:SOT-89-3",
     "C42738", "L78L05AB", "Y", "NEW", "", "-40..+125 C, 100 mA, input to 30 V."),
    ("8 Analog", "Q801", "2N7002DW dual N-MOSFET SOT-363 (clamp)", 1, "fixed", "Package_TO_SOT_SMD:SOT-363_SC-70-6",
     "C83571", "2N7002DW", "Y", "NEW", "", "One package shorts both op-amp inputs."),
    ("8 Analog", "D801-D802", "SMAJ15A TVS 15 V SMA (AO outputs)", 2, "fixed", "Diode_SMD:D_SMA",
     "C148216", "SMAJ15A", "Y", "NEW", "", ""),
    ("8 Analog", "R8xx", "14.7 k 0.1% thin film 0603 (gain)", 2, "fixed", R0603,
     "C705725", "RT0603BRD0714K7L", "Y", "NEW", "", "0.1%, 25 ppm/C."),
    ("8 Analog", "R8xx", "10.0 k 0.1% thin film 0603 (gain)", 2, "fixed", R0603,
     "C95204", "RT0603BRD0710KL", "Y", "NEW", "", "0.1%, 25 ppm/C."),
    ("8 Analog", "R8xx", "100 k 1% 0603 (input pull-down)", 2, "fixed", R0603,
     "C25803", "0603WAF1003T5E", "Y", "NEW", "", ""),
    ("8 Analog", "R8xx", "100 R 1% 0603 (output series)", 2, "fixed", R0603,
     "C22775", "0603WAF1000T5E", "Y", "NEW", "", ""),
    ("8 Analog", "R8xx", "1 k 1% 0603 (DAC to op-amp)", 2, "fixed", R0603,
     "C21190", "0603WAF1001T5E", "Y", "NEW", "", ""),
    ("8 Analog", "C8xx", "1 uF 50 V X5R 0603", 6, "est", C0603,
     "C15849", "CL10A105KB8NNNC", "Y", "NEW", "", "VDDA, 78L05 in/out, URB Cout0 and others; final count at schematic."),
    ("8 Analog", "C8xx", "10 nF 50 V X7R 0603 (AO output)", 2, "fixed", C0603,
     "C57112", "0603B103K500NT", "Y", "NEW", "", ""),
    ("8 Analog", "J801", "Terminal header 3-pole 5.08 mm (AO1, AO2, AGND)", 1, "fixed", "TBD lcsc.pretty (M2)",
     "C441205", "KF2EDGR-5.08-3P", "Y", "NEW", "", ""),
    ("8 Analog", "P801", "Terminal plug 3-pole 5.08 mm", 1, "fixed", "TBD lcsc.pretty (M2)",
     "C440881", "KF2EDGK-5.08-3P", "Y", "NEW", "", ""),
    # --------------------------------------------------------- Power terminal / PE
    ("2 Power", "J201", "Terminal header 4-pole 5.08 mm (24V entry)", 1, "fixed", "TBD lcsc.pretty (M2)",
     "C441206", "KF2EDGR-5.08-4P", "Y", "NEW", "", ""),
    ("2 Power", "P201", "Terminal plug 4-pole 5.08 mm", 1, "fixed", "TBD lcsc.pretty (M2)",
     "C440882", "KF2EDGK-5.08-4P", "Y", "NEW", "", ""),
    ("1 Root", "J101", "PE screw terminal M3 PCB (Keystone 7770)", 1, "fixed", "TBD lcsc.pretty (M2)",
     "C5272782", "7770", "Y", "NEW", "", "Takes an M3 ring lug; also the shield-to-PE point."),
]

# Test points and mounting holes are footprints only, no purchased part.
FOOTPRINT_ONLY_NOTE = "Test points (rails, OE, AO_CLAMP, SPI, MPG A/B, PH1) and mounting holes are bare pads/holes: no part, no LCSC number."

COLUMNS = [
    "Sheet", "RefGroup", "Description", "Qty", "Qty_basis", "Footprint",
    "LCSC", "MPN", "Manufacturer", "Package_LCSC", "Temp_range", "Stock",
    "Price_USD_qty1", "Library", "Fit", "Status", "Proposed_LCSC", "Notes",
    "Checked",
]


def build():
    today = datetime.date.today().isoformat()
    cache = {}
    problems = []
    out = []

    def get(code):
        if code not in cache:
            cache[code] = fetch(code)
        return cache[code]

    for (sheet, refs, desc, qty, basis, fp, lcsc, expect, fit, status,
         proposed, notes) in ROWS:
        mpn = mfr = pkg = temp = lib = ""
        stock = price = ""
        if lcsc:
            r = get(lcsc)
            if r is None:
                problems.append(f"{lcsc} ({desc}): NOT FOUND on LCSC")
            else:
                mpn = r.get("productModel") or ""
                mfr = r.get("brandNameEn") or ""
                pkg = r.get("encapStandard") or ""
                params = {p.get("paramNameEn"): p.get("paramValueEn")
                          for p in (r.get("paramVOList") or [])}
                temp = params.get("Operating Temperature") or ""
                lib = "basic" if r.get("smtLabel") == "BASE" else "extended"
                stock = r.get("stockNumber")
                ladder = r.get("productPriceList") or []
                price = ladder[0]["usdPrice"] if ladder else ""
                if expect and expect.lower().replace(" ", "") not in mpn.lower().replace(" ", ""):
                    problems.append(
                        f"{lcsc} ({desc}): LCSC model '{mpn}' does not contain '{expect}'")
                if stock is not None and stock < qty:
                    problems.append(
                        f"{lcsc} ({desc}): stock {stock} < qty needed {qty}")
                elif stock is not None and stock < 10 * qty and status != "DECISION":
                    problems.append(
                        f"{lcsc} ({desc}): LOW stock {stock} for qty {qty}")
        if lcsc == "C2671811":
            temp = temp or "0..+70 C (plan; not shown on LCSC page)"
        if not temp and lcsc:
            temp = "see MPN datasheet"
        if status == "LOCAL":
            mfr = "Omron" if "G2R" in expect else "(local India)"
            temp = "-40..+70 C (plan, check)" if "G2R" in expect else ""
        if proposed and proposed != lcsc:
            r = get(proposed)
            if r is None:
                problems.append(f"proposed {proposed}: NOT FOUND")
        if proposed and proposed == lcsc:
            # DECISION row where the LCSC column already holds the proposal
            pass
        out.append([sheet, refs, desc, qty, basis, fp, lcsc, mpn, mfr, pkg,
                    temp, stock, price, lib, fit, status, proposed, notes, today])
    return out, problems, cache


REVIEW = os.path.join(ROOT, "docs", "review", "M1-parts.md")

CROSS_CUTTING = """\
Decided by the owner on 2026-11-05 (status CHANGED in the list, recorded in `docs/plan.md` Decisions log):

- MPG receiver: C2671811 (zero stock) replaced by **C6180 AM26LS32ACDR**.
- Relay driver: C181731 (zero stock) replaced by **C845537 UMW ULN2803A**.
- Module input capacitors: **3 x 100 uF/100 V** added, per the URB datasheet.
- Status LEDs: **yellow-green NCD0603C3** accepted in place of green.
- 24 V input fuses: **replaceable 5x20 mm fuses** (same covered holder as the relay fuses, 1 A and 3 A glass fuses on LCSC) instead of SMD fuses.
- Relay fuse holder: **C58066 kept** (80 C limit accepted).
- Terminals: **7 sets** as the sheets need them (the plan's "9 sets" was a miscount).
- SMBJ33A vs the URB 40 V input maximum: **parts kept, module-side limiting designed in M3** and brought for approval.

Still open:

1. **14-pole terminal.** Plan family has the plug at stock 1 (C976408). The list carries the Dorabo DB2 pair (C430477 + C430493, status DECISION) so plug and header match. Say yes or no.
2. **STM32F405RGT6 price.** About $6.9 at qty 1 on LCSC (plan: about $3.2), about 54 in stock. Information only.
3. **PTC margins.** The 0.5 A sensor PTC is rated 30 V against a 28.8 V maximum input. Information only.
4. **Estimated counts.** Rows with Qty_basis = est (100 nF, 10 uF, 4.7 uF, 10 k, 1 k, 49.9 R, 1 uF) are estimates; exact counts come from the schematic sheets.
"""


def render_md(rows, problems):
    idx = {c: i for i, c in enumerate(COLUMNS)}
    today = rows[0][idx["Checked"]] if rows else ""
    L = []
    L.append("# M1 - Parts list for review\n")
    L.append(f"Stock and prices checked live on LCSC on {today} (qty-1 USD). Source of truth: `bom/parts.csv`, rebuilt and re-validated by `scripts/build_bom.py`. ERC and PDF do not apply to M1 (no schematic yet).\n")
    L.append("## Still needs your decision\n")
    L.append("| Part | Plan LCSC | Proposed LCSC | Why |\n|---|---|---|---|")
    for r in rows:
        if r[idx["Status"]] == "DECISION":
            L.append(f"| {r[idx['Description']]} | {r[idx['LCSC']]} | {r[idx['Proposed_LCSC']]} | {r[idx['Notes']]} |")
    L.append("\n## Other things the checks found\n")
    L.append(CROSS_CUTTING)
    L.append("## Part-level flags\n")
    L.append("| Part | LCSC | Stock | Note |\n|---|---|---|---|")
    for r in rows:
        if r[idx["Status"]] in ("PLAN-FLAG", "NEW-FLAG"):
            L.append(f"| {r[idx['Description']]} | {r[idx['LCSC']]} | {r[idx['Stock']]} | {r[idx['Notes']]} |")
    L.append("\n## Not on LCSC (bought locally in India or unfitted)\n")
    for r in rows:
        if r[idx["Status"]] in ("LOCAL", "FOOTPRINT"):
            L.append(f"- {r[idx['Description']]} x{r[idx['Qty']]}: {r[idx['Notes']]}")
    L.append(f"- {FOOTPRINT_ONLY_NOTE}")
    L.append("\n## Full list\n")
    L.append("Status: PLAN = exactly as in the plan, verified; NEW = commodity part chosen in M1; *-FLAG = see flags above; CHANGED = approved deviation from the plan; DECISION = still needs approval; LOCAL / FOOTPRINT = not purchased through LCSC.\n")
    L.append("| Sheet | Refs | Description | Qty | LCSC | MPN | Mfr | Temp | Stock | $ | Lib | Fit | Status |\n|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        q = f"{r[idx['Qty']]}{'~' if r[idx['Qty_basis']] == 'est' else ''}"
        L.append("| " + " | ".join(str(x).replace("|", "/") for x in (
            r[idx["Sheet"]], r[idx["RefGroup"]], r[idx["Description"]], q, r[idx["LCSC"]],
            r[idx["MPN"]], r[idx["Manufacturer"]][:22], r[idx["Temp_range"]], r[idx["Stock"]],
            r[idx["Price_USD_qty1"]], r[idx["Library"]], r[idx["Fit"]], r[idx["Status"]])) + " |")
    L.append("\n`~` after a quantity = estimate. Temp is the LCSC 'Operating Temperature' field.\n")
    return "\n".join(L)


def main():
    check_only = "--check" in sys.argv
    rows, problems, cache = build()
    if not check_only:
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        with open(OUT, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(COLUMNS)
            w.writerows(rows)
        print(f"wrote {OUT}: {len(rows)} rows")
        os.makedirs(os.path.dirname(REVIEW), exist_ok=True)
        with open(REVIEW, "w", encoding="utf-8") as f:
            f.write(render_md(rows, problems))
        print(f"wrote {REVIEW}")
    total = sum(r[3] * (r[12] or 0) for r in rows if r[14] == "Y" and r[12] != "")
    lines = sum(r[3] for r in rows if r[14] == "Y")
    print(f"fitted parts: {lines} pieces, qty-1 prices sum to about ${total:.2f} per board (excludes DNP/local)")
    print(FOOTPRINT_ONLY_NOTE)
    if problems:
        print("\nPROBLEMS:")
        for p in problems:
            print(" -", p)
    return 1 if any("NOT FOUND" in p or "does not contain" in p for p in problems) else 0


if __name__ == "__main__":
    sys.exit(main())
