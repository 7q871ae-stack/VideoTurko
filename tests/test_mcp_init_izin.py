"""Tests for the MCP init_image allowed-folder check (KL-16). Stdlib unittest, no network, no GPU, no `mcp` package.

    python -I -X utf8 -m unittest discover -s tests -v

mcp/init_izin.py is loaded by file path. The server wiring is tested with a stub FastMCP injected into sys.modules
(Windows only: the server uses kernel32). Symlink/junction cases skip when the OS refuses to create them.
Default stays open: with VT_MCP_INIT_DIR unset the old behaviour (and old messages) must not change.
"""

import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
import types
import unittest
from pathlib import Path

KOK = Path(__file__).resolve().parents[1]
BS = chr(92)
WIN = os.name == "nt"
CF = getattr(subprocess, "CREATE_NO_WINDOW", 0)


def yukle(ad, yol):
    spec = importlib.util.spec_from_file_location(ad, yol)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


IZIN = yukle("vt_init_izin_test", KOK / "mcp" / "init_izin.py")


class Temel(unittest.TestCase):
    def setUp(self):
        self.t = Path(tempfile.mkdtemp(prefix="vt_izin_"))
        self.addCleanup(shutil.rmtree, str(self.t), True)
        self.root = self.t / "kok"
        (self.root / "girdi" / "alt").mkdir(parents=True)
        self.dis = self.t / "dis"
        self.dis.mkdir()
        (self.root / "girdi" / "a.png").write_bytes(b"x")
        (self.root / "girdi" / "alt" / "b.png").write_bytes(b"x")
        (self.dis / "gizli.png").write_bytes(b"x")
        (self.root / "disarda.png").write_bytes(b"x")
        self.izinli = IZIN.izinli_klasorler(self.root, "girdi")

    def tamam(self, yol, izinli=None):
        p, e = IZIN.yol_coz(str(yol), self.root, self.izinli if izinli is None else izinli)
        self.assertIsNone(e, e)
        self.assertTrue(p.is_file())
        return p

    def red(self, yol, izinli=None):
        p, e = IZIN.yol_coz(str(yol), self.root, self.izinli if izinli is None else izinli)
        self.assertIsNone(p, f"kabul edilmemeliydi: {yol}")
        self.assertTrue(e)
        self.assertNotIn(str(self.t), e, "hata iletisi yolu geri yazmamali")
        return e


class AcikKip(Temel):
    """Varsayilan: VT_MCP_INIT_DIR yok/bos = eski davranis."""

    def test_env_yok_ya_da_bos_acik(self):
        for deger in (None, "", "   "):
            self.assertIsNone(IZIN.izinli_klasorler(self.root, deger))

    def test_acik_kip_diskin_her_yeri_ve_goreli_ROOTa_gore(self):
        p, e = IZIN.yol_coz(str(self.dis / "gizli.png"), self.root, None)
        self.assertIsNone(e)
        self.assertEqual(p, (self.dis / "gizli.png").resolve())
        p, e = IZIN.yol_coz("disarda.png", self.root, None)
        self.assertIsNone(e)
        self.assertEqual(p, (self.root / "disarda.png").resolve())

    def test_acik_kip_eski_hata_iletisi(self):
        p, e = IZIN.yol_coz(str(self.dis / "yok.png"), self.root, None)
        self.assertIsNone(p)
        self.assertTrue(e.startswith("init_image dosya degil ya da yok: "), e)

    def test_acik_kipte_nokta_nokta_eskisi_gibi_cozulur(self):
        p, e = IZIN.yol_coz("girdi/../disarda.png", self.root, None)
        self.assertIsNone(e)  # eski davranis; kisitli kipte reddedilir (asagida)


