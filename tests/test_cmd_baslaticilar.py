"""Tests for kur.cmd / uret.cmd (KL-11): double-click launchers. Stdlib unittest, no network, no GPU.

    python -I -X utf8 -m unittest discover -s tests -v

Static checks run everywhere; dry runs need Windows cmd.exe and run in a throw-away folder whose name has spaces and
Turkish letters. Only -Kuru (dry) modes or a stub for powershell.exe (VT_POWERSHELL) are used: no download, no GPU job.
"""

import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
CMD = os.name == "nt" and shutil.which("cmd.exe")
CF = getattr(subprocess, "CREATE_NO_WINDOW", 0)
TR_AD = "T" + chr(252) + "rk" + chr(231) + "e Klas" + chr(246) + "r " + chr(287) + chr(252) + chr(351) + chr(305)


def beklemede(cikti):
    """True if text follows the last 'Codes and fixes' line (i.e. pause printed its prompt)."""
    return cikti.split("docs\\SIK_HATALAR.md")[-1].strip() != ""


class Statik(unittest.TestCase):
    def test_dosyalar_ascii_crlf_etiketsiz(self):
        for ad in ("kur.cmd", "uret.cmd"):
            veri = (KOK / ad).read_bytes()
            self.assertTrue(all(b < 128 for b in veri), ad + " ASCII olmali")
            self.assertFalse([b for b in veri if b < 32 and b not in (10, 13)], ad + " kontrol karakteri")
            self.assertEqual(veri.count(b"\r\n"), veri.count(b"\n"), ad + " CRLF olmali (calisma agaci)")
            metin = veri.decode("ascii")
            self.assertTrue(metin.startswith("@echo off\r\n"))
            self.assertIn("chcp 65001", metin)
            self.assertIn("pause", metin)
            self.assertIn("%*", metin, ad + " bayraklari betige iletmeli")
            self.assertEqual(metin.count("\nchcp %VT_ESKI_CP%"), 1, ad + " eski kod sayfasi geri yuklenmeli")
            # LF-guvenli: etiket (:ad) ve cok satirli parantez blogu yok
            self.assertFalse([s for s in metin.split("\r\n") if re.match(r"^\s*:[A-Za-z_]", s)], ad + " etiket icermemeli")
            self.assertFalse([s for s in metin.split("\r\n") if s.rstrip().endswith("(")], ad + " cok satirli blok icermemeli")
            # iki dilli: hem Ingilizce hem Turkce ifade
            self.assertRegex(metin, r"(?i)cikis kodu")
            self.assertRegex(metin, r"(?i)exit code")

    def test_gitattributes_kurali(self):
        ga = (KOK / ".gitattributes").read_text(encoding="utf-8")
        self.assertRegex(ga, r"(?m)^\*\.cmd\s+text\s+eol=crlf\s*$")

    def test_ps1_cagrisi_ve_yol_sirasi(self):
        for ad, betik in (("kur.cmd", "kur.ps1"), ("uret.cmd", "uret.ps1")):
            metin = (KOK / ad).read_text(encoding="ascii")
            self.assertIn('-File "%~dp0scripts\\' + betik + '"', metin)
            self.assertIn("-ExecutionPolicy Bypass", metin)
            self.assertLess(metin.index("chcp 65001"), metin.index('cd /d "%~dp0"'), "chcp, yol cozumlemeden once olmali")
            self.assertIn("%SystemRoot%\\System32\\find.exe", metin, "find, System32'den (PATH'teki baska find degil)")


