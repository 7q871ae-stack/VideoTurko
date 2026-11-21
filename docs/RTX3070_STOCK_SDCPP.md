# RTX 3070 8 GB with the stock stable-diffusion.cpp CUDA release / RTX 3070 8 GB, hazır stable-diffusion.cpp CUDA sürümüyle (EN + TR)

**EN** Short note from one machine: desktop RTX 3070, 8 GB, 31 GB RAM, Windows, driver 610.88. Label for everything below: [user-reported, this PR]; each number is [measured] from the engine log unless marked [read], [computed] or [guess]. The runs were made by Claude Code (an AI coding agent) on my PC over SSH; I watched and checked the outputs. They did **not** go through `scripts/uret.ps1` and the quality gate (`scripts/uretim_kapi.ps1`) was **not** run, so the gate result is unknown.

**TR** Tek makineden kısa not: masaüstü RTX 3070, 8 GB, 31 GB RAM, Windows, sürücü 610.88. Aşağıdaki her şey [user-reported, this PR] etiketlidir; her sayı motor günlüğünden [measured]'dir, aksi belirtilmedikçe ([read], [computed] ya da [guess]). Koşuları Claude Code (yapay zekâ kod ajanı) SSH ile PC'mde çalıştırdı; ben izledim ve çıktıları kontrol ettim. Koşular `scripts/uret.ps1` üzerinden **yapılmadı** ve kalite kapısı (`scripts/uretim_kapi.ps1`) **çalıştırılmadı**; kapı sonucu bilinmiyor.

> **Community report / Topluluk bildirimi.** EN: maintainers have not measured this card. TR: bakımcılar bu kartı ölçmedi.

## Engine / Motor

- stable-diffusion.cpp release `master-1106-532d2c1` (commit `532d2c1`), no patches from this repo [read: GitHub release page].
- `sd-master-532d2c1-bin-win-cuda12-x64.zip`, 412,365,497 bytes, sha256 `b087219145a382cc1b1e826318289e1f672b9bb6965977734ef0deb85fe2d03a` [read: GitHub release digest].
- `cudart-sd-bin-win-cu12-x64.zip`, 563,452,046 bytes, sha256 `fe20366827d357c00797eebb58244dddab7fd9a348d70090c3871004c320f38d` [read].
- The release CUDA build lists `sm_86` among its architectures [read: `.github/workflows/build.yml` of that release, `CMAKE_CUDA_ARCHITECTURES='61;70;75;80;86;89;90;100;120'`]; it ran on the RTX 3070 (compute capability 8.6) without a local build [measured].
- Models: the four files of `scripts/modeller.json`, sha256 checked [measured].

## Command / Komut

```
sd-cli.exe -M vid_gen --diffusion-model minimax_h3_fl2va_hyperflow_flash_14b-Q4_K_M.gguf --llm qwen3vl_32b_minimax_h3-Q4_K_M.gguf
  --vae minimax_h3_sol_vae_fp16.safetensors --audio-vae minimax_h3_audio_vae_fp32.safetensors --prompt-file prompt.txt
  -W 640 -H 384 --video-frames <N> --fps 24 --steps 6 --sampling-method euler
  --sigmas 1.0,0.982655942,0.914642572,0.674755692,0.385223746,0.159055337,0.0 --cfg-scale 1.0 --rng cpu --seed 42
  --flash-attn diffusion=on --offload-to-cpu --mmap -v -o out.avi
```

- Prompt: the text of `docs/ornek_istem_R0.txt`, with the one curly apostrophe written as a plain `'` [measured: file comparison].
- One process (DiT, audio VAE and video VAE). No VAE tiling flag; no "retrying with temporal tiling" line in any log [measured].
- `--max-vram` not set; the engine's automatic placement (`--auto-fit`, default on) chose the budget [read: `sd-cli --help`].

## Results / Sonuçlar (640x384, 24 fps, seed 42)

| Frames / Kare | Result / Sonuç | `generate_video` | Sampling / Örnekleme | Text encoding | DiT compute buffer (VRAM) | VAE compute buffer (VRAM) |
|---|---|---|---|---|---|---|
| 56 (2.3 s) | ok | 74.0 s | 42.0 s | 20.3 s | 1046.9 MB | 777.4 MB |
| 209 (8.7 s) | ok | 182.0 s | 138.9 s (step ~20.6 s) | 21.9 s | 3792.9 MB | 2821.2 MB |
| 243 (10.1 s) | ok, longest in one pass / tek geçişte en uzun | 211.3 s | 166.6 s (step ~25.5 s) | 21.1 s | 4403.2 MB | 3276.2 MB |
| 260 (10.8 s) | out of VRAM before sampling / örneklemeden önce bellek yetmedi | - | - | 18.4 s | need 6009.2 MB, budget 5383.5 MB, available 5892.3 MB | - |

277, 294 and 311 frames failed the same way (need 6195 / 6792 / 7123 MB) [measured].

- The buffer columns are the engine's own `compute buffer size` lines, not a whole-card `nvidia-smi` peak; the whole-card peak was not recorded. The desktop uses about 1.4 GB of the card [computed: 8191 MB total minus the 6747 MB the engine reported free at start].
- The engine kept all weights in RAM: `total params memory size = 30040.19MB (VRAM 0.00MB, RAM 30040.19MB)` [measured].
- 243 frames, looked at every 30th frame: the kitten, board and background stay the same for 10.1 s; the motion may loop (first and middle frames look very alike) [guess: not checked frame by frame].

## Larger picture size / Büyük çözünürlük (1344x768)

A different prompt (an aerial dawn shot) and seed 101 were used here, so these are not comparable to the table above.

| Frames | Result | `generate_video` | DiT compute buffer (VRAM) |
|---|---|---|---|
| 56 (2.3 s) | ok, step ~23.6 s | 192.4 s | 4267.0 MB |
| 73 (3.0 s) | out of VRAM | - | need 7004.4 MB, budget 5982.2 MB, available 6747.0 MB |
| 192 (8.0 s) | out of VRAM | - | need 16497.5 MB, budget 15475.2 MB |

- `minimax_h3_attn_chunk_budget=1` did not lower the 73-frame need [measured].
- Two-stage sampling (`--hires --hires-upscaler "Latent (bicubic)" --hires-width 1344 --hires-height 768 --hires-steps 4 --hires-denoising-strength 0.4`) at 56 frames: 176.4 s, first pass at 640x384 43.5 s; the second pass uses the same 4267.0 MB buffer, so it has the same frame limit [measured].
- 640x384 at 8 GB is not limited by speed but by frame count at larger sizes; a card with more free VRAM should go further [guess].

## Not covered / Kapsanmayan

- No quality gate run, no byte comparison with the R0 reference, no `-InitImg` run.
- Fast hand movement (a fish being lifted) jumped in a few frames in one 640x384 clip; I have no tested fix [measured: visual check of one clip].
