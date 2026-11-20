"""VT_KURU_SAHTE incelemesi (toplanti karari 6): sahte olcum anahtari YALNIZ `kur.ps1 -Kuru`'da etkin mi, kullaniciya gorunur mu, zarar yolu var mi.

  python -I tests/denetim/test_kuru_sahte.py     -> son satir: TEST_KURU_SAHTE: N/N GECTI (cikis 0)

Her kosu gecici bir VT_ROOT'ta (depoya ve gercek kurulum klasorune yazmaz); `-Adim kontrol0` disinda adim calismaz (indirme yok). Ag yok, GPU yok.
Ayirt edici sahte degerler (7777) kullanilir: gercek makinede bu sayilar gorunemez, gorunurse sahte deger sizmis demektir.
PowerShell yoksa test atlanir.
"""
import os, shutil, subprocess, sys, tempfile, unittest

KOK = os.environ.get('DENETIM_TEST_KOK') or os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
KUR = os.path.join(KOK, 'scripts', 'kur.ps1')
PS = shutil.which('powershell') or shutil.which('pwsh')
SAHTE = 'ram=7777;bos_ram=7777;disk=7777;vc=yok;python=yok;gpu=yok;vram=7777;cc=9.9'


def kos(*arg, sahte=None):
    with tempfile.TemporaryDirectory(prefix='kurusahte_') as td:
        env = dict(os.environ, VT_ROOT=td)
        env.pop('VT_KURU_SAHTE', None)
        if sahte is not None:
            env['VT_KURU_SAHTE'] = sahte
        p = subprocess.run([PS, '-NoProfile', '-NonInteractive', '-ExecutionPolicy', 'Bypass', '-File', KUR, '-Adim', 'kontrol0'] + list(arg),
                           capture_output=True, env=env, timeout=120, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        yazilan = sorted(os.listdir(td))
    return p.returncode, p.stdout.decode('utf-8', 'replace'), yazilan


@unittest.skipIf(PS is None or not os.path.isfile(KUR), 'PowerShell ya da kur.ps1 yok')
class KuruSahte(unittest.TestCase):
    def test_kuru_ile_etkin_ve_gorunur(self):
        rc, o, yazilan = kos('-Kuru', sahte=SAHTE)
        self.assertIn('SAHTE OLCUM', o)            # kullaniciya gorunur: rapor basinda uyari
        self.assertIn('7777', o)                    # deger gercekten kullanildi
        self.assertEqual(yazilan, [], 'Kuru kok klasorune dosya yazdi: %s' % yazilan)

    def test_kuru_olmadan_yok_sayilir(self):
        rc, o, _ = kos(sahte=SAHTE)
        self.assertNotIn('SAHTE OLCUM', o)
        self.assertNotIn('7777', o, 'sahte deger gercek kosuya sizdi')
        self.assertNotIn('9.9', o)

    def test_kuru_olmadan_gercek_hata_sahteyle_gizlenmez(self):
        # sahte disk=7777 gercek kosuda gecerli olsaydi disk HATA'si kaybolurdu. Gercek ve sahte kosu ayni disk/RAM satirini vermeli.
        _, gercek, _ = kos()
        _, sahteli, _ = kos(sahte=SAHTE)
        import re
        sat = lambda t: [re.sub(r'bos \d+[.,]\d+ GB', 'bos N GB', re.sub(r'kurusahte_\w+', 'K', l)) for l in t.splitlines() if ('GiB' in l or 'RAM' in l or 'HATA' in l or 'bos' in l.lower())]
        self.assertEqual(sat(gercek), sat(sahteli))

    def test_kuru_olmadan_ortam_degiskeni_kurulumu_degistirmez(self):
        rc1, _, _ = kos()
        rc2, _, _ = kos(sahte=SAHTE)
        self.assertEqual(rc1, rc2)

    def test_kuru_sahtesiz_banner_yok(self):
        rc, o, _ = kos('-Kuru')
        self.assertNotIn('SAHTE OLCUM', o)
        self.assertNotIn('7777', o)

    def test_bozuk_sahte_deger_guvenli_hata(self):
        # sayi olmayan deger: rapor cokebilir ama yan etki (dosya yazma, indirme) olmaz
        rc, o, yazilan = kos('-Kuru', sahte='disk=abc;ram=xyz')
        self.assertEqual(yazilan, [])


if __name__ == '__main__':
    r = unittest.TextTestRunner(verbosity=0, stream=sys.stderr).run(unittest.defaultTestLoader.loadTestsFromTestCase(KuruSahte))
    n = r.testsRun
    print('TEST_KURU_SAHTE: %d/%d %s' % (n - len(r.failures) - len(r.errors), n, 'GECTI' if r.wasSuccessful() else 'KIRIK'))
    sys.exit(0 if r.wasSuccessful() else 1)
