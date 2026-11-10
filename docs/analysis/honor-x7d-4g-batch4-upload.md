# HONOR X7d 4G — final firmware batch 4 inventory

Date of inspection: 2026-11-10.

## Checked files

This last batch contains **12 files totaling 624,121,833 bytes (595.21 MiB)**.

| Files | Magic/format |
| --- | --- |
| `vendor.img` (490,086,628 bytes) | Android sparse image |
| `vendor_boot(2).img` (100,663,296 bytes) | `VNDRBOOT` / Android vendor boot image |
| `vendor_dlkm.img`, `version.img` | Android sparse images |
| `xbl(4).elf`, `xbl_config(2).elf` | ELF header |
| `vbmeta_vendor_dlkm.img`, `vbmeta_version.img`, `vbmeta_system.img`, `vbmeta_system_dlkm.img`, `vbmeta_system_ext.img`, `vbmeta_vendor.img` | `AVB0` headers |

SHA-256 and file lengths are in
[honor-x7d-4g-batch4-manifest.csv](honor-x7d-4g-batch4-manifest.csv).
The manifest was calculated from locally accessible uploaded file bytes.
Header recognition alone does **not** cryptographically validate firmware.

## Where things stand after four incoming batches

- Batch 1: initial firmware metadata uploads; **not yet indexed by a batch-1 manifest**.
- Batch 2: 20 binary uploads; recorded in `batch2-manifest.csv` (292,834,349 bytes).
- Batch 3: 20 binary uploads; recorded in `batch3-manifest.csv` (167,304,522 bytes).
- Batch 4: final 12 binary uploads; recorded in `batch4-manifest.csv` (624,121,833 bytes).
- Batches 2–4 **combined inventory:** 52 file records, 1,084,260,704 bytes.

**None of these firmware binary uploads has been pushed to this GitHub repository.**
Only small, human-readable manifests and notes are versioned; the GitHub
connector here cannot transport the binary attachments from the conversation
into GitHub. These files must not be represented as present in Git history
until actually transferred and verified. Git LFS would be required for large
binary artifacts from a workstation with the files.

This repository is **public**. Do not publish private device images such as
`userdata.img`, `metadata.img`, or any image containing personal
information, secrets or device-unique identifiers. Consider proprietary
redistribution restrictions before uploading OEM firmware.

## Relevance to temporary-root research

A vendor boot image is useful for offline board / boot-chain and version
analysis. However, these 12 files do **not** establish that the kernel used
by the owner's HONOR X7d 4G is vulnerable to CVE-2026-43499. A signed,
exact-build firmware match and the device's complete `uname -r` remain
unverified in this investigation.

**No firmware was flashed, exploited, executed on a phone, or declared
root-capable. The branch `main` is intentionally unchanged.**
