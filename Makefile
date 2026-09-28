NAME    := $(shell node -p "require('./package.json').name")
VERSION := $(shell node -p "require('./package.json').version")
PUB     := $(shell node -p "require('./package.json').publisher")
EXT_ID  := $(PUB).$(NAME)-$(VERSION)
VSIX    := build/$(EXT_ID).vsix

# Eink 60Hz theme build & merge targets
# - build/hotbuild: package the extension into build/*.vsix
# - mate/css: merge the standalone rules/CSS into VS Code settings.json
.PHONY: build install hotbuild vsix mate css light

build: vsix

install: build
	code --install-extension $(VSIX) --force

# Build and install in one step — for quick iteration
hotbuild: build install

# Package the extension into build/*.vsix (requires npx)
vsix:
	mkdir -p build
	npx --yes @vscode/vsce pack -o $(VSIX)

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
