#!/usr/bin/env python3
"""VideoTurko repo ici denetim cekirdegi (KL-03). Python stdlib, ag yok, dosya yazmaz, pencere acmaz.

  python -I scripts/denetim.py --hizli          # insan icin okunur cikti
  python -I scripts/denetim.py --hizli --json   # makine icin tek JSON belgesi (stdout)
  python -I scripts/denetim.py --kapi unicode   # tek kapi
  python -I scripts/denetim.py --liste          # kapi listesi

Cikis kodu sozlesmesi (uret.ps1 / MCP ile ayni dil):
  0 = hepsi GECTI        1 = en az bir kapi KIRMIZI (bulgu var)
  3 = girdi/ortam eksik (kok yok, gecersiz bayrak)
  6 = en az bir kapi CALISMADI (coktu / okunamadi) ve KIRMIZI yok: yesil sayilmaz (kapali hata)
Son satir her zaman tek bir `SONUC:` satiridir (--json'da JSON stdout'ta, SONUC satiri stderr'de).
Yesil yalniz `SONUC: GECTI` ile; cikti yoksa ya da SONUC satiri yoksa cagiran KALDI saymalidir.

Neden / bedel / gevsetme (kapi basina) ve ne olcer: docs/KAPILAR.md degil, asagidaki KAPILAR tablosu ve tests/denetim/.
Cikti kisisel yol basmaz: kok `<ROOT>` olarak yazilir, dosyalar goreli yoldur, Unicode bulgusu karakteri degil kod noktasini basar.
Bu betik niyet okumaz, desen okur: "gecti" = bu kaba desenler yok; "guvenli" demek degildir.
"""
import sys, os, re, json, time, argparse, subprocess
import importlib.util

sys.dont_write_bytecode = True   # alt kapi modulleri yuklenirken scripts/__pycache__ yazilmasin (bu betik dosya yazmaz)

for _akis in (sys.stdout, sys.stderr):  # `python -I` PYTHONUTF8/PYTHONIOENCODING'i yok sayar; konsol/boru cp1254 ise Ibranice dosya adi basilirken COKMESIN
    try:
        _akis.reconfigure(encoding='utf-8', errors='replace')
    except (AttributeError, ValueError):
        pass

SURUM = 1
SURE_TAVANI_SN = 10

# ---------------------------------------------------------------- Unicode kural tablosu
# Sinif -> kod noktasi araligi. Karakterler kaynakta KACIS dizisiyle yazilir (bu dosya kendi kapisindan gecmeli).
# NEDEN: "Trojan Source" (bidi kilma) ve sifir genislikli karakterler kodda/talimat dosyasinda insana gorunmeyen davranis gizler.
# BEDEL: RTL/Hint dilli README ceviri dosyalari gercekten ZWNJ/ZWJ/LRM/RLM kullanir; onlara dar izin verilir (asagida).
# GEVSETME: yeni bir dil dosyasi eklenirse dil kodu IZIN tablosuna eklenir (tek satir, gerekcesiyle, denetci sahibi).
SINIFLAR = (
    ('bidi_gecersiz_kilma', ((0x202D, 0x202E),)),            # LRO/RLO: Trojan Source'un asil silahi, hicbir yerde izinli degil
    ('bidi_gomme', ((0x202A, 0x202C),)),                     # LRE/RLE/PDF
    ('bidi_izole', ((0x2066, 0x2069),)),                     # LRI/RLI/FSI/PDI
    ('bidi_isaret', ((0x200E, 0x200F), (0x061C, 0x061C))),   # LRM/RLM/ALM
    ('sifir_genislik_birlestirici', ((0x200C, 0x200D),)),    # ZWNJ/ZWJ
    ('gizli', ((0x200B, 0x200B), (0x2060, 0x2064), (0x00AD, 0x00AD), (0x180E, 0x180E), (0x034F, 0x034F),
               (0xFEFF, 0xFEFF), (0xFFF9, 0xFFFB), (0xE0000, 0xE007F))),   # ZWSP, kelime birlestirici, gorunmez islec, yumusak tire, etiket karakterleri; FEFF yalniz dosya basinda (BOM) serbest
)
RTL_DIL = frozenset(('ar', 'fa', 'he', 'ur'))     # LRM/RLM/ALM izinli diller = bugun gercekten kullanan 4 RTL ceviri (en az yetki; scripts/dil_profili.json lrm_izinli ile ayni)
ZW_DIL = frozenset(('bn', 'hi', 'th', 'fa'))      # ZWNJ/ZWJ izinli diller (dil_profili.json zwj_izinli ile ayni); yeni dil gerekirse tek satir + gerekce
README_DIL = re.compile(r'README\.([A-Za-z]{2,3})(?:-[A-Za-z]{2,4})?\.md')   # yalniz kokteki README.<dil>.md; baska hicbir dosya muaf degil


