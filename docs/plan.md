# EtherCAT I/O Slave — KiCad Schematic Plan

Approved 2026-11-05 · Aditya · Source: [Claude Doc](https://claude.ai/artifact/WW8mG2cyG7rtkuy5Czw53n)

## Scope and goals

The KiCad schematic turns the proven trial board into one chip-level board, with a new pin map for new firmware. It carries the full I/O count from the [trial board plan](https://claude.ai/artifact/REAKGojGbtDhU4pXJapQXB), aimed at 0–80 °C inside the enclosure as a reference, and every part has an LCSC number.

| Function | Final board requirement |
| --- | --- |
| Digital inputs | 8 × 24 VDC, PNP/NPN by one COM jumper, IEC 61131-2 Type 1/3 |
| MPG selector inputs | 12 × 24 VDC, dry contact or 24 V switch, enough for a 4-axis or 6-axis pendant |
| MPG | 5 V differential A/A̅/B/B̅, ≤ 20 kHz, 5 V fed from the field side |
| Relay outputs | 8 × pluggable relay (Omron G2R-1-S in P2R-05P socket), 230 VAC / 5 A NO, fuse and LED per channel, all OFF on EtherCAT loss |
| Analog outputs | 2 × 0–10 V, 12-bit, ±1 % FS after calibration, ≥ 2 kΩ load, 0 V at power-up and on loss |
| EtherCAT | LAN9252 over SPI, 2 ports, 1 ms cycle, IRQ and Distributed Clocks sync wired to the MCU |
| Power | Separate 24V_LOGIC and 24V_IO inputs, 24 VDC ±20 % |
| Mounting | DIN rail, pluggable 5.08 mm terminals, 0–80 °C inside the enclosure (reference, not a hard limit) |

The deliverable of this plan is a KiCad project whose schematic passes ERC, has an LCSC part number on every fitted part, and is laid out sheet by sheet the way a PCB engineer would hand it to layout.

## Design rules

These rules keep the part count low without giving up the industrial requirements. Claude Code applies them to every sheet.

- **One package per function group.** Quad AC-input optocouplers (4 inputs each), one octal relay driver, quad digital isolators, a dual DAC and a dual op-amp. No per-channel discrete transistors.
- **Isolated modules, not discrete converters.** Each isolated rail is one module plus its input and output capacitors. No flyback transformer, controller or feedback loop to design.
- **MCU.** STM32F405VGT6 in LQFP-100 (changed from the LQFP-64 RGT6 on 2026-11-06, see the Decisions log): the same F4 core, 168 MHz and 1 MB flash as the DISC1 chip, 82 I/O, about $7.6 at lcsc.com. Firmware is new, so the pin map is new too (MCU sheet). Clock: one 25 MHz oscillator feeds both the STM32 and the LAN9252, so firmware sets PLL M = 25.
- **Fail-safe in hardware.** Outputs drop if the MCU hangs or EtherCAT stops, without relying on firmware alone (see the relay output sheet).
- **Temperature grade.** 0–80 °C inside the enclosure is a reference, not a hard limit. Prefer −40 to +85 °C parts where they cost about the same; 0–70 °C parts such as the MPG line receiver and the G2R-1-S relay are acceptable.
- **Sourcing order.** LCSC first. Mouser or element14 only when LCSC has no part with the required rating, and the BOM row says why. Relays and contact fuses are bought locally in India for service.
- **Passive sizes.** 0603 for logic, 1206 for the 24 V input resistors (power and creepage), 0.1 % thin-film for the analog gain resistors.
- **Isolation distances.** Field (24 V) and logic (3.3 V) are both SELV, so the gap between them is set by the isolator and optocoupler bodies (about 4 mm). Relay contacts (230 VAC) to any SELV copper get at least 8 mm creepage and a routed slot, to be confirmed against IEC 61010-1 during layout.

## Architecture and sheet hierarchy

The board keeps the trial board's four isolation domains and adds no new ones. Every signal that crosses a barrier goes through one of nine packages: five quad optocouplers and four digital isolators.

| Domain | Ground | Supplied from | Circuits |
| --- | --- | --- | --- |
| Logic | GND_L | URB2403S from 24V_LOGIC | STM32, LAN9252, RJ45 magnetics (chip side), logic side of all isolators |
| Field I/O | 0V_IO | 24V_IO directly, +5V_IO from URB2405S | Input optocoupler LEDs, MPG receiver, relay driver and coils |
| Analog | AGND | URB2415S from 24V_IO | DAC, clamp, op-amp, AO terminal |
| Mains | load return | external | Relay contacts, fuses, output terminals (behind a routed slot) |

The STM32 is the only part that talks to every domain, and only through the barrier parts.

| Sheet | Contents | Domain |
| --- | --- | --- |
| 1 Root | Sheet symbols, block diagram, mounting holes, PE | — |
| 2 Power | Two 24 V entries, protection, three isolated modules | All |
| 3 MCU | STM32F405VGT6, shared clock, SWD, UART, heartbeat LED, EtherCAT ERR LED | Logic |
| 4 EtherCAT | LAN9252, EEPROM, 2 × RJ45 | Logic |
| 5 Digital inputs | 4-channel block, placed 5 times (DI1–8, SEL1–12) | Field ↔ logic |
| 6 MPG | Terminal, line receiver, MPG isolator | Field ↔ logic |
| 7 Relay outputs | DO isolators, driver, 8 relays, fuses, terminals | Field ↔ logic, mains |
| 8 Analog outputs | Isolator, DAC, clamp, op-amp, terminal | Analog ↔ logic |

### How the finished board will look

Concept floor plan v2 (redrawn in M6 with the real footprints, see `docs/review/M6-review.md` and `M6-floorplan.png`): **220 × 140 mm**, top view, with the owner's decision of 2026-11-06 to shrink the board with **stacked terminals**. Input terminals, the MPG and the 24 V entry in two rows along the left and bottom edges, the two RJ45 jacks and the two analog terminals on the top edge, the eight relay terminals on the right edge. The four domains sit in their own regions, so every barrier is a straight line that an isolator or optocoupler straddles. The relays form a strip 74 mm deep along the right edge (P2R-05P socket 35.5 mm, fuse block 25.8 mm, terminal 12.5 mm, one row of 15.5 mm per channel) and bridge a routed slot: coil pins on the field side, contacts and fuses on the mains side. The original 200 × 100 mm outline predates the one-terminal-per-I/O decision.

## Block-by-block circuit plan

Each block is one schematic sheet. The values are starting values with the arithmetic shown, so they can be checked before Claude Code places them.

### Power (sheet 2)

- **Entry:** one 4-pole 5.08 mm pluggable terminal: +24V_LOGIC, 0V_LOGIC, +24V_IO, 0V_IO. A separate PE screw terminal.
- **Protection, per input:** fuse (1 A logic, 3 A I/O) → SS54 series diode for reverse polarity → SMBJ30A TVS → 47 µF/50 V + 1 µF. The 30 V stand-off clears 28.8 V (24 V +20 %) and the 48.4 V clamp stays below the URB modules' 50 V / 1 s surge rating.
- **Logic rail:** URB2403S-6WR3 isolated module, 24V_LOGIC → +3V3 on GND_L, 1.35 A max. Expected load is about 0.4 A (STM32 about 0.1 A, LAN9252 about 0.25 A, LEDs and isolators the rest), so 30 % of rating. No LDO.
- **Field 5 V:** URB2405S-6WR3, 24V_IO → +5V_IO with its 0 V tied to 0V_IO at the module. It feeds the MPG pendant, the line receiver and the field side of three isolators.
- **Analog rail:** URB2415S-6WR3, 24V_IO → +15V_A on its own isolated AGND.
- All three modules are the same SIP-8 family, input 9–36 V, so they cover 24 V ±20 %. The 2:1 Hi-Link B-series parts were rejected because they only accept ±10 %.
- **Sensor supply:** each input terminal's +24 V pin goes through a 500 mA PTC, so a shorted sensor cable does not blow the main fuse.

### MCU (sheet 3)

- **STM32F405VGT6**, LQFP-100, 82 I/O; 51 are used (the original 50 plus the EtherCAT ERR LED), PH1 stays a test pad and the other 30 are free for future use.
- **Clock:** one 25 MHz CMOS oscillator → 22 Ω → PH0 (HSE bypass), and → 22 Ω → LAN9252 OSCI (OSCO open). Firmware: PLLM = 25, PLLN = 336, PLLP = 2 → 168 MHz. This removes one crystal and its two capacitors.
- **Support parts:** 100 nF at each VDD pin, 4.7 µF bulk, VDDA through a ferrite with 1 µF + 100 nF, 2.2 µF on each VCAP pin, BOOT0 10 kΩ to GND, NRST 100 nF.
- **Debug:** 2×5 1.27 mm SWD header (PA13, PA14, PB3 SWO, NRST); USART2 (PA2/PA3) on a 3-pin header.
- **Fail-safe pull-downs:** 10 kΩ on PD2 (relay OE), 10 kΩ pull-up on PB14 (AO_CLAMP) and on PC5 (LAN9252 RST#). The independent watchdog (IWDG) is enabled in option bytes, so an MCU hang resets the chip and the pins float to their safe state.
- **Pin map:** every signal is in the table below, including all LAN9252 control lines.

| Function | STM32F405VGT6 pins | Peripheral and notes |
| --- | --- | --- |
| LAN9252 SPI | PA5 SCK, PA6 MISO, PA7 MOSI, PA4 CS | SPI1 |
| LAN9252 IRQ | PC4 | EXTI4, interrupt-driven process data |
| LAN9252 SYNC0 / SYNC1 | PA0 / PC13 | EXTI0 / EXTI13, Distributed Clocks |
| LAN9252 RST# | PC5 | Open-drain output, 10 kΩ pull-up |
| DAC SPI | PB13 SCK, PB15 MOSI, PB12 CS | SPI2 |
| AO_CLAMP | PB14 | GPIO out, pull-up = clamped until firmware releases it |
| MPG A / B | PB4 / PB5 | TIM3 CH1/CH2, encoder mode |
| DI1–8 | PC0–PC3, PC6–PC9 | GPIO in, internal pull-up |
| SEL1–12 | PB0, PB1, PB2, PB8–PB11, PA15, PB6, PB7, PC14, PC15 | GPIO in, internal pull-up |
| DO1–8 | PA8–PA12, PC10–PC12 | GPIO out |
| Relay OE | PD2 | GPIO out, 10 kΩ pull-down |
| Heartbeat LED | PA1 | GPIO out |
| EtherCAT ERR LED | PD3 | GPIO out (the LAN9252 has no ERR output) |
| Debug | PA13 SWDIO, PA14 SWCLK, PB3 SWO, PA2/PA3 USART2 | |
| Clock | PH0 | HSE bypass, shared 25 MHz |
| Spare | PH1 | Brought to a test pad |

### EtherCAT (sheet 4)

- **LAN9252I/PT** in SPI mode, copied from the EVB-LAN9252-SPI reference schematic: straps, RBIAS 12.1 kΩ 1 %, internal 1.2 V regulator capacitors and the TX/RX termination.
- **EEPROM:** 24LC32AT-I/SN on EESCL/EESDA with 4.7 kΩ pull-ups (ESI configuration).
- **Ports:** 2 × HY911105AE RJ45 jacks with integrated magnetics and LEDs, rated −40 to +85 °C. Their LEDs show LINK/ACT per port.
- **Status:** the LAN9252 RUNLED pin drives the EtherCAT RUN LED; the ERR LED is driven by STM32 pin PD3, because the LAN9252 has no ERR output. One MCU heartbeat LED replaces the four DISC1 LEDs.
- **Shield:** both jack shields → 1 nF/2 kV ∥ 1 MΩ → PE terminal.
- **MCU connections:** besides SPI, the LAN9252 IRQ, SYNC0, SYNC1 and RST# go to the STM32 (pin map above). IRQ lets firmware react to SyncManager events instead of polling, SYNC0/SYNC1 allow Distributed Clocks synchronous mode, and RST# lets firmware reset the ESC.

### Digital inputs (sheet 5, placed 5 times)

One 4-channel hierarchical sheet (one TLP290-4), placed 5 times: DI1–4, DI5–8, SEL1–4, SEL5–8 and SEL9–12. Twelve selector inputs cover both pendant types: 4-axis (OFF, X, Y, Z, 4 + ×1, ×10, ×100 = 8 wires) and 6-axis (OFF, X–6 + 3 steps = 10 wires), with 2 spare.

- **Per channel:** 4.7 kΩ 1206 series resistor and 10 nF 0603 across the optocoupler input (47 µs filter against fast transients).
- **Optocoupler:** TLP290-4, AC input (two anti-parallel LEDs), so one COM jumper selects PNP or NPN with no rewiring. One package per 4 inputs, so 5 packages for 20 inputs.
- **IEC 61131-2 Type 3 check:** at 11 V the input draws (11 − 1.2) / 4.7 kΩ = 2.1 mA (on, needs ≥ 2 mA). At 5 V it draws 0.8 mA (off, needs ≤ 1.5 mA). At 28.8 V it draws 5.9 mA, so the resistor dissipates 0.16 W, within a 1206's 0.25 W.
- **Logic side:** emitter to GND_L; collector to the MCU pin (internal pull-up) and through a green LED and 1 kΩ (4-element array) to +3V3. The LED lights when the input is on and shows the real optocoupler state, with no extra driver.
- **COM jumper:** 3-pin header with shunt, one per group (DI and SEL): COM to 0V_IO for PNP sensors, COM to +24V_IO for NPN sensors.
- **Terminals:** DI1–8 on a 10-pole 5.08 mm plug (IN1–8, +24 V through the PTC, 0 V); SEL1–12 on a 14-pole plug (IN1–12, +24 V, 0 V). Dry-contact switches wire between +24 V and the input; 24 V switches wire straight to the input. Both work in PNP mode.

### MPG (sheet 6)

- **Terminal:** 6-pole: +5V_IO (through a 250 mA PTC), 0V_IO, A, A̅, B, B̅.
- **Receiver:** AM26LS32ACDRG4 (LCSC, 0 to +70 °C) for A/A̅ and B/B̅, with 120 Ω termination footprints left unfitted (20 kHz over 5 m does not need them). One TVS array per pair.
- **Isolation:** receiver outputs go through the two reverse channels of a CA-IS3742LN to PB4/PB5 (TIM3 encoder mode). The same isolator's forward channel 1 carries the relay OE signal; channel 2 is spare.

### Relay outputs (sheet 7)

- **Isolation:** 2 × CA-IS3740LN carry DO1–8. Their outputs default low when the logic side loses power.
- **Output enable:** OE (PD2, through the CA-IS3742LN) drives the side-B enable pin of both CA-IS3740LN. When OE is low their outputs go high-impedance and two 4 × 100 kΩ arrays pull the driver inputs low.
- **Driver:** one ULN2803A drives all 8 coils, with its COM pin on +24V_IO for the built-in flyback diodes.
- **Relays:** 8 × Omron G2R-1-S DC24 plug-in relays in Omron P2R-05P PCB sockets: SPDT, 10 A / 250 VAC, 24 V coil of about 1.1 kΩ (22 mA, 0.53 W), so 176 mA for all eight, well within the ULN2803A. The board is built by PCBPower with the sockets soldered; the relays are bought in India, where the G2R-1-S is a standard Omron stock item, so a burnt relay is pulled out and replaced by hand on site.
- **ON LED:** a green LED and 22 kΩ across each coil shows the coil is actually energised (1.2 mA; 33 mW per array element against a 62.5 mW rating).
- **Contacts:** COM → T5A 5×20 mm ceramic fuse in a covered PCB holder → terminal; NO → terminal. Two 8-pole 300 V 5.08 mm terminals. RC snubber footprints across each contact, unfitted.
- **Fail-safe chain, no firmware needed after step 1:**
  1. EtherCAT loss → SM watchdog → firmware clears DO1–8 and OE.
  2. MCU hang → IWDG reset → PD2 floats → 10 kΩ pulls OE low.
  3. Logic power lost → isolators default low → OE low.
  4. E-stop opens 24V_IO externally → coils drop.

This replaces the external watchdog IC and coil-supply MOSFET from the trial plan with parts already on the board.

### Analog outputs (sheet 8)

- **Isolation:** one CA-IS3740HW, wide-body, default-high outputs: SCK, MOSI, CS (high = DAC deselected) and AO_CLAMP (high = outputs clamped). Default-high means 0 V on power-up, on logic power loss and during MCU reset.
- **DAC:** MCP4822-E/SN, dual 12-bit with internal 2.048 V reference, gain 2× → 0–4.095 V. Powered from a 78L05-class LDO off +15V_A; LDAC tied low.
- **Clamp:** per channel, DAC → 1 kΩ → op-amp input; a 2N7002DW dual MOSFET shorts both op-amp inputs to AGND while AO_CLAMP is high; 100 kΩ to AGND holds 0 V if the DAC is unpowered.
- **Gain stage:** LM2904 on +15V_A, non-inverting gain 1 + 14.7 kΩ / 10.0 kΩ = 2.47 (0.1 % resistors), so full scale is 10.11 V and firmware calibrates the 0 V and 10 V points of each channel.
- **Output:** 100 Ω inside the feedback loop, then SMAJ15A to AGND and 10 nF. At 10 V into 2 kΩ the op-amp swings to 10.6 V, below its 13.5 V limit on a 15 V rail.
- **Accuracy budget after calibration:** reference drift 125 ppm/°C × 55 °C ≈ 0.7 %, op-amp offset 3 mV ≈ 0.03 %, resistors ≈ 0.2 %, so about ±0.9 % FS worst case across 0–80 °C. Accepted.
- **Terminal:** 3-pole: AO1, AO2, AGND.

## Schematic drawing conventions

The sheets are drawn the way a PCB engineer hands them to layout: signals flow left to right, the isolation barrier is visible on the page, and every part sits next to what it serves.

- **Page:** A3 landscape, one function per sheet, title block filled (project, sheet name, revision, date).
- **Flow:** field connectors on the left edge, outputs on the right edge, supplies at the top, grounds pointing down. No ground symbol points up.
- **Isolation barrier:** a dashed vertical line with the domain name on each side. The isolator or optocoupler symbol straddles it; no wire crosses it.
- **Grid:** 50 mil (1.27 mm), every pin and wire on grid, no four-way junctions, junction dots on every T.
- **Decoupling:** each 100 nF capacitor is drawn beside the pin it serves, in pin order, so layout can see which capacitor belongs to which pin.
- **Power symbols, one set per domain:** +3V3 / GND_L, +24V_LOGIC / 0V_LOGIC, +24V_IO / 0V_IO, +5V_IO, +15V_A / AGND, PE. A separate ground symbol per domain makes an accidental bridge show up in ERC.
- **Labels:** hierarchical labels between sheets, local labels inside a sheet, no global labels except power. Buses for DI[1..8], SEL[1..12] and DO[1..8].
- **Net names:** named on both sides of the barrier, for example DI3_FIELD and DI3, MPG_A_P / MPG_A_N, DO5_COIL.
- **Repeated channels:** channel 1 drawn in full, the other channels aligned below it in the same shape, grouped by package (4 channels per optocoupler or isolator).
- **Designators:** numbered by sheet (R201–R299 on sheet 2), frozen once layout starts.
- **Fields on every symbol:** Value, Footprint, LCSC, MPN, Manufacturer, Datasheet. Unfitted parts carry DNP. KiCad 10 design variants hold BOM options such as fitted terminations.
- **Notes on the sheet:** the key calculation beside its circuit (input thresholds, gain, power budget), and a boxed "230 VAC, 8 mm creepage" note around the relay contact zone.
- **Test points:** one on every rail and on OE, AO_CLAMP, SPI and MPG A/B.

## Key-part BOM

Stock counts move daily, so Claude Code re-checks each row when it builds the BOM.

| Sheet | Part | Qty | LCSC # | Rating | Notes |
| --- | --- | --- | --- | --- | --- |
| MCU | [STM32F405VGT6](https://www.lcsc.com/product-detail/C56621.html) | 1 | C56621 | −40 to +85 °C | LQFP-100, same F4 core as the DISC1, about $7.6 |
| MCU | [ECS-3225MVQ-250-CN-TR 25 MHz oscillator](https://www.lcsc.com/product-detail/C2595919.html) | 1 | C2595919 | −40 to +85 °C | Shared clock. Confirm stability ≤ ±50 ppm for the LAN9252 |
| EtherCAT | [LAN9252I/PT](https://lcsc.com/product-detail/Ethernet-Transceivers_Microchip-Tech-LAN9252I-PT_C80933.html) | 1 | C80933 | −40 to +85 °C | |
| EtherCAT | [24LC32AT-I/SN EEPROM](https://www.lcsc.com/product-detail/C615715.html) | 1 | C615715 | −40 to +85 °C | ESI EEPROM |
| EtherCAT | [HY911105AE RJ45 with magnetics](https://www.lcsc.com/product-detail/Ethernet-Connectors-Modular-Connectors-RJ45-RJ11_Zhongshan-HanRun-Elec-HY911105AE_C69427.html) | 2 | C69427 | −40 to +85 °C | Replaces HR911105A (0–70 °C) |
| Power | [URB2403S-6WR3 (3.3 V)](https://www.lcsc.com/product-detail/C5369843.html) | 1 | C5369843 | −40 to +105 °C | 9–36 V in, 1.35 A |
| Power | [URB2405S-6WR3 (5 V)](https://www.lcsc.com/product-detail/C3031185.html) | 1 | C3031185 | −40 to +105 °C | 9–36 V in, 1.2 A |
| Power | [URB2415S-6WR3 (15 V)](https://www.lcsc.com/product-detail/C5369844.html) | 1 | C5369844 | Check datasheet | 9–36 V in, 0.4 A |
| Power | [SMBJ30A TVS](https://www.lcsc.com/product-detail/C83851.html) | 2 | C83851 | | One per 24 V input (replaces the SMBJ33A C320242, see Decisions log) |
| Inputs | [TLP290-4(GB) AC-input quad optocoupler](https://www.lcsc.com/product-detail/Transistor-Photovoltaic-Output-Optoisolators_TOSHIBA-TLP290-4-GB-TP-E-T_C39031.html) | 5 | C39031 | −55 to +110 °C | 20 inputs |
| MPG | [AM26LS32ACDRG4 line receiver](https://www.lcsc.com/product-detail/C2671811.html) | 1 | C2671811 | 0 to +70 °C | 0–70 °C grade by choice. AM26LS32AIDR (−40 to +85 °C, Mouser) has the same pinout |
| MPG / relays | [CA-IS3742LN isolator (2 fwd, 2 rev)](https://www.lcsc.com/product-detail/C5347249.html) | 1 | C5347249 | −40 to +125 °C | OE + MPG A/B |
| Relays | [CA-IS3740LN isolator (4 fwd)](https://lcsc.com/product-detail/Digital-Isolators_Chipanalog-CA-IS3740LN_C428888.html) | 2 | C428888 | −40 to +125 °C | DO1–8, default low |
| Relays | [ULN2803A](https://lcsc.com/product-detail/High-CurrentDrivers_ULN2803A_C181731.html) | 1 | C181731 | −40 to +85 °C | 8 coils, built-in flyback |
| Relays | Omron G2R-1-S DC24 relay + [P2R-05P PCB socket](https://www.lcsc.com/product-detail/C1524860.html) | 8 | C1524860 (socket) | −40 to +70 °C (check) | 10 A / 250 VAC. Socket fitted at PCB assembly (LCSC, or Mouser/DigiKey if LCSC is out); relay bought locally in India |
| Analog | [CA-IS3740HW isolator (4 fwd, wide-body)](https://lcsc.com/product-detail/Digital-Isolators_Chipanalog-CA-IS3740HW_C528653.html) | 1 | C528653 | −40 to +125 °C | Default high = safe 0 V |
| Analog | [MCP4822-E/SN dual 12-bit DAC](https://www.lcsc.com/product-detail/C16040.html) | 1 | C16040 | −40 to +125 °C | |
| Analog | [LM2904DR dual op-amp](https://jlcpcb.com/partdetail/C7934) | 1 | C7934 | −40 to +125 °C | |
| Connectors | KF2EDGK 5.08 mm pluggable plugs + matching KF2EDGR headers | 9 sets | C440886 (8-pole plug) | −40 to +105 °C | 4, 6, 10, 14, 3 and 2 × 8 poles; one LCSC # per size. Plus a PE screw terminal |

Commodity parts get their LCSC numbers in milestone M1: SS54, 2N7002DW, SMAJ15A, the 78L05-class LDO, PTCs, the MPG TVS arrays, the jumper headers, LEDs, resistor arrays and all passives. Passives come from LCSC basic parts where one exists, to avoid extended-part fees.

Relay-contact fuses: 8 × Littelfuse 646 5×20 mm PCB fuse blocks (C206887) with 648 clear covers (C187509), and 8 × T5A 250 VAC ceramic fuses, bought locally like the relays. The two 24 V inputs use the same block and cover with 1 A and 3 A 5×20 glass fuses.

## Claude Code cloud workflow

Claude Code builds the project in this repo, one milestone per pull request, and checks each sheet with KiCad's own command-line tools before review. Target KiCad 10, the current stable line.

1. **Environment.** The cloud environment's setup script installs KiCad 10 (for `kicad-cli`), `easyeda2kicad` and `kiutils`. See `scripts/cloud-setup.sh`.
2. **Network access.** easyeda2kicad pulls LCSC symbols and footprints from the EasyEDA servers, so the environment allows easyeda.com and lcsc.com.
3. **Parts list first.** Claude Code writes `bom/parts.csv` (reference group, LCSC #, MPN, footprint) from the BOM above, assigns the commodity LCSC numbers, and stops for approval.
4. **Libraries.** A script runs easyeda2kicad for every LCSC number into one project library, `lib/lcsc.kicad_sym` and `lib/lcsc.pretty`. Claude Code checks each IC symbol's pin names and numbers against its datasheet. Resistors, capacitors and LEDs use KiCad's standard symbols with the LCSC field filled.
5. **Sheets, one at a time.** A Python generator writes each `.kicad_sch` with explicit grid coordinates per block, following the conventions above. Order: power, MCU, EtherCAT, digital inputs, MPG, relay outputs, analog outputs, then the root sheet.
6. **Checks on every sheet.**
   - `kicad-cli sch erc` must report zero errors.
   - A pin-map script compares each STM32 net against the pin map table on the MCU sheet.
   - `kicad-cli sch export pdf` and a rendered PNG, which Claude Code inspects for overlaps, off-grid wires and labels crossing the barrier.
7. **BOM export.** `kicad-cli sch export bom` with the LCSC column; a script fails if any fitted part has no LCSC or Mouser/element14 number.
8. **Review.** Each milestone lands as a pull request with its PDF attached. Approve and merge, then the next milestone starts.

## Milestones

Each milestone ends at a review gate; the next one starts only after approval.

- [ ] **M1 Parts frozen:** `bom/parts.csv` complete, every row with an LCSC or fallback number and its temperature rating. Gate: approve the list.
- [ ] **M2 Libraries:** all symbols and footprints imported and pin-checked against datasheets.
- [ ] **M3 Power and MCU sheets:** ERC clean, pin map matches the MCU pin table.
- [ ] **M4 EtherCAT sheet:** matches the EVB-LAN9252-SPI reference circuit.
- [ ] **M5 I/O sheets:** inputs, MPG, relays, analog, each ERC clean, with calculations noted on the sheet.
- [ ] **M6 Full review:** root sheet, BOM export, PDF set, redrawn floor plan. Gate: schematic review against this plan, then layout starts (4-layer recommended for the STM32 and LAN9252).

## Decisions log

- Firmware will be new, so pins are chosen freely; the MCU is an STM32F405RGT6, and the LAN9252 IRQ, SYNC0/1 and RST# are wired.
- Relays are pluggable: Omron G2R-1-S DC24 in P2R-05P PCB sockets. Sockets are fitted in China; relays are sourced locally in India for service.
- 0–80 °C is inside the enclosure and only a reference. Keep the hottest parts (relays, DC-DC modules) apart and check the enclosure temperature once the first board runs.
- Relay contact fuses: industry-standard 5×20 mm (IEC 60127, T5A 250 VAC ceramic, high breaking capacity) in a covered PCB holder, one per channel.
- The MPG pendant type is not fixed: 12 selector inputs accept dry contacts or 24 V switches on a 4-axis or 6-axis pendant.
- ±0.9 % FS analog accuracy is accepted; the MCP4822 keeps its internal reference.
- PE comes from a screw terminal on the board (works with a plastic enclosure).
- MPG line receiver uses the LCSC 0–70 °C AM26LS32ACDRG4.
- M1 review, 2026-11-05: AM26LS32ACDRG4 (C2671811) has no stock, so the MPG receiver is the same TI part as C6180 AM26LS32ACDR (0–70 °C, SOIC-16).
- M1 review, 2026-11-05: ULN2803A C181731 has no stock, so the relay driver is C845537 (UMW ULN2803A, SOP-18-300mil). Pin-check in M2.
- M1 review, 2026-11-05: each URB module gets the 100 µF/100 V input capacitor its datasheet recommends (3 × C2960285), in addition to the 47 µF/50 V entry capacitors.
- M1 review, 2026-11-05: status LEDs use yellow-green NCD0603C3 (C89809). No ~2 V green LED exists on LCSC and emerald green may not light from 3.3 V through 1 kΩ.
- M1 review, 2026-11-05: the two 24 V input fuses are replaceable 5×20 mm glass fuses (1 A C3116, 3 A C3118) in the same covered holder as the relay fuses (C58066, 80 °C rating accepted).
- M1 review, 2026-11-05: one pluggable 5.08 mm connector per I/O, no large multi-pole terminals. Each of the 8 digital inputs and 12 selector inputs gets a 3-pole connector (+24 V via PTC, IN, 0 V); each of the 8 relays gets a 3-pole connector (COM via fuse, NO, NC); each of the 2 analog outputs gets a 2-pole connector (AO, AGND). MPG stays 6-pole and the power entry 4-pole. This supersedes the 10-pole, 14-pole, 8-pole and 3-pole AO terminals in the sheet descriptions and the connector row of the key-part BOM; the "9 sets" count no longer applies.
- M1 review, 2026-11-05: the URB modules allow 40 V maximum input but the SMBJ33A clamps at 53.3 V. Parts are kept as planned; module-side limiting is designed on the power sheet in M3 and brought for approval.
- M2 review, 2026-11-06: MCU changed from the STM32F405RGT6 (LQFP-64) to the **STM32F405VGT6 (LQFP-100, C56621, 82 I/O)** so the board does not run out of pins now or later. Every existing pin assignment is unchanged (same port pin names). The EtherCAT ERR LED goes on **PD3** because the LAN9252 has only a RUNLED output. PH1 stays a test pad; the remaining free pins are reserved for future use. The six VDD pins need six 100 nF capacitors (plus VDDA and VBAT). This supersedes the "STM32F405RGT6" and "LQFP-64" wording elsewhere in this plan and the RUN and ERR LED statement in the EtherCAT section.
- M2 review, 2026-11-06: fabrication, assembly and component sourcing are done by **PCBPower**, who buy every component from **lcsc.com**. So lcsc.com's own stock is the only stock that counts and JLCPCB is not used for sourcing or stock (JLCPCB's catalogue may be used only to look up candidate LCSC numbers, which are then verified on lcsc.com). This supersedes "the board is built in China". Four capacitors that lcsc.com showed at 0 stock are replaced: 100 nF C1591, 10 nF C1589, 1 µF 0603 C559769 (X7R) and 1 µF 0805 C91185.
- M2 review, 2026-11-06: the PE terminal stays the Keystone 7770, which ships without its screw, so an M3 × 6 screw (C357543) is added to the BOM.
- M2 review, 2026-11-06: the 5×20 fuse holder C58066 (no dimensioned drawing, 80 °C rating) is replaced by the Littelfuse 646 fuse block (C206887) with the 648 clear cover (C187509): full drawing, footprint checked against it. The Littelfuse datasheet states no operating temperature. Parts whose datasheets have full dimensioned drawings (RJ45 HY911105AE, Keystone 7770, P2R-05P, URB modules, Littelfuse 646) have their footprints checked against the printed dimensions by `scripts/pincheck.py`.
- M3 review, 2026-11-06: the TVS on both 24 V inputs is changed from the SMBJ33A (C320242, clamps 53.3 V at 11.3 A) to the **SMBJ30A, Littelfuse C83851** (clamps 48.4 V at 12.4 A, 30 V stand-off above the 28.8 V maximum input, same SMB package). This brings the clamp below the URB modules' 50 V / 1 s surge rating. Supersedes the M1 decision to keep the SMBJ33A.
- M3 review, 2026-11-06: drawing rules for all sheets: every component instance at rotation 0 and unmirrored, all text horizontal, no symbol pins on the top or bottom edge. Parts that must be drawn the other way use pre-rotated standard KiCad graphics from `lib/lcec.kicad_sym`.
- M4, 2026-11-06: the EtherCAT sheet follows the EVB-LAN9252-SPI reference (supplied by the owner): chip mode 00, E2PSIZE high (24LC32A), TESTMODE/FX straps low, one 220 R ferrite (Murata BLM18EG221SN1D, C85827) each for VDD33TXRX1, VDD33TXRX2, VDD33BIAS and VDD12TX, 49.9 R terminations and centre taps on each port's filtered 3.3 V with 22 nF. Deviations from the EVB, all listed in `docs/review/M4-ethercat.md`: shared oscillator instead of a crystal, 24LC32A with 4.7 k pull-ups and WP low, no RST# capacitor/button, shield to PE through 1 nF/2 kV and 1 M.
- M5, 2026-11-06: I/O sheets drawn as planned. Inputs: one 4-channel sheet reused 5 times under a parent sheet that holds, per group (DI, SEL), the sensor-supply PTC and the COM jumper (shunt fitted for PNP). Relays: coil and contact sides of each P2R-05P are separated by a dashed barrier; unfitted RC snubber footprints are drawn as 100 R (2512) + 47 nF X2 film proposals, values to be confirmed at layout. MPG: the AM26LS32A runs from +5V_IO, the CA-IS3742LN field side on +5V_IO and its logic side on +3V3. Analog: CA-IS3740HW field side on +5V_A (78L05 from +15V_A). BOM estimates are replaced by the placed counts (see `docs/review/M5-io-sheets.md`).
- M5 review, 2026-11-06: owner confirmed the unfitted relay snubbers (100 R 2512 + 47 nF X2 film), the COM jumper shunt fitted 2-3 (PNP) on both groups, and the Omron P2R-05P socket (C1524860, 44 in stock on lcsc.com for 8 per board, enough for 5 boards; Mouser or element14 only if LCSC runs out).
- M6, 2026-11-06: full review against this plan done (`docs/review/M6-review.md`): every section matches the finished schematics apart from the changes recorded above. Owner decisions: smaller board with stacked terminals (v2 outline 220 × 140 mm), 4 layers, enclosure built around the PCB. Open: the stacked-terminal part style (a second row behind the KF2EDGR plugs blocks their side wire entry).\n