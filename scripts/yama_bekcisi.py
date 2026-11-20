"""VideoTurko yama bekcisi (KL-05): patches/ klasorunu bayt duzeyinde korur. denetim.py'nin `yama` alt kapisi.

Kapi (denetim.py --kapi yama; ag yok, dosya yazmaz):
  1. CR yok: hicbir .patch dosyasinda 0x0D bayti olmaz (CRLF yamayi bozar: `git apply` satir sonunu eslestiremez; .gitattributes `*.patch -text`).
  2. SERIES.txt: listelenen her yama var, her yama listede, grup icinde NN- onekleri artan, yinelenen yok.
  3. Hash tablosu `patches/SHA256SUMS` (sha256sum -c uyumlu): her yamanin SHA-256'si tabloyla BIREBIR; tabloda olmayan yama / dosyasi olmayan satir = KIRMIZI.
  4. Yama yapisi: `diff --git` var, hedef yol `..`/mutlak/surucu harfi icermez.
  5. Satir sonu kurali .gitattributes'tan OKUNUR (sabit yazilmaz): `eol=lf` dosyada CR yok; `eol=crlf` dosyada her LF'den once CR var (kur.cmd/uret.cmd).
Yerelde, elle (hizli kapi DEGIL, CI'da reddedilir): `--uygula-kontrol --sdcpp DIR --ggml DIR` yamalari kaynak agacina SIRAYLA `git apply --check` ile dener
(gecici indeks kullanir: calisma agacina ve depoya yazmaz). `--tablo-yaz` tabloyu yeniden yazar (bilincli yama degisikliginden sonra, insan karariyla).

NEDEN: yama baytlari derlenen motorun ta kendisidir; tek bayt degisirse bayt-ayni kaniti gecersizdir ve sessiz bir arka kapi yama icine girebilir.
BEDEL: yama bilerek degisince tablo da degismeli (bir komut + gerekce). SINIR: tablo yamayla AYNI depoda durur; ayni PR ikisini birlikte degistirirse kapi
yesil verir: gercek koruma, `patches/` degisen her PR'in `pr_kapi.py`de SARI (korumali yol) olup insan gozuyle okunmasidir. Bu betik "kazayi yakalar", "korur" demez.
GEVSETME: hicbiri; yeni yama = yeni tablo satiri + SERIES satiri (tek komut).
"""
import re, os, sys, hashlib, fnmatch, subprocess, tempfile, argparse

TABLO = 'patches/SHA256SUMS'
SERI = 'patches/SERIES.txt'
SATIR_TABLO = re.compile(r'^([0-9a-f]{64}) [ *](\S.*)$')
HEDEF = re.compile(r'^(?:diff --git a/(\S+) b/(\S+)|\+\+\+ b/(\S+)|--- a/(\S+))', re.M)


def yamalar(c):
    return [f for f in c.dosyalar if f.startswith('patches/') and f.endswith('.patch')]


def sha(b):
    return hashlib.sha256(b).hexdigest()


def tablo_oku(c):
    """-> (sozluk yol->sha, bulgu listesi) ; tablo yoksa (None, [bulgu])."""
    if TABLO not in c.dosyalar:
        return None, ['%s yok (yama hash tablosu): `python -I scripts/yama_bekcisi.py --tablo-yaz` ile uretilir, gerekce yazilir' % TABLO]
    d, b = {}, []
    for no, s in enumerate(c.bayt(TABLO).decode('utf-8', 'replace').splitlines(), 1):
        if not s.strip() or s.lstrip().startswith('#'):
            continue
        m = SATIR_TABLO.match(s)
        if not m:
            b.append('%s:%d satir bicimi bozuk (beklenen: <64 hex>  <yol>)' % (TABLO, no))
        elif m.group(2) in d:
            b.append('%s:%d yinelenen satir: %s' % (TABLO, no, m.group(2)))
        else:
            d[m.group(2)] = m.group(1)
    return d, b


def seri_oku(c):
    if SERI not in c.dosyalar:
        return None
    return [s.strip() for s in c.bayt(SERI).decode('utf-8', 'replace').splitlines() if s.strip() and not s.strip().startswith('#')]


