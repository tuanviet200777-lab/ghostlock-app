# Plan: owner-readable HONOR X7d firmware identity summary

**Level:** M (offline Python output + tests + documentation only). This batch
starts from the already-tested read-only firmware inspector in PR #3.

## Motivation and evidence boundary

The owner wants a clear answer about HONOR X7d 4G, MagicOS 9.0.0.226.
The inspected boot image contains an ARM64 kernel release candidate, but no
authenticated report of the running phone's `uname -r` has been supplied for
this work. A generic GhostLock APK build is not device support.

## Affected files and behavior

1. `tools/inspect_honor_firmware.py`: add optional `--summary-out` to save
   a short, human-readable UTF-8 summary alongside its JSON; reuse existing
   in-memory read-only report and sanitise user-derived text before display.
2. `tools/test_inspect_honor_firmware.py`: cover file-only, matching,
   mismatching, missing, and malicious/private fields, plus the CLI output.
3. `docs/analysis/honor-x7d-4g-firmware-toolkit.md` and `_ZH.md`:
   explain the option and its evidence limits.
4. `.devcontainer/README.md`: Vietnamese example of the new output.
5. This design note and `_ZH.md` translation.

Data flow: selected firmware file(s) -> existing bounded parser -> existing
optional sanitized ADB comparison -> existing JSON plus optional human-readable
summary. No new device queries, network calls, upload or automatic execution.

The summary MUST distinguish **file-only** evidence, identifier string
**match/mismatch/unknown**, and **unverified functional/root support**.
Even a string match cannot establish firmware authenticity, equal binaries,
vulnerability status, exploit compatibility, or root success. No reported
root-support or device-variant status will be elevated.

## Validation

- Python syntax and existing firmware parser tests.
- New synthetic/mocked tests for missing ADB data and output sanitization.
- GitHub PR/push Python CI at the same feature-branch head.
- Report actual test and CI results separately from device verification.

## Explicit preservation / rollback

Do not change Android app, native/Rust exploit, profiles, GLK1, route catalog,
kernel offsets, physical device state or uploaded firmware. The change is
opt-in and can be reverted without affecting existing JSON output.
