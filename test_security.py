import socket
import unittest
from unittest.mock import patch

from app import security
from app.security import UnsafeURL, is_public_ip, match_platform, validate_url


def fake_dns(ip):
    def _resolve(host, port, **kwargs):
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", (ip, port))]
    return _resolve


class PublicIpTests(unittest.TestCase):
    def test_blocks_internal_ranges(self):
        for ip in ["127.0.0.1", "10.0.0.5", "192.168.1.1", "172.16.0.9", "169.254.169.254",
                   "100.64.0.1", "0.0.0.0", "::1", "fe80::1", "fc00::1", "::ffff:127.0.0.1"]:
            self.assertFalse(is_public_ip(ip), ip)

    def test_allows_public_addresses(self):
        for ip in ["8.8.8.8", "93.184.216.34", "2606:4700:4700::1111"]:
            self.assertTrue(is_public_ip(ip), ip)


class ValidateUrlTests(unittest.TestCase):
    def test_rejects_bad_shapes(self):
        for url in ["", "   ", "ftp://example.com/a.mp4", "file:///etc/passwd", "javascript:alert(1)",
                    "http://user:pw@example.com/a.mp4", "https://example.com:8080/a.mp4",
                    "https://example.com:notaport/a.mp4", "https://" + "a" * 3000]:
            with self.assertRaises(UnsafeURL, msg=url):
                validate_url(url)

    def test_rejects_private_targets(self):
        for url in ["http://127.0.0.1/a.mp4", "http://localhost/a.mp4", "http://[::1]/a.mp4",
                    "http://169.254.169.254/latest/meta-data", "http://2130706433/a.mp4",
                    "http://10.1.2.3/a.mp4"]:
            with self.assertRaises(UnsafeURL, msg=url):
                validate_url(url)

    def test_rejects_hostname_that_resolves_to_private_ip(self):
        with patch.object(security.socket, "getaddrinfo", fake_dns("10.0.0.7")):
            with self.assertRaises(UnsafeURL):
                validate_url("https://innocent.example.com/a.mp4")

    def test_accepts_public_hostname(self):
        with patch.object(security.socket, "getaddrinfo", fake_dns("93.184.216.34")):
            self.assertEqual(validate_url("  https://example.com/a.mp4  "), "https://example.com/a.mp4")


class PlatformTests(unittest.TestCase):
    def test_matches_supported_hosts(self):
        self.assertEqual(match_platform("https://www.instagram.com/reel/abc/"), "Instagram")
        self.assertEqual(match_platform("https://x.com/user/status/1"), "X")
        self.assertEqual(match_platform("https://mobile.twitter.com/user/status/1"), "X")
        self.assertEqual(match_platform("https://t.me/channel/12"), "Telegram")

    def test_does_not_match_lookalikes(self):
        self.assertIsNone(match_platform("https://instagram.com.evil.example/reel/abc"))
        self.assertIsNone(match_platform("https://notinstagram.com/reel/abc"))
        self.assertIsNone(match_platform("https://example.com/a.mp4"))


if __name__ == "__main__":
    unittest.main()
