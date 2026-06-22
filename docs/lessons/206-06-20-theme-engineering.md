# Lessons Learned — VS Code Theme Engineering

**Session**: 2026-06-20

---

## 1. `uiTheme` is the key to UI chrome styling

`package.json` → `contributes.themes[].uiTheme` controls which base UI theme VS Code uses for
all chrome (status bar, activity bar, sidebar, tabs, panels, menus, etc.). The theme file's
`colors` section only needs to cover the **editor area** (background, selection, etc.).

| `uiTheme` | Effect |
|---|---|
| `"vs-dark"` | Default dark UI chrome (blue status bar) |
| `"hc-black"` | High-contrast black chrome — status bar, activity bar, borders all get high-contrast treatment automatically |

**Mistake**: Had `"vs-dark"` for hours — status bar stayed blue, borders weren't white.
**Fix**: Changed to `"hc-black"` — everything snapped into high-contrast immediately.

---

## 2. Theme `include` is unreliable — inline instead

VS Code added `"include": "./base.json"` in v1.97 for color theme inheritance. It merges
the included theme's colors, tokenColors, and semanticTokenColors. However:

- The feature is version-dependent (v1.97+ only).
- Even when supported, it may not resolve relative paths correctly in all extension contexts.
- With `include`, the theme file has a runtime dependency on another file being present.

**Best practice**: Fully inline the base content. Make the theme file self-contained.
This guarantees it works on any VS Code version.

---

## 3. Font styles stack on top of foreground colors

In VS Code's token color engine, rules are applied **in array order**. Each matching rule's
settings are merged — if a later rule has `fontStyle: "bold"` but no `foreground`, the
foreground from an earlier matching rule is preserved.

This means a theme can:
1. Define foreground colors once (from the base)
2. Append fontStyle-only rules at the end (our overrides)

The fontStyle rules layer on top without touching the foregrounds.

---

## 4. Semver: no leading zeros

VS Code extension packaging uses strict semver. `"2026.06.20-01"` **fails** because:
- `06` has a leading zero — not allowed in semver numeric parts
- `01` has a leading zero — same

Correct: `"2026.6.20-1"` (no leading zeros). For multiple daily releases: `-1`, `-2`, etc.

Error message from `vsce package`:
```
ERROR  Invalid extension "version": "2026.06.20-01" in package.json.
```

---

## 5. Use `json5` to parse JSON-with-comments (JSONC)

VS Code supports `//` comments in settings.json and other configuration files. Standard
`json.loads()` rejects comments and trailing commas.

**Solution**: Use the `json5` Python library — it handles both `//` comments and trailing
commas natively. Write output with `json.dumps()` (strict JSON for VS Code consumption).

```python
import json5, json
data = json5.loads(file_with_comments.read_text())
output = json.dumps(data, indent=4)  # strict JSON output
```

---

## 6. `deepmerge` for settings merging (kubeconfig style)

The `deepmerge` Python library recursively merges dicts — exactly like `kubectl config merge`.
It replaces matching keys with the override value while preserving all other keys untouched.

```python
from deepmerge import always_merger
settings = load("settings.json")
tm_rules = load("textmate_rules.json")
always_merger.merge(settings, tm_rules)
# only editor.tokenColorCustomizations is replaced, all 90+ other keys preserved
```

---

## 7. Custom UI CSS (`customvscodeuicss`) vs theme colors

Most DOM-level CSS rules have **no theme color key equivalent**. Even in VS Code 1.125:

| Themable via colors | Not themable (CSS-only) |
|---|---|
| `button.background`, `button.border`, `button.separator` | SCM section backgrounds (staged/changes) |
| `contrastBorder` (separator lines) | Font family, size, weight |
| All standard editor/UI colors | Layout (width, padding) |
| | Directory icon pseudo-elements |
| | `iframe` content styling |
| | Terminal padding |

**Conclusion**: For a complete look, you need **both** a color theme AND CSS overrides.
They serve different layers of the UI.

---

## 8. The 9 TextMate scope categories

Every code element that gets syntax-colored falls into one of these TextMate scope families:

| # | Category | Scopes | Purpose |
|---|---|---|---|
| 1 | `comment` | `comment` | Code comments |
| 2 | `string` | `string`, `string.regexp` | String literals |
| 3 | `constant` | `constant.numeric`, `constant.language` | Numbers, language constants |
| 4 | `keyword` | `keyword`, `keyword.control`, `keyword.operator` | Language keywords |
| 5 | `storage` | `storage.type`, `storage.modifier` | `def`, `class`, `static` |
| 6 | `variable` | `variable`, `variable.language.this` | Variables |
| 7 | `support` | `support.function`, `support.type` | Built-in functions/types |
| 8 | `entity` | `entity.name.tag`, `entity.name.function` | Named things |
| 9 | `markup` | `markup.heading`, `markup.inserted` | Markdown/diff |

Plus auxiliary: `meta` (preprocessor, embedded), `invalid` (errors), `punctuation` (brackets).

---

## 9. `.vscodeignore` is essential for clean VSIX packaging

Without it, `vsce package` includes every file in the repo — `.gitignore`, `Makefile`,
`__pycache__/`, dev scripts, etc. The secret scanner also chokes on directories (`EISDIR` error
when trying to read `__pycache__/`).

```ini
.vscode/**
.gitignore
Makefile
__pycache__/**
*.pyc
check_band.py
_refs/**
eink-gray-colors-bands.md
```

---

## 10. `make` targets for settings merging

Two independent merge scripts, each with a Makefile target:

```
make mate   →  merge textMate rules → settings.json
make css    →  merge custom UI CSS  → settings.json
```

Both backup `settings.json` to `settings.json.bak` before writing. Both use `deepmerge`
to touch only their target key, preserving all other settings.
