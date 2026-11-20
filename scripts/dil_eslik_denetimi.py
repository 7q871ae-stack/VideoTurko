"""Dil esligi denetimi (README ceviri parity check): the 29 README.<lang>.md files against README.md.

Stdlib only, no network. Run from anywhere; safest form (isolated, UTF-8):

    python -I -X utf8 scripts/dil_eslik_denetimi.py            # report; warnings do not fail
    python -I -X utf8 scripts/dil_eslik_denetimi.py --kati     # warnings count as errors
    python -I -X utf8 scripts/dil_eslik_denetimi.py --json     # machine-readable
    python -I -X utf8 scripts/dil_eslik_denetimi.py --dil tr   # one language
    python -I -X utf8 scripts/dil_eslik_denetimi.py --damga    # dry run: which stamps would change
    python -I -X utf8 scripts/dil_eslik_denetimi.py --damga --yaz   # rewrite the stamp (only after translations are synced)

Language list, tiers and Unicode allowances live in scripts/dil_profili.json (single source of truth).

Checks (each has an id printed in the result):
  DOSYA     every profile language has README.<lang>.md, no extra README.*.md, language bar links agree. ERROR
  DAMGA     last stamp line `<!-- i18n-source: README.md sha256:<12 hex> -->` equals sha256(README.md)[:12].
            missing stamp = ERROR; stale: tier A warning (error with --kati), tier B warning, tier C info.
  YAPI      H2/H3 count, table rows, fenced blocks equal to README.md; fenced block CONTENT byte-identical.
            WARNING (error with --kati).
  BELIRTEC  multiset of backtick spans, URLs, @users, #N references, ASCII numbers
            equals README.md (numbers: every README.md number must exist in the translation; native digits are
            normalised to ASCII first). WARNING (error with --kati).
  ETIKET    count of bracketed evidence labels (`[measured: ...]`) equals README.md. WARNING (error with --kati).
  KARAKTER  NUL/control characters, bidi embedding/override (U+202A-202E, U+2066-2069): ERROR in every file.
            ZWNJ/ZWJ and LRM/RLM only in languages the profile allows. ERROR.
  KODLAMA   the script forces UTF-8 on stdout; a crash is reported as exit 6, never as green.

Exit codes: 0 clean or warnings only, 1 error, 3 profile missing/invalid, 6 the gate itself could not run.
Honest limit: a changed prose sentence in an old translation can pass BELIRTEC; the stamp, the changed-sentence
ledger and an independent reviewer catch that, this script alone does not.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

VARSAYILAN_KOK = Path(__file__).resolve().parents[1]
DAMGA_RE = re.compile(rb"<!--\s*i18n-source:\s*README\.md\s+sha256:([0-9a-f]{12})\s*-->")
RTL_SARMAL = re.compile(r'^\s*(<div dir="rtl">|</div>)\s*$')
BIDI_YASAK = set(range(0x202A, 0x202F)) | set(range(0x2066, 0x206A))
KONTROL_OK = {0x09, 0x0A, 0x0D}
URL_RE = re.compile(r"https?://[^\s)>\]`\"']+")
KULLANICI_RE = re.compile(r"(?<![\w@])@[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?")
ISSUE_RE = re.compile(r"(?<![\w&])#\d+")
SAYI_RE = re.compile(r"\d+")
BAGLANTI_RE = re.compile(r"\[[^\]\n]*\]\([^)\s]*\)")
ETIKET_RE = re.compile(r"\[[^\]\n]*\]")
KOD_ARALIK_RE = re.compile(r"`[^`\n]+`")
YORUM_RE = re.compile(r"<!--.*?-->", re.S)
TARIH_RE = re.compile(r"\d{4}-\d{2}-\d{2}")  # ISO dates are localised in translations


class Profil:
    def __init__(self, veri: dict) -> None:
        self.ana: str = veri["ana"]
        self.diller: dict[str, dict] = veri["diller"]
        self.zwj_izinli = set(veri.get("zwj_izinli", []))
        self.lrm_izinli = set(veri.get("lrm_izinli", []))
        self.rozet_oneki: str = veri.get("rozet_url_oneki", "")  # static tier badge allowed on tier B/C files


def profil_yukle(kok: Path) -> Profil:
    yol = kok / "scripts" / "dil_profili.json"
    veri = json.loads(yol.read_text(encoding="utf-8"))
    for kod, ayar in veri["diller"].items():
        if ayar.get("tier") not in ("A", "B", "C"):
            raise ValueError(f"{kod}: tier A/B/C olmali")
    return Profil(veri)


def ozet(veri: bytes) -> str:
    return hashlib.sha256(veri.replace(b"\r\n", b"\n")).hexdigest()[:12]


def ascii_rakam(metin: str) -> str:
    return "".join(str(unicodedata.digit(c)) if c.isdigit() and not c.isascii() else c for c in metin)


def ayristir(satirlar: list[str], rtl: bool) -> dict:
    """Split a markdown file into structure facts and fence-free text."""
    kod_bloklari: list[str] = []
    duz: list[str] = []
    h2 = h3 = tablo = 0
    mevcut: list[str] | None = None
    for satir in satirlar:
        if satir.lstrip().startswith("```"):
            if mevcut is None:
                mevcut = []
            else:
                kod_bloklari.append("\n".join(mevcut))
                mevcut = None
            continue
        if mevcut is not None:
            mevcut.append(satir)
            continue
        if rtl and RTL_SARMAL.match(satir):
            continue
        duz.append(satir)
        if re.match(r"##\s+\S", satir):
            h2 += 1
        elif re.match(r"###\s+\S", satir):
            h3 += 1
        elif satir.lstrip().startswith("|"):
            tablo += 1
    if mevcut is not None:  # unterminated fence counts as a block so the count differs
        kod_bloklari.append("\n".join(mevcut))
    metin = "\n".join(duz)
    return {"h2": h2, "h3": h3, "tablo": tablo, "kod": kod_bloklari, "metin": metin}


def belirecler(metin: str) -> dict[str, Counter]:
    metin = TARIH_RE.sub(" ", ascii_rakam(YORUM_RE.sub(" ", metin)))
    kodlar = Counter(KOD_ARALIK_RE.findall(metin))
    govde = KOD_ARALIK_RE.sub(" ", metin)
    urller = Counter(u.rstrip(".,;:") for u in URL_RE.findall(govde))
    govde_u = URL_RE.sub(" ", govde)
    return {
        "kod": kodlar,
        "url": urller,
        "kullanici": Counter(KULLANICI_RE.findall(govde_u)),
        "issue": Counter(ISSUE_RE.findall(govde_u)),
        "sayi": Counter(SAYI_RE.findall(ISSUE_RE.sub(" ", KULLANICI_RE.sub(" ", govde_u)))),
    }


def etiket_sayisi(metin: str) -> int:
    govde = KOD_ARALIK_RE.sub(" ", BAGLANTI_RE.sub(" ", YORUM_RE.sub(" ", metin)))
    return len(ETIKET_RE.findall(govde))


def fark_ozeti(a: Counter, b: Counter, kisit: int = 3, yalniz_eksik: bool = False) -> str:
    eksik = list((a - b).elements())[:kisit]
    fazla = [] if yalniz_eksik else list((b - a).elements())[:kisit]
    parca = []
    if eksik:
        parca.append("missing " + ", ".join(repr(x[:40]) for x in eksik))
    if fazla:
        parca.append("extra " + ", ".join(repr(x[:40]) for x in fazla))
    return "; ".join(parca)


class Denetim:
    def __init__(self, kok: Path, profil: Profil, kati: bool, tek_dil: str | None) -> None:
        self.kok, self.profil, self.kati, self.tek_dil = kok, profil, kati, tek_dil
        self.kayitlar: list[dict] = []
        ana_yol = kok / profil.ana
        self.ana_bayt = ana_yol.read_bytes() if ana_yol.is_file() else b""
        self.ana_ozet = ozet(self.ana_bayt)
        ana_metin = self.ana_bayt.decode("utf-8", errors="replace")
        self.ana = ayristir(ana_metin.splitlines(), rtl=False)
        self.ana_bel = belirecler(self.ana["metin"])
        self.ana_etiket = etiket_sayisi(self.ana["metin"])

    def ekle(self, dil: str, kapi: str, duzey: str, ileti: str) -> None:
        """duzey: HATA, UYARI, BILGI. UYARI becomes HATA under --kati when the check is a soft one."""
        self.kayitlar.append({"dil": dil, "kapi": kapi, "duzey": duzey, "ileti": ileti})

    def yumusak(self) -> str:
        return "HATA" if self.kati else "UYARI"

    def calistir(self) -> None:
        if not self.ana_bayt:
            self.ekle("-", "DOSYA", "HATA", f"{self.profil.ana} missing or empty")
            return
        self.ana_karakter()
        mevcut = {p.name[7:-3] for p in self.kok.glob("README.*.md")}
        for fazla in sorted(mevcut - set(self.profil.diller)):
            self.ekle(fazla, "DOSYA", "HATA", f"README.{fazla}.md exists but is not in dil_profili.json")
        for dil, ayar in sorted(self.profil.diller.items()):
            if self.tek_dil and dil != self.tek_dil:
                continue
            self.dil_denetle(dil, ayar)

    def ana_karakter(self) -> None:
        for sorun in karakter_sorunlari(self.ana_bayt.decode("utf-8", errors="replace"), "-", self.profil):
            self.ekle("-", "KARAKTER", "HATA", f"{self.profil.ana}: {sorun}")

    def dil_denetle(self, dil: str, ayar: dict) -> None:
        yol = self.kok / f"README.{dil}.md"
        if not yol.is_file():
            self.ekle(dil, "DOSYA", "HATA", f"README.{dil}.md missing")
            return
        bayt = yol.read_bytes()
        try:
            metin = bayt.decode("utf-8")
        except UnicodeDecodeError as hata:
            self.ekle(dil, "KARAKTER", "HATA", f"not valid UTF-8 ({hata.reason} at byte {hata.start})")
            return
        rtl = bool(ayar.get("rtl"))
        tier = ayar["tier"]
        # KARAKTER
        for sorun in karakter_sorunlari(metin, dil, self.profil):
            self.ekle(dil, "KARAKTER", "HATA", sorun)
        # DAMGA
        m = DAMGA_RE.findall(bayt)
        if not m:
            self.ekle(dil, "DAMGA", "HATA", "i18n-source stamp missing")
        elif m[-1].decode() != self.ana_ozet:
            ileti = f"stale: stamp {m[-1].decode()}, README.md now {self.ana_ozet}"
            if tier == "A":
                self.ekle(dil, "DAMGA", self.yumusak(), ileti + " (tier A)")
            elif tier == "B":
                self.ekle(dil, "DAMGA", "UYARI", ileti + " (tier B)")
            else:
                self.ekle(dil, "DAMGA", "BILGI", ileti + " (tier C)")
        # dil cubugu
        for diger in ["README.md", *(f"README.{d}.md" for d in sorted(self.profil.diller) if d != dil)]:
            if f"({diger})" not in metin:
                self.ekle(dil, "DOSYA", "HATA", f"language bar link to {diger} missing")
        # YAPI
        y = ayristir(metin.splitlines(), rtl)
        a = self.ana
        for ad in ("h2", "h3", "tablo"):
            if y[ad] != a[ad]:
                self.ekle(dil, "YAPI", self.yumusak(), f"{ad.upper()} count {y[ad]} != {a[ad]} (README.md)")
        if len(y["kod"]) != len(a["kod"]):
            self.ekle(dil, "YAPI", self.yumusak(), f"fenced blocks {len(y['kod'])} != {len(a['kod'])}")
        else:
            for i, (b1, b2) in enumerate(zip(a["kod"], y["kod"]), 1):
                if b1 != b2:
                    self.ekle(dil, "YAPI", self.yumusak(), f"fenced block #{i} differs byte-wise from README.md")
        # BELIRTEC
        bel = belirecler(y["metin"])
        if self.profil.rozet_oneki and tier != "A":
            for u in [u for u in bel["url"] if u.startswith(self.profil.rozet_oneki)]:
                del bel["url"][u]
        for ad, sayac in self.ana_bel.items():
            # numbers: translations may spell numbers as digits (ja "1 paragraph"), so only a number that
            # exists in README.md and is MISSING from the translation counts; other kinds must match exactly.
            fark = fark_ozeti(sayac, bel[ad], yalniz_eksik=(ad == "sayi"))
            if fark:
                self.ekle(dil, "BELIRTEC", self.yumusak(), f"{ad}: {fark}")
        # ETIKET
        e = etiket_sayisi(y["metin"])
        if e != self.ana_etiket:
            self.ekle(dil, "ETIKET", self.yumusak(), f"bracketed labels {e} != {self.ana_etiket}")


def karakter_sorunlari(metin: str, dil: str, profil: Profil) -> list[str]:
    sorunlar: list[str] = []
    sayac: Counter = Counter()
    for c in metin:
        cp = ord(c)
        if cp < 32 and cp not in KONTROL_OK or cp == 0x7F:
            sayac[("control", cp)] += 1
        elif cp in BIDI_YASAK:
            sayac[("bidi", cp)] += 1
        elif cp in (0x200C, 0x200D) and dil not in profil.zwj_izinli:
            sayac[("zwnj/zwj", cp)] += 1
        elif cp in (0x200E, 0x200F) and dil not in profil.lrm_izinli:
            sayac[("lrm/rlm", cp)] += 1
        elif cp == 0xFEFF or cp == 0x200B:
            sayac[("invisible", cp)] += 1
    for (ad, cp), n in sorted(sayac.items()):
        sorunlar.append(f"forbidden {ad} U+{cp:04X} x{n}")
    return sorunlar


def damga_yaz(kok: Path, profil: Profil, yaz: bool, tek_dil: str | None) -> int:
    hedef = ozet((kok / profil.ana).read_bytes())
    degisen = 0
    for dil in sorted(profil.diller):
        if tek_dil and dil != tek_dil:
            continue
        yol = kok / f"README.{dil}.md"
        if not yol.is_file():
            print(f"{dil}: file missing")
            continue
        bayt = yol.read_bytes()
        m = list(DAMGA_RE.finditer(bayt))
        yeni_satir = f"<!-- i18n-source: README.md sha256:{hedef} -->".encode()
        if m and m[-1].group(1).decode() == hedef:
            continue
        degisen += 1
        print(f"{dil}: stamp {m[-1].group(1).decode() if m else 'none'} -> {hedef}")
        if yaz:
            if m:
                son = m[-1]
                yeni = bayt[: son.start()] + yeni_satir + bayt[son.end():]
            else:
                yeni = bayt.rstrip(b"\n") + b"\n\n" + yeni_satir + b"\n"
            yol.write_bytes(yeni)
    print(f"{'written' if yaz else 'dry run (add --yaz to write)'}: {degisen} stamp(s)")
    return 0


def sonuc(kayitlar: list[dict]) -> tuple[str, int, int]:
    hata = sum(1 for k in kayitlar if k["duzey"] == "HATA")
    uyari = sum(1 for k in kayitlar if k["duzey"] == "UYARI")
    return ("KALDI" if hata else "UYARI" if uyari else "GECTI"), hata, uyari


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ayr = argparse.ArgumentParser(description="README translation parity check", add_help=True)
    ayr.add_argument("--kok", type=Path, default=VARSAYILAN_KOK)
    ayr.add_argument("--kati", action="store_true", help="soft findings count as errors")
    ayr.add_argument("--json", action="store_true")
    ayr.add_argument("--dil", help="check one language code, e.g. tr")
    ayr.add_argument("--damga", action="store_true", help="stamp dry run; with --yaz it writes")
    ayr.add_argument("--yaz", action="store_true")
    s = ayr.parse_args(argv)
    kok = s.kok.resolve()
    try:
        profil = profil_yukle(kok)
    except (OSError, ValueError, KeyError) as hata:
        print(f"SONUC: KALDI (profile missing or invalid: {hata})")
        return 3
    if s.dil and s.dil not in profil.diller:
        print(f"SONUC: KALDI (language {s.dil} not in profile)")
        return 3
    if s.damga:
        return damga_yaz(kok, profil, s.yaz, s.dil)
    d = Denetim(kok, profil, s.kati, s.dil)
    d.calistir()
    durum, hata, uyari = sonuc(d.kayitlar)
    if s.json:
        print(json.dumps({"sonuc": durum, "hata": hata, "uyari": uyari, "kayitlar": d.kayitlar}, ensure_ascii=False))
    else:
        for k in d.kayitlar:
            print(f"{k['duzey']:<6} {k['dil']:<6} {k['kapi']:<9} {k['ileti']}")
        n = len(profil.diller) if not s.dil else 1
        print(f"checked {n} translation(s) against {profil.ana} (sha256:{d.ana_ozet})")
        print(f"SONUC: {durum} ({hata} hata, {uyari} uyari)")
    return 1 if hata else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except BaseException as hata:  # the gate crashed: never green
        print(f"SONUC: KALDI (gate could not run: {type(hata).__name__}: {hata})")
        sys.exit(6)
