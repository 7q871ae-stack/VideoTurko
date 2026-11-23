#!/usr/bin/env bash
# VideoTurko Linux CUDA derleme betiği: stable-diffusion.cpp (32d516c) + patches/SERIES.txt yamaları.
# Bellek taşmasını (OOM) önlemek için paralel iş sayısı (-j) kullanılabilir RAM'e göre sınırlanır.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="${VT_ROOT:-$(cd "$SCRIPT_DIR/.." && pwd)}"
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

if [[ ! -d "$SRC_DIR/.git" ]]; then
  echo "== stable-diffusion.cpp klonlanıyor (32d516c)"
  mkdir -p "$ROOT/engine"
  git clone --quiet https://github.com/leejet/stable-diffusion.cpp "$SRC_DIR"
  git -C "$SRC_DIR" checkout --quiet 32d516c
  git -C "$SRC_DIR" submodule update --init --recursive --quiet
fi

if [[ -z "$(git -C "$SRC_DIR" status --porcelain)" ]]; then
  echo "== Yamalar uygulanıyor (patches/SERIES.txt)"
  while IFS= read -r satir || [[ -n "$satir" ]]; do
    satir="${satir%%#*}"
    satir="$(echo "$satir" | xargs)"
    [[ -z "$satir" ]] && continue
    if [[ "$satir" == ggml/* ]]; then
      git -C "$SRC_DIR/ggml" apply "$ROOT/patches/$satir"
    elif [[ "$satir" == sdcpp/* ]]; then
      git -C "$SRC_DIR" apply "$ROOT/patches/$satir"
    fi
  done < "$ROOT/patches/SERIES.txt"
else
  echo "== Yamalar zaten uygulanmış görünüyor; atlanıyor"
fi

CUDA_ARCH="${VT_CUDA_ARCH:-}"
if [[ -z "$CUDA_ARCH" ]] && command -v nvidia-smi >/dev/null 2>&1; then
  cc="$(nvidia-smi --query-gpu=compute_cap --format=csv,noheader 2>/dev/null | head -n1 | tr -d '.[:space:]' || true)"
  [[ -n "$cc" ]] && CUDA_ARCH="$cc"
fi
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
echo "DERLE_OK: $BIN_DIR/sd-cli"
