#!/usr/bin/env python3
"""Karsilama yorumu: yeni acilan issue ve PR'a bir kez, sabit, sicak ama kurumsal bir yorum metni uretir (stdlib, ag yok).

Kullanici karari (2026-11-21): "Karsilama yapmaliyiz ... tespit edebiliyorsak diline gore, edemiyorsak Ingilizce, Turkce."

  python -I scripts/karsilama.py                      # GITHUB_EVENT_PATH olayindan yorum govdesini stdout'a yazar; atlanacaksa bos
  python -I scripts/karsilama.py --numara             # yorum atilacaksa issue/PR numarasini yazar, atlanacaksa bos
  python -I scripts/karsilama.py --yazar              # yorum atilacaksa yazar adini (dogrulanmis) yazar, atlanacaksa bos
  python -I scripts/karsilama.py --yorumlar DOSYA     # DOSYA'da gizli isaret varsa (ikinci kez) govde bos
  KARSILAMA_KONUM="..." ya da --konum "..."           # yazarin herkese acik profil konumu (yalniz ipucu; agi is akisi cagirir)

Ne yapar / yapmaz:
  - Yalniz GITHUB_EVENT_PATH dosyasini okur; ag yok, dosya yazmaz, gizli degisken kullanmaz.
  - Yorum SABIT sablondur. Degisken yalniz @login (dogrulanmis), #numara ve tur (issue/PR). Yazarin basligi ve govdesi
    HICBIR yerde ciktiya girmez: yalniz dil secimi icin okunur (dis metin veridir, talimat degildir).
  - Soz, tarih, teknik iddia yok (STANDART ilke 1: hedef, soz degil).
  - Dil: yazarin serbest metninden ipucu skoru. Ingilizce yazdiysa yalniz Ingilizce; dili bulduysa Ingilizce + o dil;
    emin degilse Ingilizce + Turkce. Yanlis dile yazmaktansa emin olmamayi secer (esikler asagida, testleri tests/denetim/test_karsilama.py).
  - Dil sirasi: (1) yazarin serbest metni; (2) metin yetmezse profil konumu (ulke/sehir adi -> dil tablosu KONUM); (3) ikisi de yoksa EN+TR.
    Konum serbest metindir ve cogu zaman bos: yalniz ipucu, yalniz tabloya bakilir. Konum ya da ulke ADI yoruma ASLA yazilmaz (gizlilik).
    Bu betikte ag yok: konumu is akisi `gh api users/<yazar>` ile alip ortam degiskeniyle verir.
  - Atlanir (yorum yok): bot (tur Bot ya da [bot] ile biten ad), depo sahibi, OWNER iliskisi, `opened` disi eylem.

Kit notu: depoya ozgu tek sey MARKER ve SAHIPLER; baska depoda bu ikisini degistirmek yeter.
Kaynak dosya kasitli olarak kod noktalarini TAM SAYI olarak yazar (kacis dizisi yazma araclarinda gercek karaktere donusur).
"""
import argparse
import json
import os
import re
import sys
import unicodedata

MARKER = "<!-- vt-karsilama -->"
SAHIPLER = frozenset(("alexturkey",))
LOGIN = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})")
METIN_TAVANI = 20000   # dil secimi icin okunacak en fazla karakter (regex maliyeti sinirli)

# ---------------------------------------------------------------- yazi sistemi araliklari (kod noktasi)
HAN = ((0x4E00, 0x9FFF), (0x3400, 0x4DBF))
KANA = ((0x3040, 0x30FF), (0x31F0, 0x31FF))
KIRIL = ((0x0400, 0x04FF),)
ARAP = ((0x0600, 0x06FF), (0x0750, 0x077F))
DEVA = ((0x0900, 0x097F),)
RUS_HARF = ((0x0410, 0x044F), (0x0401, 0x0401), (0x0451, 0x0451))   # Rusca alfabe; disindaki Kiril harfi (Ukrayna, Sirp...) Rusca sayilmaz
ARAP_HARF = ((0x0621, 0x064A),)                                    # Arapca harfler; disindaki (Fars/Urdu: pe, che, gaf, kef...) Arapca sayilmaz
MIN_KUME = 3        # Han/Kana disinda bir yazi sisteminde en az harf
MIN_CJK = 2         # Han/Kana bilgi yogun: 2 karakter yeter
PAY = 0.25          # yazi sistemi, harflerin en az bu kadari olmali

