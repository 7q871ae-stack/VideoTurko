#!/usr/bin/env python3
"""VideoTurko PR kapisi YAPISAL savunmalar (kirmizi takim 2, 2026-11-20). pr_kapi.py ve pr_kombinasyon.py bunu yukler; tek basina calistirilmaz. Python stdlib, ag yok, dosya yazmaz.

NEDEN: ilk kapi DESEN arardi; iki bagimsiz kirmizi takim (A dis saldirgan 20, B ajan manipulatoru 24) hicbir KIRMIZI almadan gecti, cunku desen listesi her yazimi bilemez.
Bu dosya desen yerine YAPI kurar (docs/github/repolar/videoturko/saldiri_kombinasyonlari.md "Kirmizi takim 2"):
  (a) cozme katmani    kural yazilmadan once satir CESITLI bicimlerde okunur: JSON/YAML/HTML kacislari, % kodlama, 'a'+'b' birlestirme, markdown vurgusu/HTML etiketi, NUL (UTF-16 artigi);
                       ardisik satirlar paragraf olarak birlestirilir (pr_kombinasyon). Kural bir kez yazilir, butun yazimlara bakar.
  (b) alan adi izni YOL duzeyinde: github.com yalniz kendi hesabimiz ve adi gecen yukari akis depolari, huggingface.co yalniz modeller.json'daki ve belgede adi gecen depolar.
  (c) yeni dosya adi/yeri   kokte .cmd/.bat/.exe/.dll..., conftest.py, sitecustomize, .pth, .pyc, __pycache__, windows komutunu golgeleyen betik = KIRMIZI.
  (d) korumali dosyada guvenlik islevi ezme/zayiflatma: Get-FileHash islevinin yeniden tanimi, hash/sha/_q satirinin silinmesi, sertifika dogrulamasini kapatma = KIRMIZI.
  (e) ajan sizdirma ve sahte onay: gh auth, git config --list, ortam dokumu, on dolgulu issue baglantisi, npx -y/uvx, "SONUC: GECTI"/"Reviewed-by"/onay iddiasi = KIRMIZI.
BEDEL: her kural tum depo taramasinda ve temiz PR ornekleriyle yanlis alarm icin olculdu (tests/denetim). GEVSETME: dar, tarihli, gerekceli istisna; kapi kapatilmaz.
SINIR: yine KABA; "guvenli" demez. Cikti beyaz liste ile suzulur; dis metin ekrana basilmaz. Bu dosya ASCII'dir; tehlikeli sozcukler parcalanarak yazilir.
"""
import re, os, sys, html
from urllib.parse import unquote

sys.dont_write_bytecode = True

K, S = 'KIRMIZI', 'SARI'
R = re.IGNORECASE


def _c(p):
    return re.compile(p, R)


# ================================================================ (a) cozme katmani
_U4 = re.compile(r'\\u([0-9a-fA-F]{4})')
_U8 = re.compile(r'\\U([0-9a-fA-F]{8})')
_UB = re.compile(r'`?\\?u\{([0-9a-fA-F]{1,6})\}')
_X2 = re.compile(r'\\x([0-9a-fA-F]{2})')
_ETIKET = re.compile(r'</?[A-Za-z][^<>]{0,30}>')
_EMFAZ = re.compile(r'\*{1,3}|_{1,3}|~~|`+')
_SESSIZ = re.compile('[\\u00ad\\u200b-\\u200f\\u2060\\ufeff]')
_KATLA = re.compile(r'[\'"]\s*\+\s*[\'"]')
_ISARET = re.compile('[\\\\&%*_~`<\\x00\'"]')
LIMIT = 20000


def _chr(m, taban=16):
    try:
        v = int(m.group(1), taban)
        return chr(v) if v < 0x110000 and not 0xD800 <= v <= 0xDFFF else m.group(0)
    except ValueError:
        return m.group(0)