def eol_kurallari(c):
    """.gitattributes -> [(desen, 'lf'|'crlf'|None)] sirayla; son eslesen kazanir. `-text`/`binary` = kontrol yok (None)."""
    if '.gitattributes' not in c.dosyalar:
        return []
    out = []
    for s in c.bayt('.gitattributes').decode('utf-8', 'replace').splitlines():
        p = s.split('#', 1)[0].split()
        if len(p) < 2:
            continue
        ozel = ' '.join(p[1:])
        m = re.search(r'\beol=(lf|crlf)\b', ozel)
        if m:
            out.append((p[0], m.group(1)))
        elif re.search(r'(^|\s)(-text|binary|-crlf)(\s|$)', ozel):
            out.append((p[0], None))
    return out


def _desen_uyar(desen, rel):
    d = desen.lstrip('/')
    return fnmatch.fnmatchcase(rel, d) if '/' in d else fnmatch.fnmatchcase(rel.rsplit('/', 1)[-1], d)


def _git_eol(c):
    """`git ls-files --eol`: {yol: (indeks_eol, calisma_eol)}; git/depo yoksa bos (bayt kontrolu yedek kalir)."""
    if not os.path.isdir(os.path.join(c.kok, '.git')):
        return {}
    try:
        p = subprocess.run(['git', '-C', c.kok, 'ls-files', '--eol', '--cached', '--others', '--exclude-standard'], capture_output=True, timeout=20,
                           creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    except (OSError, subprocess.SubprocessError):
        return {}
    out = {}
    if p.returncode == 0:
        for s in p.stdout.decode('utf-8', 'replace').splitlines():
            m = re.match(r'i/(\S*)\s+w/(\S*)\s+attr/[^\t]*\t(.*)$', s)
            if m:
                out[m.group(3)] = (m.group(1), m.group(2))
    return out


def kapi_yama(c):
    bulgu, bilgi = [], []
    ym = yamalar(c)
    # 1 + 4: CR yok, yapi
    for rel in ym:
        b = c.bayt(rel)
        cr = b.count(b'\r')
        if cr:
            bulgu.append('%s:%d CR bayti (CRLF yamayi bozar; LF ile yeniden yazin) x%d' % (rel, b.count(b'\n', 0, b.index(b'\r')) + 1, cr))
        t = b.decode('utf-8', 'replace')
        if 'diff --git ' not in t:
            bulgu.append('%s: `diff --git` yok (yama degil ya da bos)' % rel)
        for m in HEDEF.finditer(t):
            for yol in m.groups():
                if yol and (yol.startswith('/') or '..' in yol.split('/') or re.match(r'^[A-Za-z]:', yol) or '\\' in yol):
                    bulgu.append('%s:%d yama hedef yolu guvensiz (mutlak / .. / surucu): <%d krk>' % (rel, t.count('\n', 0, m.start()) + 1, len(yol)))
    # 2: SERIES
    seri = seri_oku(c)
    if seri is None:
        if ym:
            bulgu.append('%s yok ama %d yama var' % (SERI, len(ym)))
    else:
        goreli = ['patches/' + s for s in seri]
        for s, g in zip(seri, goreli):
            if g not in c.dosyalar:
                bulgu.append('%s: listelenen yama yok: %s' % (SERI, s))
        for g in sorted(set(ym) - set(goreli)):
            bulgu.append('%s listede degil (SERIES.txt eksik)' % g)
        gor = set()
        for s in seri:
            if s in gor:
                bulgu.append('%s: yinelenen satir %s' % (SERI, s))
            gor.add(s)
        son = {}
        for s in seri:
            grup, ad = (s.rsplit('/', 1) + [''])[:2] if '/' in s else ('', s)
            mm = re.match(r'(\d+)-', ad.rsplit('/', 1)[-1])
            if mm:
                n = int(mm.group(1))
                if grup in son and n <= son[grup]:
                    bulgu.append('%s: %s sirasi bozuk (NN- artan olmali)' % (SERI, s))
                son[grup] = n
    # 3: hash tablosu
    tablo, tb = tablo_oku(c)
    bulgu.extend(tb)
    if tablo is not None:
        for rel in ym:
            if rel not in tablo:
                bulgu.append('%s tabloda yok (yeni yama: tablo satiri gerekir)' % rel)
            elif tablo[rel] != sha(c.bayt(rel)):
                bulgu.append('%s sha256 tabloyla UYUSMUYOR (yama baytlari degisti: bilincli ise --tablo-yaz ve gerekce)' % rel)
        for rel in sorted(set(tablo) - set(ym)):
            bulgu.append('%s tabloda var, dosya yok' % rel)
    # 5: satir sonu kurali (.gitattributes'tan OKUNUR; sabit yazilmaz)
    kurallar = eol_kurallari(c)
    if '.gitattributes' not in c.dosyalar:
        bilgi.append('.gitattributes yok: satir sonu kurali okunamadi')
    def kural_var(rel, hedef):
        eol = None
        for desen, e in kurallar:
            if _desen_uyar(desen, rel):
                eol = e
        return eol == hedef
    for rel in c.dosyalar:   # kurala bagli olmayan ama satir sonuna duyarli turler: kural SART (yoksa LF'li bir .cmd Windows'ta bozulur)
        e = os.path.splitext(rel)[1].lower()
        if e in ('.cmd', '.bat') and not kural_var(rel, 'crlf'):
            bulgu.append('%s: .gitattributes `eol=crlf` kurali yok (.cmd/.bat CRLF ister; kural: `*.cmd text eol=crlf`)' % rel)
        elif e == '.sh' and not kural_var(rel, 'lf'):
            bulgu.append('%s: .gitattributes `eol=lf` kurali yok (.sh LF ister)' % rel)
    git_eol = _git_eol(c)   # {yol: (indeks, calisma)} ; git yoksa bos
    cr_bilgi = 0
    for rel in c.dosyalar:
        if rel.endswith('.patch'):
            continue
        eol = None
        for desen, e in kurallar:
            if _desen_uyar(desen, rel):
                eol = e
        if eol is None:
            continue
        b = c.bayt(rel)
        if b'\x00' in b[:4096]:
            continue
        if eol == 'lf':
            idx = git_eol.get(rel, ('', ''))[0]
            if idx in ('crlf', 'mixed'):
                bulgu.append('%s: depodaki (indeks) icerikte CR var ama .gitattributes eol=lf' % rel)
            elif b'\r' in b:
                if rel in git_eol:
                    cr_bilgi += 1   # git indekse LF olarak yazar: zarar yok, yalniz yerel gorunum
                else:
                    bulgu.append('%s:%d CR bayti ama .gitattributes eol=lf' % (rel, b.count(b'\n', 0, b.index(b'\r')) + 1))
        elif eol == 'crlf':
            k = re.search(rb'(?<!\r)\n', b) or re.search(rb'\r(?!\n)', b)
            if k:   # yerel dosya CRLF degil: git commit'te LF'ye cevirir ve klonda CRLF yapar, ama yerelde sinanan dosya sevk edilen bicim olmali
                bulgu.append('%s:%d satir sonu CRLF degil ama .gitattributes eol=crlf (yerelde sinanan .cmd LF ile bozulur; CRLF kaydedin)' % (rel, b.count(b'\n', 0, k.start()) + 1))
    if cr_bilgi:
        bilgi.append('%d dosya calisma agacinda CRLF (eol=lf kurali: git indekse LF yazar, zarar yok)' % cr_bilgi)
    return bulgu, bilgi


def tablo_yaz(kok, dosyalar):
    adlar = sorted(f for f in dosyalar if f.startswith('patches/') and f.endswith('.patch'))
    satirlar = ['# sha256 tablosu: `sha256sum -c patches/SHA256SUMS` (kokten) ya da scripts/yama_bekcisi.py (denetim.py --kapi yama).',
                '# Yama baytlari bilerek degisince bu dosya yeniden yazilir (python -I scripts/yama_bekcisi.py --tablo-yaz) ve gerekcesi PR/commit mesajina girer.']
    for a in adlar:
        with open(os.path.join(kok, *a.split('/')), 'rb') as f:
            satirlar.append('%s  %s' % (sha(f.read()), a))
    with open(os.path.join(kok, 'patches', 'SHA256SUMS'), 'w', newline='\n', encoding='ascii') as f:
        f.write('\n'.join(satirlar) + '\n')
    return len(adlar)


# ---------------------------------------------------------------- yerel: git apply --check (CI'da yok)
def _git(dizin, *arg, env=None):
    return subprocess.run(['git', '-C', dizin] + list(arg), capture_output=True, timeout=300, env=env,
                          creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))


