"""Tests for the stable error codes (KL-13): docs/hata_imzalari.json, SIK_HATALAR anchors, script tags, exit codes.
Stdlib unittest, no network, no GPU. PowerShell tests (Windows only) run the scripts in -Kuru (dry) mode in throw-away folders.

    python -I -X utf8 -m unittest discover -s tests -v

Iron-rod order: static checks first (JSON shape, anchors, tag <-> script agreement), then dry runs of the real scripts.
Signatures are plain case-insensitive substrings on purpose (no regular expressions: no ReDoS on untrusted log text).
"""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
JSON_YOL = KOK / "docs" / "hata_imzalari.json"
SIK = KOK / "docs" / "SIK_HATALAR.md"
BETIKLER = [KOK / "scripts" / "kur.ps1", KOK / "scripts" / "uret.ps1", KOK / "scripts" / "modelleri_indir.ps1"]
KOD_RE = re.compile(r"VT-[EW]-[A-Z0-9]+(?:-[A-Z0-9]+)*")
PS = shutil.which("powershell.exe") if os.name == "nt" else None
CF = getattr(subprocess, "CREATE_NO_WINDOW", 0)


def yukle():
    return json.loads(JSON_YOL.read_text(encoding="utf-8"))


def esle(log, kodlar):
    """Plain substring matching, same rule a future tani script will use."""
    kucuk = log.lower()
    return [k["kod"] for k in kodlar if any(i.lower() in kucuk for i in k["imza"])]


class JsonSekli(unittest.TestCase):
    def test_alanlar_ve_bicim(self):
        d = yukle()
        self.assertEqual(d["surum"], 1)
        gorulen = set()
        for k in d["kodlar"]:
            self.assertRegex(k["kod"], r"^" + KOD_RE.pattern + r"$")
            self.assertNotIn(k["kod"], gorulen, "kod tekrar: " + k["kod"])
            gorulen.add(k["kod"])
            self.assertEqual(k["tur"], "hata" if k["kod"].startswith("VT-E-") else "uyari")
            for alan in ("baslik_en", "baslik_tr", "ilk_adim_en", "ilk_adim_tr"):
                self.assertTrue(k[alan].strip(), k["kod"] + " " + alan)
            self.assertTrue(k["sik_hatalar"].isdigit())
            self.assertEqual(k["capa"], "docs/SIK_HATALAR.md#" + k["kod"].lower())
            for i in k["imza"]:
                self.assertGreaterEqual(len(i), 6, "imza cok kisa (yanlis eslesme riski): %r" % i)
            for o in k["ornek_log"]:
                self.assertLessEqual(len(o), 400)

    def test_json_ascii(self):
        veri = JSON_YOL.read_bytes()
        self.assertTrue(all(b < 128 for b in veri), "docs/hata_imzalari.json ASCII olmali")
        self.assertFalse([b for b in veri if b < 32 and b not in (9, 10, 13)])

    def test_her_imzanin_ornegi_eslesir(self):
        d = yukle()
        for k in d["kodlar"]:
            if k["imza"]:
                self.assertTrue(k["ornek_log"], k["kod"] + ": imza var ama ornek_log yok")
            for o in k["ornek_log"]:
                self.assertIn(k["kod"], esle(o, d["kodlar"]), "%s ornegi kendi imzasiyla eslesmedi: %r" % (k["kod"], o))

    def test_gercek_sik_hatalar_log_parcalari(self):
        """Log pieces quoted in SIK_HATALAR (real runs) must hit the intended code."""
        d = yukle()["kodlar"]
        beklenen = {
            "segment 5/52 (blocks.0) failed during weight preparation": "VT-E-VRAM",
            "retrying with temporal tiling": "VT-E-TILING",
            "process exited with STATUS_DLL_NOT_FOUND": "VT-E-DLL",
            "ModuleNotFoundError: No module named 'cv2'": "VT-E-PY",
            "dikis_denetim cikti ayristirilamadi": "VT-E-PY",
            "ffmpeg : The term 'ffmpeg' is not recognized as the name of a cmdlet": "VT-W-FFMPEG",
            "KAPI RED: klip kabul edilmez": "VT-E-KAPI-RED",
        }
        for log, kod in beklenen.items():
            self.assertIn(kod, esle(log, d), log)

    def test_temiz_log_hicbir_kodla_eslesmez(self):
        d = yukle()["kodlar"]
        for log in ("TAMAM 601 sn: runs\\x\\video.avi", "KAPI GECTI", "ses akisi var", "kare sayisi dogrulandi: 56 (ffprobe)",
                    "asama 1 tamam (latent 12,3 MB), asama 2 (ayri surec VAE) basliyor"):
            self.assertEqual(esle(log, d), [], log)


