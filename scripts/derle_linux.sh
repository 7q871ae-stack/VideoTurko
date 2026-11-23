#!/usr/bin/env bash
# VideoTurko Linux CUDA derleme betiği (DENEYSEL: bakımcılar Linux GPU koşusu yapmadı): stable-diffusion.cpp (sabit tam hash, aşağıda) + patches/SERIES.txt yamaları.
# Bellek taşmasını (OOM) önlemek için paralel iş sayısı (-j) kullanılabilir RAM'e göre sınırlanır.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"   # yamalar (patches/) depoda durur; VT_ROOT baska yerdeyse de buradan okunur
ROOT="${VT_ROOT:-$REPO_DIR}"
SRC_DIR="$ROOT/engine/src"
BUILD_DIR="$ROOT/engine/build"
BIN_DIR="$ROOT/engine/bin"

TC_ENV="$ROOT/engine/toolchain/env"
if [[ -d "$TC_ENV/bin" ]]; then
  export PATH="$TC_ENV/bin:$PATH"
  export CUDA_HOME="${CUDA_HOME:-$TC_ENV}"
fi

for cmd in git cmake; do
  command -v "$cmd" >/dev/null 2>&1 || { echo "HATA: $cmd bulunamadı." >&2; exit 1; }
done
command -v nvcc >/dev/null 2>&1 || { echo "HATA: nvcc (CUDA Toolkit) bulunamadı. CUDA Toolkit kurun veya PATH'e ekleyin." >&2; exit 1; }

# Sabitlenmis kaynak: TAM 40 karakterlik hash (kisa hash cakisabilir). Taban: stable-diffusion.cpp master-1088; ggml altmodulu onun sabitlemesi.
SDCPP_HASH="32d516c0197ed5ca31305b8575e14eb1451fad33"
GGML_HASH="d803c238f67915fb825a9aa4df27b99356d51597"
ISARET="$ROOT/engine/.yamalar_tamam"   # yamalar BASARIYLA bitince yazilir (kaynak agacinin disinda: git kirli sayilmaz)

# Yama dosyalari patches/SHA256SUMS ile dogrulanir (yama_bekcisi.py ile ayni tablo); tutmayan yama uygulanmaz.
command -v sha256sum >/dev/null 2>&1 || { echo "HATA: sha256sum bulunamadi (coreutils)." >&2; exit 1; }
(cd "$REPO_DIR" && sha256sum -c --quiet patches/SHA256SUMS) || { echo "HATA: patches/ dosyalari patches/SHA256SUMS ile uyusmuyor; yamalar degismis ya da bozuk. Derleme durduruldu." >&2; exit 1; }
SERI_SHA="$(sha256sum "$REPO_DIR/patches/SERIES.txt" | cut -d' ' -f1)"

if [[ ! -d "$SRC_DIR/.git" ]]; then
  echo "== stable-diffusion.cpp klonlaniyor ($SDCPP_HASH)"
  mkdir -p "$ROOT/engine"
  git clone --quiet https://github.com/leejet/stable-diffusion.cpp "$SRC_DIR"
  git -C "$SRC_DIR" checkout --quiet "$SDCPP_HASH"
  git -C "$SRC_DIR" submodule update --init --recursive --quiet
fi
[[ "$(git -C "$SRC_DIR" rev-parse HEAD)" == "$SDCPP_HASH" ]] || { echo "HATA: engine/src beklenen surumde degil (beklenen $SDCPP_HASH). engine/src klasorunu silip yeniden calistirin." >&2; exit 1; }
[[ "$(git -C "$SRC_DIR/ggml" rev-parse HEAD)" == "$GGML_HASH" ]] || { echo "HATA: ggml altmodulu beklenen surumde degil (beklenen $GGML_HASH). engine/src klasorunu silip yeniden calistirin." >&2; exit 1; }

BEKLENEN_ISARET="sdcpp=$SDCPP_HASH ggml=$GGML_HASH seri=$SERI_SHA"
if [[ -f "$ISARET" && "$(cat "$ISARET")" == "$BEKLENEN_ISARET" ]]; then
  echo "== Yamalar zaten uygulanmis (isaret dosyasi eslesiyor); atlaniyor"
