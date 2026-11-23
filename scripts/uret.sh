#!/usr/bin/env bash
# VideoTurko Linux video üretim betiği (scripts/uret.ps1 karşılığı).
set -euo pipefail

ISTEM=""
KARE=209
W=640
H=384
SEED=42
INIT_IMG=""
END_IMG=""
TEK_ASAMA=0
KURU=0
KONTROL=0
TAVAN_DK=0
ATTN="${VT_ATTN:-0.05}"
CHUNK_MB="${VT_CHUNK:-64}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --istem|-Istem) ISTEM="$2"; shift 2 ;;
    --kare|-Kare) KARE="$2"; shift 2 ;;
    -W|--w) W="$2"; shift 2 ;;
    -H|--h) H="$2"; shift 2 ;;
    --seed|-Seed) SEED="$2"; shift 2 ;;
    --init-img|-InitImg) INIT_IMG="$2"; shift 2 ;;
    --end-img|-EndImg) END_IMG="$2"; shift 2 ;;
    --tek-asama|-TekAsama) TEK_ASAMA=1; shift ;;
    --kuru|-Kuru) KURU=1; shift ;;
    --kontrol|-Kontrol) KONTROL=1; shift ;;
    --tavan-dk|-TavanDk) TAVAN_DK="$2"; shift 2 ;;
    -h|--help)
      echo "Kullanım: ./uret.sh --istem <dosya.txt> [--kare 56|141|209] [-W 640] [-H 384] [--init-img a.png] [--end-img b.png] [--tek-asama] [--kuru]"
      exit 0
      ;;
    *) echo "Bilinmeyen parametre: $1" >&2; exit 2 ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="${VT_ROOT:-$(cd "$SCRIPT_DIR/.." && pwd)}"
ENGINE_BIN="${VT_ENGINE_BIN:-$ROOT/engine/bin}"
MODEL_DIR="${VT_MODEL_DIR:-$ROOT/model}"
SD_CLI="$ENGINE_BIN/sd-cli"
PY="${VT_PYTHON:-$ROOT/.venv/bin/python}"

[[ -n "$ISTEM" && -f "$ISTEM" ]] || { echo "HATA: --istem dosyası bulunamadı: $ISTEM" >&2; exit 1; }
[[ -x "$SD_CLI" ]] || { echo "HATA: sd-cli bulunamadı: $SD_CLI" >&2; exit 1; }

if [[ "$KONTROL" -eq 0 ]]; then
  "$PY" -c "import cv2, numpy" >/dev/null 2>&1 || {
    echo "KAPI CALISAMAZ: python + opencv + numpy hazır değil ($PY). Önce ./kur.sh çalıştırın." >&2
    exit 6
  }
fi

DIT="$MODEL_DIR/minimax_h3_fl2va_hyperflow_flash_14b-Q4_K_M.gguf"
TE="$MODEL_DIR/qwen3vl_32b_minimax_h3-Q4_K_M.gguf"
VAE="$MODEL_DIR/minimax_h3_sol_vae_fp16.safetensors"
AVAE="$MODEL_DIR/minimax_h3_audio_vae_fp32.safetensors"
for f in "$DIT" "$TE" "$VAE" "$AVAE"; do
  [[ -f "$f" ]] || { echo "HATA: model dosyası eksik: $f (önce ./kur.sh)" >&2; exit 1; }
done

GPU_VRAM="$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits 2>/dev/null | head -n1 | tr -dc '0-9' || echo 0)"
GPU_CC="$(nvidia-smi --query-gpu=compute_cap --format=csv,noheader 2>/dev/null | head -n1 | tr -d '[:space:]' || echo -1)"

JETON=$(( (W / 16) * (H / 16) * ((KARE - 1) / 4 + 1) / 4 ))
KUCUK_KART=0
[[ "$GPU_VRAM" -lt 6000 ]] && KUCUK_KART=1

IKI_ASAMA=0
if [[ "$TEK_ASAMA" -eq 0 ]]; then
  if [[ "$JETON" -gt 7680 ]] || [[ -n "$END_IMG" && "$KUCUK_KART" -eq 1 ]]; then
    IKI_ASAMA=1
  fi
fi

TS="$(date +%Y%m%d_%H%M%S)"
RUN_DIR="$ROOT/runs/run_${TS}_k${KARE}"
mkdir -p "$RUN_DIR"
OUT_AVI="$RUN_DIR/video.avi"
LATENT="$RUN_DIR/latent.bin"
LOG1="$RUN_DIR/sd_asama1.log"
LOG2="$RUN_DIR/sd_asama2.log"

