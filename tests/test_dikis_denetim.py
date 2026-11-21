"""scripts/dikis_denetim.py contract (toplanti 6, denetci): exit codes 0/1/3/6, SONUC line, and the stdout line that
uretim_kapi.ps1 parses stays byte-compatible. Negative inputs first (missing file, flag, short or broken clip, no opencv):
the old script printed a traceback for those and returned 0 even when a seam was RED (measured 2026-11-21).
Tests that need opencv skip when it is missing (CI runners have no opencv); the input-error tests always run.
Synthetic clips are written with cv2.VideoWriter (MJPG .avi), no ffmpeg needed.
"""
import os, re, subprocess, sys, tempfile, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BETIK = os.path.join(ROOT, "scripts", "dikis_denetim.py")
try:
    import cv2
    import numpy as np
    CV = True
except ImportError:
    CV = False
# Same pattern uretim_kapi.ps1 uses to read the single-clip line (contract: do not change the line format).
UK_KALIP = re.compile(r"kare=(\d+) gurultu=([0-9.]+).*?orta akis=([0-9.]+)", re.S)


def kos(*arg, kod=None):
    """Runs the script with `python -I`; kod = alternative -c program (to fake a missing opencv)."""
    cmd = [sys.executable, "-I"] + (["-c", kod] if kod else [BETIK]) + list(arg)
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=120, encoding="utf-8", errors="replace",
                       creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    return p.returncode, p.stdout + p.stderr


def klip(yol, kare, hiz, boyut=(160, 96), tohum=3):
    """Textured pattern sliding `hiz` px per frame (known motion), MJPG avi."""
    rng = np.random.RandomState(tohum)
    zemin = cv2.GaussianBlur((rng.rand(boyut[1], boyut[0] * 8) * 255).astype("uint8"), (0, 0), 1.5)
    w = cv2.VideoWriter(yol, cv2.VideoWriter_fourcc(*"MJPG"), 24, boyut)
    for k in range(kare):
        x = int(round(k * hiz))
        g = zemin[:, x:x + boyut[0]]
        w.write(cv2.cvtColor(g, cv2.COLOR_GRAY2BGR))
    w.release()


class GirdiHatalari(unittest.TestCase):
    """No opencv needed: argument checks run before the import."""

    def test_argumansiz_cikis3_izleme_yok(self):
        k, o = kos()
        self.assertEqual(k, 3, o)
        self.assertIn("SONUC: GIRDI HATALI", o)
        self.assertNotIn("Traceback", o)

    def test_bayrak_cikis3(self):
        k, o = kos("-h")
        self.assertEqual(k, 3, o)
        self.assertNotIn("Traceback", o)

    def test_olmayan_dosya_cikis3_yol_basilmaz(self):
        yok = os.path.join(tempfile.gettempdir(), "vt_yok_klasor_xyz", "yok.mp4")
        k, o = kos(yok)
        self.assertEqual(k, 3, o)
        self.assertIn("yok.mp4", o)
        self.assertNotIn("vt_yok_klasor_xyz", o)   # only the base name is printed (personal path stays out of pasted logs)
        self.assertNotIn("Traceback", o)

    def test_opencv_yoksa_cikis6_ve_ps1_deseni(self):
        with tempfile.TemporaryDirectory() as t:
            f = os.path.join(t, "a.avi")
            with open(f, "wb") as h:
                h.write(b"x")
            prog = ("import sys, runpy; sys.modules['cv2'] = None; sys.argv = [%r, %r]; "
                    "runpy.run_path(%r, run_name='__main__')") % (BETIK, f, BETIK)
            k, o = kos(kod=prog)
        self.assertEqual(k, 6, o)
        self.assertIn("SONUC: CALISMADI", o)
        # uretim_kapi.ps1 maps this text to exit 6 (not RED): the regex must still match.
        self.assertRegex(o, r"No module named|ModuleNotFoundError|ImportError|DLL load failed")


@unittest.skipUnless(CV, "opencv-python + numpy needed")
class Olcum(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.t = tempfile.TemporaryDirectory()
        d = cls.t.name
        cls.a = os.path.join(d, "a.avi")        # steady slide
        cls.b = os.path.join(d, "b.avi")        # same speed: seam OK
        cls.hizli = os.path.join(d, "hizli.avi")   # 4x speed: flow ratio far outside 0.7-1.4
        cls.kisa = os.path.join(d, "kisa.avi")
        cls.bozuk = os.path.join(d, "bozuk.avi")
        klip(cls.a, 30, 2.0)
        klip(cls.b, 30, 2.0)
        klip(cls.hizli, 30, 8.0)
        klip(cls.kisa, 3, 2.0)
        with open(cls.bozuk, "wb") as h:
            h.write(b"not a video")

    @classmethod
    def tearDownClass(cls):
        cls.t.cleanup()

    def test_tek_parca_satiri_uretim_kapi_desenine_uyar(self):
        k, o = kos(self.a)
        self.assertEqual(k, 0, o)
        m = UK_KALIP.search(o)
        self.assertIsNotNone(m, o)
        self.assertEqual(m.group(1), "30")
        self.assertNotIn("SONUC:", o)   # single clip mode prints no SONUC line (old format kept)

    def test_ayni_hiz_dikis_gecer(self):
        k, o = kos(self.a, self.b)
        self.assertEqual(k, 0, o)
        self.assertIn("-> TAMAM", o)
        self.assertTrue(o.strip().endswith("SONUC: GECTI"), o)

    def test_hiz_sicramasi_kirmizi_cikis1(self):
        k, o = kos(self.a, self.hizli)
        self.assertEqual(k, 1, o)        # old script returned 0 here
        self.assertIn("-> RED", o)
        self.assertTrue(o.strip().endswith("SONUC: KIRMIZI"), o)

    def test_cok_kisa_parca_cikis6(self):
        k, o = kos(self.a, self.kisa)
        self.assertEqual(k, 6, o)
        self.assertIn("SONUC: CALISMADI", o)
        self.assertNotIn("Traceback", o)

    def test_bozuk_dosya_cikis6(self):
        k, o = kos(self.bozuk, self.a)
        self.assertEqual(k, 6, o)
        self.assertNotIn("Traceback", o)


if __name__ == "__main__":
    unittest.main()
