#!/usr/bin/env python3
"""Merge textmate rules (jsonc) into VS Code settings.json using deepmerge."""

import json
import sys
from pathlib import Path

import json5
from deepmerge import always_merger


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: merge_config.py <textmate_rules.json> [settings.json]")
        sys.exit(1)

    tm_file = Path(sys.argv[1])
    if not tm_file.exists():
        print(f"Error: {tm_file} not found")
        sys.exit(1)

    if len(sys.argv) > 2:
        settings_path = Path(sys.argv[2])
    else:
        settings_path = Path.home() / "Library/Application Support/Code/User/settings.json"

    if not settings_path.exists():
        print(f"Error: {settings_path} not found")
        sys.exit(1)

    tm_data = json5.loads(tm_file.read_text())

    settings = json5.loads(settings_path.read_text())

    backup_path = settings_path.with_suffix(".json.bak")
    settings_path.write_text(json.dumps(settings, indent=4) + "\n")

    always_merger.merge(settings, tm_data)

    settings_path.write_text(json.dumps(settings, indent=4) + "\n")

    rule_count = len(tm_data.get("editor.tokenColorCustomizations", {}).get("textMateRules", []))
    print(f"Merged {rule_count} textMate rules into {settings_path}")
    print(f"Backup: {backup_path}")


if __name__ == "__main__":
    main()
