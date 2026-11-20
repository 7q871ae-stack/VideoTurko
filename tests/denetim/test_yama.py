"""KL-05 yama bekcisi (scripts/yama_bekcisi.py, `denetim.py --kapi yama`) demir cubuk testi.

  python -I tests/denetim/test_yama.py     -> son satir: TEST_YAMA: N/N GECTI (cikis 0)

NEGATIF once: CRLF'li yama, tablo yok, hash uyusmazligi, tabloda olmayan yama, dosyasi olmayan tablo satiri, SERIES eksik/sirasiz/yinelenen, guvensiz hedef yol,
.cmd icin eol=crlf kurali yok, .cmd'de bare LF, eol=lf dosyada CR, `git apply --check` (yerel): uygulanmayan yama, yanlis taban, CI'da reddi.
POZITIF: temiz ornek seri, CRLF kuralli .cmd, gercek repo. Sahte veri calisma aninda uretilir; ag yok, GPU yok.
"""
import hashlib, os, subprocess, sys, tempfile, unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test_denetim import calistir, Sahte, KOK   # noqa: E402

YAMA_BETIGI = os.path.abspath(os.environ.get('DENETIM_TEST_YAMA') or os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'scripts', 'yama_bekcisi.py'))
GOVDE = ('From 1111111111111111111111111111111111111111 Mon Sep 17 00:00:00 2001\nFrom: A <noreply@example.invalid>\nDate: Thu, 19 Nov 2026 00:00:00 +0000\n'
         'Subject: [PATCH] t\n\n---\n a.txt | 2 +-\n\ndiff --git a/a.txt b/a.txt\n--- a/a.txt\n+++ b/a.txt\n@@ -1 +1 @@\n-eski\n+yeni\n-- \n2.0\n')
GENEL_ATTR = '*.patch -text\n*.ps1 text eol=lf\n*.py text eol=lf\n*.cmd text eol=crlf\n'


def sha(b):
    return hashlib.sha256(b).hexdigest()


def temiz_seri(s, govde=GOVDE):
    """Temiz sahte repo: 2 yama, SERIES, tablo, .gitattributes."""
    s.yaz('.gitattributes', GENEL_ATTR)
    g2 = govde.replace('+yeni', '+yeni2').replace('-eski', '-yeni')
    s.yaz('patches/sdcpp/01-bir.patch', govde).yaz('patches/sdcpp/02-iki.patch', g2)
    s.yaz('patches/SERIES.txt', '# yorum\nsdcpp/01-bir.patch\nsdcpp/02-iki.patch\n')
    tablo(s)
    return s


def tablo(s, ek=''):
    satirlar = []
    for ad in ('patches/sdcpp/01-bir.patch', 'patches/sdcpp/02-iki.patch'):
        if os.path.exists(os.path.join(s.kok, *ad.split('/'))):
            satirlar.append('%s  %s' % (sha(open(os.path.join(s.kok, *ad.split('/')), 'rb').read()), ad))
    s.yaz('patches/SHA256SUMS', '# t\n' + '\n'.join(satirlar) + '\n' + ek)


