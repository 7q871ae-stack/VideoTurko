# VideoTurko: Sik hatalar / Common pitfalls

Bu liste gercek kosulardan cikmistir (4 GB GTX 1050 Ti, stable-diffusion.cpp `sd-cli -M vid_gen`, MiniMax H3 HyperFlow Flash GGUF).
Her madde: **belirti**, **neden**, **kalici cozum**. Etiketler: [olctum] = bu projede olculdu, [okudum] = kodda/belgede goruldu, [tahmin] = dogrulanmadi.
This list comes from real runs. Each item: symptom, cause, lasting fix.

## A. Bellek ve kapi (VRAM)

1. **VRAM kapisi `blocks.0` agirlik hazirliginda dusuyor** (`segment 5/52 (blocks.0) failed during weight preparation`) [olctum]
   - Neden: yukleme kapisi `ihtiyac = bekleyen + eksik + marj`; kare sayisi buyudukce compute tamponu artar, tahliye yetmez.
   - Cozum: marj icin `SD_VRAM_MARGIN_MB=1` kullan. **`0` degeri "ayarsiz" sayilir ve 1024 MB'lik tuzaga duser** [okudum]. Kare tavani tablosu: `OLCUMLER.md`.
2. **`SD_CAPACITY_LOG` satirlari bir sonraki segmentin kapisini gosterir** (etiket kaymasi) [olctum]
   - `executing segment N` satirindan sonra yazilan CAPACITY satiri N+1'in kapisidir; olen kapiyi `segment K/52 (blocks.X) failed` satiri belirler.
