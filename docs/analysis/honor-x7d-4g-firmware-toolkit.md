# HONOR X7d 4G: read-only firmware parameter toolkit

**Purpose:** determine what the supplied firmware images actually contain and
compare the embedded boot-image kernel release against a *separately collected*
read-only ADB report. **No root attempt, exploit, flashing, bypass, or writes to
the phone.** Only standard Python 3.9+ modules are used.

The owner confirmed **MagicOS 9.0.0.226** in this conversation. Do **not** use
the earlier mistakenly submitted GitHub report as device identification or
evidence of an exploit outcome.

## Data flow and scope (M-level change)

Motivation: checksums and filenames alone do not distinguish an uploaded
kernel from the *running* device kernel. Files added in this batch:
`tools/inspect_honor_firmware.py`, `tools/test_inspect_honor_firmware.py`,
and this English/Chinese documentation pair. No app, Rust extractor, native
attack, profile resolver, `index.conf`, or kernel-support status changes.

Input images are read, hashed, and identified by magic, then a bounded Android
boot v3/v4 kernel section is inspected for embedded `Linux version` candidates.
The tool does not extract exploit offsets, interpret BTF, verify AVB signatures,
or assert stock firmware authenticity.

## Inspect supplied firmware offline

From the repository root, with copies of the images in a local directory:

```sh
mkdir -p build
python3 tools/inspect_honor_firmware.py \
  --boot "/path/to/boot(2).img" \
  --vendor-boot "/path/to/vendor_boot(2).img" \
  --version-tag "/path/to/version_by_CI(1).tag" \
  --image "/path/to/vbmeta.img" \
  --image "/path/to/vendor_dlkm.img" \
  --out build/honor-x7d-4g-local-report.json \
  --summary-out build/honor-x7d-identity-summary.txt
```

The optional `--summary-out` creates a short, human-readable Vietnamese
identity summary alongside the original JSON. Its status is **file-only**
without a separately acquired ADB report; if supplied, a matching kernel
release is **only a string match**, not proof that GhostLock works. The
summary never copies raw ADB properties or device identifiers.

The `build/` directory is already ignored by Git. The output is JSON with
SHA-256 checksums, file/header details and a **candidate** kernel release.
A `boot.img` string is not proof of what the phone currently runs.
Sparse expanded size is calculated from header fields, not validated by
reading all sparse chunks. AVB header recognition is **not cryptographic
signature verification**.

The tool rejects specific potentially private files including `userdata.img`,
`metadata.img`, `cache.img`, `persist.img`, and key-related partitions. Its
allowlist is *not* a guarantee that all other firmware is safe to publish.

## Design: minimal on-device kernel check (M-level)

**Motivation:** The existing ADB inventory reads many build properties,
including a fingerprint, although the immediate missing evidence is only the
live kernel release. It is too easy to share more device details than needed.

**Scope:** `tools/probe_honor_x7d_4g.py` gains an opt-in `--minimal` path,
reading only `adb devices` for authorization and `adb shell uname -r` for
kernel identity; `tools/inspect_honor_firmware.py` distinguishes missing
build properties from an observed mismatch and rejects unsafe release strings.
Their two Python unit-test files and English/Chinese documentation are
updated. No new schema version, network calls, physical writes, or additional
privileges. Default full-probe behavior remains unchanged.

**Evidence and verification:** Test minimal output contracts and the exact
allowed ADB commands with mocks, verify malformed kernel strings are never
copied, and exercise `match/mismatch/unknown` with synthetic records. Run
both Python test suites in GitHub Actions and the Dev Container build job;
report only observed outcomes. The device itself cannot be tested by CI.

**Explicit preservation:** No changes to Android APK, Rust extractor,
C++/root code, kernel profiles, GLK1, or device support catalog. A matching
kernel release is *not* proof of GhostLock/root support.

## Optional: compare with read-only data from the actual phone

With Android platform-tools and USB debugging authorization, run on the
computer connected to your own phone:

```sh
python3 tools/probe_honor_x7d_4g.py > build/honor-x7d-device-private.json
```

Then compare the two independent sources:

```sh
python3 tools/inspect_honor_firmware.py \
  --boot "/path/to/boot(2).img" \
  --device-report build/honor-x7d-device-private.json \
  --out build/honor-x7d-compared-private.json
```

The comparison field is one of `match`, `mismatch`, or `unknown`. `match`
only means identical release **text**: it does not prove matching bytes,
signature, firmware authenticity, vulnerable code, or successful root.
Build property comparison is advisory, since Android build properties do not
always contain the user-visible MagicOS version.

The **source ADB JSON** may contain a build fingerprint; do not upload it
without personal review. The derived report intentionally does not copy
fingerprints, IMEI, serial numbers, account or networking identifiers.

## Host tests and baseline observation

```sh
python3 -m unittest discover -s tools -p 'test_inspect_honor_firmware.py' -v
```

Verified locally with Python 3 on 2026-11-10: **9 / 9 unit tests passed**;
and the standalone inspector was run in read-only mode against these uploaded
files in this conversation:

| Uploaded artifact | Observed property |
| --- | --- |
| `version_by_CI(1).tag` | `9.0.0.226` |
| `boot(2).img` | Boot v4, `ANDROID!`, SHA-256 `fa2be60595d903ac90c06638a650a5ce754f065e622307b298e18da93e7237d3` |
| Kernel embedded in that boot image | `5.15.194-android13-8-00038-g853eb7b6b965-ab15936612`; ARM64 `ARMd` marker |
| `vendor_boot(2).img` | `VNDRBOOT`, v4 |
| `vbmeta.img` | `AVB0` header (signature not verified) |
| `vendor_dlkm.img` | Android sparse header |

No physical phone was connected during that test. Kernel support and root
remain **UNVERIFIED**. Tests were run for the new Python tool only; the
repository-wide NDK, Android, Rust, lint and device gates were **not run**.

## Optional deeper offline analysis

GhostLock already contains `tools/extract_rs`, a separate Rust kernel
extractor. Its `--analysis` mode is the appropriate next tool for inspecting
embedded BTF and symbol availability **offline**. Its output is a diagnostic
candidate, not a device qualification. Do not publish a kernel profile or
run the native exploit simply because a tool can parse an image.

**Explicit preservation:** no changes to native code, the GLK1 wire format,
profile offsets, supported kernel catalog, Android execution or firmware
partitions. Keep the work on its own review branch until the evidence can be
independently checked.
