## Project Structure

- `_refs/` is a reference folder containing symlinks to external projects. Do not modify files through these symlinks; they are read-only references.
  - `_refs/vscode/` is the codebase of original vscode. Do not edit this.
  - `_refs/vscode.settings.json` is the symlink to the vscode `settings.json` file on this machine. You must ask user before editing this. And always back it up before a session of editting.
- `./exp` is used as the temporary directory for experiments, outputs, or scratch data; you may recreate it if not exist.