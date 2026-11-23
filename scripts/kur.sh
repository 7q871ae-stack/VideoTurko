#!/usr/bin/env bash
# VideoTurko Linux kurulumu (scripts/kur.ps1 karsiligi). DENEYSEL: bakimcilar Linux'ta GPU kosusu yapmadi.
# Sira (kur.ps1 ile ayni): GPU -> disk (MODEL surucusu) -> lisans -> venv -> motor (klon + derleme) -> model -> 5 karelik GERCEK kontrol uretimi -> HAZIR.
# HAZIR yalniz kontrol uretimi basarili olunca yazilir. Klon ve derleme, GPU/disk/lisans kapilarindan SONRA baslar.
# Kullanim: ./kur.sh [--kuru] [--lisans-kabul E] [--dogrula] [--kontrol-atla]
#   --kuru          : ne yapacagini yazar (GPU, disk, lisans, motor, model); hicbir sey indirmez/olusturmaz/derlemez; cikis kodu hazirlik durumunu verir
#   --kontrol-atla  : 5 karelik kontrol uretimini atlar; bu durumda HAZIR YAZILMAZ ("KONTROL ATLANDI")
#   (--kontrol eski surumde kontrolu acardi; kontrol artik her zaman calisir, bayrak kabul edilir ve bir sey degistirmez)
# Cikis kodlari: 0 HAZIR (ya da --kuru raporu tamam), 1 hata, 2 lisans kabul gerekli, 3 donanim/disk yetersiz.
# Ortam: VT_ROOT, VT_ENGINE_BIN, VT_MODEL_DIR (VT_DF_KOMUT, VT_NVIDIA_SMI: yalniz test kancalari, sahte komut).
set -euo pipefail

LISANS_KABUL=""
KURU=0
DOGRULA=0
KONTROL_ATLA=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --lisans-kabul|-LisansKabul)
      [[ $# -ge 2 ]] || { echo "HATA: --lisans-kabul icin deger gerekir (E)" >&2; exit 2; }
      LISANS_KABUL="$2"; shift 2 ;;
    --kuru|-Kuru) KURU=1; shift ;;
    --dogrula|-Dogrula) DOGRULA=1; shift ;;
    --kontrol|-Kontrol) shift ;;
    --kontrol-atla) KONTROL_ATLA=1; shift ;;
    -h|--help)
      echo "Kullanim: ./kur.sh [--kuru] [--lisans-kabul E] [--dogrula] [--kontrol-atla]"
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
MODEL_MIN_GIB=32   # 29,31 GiB model + pay (kur.ps1 / README ile ayni sayi)
MOTOR_MIN_GIB=10   # klon + derleme agaci + venv icin kok surucusunde pay [tahmin; Linux'ta olculmedi]

echo "VideoTurko kurulumu (Linux, DENEYSEL) · kok: $ROOT$([[ "$KURU" -eq 1 ]] && echo ' · --kuru: hicbir sey yazilmaz')"

PROBLEM=0
sorun() { echo "HATA: $1" >&2; PROBLEM=1; }

# bos_gib <yol>: yolun (yoksa var olan en yakin ust klasorun) surucusunde bos GiB; aygit adi da doner
bos_gib() {
  local d="$1"
  while [[ ! -d "$d" && "$d" != "/" && "$d" != "." ]]; do d="$(dirname "$d")"; done
  "${VT_DF_KOMUT:-df}" -Pk "$d" 2>/dev/null | awk 'NR==2 {printf "%d %s", $4/1048576, $1}'
}

# 1) GPU
SMI="${VT_NVIDIA_SMI:-nvidia-smi}"   # VT_NVIDIA_SMI: yalniz test kancasi
if ! command -v "$SMI" >/dev/null 2>&1; then
  sorun "[VT-E-GPU] nvidia-smi yok: NVIDIA surucusu kurulu degil ya da NVIDIA kart yok (Linux betigi yalniz NVIDIA CUDA; AMD icin docs/AMD_ROCM.md)."
else
  gpu_satir="$("$SMI" --query-gpu=name,memory.total,compute_cap --format=csv,noheader,nounits 2>/dev/null | head -n1 || true)"
  echo "  GPU: ${gpu_satir:-okunamadi}"
  vram="$(echo "$gpu_satir" | awk -F', *' '{print $(NF-1)}' | tr -dc '0-9')"
  cc="$(echo "$gpu_satir" | awk -F', *' '{print $NF}' | tr -d '[:space:]' | tr ',' '.')"
  if [[ -n "$vram" && "$vram" -lt 3800 ]]; then sorun "[VT-E-GPU-VRAM] en az 4 GB VRAM gerekir (okunan: $vram MiB)"; fi
  if [[ "$cc" =~ ^[0-9]+(\.[0-9]+)?$ ]] && awk -v c="$cc" 'BEGIN{exit !(c+0 < 6.1)}'; then sorun "[VT-E-GPU-CC] compute capability 6.1 (Pascal) ya da ustu gerekir (okunan: $cc)"; fi