class Yama(unittest.TestCase):
    def kos(self, s):
        return calistir('--hizli', '--kapi', 'yama', kok=s.kok)

    def kirmizi(self, s, beklenen):
        rc, o, _ = self.kos(s)
        self.assertEqual(rc, 1, o)
        self.assertIn('SONUC: KIRMIZI', o)
        for b in beklenen:
            self.assertIn(b, o)
        return o

    def test_pozitif_temiz_seri(self):
        with Sahte() as s:
            rc, o, _ = self.kos(temiz_seri(s))
            self.assertEqual(rc, 0, o); self.assertIn('SONUC: GECTI', o)

    def test_negatif_crlf_yama(self):
        with Sahte() as s:
            temiz_seri(s)
            s.yaz('patches/sdcpp/01-bir.patch', GOVDE.replace('\n', '\r\n')); tablo(s)   # tablo guncel: yalniz CR kapisi yakalamali
            o = self.kirmizi(s, ['CR bayti', '01-bir.patch:1'])
            self.assertNotIn('UYUSMUYOR', o)

    def test_negatif_tek_cr_bile_yakalanir(self):
        with Sahte() as s:
            temiz_seri(s)
            s.yaz('patches/sdcpp/02-iki.patch', GOVDE.replace('+yeni', '+yeni\r', 1).replace('-eski', '-yeni')); tablo(s)
            self.kirmizi(s, ['CR bayti', '02-iki.patch'])

    def test_negatif_tablo_yok(self):
        with Sahte() as s:
            temiz_seri(s)
            os.remove(os.path.join(s.kok, 'patches', 'SHA256SUMS'))
            self.kirmizi(s, ['SHA256SUMS yok'])

    def test_negatif_hash_uyusmuyor(self):
        with Sahte() as s:
            temiz_seri(s)
            s.yaz('patches/sdcpp/01-bir.patch', GOVDE.replace('+yeni', '+bozuk'))   # tablo eski kaldi
            self.kirmizi(s, ['01-bir.patch', 'UYUSMUYOR'])

    def test_negatif_tabloda_olmayan_yama(self):
        with Sahte() as s:
            temiz_seri(s)
            s.yaz('patches/sdcpp/03-uc.patch', GOVDE); s.yaz('patches/SERIES.txt', '# y\nsdcpp/01-bir.patch\nsdcpp/02-iki.patch\nsdcpp/03-uc.patch\n')
            self.kirmizi(s, ['03-uc.patch tabloda yok'])

    def test_negatif_dosyasi_olmayan_tablo_satiri(self):
        with Sahte() as s:
            temiz_seri(s)
            tablo(s, ek='%s  patches/sdcpp/09-hayalet.patch\n' % ('a' * 64))
            self.kirmizi(s, ['09-hayalet.patch tabloda var, dosya yok'])

    def test_negatif_tablo_satiri_bozuk(self):
        with Sahte() as s:
            temiz_seri(s)
            tablo(s, ek='kisa hash patches/x.patch\n')
            self.kirmizi(s, ['satir bicimi bozuk'])

    def test_negatif_series_listede_olmayan_yama(self):
        with Sahte() as s:
            temiz_seri(s)
            s.yaz('patches/SERIES.txt', 'sdcpp/01-bir.patch\n')
            self.kirmizi(s, ['02-iki.patch listede degil'])

    def test_negatif_series_dosyasi_olmayan_satir(self):
        with Sahte() as s:
            temiz_seri(s)
            s.yaz('patches/SERIES.txt', 'sdcpp/01-bir.patch\nsdcpp/02-iki.patch\nsdcpp/05-yok.patch\n')
            self.kirmizi(s, ['listelenen yama yok'])

    def test_negatif_series_sirasiz_ve_yinelenen(self):
        with Sahte() as s:
            temiz_seri(s)
            s.yaz('patches/SERIES.txt', 'sdcpp/02-iki.patch\nsdcpp/01-bir.patch\nsdcpp/01-bir.patch\n')
            self.kirmizi(s, ['sirasi bozuk', 'yinelenen'])

    def test_negatif_guvensiz_hedef_yol(self):
        for kotu in ('../disari.txt', '/etc/x', 'C:/x/y.txt'):
            with Sahte() as s:
                temiz_seri(s)
                s.yaz('patches/sdcpp/02-iki.patch', GOVDE.replace('a/a.txt b/a.txt', 'a/%s b/%s' % (kotu, kotu))); tablo(s)
                self.kirmizi(s, ['hedef yolu guvensiz'])

    def test_negatif_yama_degil(self):
        with Sahte() as s:
            temiz_seri(s)
            s.yaz('patches/sdcpp/02-iki.patch', 'sadece metin\n'); tablo(s)
            self.kirmizi(s, ['diff --git'])

    def test_negatif_cmd_icin_kural_yok(self):
        with Sahte() as s:
            temiz_seri(s)
            s.yaz('.gitattributes', '*.patch -text\n*.py text eol=lf\n'); s.yaz('kur.cmd', '@echo off\r\n')
            self.kirmizi(s, ['kur.cmd', 'eol=crlf` kurali yok'])

    def test_negatif_cmd_bare_lf(self):
        with Sahte() as s:
            temiz_seri(s)
            s.yaz('kur.cmd', '@echo off\necho x\n')
            self.kirmizi(s, ['kur.cmd:1', 'CRLF degil'])

    def test_pozitif_cmd_crlf(self):
        with Sahte() as s:
            temiz_seri(s)
            s.yaz('kur.cmd', '@echo off\r\necho x\r\n')
            rc, o, _ = self.kos(s)
            self.assertEqual(rc, 0, o)

    def test_negatif_lf_dosyada_cr(self):
        with Sahte() as s:
            temiz_seri(s)
            s.yaz('scripts/a.py', 'x = 1\r\ny = 2\r\n')
            self.kirmizi(s, ['scripts/a.py', 'eol=lf'])

    def test_kapi_yama_tablo_ile_birlikte_degisirse_yesil_sinir(self):
        # Belgelenen SINIR: tablo ayni depoda; yama ve tablo birlikte degisirse bu kapi yesil verir (pr_kapi `patches/` degisimini SARI yakalar).
        with Sahte() as s:
            temiz_seri(s)
            s.yaz('patches/sdcpp/01-bir.patch', GOVDE.replace('+yeni', '+baska')); tablo(s)
            rc, o, _ = self.kos(s)
            self.assertEqual(rc, 0, o)

    def test_pozitif_gercek_repo(self):
        # `*.cmd` icin .gitattributes kurali KL-11'de (mimar) gelir; o satir disinda bulgu olmamali.
        rc, o, _ = calistir('--hizli', '--kapi', 'yama', kok=KOK)
        kirmizi = [l for l in o.splitlines() if l.strip().startswith('KIRMIZI') and 'eol=crlf` kurali yok' not in l]
        self.assertEqual(kirmizi, [], o)


