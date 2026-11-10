"""Offline checks for the read-only HONOR X7d 4G inventory."""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import probe_honor_x7d_4g as probe  # noqa: E402


class VariantTests(unittest.TestCase):
    def test_4g_variants_are_candidates_not_proven_supported(self):
        for variant in ("LGN-LX1", "LGN-LX2", "LGN-LX3"):
            with self.subTest(variant=variant):
                self.assertEqual(
                    probe.classify_variant({"ro.product.vendor.model": variant}),
                    "x7d_4g_candidate_verify_model",
                )

    def test_5g_variant_is_not_4g(self):
        self.assertEqual(
            probe.classify_variant({"ro.product.model": "HONOR X7d LGN-NX1"}),
            "not_x7d_4g_candidate",
        )

    def test_generic_product_name_is_ambiguous(self):
        self.assertEqual(
            probe.classify_variant({"ro.product.model": "HONOR X7d"}),
            "x7d_variant_unknown",
        )

    def test_unknown_device(self):
        self.assertEqual(
            probe.classify_variant({"ro.product.model": "Other"}),
            "unknown_device",
        )


class ProbeTests(unittest.TestCase):
    def test_collect_is_read_only_and_does_not_expose_serial(self):
        calls = []

        def fake_adb(args, serial=None):
            calls.append((tuple(args), serial))
            if tuple(args) == ("shell", "getprop", "ro.product.model"):
                return "HONOR X7d"
            if tuple(args) == ("shell", "uname", "-r"):
                return "5.15.180-test"
            return ""

        with patch.object(probe, "adb", side_effect=fake_adb):
            report = probe.collect("serial-is-private")

        self.assertEqual(report["kernel_release"], "5.15.180-test")
        self.assertEqual(report["support_status"], "UNVERIFIED_DO_NOT_RUN_EXPLOIT")
        self.assertNotIn("serial-is-private", str(report))
        expected = {("shell", "getprop", key) for key in probe.PROPERTY_KEYS}
        expected |= {("shell", "uname", "-r"), ("shell", "cat", "/proc/version")}
        self.assertEqual({args for args, _ in calls}, expected)
        self.assertTrue(all(serial == "serial-is-private" for _, serial in calls))

    def test_single_device_required_unless_selected(self):
        mock_output = "List of devices attached\nfirst\tdevice\nsecond\tdevice\n"
        with patch.object(probe, "adb", return_value=mock_output):
            with self.assertRaisesRegex(RuntimeError, "exactly one"):
                probe.select_serial(None)
            self.assertEqual(probe.select_serial("second"), "second")

    def test_unauthorized_selected_device_is_rejected(self):
        mock_output = "List of devices attached\nfirst\tdevice\nsecond\tunauthorized\n"
        with patch.object(probe, "adb", return_value=mock_output):
            with self.assertRaisesRegex(RuntimeError, "not connected"):
                probe.select_serial("second")

    def test_forbidden_identifiers_never_queried(self):
        keys = " ".join(probe.PROPERTY_KEYS).lower()
        for fragment in ("serialno", "imei", "android_id", "macaddr", "ip_address"):
            self.assertNotIn(fragment, keys)


if __name__ == "__main__":
    unittest.main()