@unittest.skipUnless(CMD, "Windows cmd.exe gerekir")
class Calistirma(unittest.TestCase):
    def setUp(self):
        self.gecici = tempfile.TemporaryDirectory(prefix="vt_cmd_")
        self.addCleanup(self.gecici.cleanup)
        self.ev = Path(self.gecici.name) / TR_AD / "VideoTurko kopya"
        (self.ev / "scripts").mkdir(parents=True)
        (self.ev / "docs").mkdir()
        for ad in ("kur.cmd", "uret.cmd"):
            shutil.copyfile(KOK / ad, self.ev / ad)
        for ad in ("kur.ps1", "uret.ps1", "modelleri_indir.ps1", "modeller.json", "kart.ps1", "kart_tablosu.json"):
            shutil.copyfile(KOK / "scripts" / ad, self.ev / "scripts" / ad)
        for ad in ("ornek_istem_R0.txt", "LISANS_KABUL.txt"):
            shutil.copyfile(KOK / "docs" / ad, self.ev / "docs" / ad)

    def calistir(self, komut, ortam=None, girdi=b""):
        env = dict(os.environ)
        env["VT_KURU_SAHTE"] = "disk=100"   # test makinesinin bos diski sonucu degistirmesin (yalniz -Kuru'da etkilidir)
        for k in ("VT_ROOT", "VT_MODEL_DIR", "VT_PAUSE", "VT_NO_PAUSE", "VT_POWERSHELL"):
            env.pop(k, None)
        env.update(ortam or {})
        p = subprocess.run(komut, cwd=str(self.ev), input=girdi, capture_output=True, env=env, creationflags=CF, timeout=180)
        return p.returncode, (p.stdout + p.stderr).decode("utf-8", "replace")

    def test_kur_cmd_kuru_bosluklu_turkce_yol(self):
        kod, cikti = self.calistir(["cmd.exe", "/c", ".\\kur.cmd", "-Kuru"])
        self.assertIn(kod, (0, 3), cikti)   # 3 = bu makinede GPU/RAM HATA'si (CI); kuru rapor yine de tamamlanir
        self.assertIn("KURU ON RAPOR TAMAM", cikti)
        self.assertIn("[VT-W-YOL-BOSLUK]", cikti)
        self.assertIn("[VT-W-YOL-ASCII]", cikti)
        self.assertFalse(beklemede(cikti), "cmd /c ile pause olmamali (ajan/CI asilmasin)")

    def test_cikis_kodu_iletilir(self):
        kod, cikti = self.calistir(["cmd.exe", "/c", ".\\kur.cmd", "-Kuru"], ortam={"VT_KURU_SAHTE": "disk=10;gpu=yok;ram=8"})
        self.assertEqual(kod, 3, cikti)
        self.assertIn("[VT-E-DISK]", cikti)
        self.assertIn("cikis kodu: 3", cikti)

    def test_cift_tik_taklidi_pause_eder_cmd_c_etmez(self):
        # Explorer: cmd.exe /c ""<tam yol>\kur.cmd" "   (pause metni dile gore degisir: sonda bir sey var mi diye bakilir)
        komut = 'cmd.exe /c ""%s" -Kuru"' % (self.ev / "kur.cmd")
        kod, cikti = self.calistir(komut, girdi=b"\r\n")
        self.assertIn(kod, (0, 3), cikti)
        self.assertTrue(beklemede(cikti), "cift tik taklidinde pause bekleniyordu: " + repr(cikti[-80:]))
        kod2, cikti2 = self.calistir(["cmd.exe", "/c", ".\\kur.cmd", "-Kuru"], ortam={"VT_PAUSE": "1"}, girdi=b"\r\n")
        self.assertTrue(beklemede(cikti2), "VT_PAUSE=1 ile pause bekleniyordu")
        kod3, cikti3 = self.calistir(komut, ortam={"VT_NO_PAUSE": "1"})
        self.assertFalse(beklemede(cikti3), "VT_NO_PAUSE=1 ile pause olmamali")

    def test_lf_satir_sonu_da_calisir(self):
        veri = (self.ev / "kur.cmd").read_bytes().replace(b"\r\n", b"\n")
        (self.ev / "kur.cmd").write_bytes(veri)
        kod, cikti = self.calistir(["cmd.exe", "/c", ".\\kur.cmd", "-Kuru"])
        self.assertIn(kod, (0, 3), cikti)
        self.assertIn("KURU ON RAPOR TAMAM", cikti)

    def test_uret_cmd_modlari(self):
        kod, cikti = self.calistir(["cmd.exe", "/c", ".\\uret.cmd"])
        self.assertEqual(kod, 0, cikti)
        self.assertIn("56 frames", cikti)
        kod, cikti = self.calistir(["cmd.exe", "/c", ".\\uret.cmd", "yok.txt"])
        self.assertEqual(kod, 1, cikti)
        self.assertIn("dosya bulunamadi", cikti)
        kod, cikti = self.calistir(["cmd.exe", "/c", ".\\uret.cmd", "-Istem", "docs\\ornek_istem_R0.txt", "-Kare", "141", "-Kuru"])
        self.assertEqual(kod, 0, cikti)
        self.assertIn("KURU: kare=141 ", cikti)

    def test_uret_cmd_tek_dosya_56_kare(self):
        """One existing file (drag and drop) -> -Istem <file> -Kare 56. A stub replaces powershell.exe: no GPU job."""
        kok = self.ev
        (kok / "sahte_ps.cmd").write_bytes(b"@echo off\r\necho SAHTE-PS ARGS: %*\r\nexit /b 7\r\n")
        kod, cikti = self.calistir(["cmd.exe", "/c", ".\\uret.cmd", "docs\\ornek_istem_R0.txt"], ortam={"VT_POWERSHELL": str(kok / "sahte_ps.cmd")})
        self.assertIn('-Istem "docs\\ornek_istem_R0.txt" -Kare 56', cikti)
        self.assertIn("uret.ps1", cikti)
        self.assertEqual(kod, 7, cikti)


if __name__ == "__main__":
    unittest.main()
