# HONOR X7d 4G — MagicOS 9.0.0.226 firmware artifact review

**Status: device-specific root capability UNVERIFIED.**
Recorded 2026-11-10. Scope: inventory and read-only analysis of the
firmware files supplied in this conversation. No exploit was run or
device partitions modified.

## Source correction and boundaries

The device owner has clarified that an earlier GitHub report was sent
in error. **Do not use any details from that report** to identify the owner's
phone, kernel, device model code, processor, firmware variant, profile
fields, or exploit results. In particular, previous claims about a
particular model code or an observed W1 failure are withdrawn as evidence
about this phone.

**Independently provided in this conversation:**
- Device family described by owner: HONOR X7d 4G.
- Owner-confirmed running software version: **9.0.0.226**.
- Uploaded firmware files, including `boot(2).img`, `vendor_boot(2).img`,
  `dtbo(1).img`, `vendor.img` and version metadata.

**Not independently established on the physical phone:** exact model
code; full on-device `uname -r`; kernel patch status; whether the phone
is running the kernel found in the uploaded image; exploit behavior and
whether temporary root is possible.

## Evidence observed in uploaded files (not necessarily on the phone)

| Uploaded file | Read-only observation | Interpretation / limitation |
| --- | --- | --- |
| `version_by_CI(1).tag` | Contains `LGN-LGRP10-OVS 9.0.0.226` | Version metadata matches owner-provided .226, but alone cannot authenticate the package |
| `SOFTWARE_VER(1).mbn` | Contains `LGN-LGRP10-OVS 9.0.0.155` | Other metadata may serve a different purpose; cannot conclude this is the running device build |
| `SOFTWARE_VER_LIST(1).mbn` | Contains `9.0.0.1` and `9.0.0.155` | Field semantics are not independently verified |
| `boot(2).img` (100,663,296 bytes) | Android boot magic `ANDROID!` and header version 4; an embedded kernel release string `5.15.194-android13-8-00038-g853eb7b6b965-ab15936612` was observed in the uploaded image | **Firmware image only**; do not attribute the string to the running phone without device-side `uname -r` |
| `vendor_boot(2).img` | Android vendor boot `VNDRBOOT` header v4 | Boot component, not proof of running kernel identity |
| `dtbo(1).img` | May contain board/variant identifiers | Identification requires separate validation; do not infer model from a stray string |

These are artifacts uploaded by the owner, not a device-side ADB capture.
The inventory checksums are recorded in the batch manifests. No AVB
signature verification of the full package was completed.

## CVE research limitation

GhostLock's documented intended vulnerability is CVE-2026-43499. A
numeric kernel version and partition patch date do not establish
whether a vendor backported a security fix. This investigation has not
verified vulnerable or fixed instructions in the exact uploaded kernel,
and has no trusted result from the owner's handset.

## Safe next steps

1. Obtain the actual phone model, full `adb shell uname -r`, and
   `getprop ro.build.display.id` using a read-only source such as
   `tools/probe_honor_x7d_4g.py`. Inspect the report for sensitive
   identifiers before sharing.
2. Compare the device-side full kernel string with the string in the
   uploaded boot image. Do not assume they match.
3. Validate the authentic provenance and firmware build mapping of
   the supplied images offline before assigning offsets or a profile.
4. Keep GhostLock support status **unverified**. Do not substitute
   values from other devices or an incorrect issue report.

**Explicit preservation:** No modifications to native exploit,
kernel memory-writes, profile matching, or bootloader settings;
no root or flashing claims.
