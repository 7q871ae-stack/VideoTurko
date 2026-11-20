"""KL-04 gizlilik kapisi (scripts/gizlilik_denetimi.py, `denetim.py --kapi gizlilik`) demir cubuk testi.

  python -I tests/denetim/test_gizlilik.py     -> son satir: TEST_GIZLILIK: N/N GECTI (cikis 0)

NEGATIF once: sahte sir, sahte kisisel yol, e-posta, UTF-16 (BOM'lu ve BOM'suz), ikili icinde UTF-16, 8.3 kisa ad, yama Date saat dilimi: hepsi
KIRMIZI olmali; cikti maskeli olmali (sahte sir ve ad ekrana tam basilmaz). POZITIF: yer tutucu yollar, noreply, dar lisans istisnasi, gercek repo.
Sahte kotu veri calisma aninda PARCALARDAN uretilir (bu dosya kendi kapisindan gecer; kaynakta sir/yol/ham gorunmez karakter yok).
"""
import os, sys, unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test_denetim import calistir, Sahte, KOK   # noqa: E402

BS = chr(92)
SAHTE_TOKEN = 'ghp_' + 'A1b2C3d4' * 4 + 'WxYz'          # 36 karakter govde: sahte, hicbir hesaba ait degil
SAHTE_AD = 'zed' + 'qux'


def yol(ad='x', son='a.txt'):
    return 'C:' + BS + 'Users' + BS + ad + BS + son