class CapaVeBetik(unittest.TestCase):
    def test_capalar_sik_hatalar_icinde(self):
        d = yukle()["kodlar"]
        metin = SIK.read_text(encoding="utf-8").replace("\r\n", "\n")
        for k in d:
            cap = '<a id="%s"></a>' % k["kod"].lower()
            self.assertEqual(metin.count(cap), 1, "capa yok ya da tekrar: " + k["kod"])
            satir = [s for s in metin.split("\n") if cap in s][0]
            self.assertTrue(satir.startswith(k["sik_hatalar"] + ". "), "%s: capa %s. maddede olmali: %r" % (k["kod"], k["sik_hatalar"], satir[:40]))

    def test_betikteki_her_kod_json_icinde_ve_tersi(self):
        d = {k["kod"]: k for k in yukle()["kodlar"]}
        betikte = {}
        for b in BETIKLER:
            for kod in set(KOD_RE.findall(b.read_text(encoding="utf-8"))):
                betikte.setdefault(kod, []).append(b.name)
        for kod, dosyalar in betikte.items():
            self.assertIn(kod, d, "betikte var, JSON'da yok: %s %s" % (kod, dosyalar))
        for kod, k in d.items():
            for dosya in k["yayinlayan"]:
                self.assertIn(dosya, betikte.get(kod, []), "JSON %s yayinlayan=%s ama betikte kod yok" % (kod, dosya))
            if not k["yayinlayan"]:
                self.assertNotIn(kod, betikte, kod + " betikte var ama yayinlayan bos")

    def test_baslik_korunur(self):
        """The code never comes before the heading: no 'HATA:'/'UYARI:' text is preceded by a tag on the same literal."""
        for b in BETIKLER:
            for n, satir in enumerate(b.read_text(encoding="utf-8").splitlines(), 1):
                self.assertNotRegex(satir, r"\[VT-[EW]-[A-Z0-9-]+\]\s*(HATA|UYARI):", "%s:%d tag baslikdan once" % (b.name, n))

    def test_cikis_kodlari_degismedi(self):
        """uret.ps1 exits only with 0/2/5/6 (the MCP server maps 0,1,2,5,6; 1 comes from an uncaught throw)."""
        uret = (KOK / "scripts" / "uret.ps1").read_text(encoding="utf-8")
        self.assertEqual(sorted(set(re.findall(r"\bexit\s+(\d+)", uret))), ["0", "2", "5", "6"])
        mcp = (KOK / "mcp" / "videoturko_mcp.py").read_text(encoding="utf-8")
        for kod in ("0", "1", "2", "5", "6"):
            self.assertIn('"%s":' % kod, mcp)
        kur = (KOK / "scripts" / "kur.ps1").read_text(encoding="utf-8")
        self.assertEqual(sorted(set(re.findall(r"\bexit\s+(\$?\w+)", kur))), ["$kod", "0", "1", "2", "3", "4"])


