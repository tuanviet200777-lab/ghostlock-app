#!/usr/bin/env python3
"""Read-only ADB inventory for investigating HONOR X7d 4G compatibility.

No root, exploit, system write, flashing, upload, or APK installation.
The output describes a build; it cannot establish vulnerability status.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from typing import Optional, Sequence

# Fixed allowlist: never dump all properties or device/account identifiers.
PROPERTY_KEYS = (
    "ro.product.model",
    "ro.product.vendor.model",
    "ro.product.odm.model",
    "ro.product.device",
    "ro.product.vendor.device",
    "ro.product.board",
    "ro.board.platform",
    "ro.hardware",
    "ro.soc.model",
    "ro.build.version.release",
    "ro.build.version.sdk",
    "ro.build.version.incremental",
    "ro.build.display.id",
    "ro.build.version.security_patch",
    "ro.vendor.build.security_patch",
    "ro.build.fingerprint",
    "ro.boot.verifiedbootstate",
    "ro.boot.flash.locked",
    "ro.boot.vbmeta.device_state",
)


def adb(args: Sequence[str], serial: Optional[str] = None) -> str:
    command = ["adb"]
    if serial is not None:
        command += ["-s", serial]
    command += list(args)
    result = subprocess.run(
        command,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=15,
        check=False,
    )
    if result.returncode:
        # Do not include stderr: it can expose device IDs or host paths.
        raise RuntimeError("ADB failed; check USB debugging and authorization")
    return result.stdout.strip()


def select_serial(requested: Optional[str]) -> str:
    output = adb(("devices",))
    connected = []
    for line in output.splitlines()[1:]:
        columns = line.split()
        if len(columns) >= 2 and columns[1] == "device":
            connected.append(columns[0])
    if requested is not None:
        if requested not in connected:
            raise RuntimeError("Selected device is not connected and authorized")
        return requested
    if len(connected) != 1:
        raise RuntimeError("Connect exactly one authorized device or supply --serial")
    return connected[0]


def classify_variant(properties: dict[str, str]) -> str:
    identity = " ".join(
        properties.get(key, "")
        for key in (
            "ro.product.model",
            "ro.product.vendor.model",
            "ro.product.odm.model",
            "ro.product.device",
            "ro.product.vendor.device",
        )
    ).upper()
    if re.search(r"LGN-NX[0-9]+", identity):
        return "not_x7d_4g_candidate"
    if re.search(r"LGN-LX[123]", identity):
        return "x7d_4g_candidate_verify_model"
    if "X7D" in identity:
        return "x7d_variant_unknown"
    return "unknown_device"



# Device-reported kernel versions are single-line tokens, never free-form text.
KERNEL_RELEASE_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._+-]{0,159}", re.ASCII)


def collect_minimal(serial: str) -> dict[str, object]:
    """Only read the live kernel release. Do not query build properties."""
    release = adb(("shell", "uname", "-r"), serial)
    if not KERNEL_RELEASE_PATTERN.fullmatch(release):
        raise RuntimeError("ADB returned an invalid kernel release")
    return {
        "schema": "honor-x7d-4g-readonly-v1",
        "kernel_release": release,
        "variant_classification": "not_measured",
        "properties": {},
        "support_status": "UNVERIFIED_DO_NOT_RUN_EXPLOIT",
        "note": "Kernel release text only; firmware authenticity and root support unverified.",
    }


def collect(serial: str) -> dict[str, object]:
    properties = {key: adb(("shell", "getprop", key), serial) for key in PROPERTY_KEYS}
    return {
        "schema": "honor-x7d-4g-readonly-v1",
        "variant_classification": classify_variant(properties),
        "kernel_release": adb(("shell", "uname", "-r"), serial),
        "kernel_build": adb(("shell", "cat", "/proc/version"), serial),
        "properties": properties,
        "support_status": "UNVERIFIED_DO_NOT_RUN_EXPLOIT",
        "note": (
            "Kernel release or patch date cannot establish whether the "
            "vendor fixed CVE-2026-43499; no root was attempted."
        ),
    }


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--serial",
        help="Select one connected ADB device (the serial is not in the report)",
    )
    parser.add_argument(
        "--minimal", action="store_true",
        help="Only read uname -r; do not collect build properties, fingerprint, or model",
    )
    opts = parser.parse_args(argv)
    try:
        selected = select_serial(opts.serial)
        report = collect_minimal(selected) if opts.minimal else collect(selected)
    except FileNotFoundError:
        print("Error: adb not found; install Android platform-tools", file=sys.stderr)
        return 1
    except subprocess.TimeoutExpired:
        print("Error: ADB timed out", file=sys.stderr)
        return 1
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
