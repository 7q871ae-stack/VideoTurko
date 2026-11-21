"""Tests for scripts/zincir.py (clip chaining helper). Stdlib unittest, no network, no GPU.
Clips are made with ffmpeg's lavfi test sources; tests that need ffmpeg are skipped when it is not installed.

    python -I -X utf8 -m unittest discover -s tests -v
"""

import contextlib
import importlib.util
import io
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
_s = importlib.util.spec_from_file_location("zincir", KOK / "scripts" / "zincir.py")
zincir = importlib.util.module_from_spec(_s)
_s.loader.exec_module(zincir)

FFMPEG = shutil.which("ffmpeg")
FFPROBE = shutil.which("ffprobe")
CF = getattr(subprocess, "CREATE_NO_WINDOW", 0)


def kos(*arg):
    """Run main() in process; return (exit code, stdout, stderr)."""
    o, e = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(o), contextlib.redirect_stderr(e):
        kod = zincir.main(list(arg))
    return kod, o.getvalue(), e.getvalue()


def klip(yol, kaynak, kare, ses=True):
    gir = ["-f", "lavfi", "-i", "%s=size=64x48:rate=24,format=yuv420p" % kaynak]
    if ses:
        gir += ["-f", "lavfi", "-i", "sine=frequency=440:sample_rate=48000"]
    subprocess.run([FFMPEG, "-v", "error", "-y"] + gir + ["-frames:v", str(kare)] + (["-shortest"] if ses else []) + [str(yol)],
                   check=True, creationflags=CF)


class Plan(unittest.TestCase):
    def test_otuz_saniye_dort_klip(self):
        kod, cikti, _ = kos("plan", "--sure", "30")
        self.assertEqual(kod, 0)
        self.assertIn("Toplam 4 klip", cikti)
        self.assertIn("YOK", cikti)  # no time estimate (not measured)

    def test_kisa_sure_tek_klip(self):
        kod, cikti, _ = kos("plan", "--sure", "5")
        self.assertEqual(kod, 0)
        self.assertIn("Tek klip", cikti)

    def test_negatifler(self):
        for arg in (["--sure", "0"], ["--sure", "-3"], ["--sure", "30", "--kare", "100"], ["--sure", "30", "--kare", "209"]):
            kod, _, hata = kos("plan", *arg)
            self.assertEqual(kod, 2, arg)
            self.assertIn("HATA", hata)

    def test_tavan_uret_ps1den_okunur(self):
        self.assertEqual(zincir._sabit("KareInit", -1), 192)
        self.assertEqual(zincir._sabit("YokBoyleSabit", 7), 7)