class Kisitli(Temel):
    def test_listede_girdi_hep_var_ve_tekrarsiz(self):
        self.assertEqual([p.name for p in self.izinli], ["girdi"])
        iki = IZIN.izinli_klasorler(self.root, os.pathsep.join(["girdi", str(self.dis), "", str(self.dis)]))
        self.assertEqual(len(iki), 2)

    def test_girdi_icindeki_dosyalar_gecer(self):
        self.tamam(self.root / "girdi" / "a.png")
        self.tamam("girdi/a.png")
        self.tamam("girdi/alt/b.png")

    @unittest.skipUnless(WIN, "backslash is a path separator only on Windows")
    def test_ters_bolu_ayirici_windows(self):
        # On Linux/macOS a backslash is an ordinary file-name character, so this input is a different (missing) file there.
        # (Before 2026-11-21 this line sat in the test above and failed on Linux/macOS: measured in WSL Ubuntu.)
        self.tamam("girdi" + BS + "alt" + BS + "b.png")

    @unittest.skipIf(WIN, "POSIX only: backslash is a literal file-name character")
    def test_posix_ters_bolu_dosya_adi_disari_cikaramaz(self):
        # The server itself is Windows-only (kernel32); this pins the module's conservative result on POSIX:
        # a backslash name is one path component, never a way out of (or into) the allowed folder.
        self.red("girdi" + BS + "alt" + BS + "b.png")
        self.red("girdi" + BS + ".." + BS + "disarda.png")
        self.red(str(self.root / "girdi") + BS + "a.png")

    def test_disarisi_reddedilir(self):
        self.red(self.root / "disarda.png")
        self.red("disarda.png")
        self.red(self.dis / "gizli.png")

    def test_nokta_nokta_reddedilir_her_bicimde(self):
        (self.root / "girdi" / "alt").mkdir(exist_ok=True)
        for y in ("girdi/../disarda.png", "girdi" + BS + ".." + BS + "disarda.png", "girdi/alt/../a.png",
                  "../dis/gizli.png", str(self.root / "girdi") + "/../../dis/gizli.png"):
            self.red(y)

    def test_kardes_klasor_on_ek_tuzagi(self):
        evil = self.root / "girdi_evil"
        evil.mkdir()
        (evil / "x.png").write_bytes(b"x")
        self.red(evil / "x.png")
        self.red("girdi_evil/x.png")

    def test_ek_klasor_env_ile(self):
        ek = IZIN.izinli_klasorler(self.root, str(self.dis))
        self.tamam(self.dis / "gizli.png", ek)
        self.tamam("girdi/a.png", ek)  # girdi her zaman var
        self.red(self.root / "disarda.png", ek)

    def test_ek_klasor_goreli_girdi_ROOTa_gore(self):
        (self.root / "resimler").mkdir()
        (self.root / "resimler" / "r.png").write_bytes(b"x")
        ek = IZIN.izinli_klasorler(self.root, "resimler")
        self.tamam("resimler/r.png", ek)

    def test_olmayan_dosya_ve_klasor_dosya_degil(self):
        self.red("girdi/yok.png")
        self.red("girdi/alt")
        self.red("girdi")

    def test_girdi_klasoru_hic_yoksa_temiz_hata(self):
        shutil.rmtree(str(self.root / "girdi"))
        self.red("girdi/a.png")

    def test_hata_iletisi_ne_yapilacagini_soyler(self):
        e = self.red(self.dis / "gizli.png")
        self.assertIn("girdi", e)
        self.assertIn("user", e)  # "yalniz kullanicinin verdigi yol" ipucu

    @unittest.skipUnless(WIN, "Windows path forms")
    def test_windows_bicimleri(self):
        self.red("girdi" + BS + "a.png:gizli")  # akis adi
        self.red(BS + BS + "?" + BS + str(self.root / "girdi" / "a.png"))  # uzun yol oneki
        self.red(BS + BS + "sunucu" + BS + "paylasim" + BS + "a.png")  # UNC
        self.red("//./C:/x.png")
        self.red("C:girdi" + BS + "a.png")  # surucu-goreli

    @unittest.skipUnless(WIN, "Windows is case-insensitive")
    def test_windows_buyuk_kucuk_harf(self):
        self.tamam("GIRDI/A.PNG")

    @unittest.skipUnless(WIN, "Windows path forms")
    def test_sonda_nokta_ve_bosluk(self):
        # Windows bunlari soyer; sonuc yine girdi icinde kalmali ya da reddedilmeli (disari asla)
        for y in ("girdi/a.png.", "girdi/a.png "):
            p, e = IZIN.yol_coz(y, self.root, self.izinli)
            if p is not None:
                self.assertTrue(str(p).lower().startswith(str(self.root.resolve() / "girdi").lower()))