def uygula_kontrol(kok, kaynaklar, c):
    """kaynaklar: {'sdcpp': dizin, 'ggml': dizin}. Yamalari SERIES sirasiyla gecici indekse uygular. -> (bulgu listesi, bilgi listesi)."""
    bulgu, bilgi = [], []
    seri = seri_oku(c) or []
    baslik = c.bayt(SERI).decode('utf-8', 'replace') if SERI in c.dosyalar else ''
    taban = {}
    m = re.search(r'stable-diffusion\.cpp ([0-9a-f]{7,40})', baslik)
    if m:
        taban['sdcpp'] = m.group(1)
    m = re.search(r'\bggml ([0-9a-f]{7,40})', baslik)
    if m:
        taban['ggml'] = m.group(1)
    for grup in ('ggml', 'sdcpp'):
        liste = [s for s in seri if s.startswith(grup + '/')]
        if not liste:
            continue
        dizin = kaynaklar.get(grup)
        if not dizin or not os.path.isdir(dizin):
            bulgu.append('%s: kaynak agaci verilmedi (--%s DIR)' % (grup, grup))
            continue
        h = _git(dizin, 'rev-parse', 'HEAD')
        if h.returncode != 0:
            bulgu.append('%s: git deposu degil' % grup)
            continue
        head = h.stdout.decode().strip()
        if grup in taban and not head.startswith(taban[grup]):
            bulgu.append('%s: HEAD %s, SERIES tabani %s: yanlis taban, sonuc anlamsiz' % (grup, head[:10], taban[grup]))
            continue
        with tempfile.TemporaryDirectory(prefix='yama_idx_') as td:
            env = dict(os.environ, GIT_INDEX_FILE=os.path.join(td, 'idx'))
            r = _git(dizin, 'read-tree', 'HEAD', env=env)
            if r.returncode != 0:
                bulgu.append('%s: gecici indeks kurulamadi' % grup)
                continue
            for s in liste:
                yol = os.path.join(kok, 'patches', *s.split('/'))
                for mod in (('--check',), ()):
                    r = _git(dizin, 'apply', '--cached', *mod, yol, env=env)
                    if r.returncode != 0:
                        bulgu.append('%s: %s uygulanmiyor (git apply %s): %s' % (grup, s.rsplit('/', 1)[-1], 'kontrol' if mod else 'uygula',
                                                                                 r.stderr.decode('utf-8', 'replace').strip().splitlines()[0][:120] if r.stderr.strip() else 'hata'))
                        break
                else:
                    continue
                break
            else:
                bilgi.append('%s: %d yama %s tabanina sirayla uygulandi (git apply --check, gecici indeks)' % (grup, len(liste), head[:10]))
    return bulgu, bilgi


