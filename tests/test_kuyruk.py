"""scripts/kuyruk.ps1 contract, run against a fake uret.ps1 (no GPU, no model).
The fake reads the wanted exit code from `kod.txt` in the plan folder and logs its arguments.
"""
import os, shutil, subprocess, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KUYRUK = ROOT / "scripts" / "kuyruk.ps1"
PS = os.name == "nt" and shutil.which("powershell.exe")
SAHTE = r"""param([string]$Istem,[int]$Kare,[string]$Cikti,[string]$InitImg,[string]$EndImg,[int]$W,[int]$H,[switch]$Kuru)
$d = Split-Path -Parent $Istem
Add-Content -LiteralPath $env:VT_TEST_KAYIT -Value ("{0}|{1}|{2}|{3}|{4}|{5}|{6}" -f (Split-Path -Leaf $d),$Kare,$W,$H,[bool]$InitImg,[bool]$EndImg,[bool]$Kuru)
if ($Kuru) { exit 0 }
$k = 0; $f = Join-Path $d 'kod.txt'; if (Test-Path -LiteralPath $f) { $k = [int](Get-Content -LiteralPath $f -TotalCount 1) }
if ($k -eq 0 -or $k -eq 5) { Set-Content -LiteralPath $Cikti -Value 'avi' }
exit $k
"""


@unittest.skipUnless(PS, "Windows PowerShell gerekir")
class Kuyruk(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory()
        self.kok = Path(self.t.name)
        self.pl = self.kok / "planlar"
        self.pl.mkdir()
        self.sahte = self.kok / "sahte_uret.ps1"
        self.sahte.write_text(SAHTE, encoding="ascii")
        self.kayit = self.kok / "kayit.txt"

    def tearDown(self):
        self.t.cleanup()

    def plan(self, ad, kod=None, ilk=False, son=False):
        d = self.pl / ad
        d.mkdir()
        (d / "istem.txt").write_text("test", encoding="utf-8")
        if kod is not None:
            (d / "kod.txt").write_text(str(kod), encoding="ascii")
        if ilk:
            (d / "ilk.png").write_bytes(b"x")
        if son:
            (d / "son.jpg").write_bytes(b"x")
        return d

    def kos(self, *arg, klasor=None):
        e = dict(os.environ, VT_KUYRUK_URET=str(self.sahte), VT_KUYRUK_TEST="1", VT_TEST_KAYIT=str(self.kayit))
        p = subprocess.run(["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(KUYRUK),
                            "-Klasor", str(klasor or self.pl)] + list(arg), capture_output=True, text=True, timeout=180,
                           env=e, encoding="utf-8", errors="replace", creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        return p.returncode, p.stdout + p.stderr

    def satirlar(self):
        return self.kayit.read_text(encoding="utf-8-sig").split() if self.kayit.exists() else []

    def test_dogal_sira_ve_kareler(self):
        self.plan("plan10"); self.plan("plan2", ilk=True); self.plan("plan2A", ilk=True, son=True)
        k, o = self.kos("-Kare", "73", "-W", "384", "-H", "672")
        self.assertEqual(k, 0, o)
        s = [x.split("|") for x in self.satirlar()]
        self.assertEqual([x[0] for x in s], ["plan2", "plan2A", "plan10"])
        self.assertEqual(s[0][1:4], ["73", "384", "672"])
        self.assertEqual(s[0][4:6], ["True", "False"])
        self.assertEqual(s[1][4:6], ["True", "True"])

    def test_kaldigi_yerden_devam(self):
        self.plan("a"); self.plan("b", kod=5)
        self.assertEqual(self.kos()[0], 5)  # a RED makes the queue exit 5 (maintainers, after PR #9)
        self.kayit.unlink()
        k, o = self.kos()
        self.assertEqual(k, 0, o)
        self.assertEqual(self.satirlar(), [])
        self.assertIn("atlandi=2", o)

    def test_parametre_degisince_yeniden_uretir(self):
        self.plan("a")
        self.assertEqual(self.kos("-Kare", "56")[0], 0)
        self.kayit.unlink()
        k, o = self.kos("-Kare", "73")
        self.assertEqual(k, 0, o)
        self.assertIn("YENIDEN: a", o)
        self.assertEqual(self.satirlar()[0].split("|")[1], "73")

    def test_kare_verilmezse_uret_varsayilani(self):
        self.plan("a")
        k, o = self.kos()
        self.assertEqual(k, 0, o)
        self.assertEqual(self.satirlar()[0].split("|")[1], "0")  # -Kare not passed, uret.ps1 default applies

    def test_hata_sonraki_plana_gecer_ve_tekrar_dener(self):
        d = self.plan("a", kod=1); self.plan("b")
        k, o = self.kos()
        self.assertEqual(k, 1, o)
        self.assertIn("gecti=1", o)
        (d / "kod.txt").write_text("0", encoding="ascii")
        self.kayit.unlink()
        k, o = self.kos()
        self.assertEqual(k, 0, o)
        self.assertEqual([x.split("|")[0] for x in self.satirlar()], ["a"])

    def test_kapi_calismazsa_durur(self):
        self.plan("a", kod=6); self.plan("b")
        k, o = self.kos()
        self.assertEqual(k, 6, o)
        self.assertEqual(len(self.satirlar()), 1)

    def test_dur_dosyasi(self):
        self.plan("a")
        (self.pl / "DUR").write_text("", encoding="ascii")
        k, o = self.kos()
        self.assertEqual(k, 2, o)
        self.assertEqual(self.satirlar(), [])

    def test_kuru_dosya_yazmaz(self):
        d = self.plan("a")
        k, o = self.kos("-Kuru")
        self.assertEqual(k, 0, o)
        self.assertEqual(self.satirlar()[0].split("|")[6], "True")
        self.assertFalse((d / "kuyruk_sonuc.txt").exists())
        self.assertFalse((d / "video.avi").exists())

    def test_girdi_hatalari(self):
        self.assertEqual(self.kos(klasor=self.kok / "yok")[0], 3)
        self.assertEqual(self.kos()[0], 3)  # no plan folder
        self.plan("a")
        self.assertEqual(self.kos("-W", "384")[0], 3)


if __name__ == "__main__":
    unittest.main()