def kacis_coz(t):
    """JSON/YAML/JS/PowerShell/HTML kacislarini ve % kodlamasini cozer (u0031 -> 1, &#104; -> h, ters bolu + bolu -> bolu)."""
    s = t
    if '\\' in s or 'u{' in s:
        s = _UB.sub(_chr, s)
        s = _U8.sub(_chr, s)
        s = _U4.sub(_chr, s)
        s = _X2.sub(_chr, s)
        s = s.replace('\\/', '/')
    if '&' in s:
        s = html.unescape(s)
    if '%' in s:
        s = unquote(s, errors='replace')
    return s


def temizle(t):
    """Markdown vurgusu, satir ici HTML etiketi ve gorunmez ayirici sozcuklerin icinden atilir (ig**no**re -> ignore)."""
    return _SESSIZ.sub('', _EMFAZ.sub('', _ETIKET.sub('', t)))


def varyantlar(t):
    """Satirin ASIL metninden farkli, taranacak ek okumalari (en cok 4). Ozel isaret yoksa bos: temiz satir ucuz."""
    if not _ISARET.search(t):
        return []
    t = t[:LIMIT]
    c = kacis_coz(t)
    adaylar = [c, _KATLA.sub('', t), temizle(t), temizle(c), t.replace('\x00', ''), _KATLA.sub('', c)]
    out = []
    for a in adaylar:
        if a != t and a not in out:
            out.append(a)
    return out[:4]


def genislet(eklenen):
    """[(yol, no, satir)] -> ayni liste + her satirin varyantlari (ayni yol/no). Kurallar hepsine bakar, tekrarlar sonda silinir."""
    ek = []
    for yol, no, t in eklenen:
        for v in varyantlar(t):
            ek.append((yol, no, v))
    return eklenen + ek


_ASCII_KACIS = ((_U4, 16), (_X2, 16), (re.compile(r'&#(\d{2,3});'), 10), (re.compile(r'&#[xX]([0-9a-fA-F]{2});'), 16))


def ascii_kacis_sayisi(t):
    """Harf/rakam/slash/iki nokta/nokta/@ uretecek kacis (x69, u0069, &#105;) sayisi: komut ya da adres gizleme belirtisi."""
    n = 0
    for rx, taban in _ASCII_KACIS:
        for m in rx.finditer(t):
            try:
                v = int(m.group(1), taban)
            except ValueError:
                continue
            if 0x30 <= v <= 0x39 or 0x41 <= v <= 0x5A or 0x61 <= v <= 0x7A or v in (0x2F, 0x3A, 0x2E, 0x40):
                n += 1
    return n


# ================================================================ (b) alan adi izni YOL duzeyinde
GITHUB_HOST = frozenset(('github.com', 'www.github.com', 'raw.githubusercontent.com'))
HF_HOST = frozenset(('huggingface.co', 'www.huggingface.co', 'hf.co'))
GITHUB_HESAP = frozenset(('alexturkey',))
GITHUB_DEPO = frozenset(('leejet/stable-diffusion.cpp', 'ggml-org/ggml', 'video-rebirth/hyperflow-h3-flash', 'qwenlm/qwen3-vl'))
GITHUB_YUKLEME = (('user-attachments', 'assets'),)
HF_DEPO_BELGE = frozenset(('minimaxai/minimax-h3', 'videorebirthai/hyperflow-h3-flash', 'comfy-org/minimax-h3', 'leejet/minimax-h3-gguf'))
_HF = None


def hf_depolari():
    """modeller.json'daki huggingface depolari + belgede adi gecen depolar (kucuk harf org/depo). Dosya yoksa ya da bozuksa yalniz belge listesi."""
    global _HF
    if _HF is None:
        s = set(HF_DEPO_BELGE)
        try:
            ham = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'modeller.json'), encoding='utf-8').read()
            for m in re.finditer(r'huggingface\.co/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)/', ham):
                s.add(m.group(1).lower())
        except (OSError, ValueError):
            pass
        _HF = frozenset(s)
    return _HF


