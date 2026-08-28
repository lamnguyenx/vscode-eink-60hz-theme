#!/usr/bin/env python3
"""Generate the light variant by inverting every color of the dark theme.

RGB channels are inverted (255 - c), alpha is preserved. This keeps the exact
same grayscale rendering on e-ink (luminance flips symmetrically) while
producing a coherent color palette for normal monitors.
"""

import json5
import json
import re
import sys
from pathlib import Path

HEX_RE = re.compile(r"#([0-9a-fA-F]{6})([0-9a-fA-F]{2})?")


def invert_color(match: re.Match) -> str:
    rgb = match.group(1)
    alpha = match.group(2) or ""
    r, g, b = (int(rgb[i : i + 2], 16) for i in (0, 2, 4))
    return f"#{255 - r:02x}{255 - g:02x}{255 - b:02x}{alpha}"


def invert_value(value):
    if isinstance(value, str):
        return HEX_RE.sub(invert_color, value)
    if isinstance(value, dict):
        return {k: invert_value(v) for k, v in value.items()}
    if isinstance(value, list):
        return [invert_value(v) for v in value]
    return value


def main() -> None:
    src = Path(sys.argv[1])
    dst = Path(sys.argv[2])
    name = sys.argv[3]

    theme = json5.loads(src.read_text())
    theme = invert_value(theme)
    theme["name"] = name
    dst.write_text(json.dumps(theme, indent="\t") + "\n")
    print(f"Wrote {dst}")


if __name__ == "__main__":
    main()