def unicode_sinifi(cp):
    for ad, aralik in SINIFLAR:
        for a, b in aralik:
            if a <= cp <= b:
                return ad
    return None


def unicode_izinli(yol, sinif):
    """Tek yetkili tablo: yalniz kok README.<dil>.md ve yalniz dile uygun sinif. Kod/AGENTS/CLAUDE/.github/scripts: hicbiri."""
    m = README_DIL.fullmatch(yol)
    if not m:
        return False
    dil = m.group(1).lower()
    if sinif == 'sifir_genislik_birlestirici':
        return dil in ZW_DIL
    if sinif == 'bidi_isaret':
        return dil in RTL_DIL
    return False   # kilma/gomme/izole/gizli: README'de bile yok (dil_eslik_denetimi.py ile ayni sinir)


# ---------------------------------------------------------------- NUL istisnasi (Z8)
# Yol -> tam NUL sayisi. NEDEN: yama 02 C kaynaginda `'\0'` yerine ham NUL bayt tasir, yama 03 tam o satiri duzeltir; dosyalar
# derlenip denendigi gibi bayt-aynisi korunur (degisirse hash degisir). docs/YAMALAR.md bunu belgeler (kapi bunu da arar).
# BEDEL: yeni her NUL kirmizi: istisna eklemek bilincli, gerekceli ve denetci incelemeli bir karar. GEVSETME: yama duzeltilince girdi silinir
# (sayi dusunce kapi "gereksiz istisna" BILGI verir).
NUL_ISTISNA = {
    'patches/ggml/02-p0005-optime-file.patch': 1,
    'patches/ggml/03-p0005-optime-fix.patch': 1,
}
NUL_BELGE = ('docs/YAMALAR.md', re.compile(r'raw NUL byte'))

IKILI_UZANTI = frozenset(('.png', '.jpg', '.jpeg', '.gif', '.webp', '.ico', '.bmp', '.zip', '.gz', '.7z', '.xz', '.bin', '.gguf', '.safetensors',
                          '.mp4', '.avi', '.mkv', '.webm', '.wav', '.mp3', '.flac', '.ogg', '.pyc', '.pdf', '.dll', '.exe', '.onnx', '.pt', '.pth', '.npy'))


