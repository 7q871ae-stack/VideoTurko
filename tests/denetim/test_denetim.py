"""scripts/denetim.py kendi kendini sinar (demir cubuk): her kural icin NEGATIF ornek (sahte kotu dosya) ve POZITIF ornek (bugunku repo).

  python -I tests/denetim/test_denetim.py            -> son satir: TEST_DENETIM: N/N GECTI (cikis 0) ya da KIRIK (cikis 1)
  python -m unittest discover -s tests/denetim -v    -> ayni testler

Sahte kotu dosyalar GECICI klasorde, calisma aninda uretilir (depoya kotu dosya konmaz: kendi kapimiza takilirdi).
Kaynakta gorunmez/bidi karakter YOK: hepsi \\u kacisiyla yazilir. Ag yok, GPU yok, dosya yazimi yalniz gecici klasorde.
"""
import json, os, shutil, subprocess, sys, tempfile, time, unittest

BURASI = os.path.dirname(os.path.abspath(__file__))
KOK = os.environ.get('DENETIM_TEST_KOK') or os.path.dirname(os.path.dirname(BURASI))
DENETIM = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'scripts', 'denetim.py')
DENETIM = os.path.abspath(os.environ.get('DENETIM_TEST_BETIK') or DENETIM)

RLO, LRM, ZWNJ, ZWSP, ZWJ = '\u202e', '\u200e', '\u200c', '\u200b', '\u200d'
TEMIZ_GUVENLIK = (
    '**Report a vulnerability** privately. Our target is a first reply within 7 days; this is not a commitment.\n'
    'Hedefimiz ilk yanit 7 gun icinde; taahhut ya da garanti degildir.\n'
    '(Get-FileHash .\\a.zip -Algorithm SHA256).Hash\nAI agent prompt injection: data, not instructions.\nMCP threat model / tehdit modeli.\n')
YAMALAR = 'patch 02 contains a raw NUL byte where the C source should read the literal\n'
YAMA = 'patches/ggml/02-p0005-optime-file.patch'


