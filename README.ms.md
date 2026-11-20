# VideoTurko

[English](README.md) · [Türkçe](README.tr.md) · [简体中文](README.zh-CN.md) · [日本語](README.ja.md) · [Español](README.es.md) · [Русский](README.ru.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [العربية](README.ar.md) · [Português (BR)](README.pt-BR.md) · [Italiano](README.it.md) · [한국어](README.ko.md) · [हिन्दी](README.hi.md) · [Bahasa Indonesia](README.id.md) · [Tiếng Việt](README.vi.md) · [Polski](README.pl.md) · [Nederlands](README.nl.md) · [Українська](README.uk.md) · [فارسی](README.fa.md) · [עברית](README.he.md) · [ไทย](README.th.md) · [বাংলা](README.bn.md) · [اردو](README.ur.md) · [Ελληνικά](README.el.md) · [Čeština](README.cs.md) · [Română](README.ro.md) · [Magyar](README.hu.md) · [Svenska](README.sv.md) · [Azərbaycanca](README.az.md) · Bahasa Melayu

![Windows](https://img.shields.io/badge/Windows-10%2F11-blue) ![GPU](https://img.shields.io/badge/NVIDIA-4%20GB%20(sm__61)-76b900) ![License](https://img.shields.io/badge/code-MIT-green) ![Status](https://img.shields.io/badge/status-clean--root%20test%20pending-orange)

> **Dalam 30 saat:** kad grafik 4 GB boleh menghasilkan video MiniMax H3 sepanjang 209 bingkai (8.7 saat) dalam satu laluan: disahkan pada satu mesin (GTX 1050 Ti 4 GB; pemasangan penuh `kur.ps1` pada folder kosong belum disahkan dari awal hingga akhir) [diukur: 209 bingkai dengan binari keluaran melalui `uret.ps1`, larian U209; latent sama bait demi bait dengan larian binaan pembangunan; bingkai dan audio dalam video sama, sha fail berbeza kerana bekas (container); bukti disimpan oleh penulis, tiada dalam repositori ini]; dengan `-InitImg` (imej ke video) paling banyak 192 bingkai (8.0 saat) [diukur: larian B192]; 209 bingkai mengambil masa kira-kira 57 minit, had masa lalai 80 minit [diukur: larian U209]; 3 langkah di bawah ialah cara menjalankannya.

VideoTurko: tampalan memori stable-diffusion.cpp beserta resipi untuk menjalankan MiniMax H3 text-to-video pada GTX 1050 Ti 4 GB, sehingga 209 bingkai (8.7 saat) dalam satu laluan; image-to-video (`-InitImg`) sehingga 192 bingkai (8.0 saat) (209 bingkai disahkan dengan rantai bait; sama bait dengan larian tanpa tampalan pada semakan 56 dan 141 bingkai).

## Mula pantas (Windows, 3 langkah)
**Status: skrip pemasangan/penggunaan di bawah masih disiapkan dan ujian clean-root belum dibuat; tiada apa-apa di sini didakwa berfungsi sehingga ujian itu lulus (lihat "Status dan had").**

1. **Muat turun** repositori ini (butang hijau **Code**, kemudian **Download ZIP**) dan ekstrak ke folder PENDEK, contohnya `C:\vt`.
2. **Pasang**: buka PowerShell dalam folder itu (taip `powershell` pada bar alamat Explorer) dan jalankan
   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File scripts\kur.ps1
   ```
   Akar pemasangan ialah folder yang anda ekstrak (enjin masuk ke `engine\bin`, model ke `model`); untuk menggunakan tempat lain, tetapkan pemboleh ubah persekitaran `VT_ROOT` terlebih dahulu. Skrip menyemak GPU, pemacu, RAM dan cakera, mengambil enjin dan model (zip enjin dan fail model yang baru dimuat turun disemak sha256; fail model yang sudah ada dengan saiz yang betul hanya disemak saiznya, `scripts\modelleri_indir.ps1 -Dogrula` menjalankan semakan sha256 penuh), menjalankan semakan sebenar yang ringkas, dan mencetak READY hanya jika semakan itu lulus [reka bentuk: `kur.ps1` belum pernah dijalankan sepenuhnya dalam folder bersih; ayat ini dikemas kini selepas ujian folder bersih]. `-ExecutionPolicy Bypass` hanya terpakai pada proses ini; baca `scripts\kur.ps1` dahulu, seperti pada mana-mana pemasang.
   Zip enjin diambil daripada keluaran GitHub v0.1.0 (diterbitkan pada 2026-11-19; sha256 baginya ditetapkan dalam `kur.ps1`). Jika di luar talian atau menggunakan binaan anda sendiri, berikan zip tempatan: `-MotorZip <path> -CudaZip <path>`. Zip tempatan juga disemak dengan sha256 tetap yang sama (fail `.sha256` di sebelahnya diabaikan), jadi ia mesti zip keluaran; untuk binaan anda sendiri, tetapkan dahulu `VT_MOTOR_SHA256` / `VT_CUDA_SHA256` kepada sha256 binaan itu. sha256 yang salah menghentikan proses dengan exit 1. Hanya `.exe`/`.dll` masuk ke `engine\bin`; lesen dan README masuk ke `engine\lisanslar\<zip name>\`. [dicuba dengan zip dist sebelum keluaran: `.sha256` sisian beserta amaran rujukan-sendiri, binari dan DLL diletakkan, `sd-cli --help` berjalan; sha binari yang dipasang sepadan (`c5cebe78...`, `e5d3d329...`); langkah model dan semakan 5 bingkai `kur.ps1` BELUM dijalankan pada GPU sebenar]
   **Lesen model:** sebelum langkah model, pemasang mencetak ringkasan lesen (`docs/LISANS_KABUL.txt`, teks penuh `docs/LISANS_UYARISI.md`: MiniMax H3 Community License, had wilayah yang turut meliputi video yang dijana, peraturan komersial dan label AI) dan meminta anda menerimanya (`E` = ya). Bacalah dahulu. Untuk larian tanpa pengawasan anda boleh memberikan `-LisansKabul E`, yang bermaksud anda sendiri telah membaca dan menerimanya; jangan tambahkannya bagi pihak orang lain. (Ejen AI: ikut `AGENTS.md`; jangan sekali-kali menaip E tanpa persetujuan pengguna.) Tanpa persetujuan, `kur.ps1` berhenti dengan kod keluar 2 dan tidak memuat turun sebarang model.
3. **Jana**: letakkan prompt anda dalam fail teks (satu perenggan bahasa Inggeris, ayat `audio:` pilihan) dan jalankan
   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File scripts\uret.ps1 -Istem istem.txt -Kare 209
   ```
   `-Kare` mengikut grid 17k+5 (56, 73, ... 192, 209); lalai 209 (8.7 saat), panjang terpanjang yang kami liputi. VAE berjalan dalam proses berasingan, tidak pernah dipecahkan kepada jubin (tiling) [larian enjin sebenar melalui `uret.ps1` dengan binari keluaran, VAE proses berasingan, lulus dalam larian U209].

   Panduan menulis prompt: [`docs/ISTEM_YAZIMI.md`](docs/ISTEM_YAZIMI.md) (corak satu syot berterusan, kepingan masa yang sama panjang, dua contoh lengkap).

| Keperluan | Nilai |
|---|---|
| OS | Windows 10/11, 64-bit |
| GPU | NVIDIA, 4 GB atau lebih; diuji hanya pada GTX 1050 Ti (sm_61); margin nipis (3777/4096 MiB pada 209 bingkai): skrin atau pelayar yang sibuk boleh menggagalkan larian; tiada kad 4 GB lain dicuba |
| RAM | 16 GB (puncak sekitar 11 GB; tutup program lain) |
| Cakera | 32 GiB atau lebih ruang kosong, model pada SSD (NVMe lebih baik) |
| Muat turun | zip enjin 36.8 MB + zip runtime CUDA 567.5 MB [diukur] + model 31,473,112,040 bait (kira-kira 29.3 GiB) [dibaca: saiz dalam `scripts/modeller.json`]; kira-kira 30 GiB kesemuanya |
| Model | tidak disertakan; diambil oleh pemasang di bawah lesen MiniMax (lihat amaran di bawah). Model (29.3 GiB, 31,473,112,040 bait dalam `scripts/modeller.json`) tidak terdapat dalam repositori atau keluaran ini: had saiz fail/keluaran GitHub terpakai, dan `kur.ps1` memuat turunnya daripada sumber rasmi dengan pengesahan sha256. |

Kod keluar `kur.ps1`: 0 READY, 1 ralat, 2 input pengguna diperlukan (lesen, atau belum ada keluaran/zip), 3 perkakasan atau cakera tidak mencukupi, 4 dihentikan (fail DUR). `uret.ps1` hanya menerima larian jika fail `.avi` wujud, bilangan bingkai betul dan log bersih [diukur: satu larian sebenar melalui `uret.ps1` pada binari keluaran, larian U209, 209 bingkai, pintu lulus]. Kod keluar `uret.ps1`: 0 DONE (pintu kualiti lulus), 1 ralat atau output tidak sah (termasuk video tanpa aliran audio), 2 dihentikan (fail DUR), 5 `KAPI RED` (pintu kualiti gagal: klip tidak diterima, keputusan di tangan anda), 6 pintu tidak dapat dijalankan (klip tidak diterima). Butiran dalam AGENTS.md. [diukur: kod keluar 0, 1 (video senyap), 5 dan 6 dalam senario dengan enjin palsu dan pintu palsu; enjin sebenar: exit 0 dalam larian U209]

### Penyelesaian masalah (butiran: `docs/SIK_HATALAR.md`)
| Apa yang anda lihat | Maksudnya, dan apa yang perlu dibuat |
|---|---|
| `STATUS_DLL_NOT_FOUND` / `cudart64_12.dll not found` (#13) | Jangan mulakan `sd-cli.exe` secara manual; jalankan `scripts\kur.ps1`, yang meletakkan DLL CUDA pada tempatnya. |
| `failed during weight preparation` pada `blocks.0` (#1, #3, #5) | VRAM tidak mencukupi pada pintu memori: gunakan bilangan bingkai yang lebih kecil pada grid 17k+5, tutup program GPU lain, kekalkan bendera yang disertakan. |
| `retrying with temporal tiling` (#6) | VAE jatuh kepada tiling; output tidak sah untuk tujuan kualiti. Jalankan semula. |
| Larian tamat pada had masa, tiada video (#7) | Naikkan `-TavanDk` untuk klip panjang (had masa lalai: 80 minit untuk 209 bingkai, ditetapkan oleh `uret.ps1`; larian 209 bingkai kami mengambil 57 minit [diukur: larian U209]). |
| Kod keluar kosong tetapi "finished" (#14) | Pembungkus (wrapper) membaca kod keluar terlalu awal; jalankan semula, dan semak bahawa fail video wujud. |
| Sistem menjadi perlahan, swapping (#18) | Enjin menggunakan kira-kira 10-11 GB RAM; tutup pelayar dan program lain. |
| sha256 tidak sepadan / muat turun gagal | Biasanya muat turun terganggu: jalankan arahan yang sama sekali lagi, fail yang telah disahkan dilangkau. |

### Baharu dalam v0.1.1: lebih banyak pilihan (butiran: `AGENTS.md`, `docs/SIK_HATALAR.md` 19-23)
Tanpa pilihan ini, tiada apa-apa yang berubah pada kad 4 GB (semakan bait 56 bingkai terhadap rujukan kami lulus semula dengan v0.1.1 [diukur]). Tambahkan `-Kuru` pada mana-mana arahan untuk melihat apa yang akan dijalankan.
- `-EndImg`: berikan juga bingkai terakhir (bingkai pertama dan terakhir, "FLF"); had 175 bingkai pada kad di bawah 8 GB (192 tidak muat pada 4 GB), 192 pada kad 8 GB ke atas. Pada GTX 1050 Ti kami ia sentiasa berjalan dalam dua proses: 56 bingkai 1040 saat, 175 bingkai 2887 saat (48 minit), kedua-duanya lulus pintu [diukur]. Petua menulis prompt: `docs/ISTEM_YAZIMI.md`.
- `-W` / `-H`: saiz lain, contohnya menegak 384x640; gandaan 32, keluasan sekurang-kurangnya 640x384 (tidak pernah lebih kecil). Belum diuji pada 4 GB; pada kad di bawah 8 GB, saiz yang melebihi kerja terbesar yang telah kami ukur ditolak. Ambang pintu kualiti ditentukur pada 640x384.
- `-TekAsama`: satu proses dan bukannya dua, untuk kad besar sahaja; tidak pernah dihidupkan secara automatik.
- GPU yang lebih baharu (compute capability 7.0+, contohnya RTX 20/30/40): `GGML_CUDA_CUBLAS_COMPUTE_TYPE=f32` ditetapkan secara automatik melainkan anda menetapkannya sendiri; ini membetulkan video hitam sepenuhnya pada 141+ bingkai pada RTX 4070 Ti milik pelapor [dilaporkan pengguna, issue #1]. Tanpa Python + OpenCV, `uret.ps1` kini berhenti dengan exit 6 sebelum kerja GPU (tiada video dihasilkan, tiada RED yang mengelirukan).
- Terima kasih kepada @SinanC73 atas laporan RTX 4070 Ti yang membawa kepada perubahan ini ([issue #1](https://github.com/alexturkey/VideoTurko/issues/1)).

```powershell
# First and last frame (FLF): the clip starts on ilk_kare.png and ends on son_kare.png (up to 175 frames on 4 GB)
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\uret.ps1 -Istem istem.txt -Kare 141 -InitImg ilk_kare.png -EndImg son_kare.png
# Vertical 9:16 (multiples of 32, area at least 640x384; not tested on 4 GB)
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\uret.ps1 -Istem istem.txt -Kare 56 -W 384 -H 640
# One process instead of two (large cards only)
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\uret.ps1 -Istem istem.txt -Kare 141 -TekAsama
# Print the exact engine command and settings without using the GPU
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\uret.ps1 -Istem istem.txt -Kare 141 -Kuru
```

## Apakah ini
Satu set tampalan kecil memori/penjadualan untuk stable-diffusion.cpp beserta resipi larian, semakan dan pengukuran yang membolehkan MiniMax H3 (DiT 33B; kami menjalankan GGUF HyperFlow Flash 13.7B Q4_K_M; pengekod teks Qwen3-VL 32B adalah berasingan) berjalan pada GPU Pascal 4 GB (GTX 1050 Ti, RAM sistem 16 GB).
- Panjang satu-laluan yang benar-benar kami hasilkan dan lulus pintu kualiti kami: 56, 141, 158, 175, 192, 209 bingkai pada 640x384, 24 fps (209 bingkai = 8.7 saat), dengan audio yang dijana oleh H3 sendiri [diukur: 209 bingkai dengan binari keluaran melalui `uret.ps1`, larian U209; latent sama bait demi bait dengan larian binaan pembangunan; bingkai dan audio dalam video sama, sha fail berbeza kerana bekas (container); bukti disimpan oleh penulis, tiada dalam repositori ini]. 209 ialah panjang terpanjang yang kami tonton dan dapati lancar [dilaporkan pengguna, 2026-11-19, video ditonton sepenuhnya; fail: output F209V2, 8.708 saat].
- **Dakwaan sama-bait, dengan skop yang jujur:** output disemak sama bait dengan rujukan tanpa tampalan hanya untuk 56 dan 141 bingkai. Untuk 158/175/192/209 bingkai kami menggunakan bendera yang sama dan rantai binari yang sama; tiada rujukan bait langsung (binaan tanpa tampalan tidak dapat menjalankan panjang itu pada GPU ini).
- Tetapan kualiti tidak pernah diturunkan: model/pengkuantuman yang sama, 6 langkah, cfg 1, 640x384, seed yang sama, VAE tanpa tiling.
- Kami tidak mendakwa sebagai yang pertama: kami mencari dan tidak menemui contoh luaran untuk ini pada 4 GB, tetapi itu bukan bukti bahawa tiada yang wujud.

## Susun atur
- `patches/` tampalan terhadap commit stable-diffusion.cpp yang dikunci (lihat nota di situ)
- `scripts/` skrip binaan, larian, VAE proses berasingan, pembantu pintu/konsistensi (`doku_norm.py`: lihat nota skala di bawah)
- `docs/KURULUM.md` perkakasan, langkah binaan dan larian (EN+TR)
- `docs/YAMALAR.md` senarai tampalan, `docs/KANITLAR.md` bukti, `docs/KAPILAR.md` jadual pintu kualiti, `docs/OLCUMLER.md` pengukuran, `docs/SIK_HATALAR.md` kesilapan lazim, `docs/LISANS_UYARISI.md` semua butiran lesen
- `scripts/` indeks ringkas: `hiz_kos3.ps1` pembungkus larian (`-Kuru` mencetak arahan yang tepat), `uretim_kapi.ps1` pintu kualiti, `dikis_denetim.py` semakan sambungan, `doku_norm.py` hingar ternormal tekstur, `bayt_kiyas.py` perbandingan bait, `derleme_sablonu.ps1` templat binaan (hanya menghentikan pembantu telemetri Visual Studio `vctip.exe` yang bermula selepas binaannya sendiri bermula, yang jika tidak akan menahan proses binaan selama beberapa minit; proses `vctip.exe` yang lain dibiarkan)

## Pintu kualiti (cara hasil diterima)

Pintu ini tidak menyemak konsistensi gerakan (lonjakan skala atau kedudukan objek): tonton keseluruhan video sebelum menerimanya.
1. Bilangan bingkai dan audio wujud; tiada fallback memori atau baris ALLOC_FAILED dalam log.
2. Pintu hingar mentah: baki median-filter <= 1.5 (skala 0-255).
3. Hingar ternormal tekstur, `scripts/doku_norm.py` (versi repositori ini): N = baki median / tekstur Sobel, setiap bingkai ke-6. **Nota skala:** dalam versi ini 10 klip yang diukur memberikan N = 0.034-0.052 (jadual dalam `docs/KAPILAR.md`; suku terakhir F192/F209V2 mencapai 0.062) dan ambang pintu tambahan ialah N <= 0.065. Pelaksanaan lain mengukur 0.028-0.036 pada klip yang sama, jadi ambang TIDAK boleh ditukar ganti antara versi. Pada tekstur yang sangat halus (barisan rumput) N bersih ialah 0.075, jadi ambang adalah mengikut keluarga babak. Penganggar frekuensi tinggi yang teguh (sigma-HH <= 1.5; bersih 0.74-1.19, hingar tambahan s=2 memberikan 2.2-3.0) ialah pintu tambahan yang disyorkan.

Skop: VideoTurko adalah mengenai SATU laluan (sehingga 209 bingkai, kira-kira 8.7 saat). Menyambung beberapa bahagian menjadi klip yang lebih panjang pernah dicuba; sambungannya kelihatan (babak tidak bersambung dengan bersih), jadi ia bukan sebahagian daripada projek ini. Jika anda mahukan klip yang lebih panjang, reka pendekatan anda sendiri.
Tetapan anda ialah milik anda: 209 bingkai ialah lalai yang kami uji pada kad 4 GB, bukan had yang mesti anda gunakan. Pilih mana-mana bilangan bingkai pada grid 17k+5 (56, 73, ... 192, 209; lihat `docs/KURULUM.md`), tukar prompt, seed, resolusi atau mana-mana bendera mengikut kehendak anda. Klip yang lebih pendek memerlukan lebih sedikit memori dan masa; GPU yang lebih besar mungkin memuatkan lebih banyak.

## Amaran lesen model
**VideoTurko hanya mengandungi tampalan dan skrip (MIT); sesiapa yang menggunakan model dan outputnya bertanggungjawab sendiri terhadap lesen MiniMax.** Bukan nasihat undang-undang. Di bawah ialah klausa MiniMax H3 Community License (2 Ogos 2026) yang diringkaskan beserta nombornya; lesen itu sendiri yang mengikat: https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/LICENSE

Repositori ini TIDAK mengandungi berat model (tiada MiniMax H3, GGUF HyperFlow-H3-Flash atau fail VAE). Projek ini tidak berafiliasi dengan atau disokong oleh MiniMax. Penggunaan komersial TIDAK dilarang (ini bukan lesen bukan-komersial); syaratnya ada di bawah.

**Wilayah (Applicable Territory)**
- **Preamble, I.3, I.5:** Seluruh dunia, KECUALI Kesatuan Eropah, United Kingdom, Republik Korea dan Amerika Syarikat. Menggunakan model dikira sebagai menerima lesen.
- **II:** Lesen bebas royalti, tidak boleh dipindah milik, terhad untuk menggunakan, menghasilkan semula, mengedar, mencipta terbitan dan mengubah suai, hanya di dalam wilayah dan mematuhi perjanjian serta Exhibit A. Orang di wilayah yang dikecualikan boleh memohon lesen berasingan daripada MiniMax.
- **V.4:** Menggunakan, menghasilkan semula, mengubah suai, mengedar atau memaparkan model, terbitannya DAN OUTPUTNYA (video/audio yang dijana) di luar wilayah tidak dibenarkan. **Jadi menerbitkan atau mempamerkan video yang dijana di EU/UK/Korea Selatan/AS adalah di luar lesen.**
- **Exhibit A-1:** Penggunaan di luar wilayah melanggar Acceptable Use Policy.

**Pengedaran (III)** (repositori ini tidak mengedar model; jika anda yang mengedarnya)
- **III.1:** Berikan setiap penerima satu salinan lesen. **III.2:** Tandakan fail yang diubah suai dengan notis yang jelas.
- **III.3:** Digalakkan (tidak wajib): notis "Powered by MiniMax H3", pengecam penjanaan AI pada fail yang dihasilkan, penulisan awam.
- **III.4:** Pengedaran MESTI disertakan dengan fail NOTICE yang mengandungi: "MiniMax H3 is licensed under the MiniMax H3 Community License Agreement, Copyright © 2026 MiniMax. All Rights Reserved."
- **Exhibit A-12:** menerbitkan kandungan ke mana-mana persekitaran awam tanpa mendedahkan dengan jelas bahawa ia dijana mesin adalah dilarang: labelkan video yang dijana AI apabila anda menerbitkannya (senarai penuh: `docs/LISANS_UYARISI.md`).
- **III (perenggan terakhir):** Anda boleh menambah hak cipta anda sendiri pada pengubahsuaian anda tetapi tidak boleh mengenakan terma tambahan atau berbeza ke atas penggunaan/pengedaran; peraturan wilayah tetap terpakai.

**Terma komersial (IV)**
- **IV.1:** Jika produk/perkhidmatan komersial anda menjana pendapatan tahunan melebihi USD 20 juta (atau setara), dapatkan kebenaran bertulis TERLEBIH DAHULU daripada api@minimax.io (subjek "MiniMax H3 licensing - authorization request").
- **IV.2:** Antara muka produk/perkhidmatan komersial yang menggunakan model ini mesti memaparkan "MiniMax H3" dengan jelas.

**Sekatan penggunaan (V)**
- **V.1:** Patuhi undang-undang yang terpakai (termasuk pematuhan perdagangan) dan Exhibit A. **V.2:** Ikat sesiapa yang anda beri akses dengan terma yang sekurang-kurangnya sama melindungi seperti sekatan ini dan maklumkan kepada mereka.
- **V.3:** Anda tidak boleh menggunakan model atau OUTPUTNYA untuk menambah baik mana-mana model AI lain (selain MiniMax H3 dan terbitannya). (I.11: penyulingan (distillation) dan latihan pada output sintetik menjadikan sesuatu model sebagai "terbitan"; output itu sendiri bukan terbitan.)
- **V.5:** Jika anda menawarkan kepada pihak ketiga produk/perkhidmatan/perkhidmatan terhos yang menjana output dengan model ini: sebelum dan sepanjang operasi, perlindungan teknikal dan organisasi yang munasabah, mekanisme pelaporan, siasatan segera, dan pengeluaran/penyahaktifan/penggantungan pelanggar berulang.

**Cap dagangan dan hak (VI)**
- **VI.1:** Anda memiliki karya terbitan dan terbitan model yang anda cipta (tertakluk kepada hak MiniMax). **VI.2:** Nama/cap MiniMax tidak dilesenkan (selain yang diperlukan untuk menerangkan dan mengedar); cap "MiniMax H3" hanya boleh digunakan untuk mematuhi III.3, di dalam wilayah; jangan membayangkan gabungan.
- **VI.3:** Jika anda menyaman MiniMax atau sesiapa dengan mendakwa bahan/output melanggar hak anda, semua lesen anda tamat pada hari itu; anda mempertahankan dan menanggung rugi MiniMax terhadap tuntutan pihak ketiga yang timbul daripada penggunaan/pengedaran oleh anda atau orang lain.
- **VI.4:** MiniMax tidak menuntut hak ke atas output; anda dan pengguna anda bertanggungjawab ke atas output dan penggunaannya.

**Penafian dan penamatan (VII, VIII, IX)**
- **VII.1:** Tiada kewajipan sokongan/kemas kini. **VII.2:** Model dan output disediakan "AS IS", tanpa waranti; anda menentukan kesesuaian dan menanggung risikonya. **VII.3:** MiniMax dan sekutunya tidak bertanggungjawab atas sebarang kerugian (setakat yang dibenarkan undang-undang).
- **VIII.1:** Berkuat kuasa apabila diterima/diakses. **VIII.2:** Jika berlaku pelanggaran, MiniMax boleh menamatkan; anda mesti berhenti menggunakan/mengedar, memadam salinan dan memaklumkan penerima (VI.1, VI.3, VII, IX kekal berkuat kuasa).
- **IX:** Undang-undang HKSAR Hong Kong; bidang kuasa eksklusif mahkamah Hong Kong (UN CISG dikecualikan).
- **Nota tambahan:** pengekod MiniMax H3 menggunakan Qwen3-VL-32B (Apache 2.0).

**Acceptable Use Policy (Exhibit A)** (JANGAN gunakan model, terbitan atau output untuk)
- A-1 penggunaan di luar wilayah; A-2 melanggar undang-undang atau harta intelek pihak ketiga; A-3 mencederakan diri sendiri atau orang lain; A-4 menggunakan semula/mengedar output untuk mencederakan; A-5 memintas perlindungan; A-6 mengeksploitasi/mencederakan kanak-kanak; A-7 maklumat palsu yang boleh disahkan untuk mencederakan orang lain atau mempengaruhi pilihan raya; A-8 penglibatan dalam talian palsu (ulasan palsu dsb.); A-9 fitnah, penghinaan, gangguan; A-10 perisian hasad (malware); A-11 data peribadi untuk mencederakan orang lain; **A-12 menerbitkan kandungan ke mana-mana persekitaran awam (termasuk siaran bot) tanpa mendedahkan dengan jelas dan ketara bahawa ia dijana mesin**; A-13 penyamaran tanpa persetujuan; A-14 keputusan automatik berisiko tinggi dalam bidang kritikal (penguatkuasaan undang-undang, imigresen, kesihatan, infrastruktur kritikal, kredit, pekerjaan, perumahan, pendidikan, pemarkahan sosial, insurans, dsb.); A-15 melanggar piawaian sosial, etika, moral negara/wilayah lain; A-16 ekstremisme ganas/keganasan; A-17 diskriminasi/kemudaratan berdasarkan ciri yang dilindungi; A-18 mengeksploitasi kumpulan yang terdedah; **A-19 tujuan ketenteraan**; A-20 aktiviti profesional tanpa kebenaran/lesen (kewangan, undang-undang, perubatan, dsb.).
- Nota: ini ialah ringkasan dalam bahasa mudah; teks lesen bahasa Inggeris diutamakan jika ada keraguan.

## Label bukti

Satu set untuk semua dokumen (ejaan lama dalam kurungan):
- **[diukur]** (TR: ölçtüm, olctum): dijalankan dalam projek ini, laluan bukti wujud.
- **[dibaca]** (TR: okudum yol, okudum): sumber atau skrip dibaca, tidak dijalankan.
- **[reka bentuk]** (TR: tasarım, tasarim): direka, belum dilihat dalam larian sebenar.
- **[anggaran]** (TR: tahmin): belum disahkan.
- **[belum dicuba]** (TR: denenmedi): tidak pernah dijalankan.
- **[dilaporkan pengguna]** (TR: kullanıcı bildirdi): dinyatakan oleh pengguna, dengan tarikh; tidak diukur secara bebas.
- **[dikira]** (TR: hesap; ejaan lama: calculated, hesap): nombor yang diperoleh daripada input yang diukur, bukan diukur sendiri; terbitannya ditulis di sebelahnya. [proposal] / [öneri] dalam teks lama = [anggaran].

Nama larian yang digunakan dalam kurungan (nama larian dalaman kami, bukan fail dalam repositori ini): U209 = 209 bingkai dengan binari keluaran melalui `uret.ps1`; B209 dan B192 = larian image-to-video (`-InitImg`) pada 209 dan 192 bingkai; B56VT2 = binari keluaran, 56 bingkai, dibandingkan dengan rujukan bait 56 bingkai R0; F209b, F209V2, F209V2K = larian 209 bingkai pada binaan pembangunan (butiran: `docs/OLCUMLER.md`).

## Had yang diketahui
- **Bukti bait** (cara menghasilkannya sendiri: `docs/KANITLAR.md`, "R0 ve latent referansi nasil uretilir"; disahkan pada kad sm_61 kami, GPU lain mungkin tidak sama bait [anggaran]): dengan siri tampalan kami (bendera memori dihidupkan) satu larian 56 bingkai memberikan sha256 `0979f156d548169b...`, sama dengan rujukan [diukur]; pada 141 bingkai sha256 latent `E5D028F8632BE4FE...` sama (dengan bendera 0013/0014). Bingkai 158 hingga 209 tiada rujukan bait langsung; rantai pintu ialah buktinya. Lulus pintu berangka tidak menjamin klip yang baik: konsistensi gerakan dari semasa ke semasa disemak dengan mata (lihat `docs/KAPILAR.md`).
- **209 bingkai, set bendera yang mana:** bukti rantai bait 209 bingkai diambil dengan set bendera F209V2 pada binaan pembangunan (tiada bendera block-tail, dibina tanpa tampalan 0019/0020); `uret.ps1` menggunakan resipi ini untuk 209 bingkai [dibaca: skripnya; larian enjin sebenar melalui `uret.ps1` lulus dalam larian U209].
- Disahkan pada satu kad (GTX 1050 Ti 4 GB); kad lain tidak dicuba.
- **Binari mana yang diukur:** latent 141 bingkai dan rantai bait diukur dengan binaan pembangunan kami. Binari keluaran yang anda muat turun ialah binaan baharu: pintu bait 56 bingkainya lulus (butiran seterusnya) dan larian 209 bingkai melalui `uret.ps1` lulus pintu (larian U209, 3414 saat, puncak VRAM 3777 MiB) [diukur]; berbanding larian 209 binaan pembangunan, latent sama bait demi bait; dalam video bingkai (md5) dan audio sama, sha256 fail AVI berbeza kerana bekas (container) [diukur] (lihat `docs/OLCUMLER.md`, bahagian 0).
- **Binari keluaran, 56 bingkai:** binari keluaran (sd-cli `c5cebe78...`, stable-diffusion.dll `e5d3d329...`) memberikan hasil 56 bingkai yang sama bait dengan R0 (sha256 `0979f156d548169be03acd1a9d7617102a75333aa48a28d6bbfd1cc5fa3f604d`; md5 setiap bingkai dan audio sama), dijalankan terus dengan bendera lalai (tanpa pemboleh ubah `SD_*`), kod keluar 0, 601 saat [diukur: larian B56VT2, 2026-11-19; bukti disimpan oleh penulis, tiada dalam repositori ini]. Skop: hanya kad sm_61 kami dan 56 bingkai; bukan ujian pemasangan clean-root; latent 141 bingkai dan rantai 209 diukur dengan binari yang lebih lama dan TIDAK diulang dengan binari ini [belum dicuba]. Percubaan pertama (B56VT, melalui skrip pembantu) berakhir secara senyap selepas 58 saat, punca tidak diketahui [anggaran: tekanan memori]; percubaan kedua menjalankan `sd-cli` terus.
- Skrip pemasangan dan larian belum disahkan daripada folder kosong (ujian clean-root belum dibuat).
- Pelan hala tuju dan langkah seterusnya: `ROADMAP.md`.

## Status dan had
- Disahkan pada satu mesin (GTX 1050 Ti 4 GB, RAM 16 GB, i7-7700HQ). Kad 4 GB lain dan saiz RAM lain mungkin berbeza.
- **Lalai 209 bingkai (8.7 saat):** lulus pintu kualiti kami (hingar 1.08, larian F209V2K) [diukur: 209 bingkai dengan binari keluaran melalui `uret.ps1`, larian U209; latent sama bait demi bait dengan larian binaan pembangunan; bingkai dan audio dalam video sama, sha fail berbeza kerana bekas (container); bukti disimpan oleh penulis, tiada dalam repositori ini]. Pada 209 bingkai puncak VRAM DiT ialah 3777 MiB daripada 4096 MiB (larian F209b dan U209; bacaan `nvidia-smi` seluruh kad), margin nipis: beban GPU lain (skrin, aplikasi lain) boleh menyebabkan larian gagal pada `blocks.0`; diuji hanya pada GTX 1050 Ti. Keadaan skrin semasa larian itu tidak direkodkan; jika skrin anda berjalan pada kad ini, VRAM yang tersedia lebih sedikit [anggaran: beban skrin Windows kira-kira 100-300 MB]; jika perlu, sambungkan skrin ke GPU bersepadu [nasihat, belum diuji]. Pensampelan mengambil 2730 saat (larian U209: langkah 436-483 saat) dan penyahkodan VAE proses berasingan 173 saat (peringkat 2 keseluruhan 193 saat bersama penyahkodan audio) [diukur: U209 binari keluaran; larian pembangunan lama: 2664 saat dan 174 saat]. Pada peringkat 1 VAE dalam-proses kehabisan memori dan jatuh kepada temporal tiling (320 saat); output itu dibuang, video datang daripada peringkat 2 tanpa tiling. Puncak RAM tidak diukur dalam U209. Klip yang lebih panjang daripada 209 bingkai bukan sebahagian daripada keluaran ini.
- **Image-to-video (`-InitImg`):** dengan imej awal, had ialah 192 bingkai (8.0 saat pada 24 fps) pada GPU ini: 209 bingkai tidak muat (kekurangan kira-kira 17.5 MB VRAM pada blok 0: perlu 2587 MB, tersedia 2570 MB); 192 bingkai berjalan melalui `uret.ps1` dalam 3086 saat dengan puncak VRAM 3783 MiB dan pintu lulus [diukur: larian B209 dan B192, 2026-11-20, satu babak; bukti disimpan oleh penulis, tiada dalam repositori ini]. Tidak dicuba pada GPU lain [belum dicuba].
- **RAM kosong penting:** anda memerlukan kira-kira 11 GB RAM KOSONG (proses enjin memegang kira-kira 11 GB) [diukur]. Dengan RAM kosong yang terlalu sedikit proses boleh mati tanpa mesej ralat [anggaran: kami melihatnya sekali dengan kira-kira 300 MB RAM kosong ketika `sd-cli` memegang kira-kira 10 GB]. Jangan buka program besar lain semasa ia berjalan: pada mesin 16 GB hanya kira-kira 0.3-0.5 GB tinggal kosong, dan di bawah tekanan memori larian boleh mati secara senyap. Sebelum bermula, tutup pelayar, permainan dan program besar lain, dan semak RAM yang kosong.
- **Ujian clean-root belum dibuat:** skrip pemasangan dan larian belum disahkan daripada folder kosong hanya dengan arahan ini; bahagian ini akan dikemas kini apabila ujian itu (termasuk perbandingan bait 56 bingkai dengan rujukan) direkodkan.
- Tiada video yang dijana disertakan di sini.

<!-- i18n-source: README.md sha256:0070eed33ffd -->
