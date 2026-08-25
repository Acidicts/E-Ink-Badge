# E-Ink Badge

A DIY E-Ink display badge powered by the RP2350A, inspired by the GitHub Universe 2024 conference badge.

<div style="width:100%; display:inline-flex">
    <img style="width:49%" alt="E-Ink Badge render 1" src="https://github.com/user-attachments/assets/56c6940c-3105-4df8-8d04-2791b771ce14" />
    <img style="width:49%" alt="E-Ink Badge render 2" src="https://github.com/user-attachments/assets/baa17b3d-0c78-4348-9072-256c4763411c" />
</div>

*(Renders made in Fusion 360)*

<div style="width:100%;">
    <div style="width:100%; display:inline-flex">
        <img style="width:33%" alt="Assembled badge, main view" src="assets/main.png" />
        <img style="width:33%" alt="E-Ink display detail" src="assets/display.png" />
        <img style="width:33%" alt="Battery mounting detail" src="assets/batteru.png" />
    </div>
    <div style="width:100%; display:inline-flex">
        <img style="width:100%" alt="PCB layout" src="assets/PCB.png" />
    </div>
</div>

## Features

- **MCU:** RP2350A
- **Flash:** 16MB onboard
- **Power:** Integrated battery management for a single-cell LiPo
- **Display:** E-Ink support over SPI
- **Software:** No dedicated firmware/software yet — I'm considering adapting the [Badger 2040](https://github.com/pimoroni/badger2040) software from the GitHub Universe conference badge as a starting point

## Build Guide

This board has some fine-pitch and hand-soldering-unfriendly parts (the RP2350A and the E-Ink display's FPC connector), so I'd recommend using a **PCBA (assembly) service** for the main board rather than hand-soldering it yourself.

Most components will already be populated by the assembly service — you'll only need to install the **battery** and the **display** yourself:

1. **Prepare the battery connector:** Trim the battery connector's legs slightly so they don't press against the back of the display once everything is assembled.
2. **Mount the battery:** Apply adhesive to the marked area on the PCB and stick the battery down.
3. **Connect the battery:** Plug the battery cable into the battery connector on the PCB.
4. **Mount the display:** Apply adhesive to the marked area on the front of the PCB and attach the E-Ink display.
5. **Connect the display cable:** Route the ribbon cable through the indentation/slot in the PCB. Open the FPC connector's clamp arm, insert the ribbon cable, then press the clamp lever back down to lock it in place.

That's it — the badge is fully assembled!

For getting started with software, I'd recommend flashing **CircuitPython**, as it's the easiest way to get up and running. I also have some demo firmware included in this repo, though it's untested/may not work out of the box.

## Firmware

I have some basic firmware in this repo. If you'd like to write your own, here are the SPI pin mappings for the display connection:

### SPI Pinout

| Signal | GPIO |
|--------|------|
| SCLK (Clock)      | GPIO 2 |
| SDI (MOSI/Data)   | GPIO 3 |
| D/C (Data/Command)| GPIO 4 |
| CS (Chip Select)  | GPIO 5 |
| RES (Reset)       | GPIO 6 |
| BUSY              | GPIO 7 |

## Bill of Materials (BOM)

- [Project BOM](./BOM.csv) — full parts list for the badge
- [PCB BOM](./PCB_BOM.md) — parts list specific to the PCB assembly
