# AMD (RX 9070 XT): Vulkan and ROCm / AMD kartlar: Vulkan ve ROCm (EN + TR)

**EN** Short note from one machine: RX 9070 XT, 16 GB, Windows 11. Label for everything below: [user-reported, this PR]; each number is [measured] unless marked [read] or [guess]. The release engine of this repo is CUDA (`sm_61`) and does not run on AMD, so a stable-diffusion.cpp release build was used instead. No patch from `patches/` was applied. Quality settings are the fixed ones (6 steps, cfg 1, 640x384, seed 42, non-tiled VAE).

**TR** Tek makineden kısa not: RX 9070 XT, 16 GB, Windows 11. Aşağıdaki her şey [user-reported, this PR] etiketlidir; her sayı [measured]'dir, aksi belirtilmedikçe ([read] ya da [guess]). Bu deponun hazır motoru CUDA (`sm_61`) olduğu için AMD'de çalışmaz; bunun yerine stable-diffusion.cpp'nin hazır sürümü kullanıldı. `patches/` içinden hiçbir yama uygulanmadı. Kalite ayarları sabit olanlardır (6 adım, cfg 1, 640x384, seed 42, parçasız VAE).

## Engine / Motor

- stable-diffusion.cpp release `master-1106-532d2c1` (commit `532d2c1`) [read: GitHub release page].
- ROCm asset: `sd-master-532d2c1-bin-win-rocm-10.1.0-x64.zip`, 283,581,117 bytes, sha256 `b10fcc88f5a37adc1b63e0c1bd06fcbc8212340a68b96022b45d72e64c9e45a1` [read: GitHub release digest; the downloaded file matched].
- Vulkan asset: `sd-master-532d2c1-bin-win-vulkan-x64.zip`, 30,312,081 bytes [read].
- `amdhip64_7.dll` inside the ROCm zip reports file version `10.0.3684.0` [measured: file properties].
- This sd.cpp version already knows the `hyperflow-h3-flash-6` sigmas preset and the `minimax_h3_attn_chunk_budget` model argument [measured: the `--sigmas` presets are listed by `sd-cli --help`, and both builds accepted the model argument], so no patch was needed for the recipe in these runs.

## Command line / Komut satırı

```
set HIP_VISIBLE_DEVICES=1
sd-cli.exe -M vid_gen ^
  --diffusion-model <MODEL_DIR>\minimax_h3_fl2va_hyperflow_flash_14b-Q4_K_M.gguf ^
  --llm <MODEL_DIR>\qwen3vl_32b_minimax_h3-Q4_K_M.gguf ^
  --vae <MODEL_DIR>\minimax_h3_sol_vae_fp16.safetensors ^
  --audio-vae <MODEL_DIR>\minimax_h3_audio_vae_fp32.safetensors ^
  --prompt-file prompt.txt -W 640 -H 384 --video-frames 209 --fps 24 ^
  --steps 6 --sampling-method euler --sigmas hyperflow-h3-flash-6 --cfg-scale 1.0 ^
  --rng cpu --seed 42 -t 4 --flash-attn off,diffusion=on ^
  --model-args minimax_h3_attn_chunk_budget=0.03 ^
  --offload-to-cpu --mmap --backend te=cpu -o out.avi
```

