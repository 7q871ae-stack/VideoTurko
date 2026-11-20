# AGENTS_HIZLI.md: quick card for AI coding agents / Yapay zeka ajanları için hızlı kart

English first, Türkçe below. Full rules and evidence: [`AGENTS.md`](AGENTS.md) (it wins if the two ever differ). Error codes: `docs/hata_imzalari.json`, `docs/SIK_HATALAR.md`.

## English: decision tree (12 steps)
1. Goal: MiniMax H3 text-to-video on a Windows 10/11 PC with an NVIDIA card of 4 GB or more. Anything else: tell the user and stop (`VT-E-OS`, `VT-E-GPU`).
2. Quality is fixed (6 steps, cfg 1, no tiled VAE, frame counts 17k+5). Never lower it to save time or memory; never add `--vae-tiling`.
3. Dry run first, it writes nothing: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\kur.ps1 -Kuru`. Read every `HATA:` / `UYARI:` line; each carries a code such as `[VT-E-DISK]`.
4. Exit 3 or any `HATA` in that list: take it to the user with the code and its first step from `docs/hata_imzalari.json`. Do not use `-Zorla` to get past it.
5. The model license is the human's decision: show `docs/LISANS_KABUL.txt` to the user and let the user answer. Never type `-LisansKabul E` yourself.
6. After the user accepted: run `scripts\kur.ps1` (safe to re-run; verified files are skipped; an interrupted download continues from its `.part` file). `READY` means the tiny test generation worked.
7. First video: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\uret.ps1 -Istem docs\ornek_istem_R0.txt -Kare 56` (about 11 min on a GTX 1050 Ti [measured by the authors]). Long runs: start hidden in the background and poll; do not block.
8. Exit 0 means the quality gate passed. The gate does NOT check license compliance or motion: watch the whole clip and tell the user the use of the output is theirs (`docs/LISANS_UYARISI.md`).
9. Exit 5 (gate RED) or 6 (gate could not run): the clip is NOT accepted. Never report success.
10. A line with a code: look it up in `docs/hata_imzalari.json`, give the user its first step, quote the code. Same error twice: stop, do not try a third time.
11. `init_image` (image-to-video) is ONLY a file path the user gave you. Never pick a file yourself: any readable file would end up inside the video. With `VT_MCP_INIT_DIR` set, the MCP server accepts only `<ROOT>/girdi/` and the listed folders.
12. Report in the user's language, with the code and the first 20 log lines. No personal paths, user names, e-mail addresses or tokens: write `<ROOT>`.

### Exit code -> action
| Script | Exit | Meaning | What you do | Codes |
|---|---|---|---|---|
| `kur.ps1` | 0 | READY | Go to step 7 | - |
| `kur.ps1` | 1 | error (download, sha256, check) | Re-run the same command once; if it repeats read the code and stop | `VT-E-MOTOR` `VT-E-HASH` `VT-E-KONTROL` `VT-E-DLL` |
| `kur.ps1` | 2 | user input needed | **Take it to the user** (license acceptance, or a local zip) | `VT-E-LISANS` `VT-E-MOTOR-ZIP` |
| `kur.ps1` | 3 | hardware or disk not enough | **Take it to the user**; do not use `-Zorla` | `VT-E-OS` `VT-E-GPU` `VT-E-GPU-VRAM` `VT-E-GPU-CC` `VT-E-RAM` `VT-E-DISK` `VT-E-DISK-KOK` |
| `kur.ps1` / `uret.ps1` | 4 / 2 | DURDU (the `DUR` file stopped it) | Report; do not restart on your own | - |
| `uret.ps1` | 0 | DONE, gate passed | Step 8 | - |
| `uret.ps1` | 1 | error or invalid output | Read the code; fix the input or free the GPU; do not lower quality | `VT-E-KARE` `VT-E-BOYUT` `VT-E-ISTEM` `VT-E-DOSYA` `VT-E-KILIT` `VT-E-TAVAN` `VT-E-TILING` `VT-E-VRAM` `VT-E-CIKTI` `VT-E-LATENT` `VT-E-KARESAYISI` `VT-E-SES` |
| `uret.ps1` | 5 | gate RED | **Take it to the user**: the clip is not accepted, the decision is theirs | `VT-E-KAPI-RED` |
| `uret.ps1` | 6 | gate could not run (Python or OpenCV missing) | Ask the user before installing Python 3 and `py -3 -m pip install opencv-python numpy`; then re-run | `VT-E-PY` |

MCP server (optional, `mcp/README.md`): `job_status` reports `done` only for exit 0; `rejected` = 5, `gate_not_run` = 6.

