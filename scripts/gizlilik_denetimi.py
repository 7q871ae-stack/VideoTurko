"""VideoTurko gizlilik kapisi (KL-04): repoya sir, kisisel yol, e-posta, saat dilimi izi girmesin. denetim.py'nin alt kapisi.

Kaynak: ekip kapisi `yasal_denetim.py` uyarlamasi; VideoTurko icin sadelestirildi: lisans ve medya kurallari yok,
UTF-16 bayt taramasi ve yama `Date:` kurali eklendi. Tek giris `python -I scripts/denetim.py --kapi gizlilik`; bu dosya kendi basina calismaz.

Ne yapar: izlenen/izlenmeyen-ama-ignore-olmayan her dosyanin BAYTLARINI okur; UTF-8 metni, UTF-16 (BOM'lu ya da BOM'suz, cift/tek hizali) ve
ikili dosyadaki ASCII/UTF-16 dizileri ayni kurallardan gecirir (bekci ile ayni yontem: `v0.1.0` oncesi yol sizintilari boyle yakalandi).
Cikti MASKELIDIR: sir ilk 4 karakter + uzunluk, yol yalniz tur + uzunluk, e-posta yalniz alan adi. Kisisel yol/ad ekrana basilmaz.

NEDEN: sizan sir/yol/ad geri alinamaz (git gecmisi). BEDEL: yanlis alarm (dar `IZIN` tablosuyla yonetilir). GEVSETME: yalniz dar, gerekceli, denetci
onayli `IZIN` satiri (kural + dosya deseni + metin deseni); MiniMax lisans yetki adresi yalniz lisans belgelerinde. "Gecti" = bu kaba desenler yok; "gizlilik
tamam" demek degildir (adlar, takma adlar, resimdeki yuzler taranmaz).
Bu dosya ASCII'dir ve kendi kapisindan gecer: sahte sir/yol testte calisma aninda parcalardan uretilir.
"""
import re, os, fnmatch

BOYUT_TAVANI = 32 * 1024 * 1024   # bundan buyuk dosya taranamaz = bulgu (yesil gizlenmez)
IKILI_UZANTI = frozenset(('.png', '.jpg', '.jpeg', '.gif', '.webp', '.ico', '.bmp', '.zip', '.gz', '.7z', '.xz', '.bin', '.gguf', '.safetensors',
                          '.mp4', '.avi', '.mkv', '.webm', '.wav', '.mp3', '.flac', '.ogg', '.pyc', '.pdf', '.dll', '.exe', '.onnx', '.pt', '.pth', '.npy'))

# ---------------------------------------------------------------- kurallar
SIR = re.compile(
    r'\bsk-(?:ant-|proj-)?[A-Za-z0-9_-]{20,}'
    r'|\bAIza[0-9A-Za-z_-]{35}\b'
    r'|\bgh[pousr]_[A-Za-z0-9]{36,}\b|\bgithub_pat_[A-Za-z0-9_]{22,}\b'
    r'|\bhf_[A-Za-z0-9]{30,}\b|\bgsk_[A-Za-z0-9]{40,}\b|\bxox[abprs]-[A-Za-z0-9-]{10,}'
    r'|\bAKIA[0-9A-Z]{16}\b'
    r'|\b\d{8,10}:AA[A-Za-z0-9_-]{30,}\b'
    r'|-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----'
    r'|discord(?:app)?\.com/api/webhooks/\d+'
    r'|\b(?:api[_-]?key|secret|token|password|passwd)\s*[=:]\s*[\'"][A-Za-z0-9_\-./+=]{16,}[\'"]', re.I | re.A)

# Windows/Unix kullanici profil yolu: ad kismi yer tutucu degilse bulgu (yer tutucu ad ve %USERNAME% serbest; gercek ad, tek harf bile, bulgu).
YER_TUTUCU_AD = frozenset(('public', 'default', 'user', 'username', 'you', 'name', 'example', 'runner', 'runneradmin', 'ubuntu', 'shared', 'all users', 'yourname'))
YOL_PROFIL = re.compile(
    r'\b[A-Za-z]:[\\/]+(?:Users|Documents and Settings)[\\/]+(?P<ad1>[^\\/\s"\'`<>|*?]+)'
    r'|(?<![\w.])/(?:c|mnt/c)/Users/(?P<ad2>[^/\s"\'`<>|*?]+)'
    r'|(?<![\w.])/home/(?P<ad3>[A-Za-z0-9_.-]+)/'
    r'|(?<![\w.])/Users/(?P<ad4>[A-Za-z0-9_.-]+)/', re.A)
