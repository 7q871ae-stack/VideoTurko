"""scripts/son_kare_denetim.py contract: information only, exit codes 0/3/6, one SON_KARE line per clip.
Input-error tests always run; tests that need opencv skip when it is missing (CI runners have no opencv).
Synthetic clips are written with cv2.VideoWriter (MJPG .avi), no ffmpeg needed.
"""
import os, subprocess, sys, tempfile, unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BETIK = os.path.join(ROOT, "scripts", "son_kare_denetim.py")
try:
    import cv2
    import numpy as np
    CV = True
except ImportError:
    CV = False


def kos(*arg):
    p = subprocess.run([sys.executable, "-I", BETIK] + list(arg), capture_output=True, text=True, timeout=120,
                       encoding="utf-8", errors="replace", creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    return p.returncode, p.stdout + p.stderr


def klip(yol, kare=56, degisim=None, boyut=(192, 336)):
    """Slowly sliding texture; from frame `degisim` on, the picture is replaced by a different texture."""
    rng = np.random.RandomState(3)
    def doku():
        g = cv2.GaussianBlur(rng.rand(boyut[1], boyut[0] * 2).astype("float32"), (0, 0), 16)
        return cv2.normalize(g, None, 0, 255, cv2.NORM_MINMAX).astype("uint8")
    a, b = doku(), doku()
    w = cv2.VideoWriter(yol, cv2.VideoWriter_fourcc(*"MJPG"), 24, boyut)
    for k in range(kare):
        z = b if degisim is not None and k >= degisim else a
        x = k  # slow against the blur: frames 8 apart still look alike
        w.write(cv2.cvtColor(z[:, x:x + boyut[0]], cv2.COLOR_GRAY2BGR))
    w.release()


class GirdiHatalari(unittest.TestCase):
    def test_argumansiz_cikis3(self):
        k, o = kos()
        self.assertEqual(k, 3)
        self.assertIn("Kullanim", o)
        self.assertNotIn("Traceback", o)

    def test_olmayan_dosya_cikis3(self):
        k, o = kos(os.path.join(tempfile.gettempdir(), "yok_son_kare.avi"))
        self.assertEqual(k, 3)
        self.assertNotIn("Traceback", o)


@unittest.skipUnless(CV, "opencv yok")
class Olcum(unittest.TestCase):
    def test_duzgun_klip_normal(self):
        with tempfile.TemporaryDirectory() as t:
            p = os.path.join(t, "duz.avi")
            klip(p)
            k, o = kos(p)
        self.assertEqual(k, 0, o)
        self.assertIn("sonuc=esik_asilmadi", o)

    def test_sonda_degisen_klip_supheli_ve_cikis0(self):
        with tempfile.TemporaryDirectory() as t:
            p = os.path.join(t, "sicrama.avi")
            klip(p, degisim=50)
            k, o = kos(p)
        self.assertEqual(k, 0, o)  # information only: never a RED exit
        self.assertIn("SUPHELI", o)
        self.assertIn("ilk 50 kare", o)

    def test_cok_kisa_klip_cikis3(self):
        with tempfile.TemporaryDirectory() as t:
            p = os.path.join(t, "kisa.avi")
            klip(p, kare=10)
            k, o = kos(p)
        self.assertEqual(k, 3, o)
        self.assertNotIn("Traceback", o)


if __name__ == "__main__":
    unittest.main()
