# VideoTurko

[English](README.md) · [Türkçe](README.tr.md) · [简体中文](README.zh-CN.md) · [日本語](README.ja.md) · [Español](README.es.md) · [Русский](README.ru.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [العربية](README.ar.md) · [Português (BR)](README.pt-BR.md) · [Italiano](README.it.md) · [한국어](README.ko.md) · [हिन्दी](README.hi.md) · Bahasa Indonesia · [Tiếng Việt](README.vi.md) · [Polski](README.pl.md) · [Nederlands](README.nl.md) · [Українська](README.uk.md) · [فارسی](README.fa.md) · [עברית](README.he.md) · [ไทย](README.th.md) · [বাংলা](README.bn.md) · [اردو](README.ur.md) · [Ελληνικά](README.el.md) · [Čeština](README.cs.md) · [Română](README.ro.md) · [Magyar](README.hu.md) · [Svenska](README.sv.md) · [Azərbaycanca](README.az.md) · [Bahasa Melayu](README.ms.md)

Terjemahan mengikuti README bahasa Inggris ini. Jika terjemahan berbeda atau tertinggal, teks bahasa Inggris yang berlaku, terutama untuk teks lisensi dan keamanan ([`SECURITY.md`](SECURITY.md) dan [`docs/LISANS_UYARISI.md`](docs/LISANS_UYARISI.md) hanya dipelihara dalam bahasa Inggris dan Turki).

![Windows](https://img.shields.io/badge/Windows-10%2F11-blue) ![GPU](https://img.shields.io/badge/NVIDIA-4%20GB%20(sm__61)-76b900) ![License](https://img.shields.io/badge/code-MIT-green) ![Status](https://img.shields.io/badge/status-clean--root%20test%20pending-orange)

> **Sebelum mulai (lisensi, wilayah):** repositori ini berlisensi MIT dan hanya berisi patch dan skrip. Model MiniMax H3 yang diunduhnya berada di bawah MiniMax H3 Community License: wilayahnya tidak mencakup Uni Eropa, Inggris Raya, Korea Selatan, dan Amerika Serikat, dan model, turunannya **serta keluarannya (video yang Anda hasilkan)** tidak boleh digunakan, didistribusikan, atau ditampilkan di sana (V.4). Penggunaan komersial diizinkan dalam batas ketentuan lisensi. Baca [`docs/LISANS_UYARISI.md`](docs/LISANS_UYARISI.md) sebelum memasang; ini bukan nasihat hukum.

> **Dalam 30 detik:** kartu grafis 4 GB bisa membuat video MiniMax H3 sepanjang 209 frame (8,7 dtk) dalam satu kali proses: terverifikasi pada satu mesin (GTX 1050 Ti 4 GB; instalasi `kur.ps1` lengkap pada folder kosong belum diverifikasi dari awal sampai akhir) [terukur: 209 frame dengan binary rilis melalui `uret.ps1`, run U209; latent identik byte demi byte dengan run dengan build pengembangan; frame dan audio pada video identik, sha file berbeda karena kontainer; bukti disimpan oleh penulis, tidak ada di repo ini]; dengan `-InitImg` (gambar ke video) paling banyak 192 frame (8,0 dtk) [terukur: run B192]; 209 frame memakan waktu sekitar 57 menit, batas waktu bawaan 80 menit [terukur: run U209]; 3 langkah di bawah adalah cara menjalankannya.

VideoTurko: patch memori stable-diffusion.cpp beserta resep menjalankan MiniMax H3 text-to-video di GTX 1050 Ti 4 GB, hingga 209 frame (8,7 dtk) dalam satu kali proses; image-to-video (`-InitImg`) hingga 192 frame (8,0 dtk) (209 frame diverifikasi dengan rantai byte; identik byte dengan proses tanpa patch pada pemeriksaan 56 dan 141 frame).

## Mulai cepat (Windows, 3 langkah)
**Status: skrip instalasi/penggunaan di bawah masih diselesaikan dan uji clean-root belum dilakukan; tidak ada yang di sini diklaim berfungsi sampai uji itu lulus (lihat "Status dan batasan").**

1. **Unduh** repositori ini (tombol hijau **Code**, lalu **Download ZIP**) dan ekstrak ke folder PENDEK, misalnya `C:\vt`.
2. **Pasang: klik dua kali `kur.cmd`** (jendela hitam terbuka dan menampilkan setiap langkah; menutupnya menghentikan pemasangan, dan menjalankannya lagi melanjutkan dari tempat berhenti: berkas model yang terunduh separuh dilanjutkan [dibaca: skrip unduh menyimpan berkas `.part` dan melanjutkan darinya; kelanjutan penuh 29 GiB belum diukur]). Jika Windows memberi peringatan tentang berkas yang diunduh, gunakan perintah PowerShell di bawah sebagai gantinya [saran, belum diuji pada ZIP yang diunduh]. Lebih suka baris perintah? Buka PowerShell di folder itu (ketik `powershell` di bilah alamat Explorer) dan jalankan pemasangan yang sama:
   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File scripts\kur.ps1
   ```
   Root instalasi adalah folder hasil ekstrak (engine masuk ke `engine\bin`, model ke `model`); untuk memakai lokasi lain, atur dulu variabel lingkungan `VT_ROOT`. Skrip memeriksa GPU, driver, RAM, dan disk, mengambil engine dan model (zip engine dan file model yang baru diunduh diperiksa sha256; file model yang sudah ada dengan ukuran yang benar hanya diperiksa ukurannya, `scripts\modelleri_indir.ps1 -Dogrula` menjalankan pemeriksaan sha256 penuh), menjalankan pemeriksaan nyata singkat, dan mencetak READY hanya jika pemeriksaan itu lulus [rancangan: `kur.ps1` belum pernah dijalankan penuh di folder bersih; kalimat ini diperbarui setelah uji folder bersih]. `-ExecutionPolicy Bypass` hanya berlaku untuk proses ini; baca `scripts\kur.ps1` terlebih dahulu, seperti pada installer mana pun.
   Zip engine diunduh dari rilis GitHub v0.1.0 (dipublikasikan 2026-11-19; sha256-nya dikunci di `kur.ps1`). Jika offline atau memakai build sendiri, berikan zip lokal: `-MotorZip <path> -CudaZip <path>`. Zip lokal juga diperiksa dengan sha256 terkunci yang sama (file `.sha256` di sampingnya diabaikan), jadi harus zip rilis; untuk build sendiri, atur dulu `VT_MOTOR_SHA256` / `VT_CUDA_SHA256` ke sha256 build tersebut. sha256 yang salah menghentikan proses dengan exit 1. Hanya `.exe`/`.dll` yang masuk ke `engine\bin`; lisensi dan README masuk ke `engine\lisanslar\<zip name>\`. [dicoba dengan zip dist sebelum rilis: `.sha256` pendamping beserta peringatan merujuk-diri-sendiri, binary dan DLL terpasang, `sd-cli --help` berjalan; sha binary terpasang cocok (`c5cebe78...`, `e5d3d329...`); langkah model dan pemeriksaan 5 frame pada `kur.ps1` BELUM dijalankan di GPU sungguhan]
   **Lisensi model:** sebelum langkah model, installer mencetak ringkasan lisensi (`docs/LISANS_KABUL.txt`, teks lengkap `docs/LISANS_UYARISI.md`: MiniMax H3 Community License, batasan wilayah yang juga mencakup video hasil generasi, aturan komersial dan label AI) dan meminta Anda menerimanya (`E` = ya). Bacalah terlebih dahulu. Untuk eksekusi tanpa pengawasan Anda bisa memberikan `-LisansKabul E`, yang berarti Anda sudah membaca dan menerimanya sendiri; jangan menambahkannya atas nama orang lain. (Agen AI: ikuti `AGENTS.md`; jangan pernah mengetik E tanpa persetujuan pengguna.) Tanpa persetujuan, `kur.ps1` berhenti dengan exit code 2 dan tidak mengunduh model apa pun.
3. **Video pertama Anda (56 frame, sekitar 11 mnt pada GTX 1050 Ti kami** [terukur: 641 dtk, run R0, `docs/OLCUMLER.md`; kartu lain tidak diukur]**)**: saat pemasang mencetak `HAZIR / READY`, jalankan
   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File scripts\uret.ps1 -Istem docs\ornek_istem_R0.txt -Kare 56
   ```
   (jalan pintas: seret berkas teks prompt ke `uret.cmd`, atau jalankan `uret.cmd docs\ornek_istem_R0.txt`: run 56 frame yang sama). Videonya ada di `runs\`. Lalu tulis prompt Anda sendiri dalam berkas teks (satu paragraf bahasa Inggris, kalimat `audio:` opsional) dan jalankan klip terpanjang yang kami cakup (bawaan, sekitar 57 mnt [terukur: run U209]):
   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File scripts\uret.ps1 -Istem istem.txt -Kare 209
   ```
   `-Kare` mengikuti kisi 17k+5 (56, 73, ... 192, 209); bawaan 209 (8,7 dtk), panjang terpanjang yang kami cakup. VAE berjalan di proses terpisah, tidak pernah dipecah menjadi tile [run engine nyata melalui `uret.ps1` dengan binary rilis, VAE proses terpisah, lulus pada run U209].

   Panduan menulis prompt: [`docs/ISTEM_YAZIMI.md`](docs/ISTEM_YAZIMI.md) (pola satu pengambilan gambar tanpa putus, potongan waktu yang sama panjang, dua contoh lengkap).

| Persyaratan | Nilai |
|---|---|
| OS | Windows 10/11, 64-bit |
| GPU | NVIDIA, 4 GB atau lebih; diuji hanya pada GTX 1050 Ti (sm_61); margin tipis (3777/4096 MiB pada 209 frame): layar atau browser yang sibuk bisa menggagalkan proses; tidak ada kartu 4 GB lain yang dicoba |
| RAM | 16 GB (puncak sekitar 11 GB; tutup program lain) |
| Disk | minimal 32 GiB kosong (disarankan 40 GiB atau lebih: di antara 32 dan 40 pemasang mencetak peringatan, `[VT-W-DISK-PAY]` [terukur: run `-Kuru` dengan disk simulasi]), model di SSD (NVMe lebih baik) |
| Unduhan | zip engine 36,8 MB + zip runtime CUDA 567,5 MB [terukur] + model 31.473.112.040 byte (sekitar 29,3 GiB) [dibaca: ukuran di `scripts/modeller.json`]; total sekitar 30 GiB |
| Model | tidak disertakan; diambil oleh installer di bawah lisensi MiniMax (lihat peringatan di bawah). Model (29,3 GiB, 31.473.112.040 byte di `scripts/modeller.json`) tidak ada di repositori atau rilis ini: batas ukuran file/rilis GitHub berlaku, dan `kur.ps1` mengunduhnya dari sumber resmi dengan verifikasi sha256. |

Kode keluar `kur.ps1`: 0 READY, 1 galat, 2 butuh masukan pengguna (lisensi, atau belum ada rilis/zip), 3 perangkat keras atau disk tidak mencukupi, 4 dihentikan (file DUR). `uret.ps1` hanya menerima hasil jika file `.avi` ada, jumlah frame benar, dan log bersih [terukur: satu run nyata melalui `uret.ps1` pada binary rilis, run U209, 209 frame, gerbang lulus]. Kode keluar `uret.ps1`: 0 DONE (gerbang kualitas lulus), 1 galat atau keluaran tidak valid (termasuk video tanpa aliran audio), 2 dihentikan (file DUR), 5 `KAPI RED` (gerbang kualitas gagal: klip tidak diterima, keputusan ada di tangan Anda), 6 gerbang tidak dapat dijalankan (klip tidak diterima). Rincian di AGENTS.md. [terukur: kode keluar 0, 1 (video bisu), 5, dan 6 pada skenario dengan engine palsu dan gerbang palsu; engine nyata: exit 0 pada run U209]

### Pemecahan masalah (rincian: `docs/SIK_HATALAR.md`)
Baris galat dari skrip kami membawa kode tetap, misalnya `HATA: [VT-E-DLL] ...` atau `UYARI: [VT-W-DISK-PAY] ...`. Cari kodenya di [`docs/SIK_HATALAR.md`](docs/SIK_HATALAR.md) (contoh jangkar `#vt-e-dll`) atau di `docs/hata_imzalari.json`, dan tulis kodenya di issue Anda. Kolom pertama tabel di bawah tetap seperti yang dicetak (jangan terjemahkan kode dan teks log).

| Yang Anda lihat | Artinya, dan yang harus dilakukan |
|---|---|
| `STATUS_DLL_NOT_FOUND` / `cudart64_12.dll not found` (#13) | Jangan menjalankan `sd-cli.exe` secara manual; jalankan `scripts\kur.ps1`, yang menempatkan DLL CUDA pada tempatnya. |
| `failed during weight preparation` pada `blocks.0` (#1, #3, #5) | VRAM tidak cukup pada gerbang memori: pakai jumlah frame yang lebih kecil pada kisi 17k+5, tutup program GPU lain, pertahankan flag bawaan. |
| `retrying with temporal tiling` (#6) | VAE beralih ke mode tiling; keluarannya tidak valid untuk keperluan kualitas. Jalankan ulang. |
| Run berakhir di batas waktu, tanpa video (#7) | Naikkan `-TavanDk` untuk klip panjang (batas waktu bawaan: 80 menit untuk 209 frame, diatur oleh `uret.ps1`; run 209 frame kami memakan waktu 57 menit [terukur: run U209]). |
| Exit code kosong tetapi "finished" (#14) | Wrapper membaca exit code terlalu cepat; jalankan ulang, dan periksa bahwa file video ada. |
| Sistem melambat, swapping (#18) | Engine memakai sekitar 10-11 GB RAM; tutup browser dan program lain. |
| sha256 tidak cocok / unduhan gagal | Biasanya unduhan terputus: jalankan perintah yang sama lagi, file yang sudah terverifikasi dilewati. |

**Terkendala atau penasaran?** [`SUPPORT.md`](SUPPORT.md) (tempat bertanya; waktu balasan adalah target, bukan komitmen) · [`PRIVACY.md`](PRIVACY.md) (tanpa telemetri; jaringan hanya dipakai untuk mengunduh mesin dan model dari host yang terdaftar) · [`SECURITY.md`](SECURITY.md) (laporan privat) · [`CONTRIBUTING.md`](CONTRIBUTING.md) (pull request pertama dalam 5 langkah; tidak perlu GPU untuk dokumen dan skrip).

### Baru di v0.1.1: lebih banyak opsi (rincian: `AGENTS.md`, `docs/SIK_HATALAR.md` 19-23)
Tanpa opsi-opsi ini tidak ada yang berubah pada kartu 4 GB (pemeriksaan byte 56 frame terhadap referensi kami kembali lulus dengan v0.1.1 [terukur]). Tambahkan `-Kuru` ke perintah apa pun untuk melihat apa yang akan dijalankan.
- `-EndImg`: berikan juga frame terakhir (frame pertama dan terakhir, "FLF"); batasnya 175 frame pada kartu di bawah 8 GB (192 tidak muat di 4 GB), 192 pada kartu 8 GB ke atas. Di GTX 1050 Ti kami opsi ini selalu berjalan dalam dua proses: 56 frame 1040 dtk, 175 frame 2887 dtk (48 menit), keduanya lulus gerbang [terukur]. Tips menulis prompt: `docs/ISTEM_YAZIMI.md`.
- `-W` / `-H`: ukuran lain, misalnya vertikal 384x640; kelipatan 32, luas minimal 640x384 (tidak pernah lebih kecil). Belum diuji pada 4 GB; pada kartu di bawah 8 GB, ukuran yang melampaui pekerjaan terbesar yang pernah kami ukur akan ditolak. Ambang gerbang kualitas dikalibrasi pada 640x384.
- `-TekAsama`: satu proses alih-alih dua, khusus kartu besar; tidak pernah diaktifkan secara otomatis.
- GPU yang lebih baru (compute capability 7.0+, misalnya RTX 20/30/40): `GGML_CUDA_CUBLAS_COMPUTE_TYPE=f32` diatur otomatis kecuali Anda mengaturnya sendiri; ini memperbaiki video yang hitam total pada 141+ frame di RTX 4070 Ti milik pelapor [dilaporkan pengguna, issue #1]. Tanpa Python + OpenCV, `uret.ps1` kini berhenti dengan exit 6 sebelum pekerjaan GPU (tidak ada video yang dibuat, tidak ada RED yang menyesatkan).
- Terima kasih kepada @SinanC73 atas laporan RTX 4070 Ti yang mendorong perubahan ini ([issue #1](https://github.com/alexturkey/VideoTurko/issues/1)).

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

## Disk layout and removal

> Translation of this section is pending; the English text is authoritative. / Bu bölümün çevirisi bekliyor; İngilizce metin esastır.

Everything VideoTurko installs lives in one root folder, `<VT_ROOT>` (default: the folder you extracted; set the environment variable `VT_ROOT` before running the scripts to use another place). Nothing is written to the system PATH, the user profile or the registry.

| Folder under `<VT_ROOT>` | What is in it | Size |
|---|---|---|
| `engine\bin`, `engine\lisanslar` | the engine from the GitHub release (exe and DLLs) and the license files of its zips | not measured |
| `model` | the model files, downloaded from the official source and sha256-checked | 29.3 GiB [read: `AGENTS.md`] |
| `indirme` | downloaded zips and their unpacking leftovers | not measured |
| `runs` | your finished videos | grows with use |
| `.venv` (optional) | the Python environment for the quality gate (opencv-python, numpy) | not measured |

The install scripts run no `pip`, `uv` or Hugging Face tool, so they write no package or model cache. Only if you install the optional gate packages yourself, keep the cache in the root too: `py -3 -m venv <VT_ROOT>\.venv`, then `<VT_ROOT>\.venv\Scripts\python.exe -m pip install --cache-dir <VT_ROOT>\.onbellek\pip opencv-python numpy`; the scripts use `<VT_ROOT>\.venv` when it exists (unless `VT_PYTHON` is set).

**Already downloaded the model?** Point the installer at it with `-ModelKlasoru <folder>`: files whose sha256 matches are linked instead of downloaded. On the same drive this is a hard link (the data exists once, so deleting the source folder later does not free the space); on another drive it is a COPY (about 29 GiB twice). A complete file with the right sha256 is skipped, and an interrupted download continues from its `.part` file.

**Removal:** close VideoTurko, copy out the videos you want to keep from `runs`, then delete the `<VT_ROOT>` folder. That is the whole uninstall. Not ours to remove: a `pip install` you made into the system Python (use a `.venv` as above to avoid that) and anything installed with `winget`.

## Kartu apa yang saya punya? (hanya tautan)

Nilai repo ini adalah patch yang membuat model muat di 4 GB beserta gerbang kualitas. Untuk kartu lain, rilis CUDA stable-diffusion.cpp yang sudah jadi adalah sebuah OPSI: kami tidak mengukurnya dan gerbang kualitas kami tidak dijalankan padanya. Pengukuran kami sendiri mencakup satu kartu (GTX 1050 Ti 4 GB). Selebihnya adalah laporan komunitas: kami memberi tautannya dan tidak menjaminnya.

| Perangkat Anda | Di mana melihat | Bukti |
|---|---|---|
| GTX 1050 Ti 4 GB (zip rilis kami) | README ini, `docs/OLCUMLER.md` | [terukur] |
| Kartu NVIDIA lainnya (compute capability 7.0+: RTX 20/30/40) | `docs/KART_PROFILLERI.md` (`uret.ps1` mengatur `f32` secara otomatis; rilis CUDA stable-diffusion.cpp yang sudah jadi: sebuah opsi, tidak kami ukur [belum dicoba]) | [dilaporkan pengguna] |
| seri RTX 50 | `docs/KURULUM.md`, `docs/RTX5060_TEST_RAPORU.md` | [dilaporkan pengguna, PR #3] |
| AMD / non-NVIDIA | `docs/AMD_ROCM.md` (catatan komunitas, tanpa dukungan resmi; mesin rilis adalah CUDA) | [dilaporkan pengguna, PR #4] |
| Film yang lebih panjang dari beberapa klip | `docs/KLIP_ZINCIRI.md`, `scripts/zincir.py` | [dilaporkan pengguna]; kualitas film yang dirangkai tidak kami ukur [belum dicoba] |

Lisensi: persetujuan lisensi MiniMax H3 (`docs/LISANS_KABUL.txt`) berlaku di semua jalur; langkah persetujuan di `kur.ps1` tidak berjalan dengan rilis yang sudah jadi.

## Apa ini
Sekumpulan patch kecil memori/penjadwalan untuk stable-diffusion.cpp beserta resep penggunaan, pemeriksaan, dan pengukuran yang memungkinkan MiniMax H3 (DiT 33B; kami menjalankan GGUF HyperFlow Flash 13.7B Q4_K_M; text encoder Qwen3-VL 32B terpisah) berjalan di GPU Pascal 4 GB (GTX 1050 Ti, RAM sistem 16 GB).
- Panjang satu-proses yang benar-benar kami hasilkan dan lulus gerbang kualitas kami: 56, 141, 158, 175, 192, 209 frame pada 640x384, 24 fps (209 frame = 8,7 dtk), dengan audio buatan H3 sendiri [terukur: 209 frame dengan binary rilis melalui `uret.ps1`, run U209; latent identik byte demi byte dengan run dengan build pengembangan; frame dan audio pada video identik, sha file berbeda karena kontainer; bukti disimpan oleh penulis, tidak ada di repo ini]. 209 adalah panjang terpanjang yang kami tonton dan kami nilai mulus [dilaporkan pengguna, 2026-11-19, video ditonton penuh; file: keluaran F209V2, 8,708 dtk].
- **Klaim identik-byte, dengan cakupan yang jujur:** keluaran diperiksa identik byte dengan referensi tanpa patch hanya untuk 56 dan 141 frame. Untuk 158/175/192/209 frame kami memakai flag yang sama dan rantai binary yang sama; tidak ada referensi byte langsung (build tanpa patch tidak bisa menjalankan panjang itu di GPU ini).
- Pengaturan kualitas tidak pernah diturunkan: model/kuantisasi sama, 6 langkah, cfg 1, 640x384, seed sama, VAE tanpa tiling.
- Kami tidak mengklaim sebagai yang pertama: kami mencari dan tidak menemukan contoh luar untuk ini di 4 GB, tetapi itu bukan bukti bahwa tidak ada.

## Tata letak
- `patches/` patch untuk commit stable-diffusion.cpp yang dikunci (lihat catatan di sana)
- `scripts/` skrip build, jalankan, VAE proses terpisah, pembantu gerbang/konsistensi (`doku_norm.py`: lihat catatan skala di bawah)
- `docs/KURULUM.md` perangkat keras, langkah build dan jalankan (EN+TR)
- `docs/YAMALAR.md` daftar patch, `docs/KANITLAR.md` bukti, `docs/KAPILAR.md` tabel gerbang kualitas, `docs/OLCUMLER.md` pengukuran, `docs/SIK_HATALAR.md` kesalahan umum, `docs/LISANS_UYARISI.md` seluruh butir lisensi
- `scripts/` indeks singkat: `hiz_kos3.ps1` wrapper jalankan (`-Kuru` mencetak perintah persisnya), `uretim_kapi.ps1` gerbang kualitas, `dikis_denetim.py` pemeriksaan sambungan, `doku_norm.py` noise ternormalisasi tekstur, `bayt_kiyas.py` perbandingan byte, `derleme_sablonu.ps1` templat build (hanya menghentikan helper telemetri Visual Studio `vctip.exe` yang mulai setelah build-nya sendiri berjalan, yang kalau tidak akan menahan proses build selama beberapa menit; proses `vctip.exe` lainnya dibiarkan)

## Gerbang kualitas (cara hasil diterima)

Gerbang ini tidak memeriksa konsistensi gerak (lompatan skala atau posisi objek): tonton seluruh video sebelum menerimanya.
1. Jumlah frame dan audio ada; tidak ada fallback memori atau baris ALLOC_FAILED di log.
2. Gerbang noise mentah: residu median-filter <= 1,5 (skala 0-255).
3. Noise ternormalisasi tekstur, `scripts/doku_norm.py` (versi repo ini): N = residu median / tekstur Sobel, setiap frame ke-6. **Catatan skala:** pada versi ini 10 klip terukur menghasilkan N = 0,034-0,052 (tabel di `docs/KAPILAR.md`; seperempat terakhir F192/F209V2 mencapai 0,062) dan ambang gerbang tambahan adalah N <= 0,065. Implementasi lain mengukur 0,028-0,036 pada klip yang sama, sehingga ambang TIDAK dapat dipertukarkan antarversi. Pada tekstur yang sangat halus (barisan rumput) N bersih adalah 0,075, jadi ambang berlaku per keluarga adegan. Estimator frekuensi tinggi yang kokoh (sigma-HH <= 1,5; bersih 0,74-1,19, noise tambahan s=2 menghasilkan 2,2-3,0) adalah gerbang tambahan yang direkomendasikan.

Cakupan: VideoTurko membahas SATU kali jalan saja (hingga 209 bingkai, sekitar 8,7 dtk). Uji perangkaian kami sendiri menunjukkan sambungan yang terlihat (adegan tidak berlanjut mulus), jadi film yang lebih panjang tidak termasuk yang kami verifikasi. Untuk merangkai ada panduan komunitas `docs/KLIP_ZINCIRI.md` dan alat bantu kami khusus CPU `scripts/zincir.py` (`plan`, `son-kare`, `bagla`; tidak pernah menjalankan mesin); kualitas film yang dirangkai tidak kami ukur [belum dicoba], jadi periksa setiap sambungan dengan mata dan dengan `scripts/dikis_denetim.py`.
Pengaturan adalah milik Anda: 209 frame adalah bawaan yang kami uji pada kartu 4 GB, bukan batas yang harus Anda pakai. Pilih jumlah frame mana pun pada kisi 17k+5 (56, 73, ... 192, 209; lihat `docs/KURULUM.md`), ubah prompt, seed, resolusi, atau flag apa pun sesuka Anda. Klip yang lebih pendek butuh lebih sedikit memori dan waktu; GPU yang lebih besar mungkin muat lebih banyak.

## Peringatan lisensi model
**VideoTurko hanya berisi patch dan skrip (MIT); siapa pun yang memakai model dan keluarannya bertanggung jawab sendiri atas lisensi MiniMax.** Bukan nasihat hukum. Berikut klausul MiniMax H3 Community License (2 Agustus 2026) diringkas beserta nomornya; lisensi itu sendiri yang mengikat: https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/LICENSE

Lisensi MIT repositori ini tidak mencakup bobot model; lihat [`NOTICE`](NOTICE). Repo ini TIDAK berisi bobot model (tidak ada MiniMax H3, GGUF HyperFlow-H3-Flash, atau file VAE). Proyek ini tidak berafiliasi dengan atau didukung oleh MiniMax. Penggunaan komersial TIDAK dilarang (ini bukan lisensi non-komersial); syaratnya ada di bawah.

**Wilayah (Applicable Territory)**
- **Preamble, I.3, I.5:** Seluruh dunia, KECUALI Uni Eropa, Britania Raya, Republik Korea, dan Amerika Serikat. Memakai model berarti menerima lisensi.
- **II:** Lisensi bebas royalti, tidak dapat dipindahtangankan, terbatas untuk menggunakan, mereproduksi, mendistribusikan, membuat turunan, dan memodifikasi, hanya di dalam wilayah dan sesuai dengan perjanjian serta Exhibit A. Orang di wilayah yang dikecualikan dapat meminta lisensi terpisah dari MiniMax.
- **V.4:** Menggunakan, mereproduksi, memodifikasi, mendistribusikan, atau menampilkan model, turunannya, DAN KELUARANNYA (video/audio hasil generasi) di luar wilayah tidak diizinkan. **Jadi mempublikasikan atau menampilkan video hasil generasi di UE/Inggris/Korea Selatan/AS berada di luar lisensi.**
- **Exhibit A-1:** Penggunaan di luar wilayah melanggar Acceptable Use Policy.

**Distribusi (III)** (repo ini tidak mendistribusikan model; jika Anda yang melakukannya)
- **III.1:** Berikan salinan lisensi kepada setiap penerima. **III.2:** Tandai file yang dimodifikasi dengan pemberitahuan yang mencolok.
- **III.3:** Dianjurkan (tidak wajib): pemberitahuan "Powered by MiniMax H3", penanda hasil generasi AI pada file yang dihasilkan, artikel publik.
- **III.4:** Distribusi HARUS disertai file NOTICE berisi: "MiniMax H3 is licensed under the MiniMax H3 Community License Agreement, Copyright © 2026 MiniMax. All Rights Reserved."
- **Exhibit A-12:** mempublikasikan konten ke lingkungan publik mana pun tanpa mengungkapkan dengan jelas bahwa konten itu dibuat mesin dilarang: beri label pada video hasil generasi AI saat Anda mempublikasikannya (daftar lengkap: `docs/LISANS_UYARISI.md`).
- **III (paragraf terakhir):** Anda boleh menambahkan hak cipta Anda sendiri pada modifikasi Anda, tetapi tidak boleh memberlakukan syarat tambahan atau berbeda atas penggunaan/distribusi; aturan wilayah tetap berlaku.

**Ketentuan komersial (IV)**
- **IV.1:** Jika produk/layanan komersial Anda menghasilkan pendapatan tahunan lebih dari USD 20 juta (atau setara), dapatkan otorisasi tertulis SEBELUMNYA dari api@minimax.io (subjek "MiniMax H3 licensing - authorization request").
- **IV.2:** Antarmuka produk/layanan komersial yang memakai model ini harus menampilkan "MiniMax H3" secara mencolok.

**Pembatasan penggunaan (V)**
- **V.1:** Patuhi hukum yang berlaku (termasuk kepatuhan perdagangan) dan Exhibit A. **V.2:** Ikat setiap orang yang Anda beri akses dengan ketentuan yang setidaknya sama melindunginya dengan pembatasan ini dan beri tahu mereka.
- **V.3:** Anda tidak boleh memakai model atau KELUARANNYA untuk meningkatkan model AI lain (selain MiniMax H3 dan turunannya). (I.11: distilasi dan pelatihan pada keluaran sintetis menjadikan sebuah model "turunan"; keluaran itu sendiri bukan turunan.)
- **V.5:** Jika Anda menawarkan kepada pihak ketiga produk/layanan/layanan hosting yang menghasilkan keluaran dengan model ini: sebelum dan selama operasi, pengamanan teknis dan organisasi yang wajar, mekanisme pelaporan, penyelidikan cepat, dan penghapusan/penonaktifan/penangguhan pelanggar berulang.

**Merek dagang dan hak (VI)**
- **VI.1:** Anda memiliki karya turunan dan turunan model yang Anda buat (tunduk pada hak MiniMax). **VI.2:** Nama/merek MiniMax tidak dilisensikan (di luar yang diperlukan untuk mendeskripsikan dan mendistribusikan); merek "MiniMax H3" hanya boleh dipakai untuk memenuhi III.3, di dalam wilayah; jangan menyiratkan afiliasi.
- **VI.3:** Jika Anda menggugat MiniMax atau siapa pun dengan menyatakan bahwa materi/keluaran melanggar hak Anda, semua lisensi Anda berakhir pada hari itu; Anda membela dan mengganti rugi MiniMax atas klaim pihak ketiga yang timbul dari penggunaan/distribusi oleh Anda atau orang lain.
- **VI.4:** MiniMax tidak mengklaim hak atas keluaran; Anda dan pengguna Anda bertanggung jawab atas keluaran dan penggunaannya.

**Penafian dan pengakhiran (VII, VIII, IX)**
- **VII.1:** Tidak ada kewajiban dukungan/pembaruan. **VII.2:** Model dan keluaran disediakan "AS IS", tanpa jaminan; Anda yang menentukan kesesuaian dan menanggung risikonya. **VII.3:** MiniMax dan afiliasinya tidak bertanggung jawab atas kerugian apa pun (sejauh diizinkan hukum).
- **VIII.1:** Berlaku sejak penerimaan/akses. **VIII.2:** Jika terjadi pelanggaran, MiniMax dapat mengakhiri; Anda wajib berhenti memakai/mendistribusikan, menghapus salinan, dan memberi tahu penerima (VI.1, VI.3, VII, IX tetap berlaku).
- **IX:** Hukum HKSAR Hong Kong; yurisdiksi eksklusif pengadilan Hong Kong (UN CISG dikecualikan).
- **Catatan tambahan:** encoder MiniMax H3 memakai Qwen3-VL-32B (Apache 2.0).

**Acceptable Use Policy (Exhibit A)** (JANGAN memakai model, turunan, atau keluaran untuk)
- A-1 penggunaan di luar wilayah; A-2 melanggar hukum atau HKI pihak ketiga; A-3 membahayakan diri sendiri atau orang lain; A-4 mengalihgunakan/mendistribusikan keluaran untuk merugikan; A-5 menghindari pengamanan; A-6 mengeksploitasi/membahayakan anak di bawah umur; A-7 informasi palsu yang dapat diverifikasi untuk merugikan orang lain atau memengaruhi pemilu; A-8 keterlibatan daring palsu (ulasan palsu dsb.); A-9 pencemaran nama baik, perendahan, pelecehan; A-10 malware; A-11 data pribadi untuk merugikan orang lain; **A-12 mempublikasikan konten ke lingkungan publik mana pun (termasuk unggahan bot) tanpa mengungkapkan secara jelas dan mencolok bahwa konten itu dibuat mesin**; A-13 peniruan identitas tanpa persetujuan; A-14 keputusan otomatis berisiko tinggi di bidang kritis (penegakan hukum, imigrasi, kesehatan, infrastruktur kritis, kredit, ketenagakerjaan, perumahan, pendidikan, penilaian sosial, asuransi, dsb.); A-15 melanggar standar sosial, etika, moral negara/wilayah lain; A-16 ekstremisme kekerasan/terorisme; A-17 diskriminasi/kerugian berdasarkan karakteristik yang dilindungi; A-18 mengeksploitasi kelompok rentan; **A-19 tujuan militer**; A-20 kegiatan profesional tanpa izin/lisensi (keuangan, hukum, medis, dsb.).
- Catatan: ini adalah ringkasan dalam bahasa sederhana; teks lisensi berbahasa Inggris yang berlaku jika ada keraguan.

## Label bukti

Satu set untuk semua dokumen (penulisan lama dalam tanda kurung):
- **[terukur]** (TR: ölçtüm, olctum): dijalankan di proyek ini, jalur bukti ada.
- **[dibaca]** (TR: okudum yol, okudum): sumber atau skrip dibaca, tidak dijalankan.
- **[rancangan]** (TR: tasarım, tasarim): dirancang, belum terlihat dalam run nyata.
- **[perkiraan]** (TR: tahmin): belum diverifikasi.
- **[belum dicoba]** (TR: denenmedi): belum pernah dijalankan.
- **[dilaporkan pengguna]** (TR: kullanıcı bildirdi): dinyatakan oleh pengguna, dengan tanggal; tidak diukur secara independen.
- **[dihitung]** (TR: hesap; penulisan lama: calculated, hesap): angka turunan dari masukan terukur, bukan hasil pengukuran itu sendiri; penurunannya ditulis di sebelahnya. [proposal] / [öneri] pada teks lama = [perkiraan].

Nama run yang dipakai dalam tanda kurung (nama run internal kami, bukan file di repo ini): U209 = 209 frame dengan binary rilis melalui `uret.ps1`; B209 dan B192 = run image-to-video (`-InitImg`) pada 209 dan 192 frame; B56VT2 = binary rilis, 56 frame, dibandingkan dengan referensi byte 56 frame R0; F209b, F209V2, F209V2K = run 209 frame pada build pengembangan (rincian: `docs/OLCUMLER.md`).

## Keterbatasan yang diketahui
- **Bukti byte** (cara mereproduksinya sendiri: `docs/KANITLAR.md`, "R0 ve latent referansi nasil uretilir"; diverifikasi pada kartu sm_61 kami, GPU lain mungkin tidak identik byte [perkiraan]): dengan seri patch kami (flag memori aktif) run 56 frame menghasilkan sha256 `0979f156d548169b...`, identik dengan referensi [terukur]; pada 141 frame sha256 latent `E5D028F8632BE4FE...` identik (dengan flag 0013/0014). Frame 158 sampai 209 tidak memiliki referensi byte langsung; rantai gerbang adalah buktinya. Lulus gerbang numerik tidak menjamin klip yang bagus: konsistensi gerak sepanjang waktu diperiksa dengan mata (lihat `docs/KAPILAR.md`).
- **209 frame, set flag yang mana:** bukti rantai byte 209 frame diambil dengan set flag F209V2 pada build pengembangan (tanpa flag block-tail, dibangun tanpa patch 0019/0020); `uret.ps1` memakai resep ini untuk 209 frame [dibaca: skripnya; run engine nyata melalui `uret.ps1` lulus pada run U209].
- Diverifikasi oleh kami pada satu kartu (GTX 1050 Ti 4 GB); laporan dari luar untuk kartu lain didaftar beserta labelnya di `docs/KART_PROFILLERI.md` [dilaporkan pengguna].
- **Binary mana yang diukur:** latent 141 frame dan rantai byte diukur dengan build pengembangan kami. Binary rilis yang Anda unduh adalah build baru: gerbang byte 56 frame-nya lulus (butir berikutnya) dan run 209 frame melalui `uret.ps1` lulus gerbang (run U209, 3414 dtk, puncak VRAM 3777 MiB) [terukur]; terhadap run 209 frame dengan build pengembangan, latent identik byte demi byte; pada video, frame (md5) dan audio identik, sha256 file AVI berbeda karena kontainer [terukur] (lihat `docs/OLCUMLER.md`, bagian 0).
- **Binary rilis, 56 frame:** binary rilis (sd-cli `c5cebe78...`, stable-diffusion.dll `e5d3d329...`) menghasilkan keluaran 56 frame identik byte dengan R0 (sha256 `0979f156d548169be03acd1a9d7617102a75333aa48a28d6bbfd1cc5fa3f604d`; md5 per frame dan audio identik), dijalankan langsung dengan flag bawaan (tanpa variabel `SD_*`), exit code 0, 601 dtk [terukur: run B56VT2, 2026-11-19; bukti disimpan oleh penulis, tidak ada di repo ini]. Cakupan: hanya kartu sm_61 kami dan 56 frame; bukan uji instalasi clean-root; latent 141 frame dan rantai 209 diukur dengan binary yang lebih lama dan TIDAK diulang dengan binary ini [belum dicoba]. Percobaan pertama (B56VT, lewat skrip pembantu) berakhir tanpa suara setelah 58 dtk, penyebab tidak diketahui [perkiraan: tekanan memori]; percobaan kedua menjalankan `sd-cli` secara langsung.
- Skrip instalasi dan penggunaan belum diverifikasi dari folder kosong (uji clean-root tertunda).
- Peta jalan dan langkah berikutnya: `ROADMAP.md`.

## Status dan batasan
- Diverifikasi pada satu mesin (GTX 1050 Ti 4 GB, RAM 16 GB, i7-7700HQ). Kartu 4 GB lain dan ukuran RAM lain bisa berbeda.
- **Bawaan 209 frame (8,7 dtk):** lulus gerbang kualitas kami (noise 1,08, run F209V2K) [terukur: 209 frame dengan binary rilis melalui `uret.ps1`, run U209; latent identik byte demi byte dengan run dengan build pengembangan; frame dan audio pada video identik, sha file berbeda karena kontainer; bukti disimpan oleh penulis, tidak ada di repo ini]. Pada 209 frame puncak VRAM DiT adalah 3777 MiB dari 4096 MiB (run F209b dan U209; pembacaan `nvidia-smi` seluruh kartu), margin tipis: beban GPU lain (layar, aplikasi lain) bisa membuat proses gagal pada `blocks.0`; diuji hanya pada GTX 1050 Ti. Status layar selama proses itu tidak dicatat; jika layar Anda berjalan di kartu ini, VRAM yang tersedia lebih sedikit [perkiraan: beban layar Windows sekitar 100-300 MB]; bila perlu, sambungkan layar ke GPU terintegrasi [saran, belum diuji]. Sampling memakan 2730 dtk (run U209: langkah 436-483 dtk) dan dekode VAE proses terpisah 173 dtk (tahap 2 total 193 dtk bersama dekode audio) [terukur: U209 binary rilis; run pengembangan lama: 2664 dtk dan 174 dtk]. Pada tahap 1 VAE dalam proses kehabisan memori dan beralih ke temporal tiling (320 dtk); keluaran itu dibuang, video berasal dari tahap 2 tanpa tiling. Puncak RAM tidak diukur pada U209. Klip yang lebih panjang dari 209 frame bukan bagian dari rilis ini.
- **Image-to-video (`-InitImg`):** dengan gambar awal, batasnya 192 frame (8,0 dtk pada 24 fps) di GPU ini: 209 frame tidak muat (kurang sekitar 17,5 MB VRAM pada blok 0: butuh 2587 MB, tersedia 2570 MB); 192 frame berjalan melalui `uret.ps1` dalam 3086 dtk dengan puncak VRAM 3783 MiB dan gerbang lulus [terukur: run B209 dan B192, 2026-11-20, satu adegan; bukti disimpan oleh penulis, tidak ada di repo ini]. Belum dicoba pada GPU lain [belum dicoba].
- **RAM kosong itu penting:** Anda butuh sekitar 11 GB RAM KOSONG (proses engine memegang sekitar 11 GB) [terukur]. Dengan RAM kosong yang terlalu sedikit, proses bisa mati tanpa pesan galat [perkiraan: kami mengamatinya satu kali dengan sekitar 300 MB RAM kosong saat `sd-cli` memegang sekitar 10 GB]. Jangan membuka program besar lain saat proses berjalan: pada mesin 16 GB hanya sekitar 0,3-0,5 GB yang tersisa, dan di bawah tekanan memori proses bisa mati tanpa suara. Sebelum mulai, tutup browser, game, dan program besar lain, lalu periksa RAM yang kosong.
- **Uji clean-root tertunda:** skrip instalasi dan penggunaan belum diverifikasi dari folder kosong hanya dengan petunjuk ini; bagian ini akan diperbarui saat uji itu (termasuk perbandingan byte 56 frame dengan referensi) dicatat.
- Tidak ada video hasil generasi yang disertakan di sini.

<!-- i18n-source: README.md sha256:7d01bea18712 -->