YOL_SURUCU = re.compile(r'(?<![\w`])[D-Z]:[\\/]+[A-Za-z0-9_]', re.A)         # D:..Z: bu makineye ozgu; C:\vt gibi kisa kok yer tutucu sayilir
YOL_KISA_AD = re.compile(r'[\\/][A-Za-z0-9_]{2,8}~[0-9][\\/]', re.A)         # 8.3 kisa ad (ornek ALEX25~1): kullanici adi sizdirir, kara listeyi atlatir
EPOSTA = re.compile(r'(?<![A-Za-z0-9])[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}\b', re.A)
EPOSTA_SERBEST_ALAN = re.compile(r'(?i)(?:^|\.)(?:example\.(?:com|org|net)|localhost|invalid|users\.noreply\.github\.com)$')
ZAMAN = re.compile(r'(?i)Europe/Is[t]anbul|\bUTC\s*\+\s*0?3\b|\bGMT\s*\+\s*0?3\b|\d\d:\d\d(?::\d\d)?\s*\+03:?00\b|T\d\d:\d\d(?::\d\d)?\+03:00|Turkey\s+time|T[u\u00fc]rkiye\s+saati', re.A)
YAMA_DATE = re.compile(r'^Date: .*?\s([+-]\d{4})\s*$')

# Dar istisnalar: (kural, dosya deseni, normalize eslesen metin regex'i ya da None, neden). Depo-geneli desen YASAK.
IZIN = (
    ('e_posta', 'docs/LISANS_UYARISI.md', r'^api@minimax\.io$', 'MiniMax H3 lisansinin yetki-talep adresi (lisans metninden alinti)'),
    ('e_posta', 'docs/LISANS_KABUL.txt', r'^api@minimax\.io$', 'ayni adres, lisans kabul metni'),
    ('e_posta', 'README.md', r'^api@minimax\.io$', 'ayni adres, ilk ekran lisans uyarisi'),
    ('e_posta', 'README.??.md', r'^api@minimax\.io$', 'ayni adres, ceviri'),
    ('e_posta', 'README.???.md', r'^api@minimax\.io$', 'ayni adres, ceviri'),
    ('e_posta', 'README.??-??.md', r'^api@minimax\.io$', 'ayni adres, ceviri (pt-BR, zh-CN)'),
    ('e_posta', 'NOTICE', r'^api@minimax\.io$', 'ayni adres, NOTICE'),
    ('e_posta', 'LICENSE', r'^api@minimax\.io$', 'ayni adres, LICENSE ek paragrafi'),
)
# Yama `Date:` borcu: bu yamalar `+0300` ile yayinlandi (v0.1.0/v0.1.1'de, tarihte kalir); kayit KARAR bekler (mimar yama basliklarini +0000 yapar
# ve tablodan siler, ya da kullanici kabul eder). Listede OLMAYAN her yama `+0000` olmak zorunda. Bu yama icin satir sayisi sabit degil: dosya adi yeter.
YAMA_DATE_BORC = frozenset()   # denetim_kayit: asagida doldurulur (kayit dosyasi `scripts/gizlilik_borc.txt`)
BORC_DOSYASI = 'scripts/gizlilik_borc.txt'


def _maske(kural, m, metin):
    if kural == 'sir':
        return '%s...(%d krk)' % (metin[:4], len(metin))
    if kural == 'kisisel_yol':
        ad = (m.group('ad1') or m.group('ad2') or m.group('ad3') or m.group('ad4')) if m.re is YOL_PROFIL else ''
        return 'profil yolu <ad: %d krk>' % len(ad) if ad else 'makineye ozgu yol (%d krk)' % len(metin)
    if kural == 'e_posta':
        return '*@%s' % metin.rsplit('@', 1)[-1].lower()
    return metin[:60]


def _izinli(rel, kural, normal):
    for k, glob, desen, _ in IZIN:
        if k == kural and fnmatch.fnmatchcase(rel, glob) and (desen is None or re.search(desen, normal)):
            return True
    return False


def _satir_bul(metin, rel, ikili_baslik, yeni, sayac):
    """Bir metin gorunumunu kurallardan gecirir; sayac[(rel,kural,maskeli,yer)] += 1."""
    for m in SIR.finditer(metin):
        yeni('sir', m, m.group())
    for m in YOL_PROFIL.finditer(metin):
        ad = (m.group('ad1') or m.group('ad2') or m.group('ad3') or m.group('ad4') or '')
        if ad.lower() in YER_TUTUCU_AD or ad[:1] in '<{%$':
            continue
        yeni('kisisel_yol', m, m.group())
    for m in YOL_KISA_AD.finditer(metin):
        yeni('kisisel_yol', m, m.group())
    if not ikili_baslik:   # ikili dosyada yalniz guclu kurallar (sir, profil yolu, kisa ad); kalanlar rastgele baytta yanlis alarm verir
        for m in YOL_SURUCU.finditer(metin):
            yeni('kisisel_yol', m, m.group())
        for m in EPOSTA.finditer(metin):
            tam = m.group().lstrip('-._%+').lower()
            yerel, alan = tam.rsplit('@', 1)
            if yerel == 'noreply' or yerel.endswith('+noreply') or EPOSTA_SERBEST_ALAN.search(alan):
                continue
            if _izinli(rel, 'e_posta', tam):
                continue
            yeni('e_posta', m, tam)
        for m in ZAMAN.finditer(metin):
            bas = metin.rfind(chr(10), 0, m.start()) + 1
            if rel.endswith('.patch') and metin.startswith('Date: ', bas):
                continue   # yama basligi ayri kuralda (yama_date): kayitli borc listesiyle
            yeni('zaman_izi', m, m.group())