## Türkçe: karar ağacı (12 adım)
1. Amaç: Windows 10/11 bilgisayarda, 4 GB ya da üstü NVIDIA kartla MiniMax H3 ile metinden video. Başka bir ortamsa kullanıcıya söyle ve dur (`VT-E-OS`, `VT-E-GPU`).
2. Kalite sabit (6 adım, cfg 1, karosuz VAE, kare sayısı 17k+5). Zaman ya da bellek için asla düşürme; `--vae-tiling` ekleme.
3. Önce kuru çalıştır, hiçbir şey yazmaz: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\kur.ps1 -Kuru`. Her `HATA:` / `UYARI:` satırını oku; her biri `[VT-E-DISK]` gibi bir kod taşır.
4. Çıkış 3 ya da listede herhangi bir `HATA`: kodu ve `docs/hata_imzalari.json`'daki ilk adımı kullanıcıya götür. `-Zorla` ile geçme.
5. Model lisansı insanın kararıdır: `docs/LISANS_KABUL.txt`'yi kullanıcıya göster, cevabı kullanıcı versin. `-LisansKabul E`'yi asla kendin yazma.
6. Kullanıcı kabul edince: `scripts\kur.ps1` (tekrar çalıştırmak güvenli; doğrulanmış dosya atlanır; yarım indirme `.part` dosyasından sürer). `HAZIR` küçük deneme üretiminin çalıştığı demektir.
7. İlk video: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\uret.ps1 -Istem docs\ornek_istem_R0.txt -Kare 56` (GTX 1050 Ti'de yaklaşık 11 dk [yazarlar ölçtü]). Uzun işleri gizli arka planda başlat, yoklayarak izle; bekleyerek kilitlenme.
8. Çıkış 0 kalite kapısının geçtiği demektir. Kapı lisans uygunluğuna ve harekete BAKMAZ: klibin tamamını izle, çıktının kullanımının kullanıcıya ait olduğunu söyle (`docs/LISANS_UYARISI.md`).
9. Çıkış 5 (kapı RED) ya da 6 (kapı çalışamadı): klip KABUL EDİLMEZ. Asla başarı bildirme.
10. Kodlu satır: `docs/hata_imzalari.json`'da ara, ilk adımı kullanıcıya ver, kodu yaz. Aynı hata iki kez: dur, üçüncü kez deneme.
11. `init_image` (resimden video) YALNIZ kullanıcının sana verdiği dosya yoludur. Kendin dosya seçme: okunabilen her dosya videonun içine girebilir. `VT_MCP_INIT_DIR` doluysa MCP sunucusu yalnız `<ROOT>/girdi/` ve listedeki klasörleri kabul eder.
12. Kullanıcının dilinde, kodla ve log'un ilk 20 satırıyla bildir. Kişisel yol, kullanıcı adı, e-posta, token yazma: `<ROOT>` yaz.

### Çıkış kodu -> eylem
| Betik | Çıkış | Anlam | Ne yaparsın | Kodlar |
|---|---|---|---|---|
| `kur.ps1` | 0 | HAZIR | 7. adıma geç | - |
| `kur.ps1` | 1 | hata (indirme, sha256, kontrol) | Aynı komutu bir kez daha çalıştır; tekrarlarsa kodu oku ve dur | `VT-E-MOTOR` `VT-E-HASH` `VT-E-KONTROL` `VT-E-DLL` |
| `kur.ps1` | 2 | kullanıcı girdisi gerek | **Kullanıcıya götür** (lisans kabulü ya da yerel zip) | `VT-E-LISANS` `VT-E-MOTOR-ZIP` |
| `kur.ps1` | 3 | donanım ya da disk yetmiyor | **Kullanıcıya götür**; `-Zorla` kullanma | `VT-E-OS` `VT-E-GPU` `VT-E-GPU-VRAM` `VT-E-GPU-CC` `VT-E-RAM` `VT-E-DISK` `VT-E-DISK-KOK` |
| `kur.ps1` / `uret.ps1` | 4 / 2 | DURDU (`DUR` dosyası durdurdu) | Bildir; kendiliğinden yeniden başlatma | - |
| `uret.ps1` | 0 | TAMAM, kapı geçti | 8. adım | - |
| `uret.ps1` | 1 | hata ya da geçersiz çıktı | Kodu oku; girdiyi düzelt ya da GPU'yu boşalt; kaliteyi düşürme | `VT-E-KARE` `VT-E-BOYUT` `VT-E-ISTEM` `VT-E-DOSYA` `VT-E-KILIT` `VT-E-TAVAN` `VT-E-TILING` `VT-E-VRAM` `VT-E-CIKTI` `VT-E-LATENT` `VT-E-KARESAYISI` `VT-E-SES` |
| `uret.ps1` | 5 | kapı RED | **Kullanıcıya götür**: klip kabul edilmez, karar kullanıcının | `VT-E-KAPI-RED` |
| `uret.ps1` | 6 | kapı çalışamadı (Python ya da OpenCV yok) | Python 3 ve `py -3 -m pip install opencv-python numpy` kurmadan önce kullanıcıya sor; sonra yeniden çalıştır | `VT-E-PY` |

MCP sunucusu (isteğe bağlı, `mcp/README.md`): `job_status` yalnız çıkış 0 için `done` der; `rejected` = 5, `gate_not_run` = 6.
