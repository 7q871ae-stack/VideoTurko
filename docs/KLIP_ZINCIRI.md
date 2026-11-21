# Klip Zincirleme Rehberi / Clip Chaining Guide (TR + EN)

> **TR:** Upstream VideoTurko tek geçişli (≤209 kare, 8.7 sn) kliplere odaklanır. Bu rehber, RTX 5060 (`sm_120`) üzerinde `--init-img` ile ardışık 8 saniyelik klipleri üretip `ffmpeg` ile dikişsiz birleştirmek için pratik kuralları özetler.
>
> **EN:** Upstream VideoTurko focuses on single-pass clips (≤209 frames, 8.7 s). This guide summarizes practical rules for generating sequential 8-second clips via `--init-img` on RTX 5060 (`sm_120`) and stitching them cleanly with `ffmpeg`.

> **Kanıt / Evidence:** Bu rehber katkıcının RTX 5060 deneyimidir [kullanıcı bildirdi]; süreler onun ölçümü, `ffmpeg` tarifleri ve "aynı tohum tutarlılığı korur" gibi yorumlar bizim tarafımızdan ölçülmedi [denenmedi]. / This guide is the contributor's RTX 5060 experience [user-reported]; timings are their measurements, and the `ffmpeg` recipes and remarks such as "the same seed keeps consistency" were not measured by us [not tried].

---

## 1. Motor Sınırları / Engine Limits
- **Kare ızgarası / Frame grid:** `17k + 5` (5, 22, 39, 56 … 192, 209).
- **Üst sınırlar / Maximums:** Metinden en fazla **209 kare (8.7 s)**; `--init-img` ile en fazla **192 kare (8.0 s)**.
- **Biçim / Format:** 640×384, 24 fps, gömülü ses (ayrı TTS yok).
- **RTX 5060 (`sm_120`) süreleri / Timings [kullanıcı bildirdi / user-reported]:** 56 kare ≈ 2 dk, 192 kare (`init_image`) ≈ 6.3–7.0 dk, 209 kare ≈ 6 dk. Tek GPU → aynı anda tek iş.

---

## 2. Sıralı Üretim Akışı / Sequential Workflow
1. **Klipleri sırayla üretin / Generate sequentially:** Bir klip tamamlanıp kalite kapısını (`KAPI GECTI`) ve kare paftasını (`pafta_video.png`) gözle kontrol etmeden sonraki klibi başlatmayın.
2. **Sahne sığmazsa / If the action does not finish in one clip:** Aynı klibin uygun bir son karesinden ikinci parça üretip devam edin.
3. **Resimden video hazırlığı / Image-to-video prep:** Kaynak görseli 5:3 oranına kırpıp 640×384 ölçekleyin; yüzleri ve ana öğeleri kadrajda tutun, kırpımı gözle doğrulayın:
   ```powershell
   ffmpeg -i in.png -vf "crop=W:H:x:y,scale=640:384" ref.png
   ```
   Önce 56 karelik hızlı deneme yapın, uygunsa 192 kareye geçin. Telifli görsel ve gerçek kişi yüzlerinin sorumluluğu kullanıcıdadır.

---

## 3. Devir Karesi (`init_image`) Seçimi / Handoff Frame Selection
- **Varsayılan / Default:** Önceki klibin son karesi:
  ```powershell
  ffmpeg -sseof -0.05 -i klip1.avi -frames:v 1 -update 1 son.png
  ```
- **Son kare kötüyse / If the last frame is poor** (yüz kadraj dışında, karakter kameraya yapışmış vb.): Daha erken temiz bir kare seçin (`-ss <t>`), aday kareleri gözle karşılaştırın ve montajda önceki klibi tam o saniyede kesin.

---

## 4. İstem ve Ses Kuralları / Prompt & Audio Rules
- Her klipte sahneyi, karakter tarifini, ışığı ve kamera dilini tekrarlayın; **yalnızca olayı ilerletin**.
- Uzun kamera hareketlerini adım adım yazın (örn. yükselir → aşağı bakar → hedefe süzülür).
- Kadrajı açıkça belirtin (örn. geniş plan, iki figür de kadrajda).
- Konuşma/müzik istenmiyorsa her klipte ses cümlesini ekleyin:
  ```text
  Audio: <ambient sounds> only, no dialogue, no speech, no voices, no music.
  ```
- Aynı `seed` ile tutarlılık koruyun; etkileşim tutmazsa farklı `seed` deneyin veya hareketi iki parçaya bölün.

---

## 4b. Yardımcı: `scripts/zincir.py` / Helper: `scripts/zincir.py`

