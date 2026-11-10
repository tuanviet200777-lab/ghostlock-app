# HONOR X7d 4G — firmware batch 2 inventory / upload notes

Date: 2026-11-10

This batch contains **20 user-supplied files totaling 292,834,349 bytes
(279.27 MiB)**. See [batch2-manifest.csv](honor-x7d-4g-batch2-manifest.csv)
for filenames, exact byte sizes, and SHA-256 checksums.

**Only the inventory has been committed. The binary images themselves
are NOT in the repository.** The GitHub connection used for this task
cannot transfer the ~279 MiB of uploaded binary files. Do not interpret
the manifest as proof that the original binary files were uploaded,
validated as official firmware, or tested.

## Important privacy and authenticity warning

This is currently a **public** GitHub repository. Do not publish a raw
device dump without checking for personal data, device-specific keys,
private identifiers, and intellectual-property restrictions.

- `metadata.img` / `cache.img`: **do not publish** unless you have
  established that they contain no user, encryption, or other sensitive data.
- `cust.img`, `keymint.mbn`, `huksta.mbn`, `apdp.mbn` and other vendor
  images: review origin, content, and redistribution rights first.
- `boot(2).img`, `init_boot.img`, `dtbo(1).img` are the most directly
  relevant boot-related images for offline compatibility investigation,
  but still require authenticity and build-version checks.
- Do not flash, execute, or swap any image merely because its hash matches
  this inventory. Hashes only detect changes to these uploaded copies.

## How to place reviewed binaries into GitHub from your computer

Prefer a **private** repository dedicated to firmware investigation.
If using this repository anyway, keep a separate investigation branch
and make sure every file you publish is appropriate for a public repo.

Install Git and Git LFS on your computer first. On the chosen branch:

```sh
git lfs install
git lfs track "firmware/honor-x7d-4g/batch2/*.img"
git lfs track "firmware/honor-x7d-4g/batch2/*.mbn"
git lfs track "firmware/honor-x7d-4g/batch2/*.bin"
git lfs track "firmware/honor-x7d-4g/batch2/*.elf"
```

Copy **only reviewed and approved** files to
`firmware/honor-x7d-4g/batch2/`. In particular, leave `metadata.img`
and `cache.img` out of any public upload unless individually cleared.

Then inspect and commit the selected files:

```sh
git status
git lfs ls-files
git add .gitattributes firmware/honor-x7d-4g/batch2/
git diff --cached --stat
git commit -m "chore(firmware): add reviewed X7d batch-2 images via LFS"
git push
```

Verify the uploaded files against `batch2-manifest.csv`. Example:

```sh
sha256sum "firmware/honor-x7d-4g/batch2/boot(2).img"
```

Expected SHA-256 for `boot(2).img`:
`fa2be60595d903ac90c06638a650a5ce754f065e622307b298e18da93e7237d3`.

Git LFS consumes account storage/bandwidth and may require enabling LFS.
Ordinary GitHub contents API is unsuitable for transferring the large
binary uploads in this chat.

## Investigation status

No firmware images have been flashed or executed. The batch includes a
96 MiB Android boot image and an 8 MiB init_boot image, but that alone
does not confirm kernel vulnerability or temporary-root compatibility.
The user's phone's exact `uname -r` and matching official build are still
needed. Root support must not be marked as verified.