class Baglar(Temel):
    def test_dosya_sembolik_bagi_disari_gider_reddedilir(self):
        try:
            os.symlink(str(self.dis / "gizli.png"), str(self.root / "girdi" / "bag.png"))
        except (OSError, NotImplementedError, AttributeError):
            self.skipTest("sembolik bag olusturulamadi (yetki yok)")
        e = self.red("girdi/bag.png")
        self.assertIn("sembolik", e)

    def test_klasor_sembolik_bagi_reddedilir(self):
        try:
            os.symlink(str(self.dis), str(self.root / "girdi" / "baglanti"), target_is_directory=True)
        except (OSError, NotImplementedError, AttributeError):
            self.skipTest("sembolik bag olusturulamadi (yetki yok)")
        self.red("girdi/baglanti/gizli.png")

    @unittest.skipUnless(WIN and shutil.which("cmd.exe"), "junction needs Windows cmd.exe")
    def test_junction_reddedilir(self):
        j = self.root / "girdi" / "kavsak"
        r = subprocess.run(["cmd.exe", "/c", "mklink", "/J", str(j), str(self.dis)], capture_output=True,
                           creationflags=CF)
        if r.returncode != 0 or not j.exists():
            self.skipTest("junction olusturulamadi")
        e = self.red("girdi/kavsak/gizli.png")
        self.assertIn("birlesim", e)
        # junction'in gercekten disari gittigi (testin anlamli oldugu): dolayli okuma mumkun
        self.assertTrue((self.root / "girdi" / "kavsak" / "gizli.png").is_file())

    def test_realpath_ikinci_savunma_tek_basina_yeter(self):
        # Mutation guard (denetci 2026-11-21): with the first defense (_bag_mi, lstat per component) blinded, the realpath
        # check alone must still refuse a link that leaves the folder. Before this test, deleting the realpath check
        # changed no result (measured: mutant run in WSL Ubuntu), i.e. the second defense was unguarded.
        try:
            os.symlink(str(self.dis / "gizli.png"), str(self.root / "girdi" / "bag.png"))
            os.symlink(str(self.dis), str(self.root / "girdi" / "baglanti"), target_is_directory=True)
        except (OSError, NotImplementedError, AttributeError):
            self.skipTest("sembolik bag olusturulamadi (yetki yok)")
        eski = IZIN._bag_mi
        IZIN._bag_mi = lambda path: False
        self.addCleanup(setattr, IZIN, "_bag_mi", eski)
        e = self.red("girdi/bag.png")
        self.assertIn("gercek yolu", e)
        e = self.red("girdi/baglanti/gizli.png")
        self.assertIn("gercek yolu", e)

    def test_izinli_klasorun_kendisi_baglantiysa_kullanici_secimidir(self):
        # yalniz ALTINDAKI baglar reddedilir; kok kullanicinin acik secimi
        try:
            gercek = self.t / "gercek_girdi"
            gercek.mkdir()
            (gercek / "z.png").write_bytes(b"x")
            os.symlink(str(gercek), str(self.t / "kok2"), target_is_directory=True)
        except (OSError, NotImplementedError, AttributeError):
            self.skipTest("sembolik bag olusturulamadi (yetki yok)")
        ek = IZIN.izinli_klasorler(self.root, str(self.t / "kok2"))
        self.tamam(self.t / "kok2" / "z.png", ek)


class Goster(Temel):
    def test_durum_maskeli_kisisel_yol_yok(self):
        g = IZIN.goster(self.izinli, self.root)
        self.assertEqual(g["mode"], "restricted")
        self.assertEqual(g["dirs"], ["<ROOT>/girdi"])
        self.assertNotIn(str(self.t), repr(g))
        self.assertEqual(IZIN.goster(None, self.root), {"mode": "open", "dirs": []})
        g2 = IZIN.goster(IZIN.izinli_klasorler(self.root, str(self.dis)), self.root)
        self.assertEqual(g2["dirs"], ["<ROOT>/girdi", "<outside ROOT>"])
        self.assertNotIn(str(self.t), repr(g2))


class Statik(unittest.TestCase):
    def test_sunucu_modulu_kullaniyor_ve_acik_kapatma_anahtari_duruyor(self):
        kaynak = (KOK / "mcp" / "videoturko_mcp.py").read_text(encoding="utf-8")
        self.assertIn("init_izin.py", kaynak)
        self.assertIn("VT_MCP_INIT_DIR", kaynak)
        self.assertIn("VT_MCP_ALLOW_INIT", kaynak)  # kapatma anahtari kaybolmasin
        self.assertIn("_IZIN.yol_coz", kaynak)

    def test_modul_ascii_ve_stdlib(self):
        b = (KOK / "mcp" / "init_izin.py").read_bytes()
        self.assertTrue(all(c < 128 for c in b), "ASCII olmali")
        kaynak = b.decode("ascii")
        for satir in kaynak.splitlines():
            if satir.startswith(("import ", "from ")):
                self.assertTrue(satir.split()[1].split(".")[0] in ("os", "stat", "pathlib"), satir)