- **TR:** Elle yaptığınız adımları üç alt komutla kolaylaştırır; yalnız CPU, GPU ve ağ yok, motoru hiç başlatmaz. `plan` hedef süreyi klip planına çevirir (süre tahmini vermez: zincir ölçümü yapılmadı [denenmedi]); `son-kare` klibin GERÇEK son karesini sayarak çıkarır (okuyamazsa hata verir, tahmin etmez; yanlış kare dikişi bozar, bkz. `docs/SIK_HATALAR.md` 9); `bagla` birleştirme komutunu yazdırır, `--calistir` ile çalıştırır. Tek klibin kalite kapısı dikişi ölçmez: birleştirdikten sonra dikişi gözle ve `scripts/dikis_denetim.py` ile kontrol edin.
- **EN:** Three subcommands replace the manual steps; CPU only, no GPU, no network, it never starts the engine. `plan` turns a target length into a clip plan (no time estimate: chain runs were not measured [not tried]); `son-kare` extracts the REAL last frame by counting (it errors out instead of guessing; a wrong frame breaks the seam, see `docs/SIK_HATALAR.md` item 9); `bagla` prints the join command, or runs it with `--calistir`. The single-clip quality gate does not measure the seam: after joining, check it by eye and with `scripts/dikis_denetim.py`.

```powershell
python -I -X utf8 scripts\zincir.py plan --sure 30
python -I -X utf8 scripts\zincir.py son-kare klip1.avi devir_kare.png
python -I -X utf8 scripts\zincir.py bagla klip1.avi klip2.avi klip3.avi klip4.avi -o film.mp4 --calistir
```

---

## 5. `ffmpeg` ile Birleştirme / Stitching with `ffmpeg`
- **İlk kareyi at / Drop duplicate first frame:** Devam klibi önceki klibin son karesiyle başlar; video için `trim=start_frame=1`, ses için `atrim=start=0.0417` (1/24 sn) uygulayın.
- **Bağlama / Concat & audio crossfade:** Videoyu `concat`, sesi `acrossfade=d=0.25` (veya `0.3`) ile bağlayın. Tüm akışlarda `setpts=PTS-STARTPTS`, gerekirse `fps=24,settb=1/24` ve `aresample=48000` kullanın.
- **Model ilk karede atlarsa / First-frame jump recovery:** Model `init_image`'ı sürdürmeyip başka bir açıdan başlarsa, yeni klipte önceki klibin son karesine en yakın kareyi (`N`) bulun; klibi `trim=start_frame=N` / `atrim=start=N/24` ile kesip `xfade=transition=fade:duration=0.333` ile bağlayın ve ek noktasını ±1 sn kare dizisiyle doğrulayın.
- **İsteğe bağlı hız rampası / Optional speed ramp:** Model hızlanmayı zayıf yaptıysa:
  ```text
  setpts='if(lt(T,2),T,2+(log(1+(T-2)/6)*6))/TB',fps=24
  ```
  (2. saniyeden sonra kademeli 2× hızlanma; sesi hızlandırmayın, yeni uzunluğa kırpıp sonunda `afade` ile kısın.)
- **Ses seviyesi ve çıkış / Loudness & export:** Tüm birleşik sese tek seferde `loudnorm=I=-23:TP=-2:LRA=11` uygulayın; standart çıkış:
  ```powershell
  -c:v libx264 -crf 18 -pix_fmt yuv420p -c:a aac -b:a 160k -ar 48000
  ```

- **1080p'ye büyütme / Upscaling to 1080p:** VideoTurko 640x384 yazar; birleştirmeden önce ya da sonra büyütmek isterseniz, bir katkıcının RTX 3070'te ölçtüğü dört araç ve süreleri: `docs/RTX3070_STOCK_SDCPP.md`, "Upscaling to 1080p" [user-reported, PR #7]. Büyütücü bu reponun parçası değildir. / VideoTurko writes 640x384; for upscaling, see the four tools a contributor timed on an RTX 3070 in that file [user-reported, PR #7]; no upscaler is part of this repo.

---

## 6. Doğrulama Kontrol Listesi / Verification Checklist
- **Kalite kapısı / Gate:** `runs/olaylar.txt` son satırı `KAPI GECTI` (`gurultu <= 1.5`, `orta_akis > 0.05`). `gurultu=0` ve `orta_akis=0` siyah video demektir.
- **Ek noktası paftası / Seam contact sheet:**
  ```powershell
  ffmpeg -ss <t> -t 1.6 -i final.mp4 -vf "fps=10,scale=160:96,tile=8x2" -frames:v 1 ek.png
  ```
- **Süre / Duration:** `ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 final.mp4`
- **Ses seviyesi / Loudness:** `ffmpeg -i final.mp4 -af ebur128=peak=true -f null -` (hedef ≈ −23 LUFS, tepe < −2 dBFS).
- **İstenmeyen konuşma kontrolü (isteğe bağlı) / Optional speech check:** `faster_whisper` (`tiny`, CPU, `vad_filter=True`) ile konuşmasız sahnelerde 0 segment doğrulaması.
