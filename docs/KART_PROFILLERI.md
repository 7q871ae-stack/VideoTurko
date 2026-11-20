# Kart profilleri / Per-card results (EN + TR)

One row per card that has run VideoTurko. Data only: quality settings are fixed for every card (6 steps, cfg 1, 640x384 default, non-tiled VAE, seed 42) and are never part of a profile. Add your card with a PR or an issue; label every number.

Her satır VideoTurko'yu çalıştırmış bir kart. Yalnız veri: kalite ayarları her kartta sabittir ve profile girmez. Kartınızı PR ya da issue ile ekleyin; her sayıyı etiketleyin.

| Card / Kart | Compute capability | VRAM | Engine / Motor | Extra setting / Ek ayar | Longest run / En uzun koşu | Time / Süre | Evidence / Kanıt |
|---|---|---|---|---|---|---|---|
| GTX 1050 Ti | 6.1 | 4 GB | release `sm_61` (v0.1.0 zip) | none | 209 frames, peak 3777 MiB | 3414 s (run U209) | [measured, authors] `docs/OLCUMLER.md` |
| RTX 4070 Ti | 8.9 | 12 GB | release `sm_61` (v0.1.0 zip) | `GGML_CUDA_CUBLAS_COMPUTE_TYPE=f32` at 141+ frames (automatic since v0.1.1) | 141 frames in one process (black video fixed; that textured scene was gate RED, noise 1.76); 720x1280 at 107 frames | 141 frames: DiT about 210 s | [user-reported, issue #1] `docs/OLCUMLER.md` section 8 |
| RTX 5060 Laptop | 12.0 | 8 GB | native `sm_120` build (CUDA 12.8.1) | none; the release `sm_61` engine was black at 56+ frames with the v0.1.0 script | 209 frames, peak 7438/8151 MiB; 192 frames with `-InitImg` | 209 frames: 356 s | [user-reported, PR #3] `docs/RTX5060_TEST_RAPORU.md` |

Open question / Açık soru: does the release `sm_61` engine work on RTX 50 with the v0.1.1 script (f32 on)? / Hazır `sm_61` motor RTX 50'de v0.1.1 betiğiyle (f32 açık) çalışıyor mu?
