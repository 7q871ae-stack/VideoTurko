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


KARSILAMA = 'karsilama.yml'   # PR'a yorum icin ayricalikli tetik kullanan TEK is akisi; kurallari KarsilamaIsAkisi sinifinda


def genel_akislar():
    return [y for y in is_akislari() if os.path.basename(y) != KARSILAMA]


def karsilama_ihlalleri(metin):
    """karsilama.yml'nin guvenlik kosullari; ihlal listesi (bos = temiz). Yorum satirlari sayilmaz."""
    ih = []
    metin = metin.replace('\r\n', '\n')
    satirlar = komut_satirlari(metin)
    govde = '\n'.join(satirlar)
    # tetikler: yalniz issues ve pull_request_target, ikisi de yalniz types: [opened]
    m = re.search(r'(?m)^on:\s*\n((?:[ \t]+.*\n?|\n)+)', govde)
    tetikler = re.findall(r'(?m)^  ([A-Za-z_]+):\s*$', m.group(1)) if m else []
    if sorted(tetikler) != ['issues', 'pull_request_target']:
        ih.append('tetikler yalniz issues ve pull_request_target olmali: %s' % tetikler)
    if len(re.findall(r'(?m)^    types:\s*\[opened\]\s*$', govde)) != 2:
        ih.append('her tetik yalniz types: [opened] olmali')
    # izinler: tam olarak bu uc satir
    m = re.search(r'(?m)^permissions:\s*\n((?:[ \t]+\S.*\n?)+)', govde)
    izin = dict(re.findall(r'(?m)^\s+([\w-]+):\s*(\S+)\s*$', m.group(1))) if m else {}
    if izin != {'contents': 'read', 'issues': 'write', 'pull-requests': 'write'}:
        ih.append('permissions en dar degil: %s' % izin)
    if re.search(r'(?i)write-all|read-all', govde):
        ih.append('write-all/read-all')
    # PR kodu getirilmez: checkout'ta ref/repository/token/path yok, kimlik bilgisi diske yazilmaz
    if re.search(r'(?m)^\s*(ref|repository|token|path|submodules)\s*:', govde):
        ih.append('checkout ref/repository/token/path/submodules verilmis (PR kodu getirilebilir)')
    if not re.search(r'(?m)^\s*persist-credentials:\s*false\s*$', govde):
        ih.append('persist-credentials: false yok')
    if re.search(r'(?i)github\.event|github\.head_ref|head\.sha|head\.ref|pull_request\.head|github-script', govde):
        ih.append('olay/PR-head ifadesi ya da github-script')
    # ifade olarak yalniz secrets.GITHUB_TOKEN, o da yalniz GH_TOKEN env'inde; run satirinda ifade yok
    for satir in satirlar:
        for ifade in re.findall(r'\$\{\{\s*(.*?)\s*\}\}', satir):
            if ifade != 'secrets.GITHUB_TOKEN' or not re.match(r'\s*GH_TOKEN:', satir):
                ih.append('izinli olmayan ifade: %s' % ifade)
    kullanimlar = re.findall(r'(?m)^\s*-?\s*uses:\s*(\S+)', govde)
    if not kullanimlar:
        ih.append('uses yok')
    for u in kullanimlar:
        if not re.match(r'^[\w.-]+/[\w./-]+@[0-9a-f]{40}$', u):
            ih.append('SHA ile sabit degil: %s' % u)
    for satir in satirlar:
        if re.search(r'\buses:\s*\S+@[0-9a-f]{40}', satir) and not re.search(r'#\s*v\d', satir):
            ih.append('surum yorumu yok: %s' % satir.strip())
    if re.search(r'(?m)body=(?!@)', govde):
        ih.append('yorum govdesi dosyadan (@) verilmeli')
    if not re.search(r'(?m)^\s*gh api -X POST "repos/\$GITHUB_REPOSITORY/issues/\$N/comments" -F "body=@', govde):
        ih.append('yorum gh api ile, govde dosyadan atilmali')
    if 'karsilama.py --yorumlar' not in govde:
        ih.append('ikinci kez yazmama adimi (--yorumlar) yok')
    if re.search(r'(?i)\b(cu' + r'rl|w' + r'get|Invoke-Web' + r'Request|self-hosted)\b', govde):
        ih.append('curl/wget/self-hosted')
    if re.search(r'secrets\.(?!GITHUB_TOKEN)', govde):
        ih.append('baska gizli degisken')
    return ih


