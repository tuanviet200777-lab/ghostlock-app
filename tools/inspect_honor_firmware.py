#!/usr/bin/env python3
"""Read-only, dependency-free Android firmware identity inspection.

This utility does not exploit vulnerabilities, extract attack offsets, flash
partitions, access credentials, or communicate with a device or network.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import sys
from pathlib import Path
from typing import Any

BOOT_MAGIC = b"ANDROID!"
VENDOR_BOOT_MAGIC = b"VNDRBOOT"
SPARSE_MAGIC = b"\x3a\xff\x26\xed"
ARM64_MAGIC = b"ARM\x64"
MAX_KERNEL_BYTES = 256 * 1024 * 1024
VERSION_RE = re.compile(rb"(?<![0-9])\d+\.\d+\.\d+\.\d+(?![0-9])")
RELEASE_RE = re.compile(
    rb"Linux version ([0-9]+\.[0-9]+\.[0-9]+[a-zA-Z0-9_.+\-]*)(?=[ \t\r\n\x00])"
)
SENSITIVE_FILENAMES = {
    "userdata.img", "metadata.img", "cache.img", "persist.img", "frp.img",
    "keymint.mbn", "huksta.mbn", "keystore.img", "modemst1.img", "modemst2.img",
}


def approved_file(value: str) -> Path:
    path = Path(value)
    if path.name.lower() in SENSITIVE_FILENAMES or path.name.lower().endswith((".key", ".pem")):
        raise ValueError(f"refusing a potentially sensitive input: {path.name}")
    if not path.is_file():
        raise ValueError(f"not a regular file: {path.name}")
    return path


def checksum(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(4 * 1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def common(path: Path) -> dict[str, Any]:
    return {"filename": path.name, "size_bytes": path.stat().st_size, "sha256": checksum(path)}


def inspect_header(path: Path) -> dict[str, Any]:
    result = common(path)
    with path.open("rb") as stream:
        data = stream.read(4096)
    if data.startswith(BOOT_MAGIC):
        result["format"] = "android_boot"
        if len(data) >= 44:
            result["header_version"] = struct.unpack_from("<I", data, 40)[0]
    elif data.startswith(VENDOR_BOOT_MAGIC):
        result["format"] = "android_vendor_boot"
        if len(data) >= 28:
            result["header_version"] = struct.unpack_from("<I", data, 8)[0]
            result["page_size"] = struct.unpack_from("<I", data, 12)[0]
            result["vendor_ramdisk_size"] = struct.unpack_from("<I", data, 24)[0]
    elif data.startswith(SPARSE_MAGIC):
        result["format"] = "android_sparse"
        if len(data) >= 28:
            major, minor, header_size, chunk_header_size = struct.unpack_from("<HHHH", data, 4)
            block_size, blocks, chunks = struct.unpack_from("<III", data, 12)
            if header_size >= 28 and chunk_header_size >= 12 and block_size > 0:
                result["sparse"] = {
                    "major": major, "minor": minor,
                    "block_size": block_size, "block_count": blocks,
                    "chunk_count": chunks, "expanded_size_bytes": block_size * blocks,
                }
    elif data.startswith(b"AVB0"):
        result["format"] = "android_avb_vbmeta"
        if len(data) >= 12:
            result["avb_header_version"] = [
                struct.unpack_from(">I", data, 4)[0],
                struct.unpack_from(">I", data, 8)[0],
            ]
        result["cryptographic_verification"] = "not_performed"
    elif data.startswith(b"\x7fELF"):
        result["format"] = "elf"
    else:
        result["format"] = "unknown"
    return result


def inspect_boot(path: Path) -> dict[str, Any]:
    result = inspect_header(path)
    if result["format"] != "android_boot":
        raise ValueError("boot image does not have ANDROID! magic")
    with path.open("rb") as stream:
        head = stream.read(4096)
        if len(head) < 44:
            raise ValueError("truncated boot image header")
        kernel_size, ramdisk_size, _, header_size = struct.unpack_from("<IIII", head, 8)
        header_version = struct.unpack_from("<I", head, 40)[0]
        if header_version not in (3, 4):
            raise ValueError(f"unsupported Android boot header version: {header_version}")
        if not 1580 <= header_size <= 4096:
            raise ValueError("invalid v3/v4 boot header size")
        if kernel_size <= 0 or kernel_size > MAX_KERNEL_BYTES:
            raise ValueError("kernel size outside analysis limit")
        kernel_offset = 4096  # v3/v4 boot images use a 4096-byte aligned kernel.
        if kernel_offset + kernel_size > result["size_bytes"]:
            raise ValueError("kernel payload extends beyond image")
        stream.seek(kernel_offset)
        kernel = stream.read(kernel_size)
        if len(kernel) != kernel_size:
            raise ValueError("kernel payload was truncated")
    candidates = sorted({m.group(1).decode("ascii") for m in RELEASE_RE.finditer(kernel)})
    kernel_info: dict[str, Any] = {
        "file_offset_bytes": kernel_offset,
        "size_bytes": kernel_size,
        "release_candidates": candidates,
        "release_source": "embedded_kernel_banner_in_uploaded_image",
        "architecture_hint": "arm64" if len(kernel) >= 64 and kernel[56:60] == ARM64_MAGIC else "unknown",
    }
    if kernel_info["architecture_hint"] == "arm64":
        kernel_info["arm64_image_size_bytes"] = struct.unpack_from("<Q", kernel, 16)[0]
    result["kernel"] = kernel_info
    result["ramdisk_size_bytes"] = ramdisk_size
    result["running_device_verified"] = False
    return result


def inspect_version_tag(path: Path) -> dict[str, Any]:
    result = common(path)
    if result["size_bytes"] > 8192:
        raise ValueError("version tag file too large")
    contents = path.read_bytes()
    result["version_strings"] = sorted({s.decode("ascii") for s in VERSION_RE.findall(contents)})
    result["evidence_scope"] = "file_metadata_only"
    return result


def compare_device(report_path: Path, kernel_candidates: list[str], expected_build: str) -> dict[str, Any]:
    # The ADB report contains potentially identifying fields: never echo it.
    data = json.loads(report_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("schema") != "honor-x7d-4g-readonly-v1":
        raise ValueError("unexpected device report schema")
    release = data.get("kernel_release")
    # A device report may come from outside this tool. Never echo arbitrary
    # strings that might contain identifiers or multi-line private metadata.
    valid_release = (
        isinstance(release, str)
        and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._+-]{0,159}", release, re.ASCII)
    )
    release = release if valid_release else ""
    if not release or not kernel_candidates:
        kernel_match = "unknown"
    else:
        kernel_match = "match" if release in kernel_candidates else "mismatch"
    props = data.get("properties")
    props = props if isinstance(props, dict) else {}
    version_keys = ("ro.build.display.id", "ro.build.version.incremental")
    measured = any(key in props for key in version_keys)
    candidate_fields = [props.get(key) for key in version_keys]
    version_found = (
        any(isinstance(value, str) and expected_build in value for value in candidate_fields)
        if measured else None
    )
    return {
        "device_kernel_release": release or None,
        "kernel_release_match": kernel_match,
        "build_version_present_in_adb_properties": version_found,
        "build_property_check": "advisory_only" if measured else "not_measured",
        "private_device_properties_copied": False,
    }


def build_report(opts: argparse.Namespace) -> dict[str, Any]:
    boot = inspect_boot(approved_file(opts.boot))
    candidates = boot["kernel"]["release_candidates"]
    report: dict[str, Any] = {
        "schema": "ghostlock-offline-firmware-v1",
        "expected_build_owner_confirmed": opts.expected_build,
        "boot": boot,
        "vendor_boot": inspect_header(approved_file(opts.vendor_boot)) if opts.vendor_boot else None,
        "version_tag": inspect_version_tag(approved_file(opts.version_tag)) if opts.version_tag else None,
        "additional_images": [inspect_header(approved_file(name)) for name in opts.image],
        "device_comparison": None,
        "root_support": "UNVERIFIED_NO_EXPLOIT_ATTEMPTED",
        "notes": [
            "The boot image is an offline file; its release string is NOT the phone's measured uname -r.",
            "SHA-256 and magic identify bytes, not official firmware authenticity or AVB signature validity.",
            "No memory offsets, exploit payloads, device writes, or network calls are performed.",
        ],
    }
    if opts.device_report:
        report["device_comparison"] = compare_device(
            approved_file(opts.device_report), candidates, opts.expected_build
        )
    return report



def safe_summary_token(value: Any) -> str:
    """Only permit nonidentifying, single-line version/identity tokens."""
    if not isinstance(value, str) or not 1 <= len(value) <= 160:
        return "(khong ro)"
    if not re.fullmatch(r"[A-Za-z0-9._+\-]+", value):
        return "(khong ro)"
    return value


def summarize_identity(report: dict[str, Any]) -> str:
    """Vietnamese evidence summary. Never imply functional/root support."""
    boot = report["boot"]
    kernel = boot["kernel"]
    releases = kernel.get("release_candidates", [])
    release_text = ", ".join(safe_summary_token(x) for x in releases) if releases else "(khong tim thay)"
    expected = safe_summary_token(report.get("expected_build_owner_confirmed"))
    version_tag = report.get("version_tag")
    versions = version_tag.get("version_strings", []) if isinstance(version_tag, dict) else []
    if version_tag is None:
        tag_status = "Chua cung cap version tag"
    elif expected in versions:
        tag_status = "Tim thay chuoi phien ban du kien trong file tag"
    else:
        tag_status = "Khong tim thay chuoi phien ban du kien trong file tag"
    comparison = report.get("device_comparison")
    if comparison is None:
        device_status = "CHUA DOI CHIEU: Khong co ADB report do truc tiep tu dien thoai"
    else:
        match = comparison.get("kernel_release_match")
        if match == "match":
            device_status = "TRUNG CHUOI kernel release (KHONG chung minh ho tro root)"
        elif match == "mismatch":
            device_status = "KHAC CHUOI kernel release (can kiem tra nguon firmware)"
        else:
            device_status = "KHONG DU DU LIEU de so sanh kernel release"
    lines = [
        "BAO CAO DOI CHIEU FIRMWARE HONOR (CHI DOC)",
        f"MagicOS du kien (chu may cung cap): {expected}",
        f"Android boot header: v{boot.get('header_version', 'unknown')}",
        f"SHA-256 boot file: {safe_summary_token(boot.get('sha256'))}",
        f"Kernel release trong boot file: {release_text}",
        f"Version tag: {tag_status}",
        f"Ket qua voi dien thoai: {device_status}",
        "Tinh trang GhostLock/root: CHUA DUOC KIEM CHUNG",
        "Gioi han: Header/chuoi version khong xac thuc firmware, chu ky AVB,",
        "khong chung minh kernel dang chay cung byte, lo hong hay root thanh cong.",
        "Khong ghi, flash, chay exploit, tai firmware len mang hoac truy van thiet bi.",
    ]
    return "\n".join(lines) + "\n"

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--boot", required=True, help="Uploaded Android v3/v4 boot image")
    parser.add_argument("--vendor-boot", help="Optional vendor_boot image")
    parser.add_argument("--version-tag", help="Optional firmware version text/tag")
    parser.add_argument("--image", action="append", default=[], help="Additional nonsensitive image (repeatable)")
    parser.add_argument("--device-report", help="Optional JSON from probe_honor_x7d_4g.py")
    parser.add_argument("--expected-build", default="9.0.0.226", help="Owner-confirmed build label")
    parser.add_argument("--out", help="Local JSON output file (stdout by default); never commit private reports")
    parser.add_argument("--summary-out", help="Optional local Vietnamese evidence summary text file")
    opts = parser.parse_args(argv)
    try:
        if opts.summary_out and opts.out and Path(opts.summary_out).resolve() == Path(opts.out).resolve():
            raise ValueError("JSON and summary output paths must be different")
        result = build_report(opts)
        rendered = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
        if opts.out:
            Path(opts.out).write_text(rendered, encoding="utf-8")
        else:
            sys.stdout.write(rendered)
        if opts.summary_out:
            Path(opts.summary_out).write_text(summarize_identity(result), encoding="utf-8")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Analysis failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