- Vulkan: the same line without `HIP_VISIBLE_DEVICES` (the release Vulkan build). The Vulkan 56/141/209-frame runs in `docs/KART_PROFILLERI.md` used the default `minimax_h3_attn_chunk_budget=0.05`; see `docs/SIK_HATALAR.md` item 25 for why `0.03` was used later.
- Image-to-video: add `--init-img first_frame.png` (192 frames measured on ROCm).
- `HIP_VISIBLE_DEVICES`: on this machine the integrated GPU is ROCm device 0 and the RX 9070 XT is device 1 [measured: llama.cpp's `llama-bench --list-devices` with the variable unset listed both, iGPU first; with `HIP_VISIBLE_DEVICES=1` `sd-cli --list-devices` showed only the RX 9070 XT]. Set the number of your discrete card.
- No VAE tiling flags, as in `scripts/uret.ps1`.

TR: Vulkan için aynı satır, `HIP_VISIBLE_DEVICES` olmadan (hazır Vulkan sürümü). `docs/KART_PROFILLERI.md`'deki Vulkan 56/141/209 kare koşuları varsayılan `minimax_h3_attn_chunk_budget=0.05` ile yapıldı; `0.03`'ün neden kullanıldığı için `docs/SIK_HATALAR.md` madde 25. Görselden videoya: `--init-img ilk_kare.png` (ROCm'da 192 kare ölçüldü). Bu makinede tümleşik ekran kartı ROCm aygıt 0, RX 9070 XT aygıt 1'dir [measured: llama.cpp `llama-bench --list-devices`; `HIP_VISIBLE_DEVICES=1` ile `sd-cli --list-devices` yalnız RX 9070 XT'yi gösterdi]; kendi ayrık kartınızın numarasını yazın. VAE tiling bayrağı yok.

## Missing `hipblas.dll` / Eksik çıkan `hipblas.dll`

**EN** The ROCm zip does not contain `hipblas.dll`. An import scan of `stable-diffusion.dll` found `hipblas.dll` as the only DLL name that is neither in the zip folder nor in System32 [measured], and after adding the files below the DLL loaded [measured]. (The load error before adding them was not captured for this DLL; for llama.cpp's `ggml-hip.dll` the same missing name gave "could not find the module (or one of its dependencies)" [measured].) What was added next to `sd-cli.exe` (the DLL files are NOT in this repo, only names, sizes and hashes):

| File added | Size (bytes) | sha256 |
|---|---|---|
| `libhipblas.dll`, renamed to `hipblas.dll` | 716,696 | `6055254510d720213f6f835efb92f3d08dc49d5023dd0a14c00111771051a74e` |
| `rocblas.dll` | 41,072,536 | `5c001a3a4693f344899d36bc31c6202681fa467e9e25b127a42067c6732b3fc5` |
| `libhipblaslt.dll` | 6,012,312 | `9f97d95c3b7257efcab992914b4e1c1b3b71b0693a6ad5d61a8f3cbf08a96dee` |
| folders `rocblas/` and `hipblaslt/` | | |

- **Version: unknown.** The files have no version resource (file properties are empty), and a simple text search for version strings in them found nothing [measured]. The version cannot be given.
- Origin: the folder of a llama.cpp `b9592` HIP build on the same machine [read]. The exact zip the files came from was not recorded; the HIP asset of that release is named `llama-b9592-bin-win-hip-radeon-x64.zip` [read: GitHub release page].
- With these files the ROCm runs in `docs/KART_PROFILLERI.md` finished without errors [measured]. Nothing else about this mix is claimed.

**TR** ROCm zip'inde `hipblas.dll` yok. `stable-diffusion.dll`'in içe aktarma taramasında zip klasöründe de System32'de de olmayan tek DLL adı `hipblas.dll` çıktı [measured]; aşağıdaki dosyalar eklenince DLL yüklendi [measured]. (Ekleme öncesi yükleme hatası bu DLL için kaydedilmedi; llama.cpp'nin `ggml-hip.dll`'inde aynı eksik ad "modül (ya da bağımlılıklarından biri) bulunamadı" hatasını verdi [measured].) `sd-cli.exe`'nin yanına eklenenler yukarıdaki tabloda (DLL dosyaları bu depoya KONMAZ; yalnız ad, boyut ve özet). **Sürüm bilinmiyor:** dosyaların sürüm kaynağı boş, içlerinde basit bir metin aramasıyla sürüm metni de bulunamadı [measured]; sürüm verilemez. Kaynak: aynı makinedeki bir llama.cpp `b9592` HIP derlemesinin klasörü [read]; dosyaların geldiği zip'in adı kaydedilmemiş, o sürümün HIP dosyası `llama-b9592-bin-win-hip-radeon-x64.zip` adını taşıyor [read]. Bu dosyalarla `docs/KART_PROFILLERI.md`'deki ROCm koşuları hatasız bitti [measured]; bu karışım hakkında başka bir şey iddia edilmiyor.

## Result / Sonuç

Times, VRAM peaks and prompts: see the RX 9070 XT row in `docs/KART_PROFILLERI.md`. / Süreler, VRAM tepeleri ve istemler: `docs/KART_PROFILLERI.md` içindeki RX 9070 XT satırı.
