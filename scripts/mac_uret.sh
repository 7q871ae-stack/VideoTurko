#!/usr/bin/env bash
set -euo pipefail

# macOS (Apple Silicon / Metal) yardimci uretim betigi.
# Windows betiklerine ve sabit kalite ayarlarina (6 adim, cfg 1.0, 640x384, parcasiz VAE, tohum 42) dokunmaz.
#
# Iki mod:
#   Varsayilan (TAM_METAL=0): ilk calisan guvenli hal (--offload-to-cpu --backend te=cpu, chunk_budget=0.03)
#   Istege bagli 48 GB+ (TAM_METAL=1): tum 30 GB agirlik MTL0 GPU'da (--auto-fit on --flash-attn on, chunk_budget=0)
#
# Kullanim:
#   scripts/mac_uret.sh <istem.txt> [kare=56] [genislik=640] [yukseklik=384] [ilk_kare.png]
#   TAM_METAL=1 scripts/mac_uret.sh <istem.txt> 56
#
# Ortam degiskenleri (istege bagli):
#   VT_ROOT          (varsayilan: bu betigin ust klasoru)
#   VT_ENGINE_BIN    (varsayilan: <VT_ROOT>/engine_mac/bin)
#   VT_MODEL_DIR     (varsayilan: <VT_ROOT>/model)
#   TAM_METAL=0      (1 ise 48 GB+ Mac icin tam Metal hiz modu acilir)
#   H3_CHUNK_BUDGET  (varsayilan: TAM_METAL=0 icin 0.03, TAM_METAL=1 icin 0)
#   VT_PYTHON        (kalite kapisi icin opencv-python + numpy olan python; varsayilan: <VT_ROOT>/.venv/bin/python, yoksa python3)
# Tohum 42 ve 24 fps kalite sabitidir, ortamdan degismez (maintainers, after PR #10).

