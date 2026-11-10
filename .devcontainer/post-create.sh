#!/usr/bin/env bash
set -euo pipefail

# Codespaces keeps /workspaces across devcontainer rebuilds. Store raw
# images OUTSIDE the Git working tree so 'git add .' cannot include them.
repo_root="$(git rev-parse --show-toplevel)"
workspace_parent="$(dirname "$repo_root")"
private_root="$workspace_parent/ghostlock-private"

mkdir -p "$private_root/firmware" "$private_root/reports"
chmod 700 "$private_root" "$private_root/firmware" "$private_root/reports"

cd "$repo_root"
printf '\n[HONOR] Read-only Codespaces environment ready.\n'
printf '[HONOR] Firmware directory (outside Git): %s/firmware\n' "$private_root"
printf '[HONOR] Private reports directory: %s/reports\n' "$private_root"
printf '[HONOR] No firmware has been uploaded automatically.\n'
printf '[HONOR] Python: '; python3 --version
printf '[HONOR] Rust: '; cargo --version

# These two test files use synthetic data / mocks; they do not connect
# to ADB or execute the native exploit.
python3 -m unittest discover -s tools -p 'test_inspect_honor_firmware.py' -v
python3 -m unittest discover -s tools -p 'test_probe_honor_x7d_4g.py' -v