3. **`SD_MLP_SET_OUT=1` bellegi azaltmaz, artirir** [okudum + olctum]
   - Hedef tensor "yaprak" oldugundan grafik basinda ayrilir ve tum blok boyunca canli kalir: 209 karede ~+342 MB (G209c'de +320 MB olculdu). Varsayilan kapali kalir; kanitli yama listesi `YAMALAR.md`.
4. **Bir yamanin tek basina kullanimi tepeyi buyutebilir**: `0006b` tek basina +121,5 MB; `SD_QKV_SET_OUT` ile birlikte kullan [olctum].
5. **Bellek tahmini yanlis girdiyle yapildi**: jeton sayisi N'yi formulle varsayma, logdaki `PEAK_DUMP` sekillerinden oku (209: N=15889); iki kosuyu karsilastirmadan once bayrak setini fark'la (ayni bayrak seti degilse "karsilastirilamaz" yaz) [olctum].

## B. VAE ve uretim

6. **Karoli VAE'ye sessiz dusus (`retrying with temporal tiling`)**: cikti gecersiz sayilir [olctum]. Cozum: DiT ve VAE'yi AYRI surecte kos (latent kaydet/yukle), `SD_VAE_NO_TILING_FALLBACK=1` ile dusus yerine hizli hata ver. 192 ve 209 kare bu yolla uretildi.
7. **Sure tavani (`-TavanDk`) kare sayisina gore ayarlanmadi**: 209 karede 6 DiT adimi bittikten sonra VAE sirasinda 50 dk tavanda olduruldu [olctum]. Kural: tavan = tahmini sure x 1,4; 209 icin en az 80 dk.
8. **Kopyalanan satirda latent/cikti yolu eski adda kaldi** (yeni kosu eski `*_latent.bin` uzerine yazdi) [olctum]: kopyada `-Deney`, `-Cikti`, `-OutDir`, `SD_VIDEO_LATENT_SAVE` ve `-TavanDk` ayri ayri dogrulanir.
9. **Zincirleme (`--init-img`) icin onceki videonun GERCEK son karesi kullanilmadi** (205. kare verildi, son kare 208'di): dikis SSIM 0,659 [olctum]. Cozum: kare sayisini `ffprobe` ile al, son kareyi cikar, orijinal videoyla 0,00 fark dogrula; birlestirirken onceki videoyu kirp, tekrar eden ilk kareyi at.
10. **Karolu VAE yedegi, adim/cfg/cozunurluk dusurmek kalite yolu degildir**: bu proje sabit ayar kullanir (6 adim, cfg 1, varsayilan 640x384; `-W/-H` alani yalniz buyutebilir, kucultemez), bellek yamalari yalniz hesabin NEREDE yapildigini degistirir ve 56/141 kare kapilarinda bayt-aynidir.

## C. Kalite kapisi

11. **Ham gurultu olcusu sahne dokusuna baglidir**: gri karelerde her 8. karede ortalama |kare - 3x3 medyan| yuksek frekansli dokuyu (dal, cim, toz, yakin ucak) da sayar; Z3_175 klibi 1,86 ile RED aldi ama gozle ve zamansal olcuyle bozulma yoktu [olctum]. Ek olarak dokuya normalize N (medyan artik / Sobel doku gucu) kullanilir; esik kapiyi gevsetmez, yalniz RED nedenini raporlar. Hangi `doku_norm` surumunun hangi olcekte oldugunu belgeleyin (iki surumun degerleri farkli olcekte).
12. **Bayt kapisi bayrak setiyle yapilir**: bir yama 56 karede R0'a bayt-ayni gecmediyse reddedilir; kapi hangi env bayraklariyla kosulduysa uretim de o setle kosulmalidir. 158-209 kare icin dogrudan bayt referansi YOKTUR: "ayni bayrak ve ikili zinciri" dur [okudum].

## D. Kosucu ve Windows

13. **DLL bulunamadi (`STATUS_DLL_NOT_FOUND` / 0xC0000135)**: `cudart`/`cublas` DLL'lerini calistirma PATH'ine ekle [olctum].
14. **Cikis kodu bos "bitti" yazildi**: `Process` bitmeden `ExitCode` okundu; `WaitForExit()` sonrasi oku [olctum].
15. **Turkce kulturde ondalik virgul CSV'yi kaydirdi**: bicimlemede `InvariantCulture` kullan [olctum].
16. **Durdurma isareti (`DUR` dosyasi) kosan satiri da oldurur**: "kosan satir dogal bitsin" isteniyorsa isaret satir bitince konur; satirin ozet dosyasi (`ozet=`) olmadan koşucu cikis=0'i BITTI sayar, kanit yoktur: uretim ve kapi satirlarinda ozet zorunlu [olctum].
17. **Gozlemci sessizce sondu** (izleyicinin 30 dk tavani): alarm yazilir ama okuyan kalmaz; bitis saatini kaydet, sona erince yeniden kur, uzun islerde kalp atisi ve yedek is satiri kullan [olctum].
18. **Bellek baskisi**: sd-cli ~10-11 GB RAM kullanir (16 GB sistemde); uretim sirasinda diski tarayan agir islerden kacin, bellek kritik dusunce yardimci surecler durdurulur [olctum].

## E. Diger kartlar ve kapi araclari (v0.1.1, issue #1)

19. **Yeni kartta (compute capability 7.0+) 141 kare ve ustunde video tamamen siyah** (kare ortalamasi 0; latent NaN). 56 ve 107 kare sorunsuz [kullanici bildirdi: RTX 4070 Ti 12 GB, issue #1].
   - Neden (iki aday, ayrilmadi): cuBLAS'in fp16 hesap modu uzun dizide tasiyor OLABILIR; ya da `GGML_CUDA_CUBLAS_COMPUTE_TYPE` ayarlaninca kapanan bf16 birlesik cekirdek (yalniz 8.x ve ustu kartlarda devrede) [okudum: motor `src/core/cuda/bf16.cu`; neden: tahmin]. GTX 1050 Ti'de (6.1) iki yol da zaten devre disi, bu yuzden orada gorulmedi [okudum: `ggml-cuda/common.cuh` fast_fp16_hardware_available].
   - Cozum: v0.1.1 `uret.ps1`, kart 7.0+ ise ve sen ayarlamadiysan `GGML_CUDA_CUBLAS_COMPUTE_TYPE=f32` yapar; `-Kuru` ciktisinda gorunur. Hiz farki olculemedi (141 kare DiT 211,8 sn ile 209,9 sn) [kullanici bildirdi, issue #1]. Eski surumde elle, ayni PowerShell penceresinde `uret.ps1`'den once:
     `$env:GGML_CUDA_CUBLAS_COMPUTE_TYPE = 'f32'`
   - EN: all-black (NaN) video at 141+ frames on compute capability 7.0+ cards; v0.1.1 sets `GGML_CUDA_CUBLAS_COMPUTE_TYPE=f32` there unless you set it yourself.
20. **"KAPI RED" ama video duzgun gorunuyor; olaylar.txt'de `dikis_denetim cikti ayristirilamadi`** [olctum: ekip testi 2026-11-20, `No module named 'cv2'` veren sahte python ile; kayit yazarlarda, repoda yok]
   - Neden: python var ama `opencv-python`/`numpy` yok; v0.1.0 bunu yanlislikla RED (cikis 5) sayiyordu.
   - Ozel durum: Windows'ta python kurulu degilken bile `python` komutu bulunur (Microsoft Store kisayolu `WindowsApps\python.exe`); calistirilinca yalniz 9009 ile cikar. `Get-Command` bunu ayirmaz.
   - Cozum: v0.1.1 `uret.ps1` GPU isinden ONCE `python -I -c "import cv2, numpy"` dener; olmazsa **cikis 6** verir ve video uretmez (uzun kosu bosa gitmez). Kapi tek basina kosulursa da bu durumlarda **cikis 6 `KAPI CALISMADI`** (RED degil). Python 3'u python.org'dan kur, paketleri kur, `uret.ps1`'i yeniden calistir; elinde v0.1.0'dan kalan video varsa yalniz kapiyi kos:
     `py -3 -m pip install opencv-python numpy`
     `powershell -NoProfile -File scripts\uretim_kapi.ps1 -Dizin <cikti klasoru> -Ad video -Kare <kare>`
   - Python baska yerdeyse: `$env:VT_PYTHON = '<python.exe tam yolu>'`.
   - EN: no Python, the Windows Store alias (exit 9009) or a Python without OpenCV now gives exit 6, checked before the GPU job (no video made), never 5 (RED). Install Python 3 and `opencv-python numpy`, then run again.
21. **Kirmizi "ffmpeg is not recognized" satiri, pafta (12 karelik onizleme) yok** [olctum: ekip testi 2026-11-20, uc senaryo (yanlis VT_FFMPEG, PATH'te ffmpeg yok, EAP=Stop sarmali): KAPI GECTI, cikis 0; kayit yazarlarda, repoda yok]
   - Neden: ffmpeg yalniz paftayi cizer; kapi olcutu (kare, gurultu, akis) OpenCV'den gelir. v0.1.0 yalniz `VT_FFMPEG` ve PATH'e bakiyordu.
   - Cozum: v0.1.1 ffmpeg'i `VT_FFMPEG`, PATH ve `engine\bin`'de arar (release ffmpeg icermez; `engine\bin` yalniz siz koyarsaniz ise yarar); bulamazsa acik BILGI satiri yazar, paftayi atlar. Kurmak icin `winget install Gyan.FFmpeg` (sonra yeni pencere ac) ya da `$env:VT_FFMPEG = '<ffmpeg.exe tam yolu>'`.
   - EN: ffmpeg only draws the contact sheet; when it is missing v0.1.1 warns and skips the sheet, the gate decision is unchanged.
22. **`-W 720` reddedildi** [okudum: motor `request.cpp` hizalama]
   - Neden: motor genislik/yuksekligi 32'nin katina yukari yuvarlar (720 -> 736); betik bu sessiz degisikligi kabul etmez. Dikey ornekler: 384x640, 480x832, 576x1024, 736x1280 (hepsi 32'nin kati).
   - Not: 640x384 disindaki boyutlar 4 GB'ta denenmedi; kapi esikleri 640x384'te kalibre, buyuk boyutta gurultu dusuk okunur [olctum: ekip testi 2026-11-20, F209V2 klibi 1280x768'e buyutulunce gurultu 1,08 -> 0,32, N 0,048 -> 0,020; kayit yazarlarda, repoda yok].
23. **12 GB+ kartta her kosuda "VRAM ince marj" uyarisi** [kullanici bildirdi, issue #1]
   - Neden: v0.1.0 esigi sabit 3800 MiB idi; `--offload-to-cpu` buyuk kartta da karti doldurur.
   - Cozum: v0.1.1 esigi "tepede bos VRAM <= 296 MiB" yapti (4096 MiB kartta eskisiyle ayni).

24. **RTX 50 serisinde (compute capability 12.x) 56 kare ve ustunde video tamamen siyah** (`-InitImg` ile 22/39 karede de) [kullanici bildirdi: RTX 5060 Laptop 8 GB, PR #3; v0.1.0 betigiyle].
   - Neden (ayrilmadi): hazir motor yalniz `sm_61` icin derli; katkicinin hipotezi surucunun bu kodu calisirken cevirmesi [tahmin]. v0.1.1'in otomatik `f32` ayari bu kartta denenmedi.
   - Cozum sirasi: (1) v0.1.1 betigi ve hazir motorla 56 kare dene; (2) yine siyahsa motoru `-DCMAKE_CUDA_ARCHITECTURES=120` ve CUDA 12.8.1+ ile derle, `VT_ENGINE_BIN`'i o klasore ver. Tarif ve test raporu: `docs/RTX5060_SM120_DERLEME.md`, `docs/RTX5060_TEST_RAPORU.md`. Bizde RTX 50 kart yok, olcmedik; (1)'in sonucunu issue olarak bildirirseniz kok neden netlesir.
   - EN: all-black video on RTX 50 reported with the v0.1.0 script; first try the release engine with the v0.1.1 script (f32 on), then build natively for sm_120 (`docs/RTX5060_SM120_DERLEME.md`).
