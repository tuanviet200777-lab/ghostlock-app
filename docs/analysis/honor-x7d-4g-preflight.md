# HONOR X7d 4G — read-only kernel support investigation

**Status on 2026-11-10: unverified, not supported.**
This document and its diagnostic script are not a root solution. Neither
a kernel release nor a security patch date proves CVE-2026-43499 works.

## Verified public information vs. device-specific unknowns

HONOR's official product specification lists Snapdragon 685, MagicOS 9.0
(Android 15), and 4G variants **LGN-LX1 / LGN-LX2 / LGN-LX3**.
The similarly named X7d **5G (LGN-NX1)** must not be confused with the 4G
device. One independent LGN-LX2 report lists kernel `5.15.180`; this is
not proof of the owner's running kernel. The owner confirms
**MagicOS 9.0.0.226** in this conversation. The uploaded `boot(2).img`
contains the kernel release string
`5.15.194-android13-8-00038-g853eb7b6b965-ab15936612`.
**The device's actual model code and kernel release have not been
independently read from the phone.** A previously submitted GitHub report
was disavowed by the owner and is not used as device evidence.
See [the corrected firmware evidence review](honor-x7d-4g-226-evidence.md).

At the time of this investigation, GhostLock's built-in
`app/src/main/assets/kernel_profiles/index.conf` does not include a
verified HONOR X7d 4G profile. The project requires an **exact** release
match; an existing profile from another device is not interchangeable.

## Safe evidence collection without root

Requirements: a computer with Python 3.9+, Android platform-tools
(`adb`), a USB cable and debugging authorization on the phone.
Run the following in the cloned repository:

```sh
python3 tools/probe_honor_x7d_4g.py > honor-x7d-4g-report.json
python3 -m unittest discover -s tools -p 'test_probe_honor_x7d_4g.py'
```

The script executes **only** a fixed list of read-only `adb shell getprop`
queries, `uname -r`, and `cat /proc/version`. It never writes to the phone,
installs software, starts Shizuku, attempts root, or modifies partitions.
It requires exactly one authorized ADB device unless `--serial` selects
one of multiple devices.

The report does not contain the ADB serial or query IMEI, account details,
Android ID, or network identifiers. However, **review its build properties
and fingerprint before sharing**. The exact Android build and version are
needed for useful analysis. `support_status` is always
`UNVERIFIED_DO_NOT_RUN_EXPLOIT`, not a detection result.

## Decision gates

1. Confirm the model's identity through the phone's About screen or packaging.
   A product name alone does not distinguish 4G from 5G reliably.
2. Collect the complete `kernel_release`, build version and patch metadata
   with the read-only script.
3. Identify matching trusted, authentic firmware / kernel material for
   offline analysis. Do not copy offsets or payload settings from other
   Snapdragon phones, or different kernel builds.
4. Assess whether the relevant vulnerability has been corrected/backported.
   `uname -r` and security-patch-level values alone cannot settle that.
5. Do not add a candidate profile to the supported list until its fields,
   host validation and explicitly authorized device verification pass.
   Unverified exploit attempts can crash or reboot a device or lose data.

**Explicit preservation:** No attack/race/backend/payload edits, no weakening
of profile matching, no default-root switch, and no supported-device claim.
Only read-only tooling, tests, and documentation are introduced.

## Sources

- [Official HONOR X7d specifications](https://www.honor.com/global/phones/honor-x7d/spec/)
- [Observed X7d LGN-LX2 record (independent, not owner's device)](https://www.deviceinfo.app/devices/honor/x7d/)
- [4G vs 5G model reports](https://www.thetechoutlook.com/tech-whispers/honor-x7d-4g-and-x7d-5g-smartphone-models-certified-by-the-tdra-authority-honor-x7d-4g-also-listed-on-the-google-play-console-database/)
- [GhostLock porting guide](../kernel_profiles/README.md)

## Test plan / known limitations

Run `python3 -m unittest discover -s tools -p 'test_probe_honor_x7d_4g.py'`
on a machine with Python, then manually inspect the JSON from an
authorized X7d 4G. The tests use mocks and require no connected device.
No actual-device verification, build, or successful root is claimed here.
