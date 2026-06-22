.PHONY: build install hotbuild mate css

build:
	npx @vscode/vsce package --out out/

install:
	code --install-extension $$(ls -t out/*.vsix | head -1) --force

hotbuild: build install

mate:
	python3 local/merge_config.py text-mate-rules/dark_plus_text.json

css:
	python3 local/merge_css.py themes/dark_plus.css