def yol_parcalari(yol):
    """/a/b/../c?x#y -> ['a', 'c'] (kucuk harf, % cozulmus, nokta ve cift nokta islenmis)."""
    yol = unquote(re.split(r'[?#]', yol or '', 1)[0], errors='replace').replace('\\', '/').rstrip('.,;:!?*_')   # cumle sonu noktalama adres sayilmaz
    out = []
    for p in yol.split('/'):
        if p in ('', '.'):
            continue
        if p == '..':
            if out:
                out.pop()
            continue
        out.append(p.lower())
    return out


def adres_durumu(host, yol):
    """-> 'izinli' | 'yol_disi' | None (bu alan adi yol duzeyinde denetlenmeyen sinif: HOST_IZIN'e bakilir)."""
    h = host.lower().strip('.')
    p = yol_parcalari(yol)
    if p and ('...' in p or '\u2026' in p) and (h in GITHUB_HOST or h in HF_HOST):
        return 'izinli'   # belgedeki yer tutucu (github.com/.../dosya.zip): gercek adres degil, cozulemez
    if h in GITHUB_HOST:
        if len(p) >= 1 and p[0] in GITHUB_HESAP:
            return 'izinli'
        if len(p) >= 2 and (p[0] + '/' + re.sub(r'\.git$', '', p[1])) in GITHUB_DEPO:
            return 'izinli'
        if any(tuple(p[:len(g)]) == g for g in GITHUB_YUKLEME):
            return 'izinli'
        return 'izinli' if (not p and h != 'raw.githubusercontent.com') else 'yol_disi'
    if h in HF_HOST:
        depo = hf_depolari()
        if not p:
            return 'izinli'
        if len(p) == 1:
            return 'izinli' if any(d.split('/')[0] == p[0] for d in depo) else 'yol_disi'
        return 'izinli' if (p[0] + '/' + p[1]) in depo else 'yol_disi'
    if h.endswith('.github.com') or h.endswith('.huggingface.co') or h.endswith('.hf.co'):
        return 'yol_disi'
    return None


# ================================================================ (c) yeni dosya adi / yeri
KOK_CALISTIRILABILIR = frozenset(('.cmd', '.bat', '.exe', '.dll', '.com', '.scr', '.vbs', '.lnk', '.wsf', '.msi', '.jar', '.ps1', '.psm1'))
KOK_YAPILANDIRMA = frozenset(('setup.py', 'setup.cfg', 'pyproject.toml', 'pytest.ini', 'tox.ini', 'noxfile.py', 'makefile', 'package.json'))
PY_OTOMATIK = frozenset(('conftest.py', 'sitecustomize.py', 'usercustomize.py'))
PY_UZANTI = frozenset(('.pyc', '.pyo', '.pth', '.egg', '.whl', '.pyz', '.pyd'))
WIN_KOMUT = frozenset(('chcp', 'find', 'findstr', 'where', 'powershell', 'pwsh', 'curl', 'tar', 'python', 'pythonw', 'py', 'pip', 'git', 'cmd', 'reg', 'sc', 'net',
                       'ping', 'xcopy', 'robocopy', 'attrib', 'icacls', 'cert' 'util', 'bits' 'admin', 'mshta', 'rundll32', 'wscript', 'cscript', 'ffmpeg', 'nvidia-smi', 'wmic', 'cmake'))


