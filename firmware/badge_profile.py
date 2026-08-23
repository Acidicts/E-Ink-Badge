# badge_profile.py - loads /badge_profile.txt (plain key = value text) so
# the badge can be personalized by editing a text file over USB instead of
# needing to touch Python code.

_DEFAULTS = {
    "name": "Your Name",
    "pronouns": "they/them",
    "role": "Attendee",
    "handle": "@handle",
}


def load(path="/badge_profile.txt"):
    """Parse the profile text file and return a dict with at least the
    keys in _DEFAULTS. Missing file or missing keys fall back to
    defaults so the badge still boots and shows something sensible."""
    values = dict(_DEFAULTS)
    try:
        with open(path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    continue
                key, _, val = line.partition("=")
                key = key.strip().lower()
                val = val.strip()
                if key in values and val:
                    values[key] = val
    except OSError:
        # File missing - just use defaults.
        pass
    return values