@unittest.skipUnless(FFMPEG and FFPROBE, "ffmpeg/ffprobe not installed")
class Ffmpegli(unittest.TestCase):
    def setUp(self):
        self.d = Path(tempfile.mkdtemp(prefix="vt_zincir_"))
        self.addCleanup(shutil.rmtree, self.d, True)
        self.k1, self.k2 = self.d / "k1.mp4", self.d / "k2.mp4"
        klip(self.k1, "testsrc", 22)
        klip(self.k2, "testsrc2", 22)

    def test_son_kare_gercek_son_kare(self):
        png = self.d / "son.png"
        kod, cikti, _ = kos("son-kare", str(self.k1), str(png))
        self.assertEqual(kod, 0)
        self.assertIn("21.", cikti)
        # byte-compare with frame 21 and NOT with frame 20 (the SIK_HATALAR item 9 mistake)
        ref = {}
        for n in (20, 21):
            p = self.d / ("r%d.png" % n)
            subprocess.run([FFMPEG, "-v", "error", "-y", "-i", str(self.k1), "-vf", "select=eq(n\\,%d)" % n, "-vsync", "0",
                            "-frames:v", "1", "-update", "1", str(p)], check=True, creationflags=CF)
            ref[n] = p.read_bytes()
        self.assertEqual(png.read_bytes(), ref[21])
        self.assertNotEqual(ref[20], ref[21])

    def test_son_kare_negatifler(self):
        bos, tek = self.d / "bos.mp4", self.d / "tek.mp4"
        bos.write_bytes(b"")
        klip(tek, "testsrc", 1, ses=False)
        for girdi in (self.d / "yok.mp4", bos, tek):
            kod, _, hata = kos("son-kare", str(girdi), str(self.d / "x.png"))
            self.assertEqual(kod, 2, girdi.name)
            self.assertIn("HATA", hata)
            self.assertFalse((self.d / "x.png").exists())
        png = self.d / "var.png"
        png.write_bytes(b"x")
        kod, _, hata = kos("son-kare", str(self.k1), str(png))
        self.assertEqual(kod, 2)  # never overwrite silently
        self.assertEqual(png.read_bytes(), b"x")

    def test_bagla_kare_sayisi_ve_komut(self):
        kod, cikti, _ = kos("bagla", str(self.k1), str(self.k2), "-o", str(self.d / "film.mp4"))
        self.assertEqual(kod, 0)
        self.assertIn("trim=start_frame=1", cikti)
        self.assertIn("dikis_denetim.py", cikti)
        self.assertFalse((self.d / "film.mp4").exists())  # printed only, not run
        kod, _, _ = kos("bagla", str(self.k1), str(self.k2), "-o", str(self.d / "film.mp4"), "--calistir")
        self.assertEqual(kod, 0)
        self.assertEqual(zincir.kare_sayisi(str(self.d / "film.mp4"), FFPROBE), 22 + 21)  # hand-off frame dropped

    def test_bagla_sessiz_klipler(self):
        s1, s2 = self.d / "s1.mp4", self.d / "s2.mp4"
        klip(s1, "testsrc", 22, ses=False)
        klip(s2, "testsrc2", 22, ses=False)
        kod, cikti, _ = kos("bagla", str(s1), str(s2), "-o", str(self.d / "sf.mp4"), "--calistir")
        self.assertEqual(kod, 0)
        self.assertIn("yok (yalniz video", cikti)
        self.assertEqual(zincir.kare_sayisi(str(self.d / "sf.mp4"), FFPROBE), 43)

    def test_bagla_karisik_ses_reddedilir(self):
        s1 = self.d / "s1.mp4"
        klip(s1, "testsrc", 22, ses=False)
        kod, _, hata = kos("bagla", str(self.k1), str(s1), "--calistir", "-o", str(self.d / "kf.mp4"))
        self.assertEqual(kod, 2)
        self.assertIn("sessiz", hata)
        self.assertFalse((self.d / "kf.mp4").exists())

    def test_bagla_negatifler(self):
        self.assertEqual(kos("bagla", str(self.k1))[0], 2)
        self.assertEqual(kos("bagla", str(self.k1), str(self.d / "yok.mp4"))[0], 2)


POWERSHELL = shutil.which("powershell.exe") if sys.platform == "win32" else None


@unittest.skipUnless(POWERSHELL, "Windows PowerShell only")
class PowerShellTirnak(unittest.TestCase):
    """The printed command is pasted into PowerShell: ; [ ] $ backtick ' and spaces must stay literal."""

    def test_zor_dizgeler_ayni_cikar(self):
        for ham in ("a b.mp4", "it's.mp4", "$x(1).mp4", "a;b[0].mp4", "`n.mp4", "x\u2019;calc;\u2018.mp4", "a\u201ab\u201bc.mp4", "[0:v]trim=start_frame=1,setpts=PTS-STARTPTS[v0];[v0]concat=n=2:v=1:a=0[v]"):
            r = subprocess.run([POWERSHELL, "-NoProfile", "-NonInteractive", "-Command", "[Console]::OutputEncoding=[Text.Encoding]::UTF8; " + zincir.ps_tirnak(ham)],
                               capture_output=True, text=True, encoding="utf-8", creationflags=CF)
            self.assertEqual(r.stdout.rstrip("\r\n"), ham)


class FfmpegYok(unittest.TestCase):
    def test_ffmpeg_yoksa_cikis_3(self):
        eski = zincir._arac
        zincir._arac = lambda ad: None
        try:
            kod, _, hata = kos("son-kare", __file__, "x.png")
            self.assertEqual(kod, 3)
            self.assertIn("bulunamadi", hata)
            kod, _, _ = kos("bagla", __file__, __file__, "--calistir")
            self.assertEqual(kod, 3)
        finally:
            zincir._arac = eski


if __name__ == "__main__":
    unittest.main()