def dosya_bulgu(yol, bilgi):
    """-> [(sev, aciklama)] (kural adi komb_dosya_adi)."""
    out = []
    p = yol.split('/')
    ad = p[-1]
    adk = ad.lower()
    uz = os.path.splitext(adk)[1]
    kok_ad = os.path.splitext(adk)[0]
    yeni = bool(bilgi.get('yeni'))
    if len(p) == 1 and yeni and uz in KOK_CALISTIRILABILIR:
        out.append((K, 'kokte YENI calistirilabilir/betik dosyasi (cift tikla ya da PATH ile calisir): iki goz'))
    if len(p) <= 2 and yeni and adk in KOK_YAPILANDIRMA:
        out.append((K, 'yeni derleme/test yapilandirma dosyasi (toplama/kurulum aninda kod calistirabilir)'))
    if adk in PY_OTOMATIK:
        out.append((K, 'python/pytest baslarken kendiliginden yuklenen dosya (conftest, sitecustomize): kod calistirir'))
    if uz in PY_UZANTI or '__pycache__' in [x.lower() for x in p]:
        out.append((K, 'derlenmis python / paket / yol dosyasi (.pyc, __pycache__, .pth, .whl): kaynaktan baska bir sey calisir'))
    if yeni and uz in ('.cmd', '.bat', '.com', '.exe', '.ps1') and kok_ad in WIN_KOMUT:
        out.append((K, 'yeni betik Windows komutunun adini tasiyor (calisma klasoru once aranir: komut golgelenir)'))
    return out


# ================================================================ (d) korumali dosyada guvenlik islevi ezme / zayiflatma
KORUMA_SINIFLARI = [
    ('hash', re.compile(r'Get-FileHash|hashlib\.sha|hexdigest\s*\(|\.Hash\b|sha256sum', R)),
    ('sha_karsilastirma', re.compile(r'(?:-ne|-eq|-notmatch|-ieq|-ine|!=|==)[^\n#]{0,50}(?:sha|hash)|(?:sha|hash)[^\n#]{0,50}(?:-ne|-eq|-ieq|-ine|!=|==)', R)),
    ('alinti', re.compile(r'\b_q\b|\bQUOTES\b|\bshlex\.quote\b|\bps_quote\b', R)),
    ('izin', re.compile(r'\b_IZIN\b|\binit_izin\b|VT_MCP_INIT_DIR|\brealpath\b', R)),
]
KORUMA_DOSYA = re.compile(r'^(?:scripts/|mcp/|\.github/)|\.(?:ps1|cmd|bat|psm1|sh)$', R)
PS_YERLESIK = ('Get-FileHash|Expand-Archive|Invoke-Web' 'Request|Invoke-Rest' 'Method|Start-' 'Process|Test-Path|Get-Content|Set-Content|Join-Path|Resolve-Path|Get-Command|Out-File|'
               'Copy-Item|Move-Item|Remove-Item|New-Item|Get-Item|Get-ChildItem|Add-Type|ConvertFrom-Json|ConvertTo-Json|Select-String|Write-Output|Get-Process|Stop-Process|'
               'Get-CimInstance|Get-WmiObject|Get-PSDrive|Get-Volume|Invoke-Command|Import-Module|Compare-Object|Get-Date|Start-Sleep|Test-Connection|Get-NetAdapter')
FONKSIYON_EZME = [
    (re.compile(r'^\s*function\s+(?:global:|script:|private:)?(?:%s)\b' % PS_YERLESIK, R), 'yerlesik PowerShell komutunu ezen islev tanimi (islev cmdlet\'ten once calisir, Get-FileHash vb. sahtelenir)'),
    (re.compile(r'\b(?:Set-Alias|New-Alias)\b|^\s*sal\s+\w+\s|\bSet-Item\s+(?:-Path\s+)?function:', R), 'takma ad / islev tablosu degisiyor (komut adi baska seye cozulur)'),
    (re.compile(r'\b(?:hashlib|subprocess|shutil|urllib\.request|requests|ssl)\.\w+\s*=[^=]'), 'standart modul islevi yeniden ataniyor (dogrulama sahtelenir)'),
]
ZAYIFLATMA = [
    (_c(r'-SkipCertificateCheck|ServerCertificateValidationCallback|\bverify\s*=\s*False|--no-check-certificate|CURLOPT_SSL_VERIFY(?:PEER|HOST)|CERT_NONE|_create_unverified_context|-SkipHash\w*|-NoVerify\b|-Insecure\b'),
     'sertifika/sha dogrulamasini kapatma'),
    (_c(r'SecurityProtocol\s*=[^\n]*\b(?:Ssl3|Tls|Tls11)\b(?!\d)'), 'eski/zayif TLS surumune dusurme'),
]


