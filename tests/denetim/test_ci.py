"""CI is-akisi (KL-09) ve satir sonu kurali icin statik testler. Stdlib; ag yok. Dosya ASCII; yasak sozcukler parcalanir.

Yakalanan: ayricalikli tetikleyici, yazma izni, SHA'ya sabitlenmemis eylem, olay metninin kabuga girmesi,
dependabot'ta eylem kaydi yok, SHA256SUMS'in CRLF'e cevrilmesine izin veren .gitattributes.
"""
import os
import re
import unittest

KOK = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WF = os.path.join(KOK, '.github', 'workflows')


def oku(*parca):
    with open(os.path.join(KOK, *parca), 'rb') as f:
        return f.read().decode('utf-8')


def is_akislari():
    if not os.path.isdir(WF):
        return []
    return sorted(os.path.join(WF, a) for a in os.listdir(WF) if a.endswith(('.yml', '.yaml')))


def komut_satirlari(metin):
    """Yorum olmayan satirlar."""
    return [s for s in metin.splitlines() if not s.lstrip().startswith('#')]


class IsAkisiKurallari(unittest.TestCase):
    def test_en_az_bir_is_akisi_var(self):
        self.assertTrue(is_akislari(), '.github/workflows altinda denetim is akisi yok')

    def test_ayricalikli_tetik_yok(self):
        yasak = re.compile(r'\b(pull_request_' + r'target|workflow_' + r'run|issue_comment|issues|discussion|repository_dispatch)\b')
        for y in is_akislari():
            for s in komut_satirlari(oku(y)):
                self.assertIsNone(yasak.search(s), '%s: ayricalikli/yorum tetigi: %s' % (os.path.basename(y), s.strip()))

    def test_tetik_pull_request_ve_main_push(self):
        for y in is_akislari():
            m = oku(y)
            self.assertRegex(m, r'(?m)^on:\s*\n\s+pull_request:')
            self.assertRegex(m, r'(?m)^\s+push:\s*\n\s+branches:\s*\[main\]')

    def test_izin_yalniz_okuma(self):
        for y in is_akislari():
            m = oku(y)
            self.assertRegex(m, r'(?m)^permissions:\s*\n\s+contents:\s*read\s*$', y)
            self.assertNotRegex('\n'.join(komut_satirlari(m)), r'(?i):\s*write\b|write-all')

    def test_eylemler_tam_sha(self):
        for y in is_akislari():
            kullanimlar = re.findall(r'(?m)^\s*-?\s*uses:\s*(\S+)', '\n'.join(komut_satirlari(oku(y))))
            self.assertTrue(kullanimlar)
            for u in kullanimlar:
                self.assertRegex(u, r'^[\w.-]+/[\w./-]+@[0-9a-f]{40}$', '%s: SHA ile sabit degil: %s' % (os.path.basename(y), u))

    def test_surum_yorumu_var(self):
        for y in is_akislari():
            for s in komut_satirlari(oku(y)):
                if re.search(r'\buses:\s*\S+@[0-9a-f]{40}', s):
                    self.assertRegex(s, r'#\s*v\d', 'SHA yaninda surum yorumu yok: ' + s.strip())

    def test_olay_metni_kabuga_girmez(self):
        # `run` bloklarinda olay nesnesi/dal adi ifadesi olmaz; env ile bile PR basligi/govdesi dogrudan verilmez (olay JSON'u okunur)
        yasak = re.compile(r'\$\{\{[^}]*(github\.event\.|github\.head_ref|github\[|toJSON)')
        for y in is_akislari():
            for s in komut_satirlari(oku(y)):
                self.assertIsNone(yasak.search(s), '%s: olay metni ifadeye gomulu: %s' % (os.path.basename(y), s.strip()))

    def test_gizli_degisken_ve_ag_yok(self):
        for y in is_akislari():
            m = '\n'.join(komut_satirlari(oku(y)))
            self.assertNotRegex(m, r'secrets\.(?!GITHUB_TOKEN)')
            self.assertNotRegex(m, r'(?i)\b(cu' + r'rl|w' + r'get|Invoke-Web' + r'Request)\b')
            self.assertNotRegex(m, r'(?i)self-hosted')

    def test_pr_kapisi_tabandan_kosar(self):
        m = oku('.github', 'workflows', 'denetim.yml')
        self.assertIn('git worktree add', m)
        self.assertRegex(m, r'python -I "\$TABAN_KOK/scripts/pr_kapi\.py"')

    def test_negatif_kural_kendini_yakalar(self):
        # kural gevsek mi diye: kotu ornekler tek tek yakalanmali
        sha = re.compile(r'^[\w.-]+/[\w./-]+@[0-9a-f]{40}$')
        self.assertIsNone(sha.match('actions/checkout@v4'))
        self.assertIsNone(sha.match('actions/checkout@' + 'a' * 39))
        self.assertIsNotNone(sha.match('actions/checkout@' + 'a' * 40))


class DependabotVeSatirSonu(unittest.TestCase):
    def test_dependabot_eylemleri_izler(self):
        m = oku('.github', 'dependabot.yml')
        self.assertRegex(m, r'(?m)^\s*-\s*package-ecosystem:\s*"github-actions"')
        self.assertRegex(m, r'(?m)^version:\s*2')

    def test_sha256sums_lf_kurali(self):
        # Windows'ta core.autocrlf=true taze klon tabloyu CRLF yapar, `sha256sum -c` dosya adinda CR gorup 24 yamayi okuyamaz
        # (olculdu, KL-09). Kural .gitattributes'ta olmali.
        m = oku('.gitattributes')
        self.assertRegex(m, r'(?m)^patches/SHA256SUMS\s+text\s+eol=lf\s*$')

    def test_yamalar_metin_donusumu_gormez(self):
        self.assertRegex(oku('.gitattributes'), r'(?m)^\*\.patch\s+-text\s*$')


if __name__ == '__main__':
    unittest.main()
