# boot.py - runs once at power-up/reset, before code.py.
#
# By default CIRCUITPY is writable from your computer over USB but
# read-only from code.py. Since this badge doesn't need to write its own
# files at runtime (profile is a plain text file you edit over USB), we
# leave the default behavior alone. If you later want code.py to write
# things (e.g. saving the last-selected menu screen), you can make the
# filesystem writable from CircuitPython with storage.remount, but that
# makes it read-only from USB while running - see the commented example.

import board
import digitalio

# Hold button A during boot to force-remount CIRCUITPY as writable from
# the host computer even if something below would normally change that -
# handy if a previous experiment left the drive in a weird state.
# (No-op here since we don't remount by default, but the pin read is kept
# as a harmless placeholder / example.)
_boot_btn = digitalio.DigitalInOut(board.GP10)
_boot_btn.switch_to_input(pull=digitalio.Pull.UP)
_safe_mode_requested = not _boot_btn.value
_boot_btn.deinit()

# Example (disabled): make storage writable by CircuitPython code and
# read-only over USB, useful once you add persistent settings:
#
# import storage
# storage.remount("/", readonly=False)
