# E-Ink-Badge
I made a Eink display badge powered by the rp2350A inspired by the github universe conference badge from 2024

<div style="width:100%; display:inline-flex">
    <img style="width:49%" alt="E-Ink_Badge_2026-May-11_04-48-37PM-000_CustomizedView35901139220" src="https://github.com/user-attachments/assets/56c6940c-3105-4df8-8d04-2791b771ce14" />
    <img style="width:49%" alt="E-Ink_Badge_2026-May-11_04-48-49PM-000_CustomizedView10564322915" src="https://github.com/user-attachments/assets/baa17b3d-0c78-4348-9072-256c4763411c" />
</div>
(Renders made on Fusion 360)

<div style="width:100%;">
    <div style="width:100%; display:inline-flex">
        <img style="width:33%" alt="E-Ink_Badge_2026-May-11_04-48-37PM-000_CustomizedView35901139220" src="assets/main.png" />
        <img style="width:33%" alt="E-Ink_Badge_2026-May-11_04-48-37PM-000_CustomizedView35901139220" src="assets/display.png" />
        <img style="width:33%" alt="E-Ink_Badge_2026-May-11_04-48-37PM-000_CustomizedView35901139220" src="assets/batteru.png" />
    </div>
    <div style="width:100%; display:inline-flex">
        <img style="width:100%" alt="E-Ink_Badge_2026-May-11_04-48-37PM-000_CustomizedView35901139220" src="assets/PCB.png" />
    </div>
</div>

# Features
- Currently I hvae made no software for it but I may try to adapt the badger software from the conference badge
- RP2350A
- 16MB of flash
- Battery Management
- E-INK Display Support over SPI

# Build Guide
I would recommend using a pcba service for this as has many parts which may be difficult to solder (rp2350A and the eink display connetor)

As most parts will be on already except battery and display, I would recommend cutting the battery connector legs a bit so they don't press against the display. After that use an ahesive to stick the battery to the marked area on the pcb, then use the battery connector to connect the battery cable to the pcb. After that, you can install the eink display use an adhesive to mount it to the front of the pcb in the marked area, then loop the riboncable through the indentation in the pcb, open the fpc connector clamp arm and place the cable in before push the lever down.

Now you are done!!!
I would recommend running circuitpython on it as it is the easiest way to get started with it although I do have some demo code which may or may not work.

# Firmware
So I have some simple firmware but for anyone who plans to create their own here are the pinouts for spi connected to the display:
### SPI Pins:
- SCLK GPIO 2
- SDI GPIO 3
- D/C GPIO 4
- CS GPIO 5
- RES GPIO 6
- BUSY GPIO 7


# BOMs
[PROJECT BOM](./BOM.csv)
[PCB BOM](./PCB_BOM.md)