#!/usr/bin/env python3
"""Single source of truth for the STM32F405VGT6 pin map (docs/plan.md, MCU sheet table).

Used by relayout_symbols.py (symbol layout), build_schematics.py (net labels) and
check_pinmap.py (verifies the schematic netlist against docs/plan.md itself).

GROUPS: (side, title, [(net, pin name), ...]) in display order, top to bottom.
Nets that cross to other sheets keep the same name as the hierarchical label.
"""

LEFT_RIGHT = [
    ("left", "Reset and boot", [("NRST", "NRST"), ("BOOT0", "BOOT0")]),
    ("left", "Clock", [("CLK_MCU", "PH0"), ("PH1_TP", "PH1")]),
    ("left", "MPG encoder", [("MPG_A", "PB4"), ("MPG_B", "PB5")]),
    ("left", "EtherCAT in", [("ESC_IRQ", "PC4"), ("ESC_SYNC0", "PA0"), ("ESC_SYNC1", "PC13")]),
    ("left", "DI1-8", [(f"DI{i + 1}", p) for i, p in enumerate(["PC0", "PC1", "PC2", "PC3", "PC6", "PC7", "PC8", "PC9"])]),
    ("left", "SEL1-12", [(f"SEL{i + 1}", p) for i, p in enumerate(
        ["PB0", "PB1", "PB2", "PB8", "PB9", "PB10", "PB11", "PA15", "PB6", "PB7", "PC14", "PC15"])]),
    ("left", "Free for future use (port E)", [(f"FREE_PE{i}", f"PE{i}") for i in range(16)]),
    ("right", "DO1-8", [(f"DO{i + 1}", p) for i, p in enumerate(["PA8", "PA9", "PA10", "PA11", "PA12", "PC10", "PC11", "PC12"])]),
    ("right", "Relay enable", [("RELAY_OE", "PD2")]),
    ("right", "LEDs", [("HB_LED", "PA1"), ("ERR_LED", "PD3")]),
    ("right", "LAN9252 SPI1", [("ESC_CS", "PA4"), ("ESC_SCK", "PA5"), ("ESC_MISO", "PA6"), ("ESC_MOSI", "PA7")]),
    ("right", "LAN9252 reset", [("ESC_RST", "PC5")]),
    ("right", "DAC SPI2", [("DAC_CS", "PB12"), ("DAC_SCK", "PB13"), ("DAC_MOSI", "PB15")]),
    ("right", "Analog clamp", [("AO_CLAMP", "PB14")]),
    ("right", "Debug", [("SWDIO", "PA13"), ("SWCLK", "PA14"), ("SWO", "PB3")]),
    ("right", "UART2", [("UART2_TX", "PA2"), ("UART2_RX", "PA3")]),
    ("right", "Free for future use (port D)", [(f"FREE_PD{i}", f"PD{i}") for i in [0, 1] + list(range(4, 16))]),
]

# A part hangs beside these pins on the sheet, so the symbol leaves blank rows: a pull-down or capacitor
# hangs BELOW its pin (gap after), a pull-up hangs ABOVE it (gap before).
GAP_ROWS = 4
GAP_AFTER = {"NRST", "BOOT0", "RELAY_OE"}
GAP_BEFORE = {"ESC_RST", "AO_CLAMP"}

# Alternate function printed after the port name on the symbol
FUNCTIONS = {
    "PA4": "SPI1_NSS", "PA5": "SPI1_SCK", "PA6": "SPI1_MISO", "PA7": "SPI1_MOSI",
    "PB12": "SPI2_NSS", "PB13": "SPI2_SCK", "PB15": "SPI2_MOSI",
    "PB4": "TIM3_CH1", "PB5": "TIM3_CH2", "PC4": "EXTI4", "PA0": "EXTI0", "PC13": "EXTI13",
    "PA13": "SWDIO", "PA14": "SWCLK", "PB3": "SWO", "PA2": "USART2_TX", "PA3": "USART2_RX",
    "PH0": "OSC_IN", "PH1": "OSC_OUT", "PB2": "BOOT1", "PC14": "OSC32_IN", "PC15": "OSC32_OUT",
}

VDD_PINS = [11, 19, 28, 50, 75, 100]
VSS_PINS = [10, 27, 74, 99]

# nets that are NOT plain STM32 port signals (support circuits) are named in build_schematics.py
LAN9252_SIGNALS = ["ESC_CS", "ESC_SCK", "ESC_MISO", "ESC_MOSI", "ESC_IRQ", "ESC_SYNC0", "ESC_SYNC1", "ESC_RST"]


def all_signal_nets():
    """{net: pin name} for every port signal that is used (not 'free for future use')."""
    out = {}
    for side, title, items in LEFT_RIGHT:
        if title.startswith("Free"):
            continue
        for net, pin in items:
            out[net] = pin
    return out
