"""init_image izinli klasor denetimi (yalniz stdlib; MCP paketi gerekmez, testte tek basina yuklenir).

Neden: init_image eskiden sureclerin okuyabildigi HER dosyayi motora resim olarak veriyordu; diskin herhangi bir
yerindeki bir dosya uretilen videonun icine girebilirdi (SECURITY.md). Bu modul isteyene dar bir kapi verir.
Why: init_image used to accept any readable file; this lets you restrict it to a folder (opt-in, default stays open).

Kural / Rule:
- VT_MCP_INIT_DIR yok ya da bos: ESKI DAVRANIS (acik). Varsayilan degismez (STANDART ilke 4).
- VT_MCP_INIT_DIR dolu: yalniz <ROOT>/girdi/ ve listedeki klasorler (os.pathsep ile ayrilir; goreli girdi ROOT'a gore).
  Tek klasore (yalniz <ROOT>/girdi/) kisitlamak icin: VT_MCP_INIT_DIR=girdi
- Kisitli kipte reddedilir: ".." parcasi, izinli klasorun ALTINDAKI sembolik baglar ve birlesim noktalari (junction),
  akis adi (":"), uzun-yol oneki ve UNC yollari, izinli klasorun disina cikan gercek yol.
- Sinir (durust): denetim ile motorun dosyayi acisi arasinda zaman farki vardir (TOCTOU); izinli klasoru yalniz
  guvendiginiz kisilerin yazabildigi bir yer yapin. Izinli klasorun KENDISI sembolik bag ise kullanicinin acik secimidir.
"""
import os
import stat
from pathlib import Path

# Windows yeniden-ayristirma etiketleri: sembolik bag ve birlesim noktasi (OneDrive/bulut etiketleri bilerek yok sayilir)
TAG_SYMLINK = 0xA000000C
TAG_MOUNT_POINT = 0xA0000003


def izinli_klasorler(root, deger):
    """None = acik kip (VT_MCP_INIT_DIR yok/bos). Aksi halde [<ROOT>/girdi, ...] (mutlak, tekrarsiz)."""
    if deger is None or not str(deger).strip():
        return None
    root = Path(root)
    out = [root / "girdi"]
    for parca in str(deger).split(os.pathsep):
        parca = parca.strip().strip('"')
        if not parca:
            continue
        p = Path(parca).expanduser()
        out.append(p if p.is_absolute() else root / p)
    gorulen, sonuc = set(), []
    for p in out:
        a = os.path.abspath(str(p))
        k = os.path.normcase(a)
        if k not in gorulen:
            gorulen.add(k)
            sonuc.append(Path(a))
    return sonuc


def _bag_mi(path):
    """Sembolik bag ya da birlesim noktasi mi (lstat; hedefe gitmez)."""
    try:
        st = os.lstat(path)
    except OSError:
        return False
    if stat.S_ISLNK(st.st_mode):
        return True
    return getattr(st, "st_reparse_tag", 0) in (TAG_SYMLINK, TAG_MOUNT_POINT)


def _altinda(yol, kok):
    """Sozcuk olarak yol, kok'un icinde mi (normcase; 'girdi_evil' 'girdi' sayilmaz)."""
    a, b = os.path.normcase(os.path.abspath(str(yol))), os.path.normcase(os.path.abspath(str(kok)))
    try:
        return os.path.commonpath([a, b]) == b
    except ValueError:  # farkli surucu
        return False


def goster(izinli, root):
    """Durum cikti icin: kisisel yol yok, <ROOT> maskeli."""
    if izinli is None:
        return {"mode": "open", "dirs": []}
    out = []
    for p in izinli:
        s = str(p)
        r = os.path.abspath(str(root))
        out.append("<ROOT>" + s[len(r):].replace(chr(92), "/") if _altinda(s, r) else "<outside ROOT>")
    return {"mode": "restricted", "dirs": out}


def yol_coz(init_image, root, izinli):
    """(Path, None) ya da (None, hata_metni). izinli None ise eski acik davranis (ayni iletiler)."""
    p = Path(init_image).expanduser()
    if izinli is None:
        p = (p if p.is_absolute() else Path(root) / p).resolve()  # uret.ps1 ROOT'ta calisir: goreli yol ROOT'a gore
        if not p.is_file():
            return None, f"init_image dosya degil ya da yok: {p}"
        return p, None
    ham = str(init_image).replace(chr(92), "/")
    ipucu = (" / init_image must be a file inside the allowed folder (default <ROOT>/girdi/, VT_MCP_INIT_DIR): "
             "put the file there and use the path the user gave you")
    if any(parca == ".." for parca in ham.split("/")):
        return None, "init_image yolunda '..' olamaz" + ipucu
    if ham.startswith("//") or ham.startswith("/?/") or ham.startswith("/./"):
        return None, "init_image UNC/aygit yolu olamaz" + ipucu
    if p.drive and not p.root:  # surucu-goreli (C:dosya): pathlib sessizce birlestirirdi, belirsiz: reddet
        return None, "init_image surucu-goreli yol olamaz" + ipucu
    aday = p if p.is_absolute() else Path(root) / p
    aday = Path(os.path.abspath(str(aday)))
    kok = next((k for k in izinli if _altinda(aday, k)), None)
    if kok is None:
        return None, "init_image izinli klasorlerin disinda" + ipucu
    # kok'un ALTINDAKI her parca: akis adi yok, sembolik bag/junction yok
    rel = os.path.relpath(str(aday), str(kok))
    gecerli = kok
    for parca in ([] if rel == "." else rel.replace(chr(92), "/").split("/")):
        if ":" in parca:
            return None, "init_image yolunda ':' (akis adi) olamaz" + ipucu
        gecerli = gecerli / parca
        if _bag_mi(gecerli):
            return None, "init_image yolunda sembolik bag ya da birlesim noktasi var" + ipucu
    gercek = Path(os.path.realpath(str(aday)))
    if not _altinda(gercek, os.path.realpath(str(kok))):
        return None, "init_image gercek yolu izinli klasorun disina cikiyor" + ipucu
    if not gercek.is_file():
        return None, "init_image dosya degil ya da yok (izinli klasorde)" + ipucu
    return gercek, None
