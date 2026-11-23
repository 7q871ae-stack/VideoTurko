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
#   SEED=42          (varsayilan: 42)
#   FPS=24           (MiniMax H3 icin 24 sabit onerilir)

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
SEED="${SEED:-42}"
FPS="${FPS:-24}"

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
/usr/bin/time -l "${CMD[@]}" > "$LOG_FILE" 2>&1

if grep -qi "retrying with temporal tiling" "$LOG_FILE"; then
  echo "GECERSIZ CIKTI: Logda 'retrying with temporal tiling' goruldu."
  exit 1
fi

echo "=== TAMAM ==="
echo "Video: $OUT_VIDEO"
grep -iE "get_learned_condition completed|sampling completed|decode_first_stage completed|generate_video completed" "$LOG_FILE" || true
grep -iE "maximum resident set size|peak memory footprint" "$LOG_FILE" || true