def main(argv=None):
    sys.dont_write_bytecode = True
    ap = argparse.ArgumentParser(prog='yama_bekcisi.py')
    ap.add_argument('--kok', default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ap.add_argument('--tablo-yaz', action='store_true')
    ap.add_argument('--uygula-kontrol', action='store_true')
    ap.add_argument('--sdcpp')
    ap.add_argument('--ggml')
    a = ap.parse_args(argv)
    kok = os.path.abspath(a.kok)
    # denetim.py'nin Baglam sinifi: ayni dosya listesi
    import importlib.util
    spec = importlib.util.spec_from_file_location('vt_denetim', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'denetim.py'))
    d = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(d)
    c = d.Baglam(kok)
    if a.tablo_yaz:
        print('SONUC: TABLO YAZILDI (%d yama)' % tablo_yaz(kok, c.dosyalar))
        return 0
    if a.uygula_kontrol:
        if os.environ.get('CI') or os.environ.get('GITHUB_ACTIONS'):
            print('GIRDI HATALI: --uygula-kontrol yalniz yerelde (CI kaynak agaci indirmez)')
            print('SONUC: GIRDI HATALI (3)')
            return 3
        bulgu, bilgi = uygula_kontrol(kok, {'sdcpp': a.sdcpp, 'ggml': a.ggml}, c)
        for b in bulgu:
            print('KIRMIZI %s' % b)
        for b in bilgi:
            print('BILGI   %s' % b)
        if bulgu:
            print('SONUC: KIRMIZI (%d)' % len(bulgu))
            return 1
        if not bilgi:
            print('SONUC: CALISMADI (6)')   # hicbir grup denenmediyse yesil verilmez
            return 6
        print('SONUC: GECTI')
        return 0
    ap.print_help()
    return 3


if __name__ == '__main__':
    sys.exit(main())
