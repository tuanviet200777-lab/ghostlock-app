# HONOR X7d 4G — firmware batch 3 (2026-11-10)

## What was actually received

20 binary files, totaling **167,304,522 bytes (159.55 MiB)**, were present in the conversation and directly inspected in read-only mode. The hash was calculated from each local uploaded file, and the format classification is only based on file magic:

- `recovery.img`: Android boot-header magic (`ANDROID!`), 67,108,864 bytes.
- `system_ext.img`: Android sparse-image magic, 87,867,504 bytes.
- `product.img`, `preload.img`, `system_dlkm.img`, and `userdata.img`: Android sparse-image magic.
- `qupv3fw.elf`, `rpm.mbn`, `storsec.mbn`, `tz(1).mbn`, and `uefi_sec(3).mbn`: ELF magic.
- `vbmeta.img`, `vbmeta_cust.img`, `vbmeta_odm.img`, `vbmeta_preas.img`, `vbmeta_preavs.img`, `vbmeta_preload.img`, `vbmeta_product.img`, `vbmeta_product_h.img`: AVB `AVB0` magic.
- `super_metadata.img`: initial bytes all zero; **the entire file was not proven empty**.

The precise file-size/hash inventory is in
[`honor-x7d-4g-batch3-manifest.csv`](honor-x7d-4g-batch3-manifest.csv).

## Publication status

**The 20 binary files have NOT been pushed to this public GitHub repository.**
The available GitHub connection supports repository text/blob APIs but cannot
transport the large binary attachments from the chat container into GitHub.
Only the text inventory and these notes have been committed.

**Never upload `userdata.img` to a public repository.** It may hold personal
data, tokens, and sensitive partition data. Its SHA-256 is deliberately not
published in this manifest. Do not assume other partition images are clean;
check provenance, device identifiers, keys and copyright before publishing.

If the binary images are genuinely required for offline investigation, upload
a vetted subset using Git LFS from the computer holding them, preferably to a
**private** repository. See [batch 2 upload notes](honor-x7d-4g-batch2-upload.md)
for the Git LFS workflow. Keep `userdata.img` out of that upload entirely.

## Technical limitations

Checking the header and SHA-256 verifies that a particular uploaded byte
sequence was examined; it does **not** prove it is legitimate HONOR stock
firmware, belongs to the user's exact X7d 4G build, or contains a vulnerable
kernel. AVB headers were **not** cryptographically authenticated. Nothing was
flashed, executed on a phone, or used to initiate a root exploit.

For the temporary-root research objective, the most immediately relevant
already-received images are `boot(2).img` and `init_boot.img` from batch 2
and `recovery.img` from batch 3, pending their exact build match and
non-invasive offline assessment.

**Explicit preservation:** do not enable exploit, alter built-in profile
matching, or mark HONOR X7d 4G as supported without evidence.
