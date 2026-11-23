#!/usr/bin/env python3
"""VideoTurko model indirici: scripts/modeller.json içindeki sabit adres + sha256 ile."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = Path(__file__).with_name("modeller.json")


def sha256_dosya(yol: Path) -> str:
    h = hashlib.sha256()
    with open(yol, "rb") as f:
        while True:
            b = f.read(4 << 20)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def indir(url: str, hedef: Path, beklenen_boyut: int, beklenen_sha: str, dogrula: bool) -> None:
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != "https":
        raise SystemExit(f"Yalnız https desteklenir: {url}")

    if hedef.is_file() and hedef.stat().st_size == beklenen_boyut:
        if not dogrula:
            print(f"  var (boyut doğru): {hedef.name}", flush=True)
            return
        if sha256_dosya(hedef) == beklenen_sha:
            print(f"  var (sha256 doğru): {hedef.name}", flush=True)
            return
        print(f"  uyarı: {hedef.name} sha256 tutmadı, yeniden indiriliyor...", flush=True)

    hedef.parent.mkdir(parents=True, exist_ok=True)
    part = hedef.with_name(hedef.name + ".part")
    mevcut = part.stat().st_size if part.is_file() else 0
    if mevcut > beklenen_boyut:
        part.unlink()
        mevcut = 0

    req = urllib.request.Request(url, headers={"User-Agent": "VideoTurko/0.1.1"})
    if mevcut > 0:
        req.add_header("Range", f"bytes={mevcut}-")
        print(f"  devam ediyor ({mevcut / (1 << 20):.1f} MiB): {hedef.name}", flush=True)
    else:
        print(f"  indiriliyor ({beklenen_boyut / (1 << 30):.2f} GiB): {hedef.name}", flush=True)

    with urllib.request.urlopen(req, timeout=60) as resp:
        status = getattr(resp, "status", 200)
        mode = "ab" if (mevcut > 0 and status == 206) else "wb"
        if mode == "wb":
            mevcut = 0
        inen = mevcut
        son_yuzde = -1
        with open(part, mode) as out:
            while True:
                parca = resp.read(1 << 20)
                if not parca:
                    break
                out.write(parca)
                inen += len(parca)
                yuzde = int(inen * 100 / beklenen_boyut) if beklenen_boyut else 0
                if yuzde != son_yuzde and (yuzde % 5 == 0 or yuzde == 100):
                    son_yuzde = yuzde
                    print(f"    %{yuzde} ({inen / (1 << 20):.0f} / {beklenen_boyut / (1 << 20):.0f} MiB)", flush=True)

    if part.stat().st_size != beklenen_boyut:
        raise SystemExit(f"boyut tutmadı ({hedef.name}): {part.stat().st_size} != {beklenen_boyut}")
    print(f"  sha256 doğrulanıyor: {hedef.name}...", flush=True)
    gelen_sha = sha256_dosya(part)
    if gelen_sha != beklenen_sha:
        part.unlink(missing_ok=True)
        raise SystemExit(f"sha256 tutmadı ({hedef.name}):\n  beklenen {beklenen_sha}\n  gelen    {gelen_sha}")
    part.replace(hedef)
    print(f"  indi ve doğrulandı: {hedef.name}", flush=True)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="VideoTurko model indirici")
    ap.add_argument("--model-dir", type=Path, default=ROOT / "model")
    ap.add_argument("--dogrula", action="store_true")
    ap.add_argument("--liste", action="store_true")
    args = ap.parse_args(argv)

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))["dosyalar"]
    if args.liste:
        for k in manifest:
            print(f"{k['adim']:10} {k['boyut'] / (1 << 30):5.2f} GiB  {k['hedef']}")
        return 0

    for k in manifest:
        indir(k["url"], args.model_dir / k["hedef"], int(k["boyut"]), k["sha256"], args.dogrula)
    print("MODELLER_OK", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