# ---------------------------------------------------------------- dosya listesi
class Baglam:
    def __init__(self, kok):
        self.kok = kok
        self.dosyalar = self._liste()
        self._onbellek = {}

    def _liste(self):
        kok = self.kok
        if os.path.exists(os.path.join(kok, '.git')):   # klasor ya da worktree isaretci dosyasi
            try:
                p = subprocess.run(['git', '-C', kok, 'ls-files', '-z', '--cached', '--others', '--exclude-standard'], capture_output=True, timeout=8,
                                   creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
                if p.returncode == 0:
                    adlar = [x.decode('utf-8', 'replace') for x in p.stdout.split(b'\0') if x]
                    return sorted(a for a in adlar if os.path.isfile(os.path.join(kok, a)))
            except (OSError, subprocess.SubprocessError):
                pass   # git yok: yuruyus
        atla = {'.git', '__pycache__', 'node_modules'}
        gi = os.path.join(kok, '.gitignore')
        if os.path.isfile(gi):   # yalniz koke sabit `/ad/` satirlari (agir yerel klasorler); tam gitignore degil
            for s in open(gi, encoding='utf-8', errors='replace').read().splitlines():
                m = re.fullmatch(r'/([^/*?]+)/?', s.strip())
                if m:
                    atla.add(m.group(1))
        out = []
        for d, ds, fs in os.walk(kok):
            ds[:] = [x for x in ds if x not in atla]
            for f in fs:
                if f == '.git':   # worktree isaretcisi: commit edilmez, mutlak yol tasir
                    continue
                out.append(os.path.relpath(os.path.join(d, f), kok).replace(os.sep, '/'))
        return sorted(out)

    def bayt(self, rel):
        if rel not in self._onbellek:
            with open(os.path.join(self.kok, rel), 'rb') as f:
                self._onbellek[rel] = f.read()
        return self._onbellek[rel]

    def metinler(self):
        for rel in self.dosyalar:
            if os.path.splitext(rel)[1].lower() in IKILI_UZANTI:
                continue
            yield rel, self.bayt(rel)


def _metin(b):
    """UTF-16 BOM'lu dosyayi UTF-16, digerini UTF-8 oku (gecersiz bayt yerine koyma: kapi cokmez)."""
    if b[:2] in (b'\xff\xfe', b'\xfe\xff'):
        return b.decode('utf-16', 'replace'), True
    return b.decode('utf-8', 'replace'), False


# ---------------------------------------------------------------- kapilar: fonksiyon(baglam) -> (bulgu listesi, bilgi listesi)
def kapi_unicode(c):
    bulgu, bilgi = [], []
    for rel, b in c.metinler():
        t, _ = _metin(b)
        sayac = {}
        for m in re.finditer('[\u00ad\u034f\u061c\u180e\u200b-\u200f\u202a-\u202e\u2060-\u2069\ufff9-\ufffb\ufeff\U000e0000-\U000e007f]', t):
            cp = ord(m.group())
            if cp == 0xFEFF and m.start() == 0:
                continue   # dosya basindaki BOM (PowerShell 5.1 icin gerekli olabilir)
            s = unicode_sinifi(cp)
            if s is None or unicode_izinli(rel, s):
                continue
            k = (cp, s)
            if k not in sayac:
                sayac[k] = [t.count('\n', 0, m.start()) + 1, 0]
            sayac[k][1] += 1
        for (cp, s), (satir, n) in sorted(sayac.items()):
            bulgu.append('%s:%d U+%04X %s x%d (bu dosya turunde izinli degil)' % (rel, satir, cp, s, n))
    return bulgu, bilgi


def kapi_kontrol(c):
    """Kontrol baytlari (<0x20, TAB/LF/CR haric): ham NUL, geri silme (ters bolu kacis kazasi), ESC. NUL yalniz kayitli yamalarda, tam sayiyla."""
    bulgu, bilgi = [], []
    belge_ok = None
    for rel, b in c.metinler():
        if b[:2] in (b'\xff\xfe', b'\xfe\xff'):
            continue   # UTF-16 dosyada NUL dogal; Unicode kapisi okur
        kt = [(i, x) for i, x in enumerate(b) if x < 0x20 and x not in (9, 10, 13)]
        if not kt:
            if rel in NUL_ISTISNA:
                bilgi.append('%s: kayitli NUL istisnasi gereksiz (dosyada NUL yok): NUL_ISTISNA girdisini sil' % rel)
            continue
        nul = sum(1 for _, x in kt if x == 0)
        diger = [(i, x) for i, x in kt if x != 0]
        for i, x in diger[:3]:
            bulgu.append('%s:%d kontrol bayti 0x%02X' % (rel, b.count(b'\n', 0, i) + 1, x))
        if nul:
            beklenen = NUL_ISTISNA.get(rel)
            if beklenen is None:
                bulgu.append('%s: %d NUL bayt (kayitli istisna yok)' % (rel, nul))
            else:
                if belge_ok is None:
                    try:
                        belge_ok = bool(NUL_BELGE[1].search(c.bayt(NUL_BELGE[0]).decode('utf-8', 'replace')))
                    except OSError:
                        belge_ok = False
                if nul > beklenen:
                    bulgu.append('%s: %d NUL bayt, kayitli istisna %d' % (rel, nul, beklenen))
                elif not belge_ok:
                    bulgu.append('%s: NUL istisnasi var ama %s belgelemiyor' % (rel, NUL_BELGE[0]))
                elif nul < beklenen:
                    bilgi.append('%s: NUL sayisi %d < kayitli %d: istisnayi daralt' % (rel, nul, beklenen))
    return bulgu, bilgi


def kapi_sozdizimi(c):
    """Her *.py derlenir (calistirilmaz, __pycache__ yazilmaz), her *.json ayristirilir."""
    bulgu = []
    for rel in c.dosyalar:
        e = os.path.splitext(rel)[1].lower()
        if e == '.py':
            try:
                compile(c.bayt(rel), rel, 'exec', dont_inherit=True)
            except (SyntaxError, ValueError) as ex:
                bulgu.append('%s:%s python sozdizimi: %s' % (rel, getattr(ex, 'lineno', None) or 0, type(ex).__name__))
        elif e == '.json':
            try:
                json.loads(c.bayt(rel).decode('utf-8-sig'))
            except (ValueError, UnicodeDecodeError) as ex:
                bulgu.append('%s json ayristirilamadi: %s' % (rel, type(ex).__name__))
    return bulgu, []


def kapi_guvenlik_md(c):
    """SECURITY.md: gizli bildirim yolu, 'hedef' dili (taahhut degil), sha dogrulama, ajan enjeksiyonu ve MCP tehdit modeli yazili mi."""
    if 'SECURITY.md' not in c.dosyalar:
        return ['SECURITY.md yok'], []
    t = c.bayt('SECURITY.md').decode('utf-8', 'replace')
    bulgu = []
    if not re.search(r'Report a vulnerability', t):
        bulgu.append('SECURITY.md: "Report a vulnerability" (gizli bildirim yolu) yok')
    if not re.search(r'(?i)\btarget\b[^.\n]{0,80}\b(7|seven)\b[^.\n]{0,12}days?', t):
        bulgu.append('SECURITY.md: EN "target ... 7 days" (hedef sure) cumlesi yok')
    if not re.search(r'(?i)\bhedef\w*[^.\n]{0,80}\b7\b[^.\n]{0,12}g[uü]n', t):
        bulgu.append('SECURITY.md: TR "hedef ... 7 gun" cumlesi yok')
    if not re.search(r'(?i)not a (commitment|guarantee|promise)', t):
        bulgu.append('SECURITY.md: EN "not a commitment" ibaresi yok')
    if not re.search(r'(?i)taahh[uü]t[^.\n]{0,30}de[gğ]il', t):
        bulgu.append('SECURITY.md: TR "taahhut degil" ibaresi yok')
    for m in re.finditer(r'(?i)(within|in)\s+(7|seven)\s+days|\b7\s+g[uü]n\s+i[cç]inde', t):   # "target" yoksa soz gibi okunur
        if not re.search(r'(?i)target|hedef|aim', t[max(0, m.start() - 90):m.start() + 20]):
            bulgu.append('SECURITY.md: "7 gun" hedef/target olmadan (taahhut gibi okunur): %r' % t[m.start():m.end()])
    if not re.search(r'Get-FileHash', t):
        bulgu.append('SECURITY.md: tek satir sha256 dogrulama (Get-FileHash) yok')
    if not re.search(r'(?i)prompt[- ]injection', t):
        bulgu.append('SECURITY.md: ajan prompt-injection paragrafi yok')
    if not re.search(r'(?i)MCP', t) or not re.search(r'(?i)threat model|tehdit modeli', t):
        bulgu.append('SECURITY.md: MCP tehdit modeli yok')
    return bulgu, []



def _modul(ad):
    """Alt kapi modulunu bu klasorden yukler (`python -I` script klasorunu sys.path'e koymaz). Okunamazsa istisna -> kapi CALISMADI (yesil degil)."""
    yol = os.path.join(os.path.dirname(os.path.abspath(__file__)), ad + '.py')
    spec = importlib.util.spec_from_file_location('vt_' + ad, yol)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def kapi_gizlilik(c):
    """Sir, kisisel yol, e-posta, saat dilimi izi, yama Date: (UTF-8 ve UTF-16 baytlari); cikti maskeli. Ayrinti: gizlilik_denetimi.py."""
    kisisel = []
    yol = os.environ.get('VT_GIZLILIK_KISISEL')   # kisisel terim listesi (ad, takma ad): dosya depo DISINDA durmali
    if yol:
        if os.path.abspath(yol).lower().startswith(os.path.abspath(c.kok).lower() + os.sep):
            return ['VT_GIZLILIK_KISISEL listesi depo icinde olamaz (kisisel terim icerir)'], []
        kisisel = open(yol, encoding='utf-8').read().splitlines()
    return _modul('gizlilik_denetimi').kapi_gizlilik(c, kisisel)


def kapi_yama(c):
    """patches/: CR yok, SERIES.txt tutarli, sha256 tablosu birebir, yama yapisi, .gitattributes satir sonu kurali (kur.cmd CRLF). Ayrinti: yama_bekcisi.py."""
    return _modul('yama_bekcisi').kapi_yama(c)


def kapi_pr_kapi(c):
    """pr_kapi.py'nin kendi kotu/iyi diff orneklerini sinar: kapi ornegi yakalamiyorsa yesil yok. Gercek PR taramasi: `python -I scripts/pr_kapi.py --taban REF --bas REF`."""
    return _modul('pr_kapi').kapi_pr_kapi(c)


# ad -> (islev, neden, bedel, gevsetme)
KAPILAR = {
    'unicode': (kapi_unicode, 'gorunmez/bidi karakter kodda ya da ajan talimatinda davranis gizler (Trojan Source)',
                'RTL ve Hint yazili README ceviri dosyalari dar izinle muaf; baska her yerde 1 karakter KIRMIZI', 'yeni dil dosyasi: dil kodu tabloya eklenir'),
    'kontrol': (kapi_kontrol, 'ham NUL/geri silme/ESC baytlari kacis kazasi ya da gizleme belirtisidir (gecmiste "\\b" yol kazasi yasandi)',
                'kayitli yama istisnasi disinda her NUL KIRMIZI', 'yama duzelince NUL_ISTISNA girdisi silinir'),
    'sozdizimi': (kapi_sozdizimi, 'bozuk betik/JSON push edilmesin; calistirmadan derleme yeterli',
                  '.ps1 icin yok (PowerShell ayristiricisi stdlib degil)', 'PowerShell ayristirma ayri kapiyla eklenebilir'),
    'guvenlik_md': (kapi_guvenlik_md, 'guvenlik bildirim sozu dogru ve taahhut gibi okunmayan dille yazili kalsin',
                    'metin kalibi arar, icerigin dogrulugunu olcmez', 'SECURITY.md sade tutulacaksa kalip gevsetilir (denetci karari)'),
    'gizlilik': (kapi_gizlilik, 'sizan sir, kisisel yol, e-posta ve saat dilimi izi git gecmisinde kalir, geri alinamaz',
                 'yanlis alarm (dar IZIN tablosu); ikili dosyada yalniz guclu kurallar; adlar/yuzler taranmaz', 'dar, gerekceli, denetci onayli IZIN satiri; MiniMax lisans adresi yalniz lisans belgelerinde'),
    'pr_kapi': (kapi_pr_kapi, 'dis PR betigi kullanicinin makinesinde calisir: PR kapisi (pr_kapi.py) kaba kotu niyet desenlerini yakalamali; bu kapi onun kendi orneklerini sinar',
                'KABA DESEN yakalar, niyet okumaz, "korur" denmez; yanlis pozitif ve bakim', 'dar, tarihli IZIN satiri; kapi kapanmaz'),
    'yama': (kapi_yama, 'yama baytlari derlenen motorun kendisidir: CRLF yamayi bozar, sessiz degisiklik bayt-ayni kanitini gecersiz kilar',
             'yama bilerek degisince sha256 tablosu da yenilenir (tek komut); tablo ayni depoda: ayni PR ikisini degistirirse kapi yesil verir (pr_kapi SARI yakalar)',
             'yok; yeni yama = yeni tablo ve SERIES satiri'),
}


# ---------------------------------------------------------------- calistirici
class Ayri(argparse.ArgumentParser):
    def error(self, mesaj):
        raise ValueError(mesaj)


def _maske(s, kok):
    return s.replace(kok, '<ROOT>').replace(kok.replace(os.sep, '/'), '<ROOT>')


def calistir(secili, kok):
    sonuc = []
    c = Baglam(kok)
    for ad in secili:
        islev = KAPILAR[ad][0]
        try:
            bulgu, bilgi = islev(c)
            durum = 'KIRMIZI' if bulgu else 'GECTI'
        except Exception as e:   # kapali hata: coken kapi yesil degildir
            bulgu, bilgi, durum = ['kapi CALISMADI: %s: %s' % (type(e).__name__, _maske(str(e), kok)[:160])], [], 'CALISMADI'
        sonuc.append({'ad': ad, 'durum': durum, 'bulgu': bulgu, 'bilgi': bilgi})
    return sonuc


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    ap = Ayri(prog='denetim.py', add_help=True)
    ap.add_argument('--hizli', action='store_true', help='ag yok, <=10 sn (su an tam mod da ayni kapilari kosar; sonraki dalgalar tam moda ekler)')
    ap.add_argument('--json', action='store_true')
    ap.add_argument('--kapi', action='append', default=[], help='yalniz bu kapi (tekrarlanabilir)')
    ap.add_argument('--liste', action='store_true')
    ap.add_argument('--kok', default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    try:
        a = ap.parse_args(argv)
    except ValueError as e:
        print('GIRDI HATALI: %s' % str(e)[:120])
        print('SONUC: GIRDI HATALI (3)')
        return 3
    except SystemExit as e:   # --help
        return int(e.code or 0)
    if a.liste:
        for ad, (_, neden, bedel, gev) in KAPILAR.items():
            print('%-12s neden: %s | bedel: %s | gevsetme: %s' % (ad, neden, bedel, gev))
        print('SONUC: LISTE (0)')
        return 0
    kok = os.path.abspath(a.kok)
    bilinmeyen = [k for k in a.kapi if k not in KAPILAR]
    if bilinmeyen or not os.path.isdir(kok):
        print('GIRDI HATALI: %s' % ('bilinmeyen kapi %s' % bilinmeyen if bilinmeyen else 'kok klasor yok'))
        print('SONUC: GIRDI HATALI (3)')
        return 3
    t0 = time.time()
    try:
        sonuc = calistir(a.kapi or list(KAPILAR), kok)
    except Exception as e:   # baglam kurulamadi vb.: hicbir sey olculmedi
        print('CALISMADI: %s: %s' % (type(e).__name__, _maske(str(e), kok)[:160]))
        print('SONUC: CALISMADI (6)')
        return 6
    sure = time.time() - t0
    kirmizi = [s for s in sonuc if s['durum'] == 'KIRMIZI']
    coken = [s for s in sonuc if s['durum'] == 'CALISMADI']
    if kirmizi:
        satir, kod = 'SONUC: KIRMIZI (%d)' % len(kirmizi), 1
    elif coken:
        satir, kod = 'SONUC: CALISMADI (%d)' % len(coken), 6
    else:
        satir, kod = 'SONUC: GECTI', 0
    uyari = ['sure %.1f sn > %d sn tavani' % (sure, SURE_TAVANI_SN)] if sure > SURE_TAVANI_SN else []
    if a.json:
        print(json.dumps({'surum': SURUM, 'mod': 'hizli' if a.hizli else 'tam', 'kok': '<ROOT>', 'sure_sn': round(sure, 2), 'uyari': uyari,
                          'kapilar': sonuc, 'sonuc': satir[len('SONUC: '):], 'cikis': kod}, ensure_ascii=False, indent=1))
        print(satir, file=sys.stderr)
    else:
        for s in sonuc:
            print('%-12s %-9s' % (s['ad'], s['durum']))
            for b in s['bulgu']:
                print('    KIRMIZI %s' % b)
            for b in s['bilgi']:
                print('    BILGI   %s' % b)
        for u in uyari:
            print('UYARI %s' % u)
        print(satir)
    return kod


if __name__ == '__main__':
    sys.exit(main())