# ---------------------------------------------------------------- Latin yazili diller: kelime ipuclari (yalniz o dile ozgu ya da baskin)
# Ortak (iki dilde birden yaygin) kelimeler kasitli yok: para, por, que, no, es, un, la, de, en, com...
KELIME = {
    "tr": "ve bir bu için ile değil olarak çok nasıl merhaba selam teşekkürler teşekkür hata çalışmıyor çalışıyor oluyor yok ben daha gibi kadar sonra lütfen kart bilgisayar denedim sürüm neden ama".split(),
    "es": "el los las una con hola gracias funciona tengo pero estoy cuando también cómo qué hay muy esto del tarjeta puedo necesito archivo versión porque".split(),
    "pt": "não uma você voce obrigado obrigada olá tenho mas quando também muito com já são ao erro placa rodar arquivo isso isto pra aqui agora ainda ele ela".split(),
    "de": "und nicht eine einen mit für ich ist das der bitte danke hallo fehler aber wenn kann habe funktioniert wird auf auch noch nur wie ein zu bei von dass sich meine mein grafikkarte".split(),
    "fr": "les une pour avec dans mais pas est des sur bonjour merci ça très fonctionne je nous vous où carte erreur problème".split(),
    "id": "yang dan tidak untuk dengan saya ini itu ada tetapi bisa gagal terima kasih halo kartu bagaimana sudah belum pada dari adalah atau karena tolong mohon apakah kalau jika masih sedang mengapa".split(),
    "vi": "và không của là cho tôi bị lỗi với này được một các những khi nhưng xin chào cảm ơn bạn đã để".split(),
    "en": "the and is are was with this that it to have has my not when but for you can does doesn't please thanks thank of be from if how what why get got fails failed works work don't hi hello".split(),
}
# Dile ozgu karakterler (her bulunuşu 1 puan); kod noktasi araliklari
KARAKTER = {
    "tr": ((0x011F, 0x011F), (0x015F, 0x015F), (0x0131, 0x0131), (0x0130, 0x0130)),         # g-breve, s-cedilla, dotless i, I-dot
    "es": ((0x00F1, 0x00F1), (0x00BF, 0x00BF), (0x00A1, 0x00A1)),                           # n-tilde, ters soru ve unlem
    "pt": ((0x00E3, 0x00E3), (0x00F5, 0x00F5)),                                             # a-tilde, o-tilde
    "de": ((0x00DF, 0x00DF), (0x00E4, 0x00E4)),                                             # sharp s, a-umlaut
    "fr": ((0x00E8, 0x00E8), (0x00F9, 0x00F9), (0x0153, 0x0153)),                           # e-grave, u-grave, oe
    "vi": ((0x0103, 0x0103), (0x01A1, 0x01A1), (0x01B0, 0x01B0), (0x0111, 0x0111), (0x1EA0, 0x1EF9)),
    "id": (),
    "en": (),
}
MIN_LATIN = 3       # kazanan dilin en az puani
KAT = 2             # kazanan, ikinciden en az bu kat puan almali (es/pt gibi komsu dillerde yanlis secimi onler)

