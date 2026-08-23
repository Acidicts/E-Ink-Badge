# config.py - pin mapping for the E-Ink Badge (RP2350A), from GET_STARTED.md.
#
#   SPI display pins:
#     SCLK  -> GPIO 2
#     SDI   -> GPIO 3   (MCU -> display, "MOSI")
#     D/C   -> GPIO 4
#     CS    -> GPIO 5
#     RES   -> GPIO 6
#     BUSY  -> GPIO 7
#
# Everything else (battery ADC channel, buttons) isn't called out in the
# hardware docs, so sensible defaults are used below and clearly marked.
# Adjust to match your actual schematic/silkscreen if they differ.

import board

# ---- E-ink display (SSD1680-class controller, GDEY0266T90H 360x184) ----
EPD_SCLK = board.GP2
EPD_MOSI = board.GP3
EPD_DC = board.GP4
EPD_CS = board.GP5
EPD_RESET = board.GP6
EPD_BUSY = board.GP7

EPD_WIDTH = 360
EPD_HEIGHT = 184
EPD_BAUDRATE = 4_000_000  # 4 MHz, safe for SSD1680

# ---- Battery / power management (BQ24040 charger + TPS63060 buck-boost) --
# No ADC pin is documented for battery sensing in GET_STARTED.md. GP26/ADC0
# is used here as a reasonable default free pin; change to match your
# schematic, or set to None if VBAT isn't routed to the MCU at all.
BATTERY_ADC_PIN = board.GP26
BATTERY_DIVIDER_RATIO = 2.0  # Vbat = Vadc * ratio

# BQ24040 STAT pin (open-drain, active-low while charging) - optional.
# Set to a board.GPxx if wired, or None to disable charge-status reporting.
BATTERY_CHG_STAT_PIN = None

# ---- User input ----
# The board has a BOOTSEL button used for UF2 flashing, not available as a
# normal GPIO to running code. No dedicated user buttons are documented in
# GET_STARTED.md - wire tactile buttons to spare GPIOs and adjust here.
BUTTON_A_PIN = board.GP10
BUTTON_B_PIN = board.GP11
BUTTONS_ACTIVE_LOW = True