TC_LIB="$ROOT/engine/toolchain/env/lib"
export LD_LIBRARY_PATH="$ENGINE_BIN:$TC_LIB:${LD_LIBRARY_PATH:-}"

if [[ -z "${GGML_CUDA_CUBLAS_COMPUTE_TYPE:-}" ]] && awk "BEGIN{exit !($GPU_CC >= 7.0)}"; then
  export GGML_CUDA_CUBLAS_COMPUTE_TYPE="f32"
fi

ARGS=(
  -M vid_gen
  --diffusion-model "$DIT"
  --llm "$TE"
  --vae "$VAE"
  --audio-vae "$AVAE"
  --prompt-file "$ISTEM"
  -W "$W" -H "$H"
  --video-frames "$KARE"
  --fps 24
  --steps 6
  --sampling-method euler
  --sigmas hyperflow-h3-flash-6
  --cfg-scale 1.0
  --rng cpu
  --seed "$SEED"
  -t 4
  --flash-attn off,diffusion=on
  --model-args "minimax_h3_attn_chunk_budget=$ATTN"
  --offload-to-cpu
  --mmap
  --backend te=cpu
  --log-level debug
  -o "$OUT_AVI"
)
[[ -n "$INIT_IMG" ]] && ARGS+=(--init-img "$INIT_IMG")
[[ -n "$END_IMG" ]] && ARGS+=(--end-img "$END_IMG")

if [[ "$KURU" -eq 1 ]]; then
  echo "KURU: cozunurluk=${W}x${H} kare=$KARE jeton=$JETON iki_asama=$IKI_ASAMA gpu_cc=$GPU_CC gpu_vram=${GPU_VRAM}MiB f32=${GGML_CUDA_CUBLAS_COMPUTE_TYPE:-unset}"
  echo "KOMUT: $SD_CLI ${ARGS[*]}"
  exit 0
fi

echo "Video üretimi başlıyor -> $RUN_DIR (kare=$KARE, ${W}x${H}, iki_asama=$IKI_ASAMA, f32=${GGML_CUDA_CUBLAS_COMPUTE_TYPE:-off})"

if [[ "$IKI_ASAMA" -eq 1 ]]; then
  echo "== Aşama 1: DiT (latent üretimi)"
  MARGIN1=1
  [[ "$GPU_VRAM" -ge 6000 ]] && MARGIN1=512
  SD_VRAM_MARGIN_MB="$MARGIN1" SD_H3_EMBED_CUT=1 SD_H3_DROP_QUEUED=1 SD_H3_EVICT_PAST=1 \
  SD_ATTN_SET_OUT=1 SD_QKV_CHUNK_MB="$CHUNK_MB" SD_QKV_SET_OUT=1 SD_MLP_CHUNK_MB="$CHUNK_MB" \
  SD_VIDEO_LATENT_SAVE="$LATENT" \
  "$SD_CLI" "${ARGS[@]}" > "$LOG1" 2>&1 || true

  [[ -f "$LATENT" ]] || { echo "HATA: Aşama 1 latent üretemedi ($LOG1)" >&2; tail -n 25 "$LOG1" >&2; exit 1; }

  echo "== Aşama 2: VAE (video + ses çözme)"
  SD_VRAM_MARGIN_MB=256 SD_VAE_VRAM_MARGIN_MB=256 SD_CUT_CACHE_HOST_MB=100 \
  SD_VAE_NO_TILING_FALLBACK=1 SD_VAE_EMBED_CUT=1 SD_VIDEO_LATENT_LOAD="$LATENT" \
  "$SD_CLI" "${ARGS[@]}" > "$LOG2" 2>&1 || true
else
  echo "== Tek aşama: DiT + VAE"
  SD_VAE_NO_TILING_FALLBACK=1 \
  "$SD_CLI" "${ARGS[@]}" > "$LOG1" 2>&1 || true
fi

if [[ ! -f "$OUT_AVI" ]]; then
  echo "HATA: Çıktı videosu oluşmadı ($OUT_AVI). Log sonu:" >&2
  tail -n 30 "$LOG1" >&2
  exit 1
fi

if [[ "$KONTROL" -eq 0 ]]; then
  echo "== Kalite kapısı (scripts/dikis_denetim.py)"
  "$PY" "$ROOT/scripts/dikis_denetim.py" "$OUT_AVI"
  "$PY" "$ROOT/scripts/doku_norm.py" "$OUT_AVI" || true
fi

echo "TAMAM: $OUT_AVI"