fi

# 2) disk: MODEL surucusu (modeller baska diskteyse onun bos alani); motor eksikse kok surucusu da
modeller_tamam=1
for f in minimax_h3_fl2va_hyperflow_flash_14b-Q4_K_M.gguf qwen3vl_32b_minimax_h3-Q4_K_M.gguf minimax_h3_sol_vae_fp16.safetensors minimax_h3_audio_vae_fp32.safetensors; do
  [[ -f "$MODEL_DIR/$f" ]] || modeller_tamam=0
done
motor_var=0; [[ -x "$ENGINE_BIN/sd-cli" ]] && motor_var=1
read -r model_bos model_dev <<< "$(bos_gib "$MODEL_DIR")"
read -r kok_bos kok_dev <<< "$(bos_gib "$ROOT")"
model_gerek=0; [[ "$modeller_tamam" -eq 0 ]] && model_gerek="$MODEL_MIN_GIB"
kok_gerek=0; [[ "$motor_var" -eq 0 ]] && kok_gerek="$MOTOR_MIN_GIB"
if [[ "$model_dev" == "$kok_dev" ]]; then   # ayni surucu: ihtiyaclar toplanir
  toplam=$(( model_gerek + kok_gerek ))
  echo "  Disk: bos ${model_bos:-?} GiB (model klasoru $MODEL_DIR; gereken ~$toplam GiB)"
  [[ "${model_bos:-0}" -ge "$toplam" ]] || sorun "[VT-E-DISK] en az $toplam GiB bos disk gerekir (model $model_gerek + motor/venv payi $kok_gerek [tahmin]; bos: ${model_bos:-0} GiB)."
else
  echo "  Disk: model surucusu bos ${model_bos:-?} GiB (gereken $model_gerek GiB); kok surucusu bos ${kok_bos:-?} GiB (gereken $kok_gerek GiB)"
  [[ "${model_bos:-0}" -ge "$model_gerek" ]] || sorun "[VT-E-DISK] model surucusunde en az $model_gerek GiB bos gerekir (bos: ${model_bos:-0} GiB; $MODEL_DIR)."
  [[ "${kok_bos:-0}" -ge "$kok_gerek" ]] || sorun "[VT-E-DISK] kok surucusunde en az $kok_gerek GiB bos gerekir [tahmin] (bos: ${kok_bos:-0} GiB; $ROOT)."
fi

# 3) lisans (indirme/derleme baslamadan once)
lisans_kabul_mi() { [[ "$LISANS_KABUL" == "E" || "$LISANS_KABUL" == "e" || "$LISANS_KABUL" == "Y" || "$LISANS_KABUL" == "y" ]]; }
if [[ "$KURU" -eq 1 ]]; then
  echo "  Lisans: kabul $([[ "$modeller_tamam" -eq 1 ]] && echo 'istenmeyecek (modeller var)' || echo 'istenecek (MiniMax H3 Community License); --kuru icin sorulmadi')"
fi

if [[ "$PROBLEM" -ne 0 ]]; then
  echo "Donanim/disk kapisi gecmedi: motor klonlanmadi/derlenmedi, hicbir sey indirilmedi (cikis 3)." >&2
  exit 3
fi

if [[ "$KURU" -eq 1 ]]; then
  echo "KURU plan: $([[ "$motor_var" -eq 1 ]] && echo "motor var ($ENGINE_BIN/sd-cli)" || echo "motor yok: scripts/derle_linux.sh ile klon + derleme (git, cmake, nvcc gerekir)")"
  echo "KURU plan: python venv + opencv-python-headless + numpy (yalniz kok altinda: $VENV, onbellek $ROOT/.onbellek/pip)"
  echo "KURU plan: $([[ "$modeller_tamam" -eq 1 ]] && echo 'modeller var (--dogrula ile sha256 sinanir)' || echo "model indirme (~29,3 GiB, sha256 dogrulamali): $MODEL_DIR")"
  echo "KURU plan: 5 karelik kontrol uretimi; HAZIR yalniz o gecince yazilir"
  echo "KURU bitti: hicbir sey yazilmadi."
  exit 0
