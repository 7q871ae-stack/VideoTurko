"""Tests that the run recipe in docs/KURULUM.md can really be copy-pasted (KL-19 follow-up: the v0.1.0/v0.1.1 bug was a block of
literal backslash-n sequences instead of line breaks). Stdlib unittest, no network, no GPU.

    python -I -X utf8 -m unittest discover -s tests -v

Static: no document, script or launcher contains a backslash-n followed by a flag. Dynamic (Windows PowerShell): the block is pasted
into a PowerShell session where `sd-cli` is a stand-in that prints its arguments; the arguments must be the quality-fixed command.
"""

import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
KURULUM = KOK / "docs" / "KURULUM.md"
PS = os.name == "nt" and shutil.which("powershell.exe")
CF = getattr(subprocess, "CREATE_NO_WINDOW", 0)
BS = chr(92)
KACAK = BS + "n"


def blok():
    m = re.search(r"```powershell\r?\n(sd-cli -M vid_gen.*?)```", KURULUM.read_text(encoding="utf-8"), re.S)
    return m.group(1) if m else None


class Statik(unittest.TestCase):
    def test_belgelerde_literal_ters_bolu_n_yok(self):
        """Backslash-n + spaces + a flag (a flattened command) must not appear in any text file of the repo."""
        desen = re.compile(re.escape(KACAK) + r"\s{0,4}--?[A-Za-z]")
        bulunan = []
        for yol in KOK.rglob("*"):
            if not yol.is_file() or ".git" in yol.parts or "__pycache__" in yol.parts or yol.suffix.lower() not in (".md", ".txt", ".cmd", ".ps1", ".yml", ".json"):
                continue
            if yol.relative_to(KOK).as_posix().startswith("tests/"):
                continue
            try:
                metin = yol.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            for no, satir in enumerate(metin.splitlines(), 1):
                if desen.search(satir):
                    bulunan.append("%s:%d" % (yol.relative_to(KOK).as_posix(), no))
        self.assertEqual(bulunan, [])

    def test_blok_var_ve_gercek_satirlara_bolunmus(self):
        b = blok()
        self.assertIsNotNone(b, "docs/KURULUM.md bolum 4 powershell blogu bulunamadi")
        self.assertNotIn(KACAK, b)
        satirlar = b.rstrip().splitlines()
        self.assertGreaterEqual(len(satirlar), 8)
        for s in satirlar[:-1]:
            self.assertTrue(s.rstrip().endswith("`"), "satir arka tirnak devamiyla bitmeli: " + s[:40])


@unittest.skipUnless(PS, "Windows PowerShell gerekir")
class Dinamik(unittest.TestCase):
    def test_yapistirilan_blok_kalite_sabitleriyle_calisir(self):
        b = blok()
        self.assertIsNotNone(b)
        b = b.replace("<MODEL_DIR>", "M").replace("<prompt.txt>", "p.txt").replace("<N>", "56").replace("<out>", "o")
        betik = "function sd-cli { $args | ForEach-Object { '[' + $_ + ']' } }\n" + b
        with tempfile.TemporaryDirectory(prefix="vt_belge_") as d:
            yol = Path(d) / "yapistir.ps1"
            yol.write_text(betik, encoding="utf-8-sig")
            p = subprocess.run(["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(yol)], capture_output=True, creationflags=CF, timeout=60)
        self.assertEqual(p.returncode, 0, p.stderr.decode("utf-8", "replace"))
        argumanlar = re.findall(r"\[(.*?)\]", p.stdout.decode("utf-8", "replace"))
        # quality constants of VideoTurko: 6 steps, cfg 1, non-tiled VAE, euler + hyperflow sigmas
        for ad, deger in (("--steps", "6"), ("--sampling-method", "euler"), ("--sigmas", "hyperflow-h3-flash-6"),
                          ("--video-frames", "56"), ("--flash-attn", "off,diffusion=on"), ("--backend", "te=cpu"), ("-o", "o.avi")):
            self.assertIn(ad, argumanlar)
            self.assertEqual(argumanlar[argumanlar.index(ad) + 1], deger, ad)
        self.assertIn(argumanlar[argumanlar.index("--cfg-scale") + 1], ("1", "1.0"))
        for yasak in ("--vae-tiling", "--temporal-tiling"):
            self.assertNotIn(yasak, argumanlar)
        for a in argumanlar:
            self.assertNotIn(KACAK, a)
        self.assertEqual(argumanlar[0:2], ["-M", "vid_gen"])


if __name__ == "__main__":
    unittest.main()
