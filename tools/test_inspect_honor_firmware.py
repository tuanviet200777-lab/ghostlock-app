"""Offline unit tests for inspect_honor_firmware.py. No phone is accessed."""
import json
import struct
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import inspect_honor_firmware as tool  # noqa: E402


class FirmwareInspectorTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.folder = Path(self.temporary.name)

    def fixture_boot(self, name="boot.img", release="5.15.194-test-kernel"):
        header = bytearray(4096)
        header[:8] = b"ANDROID!"
        kernel = bytearray(512)
        kernel[56:60] = b"ARMd"
        struct.pack_into("<Q", kernel, 16, 512)
        kernel[128:128 + len(f"Linux version {release} (test builder)".encode())] = (
            f"Linux version {release} (test builder)".encode()
        )
        struct.pack_into("<IIII", header, 8, len(kernel), 0, 0, 1584)
        struct.pack_into("<I", header, 40, 4)
        path = self.folder / name
        path.write_bytes(header + kernel)
        return path

    def test_boot_identification_and_embedded_kernel_release(self):
        img = self.fixture_boot()
        report = tool.inspect_boot(img)
        self.assertEqual(report["header_version"], 4)
        self.assertEqual(report["kernel"]["release_candidates"], ["5.15.194-test-kernel"])
        self.assertEqual(report["kernel"]["architecture_hint"], "arm64")
        self.assertFalse(report["running_device_verified"])
        self.assertEqual(len(report["sha256"]), 64)

    def test_bounded_boot_parser_rejects_truncation(self):
        img = self.fixture_boot()
        data = bytearray(img.read_bytes())
        struct.pack_into("<I", data, 8, 90000)
        img.write_bytes(data)
        with self.assertRaisesRegex(ValueError, "extends beyond"):
            tool.inspect_boot(img)

    def test_unexpected_boot_header_is_rejected(self):
        img = self.fixture_boot()
        data = bytearray(img.read_bytes())
        struct.pack_into("<I", data, 40, 2)
        img.write_bytes(data)
        with self.assertRaisesRegex(ValueError, "unsupported"):
            tool.inspect_boot(img)

    def test_sparse_avb_vendor_and_elf(self):
        sparse = self.folder / "vendor.img"
        content = bytearray(64)
        content[:4] = tool.SPARSE_MAGIC
        struct.pack_into("<HHHHIII", content, 4, 1, 0, 28, 12, 4096, 3, 2)
        sparse.write_bytes(content)
        self.assertEqual(tool.inspect_header(sparse)["sparse"]["expanded_size_bytes"], 12288)
        avb = self.folder / "vbmeta.img"
        avb.write_bytes(b"AVB0" + struct.pack(">II", 1, 0) + bytes(256))
        self.assertEqual(tool.inspect_header(avb)["cryptographic_verification"], "not_performed")
        vendor = self.folder / "vendor_boot.img"
        head = bytearray(64)
        head[:8] = b"VNDRBOOT"
        struct.pack_into("<I", head, 8, 4)
        struct.pack_into("<I", head, 12, 4096)
        vendor.write_bytes(head)
        self.assertEqual(tool.inspect_header(vendor)["header_version"], 4)
        elf = self.folder / "xbl.elf"
        elf.write_bytes(b"\x7fELF" + bytes(50))
        self.assertEqual(tool.inspect_header(elf)["format"], "elf")

    def test_version_tag_only_exposes_version_tokens(self):
        tag = self.folder / "version.tag"
        tag.write_bytes(b"private-prefix=secret\nversion=LGN-LGRP10-OVS 9.0.0.226")
        report = tool.inspect_version_tag(tag)
        self.assertEqual(report["version_strings"], ["9.0.0.226"])
        self.assertNotIn("secret", json.dumps(report))

    def test_sensitive_images_are_rejected(self):
        for name in ("userdata.img", "metadata.img", "huksta.mbn", "cache.img"):
            with self.subTest(name=name):
                with self.assertRaisesRegex(ValueError, "sensitive"):
                    tool.approved_file(str(self.folder / name))

    def test_device_comparison_omits_fingerprint(self):
        report = self.folder / "probe.json"
        report.write_text(json.dumps({
            "schema": "honor-x7d-4g-readonly-v1",
            "kernel_release": "5.15.194-test-kernel",
            "properties": {
                "ro.build.display.id": "MagicOS 9.0.0.226",
                "ro.build.fingerprint": "user_sensitive_fingerprint",
            },
        }), encoding="utf-8")
        result = tool.compare_device(report, ["5.15.194-test-kernel"], "9.0.0.226")
        self.assertEqual(result["kernel_release_match"], "match")
        self.assertTrue(result["build_version_present_in_adb_properties"])
        self.assertNotIn("user_sensitive_fingerprint", json.dumps(result))

    def test_device_mismatch_does_not_infer_root(self):
        report = self.folder / "probe.json"
        report.write_text(json.dumps({
            "schema": "honor-x7d-4g-readonly-v1", "kernel_release": "other",
            "properties": {},
        }), encoding="utf-8")
        result = tool.compare_device(report, ["5.15.194-test-kernel"], "9.0.0.226")
        self.assertEqual(result["kernel_release_match"], "mismatch")

    def test_cli_report_with_synthetic_boot(self):
        img = self.fixture_boot()
        tag = self.folder / "version.tag"
        tag.write_text("base_version_number=9.0.0.226", encoding="utf-8")
        out = self.folder / "out.json"
        exit_code = tool.main(["--boot", str(img), "--version-tag", str(tag), "--out", str(out)])
        self.assertEqual(exit_code, 0)
        record = json.loads(out.read_text())
        self.assertEqual(record["root_support"], "UNVERIFIED_NO_EXPLOIT_ATTEMPTED")
        self.assertEqual(record["version_tag"]["version_strings"], ["9.0.0.226"])


if __name__ == "__main__":
    unittest.main()
