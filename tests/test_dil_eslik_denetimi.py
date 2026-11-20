"""Negative and positive tests for scripts/dil_eslik_denetimi.py (stdlib unittest, no network).

    python -I -X utf8 -m unittest discover -s tests -v

Each test works on a throw-away copy of README*.md and scripts/dil_profili.json; the real tree is never touched.
Ordering of the iron-rod method: the clean copy must pass first, then each targeted corruption must turn the
matching check red (or yellow in the default warning mode, red with --kati).
"""

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

BS_N = bytes([10])
KOK = Path(__file__).resolve().parents[1]
BETIK = KOK / "scripts" / "dil_eslik_denetimi.py"


class Temel(unittest.TestCase):
    def setUp(self) -> None:
        self.gecici = tempfile.TemporaryDirectory()
        self.addCleanup(self.gecici.cleanup)
        self.kok = Path(self.gecici.name) / "repo"
        (self.kok / "scripts").mkdir(parents=True)
        for yol in KOK.glob("README*.md"):
            shutil.copyfile(yol, self.kok / yol.name)
        shutil.copyfile(KOK / "scripts" / "dil_profili.json", self.kok / "scripts" / "dil_profili.json")

    def calistir(self, *arg: str) -> tuple[int, str]:
        s = subprocess.run(
            [sys.executable, "-I", "-X", "utf8", str(BETIK), "--kok", str(self.kok), *arg],
            capture_output=True, text=True, encoding="utf-8", timeout=60,
        )
        return s.returncode, s.stdout

    def degistir(self, ad: str, eski: bytes, yeni: bytes) -> None:
        yol = self.kok / ad
        veri = yol.read_bytes()
        self.assertIn(eski, veri, f"test setup: {eski!r} not in {ad}")
        yol.write_bytes(veri.replace(eski, yeni, 1))

    def profil(self, degistir) -> None:
        yol = self.kok / "scripts" / "dil_profili.json"
        veri = json.loads(yol.read_text(encoding="utf-8"))
        degistir(veri)
        yol.write_text(json.dumps(veri), encoding="utf-8")


class Pozitif(Temel):
    def test_temiz_kopya_gecer_rtl_dahil(self) -> None:
        kod, cikti = self.calistir()
        self.assertEqual(kod, 0, cikti)
        self.assertIn("SONUC: GECTI", cikti)
        self.assertIn("checked 29 translation(s)", cikti)

    def test_temiz_kopya_kati_modda_da_gecer(self) -> None:
        kod, cikti = self.calistir("--kati")
        self.assertEqual(kod, 0, cikti)

    def test_json_cikti(self) -> None:
        kod, cikti = self.calistir("--json")
        self.assertEqual(kod, 0)
        self.assertEqual(json.loads(cikti)["sonuc"], "GECTI")

    def test_tek_dil(self) -> None:
        kod, cikti = self.calistir("--dil", "ar")
        self.assertEqual(kod, 0, cikti)
        self.assertIn("checked 1 translation(s)", cikti)


