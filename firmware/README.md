# E-Ink Badge — CircuitPython firmware

Firmware for the [E-Ink-Badge](https://github.com/) hardware: an RP2350A
board with a 360×184 SSD1680-class e-ink panel (GDEY0266T90H) over SPI,
BQ24040 LiPo charging, and a TPS63060 buck-boost rail.

This targets **CircuitPython**, not the Pico SDK / Arduino. It uses
`displayio` + Adafruit's `adafruit_ssd1680` driver.

## What you get

- Full-screen badge display: name / pronouns / role / handle, loaded from
  a plain-text profile file so you don't need to touch Python to
  personalize it.
- A tiny 2-button menu (Badge / Battery info / Sleep display).
- A battery icon + percentage in the corner, estimated from a LiPo
  discharge curve.
- Everything laid out in `displayio` groups so screens redraw cleanly.

## Hardware pin mapping (from GET_STARTED.md)

| Signal | GPIO |
|---|---|
| SCLK | 2 |
| SDI (MOSI) | 3 |
| D/C | 4 |
| CS | 5 |
| RES | 6 |
| BUSY | 7 |

These are wired up in `config.py`. Everything else — battery ADC pin,
charge-status pin, and the two menu buttons — **isn't documented in the
hardware README**, so `config.py` uses reasonable placeholder GPIOs
(GP26 for battery sense, GP10/GP11 for buttons) that you should double
check against your actual schematic/silkscreen and adjust if needed. If
your board doesn't route battery voltage to an ADC pin at all, set
`BATTERY_ADC_PIN = None` in `config.py` and the battery reading will
report "n/a" instead of a bogus number.

## Setup

1. **Flash CircuitPython** onto the RP2350A. Hold BOOTSEL while plugging
   in USB-C, then drag the appropriate `.uf2` for RP2350 onto the
   `RPI-RP2` drive that shows up. Get it from
   https://circuitpython.org/downloads (search for an RP2350-based board;
   if there's no exact board definition for this custom PCB, the generic
   `Raspberry Pi Pico 2` build is the right starting point since it's the
   same RP2350A/RP2350B family).

2. **Copy libraries.** Download the
   [Adafruit CircuitPython Bundle](https://circuitpython.org/libraries)
   matching your CircuitPython version, then copy these into a `lib/`
   folder on the `CIRCUITPY` drive:
   - `adafruit_ssd1680.mpy`
   - `adafruit_display_text/` (folder)
   - `fourwire.mpy` (only needed on older CircuitPython builds where it
     isn't built in — recent versions have `fourwire` built into the
     firmware itself, in which case you can skip this file)

3. **Copy this project's files** onto `CIRCUITPY`:
   - `boot.py`
   - `code.py`
   - `config.py`
   - `battery.py`
   - `buttons.py`
   - `badge_profile.py`
   - `badge_profile.txt`

4. **Personalize the badge** by editing `badge_profile.txt` directly on
   the `CIRCUITPY` drive — no code changes needed:
   ```
   name = Ada Lovelace
   pronouns = she/her
   role = Firmware
   handle = @ada
   ```

5. Power-cycle or save any file to trigger a reload. The badge will do a
   full refresh and show your badge screen.

## Controls

- **Button A**: from the badge screen, opens the menu. Inside the menu,
  cycles through items.
- **Button B**: confirms the highlighted menu item. From the badge
  screen, forces a full refresh (clears any ghosting).

## Notes / things you may want to change

- **Partial refresh**: `adafruit_ssd1680`'s stock `refresh()` always does
  a full (flashing) update. The status bar in the corner currently uses
  the same full refresh, on a 60-second timer, to keep things simple and
  dependency-light. If you want a snappier, non-flashing battery icon
  update, you'll need to either extend `adafruit_ssd1680` to expose the
  SSD1680's partial-refresh LUT/window commands directly, or drop down to
  raw `busio.SPI` + manual command bytes (the datasheet commands are
  `0x21`/`0x22` display update control + `0x44`/`0x45` RAM window +
  `0x24` write RAM + `0x20` master activate, with border waveform `0x3C`
  set to `0x80` for a partial, non-flashing update).
- **Deep sleep**: e-ink is bistable (holds its image with the panel fully
  powered off), so the "Sleep display" menu option here just stops
  issuing refreshes rather than needing to explicitly command the SSD1680
  into its deep-sleep register state. If you want to minimize current
  draw further, look at `alarm`/`microcontroller.deepsleep` in
  CircuitPython to put the RP2350 itself into a low-power state between
  button presses.
- **Battery sensing**: double-check `BATTERY_ADC_PIN` and
  `BATTERY_DIVIDER_RATIO` in `config.py` against your actual resistor
  divider before trusting the percentage shown.