@unittest.skipUnless(WIN, "the MCP server uses kernel32")
class SunucuBaglantisi(unittest.TestCase):
    """generate_video: stub FastMCP ile gercek sunucu dosyasi; motor yok -> gecerli yol 'hazir degil'e ulasir."""

    def setUp(self):
        self.t = Path(tempfile.mkdtemp(prefix="vt_mcp_"))
        self.addCleanup(shutil.rmtree, str(self.t), True)
        (self.t / "girdi").mkdir()
        (self.t / "girdi" / "a.png").write_bytes(b"x")
        (self.t / "disarda.png").write_bytes(b"x")
        self.eski_mod = {k: sys.modules.get(k) for k in ("mcp", "mcp.server", "mcp.server.fastmcp")}
        self.eski_env = {k: os.environ.get(k) for k in ("VT_ROOT", "VT_MCP_INIT_DIR", "VT_MCP_ALLOW_INIT")}
        st = types.ModuleType("mcp.server.fastmcp")

        class FastMCP:
            def __init__(self, *a, **k):
                pass

            def tool(self):
                return lambda f: f

            def run(self):
                pass

        st.FastMCP = FastMCP
        for ad, m in (("mcp", types.ModuleType("mcp")), ("mcp.server", types.ModuleType("mcp.server")),
                      ("mcp.server.fastmcp", st)):
            sys.modules[ad] = m
        os.environ["VT_ROOT"] = str(self.t)
        os.environ.pop("VT_MCP_ALLOW_INIT", None)
        self.addCleanup(self.geri)
        self.srv = yukle("vt_srv_test", KOK / "mcp" / "videoturko_mcp.py")

    def geri(self):
        for k, v in self.eski_mod.items():
            if v is None:
                sys.modules.pop(k, None)
            else:
                sys.modules[k] = v
        for k, v in self.eski_env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v

    def uret(self, yol):
        return self.srv.generate_video("a cat", frames=56, init_image=str(yol))

    def test_varsayilan_acik_disardaki_dosya_kabul_hazir_degile_ulasir(self):
        os.environ.pop("VT_MCP_INIT_DIR", None)
        r = self.uret(self.t / "disarda.png")
        self.assertEqual(r.get("error"), "hazir degil", r)  # yol denetimini gecti (motor yok)
        self.assertEqual(self.srv.status()["init_image"]["mode"], "open")

    def test_kisitli_disardaki_dosya_reddedilir_icerdeki_gecer(self):
        os.environ["VT_MCP_INIT_DIR"] = "girdi"
        r = self.uret(self.t / "disarda.png")
        self.assertIn("izinli klasorlerin disinda", r.get("error", ""), r)
        r = self.uret("girdi/../disarda.png")
        self.assertIn("'..'", r.get("error", ""), r)
        r = self.uret(self.t / "girdi" / "a.png")
        self.assertEqual(r.get("error"), "hazir degil", r)
        st = self.srv.status()["init_image"]
        self.assertEqual(st, {"mode": "restricted", "dirs": ["<ROOT>/girdi"]})

    def test_allow_init_0_hala_hepsini_kapatir(self):
        os.environ["VT_MCP_INIT_DIR"] = "girdi"
        os.environ["VT_MCP_ALLOW_INIT"] = "0"
        r = self.uret(self.t / "girdi" / "a.png")
        self.assertIn("VT_MCP_ALLOW_INIT", r.get("error", ""), r)

    def test_kare_siniri_ve_satir_sonu_denetimi_korunur(self):
        r = self.srv.generate_video("a cat", frames=209, init_image=str(self.t / "girdi" / "a.png"))
        self.assertIn("192", r.get("error", ""), r)
        r = self.uret("girdi/a.png" + chr(10) + "x")
        self.assertIn("satir sonu", r.get("error", ""), r)


if __name__ == "__main__":
    unittest.main()