# ---------------------------------------------------------------- sabit metinler (issue, PR); {login} ve {n} disinda degisken yok
METIN = {
    "en": (
        "Hi @{login}, thank you for taking the time to open issue #{n}. We read every report. If this is a bug report, the output of `tani.cmd` helps us see your setup (optional).",
        "Hi @{login}, thank you for your pull request #{n}. Automated checks will run on it and a maintainer will review it.",
    ),
    "tr": (
        "Merhaba @{login}, #{n} numaralı konuyu (issue) açtığınız için teşekkür ederiz. Her bildirimi okuyoruz. Bir hata bildiriyorsanız `tani.cmd` çıktısı kurulumunuzu anlamamıza yardımcı olur (isteğe bağlı).",
        "Merhaba @{login}, #{n} numaralı çekme isteğiniz (PR) için teşekkür ederiz. Otomatik kontroller çalışacak ve bir bakımcı inceleyecek.",
    ),
    "es": (
        "Hola @{login}, gracias por dedicar tu tiempo a abrir el issue #{n}. Leemos todos los reportes. Si es un reporte de error, la salida de `tani.cmd` nos ayuda a ver tu configuración (opcional).",
        "Hola @{login}, gracias por tu pull request #{n}. Se ejecutarán comprobaciones automáticas y un mantenedor lo revisará.",
    ),
    "pt": (
        "Olá @{login}, obrigado por dedicar seu tempo a abrir a issue #{n}. Lemos todos os relatos. Se for um relato de erro, a saída do `tani.cmd` nos ajuda a entender a sua configuração (opcional).",
        "Olá @{login}, obrigado pelo seu pull request #{n}. As verificações automáticas vão rodar e um mantenedor vai revisá-lo.",
    ),
    "de": (
        "Hallo @{login}, danke, dass du dir die Zeit genommen hast, das Issue #{n} zu eröffnen. Wir lesen jeden Bericht. Falls es ein Fehlerbericht ist, hilft uns die Ausgabe von `tani.cmd`, deine Umgebung zu verstehen (optional).",
        "Hallo @{login}, danke für deinen Pull Request #{n}. Automatische Prüfungen werden ausgeführt, und ein Maintainer wird ihn prüfen.",
    ),
    "fr": (
        "Bonjour @{login}, merci d'avoir pris le temps d'ouvrir l'issue #{n}. Nous lisons chaque signalement. S'il s'agit d'un bogue, la sortie de `tani.cmd` nous aide à comprendre votre configuration (facultatif).",
        "Bonjour @{login}, merci pour votre pull request #{n}. Des vérifications automatiques vont s'exécuter, puis un mainteneur la relira.",
    ),
    "ru": (
        "Здравствуйте, @{login}! Спасибо, что нашли время открыть issue #{n}. Мы читаем каждое обращение. Если это сообщение об ошибке, вывод `tani.cmd` поможет нам понять вашу конфигурацию (по желанию).",
        "Здравствуйте, @{login}! Спасибо за pull request #{n}. Автоматические проверки запустятся, после чего один из сопровождающих его рассмотрит.",
    ),
    "zh": (
        "你好 @{login},感谢你抽出时间提交 issue #{n}。我们会阅读每一份反馈。如果这是错误报告,附上 `tani.cmd` 的输出能帮助我们了解你的环境(可选)。",
        "你好 @{login},感谢你提交 pull request #{n}。系统会自动运行检查,随后由维护者进行审阅。",
    ),
    "ar": (
        "مرحبًا @{login}، شكرًا لك على وقتك في فتح المشكلة #{n} (issue). نقرأ كل بلاغ. إذا كان هذا بلاغًا عن خطأ، فإن مخرجات `tani.cmd` تساعدنا على فهم إعدادات جهازك (اختياري).",
        "مرحبًا @{login}، شكرًا لك على طلب الدمج #{n} (pull request). ستُشغَّل فحوصات تلقائية، ثم يراجعه أحد القائمين على المشروع.",
    ),
    "hi": (
        "नमस्ते @{login}, समय निकालकर issue #{n} खोलने के लिए धन्यवाद। हम हर रिपोर्ट पढ़ते हैं। अगर यह बग रिपोर्ट है, तो `tani.cmd` का आउटपुट हमें आपका सेटअप समझने में मदद करता है (वैकल्पिक)।",
        "नमस्ते @{login}, pull request #{n} के लिए धन्यवाद। स्वचालित जाँच चलेगी और उसके बाद एक मेंटेनर इसकी समीक्षा करेगा।",
    ),
    "id": (
        "Halo @{login}, terima kasih sudah meluangkan waktu membuka issue #{n}. Kami membaca setiap laporan. Jika ini laporan bug, keluaran `tani.cmd` membantu kami memahami pengaturan Anda (opsional).",
        "Halo @{login}, terima kasih atas pull request #{n}. Pemeriksaan otomatis akan berjalan, lalu seorang maintainer akan meninjaunya.",
    ),
    "vi": (
        "Xin chào @{login}, cảm ơn bạn đã dành thời gian mở issue #{n}. Chúng tôi đọc mọi báo cáo. Nếu đây là báo cáo lỗi, kết quả của `tani.cmd` sẽ giúp chúng tôi hiểu cấu hình của bạn (không bắt buộc).",
        "Xin chào @{login}, cảm ơn bạn đã gửi pull request #{n}. Các bước kiểm tra tự động sẽ chạy, sau đó một người bảo trì sẽ xem xét.",
    ),
    "ja": (
        "@{login} さん、こんにちは。お時間をいただき issue #{n} を作成してくださりありがとうございます。すべての報告に目を通しています。不具合の報告であれば、`tani.cmd` の出力があると環境の把握に役立ちます(任意)。",
        "@{login} さん、こんにちは。pull request #{n} をありがとうございます。自動チェックが実行され、その後メンテナーが確認します。",
    ),
}
DILLER = tuple(METIN)

