# buttons.py - simple debounced button polling.

import time
import digitalio


class Button:
    def __init__(self, pin, active_low=True, debounce_ms=30):
        self._io = digitalio.DigitalInOut(pin)
        self._io.switch_to_input(
            pull=digitalio.Pull.UP if active_low else digitalio.Pull.DOWN
        )
        self._active_low = active_low
        self._debounce_ms = debounce_ms

        self._stable_down = False
        self._raw_down = False
        self._last_change = time.monotonic_ns() // 1_000_000
        self._pending_press = False

    def _raw_is_down(self):
        val = self._io.value
        return (not val) if self._active_low else val

    def poll(self):
        """Call once per loop iteration to update debounced state."""
        now_ms = time.monotonic_ns() // 1_000_000
        down_now = self._raw_is_down()

        if down_now != self._raw_down:
            self._raw_down = down_now
            self._last_change = now_ms
        elif (now_ms - self._last_change) > self._debounce_ms:
            if self._stable_down != self._raw_down:
                self._stable_down = self._raw_down
                if self._stable_down:
                    self._pending_press = True

    def is_down(self):
        return self._stable_down

    def was_pressed(self):
        """Edge-triggered: True once per press, consumes the event."""
        if self._pending_press:
            self._pending_press = False
            return True
        return False