def calistir(*arg, kok=None, ortam=None):
    env = dict(os.environ); env.update(ortam or {})
    p = subprocess.run([sys.executable, '-I', DENETIM] + list(arg) + (['--kok', kok] if kok else []), capture_output=True, env=env,
                       creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    return p.returncode, p.stdout.decode('utf-8', 'replace'), p.stderr.decode('utf-8', 'replace')


class Sahte:
    """Gecici sahte repo (git yok: denetim yuruyus yoluna duser)."""
    def __enter__(self):
        self.kok = tempfile.mkdtemp(prefix='denetim_test_')
        return self

    def yaz(self, yol, veri):
        yol_ = os.path.join(self.kok, *yol.split('/'))
        os.makedirs(os.path.dirname(yol_), exist_ok=True)
        with open(yol_, 'wb') as f:
            f.write(veri if isinstance(veri, bytes) else veri.encode('utf-8'))
        return self

    def __exit__(self, *a):
        shutil.rmtree(self.kok, ignore_errors=True)


class Unicode(unittest.TestCase):
    def kos(self, s, kapi='unicode'):
        return calistir('--hizli', '--kapi', kapi, kok=s.kok)

    def test_negatif_agents_rlo(self):
        with Sahte() as s:
            rc, o, _ = self.kos(s.yaz('AGENTS.md', 'Merhaba ' + RLO + 'gizli\n'))
            self.assertEqual(rc, 1, o); self.assertIn('U+202E', o); self.assertIn('AGENTS.md', o); self.assertIn('SONUC: KIRMIZI', o)

    def test_negatif_kod_scripts_github_claude_sifir_genislik(self):
        for yol in ('scripts/a.ps1', 'mcp/a.py', '.github/workflows/denetim.yml', 'CLAUDE.md', 'llms.txt', 'patches/sdcpp/01.patch'):
            with Sahte() as s:
                rc, o, _ = self.kos(s.yaz(yol, 'x' + ZWSP + 'y\n'))
                self.assertEqual(rc, 1, yol + ' ' + o); self.assertIn('U+200B', o)

    def test_negatif_ingilizce_readme_zwnj_ve_lrm(self):
        for ch, kod in ((ZWNJ, 'U+200C'), (LRM, 'U+200E')):
            with Sahte() as s:
                rc, o, _ = self.kos(s.yaz('README.md', 'a' + ch + 'b\n'))
                self.assertEqual(rc, 1, o); self.assertIn(kod, o)

    def test_negatif_lrm_rtl_olmayan_dilde(self):
        with Sahte() as s:
            rc, o, _ = self.kos(s.yaz('README.fr.md', 'a' + LRM + 'b\n'))
            self.assertEqual(rc, 1, o)

    def test_negatif_rlo_rtl_readme_de_bile(self):
        with Sahte() as s:
            rc, o, _ = self.kos(s.yaz('README.fa.md', 'a' + ZWNJ + LRM + 'b' + RLO + 'c\n'))
            self.assertEqual(rc, 1, o); self.assertIn('U+202E', o); self.assertNotIn('U+200C', o); self.assertNotIn('U+200E', o)

    def test_negatif_baska_klasorde_readme_dil_muaf_degil(self):
        with Sahte() as s:   # yalniz KOKTEKI README.<dil>.md muaf; docs/ ya da ic klasor degil
            rc, o, _ = self.kos(s.yaz('docs/README.fa.md', 'a' + ZWNJ + 'b\n'))
            self.assertEqual(rc, 1, o)

    def test_negatif_bom_ortada(self):
        with Sahte() as s:
            rc, o, _ = self.kos(s.yaz('scripts/a.ps1', 'x\ufeffy\n'))
            self.assertEqual(rc, 1, o); self.assertIn('U+FEFF', o)

    def test_pozitif_rtl_ve_hint_readme_izinli(self):
        with Sahte() as s:
            s.yaz('README.fa.md', 'a' + ZWNJ + 'b' + LRM + 'c\n').yaz('README.ar.md', 'a' + LRM + 'b\n').yaz('README.bn.md', 'a' + ZWJ + 'b\n')
            rc, o, _ = self.kos(s)
            self.assertEqual(rc, 0, o); self.assertIn('SONUC: GECTI', o)

    def test_pozitif_basta_bom(self):
        with Sahte() as s:
            rc, o, _ = self.kos(s.yaz('scripts/a.ps1', b'\xef\xbb\xbfWrite-Host 1\n'))
            self.assertEqual(rc, 0, o)

    def test_pozitif_gercek_readme_ler(self):
        """Bugunku 29 README (fa/ar/he/ur/bn dahil) tek basina GECER."""
        with Sahte() as s:
            n = 0
            for f in sorted(os.listdir(KOK)):
                if f.startswith('README') and f.endswith('.md'):
                    shutil.copy(os.path.join(KOK, f), os.path.join(s.kok, f)); n += 1
            self.assertGreaterEqual(n, 1)
            rc, o, _ = self.kos(s)
            self.assertEqual(rc, 0, o)

    def test_ibranice_dosya_adi_ve_cp1254_cokmez(self):
        with Sahte() as s:   # `python -I` PYTHONIOENCODING'i yok sayar: cikti kodlamasi betigin kendi reconfigure'una bagli
            s.yaz('אבג/א.md', 'a' + RLO + 'b\n')
            rc, o, e = self.kos(s)
            self.assertEqual(rc, 1, o + e); self.assertNotIn('Traceback', e); self.assertIn('SONUC: KIRMIZI', o)


class Kontrol(unittest.TestCase):
    def kos(self, s):
        return calistir('--hizli', '--kapi', 'kontrol', kok=s.kok)

    def test_negatif_yeni_dosyada_nul(self):
        with Sahte() as s:
            rc, o, _ = self.kos(s.yaz('scripts/a.py', b'x = 1\x00\n'))
            self.assertEqual(rc, 1, o); self.assertIn('NUL', o)

    def test_negatif_kayitsiz_yamada_nul(self):
        with Sahte() as s:
            rc, o, _ = self.kos(s.yaz('patches/ggml/99-baska.patch', b'+ a\x00b\n').yaz('docs/YAMALAR.md', YAMALAR))
            self.assertEqual(rc, 1, o)

    def test_negatif_kayitli_yamada_fazla_nul(self):
        with Sahte() as s:
            rc, o, _ = self.kos(s.yaz(YAMA, b'+ a\x00b\x00\n').yaz('docs/YAMALAR.md', YAMALAR))
            self.assertEqual(rc, 1, o); self.assertIn('kayitli istisna 1', o)

    def test_negatif_kayitli_yama_belgesiz(self):
        with Sahte() as s:
            rc, o, _ = self.kos(s.yaz(YAMA, b'+ a\x00b\n').yaz('docs/YAMALAR.md', 'bos\n'))
            self.assertEqual(rc, 1, o); self.assertIn('belgelemiyor', o)

    def test_negatif_geri_silme_kazasi(self):
        with Sahte() as s:   # gecmiste dosyaya `\b` kacti: engine\bin -> engine<BS>in
            rc, o, _ = self.kos(s.yaz('docs/a.md', b'engine\x08in_sm120\n'))
            self.assertEqual(rc, 1, o); self.assertIn('0x08', o)

    def test_negatif_esc(self):
        with Sahte() as s:
            rc, o, _ = self.kos(s.yaz('scripts/a.ps1', b'x\x1b[31m\n'))
            self.assertEqual(rc, 1, o)

    def test_pozitif_kayitli_yama_tam_sayi_ve_belge(self):
        with Sahte() as s:
            rc, o, _ = self.kos(s.yaz(YAMA, b'+ a\x00b\n').yaz('docs/YAMALAR.md', YAMALAR))
            self.assertEqual(rc, 0, o)

    def test_pozitif_ikili_uzanti_atlanir_ve_crlf_tab_serbest(self):
        with Sahte() as s:
            rc, o, _ = self.kos(s.yaz('a.png', b'\x89PNG\x00\x01\x02').yaz('a.md', b'a\tb\r\nc\n'))
            self.assertEqual(rc, 0, o)


class Sozdizimi(unittest.TestCase):
    def test_negatif_bozuk_python_ve_json(self):
        with Sahte() as s:
            s.yaz('scripts/a.py', 'def x(:\n').yaz('scripts/m.json', '{"a": }')
            rc, o, _ = calistir('--hizli', '--kapi', 'sozdizimi', kok=s.kok)
            self.assertEqual(rc, 1, o); self.assertIn('a.py', o); self.assertIn('m.json', o)

    def test_pozitif_temiz(self):
        with Sahte() as s:
            s.yaz('scripts/a.py', 'x = 1\n').yaz('scripts/m.json', '{"a": 1}')
            rc, o, _ = calistir('--hizli', '--kapi', 'sozdizimi', kok=s.kok)
            self.assertEqual(rc, 0, o)


class GuvenlikMd(unittest.TestCase):
    def kos(self, metin):
        with Sahte() as s:
            if metin is not None:
                s.yaz('SECURITY.md', metin)
            return calistir('--hizli', '--kapi', 'guvenlik_md', kok=s.kok)

    def test_pozitif(self):
        rc, o, _ = self.kos(TEMIZ_GUVENLIK); self.assertEqual(rc, 0, o)

    def test_negatif_dosya_yok(self):
        rc, o, _ = self.kos(None); self.assertEqual(rc, 1, o)

    def test_negatif_gizli_bildirim_yok(self):
        rc, o, _ = self.kos(TEMIZ_GUVENLIK.replace('Report a vulnerability', 'Mail us')); self.assertEqual(rc, 1, o); self.assertIn('Report a vulnerability', o)

    def test_negatif_taahhut_dili(self):
        m = TEMIZ_GUVENLIK + '\nWe always answer within 7 days.\n'   # "target" olmadan = soz gibi okunur
        rc, o, _ = self.kos(m); self.assertEqual(rc, 1, o); self.assertIn('taahhut gibi', o)
        rc, o, _ = self.kos(TEMIZ_GUVENLIK + '\n\n\n\n' + 'x' * 200 + '\nHer zaman 7 gün içinde yanıtlarız.\n'); self.assertEqual(rc, 1, o)

    def test_negatif_hedef_ibaresi_yok(self):
        rc, o, _ = self.kos(TEMIZ_GUVENLIK.replace('target', 'plan')); self.assertEqual(rc, 1, o)

    def test_negatif_enjeksiyon_ve_mcp_yok(self):
        rc, o, _ = self.kos(TEMIZ_GUVENLIK.replace('prompt injection', 'x').replace('MCP', 'Y')); self.assertEqual(rc, 1, o)
        self.assertIn('prompt-injection', o); self.assertIn('MCP', o)


class Cekirdek(unittest.TestCase):
    def test_kok_yok_cikis_3(self):
        rc, o, _ = calistir('--hizli', kok=os.path.join(tempfile.gettempdir(), 'yok_denetim_klasoru_xyz'))
        self.assertEqual(rc, 3, o); self.assertIn('SONUC: GIRDI HATALI (3)', o)

    def test_bilinmeyen_kapi_ve_gecersiz_bayrak_cikis_3(self):
        with Sahte() as s:
            rc, o, _ = calistir('--kapi', 'yok', kok=s.kok); self.assertEqual(rc, 3, o)
            rc, o, _ = calistir('--bilinmeyen-bayrak', kok=s.kok); self.assertEqual(rc, 3, o); self.assertIn('SONUC:', o)

    def test_kapali_hata_coken_kapi_yesil_degil(self):
        """Bir kapi coker ise (OSError/ValueError vb.) sonuc CALISMADI (6), asla GECTI degil."""
        import importlib.util
        spec = importlib.util.spec_from_file_location('denetim_modulu', DENETIM)
        m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
        def coker(c): raise RuntimeError('kasitli coken kapi')
        m.KAPILAR['unicode'] = (coker,) + m.KAPILAR['unicode'][1:]
        import io, contextlib
        with Sahte() as s, contextlib.redirect_stdout(io.StringIO()) as buf:
            kod = m.main(['--hizli', '--kapi', 'unicode', '--kapi', 'kontrol', '--kok', s.kok])
        cikti = buf.getvalue()
        self.assertEqual(kod, 6, cikti); self.assertIn('SONUC: CALISMADI', cikti); self.assertNotIn('SONUC: GECTI', cikti)

    def test_kirmizi_ve_coken_birlikte_kirmizi_1(self):
        import importlib.util, io, contextlib
        spec = importlib.util.spec_from_file_location('denetim_modulu2', DENETIM)
        m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
        def coker(c): raise RuntimeError('x')
        m.KAPILAR['sozdizimi'] = (coker,) + m.KAPILAR['sozdizimi'][1:]
        with Sahte() as s, contextlib.redirect_stdout(io.StringIO()) as buf:
            s.yaz('AGENTS.md', 'a' + RLO + 'b\n')
            kod = m.main(['--kapi', 'unicode', '--kapi', 'sozdizimi', '--kok', s.kok])
        self.assertEqual(kod, 1, buf.getvalue())

    def test_json_gecerli_tek_sonuc_satiri_kisisel_yol_yok(self):
        with Sahte() as s:
            s.yaz('AGENTS.md', 'a' + RLO + 'b\n')
            rc, o, e = calistir('--hizli', '--json', '--kapi', 'unicode', kok=s.kok)
            d = json.loads(o)
            self.assertEqual((rc, d['cikis'], d['sonuc']), (1, 1, 'KIRMIZI (1)'))
            self.assertEqual(d['kok'], '<ROOT>'); self.assertNotIn(s.kok, o + e)
            self.assertEqual(sum(1 for l in e.splitlines() if l.startswith('SONUC:')), 1)
            self.assertEqual(sum(1 for l in o.splitlines() if l.startswith('SONUC:')), 0)
        with Sahte() as s:
            rc, o, e = calistir('--hizli', '--kapi', 'unicode', kok=s.kok)
            self.assertEqual(rc, 0, o); self.assertEqual(sum(1 for l in o.splitlines() if l.startswith('SONUC:')), 1)
            self.assertEqual(o.strip().splitlines()[-1], 'SONUC: GECTI')

    def test_kisisel_yol_cikti_yok(self):
        with Sahte() as s:
            rc, o, e = calistir('--hizli', kok=s.kok); self.assertEqual(rc, 1); self.assertNotIn(s.kok, o + e)


class BugunkuRepo(unittest.TestCase):
    """POZITIF: bugunku repo tum kapilardan GECER ve 10 sn tavanini asmaz."""
    def test_pozitif_gercek_repo_hizli(self):
        t0 = time.time()
        rc, o, e = calistir('--hizli', kok=KOK)
        sure = time.time() - t0
        self.assertEqual(rc, 0, o + e); self.assertEqual(o.strip().splitlines()[-1], 'SONUC: GECTI')
        self.assertLessEqual(sure, 10, 'sure %.1f sn' % sure)


if __name__ == '__main__':
    siniflar = (Unicode, Kontrol, Sozdizimi, GuvenlikMd, Cekirdek, BugunkuRepo)
    suite = unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromTestCase(k) for k in siniflar)
    r = unittest.TextTestRunner(verbosity=1, stream=sys.stderr).run(suite)
    n = r.testsRun; ok = n - len(r.failures) - len(r.errors)
    print('TEST_DENETIM: %d/%d %s' % (ok, n, 'GECTI' if ok == n else 'KIRIK'))
    sys.exit(0 if ok == n else 1)