# ---------------------------------------------------------------- profil konumu -> dil (yalniz ipucu; sozcuk siniri eslesmesi, aksan ve buyuk/kucuk harf yok sayilir)
# Cakisma (ayni konumda iki farkli dil) = emin degil. Ingilizce ulkeler 'en' verir: yalniz Ingilizce yorum. Hindistan da 'en' (kullanici karari).
KONUM = {
    "tr": "turkey turkiye istanbul ankara izmir bursa antalya adana konya".split(),
    "es": "spain espana madrid barcelona valencia sevilla mexico argentina colombia chile peru venezuela ecuador uruguay bogota lima".split(),
    "pt": "brazil brasil portugal lisboa lisbon porto".split() + ["sao paulo", "rio de janeiro", "belo horizonte", "brasilia", "curitiba"],
    "de": "germany deutschland berlin munich munchen hamburg koln cologne frankfurt austria osterreich wien vienna".split(),
    "fr": "france paris lyon marseille toulouse".split(),
    "ru": ["russia", "russian federation", "moscow", "saint petersburg", "novosibirsk", "россия", "москва"],
    "zh": "china beijing shanghai shenzhen guangzhou chengdu hangzhou".split() + ["中国", "北京", "上海", "深圳"],
    "ja": "japan tokyo osaka kyoto yokohama nagoya".split() + ["日本", "東京", "大阪"],
    "id": "indonesia jakarta bandung surabaya yogyakarta".split(),
    "vi": ["vietnam", "viet nam", "hanoi", "ho chi minh", "saigon", "da nang"],
    "ar": "egypt cairo uae dubai riyadh jeddah jordan amman morocco casablanca iraq baghdad kuwait qatar doha lebanon beirut".split() + ["saudi arabia", "saudi", "united arab emirates", "abu dhabi", "مصر", "السعودية", "الإمارات"],
    "en": "usa america texas california london england uk britain canada australia sydney melbourne ireland dublin india bangalore bengaluru mumbai delhi hyderabad pune chennai".split() + ["united states", "united kingdom", "new york", "new zealand", "san francisco", "seattle"],
}
KONUM_TAVANI = 200


def _konum_norm(metin):
    metin = unicodedata.normalize("NFKD", (metin or "")[:KONUM_TAVANI])
    metin = "".join(c for c in metin if not unicodedata.combining(c))
    metin = metin.replace("ı", "i").casefold()      # noktasiz i -> i
    return " " + re.sub(r"[\W_]+", " ", metin).strip() + " "


def dil_konum(konum):
    """Profil konumundan dil kodu ('en' dahil) ya da None (bos, bilinmeyen, cakisan). Konum metni hicbir yere yazilmaz."""
    n = _konum_norm(konum)
    bulunan = set()
    for d, anahtarlar in KONUM.items():
        for k in anahtarlar:
            if k.isascii():
                if " %s " % k in n:
                    bulunan.add(d)
            elif _konum_norm(k).strip() in n:
                bulunan.add(d)
    return next(iter(bulunan)) if len(bulunan) == 1 else None



class Hata(Exception):
    pass


# ---------------------------------------------------------------- dil secimi
def _icinde(cp, araliklar):
    for a, b in araliklar:
        if a <= cp <= b:
            return True
    return False


def serbest_metin(baslik, govde):
    """Yazarin kendi yazdigi metin: sablon basliklari (' / ' iceren satir), checkbox, sablon yonerge satirlari, kod, URL ve HTML yorumu cikarilir."""
    govde = re.sub(r"<!--.*?(?:-->|\Z)", " ", govde or "", flags=re.S)
    govde = re.sub(r"(```|~~~).*?(?:\1|\Z)", " ", govde, flags=re.S)
    govde = re.sub(r"`[^`\n]*`", " ", govde)
    govde = re.sub(r"https?://\S+", " ", govde)
    satirlar = []
    for s in govde.splitlines():
        t = s.strip()
        if " / " in s or re.match(r"[-*]\s*\[[ xX]\]", t):
            continue
        if re.search(r"\[(measured|ölçtüm)\]", s) or t in ("_No response_", "_Yanıt yok_"):
            continue
        satirlar.append(s)
    return ((baslik or "") + "\n" + "\n".join(satirlar))[:METIN_TAVANI]