def koruma_bulgu(yol, eklenen, silinen, bilgi):
    """eklenen/silinen: bu dosyaya ait [(no, metin)]. -> [(sev, aciklama)] (kural komb_koruma)."""
    out = []
    if not KORUMA_DOSYA.search(yol) or yol.startswith('tests/'):
        return out
    uz = os.path.splitext(yol)[1].lower()
    for ad, rx in KORUMA_SINIFLARI:
        if ad == 'izin' and not yol.startswith('mcp/'):
            continue
        if ad == 'alinti' and uz != '.py':
            continue
        e = sum(1 for _, t in eklenen if rx.search(t))
        s = sum(1 for _, t in silinen if rx.search(t))
        if s > e:
            out.append((K, 'guvenlik/dogrulama satiri silindi ya da azaldi (%s: -%d +%d): yerine konan baska bir yerde kanitlanmali' % (ad, s, e)))
    if yol.startswith('mcp/') and (eklenen or silinen) and any(re.search(r'\bdef\s+_q\b|\bdef\s+\w*(?:quote|izin|allow)\w*', c, R) for c in bilgi.get('baslik', ())):
        out.append((K, 'alintilama/izin islevinin govdesi degisiyor (hunk basligi islevi gosteriyor): satir satir oku'))
    if uz in ('.ps1', '.psm1', '.cmd', '.bat', '.py', '.sh'):
        for _, t in eklenen:
            for rx, ac in FONKSIYON_EZME + ZAYIFLATMA:
                if rx.search(t):
                    out.append((K, ac))
    return out


# ================================================================ (e) ajan sizdirma, izinsiz arac, sahte onay
SIZDIRMA = [
    (_c(r'\bgh\s+auth\s+(?:token|status|login|setup-git)\b|\bgit\s+config\s+(?:--(?:global|system|local|worktree)\s+)?(?:--list|-l\b|--get-regexp|--show-origin)|\bgit\s+credential\s+(?:fill|approve|reject)\b'),
     'kimlik/oturum bilgisi okuyan komut (gh auth, git config --list, git credential)'),
    (_c(r'\bprintenv\b|\b(?:Get-ChildItem|gci|dir|ls)\s+(?:-\w+\s+)*env:|\bGet-Item\s+env:|\[(?:System\.)?Environment\]::GetEnvironmentVariables|\bos\.environ\.(?:items|keys|values)\s*\(|\bjson\.dumps\(\s*(?:dict\()?os\.environ|\bprint\(\s*os\.environ\s*\)|\bcmd(?:\.exe)?\s*/c\s+set\s*(?:[|>]|$)'),
     'ortam degiskenlerinin tamamini dokme (anahtarlar sizar)'),
    (_c(r'\b(?:Get-Content|gc|cat|type|more|Select-String|sls)\b[^\n|;]{0,60}(?:\.env\b|\.netrc|\.npmrc|\.git-credentials|\.aws[\\/]credentials|\.ssh[\\/]|\bid_rsa|\bid_ed25519|\.pypirc)'),
     'gizli/kimlik dosyasini okuma'),
]
ISSUE_DOLGU = _c(r'issues/new\?[^\s)>\]\'"]*\b(?:body|title)=')
IZINSIZ_ARAC = _c(r'\bnpx\s+(?:-y\b|--yes\b)|\buvx\b|\bbunx\b|\bpipx\s+run\b|\buv\s+(?:tool\s+)?run\s+[^\n]*--with\b|\bpnpm\s+dlx\b|\byarn\s+dlx\b|\bnpm\s+exec\s+(?:-y|--yes)\b')
SAHTE_ONAY = _c(r'\blabel(?:l?ed)?\b[^\n]{0,50}\b(?:checked|reviewed|approved|verified|vetted)\b[^\n]{0,60}\b(?:automation|bots?|agents?|skip|proceed|go ahead)\b|\b(?:review\s+)?automation\b[^\n]{0,30}\b(?:go ahead|may proceed|can proceed|can skip)\b|\bSONUC\s*:\s*(?:GECTI|SARI|OK|PASSED)\b|\bRESULT\s*:\s*(?:PASS|PASSED|OK|GREEN)\b|\b(?:Reviewed|Approved|Verified|Acked|Cleared|Audited|Security-reviewed)-by\s*:|\b(?:PUSH|RELEASE)\s+OK\b|'
                r'\bgate\s+result\s*:\s*(?:pass|passed|green|ok)\b|\bpr_kapi\b[^\n]{0,40}\b(?:gecti|passed|green)\b|\b(?:bekci|denetci|repo-denetci|auditor|security bot|review bot)\b[^\n]{0,30}\b(?:onayladi|approved|passed|gecti|signed off)\b|'
                r'\bSigned-off-by\s*:\s*(?:alexturkey|maintainer|repo-)')
