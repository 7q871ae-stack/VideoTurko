#!/usr/bin/env bash
# VideoTurko Linux kurulumu: .venv (opencv + numpy), derlenmiş sd-cli kontrolü ve MiniMax H3 modelleri (~29.3 GiB).
set -euo pipefail

LISANS_KABUL=""
KONTROL=0
DOGRULA=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --lisans-kabul|-LisansKabul) LISANS_KABUL="${2:-}"; shift 2 ;;
    --kontrol|-Kontrol) KONTROL=1; shift ;;
    --dogrula|-Dogrula) DOGRULA=1; shift ;;
    -h|--help)
      echo "Kullanım: ./kur.sh [--lisans-kabul E] [--dogrula] [--kontrol]"
      exit 0
      ;;
    *) echo "Bilinmeyen parametre: $1" >&2; exit 2 ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="${VT_ROOT:-$(cd "$SCRIPT_DIR/.." && pwd)}"
ENGINE_BIN="${VT_ENGINE_BIN:-$ROOT/engine/bin}"
MODEL_DIR="${VT_MODEL_DIR:-$ROOT/model}"
VENV="$ROOT/.venv"
PY="$VENV/bin/python"

echo "VideoTurko kurulumu (Linux) · kök: $ROOT"

if [[ ! -x "$ENGINE_BIN/sd-cli" ]]; then
  echo "== Motor bulunamadı; Linux CUDA derlemesi başlatılıyor (scripts/derle_linux.sh)"
  bash "$ROOT/scripts/derle_linux.sh"
fi

command -v nvidia-smi >/dev/null 2>&1 || { echo "HATA: nvidia-smi bulunamadı." >&2; exit 3; }
echo "  GPU: $(nvidia-smi --query-gpu=name,memory.total,compute_cap --format=csv,noheader | head -n1)"

bos_gb="$(df -BG --output=avail "$ROOT" | tail -n1 | tr -dc '0-9')"
if [[ "$bos_gb" -lt 32 ]]; then
  echo "HATA: En az 32 GiB boş disk alanı gerekir (mevcut: ${bos_gb} GiB)." >&2
  exit 3
fi

if [[ "$LISANS_KABUL" != "E" && "$LISANS_KABUL" != "e" ]]; then
  if [[ -f "$ROOT/docs/LISANS_KABUL.txt" ]]; then
    cat "$ROOT/docs/LISANS_KABUL.txt"
    echo ""
  fi
  read -r -p "MiniMax H3 Community License şartlarını okudunuz ve kabul ediyor musunuz? [E/h]: " LISANS_KABUL
  if [[ "$LISANS_KABUL" != "E" && "$LISANS_KABUL" != "e" ]]; then
    echo "Lisans kabul edilmedi; kurulum durduruldu (çıkış 2)." >&2
    exit 2
  fi
fi

echo "== Python .venv (opencv-python-headless + numpy)"
if [[ ! -x "$PY" ]]; then
  python3 -m venv "$VENV"
fi
"$PY" -m pip install --quiet --cache-dir "$ROOT/.onbellek/pip" --upgrade pip
"$PY" -m pip install --quiet --cache-dir "$ROOT/.onbellek/pip" opencv-python-headless numpy
"$PY" -c "import cv2, numpy; print('  opencv', cv2.__version__, 'numpy', numpy.__version__)"

echo "== Modeller (~29.3 GiB, sha256 doğrulamalı)"
extra_arg=()
[[ "$DOGRULA" -eq 1 ]] && extra_arg+=(--dogrula)
"$PY" "$ROOT/scripts/modelleri_indir.py" --model-dir "$MODEL_DIR" "${extra_arg[@]}"

if [[ "$KONTROL" -eq 1 ]]; then
  echo "== Kısa 5 karelik kontrol"
  bash "$ROOT/scripts/uret.sh" --istem "$ROOT/docs/ornek_istem_R0.txt" --kare 5 --kontrol
fi

echo "HAZIR / READY"
echo "Video üretmek için: ./uret.sh --istem docs/ornek_istem_R0.txt --kare 56"