def _yazi_sayimi(metin):
    """Harfleri yazi sistemine gore say."""
    c = {"han": 0, "kana": 0, "kiril": 0, "arap": 0, "deva": 0, "diger": 0, "latin": 0,
         "kiril_yabanci": 0, "arap_yabanci": 0}
    for ch in metin:
        if not ch.isalpha():
            continue
        cp = ord(ch)
        if cp < 0x250 or 0x1E00 <= cp <= 0x1EFF:
            c["latin"] += 1
        elif _icinde(cp, HAN):
            c["han"] += 1
        elif _icinde(cp, KANA):
            c["kana"] += 1
        elif _icinde(cp, KIRIL):
            c["kiril"] += 1
            if not _icinde(cp, RUS_HARF):
                c["kiril_yabanci"] += 1
        elif _icinde(cp, ARAP):
            c["arap"] += 1
            if not _icinde(cp, ARAP_HARF):
                c["arap_yabanci"] += 1
        elif _icinde(cp, DEVA):
            c["deva"] += 1
        else:
            c["diger"] += 1
    return c


def _latin_puani(metin):
    kucuk = metin.replace("İ", "i").replace("’", "'").lower()
    kelimeler = re.findall(r"[^\W\d_]+", kucuk)
    puan = {}
    for d, liste in KELIME.items():
        kume = frozenset(liste)
        p = sum(1 for k in kelimeler if k in kume)
        p += sum(1 for ch in metin if _icinde(ord(ch), KARAKTER[d])) if KARAKTER[d] else 0
        puan[d] = p
    return puan


def dil_tahmin(metin):
    """Serbest metinden dil kodu: 'en' (emin Ingilizce), METIN'deki baska bir kod, ya da None (emin degil)."""
    metin = unicodedata.normalize("NFC", metin)
    c = _yazi_sayimi(metin)
    harf = sum(c[k] for k in ("han", "kana", "kiril", "arap", "deva", "diger", "latin"))
    if harf == 0:
        return None
    cjk = c["han"] + c["kana"]
    if cjk >= MIN_CJK and cjk >= PAY * harf:
        return "ja" if c["kana"] >= 2 else "zh"
    for ad, dil, yabanci in (("kiril", "ru", c["kiril_yabanci"]), ("arap", "ar", c["arap_yabanci"]), ("deva", "hi", 0)):
        if c[ad] >= MIN_KUME and c[ad] >= PAY * harf:
            return None if yabanci else dil
    if c["diger"] >= MIN_KUME and c["diger"] >= PAY * harf:
        return None   # Korece, Tayca, Yunanca...: listede yok, emin olunmaz
    puan = _latin_puani(metin)
    en = puan.pop("en")
    d, p = max(puan.items(), key=lambda x: x[1])
    ikinci = max(v for k, v in puan.items() if k != d)
    if p >= MIN_LATIN and p > en and p >= KAT * ikinci:
        return d
    if en >= MIN_LATIN and en >= KAT * p:
        return "en"
    return None


def diller_kaynak(baslik, govde, konum=None):
    """(diller, kaynak): once yazarin metni, yetmezse profil konumu, yoksa EN+TR. kaynak: 'metin' | 'konum' | 'varsayilan'."""
    d = dil_tahmin(serbest_metin(baslik, govde))
    kaynak = "metin"
    if d is None:
        d = dil_konum(konum)
        kaynak = "konum" if d else "varsayilan"
    if d == "en":
        return ["en"], kaynak
    if d in METIN:
        return ["en", d], kaynak
    return ["en", "tr"], "varsayilan"


def diller_sec(baslik, govde, konum=None):
    """Yorumda kullanilacak diller: ['en'] | ['en', xx] | ['en', 'tr'] (emin degilse)."""
    return diller_kaynak(baslik, govde, konum)[0]


