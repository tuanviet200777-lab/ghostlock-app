# HONOR X7d 4G (LGN-L42) / MagicOS 9.0.0.226 — evidence review

**Status: root NOT confirmed. Existing public device log reports W1 failure.**
Date: 2026-11-10. Scope: read-only analysis of files uploaded by the owner,
plus the owner's existing upstream issue. No exploit execution, no flashing.

## Device and firmware identity

- Owner identifies the running build as **9.0.0.226** in the conversation.
- The owner's upstream GhostLock report, [issue #846](https://github.com/YuKongA/ghostlock-app/issues/846),
  records **HONOR X7d 4G, LGN-L42 / SM6225**, full firmware
  `9.0.0.226(C636E10R2P2)` / `0501AHXN` and
  full device kernel release:
  `5.15.194-android13-8-00038-g853eb7b6b965-ab15936612`.
  These details are **owner-reported**, not independently read from the
  physical phone in this investigation.
- The supplied `version_by_CI(1).tag` contains
  `base_version_number=LGN-LGRP10-OVS 9.0.0.226`.
- The supplied `SOFTWARE_VER(1).mbn` contains
  `LGN-LGRP10-OVS 9.0.0.155`, and `SOFTWARE_VER_LIST(1).mbn`
  lists `9.0.0.1` and `9.0.0.155`.
  **Do not assume** the files have been mixed or know what each field
  represents without authoritative update-package metadata.

## Direct read-only image inspection

| Uploaded item | Verified evidence | Important limitation |
| --- | --- | --- |
| `boot(2).img` (100,663,296 bytes) | `ANDROID!`, Android boot header **v4**; kernel size 47,577,600 bytes, kernel begins at file offset 0x1000 | Firmware-to-device match rests on owner report + exact kernel string, not verified boot signatures |
| Kernel within `boot(2).img` | Embedded `Linux version 5.15.194-android13-8-00038-g853eb7b6b965-ab15936612`; ARM64 `ARMd` image marker | Kernel version alone cannot show whether a security fix was backported |
| `vendor_boot(2).img` | `VNDRBOOT`, vendor boot header **v4** | Contains an unrelated `5.15.137-...-dirty` string; it is **not** evidence that the running kernel is 5.15.137 |
| `boot(2).img` AVB metadata string | `com.android.build.boot.security_patch 2026-09-01` | Describes a build partition; not proof the CVE is fixed |
| `vendor.img` AVB metadata string | `com.android.build.vendor.security_patch 2026-10-01` | Not proof of a fixed kernel |
| `dtbo(1).img` strings | `LGN-LX1`, `LGN-LX2`, `LGN-LX3`; no `LGN-L42` plaintext match | Could be multi-variant DTBO; **not proof** the image is incompatible |

All observations above were made without modifying the images or running
any code on the phone. SHA-256 of the boot image is recorded in
[`batch2-manifest.csv`](honor-x7d-4g-batch2-manifest.csv).

## Current GhostLock state from issue #846

The previously published owner log documents:
- GhostLock 1.2+591 and Shizuku shell UID 2000, seccomp=0.
- A manually imported candidate profile successfully passed app-level
  field validation (`invalid=0`). This does **not** validate kernel geometry.
- `kernel_phys_load=0xa8000000` in the attempted configuration,
  **not independently confirmed** by this investigation.
- The pselect route reported successful internal calls.
- **W1 (SELinux write verification) failed after 15 attempts**. W2 and W3
  were not reached, and no successful root is demonstrated.
- The issue calls out unconfirmed profile differences including
  `slide_boot_id` (45,162,032 vs 48,064,537),
  `cred.copy_size` (160 vs BTF `cred` structure 176),
  and `kernelsnitch.mm_struct_sz` (1024 vs BTF `mm_struct` 992).
  These differences cannot automatically be called bugs without mapping
  each field to its exact semantics.

## Known upstream vulnerability status

[CVE-2026-43499](https://www.cve.org/CVERecord?id=CVE-2026-43499)
concerns `kernel/locking/rtmutex.c`; the published Linux stable
5.15 fix is in **5.15.212**:
[Linux CVE bulletin](https://kernel.googlesource.com/pub/scm/linux/security/vulns/+/09b74d1628ea888153f0194df38a4c2f3a80ba5f/cve/published/2026/CVE-2026-43499.mbox).

The uploaded image reports **5.15.194**, numerically older than upstream
5.15.212, but HONOR may have **backported** the fix, especially given the
newer partition patch-level metadata. No code-level confirmation of the
vulnerable/fixed `remove_waiter()` has been completed on this exact image.
Do **not** equate version comparison with successful exploitation.

## Decision and remaining research

1. Treat **9.0.0.226(C636E10R2P2)** as the target build rather than .155;
   retain the .155 strings as unresolved package metadata.
2. Treat the exact kernel release above as strongly corroborated between
   the provided boot image and the owner's public report.
3. Do **not** publish a built-in profile or enable root by default.
   Existing W1 failure is actual device evidence against a working profile.
4. A safe next step is offline analysis of the exact image / extractor
   report and comparison with the owner's complete diagnostic profile/log,
   without running an exploit or flashing images.
5. The public repository should hold analysis reports/checksums, **not**
   private `userdata.img` or other device-unique data.

**Explicit preservation:** No changes to native exploit/backend/race/
memory-write code, no guessed offsets, no bypass of profile validation,
and no claim of supported device/root success.