if [[ $# -lt 1 ]]; then
  echo "Kullanim: $0 <istem.txt> [kare=56] [genislik=640] [yukseklik=384] [ilk_kare.png]"
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="${VT_ROOT:-$(cd "$SCRIPT_DIR/.." && pwd)}"
ENGINE_BIN="${VT_ENGINE_BIN:-$ROOT/engine_mac/bin}"
MODEL_DIR="${VT_MODEL_DIR:-$ROOT/model}"
SD_CLI="$ENGINE_BIN/sd-cli"

PROMPT_FILE="$1"
FRAMES="${2:-56}"
WIDTH="${3:-640}"
HEIGHT="${4:-384}"
INIT_IMG="${5:-}"

TAM_METAL="${TAM_METAL:-0}"
SEED=42
FPS=24
buyuk_mu() { awk -v a="$1" -v b="$2" 'BEGIN{exit !(a+0 >= b+0)}'; }   # a >= b (ondalik)
if [[ -n "${VT_PYTHON:-}" ]]; then PY="$VT_PYTHON"
elif [[ -x "$ROOT/.venv/bin/python" ]]; then PY="$ROOT/.venv/bin/python"
else PY="python3"; fi

if [[ -z "${H3_CHUNK_BUDGET:-}" ]]; then
  if [[ "$TAM_METAL" == "1" ]]; then
    H3_CHUNK_BUDGET="0"
  else
    H3_CHUNK_BUDGET="0.03"
  fi
fi

if [[ ! -x "$SD_CLI" ]]; then
  echo "HATA: sd-cli bulunamadi: $SD_CLI"
  exit 1
fi

if [[ ! -f "$PROMPT_FILE" ]]; then
  if [[ -f "$ROOT/$PROMPT_FILE" ]]; then
    PROMPT_FILE="$ROOT/$PROMPT_FILE"
  else
    echo "HATA: Istem dosyasi bulunamadi: $PROMPT_FILE"
    exit 1
  fi
fi

if ! [[ "$FRAMES" =~ ^[0-9]+$ ]] || (( FRAMES < 5 || (FRAMES - 5) % 17 != 0 )); then
  echo "HATA: [VT-E-KARE] Kare sayisi 17k+5 olmali (5, 22, 39, 56, ... 209). Verilen: $FRAMES" >&2
  exit 1
fi

if (( WIDTH % 32 != 0 || HEIGHT % 32 != 0 )); then
  echo "HATA: Genislik ($WIDTH) ve yukseklik ($HEIGHT) 32'nin kati olmalidir."
  exit 1
fi

if (( WIDTH * HEIGHT < 640 * 384 )); then
  echo "HATA: Cozunurluk alani 640x384 altina dusurulemez."
  exit 1
fi

if [[ -n "$INIT_IMG" && ! -f "$INIT_IMG" ]]; then
  echo "HATA: Baslangic gorseli bulunamadi: $INIT_IMG"
  exit 1
fi

echo "=== Cihaz Dogrulamasi (sd-cli --list-devices) ==="
DEVICES="$("$SD_CLI" --list-devices 2>&1)"
echo "$DEVICES"
if ! echo "$DEVICES" | grep -qiE "MTL0|metal"; then
  echo "HATA: Metal GPU (MTL0) gorunmuyor; CPU'ya dusmemek icin durduruldu."
  exit 1
fi

STEM="$(basename "$PROMPT_FILE" .txt)"
STAMP="$(date +%Y%m%d_%H%M%S)"
RUN_DIR="$ROOT/runs/${STAMP}_${STEM}_${FRAMES}k_${WIDTH}x${HEIGHT}"
LOG_FILE="$RUN_DIR/sd_cli.log"
OUT_VIDEO="$RUN_DIR/video.avi"
mkdir -p "$RUN_DIR"

CMD=(
  "$SD_CLI" -M vid_gen
  --diffusion-model "$MODEL_DIR/minimax_h3_fl2va_hyperflow_flash_14b-Q4_K_M.gguf"
  --llm "$MODEL_DIR/qwen3vl_32b_minimax_h3-Q4_K_M.gguf"
  --vae "$MODEL_DIR/minimax_h3_sol_vae_fp16.safetensors"
  --audio-vae "$MODEL_DIR/minimax_h3_audio_vae_fp32.safetensors"
  --prompt-file "$PROMPT_FILE"
  -W "$WIDTH" -H "$HEIGHT" --video-frames "$FRAMES" --fps "$FPS"
  --steps 6 --sampling-method euler --sigmas hyperflow-h3-flash-6 --cfg-scale 1.0
  --rng cpu --seed "$SEED"
  --model-args "minimax_h3_attn_chunk_budget=$H3_CHUNK_BUDGET"
  --mmap
  -o "$OUT_VIDEO"
)

if [[ "$TAM_METAL" == "1" ]]; then
  CMD+=(--flash-attn on --auto-fit on)
else
  CMD+=(-t 8 --flash-attn off,diffusion=on --offload-to-cpu --backend te=cpu)
fi

if [[ -n "$INIT_IMG" ]]; then
  CMD+=(--init-img "$INIT_IMG")
fi

echo "Mod: TAM_METAL=$TAM_METAL | Boyut: ${WIDTH}x${HEIGHT} | Kare: $FRAMES | FPS: $FPS | Seed: $SEED | ChunkBudget: $H3_CHUNK_BUDGET"
rc=0
/usr/bin/time -l "${CMD[@]}" > "$LOG_FILE" 2>&1 || rc=$?
if [[ "$rc" -ne 0 ]]; then
  echo "HATA: [VT-E-CIKTI] sd-cli cikis kodu $rc; log: $LOG_FILE" >&2
  tail -n 20 "$LOG_FILE" >&2 || true
  exit 1
fi
if [[ ! -s "$OUT_VIDEO" ]]; then
  echo "HATA: [VT-E-CIKTI] video dosyasi yok ya da bos: $OUT_VIDEO (log: $LOG_FILE)" >&2
  exit 1
fi

if grep -qi "retrying with temporal tiling" "$LOG_FILE"; then
  echo "HATA: [VT-E-TILING] GECERSIZ CIKTI: logda 'retrying with temporal tiling' goruldu ($LOG_FILE)" >&2
  exit 1
fi

# Kalite kapisi: uret.sh / uretim_kapi.ps1 ile ayni esikler (kare = beklenen VE gurultu <= 1,5 VE orta akis > 0,05). Esiklere dokunulmaz (docs/KAPILAR.md).
echo "== Kalite kapisi (scripts/dikis_denetim.py)"
kapi_cikti="$("$PY" -I "$SCRIPT_DIR/dikis_denetim.py" "$OUT_VIDEO" 2>&1)" && kapi_kod=0 || kapi_kod=$?
if [[ "$kapi_kod" -eq 6 || "$kapi_kod" -eq 3 ]] || [[ "$kapi_cikti" =~ (No\ module\ named|ModuleNotFoundError|ImportError) ]]; then
  echo "VIDEO URETILDI ama KAPI CALISMADI [VT-E-PY] (python'da opencv/numpy yok: pip install opencv-python-headless numpy ya da VT_PYTHON): klip kabul edilmedi sayilir: $OUT_VIDEO" >&2
  echo "${kapi_cikti:0:300}" >&2
  exit 6
fi
if ! [[ "$kapi_cikti" =~ kare=([0-9]+)\ gurultu=([0-9.]+).*orta\ akis=([0-9.]+) ]]; then
  echo "KAPI RED: [VT-E-KAPI-RED] dikis_denetim cikti ayristirilamadi: ${kapi_cikti:0:200}" >&2
  exit 5
fi
olc="${BASH_REMATCH[1]}"; gur="${BASH_REMATCH[2]}"; ak="${BASH_REMATCH[3]}"
if [[ "$olc" -eq "$FRAMES" ]] && buyuk_mu 1.5 "$gur" && buyuk_mu "$ak" 0.0500001; then
  echo "KAPI GECTI: kare=$olc gurultu=$gur orta_akis=$ak"
else
  echo "KAPI RED: [VT-E-KAPI-RED] kare=$olc (beklenen $FRAMES) gurultu=$gur (<=1,5) orta_akis=$ak (>0,05); klip kabul edilmez, karar kullanicinindir; docs/KAPILAR.md" >&2
  exit 5
fi
[[ "$WIDTH" -eq 640 && "$HEIGHT" -eq 384 ]] || echo "UYARI: kalite kapisi esikleri 640x384 icin kalibre; ${WIDTH}x${HEIGHT} boyutunda degerler karsilastirilamaz. Videoyu gozle izleyin (docs/KAPILAR.md)."
echo "Kalite kapisi lisans uygunlugunu denetlemez; cikti kullanimi sizin sorumlulugunuzdadir: docs/LISANS_UYARISI.md"

echo "=== TAMAM ==="
echo "Video: $OUT_VIDEO"
grep -iE "get_learned_condition completed|sampling completed|decode_first_stage completed|generate_video completed" "$LOG_FILE" || true
grep -iE "maximum resident set size|peak memory footprint" "$LOG_FILE" || true
