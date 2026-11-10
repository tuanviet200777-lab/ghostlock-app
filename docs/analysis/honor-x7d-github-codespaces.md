# HONOR X7d 4G read-only research in GitHub Codespaces

See [Vietnamese quick-start](../../.devcontainer/README.md) and
[Chinese translation](honor-x7d-github-codespaces_ZH.md).

## Creating the Codespace
1. Open the repository on GitHub and select the
   `tools/honor-x7d-firmware-readonly-analysis` branch (PR #3).
2. Select **Code → Codespaces → Create codespace on this branch**.
3. GitHub builds `.devcontainer/devcontainer.json` (Ubuntu 24.04, Python 3.12,
   Rust stable, Git LFS, and offline analysis utilities).
4. The post-create script runs the two Python test suites and creates
   `/workspaces/ghostlock-private/firmware/` and
   `/workspaces/ghostlock-private/reports/` **outside the Git checkout**.

The branch currently has a prepared configuration, not a guaranteed already
running Codespace. This GitHub connector does not create or control Codespaces
in the owner's account. Codespaces may incur usage/storage charges.

## Data provenance and privacy
Only inspect files whose origin and permission to process have been checked.
Do **not** upload `userdata.img`, `metadata.img`, `cache.img`, secrets,
key partitions, or raw personal dumps. Codespace storage is hosted remotely;
the private directory reduces accidental Git commits but is not encryption or
a backup guarantee. GitHub documents that `/workspaces` persists on container
rebuild; deletion or retention policy may still remove the workspace.

The owner confirmed **MagicOS 9.0.0.226**. A previous mistaken GitHub device
report is explicitly excluded as evidence. The kernel string from an uploaded
`boot(2).img` is not a measured on-device `uname -r`.

Codespaces cannot automatically reach a phone plugged into the owner's PC.
Collect optional ADB reports locally and review them before transferring them
to cloud storage; do not share private identifiers.

## Offline analysis command

Place reviewed boot/vendor-boot/version files in the firmware directory, then
run from the Codespace terminal in the repository root:

```bash
python3 tools/inspect_honor_firmware.py \
  --boot "/workspaces/ghostlock-private/firmware/boot(2).img" \
  --vendor-boot "/workspaces/ghostlock-private/firmware/vendor_boot(2).img" \
  --version-tag "/workspaces/ghostlock-private/firmware/version_by_CI(1).tag" \
  --out "/workspaces/ghostlock-private/reports/x7d-226-offline.json"
```

For offline unit tests:

```bash
python3 -m unittest discover -s tools -p 'test_inspect_honor_firmware.py' -v
python3 -m unittest discover -s tools -p 'test_probe_honor_x7d_4g.py' -v
```

The separate GitHub Actions workflow
`.github/workflows/honor-firmware-tools.yml` checks JSON/Bash syntax and
runs both suites on PRs or scoped pushes. On PRs and manual dispatch it also
uses `devcontainers/ci@v0.3` to **build the complete image** (including
Features) and run the safe checks **inside** the container, without pushing
an image to any registry. The repo's Android build is independent.

The existing Rust `tools/extract_rs` is available for **offline analysis**
within the workspace, but no exploit execution, device flashing, kernel offset
generation, firmware upload, or native-code changes are automated here.

## Verification limits

The separate container-build job verifies whether the complete Dev Container
image and Features can build on a GitHub runner. That job's actual status must
be checked before claiming it passed. Even if it succeeds, **it does not
create or prove a running Codespace** in the owner's account. The owner must
instantiate a Codespace to verify account-specific launch and persistence.
No physical-device gate or root-capability verification has been performed.

**Explicit preservation:** no changes to the Android app, native exploit,
GLK1 binary format, kernel profiles, supported-device catalog or `main`.