fi

if ! lisans_kabul_mi; then
  if [[ "$modeller_tamam" -eq 0 || "$motor_var" -eq 0 ]]; then
    if [[ -f "$SCRIPT_DIR/../docs/LISANS_KABUL.txt" ]]; then cat "$SCRIPT_DIR/../docs/LISANS_KABUL.txt"; echo ""; fi
    LISANS_KABUL=""
    read -r -p "MiniMax H3 Community License sartlarini okudunuz ve kabul ediyor musunuz? [E/h]: " LISANS_KABUL || {
      echo "[VT-E-LISANS] Lisans kabulu etkilesimsiz alinamadi: kullaniciya sorun, kabul gelince --lisans-kabul E ile calistirin; hicbir sey indirilmedi/derlenmedi (cikis 2)." >&2
      exit 2
    }
    lisans_kabul_mi || { echo "[VT-E-LISANS] Lisans kabul edilmedi; kurulum durduruldu (cikis 2)." >&2; exit 2; }
  fi
fi

# 4) python venv (opencv-python-headless + numpy; yalniz kok altinda)
command -v python3 >/dev/null 2>&1 || { echo "HATA: [VT-E-PYTHON] python3 bulunamadi." >&2; exit 1; }
echo "== Python .venv (opencv-python-headless + numpy)"
if [[ ! -x "$PY" ]]; then python3 -m venv "$VENV"; fi
"$PY" -m pip install --quiet --only-binary=:all: --cache-dir "$ROOT/.onbellek/pip" --upgrade pip
"$PY" -m pip install --quiet --only-binary=:all: --cache-dir "$ROOT/.onbellek/pip" opencv-python-headless numpy
"$PY" -c "import cv2, numpy; print('  opencv', cv2.__version__, 'numpy', numpy.__version__)"

# 5) motor (klon + derleme): GPU, disk ve lisans kapilarindan SONRA
if [[ "$motor_var" -eq 0 ]]; then
  echo "== Motor bulunamadi; Linux CUDA derlemesi baslatiliyor (scripts/derle_linux.sh)"
  bash "$SCRIPT_DIR/derle_linux.sh"
fi
[[ -x "$ENGINE_BIN/sd-cli" ]] || { echo "HATA: [VT-E-MOTOR] sd-cli yok: $ENGINE_BIN/sd-cli" >&2; exit 1; }

# 6) modeller
echo "== Modeller (~29.3 GiB, sha256 dogrulamali)"
extra_arg=()
[[ "$DOGRULA" -eq 1 ]] && extra_arg+=(--dogrula)
"$PY" -I "$SCRIPT_DIR/modelleri_indir.py" --model-dir "$MODEL_DIR" ${extra_arg[@]+"${extra_arg[@]}"}

# 7) 5 karelik GERCEK kontrol uretimi: HAZIR yalniz basariliysa
if [[ "$KONTROL_ATLA" -eq 1 ]]; then
  echo "KONTROL ATLANDI: kurulum bitti ama HAZIR YAZILMAZ (5 karelik uretim denenmedi)."
  echo "Deneyin: ./uret.sh --istem docs/ornek_istem_R0.txt --kare 5 --kontrol"
  exit 0
fi
echo "== Kontrol: 5 karelik GERCEK uretim (uret.sh ile ayni yol); yalniz basariliysa HAZIR"
kontrol_log="$(mktemp "$ROOT/.kontrol_log.XXXXXX")"
trap 'rm -f "$kontrol_log"' EXIT
kontrol_kod=0
bash "$SCRIPT_DIR/uret.sh" --istem "$SCRIPT_DIR/../docs/ornek_istem_R0.txt" --kare 5 --kontrol --tavan-dk 30 2>&1 | tee "$kontrol_log" || kontrol_kod=${PIPESTATUS[0]}
kontrol_avi="$(sed -n 's/^TAMAM: //p' "$kontrol_log" | tail -n1)"
if [[ "$kontrol_kod" -ne 0 || -z "$kontrol_avi" || ! -f "$kontrol_avi" ]]; then
  echo "KONTROL BASARISIZ [VT-E-KONTROL] (cikis $kontrol_kod): HAZIR YAZILMAZ. Log: runs/ klasorundeki son run_*_k5/sd_asama1.log" >&2
  exit 1
fi

echo "HAZIR / READY (5 karelik kontrol uretimi gecti)"
echo "Video uretmek icin: ./uret.sh --istem docs/ornek_istem_R0.txt --kare 56"
