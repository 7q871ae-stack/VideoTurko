# RTX 3070 8 GB with the stock stable-diffusion.cpp CUDA release / RTX 3070 8 GB, hazır stable-diffusion.cpp CUDA sürümüyle (EN + TR)

**EN** Short note from one machine: desktop RTX 3070, 8 GB, 31 GB RAM, Windows, driver 610.88. Label for everything below: [user-reported, PR #6]; each number is [measured] from the engine log unless marked [read], [computed] or [guess]. The runs were made by Claude Code (an AI coding agent) on my PC over SSH; I watched and checked the outputs. They did **not** go through `scripts/uret.ps1` and the quality gate (`scripts/uretim_kapi.ps1`) was **not** run, so the gate result is unknown.

**TR** Tek makineden kısa not: masaüstü RTX 3070, 8 GB, 31 GB RAM, Windows, sürücü 610.88. Aşağıdaki her şey [user-reported, PR #6] etiketlidir; her sayı motor günlüğünden [measured]'dir, aksi belirtilmedikçe ([read], [computed] ya da [guess]). Koşuları Claude Code (yapay zekâ kod ajanı) SSH ile PC'mde çalıştırdı; ben izledim ve çıktıları kontrol ettim. Koşular `scripts/uret.ps1` üzerinden **yapılmadı** ve kalite kapısı (`scripts/uretim_kapi.ps1`) **çalıştırılmadı**; kapı sonucu bilinmiyor.

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

## Image-to-video with your own first frame / Kendi ilk karenle resimden video (`--init-img`)

**EN** Added after PR #6, same machine, same engine and command as above plus `--init-img`; started with `sd-cli` directly, not through `scripts/uret.ps1`, gate not run.

| Run | Prompt | Frames | `generate_video` | Sampling | DiT compute buffer (VRAM) | Result |
|---|---|---|---|---|---|---|
| text only, seed 202 | the whole scene: a fisherman on the Galata Bridge, the Golden Horn and the old city skyline behind him | 189 | not recorded here | - | - | a made-up skyline, no Galata Tower [measured: visual check, frames 0, 94, 185] |
| `--init-img`, seed 202 | only the motion and the sound: the fisherman casts, "the background stays still and unchanged"; the init image shows the Galata Tower | 189 requested, 192 written | 175.4 s | 130.0 s | 3510.8 MB | the tower and the skyline of the init image stay for the whole 8 s; the fisherman casts [measured: visual check, frames 0, 94, 185] |

- The init image was a 1280x768 still made with another open model (Z-Image Turbo, Apache-2.0), scaled to 640x384 PNG before the run [measured].
- 189 is not on the 17k+5 grid; the engine wrote 192 frames, as `AGENTS.md` says [measured: ffprobe].
- What helped: put the scene (who is where, which landmark, what is in the background) into the still, and let the prompt describe only the motion and the sound. A text-only prompt that named the landmark ("a single Galata Tower, only one tower") gave one tower but almost no motion in a run on another stack (ComfyUI, pruned Q4_K model) [measured, other stack, not this engine].

**TR** PR #6'dan sonra eklendi; aynı makine, yukarıdaki motor ve komut, üstüne `--init-img`. `sd-cli` doğrudan başlatıldı, `scripts/uret.ps1` kullanılmadı, kapı çalıştırılmadı.

- Sahnenin tamamını anlatan istemle (seed 202) siluet uydurma, Galata Kulesi yok [ölçtüm: 0, 94 ve 185. kareler]. Aynı seed ile `--init-img` verilince ilk karedeki kule ve siluet 8 sn boyunca duruyor, balıkçı oltayı atıyor; 175,4 sn, örnekleme 130,0 sn, DiT tamponu 3510,8 MB [ölçtüm].
- İlk kare başka bir açık modelle (Z-Image Turbo, Apache-2.0) 1280x768 üretildi, koşudan önce 640x384 PNG'ye küçültüldü. 189 kare istendi, motor 192 yazdı.
- İşe yarayan: sahneyi (kim nerede, hangi yapı, arkada ne var) ilk kareye koy, istem yalnız hareketi ve sesi anlatsın.

## Upscaling to 1080p / 1080p'ye büyütme

**EN** VideoTurko writes 640x384. These are the upscalers I ran on the same RTX 3070 8 GB on H3 output from this engine; none of them is part of this repo, check each project's licence yourself. Times are from my run logs [measured].

| Tool | Setting | Input | Time | What I saw |
|---|---|---|---|---|
| Real-ESRGAN ncnn-vulkan, `realesrgan-x4plus` | x4, PNG frames | 30 s film, 720 frames | 622 s | slow |
| Real-ESRGAN ncnn-vulkan, `realesr-general-x4v3` (official weight converted to ncnn) | x4, `-j 2:4:4`, JPG frames | 30 s film, 720 frames | 38.6 s | fast, leaves halos at edges [measured: visual check] |
| SeedVR2 (`numz/ComfyUI-SeedVR2_VideoUpscaler` `4490bd1`, `inference_cli.py`, 3B fp8) | `--resolution 768`, batch 9, DiT on CPU, `--blocks_to_swap 32`, tiled VAE 512/32 | one 8 s shot, 189 frames | 373 s | best on faces, beard and fabric |
| FlashVSR v1.1 (`lihaoyun6/ComfyUI-FlashVSR_Ultra_Fast` `4820b3f`) | mode `tiny`, scale 2, tiled DiT 256 / overlap 24, tiled VAE, `sparse_sage_attention` | one 8 s shot, 192 frames | 125-130 s (5 runs) | close to SeedVR2; tile 512 ran out of memory |

- My pick: FlashVSR x2 to 1280x768, then `ffmpeg` lanczos to 1920x1152 and a crop to 1920x1080. FlashVSR writes no audio; take it from the H3 file [measured].
- In a side-by-side look FlashVSR x2 beat a mix of SeedVR2 (faces) and general-x4v3 (background) [user-reported: my own visual judgement].
- Watch wide water shots: FlashVSR can leave a fine grid pattern there [measured: one shot].

**TR** Aynı RTX 3070 8 GB'ta, bu motorun H3 çıktısında çalıştırdığım büyütücüler. Hiçbiri bu reponun parçası değil; lisanslarına kendin bak. Süreler koşu günlüklerimden [ölçtüm].

- Real-ESRGAN `x4plus`: 30 sn'lik film (720 kare) 622 sn. `general-x4v3` (resmi ağırlık ncnn'e çevrildi): aynı film 38,6 sn, kenarlarda hare bırakıyor.
- SeedVR2 (`--resolution 768`): 8 sn'lik çekim (189 kare) 373 sn, yüzde ve kumaşta en iyisi.
- FlashVSR v1.1 `tiny`, 2 kat, tile 256: 8 sn'lik çekim (192 kare) 125-130 sn; tile 512 belleğe sığmadı. Seçimim bu: 2 kat 1280x768, sonra `ffmpeg` lanczos ile 1920x1152 ve 1080p'ye kırpma; ses H3 dosyasından alınır. Geniş su çekimlerinde ince ızgara desenine bak.

## Not covered / Kapsanmayan

- No quality gate run, no byte comparison with the R0 reference; `--init-img` was run with `sd-cli` directly, not through `uret.ps1 -InitImg`.
- Fast hand movement (a fish being lifted) jumped in a few frames in one 640x384 clip; I have no tested fix [measured: visual check of one clip].