@unittest.skipUnless(PS, "Windows PowerShell gerekir")
class KuruCalistirma(unittest.TestCase):
    """Dry runs (-Kuru) of the real scripts in throw-away folders: nothing is downloaded or written outside temp."""

    def setUp(self):
        self.gecici = tempfile.TemporaryDirectory()
        self.addCleanup(self.gecici.cleanup)
        self.kok = Path(self.gecici.name) / "kok"
        self.model = Path(self.gecici.name) / "model"
        self.kok.mkdir()
        self.model.mkdir()

    def calistir(self, betik, *arg, ortam=None):
        env = dict(os.environ)
        env.update({"VT_ROOT": str(self.kok), "VT_MODEL_DIR": str(self.model)})
        env.update(ortam or {})
        p = subprocess.run([PS, "-NoProfile", "-File", str(KOK / "scripts" / betik)] + list(arg), capture_output=True, env=env, creationflags=CF, timeout=180)
        return p.returncode, (p.stdout + p.stderr).decode("utf-8", "replace")

    def test_kur_kuru_kotu_ortam_kodlari(self):
        sahte = "ram=8;bos_ram=2;disk=10;vc=yok;python=yok;gpu=yok;vram=3000;cc=5.2"
        kod, cikti = self.calistir("kur.ps1", "-Kuru", "-Adim", "kontrol0", ortam={"VT_KURU_SAHTE": sahte})
        self.assertEqual(kod, 3, cikti)
        for beklenen in ("HATA: [VT-E-GPU]", "HATA: [VT-E-RAM]", "HATA: [VT-E-DISK]", "UYARI: [VT-W-RAM-BOS]", "UYARI: [VT-W-VC]", "UYARI: [VT-W-PY]", "== KURU ON RAPOR TAMAM"):
            self.assertIn(beklenen, cikti)
        d = {k["kod"] for k in yukle()["kodlar"]}
        for kod_ in KOD_RE.findall(cikti):
            self.assertIn(kod_, d)

    def test_kur_kuru_disk_bandi(self):
        """32 GiB is the HATA threshold; 32-40 GiB gives a WARNING, 40+ gives nothing (toplanti 1 karari 2)."""
        def calis(disk):
            return self.calistir("kur.ps1", "-Kuru", "-Adim", "kontrol0", ortam={"VT_KURU_SAHTE": "disk=%s" % disk})[1]
        self.assertIn("HATA: [VT-E-DISK]", calis("31.9"))
        self.assertNotIn("[VT-E-DISK]", calis("32"))
        self.assertIn("UYARI: [VT-W-DISK-PAY]", calis("32"))
        self.assertIn("UYARI: [VT-W-DISK-PAY]", calis("39.9"))
        self.assertNotIn("VT-W-DISK-PAY", calis("40"))

    def test_sahte_anahtar_kuru_disinda_etkisiz(self):
        """VT_KURU_SAHTE must be ignored without -Kuru: kontrol0 reads the real machine (denetci kosulu)."""
        _, cikti = self.calistir("kur.ps1", "-Adim", "kontrol0", ortam={"VT_KURU_SAHTE": "disk=1;ram=1;gpu=yok"})
        self.assertNotIn("SAHTE OLCUM", cikti)

    def test_yarim_part_rapor_cokmez(self):
        """Regression (v0.1.2): a .part larger than the Int32 range crashed [math]::Max(0, long) in PowerShell 5.1."""
        kayit = json.loads((KOK / "scripts" / "modeller.json").read_text(encoding="utf-8"))
        ilk = kayit["dosyalar"][0]
        self.assertGreater(ilk["boyut"], 2 ** 31)
        (self.model / (ilk["hedef"] + ".part")).write_bytes(b"\0" * 1048576)
        kod, cikti = self.calistir("modelleri_indir.ps1", "-Kuru")
        self.assertNotIn("Cannot convert", cikti)
        self.assertIn("YARIM (.part", cikti)
        self.assertEqual(kod, 1, cikti)
        kod2, cikti2 = self.calistir("kur.ps1", "-Kuru", "-Adim", "kontrol0")
        self.assertNotIn("Cannot convert", cikti2)
        self.assertIn("Indirilecek model:", cikti2)

    def test_uret_kuru_blackwell_uyarisi_ve_kare_hatasi(self):
        istem = str(KOK / "docs" / "ornek_istem_R0.txt")
        kod, cikti = self.calistir("uret.ps1", "-Istem", istem, "-Kare", "56", "-Kuru", ortam={"VT_GPU_CC": "12.0"})
        self.assertEqual(kod, 0, cikti)
        self.assertIn("UYARI: [VT-W-BLACKWELL]", cikti)
        kod, cikti = self.calistir("uret.ps1", "-Istem", istem, "-Kare", "100", "-Kuru")
        self.assertNotEqual(kod, 0)
        self.assertIn("[VT-E-KARE]", cikti)
        self.assertIn("VT-E-KARE", esle(cikti, yukle()["kodlar"]))

    def test_hazir_satirindaki_komut_calisir(self):
        """The first-video command printed after HAZIR (56 frames) must be accepted by uret.ps1 -Kuru."""
        metin = (KOK / "scripts" / "kur.ps1").read_text(encoding="utf-8")
        m = re.search(r"Say '\s*powershell -NoProfile -File scripts.uret\.ps1 -Istem (\S+) -Kare (\d+)'", metin)
        self.assertIsNotNone(m, "HAZIR satirinda ilk video komutu yok")
        self.assertEqual(m.group(2), "56")
        kod, cikti = self.calistir("uret.ps1", "-Istem", str(KOK / m.group(1).replace("\\", "/")), "-Kare", m.group(2), "-Kuru")
        self.assertEqual(kod, 0, cikti)
        self.assertIn("KURU: kare=56 ", cikti)


class AmdYonlendirme(unittest.TestCase):
    """VT-E-GPU must point a non-NVIDIA user to docs/AMD_ROCM.md, and that file must exist (no dead link)."""

    def test_vt_e_gpu_amd_notuna_baglanir(self):
        kayit = [k for k in yukle()["kodlar"] if k["kod"] == "VT-E-GPU"][0]
        self.assertTrue((KOK / "docs" / "AMD_ROCM.md").is_file())
        for alan in ("ilk_adim_en", "ilk_adim_tr"):
            self.assertIn("docs/AMD_ROCM.md", kayit[alan])
        self.assertIn("docs/AMD_ROCM.md", kayit["ornek_log"][0])
        self.assertIn("docs/AMD_ROCM.md", (KOK / "scripts" / "kur.ps1").read_text(encoding="utf-8"))
        self.assertNotIn("Intel", kayit["ilk_adim_en"] + kayit["ilk_adim_tr"])  # no Intel claim: no document, not measured


if __name__ == "__main__":
    unittest.main()