class UygulaKontrol(unittest.TestCase):
    """`git apply --check` (yalniz yerel): gecici git deposunda sahte taban + yamalar."""
    G = ['git', '-c', 'user.name=t', '-c', 'user.email=t@example.invalid', '-c', 'commit.gpgsign=false']

    def git(self, d, *a):
        return subprocess.run(self.G + ['-C', d] + list(a), capture_output=True, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))

    def kaynak(self, td):
        d = os.path.join(td, 'kaynak'); os.makedirs(d)
        open(os.path.join(d, 'a.txt'), 'w', newline='\n').write('eski\n')
        self.git(d, 'init', '-q'); self.git(d, 'add', '.'); self.git(d, 'commit', '-q', '-m', 'taban')
        return d, self.git(d, 'rev-parse', 'HEAD').stdout.decode().strip()

    def kos(self, s, d, ortam=None, *ek):
        env = dict(os.environ); env.pop('CI', None); env.pop('GITHUB_ACTIONS', None); env.update(ortam or {})
        p = subprocess.run([sys.executable, '-I', YAMA_BETIGI, '--kok', s.kok, '--uygula-kontrol', '--sdcpp', d] + list(ek), capture_output=True, env=env,
                           creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        return p.returncode, p.stdout.decode('utf-8', 'replace')

    def seri(self, s, taban):
        temiz_seri(s)
        s.yaz('patches/SERIES.txt', '# Bases: stable-diffusion.cpp %s\nsdcpp/01-bir.patch\nsdcpp/02-iki.patch\n' % taban[:10])

    def test_pozitif_sirayla_uygulanir(self):
        with tempfile.TemporaryDirectory() as td, Sahte() as s:
            d, h = self.kaynak(td); self.seri(s, h)
            rc, o = self.kos(s, d)
            self.assertEqual(rc, 0, o); self.assertIn('2 yama', o)
            self.assertEqual(open(os.path.join(d, 'a.txt')).read(), 'eski\n')   # calisma agacina YAZILMADI
            self.assertEqual(self.git(d, 'status', '--porcelain').stdout, b'')

    def test_negatif_uygulanmayan_yama(self):
        with tempfile.TemporaryDirectory() as td, Sahte() as s:
            d, h = self.kaynak(td); self.seri(s, h)
            s.yaz('patches/sdcpp/02-iki.patch', GOVDE.replace('-eski', '-hic_yok').replace('+yeni', '+x'))
            rc, o = self.kos(s, d)
            self.assertEqual(rc, 1, o); self.assertIn('02-iki.patch uygulanmiyor', o)

    def test_negatif_yanlis_taban(self):
        with tempfile.TemporaryDirectory() as td, Sahte() as s:
            d, h = self.kaynak(td); self.seri(s, '0' * 40)
            rc, o = self.kos(s, d)
            self.assertEqual(rc, 1, o); self.assertIn('yanlis taban', o)

    def test_negatif_kaynak_verilmedi_yesil_degil(self):
        with Sahte() as s:
            self.seri(s, 'a' * 40)
            rc, o = self.kos(s, os.path.join(s.kok, 'yok'))
            self.assertNotEqual(rc, 0, o); self.assertNotIn('SONUC: GECTI', o)

    def test_negatif_ci_ortaminda_reddedilir(self):
        with tempfile.TemporaryDirectory() as td, Sahte() as s:
            d, h = self.kaynak(td); self.seri(s, h)
            rc, o = self.kos(s, d, ortam={'GITHUB_ACTIONS': 'true'})
            self.assertEqual(rc, 3, o); self.assertIn('yalniz yerelde', o)


if __name__ == '__main__':
    toplam = unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromTestCase(Yama), unittest.defaultTestLoader.loadTestsFromTestCase(UygulaKontrol)])
    r = unittest.TextTestRunner(verbosity=0, stream=sys.stderr).run(toplam)
    n = r.testsRun
    print('TEST_YAMA: %d/%d %s' % (n - len(r.failures) - len(r.errors), n, 'GECTI' if r.wasSuccessful() else 'KIRIK'))
    sys.exit(0 if r.wasSuccessful() else 1)
