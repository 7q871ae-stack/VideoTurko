# macOS (Apple Silicon / Metal) Kurulum ve Test Raporu (TR)

> **EN summary.** Community report from PR #10 (@otnemem): VideoTurko ran on an Apple M5 Pro with 48 GB unified memory using the official stable-diffusion.cpp macOS ARM64 (Metal) release `master-1111-6874e49`, no patches, with the same quality settings (6 steps, cfg 1, 640x384, tile-less VAE, seed 42, 24 fps). Default mode: 209 frames in about 704 s; optional 48 GB mode (`TAM_METAL=1`): 56 frames in about 105 s. All numbers are [user-reported, PR #10]; the maintainers have no Mac and did not re-measure them. Mode B was checked by eye only; its numeric equivalence to Mode A is not measured. The quality gate did not run on this Mac (no OpenCV). macOS is not an officially supported platform. Helper script: `scripts/mac_uret.sh`.
>
> **Kaynak / Source:** [kullanıcı bildirdi, PR #10]; bakımcılar Mac'te ölçmedi. Bakımcıların doğruladığı tek şey: motor zip'inin sha256'sı upstream sürüm kaydıyla aynı [ölçtük, 2026-11-23]. Zip adındaki `macOS-26.7.2`, upstream'in derlediği makinenin sürümüdür; aşağıdaki macOS sürümü katkıcının makinesidir.
>
> **Lisans ve bölge / License and region:** MiniMax H3 çıktısının kullanımı AB, Birleşik Krallık, Güney Kore ve ABD'de kısıtlıdır; modeli indirmeden önce `docs/LISANS_KABUL.txt` ve `docs/LISANS_UYARISI.md` okunur. Lisansı kullanıcı kabul eder, ajan kabul etmez. / Output use is restricted in the EU, UK, South Korea and the US; read `docs/LISANS_UYARISI.md` first. The user accepts the license, never an agent.

**Donanım:** MacBook Pro (`Mac17,12`), Apple M5 Pro — 18 çekirdek CPU (6 Super + 12 Performance), 20 çekirdek dahili GPU (`MTL0`, `MTLGPUFamilyApple10`, `MTLGPUFamilyMetal4`, `recommendedMaxWorkingSetSize = 40200.90 MB`), **48 GB birleşik bellek**, **macOS 27.2.1** (`arm64`, Build `26B8132`) `[kullanıcı bildirdi]`.  
**Tarih:** 2026-11-23  
**Motor:** `stable-diffusion.cpp` resmî hazır macOS ARM64 (Metal) sürümü `master-1111-6874e49` (`sd-master-6874e49-bin-Darwin-macOS-26.7.2-arm64.zip`, 36,6 MB, sha256 `6142da141ee5662d9c2fda88c2d032d8c3b5482ad14dc988bdd74b9123b59661`), `patches/` içinden yama uygulanmadı `[kullanıcı bildirdi]`.

> **Topluluk bildirimi:** Bu deponun hazır motoru ve `.ps1` betikleri Windows + NVIDIA CUDA (`sm_61`) içindir; macOS/Metal resmî desteklenen platform değildir. Aşağıdaki tüm sayılar katkıcının bu makinede aldığı ölçümlerdir `[kullanıcı bildirdi, PR #10]`. Kalite ayarlarına dokunulmadı: **6 adım, `cfg 1.0`, `640x384` varsayılan, karosuz (parçasız) VAE, tohum `42`, `24 fps`**.

---

## 1. Kurulum Adımları

1. **Donanım ve disk ön kontrolü `[kullanıcı bildirdi]`:** `sw_vers`, `system_profiler SPHardwareDataType SPDisplaysDataType`, `vm_stat` ve `df -h` ile birleşik bellek (48 GB) ve boş SSD alanı (en az 40 GB gerekir; ölçülen 732 GiB boş) doğrulandı.
2. **Motoru indirme ve açma `[kullanıcı bildirdi]`:** `leejet/stable-diffusion.cpp` GitHub Releases sayfasından `master-1111-6874e49` etiketli `sd-master-6874e49-bin-Darwin-macOS-26.7.2-arm64.zip` arşivi (36,6 MB) indirilip `shasum -a 256` ile (`6142da141ee5662d9c2fda88c2d032d8c3b5482ad14dc988bdd74b9123b59661`) doğrulandı ve `<ROOT>/engine_mac/bin` altına açıldı. `otool -L` ile `libstable-diffusion.dylib` (`arm64`) dosyasının `Metal.framework` ve `MetalKit.framework` ile bağlı olduğu doğrulandı.
3. **4 model dosyasını indirme ve `sha256` doğrulaması `[kullanıcı bildirdi]`:** MiniMax H3 Community License (`docs/LISANS_KABUL.txt`) okunup kabul edildikten sonra `scripts/modeller.json` içindeki 4 dosya (toplam 31.473.112.040 bayt / ~29,31 GiB) `<MODEL_DIR>` altına indirilip `shasum -a 256` ile doğrulandı:
   - `minimax_h3_fl2va_hyperflow_flash_14b-Q4_K_M.gguf` (8,4 GiB)
   - `qwen3vl_32b_minimax_h3-Q4_K_M.gguf` (17,0 GiB)
   - `minimax_h3_sol_vae_fp16.safetensors` (3,3 GiB)
   - `minimax_h3_audio_vae_fp32.safetensors` (577 MiB)
4. **Cihaz doğrulaması `[kullanıcı bildirdi]`:** `<ROOT>/engine_mac/bin/sd-cli --list-devices` çıktısında `MTL0	Apple M5 Pro` satırı doğrulandı (`recommendedMaxWorkingSetSize = 40200.90 MB`).

---

## 2. İki Çalıştırma Modu (Varsayılan vs. 48 GB İsteğe Bağlı)

Kalite ayarları her iki modda da birebir aynıdır (**6 adım, `cfg 1.0`, `640x384`, `24 fps`, tohum `42`, parçasız VAE**). Mod B bellek ve hız ayarlarını değiştirir (`--flash-attn on`, `--auto-fit on`, `budget=0`); Mod A ile sayısal eşdeğerliği ölçülmedi, çıktı yalnız gözle kontrol edildi `[denenmedi]`.

### A. İlk Çalışan Hâl — Herkes İçin Varsayılan (Güvenli Bellek Modu)
Ağırlıkları bellek eşlemeli (`--mmap`) olarak RAM'de tutar, metin kodlayıcıyı CPU'da çalıştırır ve dikkat (attention) belleğini `0.03 GiB` ile sınırlar. 209 kare (8,7 sn) tek süreçte sorunsuz tamamlanır `[kullanıcı bildirdi]`:

```bash
<ROOT>/engine_mac/bin/sd-cli -M vid_gen \
  --diffusion-model <MODEL_DIR>/minimax_h3_fl2va_hyperflow_flash_14b-Q4_K_M.gguf \
  --llm <MODEL_DIR>/qwen3vl_32b_minimax_h3-Q4_K_M.gguf \
  --vae <MODEL_DIR>/minimax_h3_sol_vae_fp16.safetensors \
  --audio-vae <MODEL_DIR>/minimax_h3_audio_vae_fp32.safetensors \
  --prompt-file <ROOT>/docs/ornek_istem_R0.txt \
  -W 640 -H 384 --video-frames 209 --fps 24 \
  --steps 6 --sampling-method euler --sigmas hyperflow-h3-flash-6 --cfg-scale 1.0 \
  --rng cpu --seed 42 -t 8 --flash-attn off,diffusion=on \
  --model-args minimax_h3_attn_chunk_budget=0.03 \
  --offload-to-cpu --mmap --backend te=cpu \
  -o <ROOT>/runs/out_209.avi
```

### B. 48 GB+ Mac İçin İsteğe Bağlı Hız Ayarı (`TAM_METAL=1`)
48 GB birleşik bellekte (~38–40 GB Metal GPU çalışma alanı), `--offload-to-cpu` ve `--backend te=cpu` kaldırılıp `--auto-fit on --flash-attn on` ve `minimax_h3_attn_chunk_budget=0` verildiğinde 30,0 GB ağırlığın tamamı doğrudan `MTL0` GPU'ya yerleşir. Metin kodlama 63,7–75,8 sn'den **4,33–4,38 sn**'ye düşer (**14,5–17,5× hızlanma**), 56 kare toplam süre **172,47 sn → 105,05 sn** olur `[kullanıcı bildirdi]`:

```bash
<ROOT>/engine_mac/bin/sd-cli -M vid_gen \
  --diffusion-model <MODEL_DIR>/minimax_h3_fl2va_hyperflow_flash_14b-Q4_K_M.gguf \
  --llm <MODEL_DIR>/qwen3vl_32b_minimax_h3-Q4_K_M.gguf \
  --vae <MODEL_DIR>/minimax_h3_sol_vae_fp16.safetensors \
  --audio-vae <MODEL_DIR>/minimax_h3_audio_vae_fp32.safetensors \
  --prompt-file <ROOT>/istem.txt \
  -W 640 -H 384 --video-frames 56 --fps 24 \
  --steps 6 --sampling-method euler --sigmas hyperflow-h3-flash-6 --cfg-scale 1.0 \
  --rng cpu --seed 42 --flash-attn on --auto-fit on \
  --model-args minimax_h3_attn_chunk_budget=0 --mmap \
  -o <ROOT>/runs/out_56_metal.avi
```

*(Yardımcı betik: `scripts/mac_uret.sh` varsayılan olarak **Mod A** ile çalışır; 48 GB+ Mac'lerde isteğe bağlı `TAM_METAL=1 scripts/mac_uret.sh <istem.txt> 56` ile **Mod B** açılır.)*

---

## 3. Ölçümler `[kullanıcı bildirdi]`

### Ana 209 Kare Ölçümü (Mod A — Varsayılan, `640x384`, 8,7 sn, 6 adım, `cfg=1.0`, `seed=42`)
- **Toplam süre (`generate_video completed`):** **703,76 sn** (11 dk 44 sn) `[kullanıcı bildirdi]`
- **Metin kodlama (`get_learned_condition`):** **75,81 sn** `[kullanıcı bildirdi]`
- **6 adım örnekleme (`sampling`):** **595,54 sn** (~99 sn/adım) `[kullanıcı bildirdi]`
- **Video VAE (`decode_first_stage`, parçasız):** **27,62 sn** `[kullanıcı bildirdi]`
- **Ses VAE (`MiniMax-H3 audio VAE decode`):** **4,70 sn** `[kullanıcı bildirdi]`
- **Bellek tepesi (`/usr/bin/time -l`):** **31,62 GiB** max RSS (`mmap` dâhil), **9,32 GiB** aktif tepe (`peak memory footprint`), **0 swap** `[kullanıcı bildirdi]`

### Varsayılan (Mod A) ve 48 GB İsteğe Bağlı (Mod B) Karşılaştırma Tablosu `[kullanıcı bildirdi]`

| Mod | Koşu | Boyut | Kare | Metin Kodlama | 6 Adım Örnekleme | Video + Ses VAE | Toplam (`generate_video`) | En Yüksek Bellek (`/usr/bin/time -l`) |
|---|---|---|---:|---:|---:|---:|---:|---|
| **Mod A (Varsayılan)** | `ornek_istem_R0` | 640×384 | 56 | 15,47 sn | 118,21 sn | 12,10 + 2,24 sn | **148,03 sn** (2 dk 28 sn) | 31,20 GiB max RSS · 8,87 GiB aktif · 0 swap |
| **Mod A (Varsayılan)** | 2B dans | 640×384 | 56 | 63,74 sn | 99,82 sn | 7,45 + 1,43 sn | **172,47 sn** (2 dk 52 sn) | 28,56 GiB max RSS · 8,93 GiB aktif · 0 swap |
| **Mod B (48 GB `TAM_METAL=1`)** | 2B dans (aynı istem) | 640×384 | 56 | **4,38 sn** | **91,23 sn** | 7,86 + 1,56 sn | **105,05 sn** (1 dk 45 sn) | 30,0 GB ağırlık `MTL0`'da · 0,81 GiB CPU RSS · 1,04 GiB aktif CPU · 0 swap |
| **Mod A (Varsayılan)** | 2B dans | 640×384 | 209 | 68,31 sn | 601,80 sn | 26,59 + 4,55 sn | **701,34 sn** (11 dk 41 sn) | 30,14 GiB max RSS · 9,31 GiB aktif · 0 swap |
| **Mod A (Varsayılan)** | Robot sahnesi | 640×384 | 209 | 75,81 sn | 595,54 sn | 27,62 + 4,70 sn | **703,76 sn** (11 dk 44 sn) | 31,62 GiB max RSS · 9,32 GiB aktif · 0 swap |
| **Mod B (48 GB `TAM_METAL=1`)** | Robot (yüksek çöz.) | 960×544 | 56 | 4,33 sn | 247,92 sn | 19,78 + 1,53 sn | **273,62 sn** (4 dk 34 sn) | 30,0 GB ağırlık `MTL0`'da · 1,43 GiB CPU RSS · 1,69 GiB aktif CPU · 0 swap |
| **Mod B (`budget=0.5`)** | Robot (768p) | 1344×768 | 56 | 4,35 sn | 736,24 sn | 34,20 + 1,55 sn | **776,44 sn** (12 dk 56 sn) | 30,0 GB ağırlık `MTL0`'da · 2,60 GiB CPU RSS · 2,86 GiB aktif CPU · 0 swap |

---

## 4. Karşılaşılan Sorunlar ve Çözümleri

1. **`--list-devices` cihaz adı (`MTL0`) `[kullanıcı bildirdi]`:** Metal cihazı `metal` değil `MTL0` adıyla listelenir; kontrol betikleri `MTL0|metal` aramalıdır.
2. **İzole kabukta Metal'in gizlenmesi `[kullanıcı bildirdi]`:** Kısıtlı alt kabuklarda `sd-cli --list-devices` yalnız CPU/Accelerate görür; doğrudan macOS Terminal'inden çalıştırıldığında `MTL0` görünür.
3. **`1344x768 × 209 kare` bellek kapısı (`Mod B`) `[kullanıcı bildirdi]`:** 30,0 GB ağırlığın tamamı `MTL0`'da yerleşikken (26,01 GB aktif), `1344x768 × 209` koşusu `blocks.0` aşamasında 18,76 GB hesap tamponu istedi ve 12,32 GB boş alan yetmedi (6,39 sn'de `failed during weight preparation`). Bu uç boyutta **Mod A** (`--offload-to-cpu` + küçük `chunk_budget`) gerekir `[tahmin; 1344x768 × 209 Mod A ile henüz denenmedi]`.

---

## 5. Kalite Kapısı (Dikiş Denetimi) Sonucu

- **Otomatik kalite kapısı (`scripts/dikis_denetim.py` / `scripts/doku_norm.py`):** `[denenmedi]` — bu Mac'te `opencv-python` (`cv2`) kurulu olmadığından sayısal gürültü ve orta akış kapısı çalıştırılamadı.
- **Günlük ve gözle doğrulama `[kullanıcı bildirdi]`:** Başarılı 7 koşunun hiçbirinde `retrying with temporal tiling`, `ALLOC_FAILED`, `[E]` veya swap görülmedi; 56 ve 209 kare çıktılar sesle birlikte baştan sona izlenerek doğrulandı.


## 6. MacBook Air M4 (16 GB)

[ölçtüm, 2026-11-23] MacBook Air (`Mac16,12`), Apple M4, 16 GB birleşik bellek, macOS 26.6.2 (`arm64`, build `25G83`). Motor resmî macOS ARM64 Metal sürümü `master-1111-6874e49` ve cihaz `MTL0`. Motor arşivi ve USB4 SSD'deki dört model dosyası SHA-256 ile doğrulandı. Kalite kapısı, depo kökündeki Python ortamında `opencv-python-headless 5.1.0.95` ve `numpy 2.5.5` ile çalıştı.

- Varsayılan `TAM_METAL=0` 56 kare denemesinde ölçüm izleyicisi, sistem diski boş alanı 2,5 GiB altına indiğinde örneklemeyi durdurdu. Başarılı çıktı veya kalite kapısı sonucu yoktu.
- İkinci koşuda `scripts/mac_uret.sh` ve `TAM_METAL=0` kullanıldı. `VT_ENGINE_BIN` ile verilen yerel uyarlayıcı yalnız bellek yerleşimini değiştirdi: `--offload-to-cpu --backend te=cpu` yerine `--backend MTL0 --params-backend disk --max-vram 6 --disable-prefetch` geçti. `--mmap`, `minimax_h3_attn_chunk_budget=0.03` ve projenin kalite ayarları korundu. Bu, motorun yönetilen GPU bütçesidir. Ölçülen süreç belleği ayrı verilir.
- Komut: `TAM_METAL=0 VT_MODEL_DIR="<MODEL_DIR>" VT_ENGINE_BIN="<ADAPTER_DIR>" ./scripts/mac_uret.sh docs/ornek_istem_R0.txt 56`. Uzunluk denemesinde yalnız kare argümanı değişir.

| Kare | Motor süresi (`generate_video`) | Betik toplamı | Tepe bellek ayak izi / max RSS | Kalite kapısı |
|---:|---:|---:|---:|---|
| 56 | 732,03 sn | 734,25 sn | 6,20 / 7,89 GiB | `KAPI GECTI: kare=56 gurultu=0.68 orta_akis=3.77` |
| 124 | 1657,04 sn | 1659,88 sn | 6,21 / 8,58 GiB | `KAPI GECTI: kare=124 gurultu=0.64 orta_akis=3.36` |

[ölçtüm] `ffprobe`, her iki kare sayısını, 640×384, 24 fps ve 32 kHz stereo PCM sesi doğruladı. Motor günlüğünde tahsis hatası veya VAE karolama yedeği görülmedi. Bellek değerleri `/usr/bin/time -l` sayaçlarından GiB'ye çevrildi [hesap]. Ham günlükler yerelde saklandı.
