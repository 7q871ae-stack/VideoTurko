# Kart profilleri / Per-card results (EN + TR)

One row per card that has run VideoTurko. Data only: quality settings are fixed for every card (6 steps, cfg 1, 640x384 default, non-tiled VAE, seed 42) and are never part of a profile. Add your card with a PR or an issue; label every number.

Her satır VideoTurko'yu çalıştırmış bir kart. Yalnız veri: kalite ayarları her kartta sabittir ve profile girmez. Kartınızı PR ya da issue ile ekleyin; her sayıyı etiketleyin.

| Card / Kart | Compute capability | VRAM | Engine / Motor | Extra setting / Ek ayar | Longest run / En uzun koşu | Time / Süre | Evidence / Kanıt |
|---|---|---|---|---|---|---|---|
| GTX 1050 Ti | 6.1 | 4 GB | release `sm_61` (v0.1.0 zip) | none | 209 frames, peak 3777 MiB | 3414 s (run U209) | [measured, authors] `docs/OLCUMLER.md` |
| RTX 4070 Ti | 8.9 | 12 GB | release `sm_61` (v0.1.0 zip) | `GGML_CUDA_CUBLAS_COMPUTE_TYPE=f32` at 141+ frames (automatic since v0.1.1) | 141 frames in one process (black video fixed; that textured scene was gate RED, noise 1.76); 720x1280 at 107 frames | 141 frames: DiT about 210 s | [user-reported, issue #1] `docs/OLCUMLER.md` section 8 |
| RTX 5060 Laptop | 12.0 | 8 GB | native `sm_120` build (CUDA 12.8.1) | none; the release `sm_61` engine was black at 56+ frames with the v0.1.0 script | 209 frames, peak 7438/8151 MiB; 192 frames with `-InitImg` | 209 frames: 356 s | [user-reported, PR #3] `docs/RTX5060_TEST_RAPORU.md` |
| RTX 4060 | 8.9 | 8 GB (8188 MiB) | native `sm_89` build from `patches/` (CUDA Toolkit 12.8, CUDA 12 runtime); local VideoTurko v0.1.0 checkout with the pre-v0.1.1 `uret.ps1` | driver 621.24, `nvidia-smi` CUDA UMD 13.5; `VT_ENGINE_BIN=<ROOT>\engine_sm89\bin`, `VT_MODEL_DIR=<ROOT>\models`; `f32` cuBLAS not set (v0.1.0 script) | 141 frames, 640x384, 24 fps, seed 42, peak 7572/8188 MiB, `KAPI GECTI` | 141 frames: 224 s | [user-reported, measured] console log kept locally (not committed); `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\uret.ps1 -Istem <PROMPT> -Kare 141 -Cikti <OUT>\video.avi` |

Open question / Açık soru: does the release `sm_61` engine work on RTX 50 with the v0.1.1 script (f32 on)? / Hazır `sm_61` motor RTX 50'de v0.1.1 betiğiyle (f32 açık) çalışıyor mu?