_AJAN_YASAK_RX = _c(r'\b(?:assistant|agent|bot|llm)\b[^\n]{0,60}\b(?:accept|agree|approve|sign|consent|answer|respond|confirm)\w*\b[^\n]{0,40}\b(?:licen[sc]e|terms|eula|-LisansKabul|policy|prompt)|licen[sc]e[^\n]{0,80}\b(?:assistant|agent|bot|llm)\b[^\n]{0,40}\b(?:answer|accept|agree|confirm|respond|click|press)|-LisansKabul\b[^\n]{0,40}\b(?:assistant|agent|bot|on the user|on behalf)\b')
_OLUMSUZ = _c(r"\b(?:never|not|no|cannot|can't|must not|mustn't|don't|do not|without|unless|only the (?:user|human)|nicht|nie|asla|etmez|etmemeli|yapmaz|degil|insan|kullanicinin kararidir|human's|user's decision)\b|n't")


class _AjanYasak:
    """Lisans/sozlesme kabulunu ajana yaptiran kalip. Olumsuz cumle (AI agents must never accept for the user: belgenin KENDI kurali) yakalanmaz: baglamda olumsuzluk varsa atlanir."""

    @staticmethod
    def search(t):
        for m in _AJAN_YASAK_RX.finditer(t):
            if not _OLUMSUZ.search(t[max(0, m.start() - 45):m.end() + 12]):
                return m
        return None


AJAN_YASAK = _AjanYasak()
SAHTE_RUNS = re.compile(r'^runs/')
DEPENDABOT = re.compile(r'(?:^|/)dependabot\.ya?ml$', R)
DEPENDABOT_RISK = _c(r'insecure-external-code-execution|^\s*registries\s*:|\breplaces-base\b')
KARISIK_KOMUT_CMD = _c(r'^\s*(?:@?call\s+)?%[A-Za-z_]\w*%%[A-Za-z_%]')
CALL_DEGISKEN = _c(r'^\s*@?call\s+%[A-Za-z_]\w*%')
UZAK_EK = [
    (_c(r'\bDownload(?:Data|StringAsync|FileAsync)\s*\(|\[(?:System\.)?Reflection\.Assembly\]::(?:Load|LoadFrom|LoadFile)|Assembly\]::Load|\[scriptblock\]::Create|\bOpenRead\s*\(\s*[\'"]?https?:'),
     'indirilen bayti bellekte yukleme/kod olarak calistirma (DownloadData, Assembly::Load, scriptblock::Create)'),
]
PY_DINAMIK = _c(r'(?<![\w.])__import__\s*\(|\bgetattr\s*\(\s*__import__|\bimportlib\.import_module\s*\(\s*[\'"][a-z.]+[\'"]\s*\+')
DERLEME_BASLATICI = _c(r'COMPILER_LAUNCHER|CMAKE_PROJECT_(?:TOP_LEVEL_)?INCLUDES?\b|CMAKE_TOOLCHAIN_FILE|\bRULE_LAUNCH_(?:COMPILE|LINK|CUSTOM)|-fplugin=|-Wl,-plugin')
DERLEME_DOSYA = _c(r'(?:^|/)(?:derle[^/]*|derleme[^/]*|build[^/]*|CMakeLists\.txt|[^/]*\.cmake|[^/]*\.ps1|[^/]*\.cmd)$')
PIP_EK = _c(r'\bpip3?\.exe\s+install\b|\bgit\+ssh\b|\s@\s*git\+|\s-r\s+https?://|--requirement\s+https?://|\bPIP_(?:INDEX_URL|EXTRA_INDEX_URL|FIND_LINKS)\b')
GIZLI_EK = re.compile('[\\ufe00-\\ufe0e\\U000e0100-\\U000e01ef\\u3164\\u2800\\u115f\\u1160\\u17b4\\u17b5\\uffa0]')