else
  # Isaret yok ya da eslesmiyor: agac TEMIZ olmali (yarim/kirli yama durumu sessizce atlanmaz)
  if [[ -n "$(git -C "$SRC_DIR" status --porcelain)" || -n "$(git -C "$SRC_DIR/ggml" status --porcelain)" ]]; then
    echo "HATA: engine/src degistirilmis ama yamalar tamam isareti yok (yarim yama ya da elle degisiklik). engine/src klasorunu silip yeniden calistirin." >&2
    exit 1
  fi
  echo "== Yamalar uygulaniyor (patches/SERIES.txt)"
  yama_geri_al() {
    git -C "$SRC_DIR/ggml" reset --hard --quiet "$GGML_HASH" || true
    git -C "$SRC_DIR" reset --hard --quiet "$SDCPP_HASH" || true
  }
  while IFS= read -r satir || [[ -n "$satir" ]]; do
    satir="${satir%%#*}"
    satir="$(echo "$satir" | xargs)"
    [[ -z "$satir" ]] && continue
    case "$satir" in
      ggml/*) hedef="$SRC_DIR/ggml" ;;
      sdcpp/*) hedef="$SRC_DIR" ;;
      *) echo "HATA: patches/SERIES.txt taniyamadigi satir: $satir" >&2; yama_geri_al; exit 1 ;;
    esac
    if ! git -C "$hedef" apply "$REPO_DIR/patches/$satir"; then
      echo "HATA: yama uygulanamadi: $satir; kaynak agaci sabit surume geri alindi." >&2
      yama_geri_al; exit 1
    fi
  done < "$REPO_DIR/patches/SERIES.txt"
  printf '%s' "$BEKLENEN_ISARET" > "$ISARET"
fi

CUDA_ARCH="${VT_CUDA_ARCH:-}"
if [[ -z "$CUDA_ARCH" ]] && command -v nvidia-smi >/dev/null 2>&1; then
  cc="$(nvidia-smi --query-gpu=compute_cap --format=csv,noheader 2>/dev/null | head -n1 | tr -d '.[:space:]' || true)"
  [[ -n "$cc" ]] && CUDA_ARCH="$cc"
fi
[[ -z "$CUDA_ARCH" || "$CUDA_ARCH" =~ ^[0-9]+(\;[0-9]+)*$ ]] || { echo "HATA: VT_CUDA_ARCH/compute_cap degeri gecersiz: $CUDA_ARCH (ornek: 86 ya da 61;86)" >&2; exit 1; }
CUDA_ARCH="${CUDA_ARCH:-61;75;80;86;89}"

# CUDA çekirdek derlemesi iş başına ~3-4 GB RAM kullanabilir; kullanılabilir RAM'e göre güvenli -j seç.
JOBS="${VT_BUILD_JOBS:-}"
if [[ -z "$JOBS" ]]; then
  avail_kb="$(awk '/MemAvailable/ {print $2}' /proc/meminfo 2>/dev/null || echo 8388608)"
  avail_gb=$(( avail_kb / 1024 / 1024 ))
  JOBS=$(( avail_gb / 4 ))
  [[ "$JOBS" -lt 1 ]] && JOBS=1
  [[ "$JOBS" -gt 4 ]] && JOBS=4
fi

GEN_ARGS=()
command -v ninja >/dev/null 2>&1 && GEN_ARGS=(-G Ninja)

CC_ARGS=()
if [[ -x "$TC_ENV/bin/x86_64-conda-linux-gnu-gcc" && -x "$TC_ENV/bin/x86_64-conda-linux-gnu-g++" ]]; then
  CC_ARGS+=(
    "-DCMAKE_C_COMPILER=$TC_ENV/bin/x86_64-conda-linux-gnu-gcc"
    "-DCMAKE_CXX_COMPILER=$TC_ENV/bin/x86_64-conda-linux-gnu-g++"
    "-DCMAKE_CUDA_HOST_COMPILER=$TC_ENV/bin/x86_64-conda-linux-gnu-g++"
    "-DCUDAToolkit_ROOT=$TC_ENV"
  )
fi

echo "== CMake & CUDA derlemesi (arch=$CUDA_ARCH, jobs=$JOBS)"
cmake -S "$SRC_DIR" -B "$BUILD_DIR" "${GEN_ARGS[@]}" \
  -DCMAKE_BUILD_TYPE=Release \
  -DSD_CUDA=ON \
  -DCMAKE_CUDA_ARCHITECTURES="$CUDA_ARCH" \
  -DGGML_NATIVE=OFF \
  "${CC_ARGS[@]}"

cmake --build "$BUILD_DIR" --config Release --target sd-cli -j "$JOBS"

mkdir -p "$BIN_DIR"
cp -f "$BUILD_DIR/bin/sd-cli" "$BIN_DIR/sd-cli"
chmod +x "$BIN_DIR/sd-cli"
(cd "$BIN_DIR" && sha256sum sd-cli > SHA256SUMS)   # derlenen ikilinin parmak izi (karsilastirma ve hata raporu icin)
echo "DERLE_OK: $BIN_DIR/sd-cli (sha256 $BIN_DIR/SHA256SUMS)"
