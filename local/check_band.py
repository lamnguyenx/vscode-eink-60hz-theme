"""
E-ink Band Collision Checker
=============================

Checks whether arbitrary colors fall into the same e-ink gray band,
meaning they'd look indistinguishable on an e-ink display.

Usage:
    python check_band.py #color1 #color2 [#color3 ...]

Output (JSON):
    colors   — each color's hex, luminance, e-ink band, and gap-from-band
    pairs    — every unique pair with same_band: true/false
    conflicts — count of pairs sharing a band

How It Works
-------------
1. Each hex color is converted to perceived luminance using the WCAG formula:
       L = 0.2126·R + 0.7152·G + 0.0722·B

2. The e-ink display can only resolve ~55 distinct gray levels across 9 bands.
   The bands table (below) defines which luminance ranges share the same
   physical gray level on the display.

3. If two colors fall within the same band, they will look the SAME on e-ink
   regardless of their original hue/saturation differences.

Band Table (from e-ink characterization):
    Band  Range    Levels  Description
    1       0–125   31     Very dark (black → medium-dark gray)
    2     130–138    2
    3     142–150    2
    4     154–166    3
    5     170–178    2
    6     182–194    3
    7     198–206    2
    8     210–219    2
    9     223–255    8     Very light (light gray → white)

    Gaps exist between bands (e.g. 126–129, 139–141). Colors in gaps
    are snapped to the nearest band; the "gap" field shows the distance.
"""

import json
import re
import sys

# ── E-ink gray bands ──────────────────────────────────────────────────
# Each entry: (band_id, luminance_min, luminance_max, hex_min, hex_max)
# Colors whose luminance falls within [min, max] map to the same band.
BANDS = [
    (1, 0, 125,   "#000000", "#7d7d7d"),
    (2, 130, 138, "#828282", "#8a8a8a"),
    (3, 142, 150, "#8e8e8e", "#969696"),
    (4, 154, 166, "#9a9a9a", "#a6a6a6"),
    (5, 170, 178, "#aaaaaa", "#b2b2b2"),
    (6, 182, 194, "#b6b6b6", "#c2c2c2"),
    (7, 198, 206, "#c6c6c6", "#cecece"),
    (8, 210, 219, "#d2d2d2", "#dbdbdb"),
    (9, 223, 255, "#dfdfdf", "#ffffff"),
]


def luminance(r: int, g: int, b: int) -> float:
    """
    Perceived brightness using WCAG relative luminance.
    This is what the human eye actually sees — green contributes most,
    blue least.
    """
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def hex_info(raw: str) -> dict:
    """
    Parse a hex color and return its e-ink band info.

    Steps:
      1. Strip #, normalize #rgb → #rrggbb
      2. Compute luminance
      3. Find which band the luminance falls into
         - If it's outside all bands (in a gap), snap to the nearest band
         - 'gap' shows the distance to the band boundary (0 = exact fit)
    """
    h = raw.lstrip("#")[:6]
    if len(h) == 3:
        h = "".join(c * 2 for c in h)

    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    lum = luminance(r, g, b)

    best_band = None
    best_dist = float("inf")

    for bid, lo, hi, _, _ in BANDS:
        if lo <= lum <= hi:
            best_band, best_dist = bid, 0
            break
        dist = min(abs(lum - lo), abs(lum - hi))
        if dist < best_dist:
            best_dist = dist
            best_band = bid

    return {
        "hex": f"#{h}",
        "luminance": round(lum, 2),
        "band": best_band,
        "gap": round(best_dist, 1) if best_dist else 0,
    }


# ── CLI ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if re.match(r"^#?[0-9a-fA-F]{3,8}", a)]

    if not args:
        print(__doc__)
        sys.exit(0)

    colors = [hex_info(a) for a in args]

    pairs = []
    for i in range(len(args)):
        for j in range(i + 1, len(args)):
            ci, cj = colors[i], colors[j]
            pairs.append({
                "a": args[i],
                "b": args[j],
                "a_info": ci,
                "b_info": cj,
                "same_band": ci["band"] == cj["band"],
            })

    result = {
        "colors": colors,
        "pairs": pairs,
        "total": len(colors),
        "pair_count": len(pairs),
        "conflicts": sum(1 for p in pairs if p["same_band"]),
    }

    print(json.dumps(result, indent=2))
