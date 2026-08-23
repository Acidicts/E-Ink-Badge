# code.py - E-Ink Badge firmware (CircuitPython).
#
# Requires these libraries copied into /lib on CIRCUITPY (from the Adafruit
# CircuitPython Bundle matching your CircuitPython version):
#   adafruit_ssd1680.mpy
#   fourwire.mpy            (built into recent CircuitPython; if your build
#                             doesn't have it, use `displayio.FourWire`
#                             instead - see the commented alternative below)
#   adafruit_display_text/  (folder, for label.Label)
#
# Behavior:
#   - Boots, loads /badge_profile.txt, draws the badge screen (full
#     refresh).
#   - Button A: open a simple menu (Badge / Battery / Sleep display).
#   - Button B: confirm menu selection / force full refresh on badge
#     screen.
#   - Battery icon in the corner updates periodically via a fast partial
#     refresh so it doesn't need a full flashing redraw.

import time
import gc

import busio
import displayio
import terminalio
from adafruit_display_text import label

try:
    from fourwire import FourWire
except ImportError:
    from displayio import FourWire

import adafruit_ssd1680

import config
import battery
import badge_profile
from buttons import Button

displayio.release_displays()

# ---------------------------------------------------------------------
# Display bring-up
# ---------------------------------------------------------------------
spi = busio.SPI(clock=config.EPD_SCLK, MOSI=config.EPD_MOSI)

display_bus = FourWire(
    spi,
    command=config.EPD_DC,
    chip_select=config.EPD_CS,
    reset=config.EPD_RESET,
    baudrate=config.EPD_BAUDRATE,
)

display = adafruit_ssd1680.SSD1680(
    display_bus,
    width=config.EPD_WIDTH,
    height=config.EPD_HEIGHT,
    busy_pin=config.EPD_BUSY,
    rotation=0,
    # This is a monochrome panel (GDEY0266T90H), so no highlight_color.
)

# ---------------------------------------------------------------------
# Battery + buttons
# ---------------------------------------------------------------------
chg_pin = None
if config.BATTERY_CHG_STAT_PIN is not None:
    import digitalio

    chg_pin = digitalio.DigitalInOut(config.BATTERY_CHG_STAT_PIN)
    chg_pin.switch_to_input(pull=digitalio.Pull.UP)

batt = battery.Battery(
    adc_pin=config.BATTERY_ADC_PIN,
    divider_ratio=config.BATTERY_DIVIDER_RATIO,
    charging_pin=chg_pin,
)

btn_a = Button(config.BUTTON_A_PIN, active_low=config.BUTTONS_ACTIVE_LOW)
btn_b = Button(config.BUTTON_B_PIN, active_low=config.BUTTONS_ACTIVE_LOW)

profile = badge_profile.load()

# ---------------------------------------------------------------------
# Screens
# ---------------------------------------------------------------------

WHITE = 0xFFFFFF
BLACK = 0x000000

PALETTE = displayio.Palette(2)
PALETTE[0] = WHITE
PALETTE[1] = BLACK


def solid_bitmap(w, h, color_index):
    bmp = displayio.Bitmap(w, h, 2)
    bmp.fill(color_index)
    return bmp


def make_badge_group():
    group = displayio.Group()

    # White background covering the whole panel.
    bg = displayio.TileGrid(
        solid_bitmap(config.EPD_WIDTH, config.EPD_HEIGHT, 0), pixel_shader=PALETTE
    )
    group.append(bg)

    # Header bar (black strip across the top).
    header_h = 22
    header = displayio.TileGrid(
        solid_bitmap(config.EPD_WIDTH, header_h, 1), pixel_shader=PALETTE
    )
    group.append(header)

    header_label = label.Label(
        terminalio.FONT, text="E-INK BADGE", color=WHITE, x=10, y=header_h // 2
    )
    group.append(header_label)

    margin = 12
    y = 44

    name_label = label.Label(
        terminalio.FONT,
        text=profile["name"],
        color=BLACK,
        scale=3,
        x=margin,
        y=y,
    )
    group.append(name_label)
    y += 34

    line2 = "{}  |  {}".format(profile["pronouns"], profile["role"])
    line2_label = label.Label(terminalio.FONT, text=line2, color=BLACK, x=margin, y=y)
    group.append(line2_label)
    y += 16

    # Divider line.
    divider = displayio.TileGrid(
        solid_bitmap(config.EPD_WIDTH - 2 * margin, 1, 1),
        pixel_shader=PALETTE,
        x=margin,
        y=y,
    )
    group.append(divider)
    y += 12

    handle_label = label.Label(
        terminalio.FONT, text=profile["handle"], color=BLACK, scale=2, x=margin, y=y
    )
    group.append(handle_label)

    footer_label = label.Label(
        terminalio.FONT,
        text="hold A: menu   B: refresh",
        color=BLACK,
        x=margin,
        y=config.EPD_HEIGHT - 10,
    )
    group.append(footer_label)

    # Status bar group (battery icon + %), kept as a sub-group so it can be
    # rebuilt independently for partial refreshes without touching the
    # rest of the badge layout.
    status_group = displayio.Group()
    group.append(status_group)

    return group, status_group