class IsAkisiKurallari(unittest.TestCase):
    def test_en_az_bir_is_akisi_var(self):
        self.assertTrue(is_akislari(), '.github/workflows altinda denetim is akisi yok')

    def test_ayricalikli_tetik_yok(self):
        yasak = re.compile(r'\b(pull_request_' + r'target|workflow_' + r'run|issue_comment|issues|discussion|repository_dispatch)\b')
        for y in genel_akislar():   # karsilama.yml ayri sinifta, dar kosullarla
            for s in komut_satirlari(oku(y)):
                self.assertIsNone(yasak.search(s), '%s: ayricalikli/yorum tetigi: %s' % (os.path.basename(y), s.strip()))
        # karsilama.yml'de de yalniz issues + pull_request_target izinli; digerleri yasak
        yasak2 = re.compile(r'\b(workflow_' + r'run|issue_comment|discussion|repository_dispatch|workflow_dispatch)\b')
        for y in is_akislari():
            for s in komut_satirlari(oku(y)):
                self.assertIsNone(yasak2.search(s), '%s: yasak tetik: %s' % (os.path.basename(y), s.strip()))

    def test_tetik_pull_request_ve_main_push(self):
        for y in genel_akislar():
            m = oku(y)
            self.assertRegex(m, r'(?m)^on:\s*\n\s+pull_request:')
            self.assertRegex(m, r'(?m)^\s+push:\s*\n\s+branches:\s*\[main\]')

    def test_izin_yalniz_okuma(self):
        for y in genel_akislar():
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


class KarsilamaIsAkisi(unittest.TestCase):
    """karsilama.yml: ayricalikli tetik YALNIZ burada ve YALNIZ su kosullarla (taban dal checkout'u, dar izin, ifade yok, SHA'li eylem)."""
    def test_dosya_var_ve_temiz(self):
        self.assertTrue(os.path.isfile(os.path.join(WF, KARSILAMA)), KARSILAMA + ' yok')
        self.assertEqual(karsilama_ihlalleri(oku('.github', 'workflows', KARSILAMA)), [])

    def test_ayricalikli_tetik_baska_dosyada_yok(self):
        # denetim.yml dahil karsilama disindaki her akis hala yasakli
        for y in genel_akislar():
            self.assertNotRegex('\n'.join(komut_satirlari(oku(y))), r'pull_request_' + r'target')

    def test_kural_kotu_ornekleri_yakalar(self):
        iyi = oku('.github', 'workflows', KARSILAMA).replace('\r\n', '\n')   # autocrlf=true klonunda CRLF gelir; ornekler LF uzerinden uretilir
        sha = '3d3c42e5aac5ba805825da76410c181273ba90b1'
        kimlik = '          persist-credentials: false'
        kotu = {
            'head ref checkout': iyi.replace(kimlik, '          ref: ${{ github.event.pull_request.head.sha }}\n' + kimlik),
            'ref (ifadesiz)': iyi.replace(kimlik, '          ref: refs/pull/1/merge\n' + kimlik),
            'repository (fork)': iyi.replace(kimlik, '          repository: baska/fork\n' + kimlik),
            'kimlik diske yazilir': iyi.replace('persist-credentials: false', 'persist-credentials: true'),
            'fazla izin': iyi.replace('  pull-requests: write\n', '  pull-requests: write\n  actions: write\n'),
            'contents write': iyi.replace('  contents: read\n', '  contents: write\n'),
            'write-all': iyi.replace('permissions:\n  contents: read\n  issues: write\n  pull-requests: write\n', 'permissions: write-all\n'),
            'fazla tetik': iyi.replace('  pull_request_target:\n', '  issue_comment:\n    types: [opened]\n  pull_request_target:\n'),
            'tum turler': iyi.replace('types: [opened]', 'types: [opened, synchronize]', 1),
            'run icinde olay': iyi.replace('          set -eu\n', '          set -eu\n          echo "${{ github.event.pull_request.title }}"\n'),
            'run icinde baska ifade': iyi.replace('          set -eu\n', '          set -eu\n          echo "${{ github.repository }}"\n'),
            'sabitlenmemis eylem': iyi.replace('@' + sha + ' # v7.0.1', '@v7'),
            'surum yorumu yok': iyi.replace(' # v7.0.1', ''),
            'govde komut satirinda': iyi.replace('-F "body=@$RUNNER_TEMP/govde.md"', '-F "body=$GOVDE"'),
            'ikinci kez adimi yok': iyi.replace('--yorumlar', '--olay-yok'),
            'baska gizli degisken': iyi.replace('secrets.GITHUB_TOKEN', 'secrets.BASKA_ANAHTAR'),
            'github-script': iyi.replace('uses: actions/checkout@' + sha, 'uses: actions/github-script@' + sha),
        }
        for ad, metin in kotu.items():
            self.assertNotEqual(metin, iyi, 'ornek uretilemedi: ' + ad)
            self.assertTrue(karsilama_ihlalleri(metin), 'kapi bu kotu ornegi yakalamadi: ' + ad)


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
