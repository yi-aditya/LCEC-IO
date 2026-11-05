# LCEC-IO — instructions for Claude Code

This repo holds the KiCad 10 hardware design for an industrial EtherCAT slave I/O board (STM32F405RGT6 + LAN9252). The approved design is `docs/plan.md`. Treat it as the specification: do not change part choices, pin assignments or circuit values without asking first, and record any approved change in its "Decisions log".

## How to work

- Work one milestone at a time (M1 → M6 in `docs/plan.md`). Each milestone is its own branch and pull request. Stop at the end of a milestone and wait for approval before starting the next one.
- Never push to `main` directly. Open a pull request; the owner reviews it in the browser.
- The owner works from a browser only. Put everything they need to review in the PR: a short summary, the ERC result, and the exported PDF (and PNG previews) committed under `docs/review/`.
- If a datasheet, footprint or LCSC page contradicts the plan, stop and ask instead of guessing.

## Sourcing rules

1. LCSC first. Every fitted part gets an `LCSC` field.
2. Mouser or element14 only when LCSC has no suitable part; put the distributor part number in an `MPN_ALT` field and say why in the BOM notes.
3. Relays (Omron G2R-1-S DC24) and contact fuses (5×20 mm T5A ceramic) are bought locally in India. Their sockets/holders are fitted at PCB assembly and need LCSC numbers; the relays and fuses themselves are marked `DNP` in the assembly BOM.
4. Passives: LCSC basic parts where possible (0603 logic, 1206 for 24 V input resistors, 0.1 % thin-film for analog gain).

## Repository layout

- `docs/plan.md` — approved specification
- `docs/review/` — exported PDFs/PNGs for each PR
- `bom/parts.csv` — master parts list (M1)
- `lib/` — project symbol, footprint and 3D libraries (`lcsc.kicad_sym`, `lcsc.pretty/`, `lcsc.3dshapes/`)
- `hardware/` — KiCad project (`lcec-io.kicad_pro`, root and sub-sheets)
- `scripts/` — generators and checks (Python)

## Tools

- `kicad-cli` (KiCad 10) for ERC, PDF, netlist and BOM export.
- `easyeda2kicad` to import LCSC parts into `lib/` (always into the project library, never a global one).
- `kiutils` or direct S-expression writing to generate `.kicad_sch` files.
- `pdftoppm` to render PDFs to PNG so you can inspect sheets visually.

## Schematic conventions (summary — full list in docs/plan.md)

- A3 landscape, one function per sheet, title block filled.
- Signals flow left to right; field connectors on the left, outputs on the right, supplies top, grounds down.
- Isolation barrier drawn as a dashed vertical line; isolators/optocouplers straddle it; no wire crosses it.
- 50 mil grid, no four-way junctions, decoupling caps beside the pin they serve.
- Separate power/ground symbols per domain: +3V3/GND_L, +24V_LOGIC/0V_LOGIC, +24V_IO/0V_IO, +5V_IO, +15V_A/AGND, PE.
- Hierarchical labels between sheets; no global labels except power.
- Designators numbered by sheet (R201… on sheet 2).
- Every symbol has Value, Footprint, LCSC, MPN, Manufacturer, Datasheet.

## Definition of done for a sheet

- `kicad-cli sch erc --exit-code-violations` reports zero errors (warnings listed and explained in the PR).
- STM32 nets match the pin map table in `docs/plan.md` (checked by script).
- PDF exported to `docs/review/`, rendered to PNG and visually checked for overlaps, off-grid wires and labels crossing the barrier.
