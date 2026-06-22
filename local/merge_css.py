#!/usr/bin/env python3
"""Merge VS Code custom UI CSS into settings.json using deepmerge."""

import sys
from pathlib import Path

import json5
from deepmerge import always_merger


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: merge_css.py <css_file> [settings.json]")
        sys.exit(1)

    css_file = Path(sys.argv[1])
    if not css_file.exists():
        print(f"Error: {css_file} not found")
        sys.exit(1)

    if len(sys.argv) > 2:
        settings_path = Path(sys.argv[2])
    else:
        settings_path = Path.home() / "Library/Application Support/Code/User/settings.json"

    if not settings_path.exists():
        print(f"Error: {settings_path} not found")
        sys.exit(1)

    css_content = css_file.read_text().strip()

    settings = json5.loads(settings_path.read_text())

    backup_path = settings_path.with_suffix(".json.bak")
    settings_path.write_text(json5.dumps(settings, indent=4) + "\n")

    always_merger.merge(settings, {"customvscodeuicss.css": css_content})

    import json
    settings_path.write_text(json.dumps(settings, indent=4) + "\n")

    print(f"Merged CSS ({len(css_content)} chars) into {settings_path}")
    print(f"Backup: {backup_path}")


if __name__ == "__main__":
    main()