# ---------------------------------------------------------------- olay ve govde
def olay_bilgisi(ev):
    """Olaydan (tur, login, numara, baslik, govde) ya da yorum atilmayacaksa None. Gecersiz olayda Hata."""
    if not isinstance(ev, dict) or ev.get("action") != "opened":
        return None
    if isinstance(ev.get("pull_request"), dict):
        tur, nesne = "pr", ev["pull_request"]
    elif isinstance(ev.get("issue"), dict) and not ev["issue"].get("pull_request"):
        tur, nesne = "issue", ev["issue"]
    else:
        return None
    kullanici = nesne.get("user") if isinstance(nesne.get("user"), dict) else {}
    login = str(kullanici.get("login") or "")
    if kullanici.get("type") == "Bot" or login.lower().endswith("[bot]"):
        return None
    depo = ev.get("repository") if isinstance(ev.get("repository"), dict) else {}
    sahip = str((depo.get("owner") or {}).get("login") or "").lower() if isinstance(depo.get("owner"), dict) else ""
    if login.lower() in SAHIPLER or (sahip and login.lower() == sahip) or nesne.get("author_association") in ("OWNER", "MEMBER", "COLLABORATOR"):
        return None
    if not LOGIN.fullmatch(login):
        raise Hata("yazar adi gecersiz")
    n = nesne.get("number")
    if not isinstance(n, int) or isinstance(n, bool) or n <= 0:
        raise Hata("numara gecersiz")
    return tur, login, n, str(nesne.get("title") or ""), str(nesne.get("body") or "")


# zh/ja metinleri kaynakta ASCII noktalama ile yazilir (PR kapisinin tam-genislik-karakter kurali kodda her ornegi gorsel taklit sayar);
# yorum uretilirken yerel tam-genislik noktalamaya cevrilir.
TAM_GENISLIK = {0x2C: 0xFF0C, 0x28: 0xFF08, 0x29: 0xFF09}


def metin_yap(d, tur, login, n):
    s = METIN[d][0 if tur == "issue" else 1].replace("{login}", login).replace("{n}", str(n))
    return s.translate(TAM_GENISLIK) if d in ("zh", "ja") else s


def govde_yap(tur, login, n, diller):
    bloklar = [metin_yap(d, tur, login, n) for d in diller]
    return MARKER + "\n" + "\n\n---\n\n".join(bloklar) + "\n"


def zaten_var(yorumlar_metni):
    """Daha once yazilmis yorumlarda gizli isaret var mi (ikinci kez yazmama)."""
    return MARKER in (yorumlar_metni or "")


def _yaz(metin):
    sys.stdout.buffer.write(metin.encode("utf-8"))
    sys.stdout.buffer.flush()


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--numara", action="store_true", help="yorum atilacaksa numarayi yaz, atlanacaksa bos")
    p.add_argument("--yazar", action="store_true", help="yorum atilacaksa dogrulanmis yazar adini yaz, atlanacaksa bos")
    p.add_argument("--konum", help="yazarin profil konumu (varsayilan: KARSILAMA_KONUM ortam degiskeni); yalniz dil ipucu")
    p.add_argument("--yorumlar", help="onceki yorum metinlerinin dosyasi; gizli isaret varsa govde bos")
    p.add_argument("--olay", help="olay JSON yolu (varsayilan: GITHUB_EVENT_PATH)")
    a = p.parse_args(argv)
    yol = a.olay or os.environ.get("GITHUB_EVENT_PATH", "")
    try:
        if not yol:
            raise Hata("GITHUB_EVENT_PATH yok")
        with open(yol, encoding="utf-8") as f:
            ev = json.load(f)
        bilgi = olay_bilgisi(ev)
    except (Hata, OSError, ValueError) as e:
        sys.stderr.write("karsilama: HATA %s\n" % e)
        return 1
    if bilgi is None:
        sys.stderr.write("karsilama: atlandi (bot, sahip ya da opened disi)\n")
        return 0
    tur, login, n, baslik, govde = bilgi
    if a.numara:
        _yaz("%d\n" % n)
        return 0
    if a.yazar:
        _yaz(login + chr(10))
        return 0
    if a.yorumlar:
        try:
            with open(a.yorumlar, encoding="utf-8", errors="replace") as f:
                if zaten_var(f.read()):
                    sys.stderr.write("karsilama: atlandi (bu konuda karsilama zaten var)\n")
                    return 0
        except OSError as e:
            sys.stderr.write("karsilama: HATA yorum dosyasi okunamadi: %s\n" % e)
            return 1
    konum = a.konum if a.konum is not None else os.environ.get("KARSILAMA_KONUM", "")
    diller, kaynak = diller_kaynak(baslik, govde, konum)
    sys.stderr.write("karsilama: %s #%d diller=%s kaynak=%s\n" % (tur, n, "+".join(diller), kaynak))
    _yaz(govde_yap(tur, login, n, diller))
    return 0


if __name__ == "__main__":
    sys.exit(main())