class Negatif(Temel):
    def test_sayi_bozulursa_uyari_kati_modda_kirmizi(self) -> None:
        self.degistir("README.tr.md", b"209", b"210")
        kod, cikti = self.calistir()
        self.assertEqual(kod, 0, cikti)  # warning mode does not fail the exit code
        self.assertIn("SONUC: UYARI", cikti)
        self.assertIn("BELIRTEC", cikti)
        kod, cikti = self.calistir("--kati")
        self.assertEqual(kod, 1, cikti)
        self.assertIn("SONUC: KALDI", cikti)

    def test_kod_blogu_bayrak_degisirse(self) -> None:
        self.degistir("README.de.md", b"-Kare 209", b"-Kare 210")
        kod, cikti = self.calistir("--kati", "--dil", "de")
        self.assertEqual(kod, 1, cikti)
        self.assertIn("fenced block", cikti)

    def test_satir_silinirse_tablo_farki(self) -> None:
        yol = self.kok / "README.fr.md"
        satirlar = yol.read_bytes().split(BS_N)
        kalan = [s for s in satirlar if not s.startswith(b"| RAM |")]
        self.assertEqual(len(kalan), len(satirlar) - 1)
        yol.write_bytes(BS_N.join(kalan))
        kod, cikti = self.calistir("--kati", "--dil", "fr")
        self.assertEqual(kod, 1, cikti)
        self.assertIn("TABLO", cikti)

    def test_damga_yok_her_zaman_hata(self) -> None:
        yol = self.kok / "README.es.md"
        veri = yol.read_bytes()
        yol.write_bytes(veri[: veri.index(b"<!-- i18n-source")])
        kod, cikti = self.calistir()  # not --kati
        self.assertEqual(kod, 1, cikti)
        self.assertIn("stamp missing", cikti)

    def test_bayat_damga_tierA_kati_hata_tierB_uyari(self) -> None:
        self.degistir("README.md", b"# VideoTurko", b"# VideoTurko ")
        kod, cikti = self.calistir()
        self.assertEqual(kod, 0, cikti)
        self.assertIn("(tier A)", cikti)
        kod, cikti = self.calistir("--kati")
        self.assertEqual(kod, 1, cikti)
        # a tier B language alone stays a warning even with --kati
        kod, cikti = self.calistir("--kati", "--dil", "de")
        self.assertEqual(kod, 0, cikti)
        self.assertIn("(tier B)", cikti)

    def test_bidi_override_her_zaman_hata(self) -> None:
        self.degistir("README.de.md", b"# VideoTurko", ("# VideoTurko" + chr(0x202E)).encode())
        kod, cikti = self.calistir()
        self.assertEqual(kod, 1, cikti)
        self.assertIn("U+202E", cikti)

    def test_nul_karakter_hata(self) -> None:
        self.degistir("README.it.md", b"# VideoTurko", b"# VideoTurko\x00")
        kod, cikti = self.calistir()
        self.assertEqual(kod, 1, cikti)
        self.assertIn("control", cikti)

    def test_zwnj_izinsiz_dilde_hata_fa_de_serbest(self) -> None:
        self.degistir("README.tr.md", b"# VideoTurko", ("# Video" + chr(0x200C) + "Turko").encode())
        kod, cikti = self.calistir("--dil", "tr")
        self.assertEqual(kod, 1, cikti)
        self.assertIn("U+200C", cikti)
        kod, cikti = self.calistir("--dil", "fa")  # fa legitimately carries ZWNJ
        self.assertEqual(kod, 0, cikti)

    def test_ana_readme_kontrol_karakteri(self) -> None:
        self.degistir("README.md", b"# VideoTurko", b"# VideoTurko\x08")
        kod, cikti = self.calistir("--dil", "tr")
        self.assertEqual(kod, 1, cikti)

    def test_profilde_olmayan_dosya_hata(self) -> None:
        self.profil(lambda v: v["diller"].pop("sv"))
        kod, cikti = self.calistir()
        self.assertEqual(kod, 1, cikti)
        self.assertIn("not in dil_profili.json", cikti)

    def test_eksik_dosya_hata(self) -> None:
        (self.kok / "README.ja.md").unlink()
        kod, cikti = self.calistir()
        self.assertEqual(kod, 1, cikti)
        self.assertIn("README.ja.md missing", cikti)

    def test_dil_cubugu_baglantisi_eksik(self) -> None:
        self.degistir("README.ko.md", b"(README.pl.md)", b"(x.md)")
        kod, cikti = self.calistir()
        self.assertEqual(kod, 1, cikti)
        self.assertIn("language bar link", cikti)

    def test_gecersiz_utf8_hata(self) -> None:
        yol = self.kok / "README.hu.md"
        yol.write_bytes(yol.read_bytes() + b"\xff\xfe")
        kod, cikti = self.calistir()
        self.assertEqual(kod, 1, cikti)
        self.assertIn("UTF-8", cikti)

    def test_profil_yoksa_3(self) -> None:
        (self.kok / "scripts" / "dil_profili.json").unlink()
        kod, cikti = self.calistir()
        self.assertEqual(kod, 3, cikti)

    def test_kapi_cokerse_yesil_yok_6(self) -> None:
        # a profile whose language entry is a string, not an object: the gate itself crashes
        self.profil(lambda v: v["diller"].__setitem__("tr", "A"))
        kod, cikti = self.calistir()
        self.assertEqual(kod, 6, cikti)
        self.assertIn("SONUC: KALDI", cikti)
        self.assertNotIn("SONUC: GECTI", cikti)


class Rozet(Temel):
    ROZET = b" ![i18n](https://img.shields.io/badge/i18n-tier%20B-lightgrey)"

    def test_rozet_B_dosyada_izinli_A_dosyada_degil(self) -> None:
        self.profil(lambda v: v.__setitem__("rozet_url_oneki", "https://img.shields.io/badge/i18n-"))
        self.degistir("README.de.md", b"![Windows]", self.ROZET + b" ![Windows]")  # de = tier B
        kod, cikti = self.calistir("--kati", "--dil", "de")
        self.assertEqual(kod, 0, cikti)
        self.degistir("README.tr.md", b"![Windows]", self.ROZET + b" ![Windows]")  # tr = tier A
        kod, cikti = self.calistir("--kati", "--dil", "tr")
        self.assertEqual(kod, 1, cikti)

    def test_rozet_tanimsizsa_ekstra_url_uyarisi(self) -> None:
        self.degistir("README.de.md", b"![Windows]", self.ROZET + b" ![Windows]")
        kod, cikti = self.calistir("--kati", "--dil", "de")
        self.assertEqual(kod, 1, cikti)


class Damga(Temel):
    def test_kuru_calisma_yazmaz_yaz_yazar(self) -> None:
        self.degistir("README.md", b"# VideoTurko", b"# VideoTurko ")
        onceki = (self.kok / "README.tr.md").read_bytes()
        kod, cikti = self.calistir("--damga")
        self.assertEqual(kod, 0)
        self.assertIn("dry run", cikti)
        self.assertEqual(onceki, (self.kok / "README.tr.md").read_bytes())
        kod, cikti = self.calistir("--damga", "--yaz")
        self.assertIn("written: 29 stamp(s)", cikti)
        sonra = (self.kok / "README.tr.md").read_bytes()
        # only the stamp changed
        self.assertEqual(len(sonra), len(onceki))
        farkli = [i for i, (a, b) in enumerate(zip(onceki, sonra)) if a != b]
        self.assertTrue(farkli and max(farkli) - min(farkli) < 12)
        kod, cikti = self.calistir()
        self.assertNotIn("DAMGA", cikti)


if __name__ == "__main__":
    unittest.main()
