#!/usr/bin/env bash
set -euo pipefail

# The unprivileged vscode user cannot necessarily create directories in
# /workspaces. Use an ignored directory inside the writable checkout instead.
# The .gitignore rule prevents accidental "git add ." of private firmware;
# it is NOT encryption and force-adding can bypass the ignore rule.
repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"
if ! git check-ignore -q -- .ghostlock-private/; then
  printf '[HONOR] ERROR: .ghostlock-private/ must be ignored by Git.\n' >&2
  exit 1
fi
private_root="$repo_root/.ghostlock-private"

mkdir -p "$private_root/firmware" "$private_root/reports"
chmod 700 "$private_root" "$private_root/firmware" "$private_root/reports"

printf '\n[HONOR] Read-only Codespaces environment ready.\n'
printf '[HONOR] Firmware directory (Git-ignored): %s/firmware\n' "$private_root"
printf '[HONOR] Private reports directory: %s/reports\n' "$private_root"
printf '[HONOR] No firmware has been uploaded automatically.\n'
printf '[HONOR] Python: '; python3 --version
printf '[HONOR] Rust: '; cargo --version

# These two test files use synthetic data / mocks; they do not connect
# to ADB or execute the native exploit.
python3 -m unittest discover -s tools -p 'test_inspect_honor_firmware.py' -v
python3 -m unittest discover -s tools -p 'test_probe_honor_x7d_4g.py' -v
