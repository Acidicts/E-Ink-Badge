# battery.py - battery voltage sensing + rough state-of-charge estimate for
# the E-Ink Badge (BQ24040 charger + TPS63060 buck-boost).
#
# NOTE: GET_STARTED.md (the badge's hardware doc) only documents the e-ink
# SPI pins - it doesn't call out a battery-voltage-sense ADC pin. This
# module assumes VBAT is divided down and fed into BATTERY_ADC_PIN (see
# config.py). If your board doesn't route battery voltage to an ADC pin,
# call battery.Battery(adc_pin=None) and the class will fall back to
# reporting a fixed "unknown" percentage - update DIVIDER_RATIO to match
# your actual resistor divider if you do have one wired up.

import analogio

# LiPo rest-voltage -> state-of-charge lookup table (single cell, ~25C,
# no load compensation). Good enough for a badge battery icon, not a fuel
# gauge.
_CURVE = (
    (4.20, 100),
    (4.10, 95),
    (4.00, 87),
    (3.90, 72),
    (3.80, 55),
    (3.70, 38),
    (3.60, 20),
    (3.50, 10),
    (3.40, 5),
    (3.30, 2),
    (3.00, 0),
)


def _voltage_to_percent(v):
    if v >= _CURVE[0][0]:
        return 100
    if v <= _CURVE[-1][0]:
        return 0
    for i in range(len(_CURVE) - 1):
        hi_v, hi_p = _CURVE[i]
        lo_v, lo_p = _CURVE[i + 1]
        if lo_v <= v <= hi_v:
            t = (v - lo_v) / (hi_v - lo_v)
            return int(lo_p + t * (hi_p - lo_p))
    return 0


class Battery:
    """Reads battery voltage via a divided ADC pin and estimates charge %.

    Args:
        adc_pin: board pin for the battery-sense ADC input, or None if not
            wired on your board (percent readings will be a fixed
            placeholder).
        divider_ratio: Vbat = Vadc * divider_ratio. Set to 1.0 if the ADC
            pin is connected directly to VBAT (only safe if VBAT never
            exceeds the MCU's ADC reference, e.g. reading the 3.3V rail
            downstream of a regulator rather than raw LiPo voltage).
        charging_pin: optional digitalio input wired to the charger's
            STAT/CHG pin (BQ24040 is open-drain active-low while charging).
    """

    def __init__(self, adc_pin=None, divider_ratio=2.0, charging_pin=None):
        self._adc = analogio.AnalogIn(adc_pin) if adc_pin is not None else None
        self._divider_ratio = divider_ratio
        self._charging_pin = charging_pin

    def read_voltage(self, samples=8):
        """Return battery voltage in volts (oversampled), or None if no
        ADC pin is configured."""
        if self._adc is None:
            return None
        acc = 0
        for _ in range(samples):
            acc += self._adc.value
        raw = acc / samples
        v_adc = (raw / 65535) * 3.3  # CircuitPython AnalogIn is 16-bit scaled
        return v_adc * self._divider_ratio

    def read_percent(self):
        """Return an estimated state-of-charge 0-100, or -1 if unknown."""
        v = self.read_voltage()
        if v is None:
            return -1
        return _voltage_to_percent(v)

    def is_charging(self):
        """Return True/False if a charge-status pin is configured, else
        None (unknown)."""
        if self._charging_pin is None:
            return None
        # BQ24040 STAT is open-drain active-low while charging.
        return not self._charging_pin.value