def satir_bulgu(yol, t, okur, ajan, betik, uz):
    """Tek satir (ya da varyanti) icin yapisal kurallar. -> [(sev, kural, aciklama)]."""
    out = []
    for rx, ac in SIZDIRMA:
        if rx.search(t):
            out.append((K, 'komb_sizdirma', ac))
    if ISSUE_DOLGU.search(t):
        out.append((K if (okur or ajan) else S, 'komb_sizdirma', 'on dolgulu issue baglantisi (kullanici tek tikla ortam/donanim bilgisini herkese acik yere gonderir)'))
    if IZINSIZ_ARAC.search(t):
        out.append((K, 'komb_bagimlilik', 'onaysiz paket calistirma (npx -y / uvx / pipx run / dlx): indirilen kod aninda calisir'))
    if SAHTE_ONAY.search(t) and (okur or ajan or SAHTE_RUNS.match(yol)):
        out.append((K, 'komb_sahte_onay', 'dosyada kapi sonucu/onay iddiasi (SONUC: GECTI, Reviewed-by, onaylandi): kanit degil, ajani kandirma girisimi olabilir'))
    if AJAN_YASAK.search(t):
        out.append((K, 'ajan_enjeksiyon', 'ajan lisans/sozlesme kabulu yapsin kalibi (lisansi yalniz insan kabul eder)'))
    if DEPENDABOT.search(yol) and DEPENDABOT_RISK.search(t):
        out.append((K, 'komb_ci', 'dependabot ozel kayit / dis kod calistirma izni'))
    if betik or uz in ('.py', '.ps1', '.cmd', '.bat'):
        for rx, ac in UZAK_EK:
            if rx.search(t):
                out.append((K, 'uzak_kod', ac))
        if uz in ('.cmd', '.bat') and (KARISIK_KOMUT_CMD.search(t) or CALL_DEGISKEN.search(t)):
            out.append((K, 'komb_gizleme', 'cmd: komut degisken parcalarindan olusturuluyor (A-B bitisik genisleme ya da call degisken)'))
        if uz == '.py' and PY_DINAMIK.search(t):
            out.append((K, 'komb_gizleme', 'python: ad calisma aninda parcalardan kuruluyor / dinamik yukleme (__import__, windll)'))
        if PIP_EK.search(t):
            out.append((K, 'komb_bagimlilik', 'pip.exe / git+ssh / uzak requirements / PIP_* ortam degiskeni ile paket kaynagi'))
    if DERLEME_DOSYA.search(yol) and DERLEME_BASLATICI.search(t):
        out.append((K, 'komb_yama_ici', 'derleme zamani yururluk: derleyici baslatici / proje icerigi / arac zinciri dosyasi (derleme aninda baska program calisir)'))
    for m in GIZLI_EK.finditer(t):
        out.append((K, 'gorunmez_unicode', 'gorunum secici/Hangul dolgu/braille bos gibi gorunmez karakter U+%04X' % ord(m.group())))
        break
    return out