def gorunumler(b, ikili):
    """(etiket, metin, ikili_mi, bayt_hizasi) listesi: UTF-8; BOM'lu UTF-16; BOM'suz NUL-yogun UTF-16 (cift ve tek hizali)."""
    out = []
    if b[:2] in (b'\xff\xfe', b'\xfe\xff'):
        out.append(('utf16', b.decode('utf-16', 'replace'), ikili, 0))
        return out
    out.append(('utf8', b.decode('utf-8', 'replace') if not ikili else b.decode('latin-1'), ikili, 1))
    nul = b.count(b'\0')
    if nul and (ikili or nul * 5 > len(b)):   # ikili: her zaman; metin: NUL > %20 ise UTF-16 sayilir (tek NUL'lu yama UTF-16 degildir)
        out.append(('utf16le', b[0::2].decode('latin-1'), True if ikili else False, 2))
        out.append(('utf16be', b[1::2].decode('latin-1'), True if ikili else False, 2))
    return out


def yama_date_borcu(c):
    """kayit dosyasi (bir yol satirda; # yorum) -> set. Dosya yoksa bos: borc yok demek."""
    try:
        t = c.bayt(BORC_DOSYASI).decode('utf-8', 'replace')
    except (OSError, KeyError):
        return set()
    return {s.strip() for s in t.splitlines() if s.strip() and not s.strip().startswith('#')}


def kapi_gizlilik(c, kisisel=()):
    bulgu, bilgi = [], []
    sayac = {}
    terimler = [t.strip().lower() for t in kisisel if len(t.strip()) >= 3]
    borc = yama_date_borcu(c)
    borc_gordu = set()
    for rel in c.dosyalar:
        if rel == BORC_DOSYASI:
            continue   # kayit dosyasi yama yollarini listeler; icerik kurala takilmaz (yalniz yol listesi)
        try:
            if os.path.getsize(os.path.join(c.kok, rel)) > BOYUT_TAVANI:
                bulgu.append('%s: dosya %d MB > %d MB tavani, taranamadi (yesil verilmez)' % (rel, os.path.getsize(os.path.join(c.kok, rel)) >> 20, BOYUT_TAVANI >> 20))
                continue
        except OSError:
            continue
        b = c.bayt(rel)
        ikili = os.path.splitext(rel)[1].lower() in IKILI_UZANTI
        for etiket, metin, ik, hiza in gorunumler(b, ikili):
            def yeni(kural, m, ham, _e=etiket, _h=hiza, _m=metin):
                yer = ('satir %d' % (_m.count('\n', 0, m.start()) + 1)) if _h < 2 and not ik else ('bayt %d' % (m.start() * (2 if _h == 2 else 1)))
                k = (rel, kural, _maske(kural, m, ham), yer if _h == 2 or ik else yer, _e if _e != 'utf8' else '')
                sayac[k] = sayac.get(k, 0) + 1
            _satir_bul(metin, rel, ik, yeni, sayac)
            if terimler and not ik:
                kucuk = metin.lower()
                for i, t in enumerate(terimler):
                    if t in kucuk:
                        sayac[(rel, 'kisisel_terim', 'terim #%d' % (i + 1), 'satir %d' % (kucuk.count('\n', 0, kucuk.index(t)) + 1), '')] = 1
            if rel.endswith('.patch') and etiket == 'utf8' and not ikili:
                for no, s in enumerate(metin.split('\n'), 1):
                    m = YAMA_DATE.match(s.rstrip('\r'))
                    if m and m.group(1) != '+0000':
                        if rel in borc:
                            borc_gordu.add(rel)
                        else:
                            bulgu.append('%s:%d yama Date: saat dilimi %s (+0000 olmali; yerel saat dilimi sizar)' % (rel, no, m.group(1)))
                        break
    for (rel, kural, maske, yer, etiket), n in sorted(sayac.items()):
        bulgu.append('%s:%s %s %s%s%s' % (rel, yer, kural, maske, (' [%s]' % etiket) if etiket else '', (' x%d' % n) if n > 1 else ''))
    if borc_gordu:
        bilgi.append('%d yamada Date: saat dilimi +0000 degil (kayitli borc, %s): mimar basliklari +0000 yapinca kayit silinir' % (len(borc_gordu), BORC_DOSYASI))
    for rel in sorted(borc - borc_gordu):
        bilgi.append('%s: kayitli yama Date: borcu gereksiz (artik +0000 ya da dosya yok): kayit satirini sil' % rel)
    return bulgu, bilgi
