import json
import struct
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"


class PwaPackagingTest(unittest.TestCase):
    APPS = {
        "index.html": ("owner.webmanifest", "/owner-app", "/?source=pwa", "owner"),
        "teacher.html": ("teacher.webmanifest", "/teacher-app", "/teacher.html?source=pwa", "teacher"),
        "kiosk.html": ("kiosk.webmanifest", "/kiosk-app", "/kiosk.html?source=pwa", "kiosk"),
    }

    def test_each_app_has_its_own_manifest_install_action_and_icons(self):
        ids = set()
        for html_name, (manifest_name, app_id, start_url, icon_prefix) in self.APPS.items():
            html = (DIST / html_name).read_text(encoding="utf-8")
            self.assertIn(f'href="/{manifest_name}"', html)
            self.assertIn("data-pwa-install", html)
            self.assertIn('src="./pwa.js?v=1"', html.replace('src="/pwa.js?v=1"', 'src="./pwa.js?v=1"'))

            manifest = json.loads((DIST / manifest_name).read_text(encoding="utf-8"))
            self.assertEqual(manifest["id"], app_id)
            self.assertEqual(manifest["start_url"], start_url)
            self.assertEqual(manifest["display"], "standalone")
            self.assertNotIn(manifest["id"], ids)
            ids.add(manifest["id"])

            for size in (192, 512):
                icon = DIST / f"{icon_prefix}-icon-{size}.png"
                self.assertTrue(icon.is_file())
                with icon.open("rb") as source:
                    self.assertEqual(source.read(8), b"\x89PNG\r\n\x1a\n")
                    length = struct.unpack(">I", source.read(4))[0]
                    self.assertEqual(source.read(4), b"IHDR")
                    width, height = struct.unpack(">II", source.read(8))
                    self.assertGreaterEqual(length, 13)
                    self.assertEqual((width, height), (size, size))

    def test_service_worker_keeps_operational_data_online_only(self):
        worker = (DIST / "app-sw.js").read_text(encoding="utf-8")
        self.assertIn('caches.match("/offline.html")', worker)
        self.assertIn('url.pathname.startsWith("/api/")', worker)
        self.assertIn('url.pathname.startsWith("/auth/")', worker)
        self.assertIn('url.pathname.startsWith("/media/")', worker)
        self.assertIn("fetch(event.request).catch", worker)


if __name__ == "__main__":
    unittest.main()
