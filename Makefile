# Eink 60Hz theme build & merge targets
# - build/hotbuild: package the extension into out/*.vsix
# - mate/css: merge the standalone rules/CSS into VS Code settings.json
.PHONY: build install hotbuild mate css light

# Package the extension into out/*.vsix (requires npx)
build:
	npx @vscode/vsce package --out out/

# Install the newest .vsix from out/ into VS Code (requires the `code` CLI)
install:
	code --install-extension $$(ls -t out/*.vsix | head -1) --force

# Build and install in one step — for quick iteration
hotbuild: build install

# Merge the standalone TextMate font-style rules into settings.json
# (backs up settings.json to .bak first; requires json5 + deepmerge)
mate:
	python3 local/merge_config.py text-mate-rules/eink_60hz_text.json

# Merge the custom UI CSS tweaks into settings.json
# (backs up settings.json to .bak first; requires json5 + deepmerge)
css:
	python3 local/merge_css.py themes/eink_60hz.css

# Regenerate the light theme as the exact inversion of the dark theme
light:
	python3 local/invert_theme.py themes/eink_60hz_dark.json themes/eink_60hz_light.json "Eink 60Hz (Light)"