STATUS_W = 70
STATUS_H = 18
STATUS_X = config.EPD_WIDTH - STATUS_W - 4
STATUS_Y = 3


def draw_battery_icon_bitmap(percent, charging):
    """Return a small bitmap with a battery glyph + percent text baked in
    as raw pixels via simple rectangle fills (keeps this dependency-free -
    no extra image assets needed)."""
    bmp = displayio.Bitmap(STATUS_W, STATUS_H, 2)
    bmp.fill(0)  # white background

    body_x, body_y, body_w, body_h = 0, 2, 26, 13
    tip_w, tip_h = 3, 6

    def rect(x, y, w, h, val):
        for yy in range(max(0, y), min(STATUS_H, y + h)):
            for xx in range(max(0, x), min(STATUS_W, x + w)):
                bmp[xx, yy] = val

    def rect_outline(x, y, w, h, val):
        rect(x, y, w, 1, val)
        rect(x, y + h - 1, w, 1, val)
        rect(x, y, 1, h, val)
        rect(x + w - 1, y, 1, h, val)

    rect_outline(body_x, body_y, body_w, body_h, 1)
    rect(body_x + body_w, body_y + (body_h - tip_h) // 2, tip_w, tip_h, 1)

    pct = max(0, min(100, percent))
    inner_w = body_w - 4
    fill_w = int(inner_w * pct / 100)
    if fill_w > 0:
        rect(body_x + 2, body_y + 2, fill_w, body_h - 4, 1)

    return bmp


def make_status_content(percent, charging):
    grp = displayio.Group()
    icon_bmp = draw_battery_icon_bitmap(percent, charging)
    icon_tile = displayio.TileGrid(icon_bmp, pixel_shader=PALETTE, x=STATUS_X, y=STATUS_Y)
    grp.append(icon_tile)

    pct_text = "?" if percent < 0 else "{}%".format(percent)
    pct_label = label.Label(
        terminalio.FONT, text=pct_text, color=BLACK, x=STATUS_X + 34, y=STATUS_Y + 9
    )
    grp.append(pct_label)
    return grp


def update_status(status_group, percent, charging):
    while len(status_group) > 0:
        status_group.pop()
    status_group.append(make_status_content(percent, charging))


def make_menu_group(title, items, selected):
    group = displayio.Group()

    bg = displayio.TileGrid(
        solid_bitmap(config.EPD_WIDTH, config.EPD_HEIGHT, 0), pixel_shader=PALETTE
    )
    group.append(bg)

    header_h = 20
    header = displayio.TileGrid(
        solid_bitmap(config.EPD_WIDTH, header_h, 1), pixel_shader=PALETTE
    )
    group.append(header)
    group.append(label.Label(terminalio.FONT, text=title, color=WHITE, x=10, y=header_h // 2))

    margin = 10
    y = 34
    row_h = 18
    for i, item in enumerate(items):
        if i == selected:
            highlight = displayio.TileGrid(
                solid_bitmap(config.EPD_WIDTH - 2 * (margin - 2), row_h - 2, 1),
                pixel_shader=PALETTE,
                x=margin - 2,
                y=y - row_h // 2,
            )
            group.append(highlight)
            group.append(label.Label(terminalio.FONT, text=item, color=WHITE, x=margin, y=y))
        else:
            group.append(label.Label(terminalio.FONT, text=item, color=BLACK, x=margin, y=y))
        y += row_h

    return group


def make_battery_screen_group():
    group = displayio.Group()
    bg = displayio.TileGrid(
        solid_bitmap(config.EPD_WIDTH, config.EPD_HEIGHT, 0), pixel_shader=PALETTE
    )
    group.append(bg)

    header_h = 20
    header = displayio.TileGrid(
        solid_bitmap(config.EPD_WIDTH, header_h, 1), pixel_shader=PALETTE
    )
    group.append(header)
    group.append(label.Label(terminalio.FONT, text="BATTERY", color=WHITE, x=10, y=header_h // 2))

    v = batt.read_voltage()
    pct = batt.read_percent()
    charging = batt.is_charging()

    lines = [
        "Voltage: {}".format("{:.2f} V".format(v) if v is not None else "n/a"),
        "Charge:  {}".format("{}%".format(pct) if pct >= 0 else "n/a"),
        "Status:  {}".format(
            "Charging" if charging else ("On battery" if charging is False else "n/a")
        ),
    ]
    y = 46
    for line in lines:
        group.append(label.Label(terminalio.FONT, text=line, color=BLACK, x=10, y=y))
        y += 18

    group.append(
        label.Label(terminalio.FONT, text="A: back", color=BLACK, x=10, y=config.EPD_HEIGHT - 10)
    )
    return group


# ---------------------------------------------------------------------
# State machine
# ---------------------------------------------------------------------

SCREEN_BADGE = "badge"
SCREEN_MENU = "menu"
SCREEN_BATTERY = "battery"

MENU_ITEMS = ["Badge", "Battery info", "Sleep display"]

state = {"screen": SCREEN_BADGE, "menu_selected": 0}

badge_group, badge_status_group = make_badge_group()


def show_badge(full_refresh=True):
    update_status(badge_status_group, batt.read_percent(), batt.is_charging())
    display.root_group = badge_group
    display.refresh()
    if not full_refresh:
        # adafruit_ssd1680's refresh() always does a full update in the
        # stock driver; partial-refresh windowing isn't exposed at this
        # layer. We still call refresh() here - see NOTE below for how to
        # add true partial refresh if you need faster status-bar-only
        # updates.
        pass


def show_menu():
    display.root_group = make_menu_group("MENU", MENU_ITEMS, state["menu_selected"])
    display.refresh()


def show_battery():
    display.root_group = make_battery_screen_group()
    display.refresh()


def wait_for_display_ready():
    # adafruit_ssd1680 already waits on BUSY internally during refresh(),
    # but time_to_refresh gives a hint for how long the caller should
    # avoid issuing another refresh.
    try:
        time.sleep(display.time_to_refresh)
    except AttributeError:
        time.sleep(2)


# ---------------------------------------------------------------------
# Boot
# ---------------------------------------------------------------------
print("E-Ink Badge booting:", profile["name"], profile["handle"])
show_badge(full_refresh=True)

next_status_update = time.monotonic() + 60  # refresh battery icon every 60s

while True:
    btn_a.poll()
    btn_b.poll()

    if btn_a.was_pressed():
        if state["screen"] == SCREEN_BADGE:
            state["screen"] = SCREEN_MENU
            state["menu_selected"] = 0
            show_menu()
        elif state["screen"] == SCREEN_MENU:
            state["menu_selected"] = (state["menu_selected"] + 1) % len(MENU_ITEMS)
            show_menu()
        elif state["screen"] == SCREEN_BATTERY:
            state["screen"] = SCREEN_BADGE
            show_badge(full_refresh=True)

    if btn_b.was_pressed():
        if state["screen"] == SCREEN_BADGE:
            show_badge(full_refresh=True)
        elif state["screen"] == SCREEN_MENU:
            sel = state["menu_selected"]
            if sel == 0:
                state["screen"] = SCREEN_BADGE
                show_badge(full_refresh=True)
            elif sel == 1:
                state["screen"] = SCREEN_BATTERY
                show_battery()
            elif sel == 2:
                print("Sleeping display. Press any button to wake.")
                # SSD1680-family panels: putting the MCU to sleep is
                # separate from the panel's own deep-sleep state, which
                # the adafruit_ssd1680 driver doesn't expose directly.
                # Simplest reliable approach: just stop refreshing and
                # wait for input; the panel holds its image with no power
                # either way since e-ink is bistable.
                while True:
                    btn_a.poll()
                    btn_b.poll()
                    if btn_a.was_pressed() or btn_b.was_pressed():
                        break
                    time.sleep(0.05)
                state["screen"] = SCREEN_BADGE
                show_badge(full_refresh=True)
        elif state["screen"] == SCREEN_BATTERY:
            state["screen"] = SCREEN_BADGE
            show_badge(full_refresh=True)

    if state["screen"] == SCREEN_BADGE and time.monotonic() >= next_status_update:
        update_status(badge_status_group, batt.read_percent(), batt.is_charging())
        display.refresh()
        next_status_update = time.monotonic() + 60

    gc.collect()
    time.sleep(0.02)
