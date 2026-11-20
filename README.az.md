# VideoTurko

[English](README.md) · [Türkçe](README.tr.md) · [简体中文](README.zh-CN.md) · [日本語](README.ja.md) · [Español](README.es.md) · [Русский](README.ru.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [العربية](README.ar.md) · [Português (BR)](README.pt-BR.md) · [Italiano](README.it.md) · [한국어](README.ko.md) · [हिन्दी](README.hi.md) · [Bahasa Indonesia](README.id.md) · [Tiếng Việt](README.vi.md) · [Polski](README.pl.md) · [Nederlands](README.nl.md) · [Українська](README.uk.md) · [فارسی](README.fa.md) · [עברית](README.he.md) · [ไทย](README.th.md) · [বাংলা](README.bn.md) · [اردو](README.ur.md) · [Ελληνικά](README.el.md) · [Čeština](README.cs.md) · [Română](README.ro.md) · [Magyar](README.hu.md) · [Svenska](README.sv.md) · Azərbaycanca · [Bahasa Melayu](README.ms.md)

Tərcümələr bu ingilis dilindəki README-ni izləyir. Tərcümə fərqlənərsə və ya geridə qalarsa, xüsusilə lisenziya və təhlükəsizlik mətnində ingilis mətni əsasdır ([`SECURITY.md`](SECURITY.md) və [`docs/LISANS_UYARISI.md`](docs/LISANS_UYARISI.md) yalnız ingilis və türk dillərində saxlanılır).

![Windows](https://img.shields.io/badge/Windows-10%2F11-blue) ![GPU](https://img.shields.io/badge/NVIDIA-4%20GB%20(sm__61)-76b900) ![License](https://img.shields.io/badge/code-MIT-green) ![Status](https://img.shields.io/badge/status-clean--root%20test%20pending-orange)

> **Başlamazdan əvvəl (lisenziya, ərazi):** bu repozitoriya MIT-dir və yalnız yamaqlar və skriptlər ehtiva edir. Yüklədiyi MiniMax H3 modeli MiniMax H3 Community License altındadır: onun ərazisinə Avropa İttifaqı, Birləşmiş Krallıq, Cənubi Koreya və Amerika Birləşmiş Ştatları daxil deyil və model, törəmələr **və çıxışlar (yaratdığınız videolar)** orada istifadə edilə, yayıla və ya göstərilə bilməz (V.4). Kommersiya istifadəsinə lisenziya şərtləri daxilində icazə verilir. Quraşdırmadan əvvəl [`docs/LISANS_UYARISI.md`](docs/LISANS_UYARISI.md) oxuyun; bu hüquqi məsləhət deyil.

> **30 saniyədə:** 4 GB-lıq video kart MiniMax H3 ilə 209 kadrlıq (8,7 san) videonu tək keçidlə hazırlaya bilir: bir kompüterdə yoxlanılıb (GTX 1050 Ti 4 GB; boş qovluqda `kur.ps1` ilə tam quraşdırma hələ başdan sona yoxlanılmayıb) [ölçülüb: `uret.ps1` vasitəsilə buraxılış (release) binarı ilə 209 kadr, U209 işə salınması; latent inkişaf (development) build işə salınması ilə bayt-bayt eynidir; videoda kadrlar və səs eynidir, fayl sha-sı konteynerə görə fərqlənir; sübutu müəlliflər saxlayır, bu repoda yoxdur]; `-InitImg` ilə (şəkildən video) ən çox 192 kadr (8,0 san) [ölçülüb: B192 işə salınması]; 209 kadr təxminən 57 dəq çəkir, standart vaxt həddi 80 dəq [ölçülüb: U209 işə salınması]; aşağıdakı 3 addım onu necə işə salmaq lazım olduğunu göstərir.

VideoTurko: 4 GB-lıq GTX 1050 Ti üzərində MiniMax H3 mətndən-videoya modelini tək keçidlə 209 kadra (8,7 san) qədər işlətmək üçün stable-diffusion.cpp yaddaş yamaqları və resept toplusu; şəkildən video (`-InitImg`) 192 kadra (8,0 san) qədər (209 kadr bayt zənciri ilə yoxlanılıb; 56 və 141 kadrlıq yoxlamalarda yamaqsız işə salınma ilə bayt-bayt eynidir).

## Sürətli başlanğıc (Windows, 3 addım)
**Vəziyyət: aşağıdakı quraşdırma və işə salma skriptləri tamamlanır, təmiz-kök (clean-root) testi gözlənilir; bu test keçməyincə burada heç nəyin işlədiyi iddia edilmir ("Vəziyyət və məhdudiyyətlər" bölməsinə baxın).**

1. Bu repozitoriyanı **yükləyin** (yaşıl **Code** düyməsi, sonra **Download ZIP**) və QISA bir qovluğa, məsələn `C:\vt` qovluğuna çıxarın.
2. **Quraşdırma: `kur.cmd` üzərinə iki dəfə klikləyin** (qara pəncərə açılır və hər addımı göstərir; onu bağlamaq quraşdırmanı dayandırır, yenidən işə salmaq qaldığı yerdən davam edir: yarıya qədər yüklənmiş model faylı davam etdirilir [oxunub: yükləmə skripti `.part` faylını saxlayır və ondan davam edir; tam 29 GiB davam ölçülməyib]). Windows yüklənmiş fayl barədə xəbərdarlıq etsə, əvəzinə aşağıdakı PowerShell əmrindən istifadə edin [məsləhət, yüklənmiş ZIP üzərində sınanmayıb]. Əmr sətrini üstün tutursunuz? Həmin qovluqda PowerShell açın (Explorer ünvan çubuğuna `powershell` yazın) və eyni quraşdırmanı işə salın:
   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File scripts\kur.ps1
   ```
   Quraşdırma kökü çıxardığınız qovluqdur (mühərrik `engine\bin` qovluğuna, modellər `model` qovluğuna düşür); başqa yer üçün əvvəlcə `VT_ROOT` mühit dəyişənini təyin edin. Skript GPU-nu, sürücünü, RAM-i və diski yoxlayır, mühərriki və modelləri yükləyir (mühərrik zip-ləri və təzə yüklənən model faylları sha256 ilə yoxlanılır; ölçüsü düzgün olan hazır model faylı yalnız ölçüyə görə yoxlanılır, tam sha256 yoxlaması üçün `scripts\modelleri_indir.ps1 -Dogrula` işə salınır), qısa real yoxlama aparır və yalnız bu yoxlama keçərsə READY çıxarır [dizayn: `kur.ps1` təmiz qovluqda tam işə salınmayıb; bu cümlə təmiz-qovluq testindən sonra yenilənəcək]. `-ExecutionPolicy Bypass` yalnız bu bir prosesə aiddir; hər quraşdırıcıda olduğu kimi, əvvəlcə `scripts\kur.ps1` faylını oxuyun.
   Mühərrik zip-i GitHub-dakı v0.1.0 buraxılışından yüklənir (19 noyabr 2026-da dərc olunub; sha256-sı `kur.ps1` faylında sabitlənib). İnternetsiz işləyirsinizsə və ya öz build-inizdən istifadə edirsinizsə, yerli zip-ləri verin: `-MotorZip <path> -CudaZip <path>`. Yerli zip də eyni sabit sha256 ilə yoxlanılır (yanındakı `.sha256` faylı nəzərə alınmır), ona görə də o, buraxılış zip-i olmalıdır; öz build-iniz üçün əvvəlcə `VT_MOTOR_SHA256` / `VT_CUDA_SHA256` dəyişənini onun sha256-sına təyin edin. Yanlış sha256 exit 1 ilə dayandırır. `engine\bin` qovluğuna yalnız `.exe`/`.dll` faylları düşür; lisenziyalar və README `engine\lisanslar\<zip name>\` qovluğuna qoyulur. [sınanıb buraxılışdan əvvəl dist zip-ləri ilə: yanındakı `.sha256` faylı və özünə istinadlı xəbərdarlıq, binar və DLL-lər yerinə qoyuldu, `sd-cli --help` işlədi; quraşdırılan binarların sha-ları üst-üstə düşdü (`c5cebe78...`, `e5d3d329...`); `kur.ps1`-in model addımı və 5 kadrlıq yoxlaması hələ real GPU-da İŞƏ SALINMAYIB]
   **Model lisenziyası:** model addımından əvvəl quraşdırıcı lisenziya xülasəsini çap edir (`docs/LISANS_KABUL.txt`, tam mətn `docs/LISANS_UYARISI.md`: MiniMax H3 Community License, yaradılan videoları da əhatə edən ərazi məhdudiyyətləri, kommersiya və AI-etiket qaydaları) və qəbul etməyinizi istəyir (`E` = bəli). Əvvəlcə oxuyun. Nəzarətsiz işə salmalar üçün `-LisansKabul E` verə bilərsiniz; bu, lisenziyanı özünüzün oxuyub qəbul etdiyiniz mənasına gəlir; başqası üçün əlavə etməyin. (AI agentləri: `AGENTS.md` faylına əməl edin; istifadəçinin razılığı olmadan heç vaxt E yazmayın.) Qəbul olunmasa `kur.ps1` exit kodu 2 ilə dayanır və heç bir model yükləmir.
3. **İlk videonuz (56 kadr, bizim GTX 1050 Ti-də təxminən 11 dəq** [ölçülüb: 641 san, işə salma R0, `docs/OLCUMLER.md`; digər kartlar ölçülməyib]**)**: quraşdırıcı `HAZIR / READY` yazdıqda işə salın
   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File scripts\uret.ps1 -Istem docs\ornek_istem_R0.txt -Kare 56
   ```
   (qısayol: prompt mətn faylını `uret.cmd` üzərinə sürükləyin və ya `uret.cmd docs\ornek_istem_R0.txt` işə salın: eyni 56 kadrlıq işə salma). Video `runs\` qovluğundadır. Sonra öz promptunuzu mətn faylına yazın (ingiliscə bir abzas, istəyə görə `audio:` cümləsi) və əhatə etdiyimiz ən uzun klipi işə salın (susmaya görə, təxminən 57 dəq [ölçülüb: işə salma U209]):
   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File scripts\uret.ps1 -Istem istem.txt -Kare 209
   ```
   `-Kare` 17k+5 şəbəkəsinə uyğundur (56, 73, ... 192, 209); standart 209 (8,7 san), əhatə etdiyimiz ən uzun müddətdir. VAE ayrı prosesdə işləyir, heç vaxt plitələrə (tiling) bölünmür [`uret.ps1` vasitəsilə buraxılış binarı ilə real mühərrik işə salınması, ayrı proses VAE ilə, U209 işə salınmasında keçdi].

   İstəm yazma bələdçisi: [`docs/ISTEM_YAZIMI.md`](docs/ISTEM_YAZIMI.md) (fasiləsiz tək plan nümunəsi, bərabər zaman dilimləri, iki tam nümunə).

| Tələb | Dəyər |
|---|---|
| ƏS | Windows 10/11, 64-bit |
| GPU | NVIDIA, 4 GB və ya daha çox; yalnız GTX 1050 Ti (sm_61) üzərində sınanıb; ehtiyat payı azdır (209 kadrda 3777/4096 MiB): məşğul ekran və ya brauzer işə salınmanı poza bilər; başqa 4 GB-lıq kart sınanmayıb |
| RAM | 16 GB (zirvə təxminən 11 GB; digər proqramları bağlayın) |
| Disk | ən azı 32 GiB boş (40 GiB və daha çox tövsiyə olunur: 32 ilə 40 arasında quraşdırıcı xəbərdarlıq yazır, `[VT-W-DISK-PAY]` [ölçülüb: simulyasiya edilmiş diskli `-Kuru` işə salmaları]), modellər SSD-də (NVMe daha yaxşıdır) |
| Yükləmə | mühərrik zip-i 36,8 MB + CUDA runtime zip-i 567,5 MB [ölçülüb] + modellər 31,473,112,040 bayt (təxminən 29,3 GiB) [oxunub: ölçülər `scripts/modeller.json` faylında]; cəmi təxminən 30 GiB |
| Modellər | daxil deyil; quraşdırıcı onları MiniMax lisenziyası çərçivəsində yükləyir (aşağıdakı xəbərdarlığa baxın). Modellər (29,3 GiB, `scripts/modeller.json` faylında 31,473,112,040 bayt) bu repozitoriyada və ya buraxılışda yoxdur: GitHub fayl/buraxılış ölçü məhdudiyyətləri tətbiq olunur, `kur.ps1` onları rəsmi mənbədən sha256 yoxlaması ilə yükləyir. |

`kur.ps1` exit kodları: 0 READY, 1 xəta, 2 istifadəçi girişi lazımdır (lisenziya və ya hələ buraxılış/zip yoxdur), 3 avadanlıq və ya disk kifayət deyil, 4 dayandırılıb (DUR faylı). `uret.ps1` nəticəni yalnız `.avi` faylı varsa, kadr sayı düzgündürsə və loglar təmizdirsə qəbul edir [ölçülüb: `uret.ps1` vasitəsilə buraxılış binarında bir real işə salınma, U209 işə salınması, 209 kadr, keçid (gate) keçdi]. `uret.ps1` exit kodları: 0 DONE (keyfiyyət keçidi keçdi), 1 xəta və ya yararsız çıxış (səs axını olmayan video daxil), 2 dayandırılıb (DUR faylı), 5 `KAPI RED` (keyfiyyət keçidi keçilmədi: klip qəbul edilmir, qərar sizindir), 6 keçid işləyə bilmədi (klip qəbul edilmir). Təfərrüatlar AGENTS.md faylındadır. [ölçülüb: saxta mühərrik və saxta keçid ssenarilərində 0, 1 (səssiz video), 5 və 6 exit kodları; real mühərrik: U209 işə salınmasında exit 0]

### Problemlərin həlli (təfərrüatlar: `docs/SIK_HATALAR.md`)
Skriptlərimizin xəta sətirləri sabit kod daşıyır, məsələn `HATA: [VT-E-DLL] ...` və ya `UYARI: [VT-W-DISK-PAY] ...`. Kodu [`docs/SIK_HATALAR.md`](docs/SIK_HATALAR.md) (lövbər nümunəsi `#vt-e-dll`) və ya `docs/hata_imzalari.json` içində axtarın və kodu issue-nuza yazın. Aşağıdakı cədvəlin birinci sütunu çap olunduğu kimi qalır (kodları və jurnal mətnini tərcümə etməyin).

| Gördüyünüz | Nə deməkdir, nə etməli |
|---|---|
| `STATUS_DLL_NOT_FOUND` / `cudart64_12.dll not found` (#13) | `sd-cli.exe` faylını əllə işə salmayın; CUDA DLL-lərini yerinə qoyan `scripts\kur.ps1` skriptini işə salın. |
| `blocks.0` mərhələsində `failed during weight preparation` (#1, #3, #5) | Yaddaş keçidində VRAM çatmır: 17k+5 şəbəkəsindən daha kiçik kadr sayı seçin, digər GPU proqramlarını bağlayın, göndərilən bayraqları saxlayın. |
| `retrying with temporal tiling` (#6) | VAE plitələrə bölməyə keçib; keyfiyyət baxımından çıxış yararsızdır. Yenidən işə salın. |
| İş vaxt həddində bitir, video yoxdur (#7) | Uzun kliplər üçün `-TavanDk` dəyərini artırın (standart vaxt həddi: 209 kadr üçün 80 dəq, `uret.ps1` tərəfindən təyin olunur; bizim 209 kadrlıq işə salınmamız 57 dəq çəkdi [ölçülüb: U209 işə salınması]). |
| Exit kodu boşdur, amma "finished" yazılıb (#14) | Sarğı (wrapper) exit kodunu çox tez oxuyub; yenidən işə salın və video faylının mövcudluğunu yoxlayın. |
| Sistem yavaşlayır, swap işləyir (#18) | Mühərrik təxminən 10-11 GB RAM istifadə edir; brauzerləri və digər proqramları bağlayın. |
| sha256 uyğunsuzluğu / yükləmə uğursuz oldu | Adətən yükləmə yarımçıq qalıb: eyni əmri yenidən işə salın, yoxlanılmış fayllar keçilir. |

**İlişib qaldınız, yoxsa maraqlanırsınız?** [`SUPPORT.md`](SUPPORT.md) (hara sual vermək; cavab müddətləri hədəfdir, öhdəlik deyil) · [`PRIVACY.md`](PRIVACY.md) (telemetriya yoxdur; şəbəkə yalnız mühərriki və modelləri göstərilən hostlardan yükləmək üçün istifadə olunur) · [`SECURITY.md`](SECURITY.md) (məxfi bildiriş) · [`CONTRIBUTING.md`](CONTRIBUTING.md) (5 addımda ilk pull request; sənədlər və skriptlər üçün GPU lazım deyil).

### v0.1.1-də yeni: əlavə seçimlər (təfərrüatlar: `AGENTS.md`, `docs/SIK_HATALAR.md` 19-23)
Bu seçimlərdən istifadə etməsəniz, 4 GB-lıq kartda heç nə dəyişmir (istinadımızla müqayisədə 56 kadrlıq bayt yoxlaması v0.1.1 ilə yenidən keçdi [ölçülüb]). Nəyin işə düşəcəyini görmək üçün istənilən əmrə `-Kuru` əlavə edin.
- `-EndImg`: son kadrı da verin (ilk və son kadr, "FLF"); 8 GB-dan az yaddaşlı kartlarda hədd 175 kadrdır (192 kadr 4 GB-da yerləşmədi), 8 GB və daha böyük kartlarda 192. Bizim GTX 1050 Ti kartımızda həmişə iki prosesdə işləyir: 56 kadr 1040 san, 175 kadr 2887 san (48 dəq), hər ikisi keçiddən keçdi [ölçülüb]. İstəm məsləhətləri: `docs/ISTEM_YAZIMI.md`.
- `-W` / `-H`: başqa ölçülər, məsələn, şaquli 384x640; 32-nin misli olmalı, sahəsi ən azı 640x384 (heç vaxt daha kiçik deyil). 4 GB-da sınanmayıb; 8 GB-dan az yaddaşlı kartlarda ölçdüyümüz ən böyük işi aşan ölçülər rədd edilir. Keyfiyyət keçidinin hədləri 640x384 üçün kalibrlənib.
- `-TekAsama`: iki proses əvəzinə bir proses, yalnız böyük kartlar üçün; heç vaxt avtomatik açılmır.
- Daha yeni GPU-lar (compute capability 7,0+, məs. RTX 20/30/40): özünüz təyin etməmisinizsə, `GGML_CUDA_CUBLAS_COMPUTE_TYPE=f32` avtomatik təyin olunur; bu, bildirişi göndərənin RTX 4070 Ti kartında 141 və daha çox kadrda tamamilə qara video problemini aradan qaldırdı [istifadəçi bildirib, issue #1]. Python + OpenCV yoxdursa, `uret.ps1` indi GPU işindən əvvəl exit 6 ilə dayanır (video yaradılmır, çaşdırıcı RED də yoxdur).
- Bu dəyişikliklərə səbəb olan RTX 4070 Ti hesabatı üçün @SinanC73-ə təşəkkür edirik ([issue #1](https://github.com/alexturkey/VideoTurko/issues/1)).

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

## Bu nədir
MiniMax H3-ün (33B DiT; biz HyperFlow Flash 13,7B Q4_K_M GGUF işlədirik; 32B Qwen3-VL mətn kodlayıcısı ayrıdır) 4 GB-lıq Pascal GPU-da (GTX 1050 Ti, 16 GB sistem RAM-i) işləməsinə imkan verən stable-diffusion.cpp üçün kiçik yaddaş/planlaşdırma yamaqları toplusu, həmçinin işə salma resepti, yoxlamalar və ölçmələr.
- Faktiki olaraq yaratdığımız və keyfiyyət keçidlərimizdən keçən tək-keçid uzunluqları: 640x384, 24 fps ilə 56, 141, 158, 175, 192, 209 kadr (209 kadr = 8,7 san), H3-ün özünün yaratdığı səslə [ölçülüb: `uret.ps1` vasitəsilə buraxılış binarı ilə 209 kadr, U209 işə salınması; latent inkişaf build işə salınması ilə bayt-bayt eynidir; videoda kadrlar və səs eynidir, fayl sha-sı konteynerə görə fərqlənir; sübutu müəlliflər saxlayır, bu repoda yoxdur]. 209 bizim izlədiyimiz və axıcı tapdığımız ən uzun müddətdir [istifadəçi bildirib, 2026-11-19, video tam izlənilib; fayl: F209V2 çıxışı, 8,708 san].
- **Bayt-bayt eyniliyə dair iddia, dürüst çərçivədə:** çıxışlar yamaqsız istinadla bayt-bayt eynilik baxımından yalnız 56 və 141 kadr üçün yoxlanılıb. 158/175/192/209 kadr üçün eyni bayraqlardan və eyni binar zəncirindən istifadə etdik; birbaşa bayt istinadı yoxdur (yamaqsız build bu GPU-da həmin uzunluqları işlədə bilmir).
- Keyfiyyət ayarları heç vaxt endirilmir: eyni model/kvantlaşdırma, 6 addım, cfg 1, 640x384, eyni seed, plitəsiz (non-tiled) VAE.
- İlk olduğumuzu iddia etmirik: axtardıq və 4 GB-da bunun kənar nümunəsini tapmadıq; bu, belə nümunənin olmadığının sübutu deyil.

## Qovluq quruluşu
- `patches/` müəyyən edilmiş (pinned) stable-diffusion.cpp commit-inə qarşı yamaqlar (orada qeydlərə baxın)
- `scripts/` build, işə salma, ayrı proses VAE, keçid/ardıcıllıq köməkçiləri (`doku_norm.py`: aşağıdakı miqyas qeydinə baxın)
- `docs/KURULUM.md` avadanlıq, build və işə salma addımları (EN+TR)
- `docs/YAMALAR.md` yamaq siyahısı, `docs/KANITLAR.md` sübutlar, `docs/KAPILAR.md` keyfiyyət keçidləri cədvəli, `docs/OLCUMLER.md` ölçmələr, `docs/SIK_HATALAR.md` tez-tez rast gəlinən səhvlər, `docs/LISANS_UYARISI.md` lisenziya bəndlərinin tam siyahısı
- `scripts/` qısa indeks: `hiz_kos3.ps1` işə salma sarğısı (`-Kuru` dəqiq əmri çap edir), `uretim_kapi.ps1` keyfiyyət keçidi, `dikis_denetim.py` tikiş yoxlaması, `doku_norm.py` teksturaya görə normallaşdırılmış küy, `bayt_kiyas.py` bayt müqayisəsi, `derleme_sablonu.ps1` build şablonu (yalnız öz build-i başladıqdan sonra işə düşən Visual Studio telemetriya köməkçisi `vctip.exe` prosesini dayandırır, əks halda o, build prosesini dəqiqələrlə bağlı saxlayır; digər `vctip.exe` prosesləri toxunulmaz qalır)

## Keyfiyyət keçidləri (nəticə necə qəbul edilir)

Bu keçid hərəkət ardıcıllığını (obyektin ölçüsündə və ya mövqeyindəki sıçrayışları) yoxlamır: qəbul etməzdən əvvəl bütün videoya özünüz baxın.
1. Kadr sayı və səsin olması; logda yaddaş fallback-i və ya ALLOC_FAILED sətirləri olmamalıdır.
2. Xam küy keçidi: median süzgəc qalığı <= 1,5 (0-255 şkalası).
3. Teksturaya görə normallaşdırılmış küy, `scripts/doku_norm.py` (bu repozitoriyanın versiyası): N = median qalıq / Sobel teksturası, hər 6-cı kadr. **Şkala qeydi:** bu versiyada ölçülmüş 10 klip N = 0,034-0,052 verir (cədvəl `docs/KAPILAR.md` faylındadır; F192/F209V2-nin son rübü 0,062-yə çatır) və əlavə keçid həddi N <= 0,065-dir. Başqa bir implementasiya eyni kliplərdə 0,028-0,036 ölçdü, ona görə hədlər versiyalar arasında dəyişdirilə BİLMƏZ. Çox incə teksturalarda (ot cərgələri) təmiz N 0,075 idi, yəni hədd səhnə ailəsinə görə təyin olunur. Möhkəm yüksək tezlikli qiymətləndirici (sigma-HH <= 1,5; təmiz 0,74-1,19, s=2 əlavə küy 2,2-3,0 verir) tövsiyə olunan əlavə keçiddir.

Əhatə dairəsi: VideoTurko TƏK bir keçid haqqındadır (209 kadra qədər, təxminən 8,7 san). Bir neçə hissəni daha uzun klipdə zəncirləmək sınanıb; tikişlər görünürdü (səhnə təmiz davam etmir), ona görə bu layihənin tərkibində deyil. Daha uzun kliplər istəyirsinizsə, öz yanaşmanızı qurun.
Ayarlar sizindir: 209 kadr 4 GB-lıq kartda sınanmış standartımızdır, məcburi olduğunuz hədd deyil. 17k+5 şəbəkəsindən istənilən kadr sayını seçin (56, 73, ... 192, 209; bax: `docs/KURULUM.md`), istəyi (prompt), seed-i, ayırdetməni və ya istənilən bayrağı öz istəyinizə görə dəyişin. Daha qısa kliplər daha az yaddaş və vaxt tələb edir; daha böyük GPU-lar daha çoxunu götürə bilər.

## Model lisenziyası xəbərdarlığı
**VideoTurko yalnız yamaqlardan və skriptlərdən ibarətdir (MIT); modeldən və onun çıxışlarından istifadə edən hər kəs MiniMax lisenziyasına görə özü məsuliyyət daşıyır.** Hüquqi məsləhət deyil. Aşağıda MiniMax H3 Community License (2 avqust 2026) bəndləri nömrələri ilə xülasə olunub; məcburi olan lisenziyanın özüdür: https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/LICENSE

Bu repozitoriyanın MIT lisenziyası model çəkilərini əhatə etmir; bax: [`NOTICE`](NOTICE). Bu repoda model çəkiləri YOXDUR (MiniMax H3, HyperFlow-H3-Flash GGUF və ya VAE faylları yoxdur). Bu layihə MiniMax ilə əlaqəli deyil və MiniMax tərəfindən təsdiqlənməyib. Kommersiya istifadəsi qadağan DEYİL (bu qeyri-kommersiya lisenziyası deyil); şərtlər aşağıdadır.

**Ərazi (Applicable Territory)**
- **Preamble, I.3, I.5:** Avropa İttifaqı, Birləşmiş Krallıq, Koreya Respublikası və Amerika Birləşmiş Ştatları İSTİSNA OLMAQLA bütün dünya. Modeldən istifadə lisenziyanı qəbul etmək sayılır.
- **II:** Pulsuz (royalty-free), ötürülməyən, məhdud lisenziya: istifadə, çoxaltma, yayma, törəmə əsərlər yaratma və dəyişdirmə hüququ yalnız ərazi daxilində və müqaviləyə, həmçinin Exhibit A-ya uyğun olaraq verilir. İstisna edilmiş ərazilərdəki şəxslər MiniMax-dan ayrıca lisenziya istəyə bilər.
- **V.4:** Modelin, onun törəmələrinin VƏ ÇIXIŞLARININ (yaradılmış video/səs) ərazidən kənarda istifadəsi, çoxaldılması, dəyişdirilməsi, yayılması və ya nümayişi icazəli deyil. **Deməli, yaradılmış videoların Aİ/BK/Cənubi Koreya/ABŞ-də dərc edilməsi və ya göstərilməsi lisenziyadan kənardadır.**
- **Exhibit A-1:** Ərazidən kənarda istifadə Məqbul İstifadə Siyasətini (Acceptable Use Policy) pozur.

**Yayım (III)** (bu repo modeli yaymır; əgər siz yayırsınızsa)
- **III.1:** Hər alıcıya lisenziyanın bir nüsxəsini verin. **III.2:** Dəyişdirilmiş faylları nəzərə çarpan bildirişlərlə işarələyin.
- **III.3:** Tövsiyə olunur (məcburi deyil): "Powered by MiniMax H3" bildirişi, hazırlanan fayllarda AI-yaradılma identifikatoru, açıq yazı.
- **III.4:** Yayımlar mütləq bu mətnli NOTICE faylı ilə müşayiət OLUNMALIDIR: "MiniMax H3 is licensed under the MiniMax H3 Community License Agreement, Copyright © 2026 MiniMax. All Rights Reserved."
- **Exhibit A-12:** məzmunun maşın tərəfindən yaradıldığını aydın şəkildə bildirmədən hər hansı ictimai mühitdə dərc edilməsi qadağandır: AI ilə yaradılmış videoları dərc edərkən onları etiketləyin (tam siyahı: `docs/LISANS_UYARISI.md`).
- **III (son abzas):** Dəyişikliklərinizə öz müəllif hüququnuzu əlavə edə bilərsiniz, lakin istifadəyə/yayıma əlavə və ya fərqli şərtlər qoya bilməzsiniz; ərazi qaydaları yenə də tətbiq olunur.

**Kommersiya şərtləri (IV)**
- **IV.1:** Kommersiya məhsullarınız/xidmətləriniz illik 20 milyon ABŞ dolları (və ya ekvivalenti) gəlirdən çox əldə edirsə, api@minimax.io ünvanından ƏVVƏLCƏDƏN yazılı icazə alın (mövzu: "MiniMax H3 licensing - authorization request").
- **IV.2:** Modeldən istifadə edən kommersiya məhsulunun/xidmətinin interfeysində "MiniMax H3" nəzərə çarpacaq şəkildə göstərilməlidir.

**İstifadə məhdudiyyətləri (V)**
- **V.1:** Tətbiq olunan qanunlara (ticarət uyğunluğu daxil) və Exhibit A-ya əməl edin. **V.2:** Giriş verdiyiniz hər kəsi ən azı bu məhdudiyyətlər qədər qoruyucu şərtlərlə bağlayın və onları məlumatlandırın.
- **V.3:** Modeldən və ya onun ÇIXIŞLARINDAN başqa AI modelini (MiniMax H3 və onun törəmələri istisna olmaqla) təkmilləşdirmək üçün istifadə edə bilməzsiniz. (I.11: distillə və sintetik çıxışlar üzərində təlim modeli "törəmə" edir; çıxışların özü törəmə deyil.)
- **V.5:** Üçüncü tərəflərə modellə çıxış yaradan məhsul/xidmət/hostinq xidməti təklif edirsinizsə: fəaliyyətdən əvvəl və boyunca ağlabatan texniki və təşkilati qoruyucu tədbirlər, bildiriş mexanizmi, təcili araşdırma və təkrar pozuntu edənlərin silinməsi/söndürülməsi/dayandırılması.

**Əmtəə nişanı və hüquqlar (VI)**
- **VI.1:** Yaratdığınız törəmə əsərlərə və model törəmələrinə siz sahibsiniz (MiniMax-ın hüquqlarına tabe olaraq). **VI.2:** MiniMax adları/nişanları lisenziyalaşdırılmayıb (təsvir və yayım üçün zəruri olandan başqa); "MiniMax H3" nişanından yalnız III.3-ə əməl etmək üçün, ərazi daxilində istifadə oluna bilər; əlaqə olduğunu ifadə etməyin.
- **VI.3:** MiniMax-ı və ya hər hansı şəxsi materialların/çıxışların hüquqlarınızı pozduğunu iddia edərək məhkəməyə versəniz, bütün lisenziyalarınız həmin gün sona çatır; sizin və ya başqalarının istifadəsi/yayımı nəticəsində yaranan üçüncü tərəf iddialarına qarşı MiniMax-ı müdafiə edir və zərərini ödəyirsiniz.
- **VI.4:** MiniMax çıxışlar üzərində heç bir hüquq iddia etmir; çıxışlara və onlardan istifadəyə siz və istifadəçiləriniz cavabdehsiniz.

**İmtinalar və xitam (VII, VIII, IX)**
- **VII.1:** Dəstək/yeniləmə öhdəliyi yoxdur. **VII.2:** Model və çıxışlar "AS IS" (olduğu kimi), zəmanətsiz təqdim olunur; uyğunluğa siz qərar verirsiniz və riski öz üzərinizə götürürsünüz. **VII.3:** MiniMax və əlaqəli şirkətlər qanunun icazə verdiyi həddə heç bir zərərə görə məsuliyyət daşımır.
- **VIII.1:** Qəbul/giriş anından qüvvəyə minir. **VIII.2:** Pozuntu olduqda MiniMax lisenziyaya xitam verə bilər; siz istifadəni/yayımı dayandırmalı, nüsxələri silməli və alıcıları məlumatlandırmalısınız (VI.1, VI.3, VII, IX qüvvədə qalır).
- **IX:** Honkonq XİR (SAR) qanunu; Honkonq məhkəmələrinin müstəsna yurisdiksiyası (BMT-nin CISG konvensiyası istisna edilir).
- **Əlavə qeyd:** MiniMax H3-ün kodlayıcısı Qwen3-VL-32B (Apache 2.0) istifadə edir.

**Məqbul İstifadə Siyasəti (Exhibit A)** (modeldən, törəmələrdən və ya çıxışlardan bunlar üçün istifadə ETMƏYİN)
- A-1 ərazidən kənarda istifadə; A-2 qanunların və ya üçüncü tərəfin əqli mülkiyyətinin pozulması; A-3 özünə və ya başqalarına zərər vurmaq; A-4 çıxışları zərər vermək üçün başqa məqsədə yönəltmək/yaymaq; A-5 qoruyucu tədbirləri dolanmaq; A-6 yetkinlik yaşına çatmayanlardan sui-istifadə/onlara zərər vurmaq; A-7 başqalarına zərər vermək və ya seçkilərə təsir göstərmək üçün yoxlanıla bilən yalan məlumat; A-8 saxta onlayn fəallıq (saxta rəylər və s.); A-9 böhtan, təhqir, təqib; A-10 zərərli proqram; A-11 başqalarına zərər vermək üçün şəxsi məlumatlar; **A-12 məzmunun maşın tərəfindən yaradıldığını aydın və nəzərə çarpan şəkildə bildirmədən hər hansı ictimai mühitdə (bot paylaşımları daxil) dərc edilməsi**; A-13 razılıq olmadan kimlik təqlidi; A-14 kritik sahələrdə yüksək riskli avtomatlaşdırılmış qərarlar (hüquq-mühafizə, immiqrasiya, səhiyyə, kritik infrastruktur, kredit, məşğulluq, mənzil, təhsil, sosial xal sistemi, sığorta və s.); A-15 digər ölkələrin/regionların sosial, etik, mənəvi normalarının pozulması; A-16 zorakı ekstremizm/terrorçuluq; A-17 qorunan xüsusiyyətlərə əsaslanan ayrı-seçkilik/zərər; A-18 həssas qrupların istismarı; **A-19 hərbi məqsədlər**; A-20 icazəsiz/lisenziyasız peşə fəaliyyəti (maliyyə, hüquq, tibb və s.).
- Qeyd: bu sadə dildə xülasədir; şübhə olduqda ingilis dilindəki lisenziya mətni üstünlük təşkil edir.

## Sübut etiketləri

Bütün sənədlər üçün bir dəst (köhnə yazılışlar mötərizədə):
- **[ölçülüb]** (EN: measured; TR: ölçtüm, olctum): bu layihədə işə salınıb, sübut yolu mövcuddur.
- **[oxunub]** (EN: read; TR: okudum yol, okudum): mənbə və ya skript oxunub, işə salınmayıb.
- **[dizayn]** (EN: design; TR: tasarım, tasarim): layihələndirilib, real işə salınmada hələ görünməyib.
- **[təxmin]** (EN: guess; TR: tahmin): yoxlanılmayıb.
- **[sınanmayıb]** (EN: not tried; TR: denenmedi): heç vaxt işə salınmayıb.
- **[istifadəçi bildirib]** (EN: user-reported; TR: kullanıcı bildirdi): istifadəçi tarixlə bildirib; müstəqil ölçülməyib.
- **[hesablanıb]** (EN: computed; TR: hesap; köhnə yazılışlar: calculated, hesap): ölçülmüş giriş məlumatlarından alınan, özü ölçülməyən ədəd; hesablama yanında yazılır. Köhnə mətndə [proposal] / [öneri] = [təxmin].

Mötərizələrdə istifadə olunan işə salınma adları (öz adlarımızdır, bu repodakı fayllar deyil): U209 = `uret.ps1` vasitəsilə buraxılış binarı ilə 209 kadr; B209 və B192 = 209 və 192 kadrda şəkildən-videoya (`-InitImg`) işə salınmaları; B56VT2 = buraxılış binarı, 56 kadr, 56 kadrlıq bayt istinadı R0 ilə müqayisə olunub; F209b, F209V2, F209V2K = inkişaf build-ində 209 kadrlıq işə salınmalar (təfərrüatlar: `docs/OLCUMLER.md`).

## Məlum məhdudiyyətlər
- **Bayt sübutu** (özünüz necə təkrar etmək olar: `docs/KANITLAR.md`, "R0 ve latent referansi nasil uretilir"; sm_61 kartımızda yoxlanılıb, digər GPU-lar bayt-bayt eyni olmaya bilər [təxmin]): yamaq seriyamızla (yaddaş bayraqları açıq) 56 kadrlıq işə salınma istinada eyni olan `0979f156d548169b...` sha256-nı verdi [ölçülüb]; 141 kadrda latent sha256 `E5D028F8632BE4FE...` eyni idi (0013/0014 bayraqları ilə). 158-dən 209-a qədər kadrlar üçün birbaşa bayt istinadı yoxdur; sübut keçid zəncirindədir. Rəqəmsal keçidlərdən keçmək yaxşı klipə zəmanət vermir: zamanla hərəkət ardıcıllığı gözlə yoxlanılır (bax: `docs/KAPILAR.md`).
- **209 kadr, hansı bayraq dəsti:** 209 kadrlıq bayt zənciri sübutu inkişaf build-ində F209V2 bayraq dəsti ilə götürülüb (blok-quyruq bayraqları yoxdur, 0019/0020 yamaqları olmadan qurulub); `uret.ps1` 209 kadr üçün bu reseptdən istifadə edir [oxunub: skript; `uret.ps1` vasitəsilə real mühərrik işə salınması U209 işə salınmasında keçdi].
- Bir kartda (GTX 1050 Ti 4 GB) yoxlanılıb; digər kartlar sınanmayıb.
- **Hansı binar ölçülüb:** 141 kadrlıq latent və bayt zənciri inkişaf build-lərimizlə ölçülüb. Yüklədiyiniz buraxılış binarı yeni build-dir: onun 56 kadrlıq bayt keçidi keçdi (növbəti bənd) və `uret.ps1` vasitəsilə 209 kadrlıq işə salınma keçidi keçdi (U209 işə salınması, 3414 san, VRAM zirvəsi 3777 MiB) [ölçülüb]; inkişaf build-indəki 209 işə salınması ilə müqayisədə latent bayt-bayt eynidir; videoda kadrlar (md5) və səs eynidir, AVI faylının sha256-sı konteynerə görə fərqlənir [ölçülüb] (bax: `docs/OLCUMLER.md`, bölmə 0).
- **Buraxılış binarı, 56 kadr:** buraxılış binarı (sd-cli `c5cebe78...`, stable-diffusion.dll `e5d3d329...`) R0 ilə bayt-bayt eyni 56 kadrlıq nəticə verdi (sha256 `0979f156d548169be03acd1a9d7617102a75333aa48a28d6bbfd1cc5fa3f604d`; hər kadrın md5-i və səs eynidir), standart bayraqlarla (`SD_*` dəyişənləri olmadan) birbaşa işə salındı, exit kodu 0, 601 san [ölçülüb: B56VT2 işə salınması, 2026-11-19; sübutu müəlliflər saxlayır, bu repoda yoxdur]. Əhatə: yalnız bizim sm_61 kartımız və 56 kadr; təmiz-kök quraşdırma testi deyil; 141 kadrlıq latent və 209 zənciri köhnə binarla ölçülüb və bununla TƏKRARLANMAYIB [sınanmayıb]. İlk cəhd (B56VT, köməkçi skript vasitəsilə) 58 san sonra səssiz bitdi, səbəbi bilinmir [təxmin: yaddaş təzyiqi]; ikinci cəhd `sd-cli` faylını birbaşa işə saldı.
- Quraşdırma və işə salma skriptləri boş qovluqdan hələ yoxlanılmayıb (təmiz-kök testi gözlənilir).
- Yol xəritəsi və növbəti addımlar: `ROADMAP.md`.

## Vəziyyət və məhdudiyyətlər
- Bir maşında yoxlanılıb (GTX 1050 Ti 4 GB, 16 GB RAM, i7-7700HQ). Digər 4 GB-lıq kartlar və digər RAM ölçüləri fərqli ola bilər.
- **Standart 209 kadr (8,7 san):** keyfiyyət keçidlərimizdən keçdi (küy 1,08, F209V2K işə salınması) [ölçülüb: `uret.ps1` vasitəsilə buraxılış binarı ilə 209 kadr, U209 işə salınması; latent inkişaf build işə salınması ilə bayt-bayt eynidir; videoda kadrlar və səs eynidir, fayl sha-sı konteynerə görə fərqlənir; sübutu müəlliflər saxlayır, bu repoda yoxdur]. 209 kadrda DiT VRAM zirvəsi 4096 MiB-dan 3777 MiB idi (F209b və U209 işə salınmaları; bütün kartın `nvidia-smi` göstəricisi), ehtiyat payı azdır: digər GPU yükü (ekran, digər tətbiqlər) işə salınmanın `blocks.0` mərhələsində uğursuz olmasına səbəb ola bilər; yalnız GTX 1050 Ti üzərində sınanıb. Həmin işə salınma zamanı ekranın vəziyyəti qeyd olunmayıb; ekranınız bu kartda işləyirsə, daha az VRAM mövcuddur [təxmin: təxminən 100-300 MB-lıq Windows ekran yükü]; lazım olsa, ekranı inteqrasiya olunmuş GPU-ya qoşun [tövsiyə, sınanmayıb]. Sampling 2730 san çəkdi (U209 işə salınması: addımlar 436-483 san) və ayrı proses VAE dekodlaması 173 san (2-ci mərhələ səs dekodlaması ilə cəmi 193 san) [ölçülüb: U209 buraxılış binarı; köhnə inkişaf işə salınmaları: 2664 san və 174 san]. 1-ci mərhələdə proses daxili VAE yaddaşı bitirdi və temporal tiling-ə keçdi (320 san); bu çıxış atılır, video plitəsiz 2-ci mərhələdən götürülür. U209-da RAM zirvəsi ölçülməyib. 209 kadrdan uzun kliplər bu buraxılışın tərkibində deyil.
- **Image-to-video (`-InitImg`):** başlanğıc şəkli ilə bu GPU-da hədd 192 kadrdır (24 fps ilə 8,0 san): 209 kadr yerləşmədi (blok 0-da təxminən 17,5 MB VRAM çatışmır: 2587 MB lazım, 2570 MB mövcud); 192 kadr `uret.ps1` vasitəsilə 3086 san-də işlədi, VRAM zirvəsi 3783 MiB oldu və keçid keçdi [ölçülüb: B209 və B192 işə salınmaları, 2026-11-20, bir səhnə; sübutu müəlliflər saxlayır, bu repoda yoxdur]. Digər GPU-larda sınanmayıb [sınanmayıb].
- **Boş RAM vacibdir:** təxminən 11 GB BOŞ RAM lazımdır (mühərrik prosesi təxminən 11 GB tutur) [ölçülüb]. Boş RAM az olduqda proses xəta mesajı olmadan ölə bilər [təxmin: bunu bir dəfə təxminən 300 MB boş RAM ilə müşahidə etdik, o zaman `sd-cli` təxminən 10 GB tuturdu]. İşləyərkən digər böyük proqramları açmayın: 16 GB-lıq maşında yalnız təxminən 0,3-0,5 GB boş qalır və yaddaş təzyiqi altında işə salınma səssizcə ölə bilər. Başlamazdan əvvəl brauzerləri, oyunları və digər böyük proqramları bağlayın və boş RAM-i yoxlayın.
- **Təmiz-kök testi gözlənilir:** quraşdırma və işə salma skriptləri yalnız bu təlimatlarla boş qovluqdan hələ yoxlanılmayıb; bu test (istinada qarşı 56 kadrlıq bayt müqayisəsi daxil) qeyd olunduqda bu bölmə yenilənəcək.
- Burada heç bir yaradılmış video verilmir.

<!-- i18n-source: README.md sha256:3ec3d0b8e9f1 -->
