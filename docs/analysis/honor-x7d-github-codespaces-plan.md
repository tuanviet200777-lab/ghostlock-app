# Design plan: GitHub Codespaces workspace for read-only HONOR firmware analysis

Status: approved scope from owner ("làm đi"), implementation on PR #3 branch.
Baseline branch head before this change:
`3fb1874b77936cae526c8164ba348ecf683607f1`.

## Why
The existing read-only Python firmware inspector and Rust extractor live in the
repository, but a user currently has to install their own environment for every
analysis. A GitHub Codespace provides a repeatable Linux workspace without
modifying a phone, bootloader, or GhostLock's native execution pipeline.

## Scope and affected files
- `.devcontainer/devcontainer.json`: Codespaces configuration with fixed
  Ubuntu 24.04 base, Python 3.12, Rust stable, and Git LFS features.
- `.devcontainer/Dockerfile`: OS tools for offline firmware analysis
  (build chain, lz4, zstd, file, and archive utilities).
- `.gitignore`: ignore local `.ghostlock-private/` input and report directory.
- `.devcontainer/post-create.sh`: initialize persistent workspace-private
  data directories, and run existing Python tests.
- `.github/workflows/honor-firmware-tools.yml`: CI checks Python tools and
  validates devcontainer JSON; a separate **PR/manual-only** job now builds
  the full Dev Container with its Features and runs safe Python tests inside
  it (no image push; independent of the Android build).
- `docs/analysis/honor-x7d-github-codespaces.md`: usage, boundaries and
  privacy handling; `_ZH.md` translation.
- `.devcontainer/README.md`: Vietnamese Codespaces quick-start and privacy rules.
- `docs/analysis/honor-x7d-github-codespaces_ZH.md`: Chinese usage translation.
- `docs/analysis/honor-x7d-github-codespaces-plan_ZH.md`: Chinese design record.
- This design record.

No changes to `tools/inspect_honor_firmware.py`, the original read-only ADB
probe, Rust extractor logic, or Android/native GhostLock code.

## Intended behavior
1. Owner launches Codespace on the PR #3 **feature branch**.
2. Dev container prepares Python, Rust, and offline inspection utilities.
3. `postCreateCommand` creates `/workspaces/ghostlock-app/.ghostlock-private/{firmware,reports}`
   **inside the checked-out repository but ignored by root `.gitignore`**,
   since the default `vscode` user lacks permission to create sibling directories
   under `/workspaces` in the CI container. Ordinary `git add .` excludes it,
   but forced additions can bypass the ignore rule. The directory is persistent
   across container rebuilds but not a backup service or secret vault.
4. Optional firmware is provided by the owner through Codespaces file upload;
   do not upload `userdata.img`, sensitive partitions, or unreviewed dumps.
5. User runs the existing inspector against selected files; reports are stored
   in the private workspace directory, not in Git history.
6. GitHub Actions tests only Python and JSON syntax on ordinary PRs/pushes.

## Compatibility, security and rollback
- Existing repository code and profile format stay identical.
- Codespaces cannot access the owner's local USB/ADB-connected phone by default;
  ADB probe must run **locally** with permission and its report must be
  reviewed before copying into the Codespace.
- Codespaces costs/quota and file lifecycle are governed by GitHub account
  settings. Data in a codespace is not automatically an archival backup.
- No automatic execution of the native exploit, no `adb root`, no flash tools,
  no kernel offset extraction in the setup steps, no repository-wide code
  changes.
- Revert the feature branch commits or close PR #3 to roll back. Leave
  `main` unchanged until review.

## Verification matrix
| Check | Target | Meaning |
| --- | --- | --- |
| JSON syntax | `.devcontainer/devcontainer.json` | Valid configuration syntax only |
| Bash syntax | `.devcontainer/post-create.sh` | Valid shell syntax |
| Python unittest | `test_inspect_honor_firmware.py` and `test_probe_honor_x7d_4g.py` | Offline parsing and read-only data contracts |
| GitHub Actions | Dedicated Python workflow | Confirms commands run on the GitHub runner |
| Dev Container CI build | PR/manual `devcontainers/ci@v0.3`, `push: never` | Confirms image/features work in GitHub runner, no real Codespace launched |
| Codespace creation | Manually launch on feature branch | Required to confirm Codespaces account creation, volumes, and lifecycle |
| Repository diff | PR #3 compare | Only listed config/docs/workflow files changed |

Evidence: record run links/results only after the tools actually execute.
Do not equate JSON parsing or CI success with a Codespace image build or
physical-device compatibility.

**Explicit preservation:** native attack code, profile/wire schema, supported
devices, Rust extractor, app/UI, and all uploaded firmware partition bytes.