class Gizlilik(unittest.TestCase):
    def kos(self, s, *ek, ortam=None):
        return calistir('--hizli', '--kapi', 'gizlilik', *ek, kok=s.kok, ortam=ortam)

    def kirmizi(self, s, beklenen, yasak=()):
        rc, o, _ = self.kos(s)
        self.assertEqual(rc, 1, o)
        self.assertIn('SONUC: KIRMIZI', o)
        for b in beklenen:
            self.assertIn(b, o)
        for y in yasak:   # maskeleme: ham deger ekrana basilmamali
            self.assertNotIn(y, o, 'ham deger cikti')
        return o

    def test_negatif_sahte_kullanici_yolu(self):
        with Sahte() as s:
            self.kirmizi(s.yaz('a.txt', 'dosya: ' + yol() + '\n'), ['a.txt:satir 1', 'kisisel_yol', 'profil yolu'])

    def test_negatif_yol_ad_ekrana_basilmaz(self):
        with Sahte() as s:
            self.kirmizi(s.yaz('a.txt', yol(SAHTE_AD) + '\n'), ['kisisel_yol'], yasak=[SAHTE_AD])

    def test_negatif_sahte_ghp_token_maskeli(self):
        with Sahte() as s:
            o = self.kirmizi(s.yaz('b.txt', 'token ' + SAHTE_TOKEN + '\n'), ['sir', 'ghp_...(40 krk)'], yasak=[SAHTE_TOKEN, SAHTE_TOKEN[8:]])
            self.assertIn('b.txt:satir 1', o)

    def test_negatif_anahtar_atamasi_ve_ozel_anahtar(self):
        with Sahte() as s:
            self.kirmizi(s.yaz('c.txt', 'api_key = "' + 'k' * 24 + '"\n' + '-----BEGIN ' + 'RSA PRIVATE KEY-----\n'), ['c.txt:satir 1', 'c.txt:satir 2'])

    def test_negatif_eposta_maskeli(self):
        with Sahte() as s:
            self.kirmizi(s.yaz('d.txt', 'yaz: ali.veli' + '@' + 'gma' + 'il.com\n'), ['e_posta', '*@gma' + 'il.com'], yasak=['ali.veli'])

    def test_negatif_utf16_bom(self):
        with Sahte() as s:
            self.kirmizi(s.yaz('e.txt', (yol('bob') + '\n').encode('utf-16')), ['e.txt', 'kisisel_yol'])

    def test_negatif_utf16_bomsuz_metin(self):
        with Sahte() as s:
            self.kirmizi(s.yaz('f.txt', (yol('bob') + '\n').encode('utf-16-le')), ['f.txt', 'kisisel_yol', 'utf16'])

    def test_negatif_ikili_icinde_utf16_yol(self):
        with Sahte() as s:
            self.kirmizi(s.yaz('motor.dll', b'MZ\x00\x01' + b'\xaa' * 7 + (yol('bob')).encode('utf-16-le') + b'\x00\x00zz'), ['motor.dll', 'kisisel_yol'])

    def test_negatif_ikili_icinde_ascii_sir(self):
        with Sahte() as s:
            self.kirmizi(s.yaz('m.dll', b'MZ\x00' + SAHTE_TOKEN.encode() + b'\x00'), ['m.dll', 'sir'])

    def test_negatif_kisa_ad_8_3(self):
        with Sahte() as s:
            self.kirmizi(s.yaz('g.txt', 'C:' + BS + 'Users' + BS + 'ABC123~1' + BS + 'x\n'), ['kisisel_yol'])

    def test_negatif_makineye_ozgu_surucu(self):
        with Sahte() as s:
            self.kirmizi(s.yaz('h.md', 'modeller E:' + BS + 'ai_models gibi\n'), ['kisisel_yol'])

    def test_negatif_unix_home(self):
        with Sahte() as s:
            self.kirmizi(s.yaz('h.sh', 'cd /home/' + SAHTE_AD + '/proje\n'), ['kisisel_yol'], yasak=[SAHTE_AD])

    def test_negatif_saat_dilimi(self):
        with Sahte() as s:
            self.kirmizi(s.yaz('log.md', 'zaman: 2026-11-20T10:00:00+' + '03:00\n'), ['zaman_izi'])

    def test_negatif_yama_date_saat_dilimi(self):
        with Sahte() as s:
            self.kirmizi(s.yaz('patches/sdcpp/01.patch', 'From abc\nFrom: A <noreply@example.invalid>\nDate: Thu, 19 Nov 2026 00:03:30 +' + '0300\n'),
                         ['patches/sdcpp/01.patch:3', 'Date', '+0300'])

    def test_negatif_lisans_adresi_baska_dosyada(self):
        with Sahte() as s:
            self.kirmizi(s.yaz('docs/baska.md', 'mail api' + '@minimax.io\n'), ['docs/baska.md', 'e_posta'])

    def test_negatif_yer_tutucu_olmayan_tek_harf_ad(self):
        with Sahte() as s:
            self.kirmizi(s.yaz('a.md', yol('x') + '\n'), ['kisisel_yol'])

    def test_negatif_kisisel_terim_listesi(self):
        with Sahte() as s, Sahte() as dis:
            dis.yaz('liste.txt', SAHTE_AD + '\n')
            rc, o, _ = self.kos(s.yaz('n.md', 'merhaba ' + SAHTE_AD + ' dunya\n'), ortam={'VT_GIZLILIK_KISISEL': os.path.join(dis.kok, 'liste.txt')})
            self.assertEqual(rc, 1, o); self.assertIn('kisisel_terim', o); self.assertNotIn(SAHTE_AD, o)

    def test_negatif_kisisel_liste_depo_icinde_olamaz(self):
        with Sahte() as s:
            s.yaz('liste.txt', 'abc\n')
            rc, o, _ = self.kos(s, ortam={'VT_GIZLILIK_KISISEL': os.path.join(s.kok, 'liste.txt')})
            self.assertEqual(rc, 1, o); self.assertIn('depo icinde', o)

    def test_negatif_buyuk_dosya_yesil_verilmez(self):
        import importlib.util
        yol_ = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'scripts', 'gizlilik_denetimi.py')
        spec = importlib.util.spec_from_file_location('gz', yol_); gz = importlib.util.module_from_spec(spec); spec.loader.exec_module(gz)
        eski = gz.BOYUT_TAVANI
        try:
            gz.BOYUT_TAVANI = 10
            with Sahte() as s:
                s.yaz('buyuk.txt', 'a' * 50)
                class C:   # denetim.Baglam yerine minimal baglam
                    kok = s.kok; dosyalar = ['buyuk.txt']
                    bayt = staticmethod(lambda r: open(os.path.join(s.kok, r), 'rb').read())
                bulgu, _ = gz.kapi_gizlilik(C)
                self.assertTrue(any('taranamadi' in b for b in bulgu), bulgu)
        finally:
            gz.BOYUT_TAVANI = eski

    # ---- pozitif
    def test_pozitif_yer_tutucular_ve_serbest_adresler(self):
        with Sahte() as s:
            s.yaz('ok.md', 'C:' + BS + 'Users' + BS + '<name>' + BS + 'a ve %USERPROFILE% ve C:' + BS + 'vt ve C:' + BS + 'Program Files ve /home/<kullanici>/x\n'
                           'From: VideoTurko <noreply@example.invalid>\nCo-Authored-By: A <noreply' + '@anthropic.com>\n12345+ad' + '@users.noreply.github.com\n')
            s.yaz('docs/LISANS_UYARISI.md', 'yetki: api' + '@minimax.io\n')
            s.yaz('README.tr.md', 'yetki: api' + '@minimax.io\n')
            s.yaz('patches/x.patch', 'From abc\nDate: Thu, 19 Nov 2026 00:03:30 +0000\n')
            rc, o, _ = self.kos(s)
            self.assertEqual(rc, 0, o); self.assertIn('SONUC: GECTI', o)

    def test_pozitif_gercek_repo(self):
        rc, o, _ = calistir('--hizli', '--kapi', 'gizlilik', kok=KOK)
        self.assertEqual(rc, 0, o); self.assertIn('SONUC: GECTI', o)


if __name__ == '__main__':
    r = unittest.TextTestRunner(verbosity=0, stream=sys.stderr).run(unittest.defaultTestLoader.loadTestsFromTestCase(Gizlilik))
    n = r.testsRun
    print('TEST_GIZLILIK: %d/%d %s' % (n - len(r.failures) - len(r.errors), n, 'GECTI' if r.wasSuccessful() else 'KIRIK'))
    sys.exit(0 if r.wasSuccessful() else 1)
