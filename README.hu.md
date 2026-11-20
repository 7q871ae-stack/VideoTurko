# VideoTurko

[English](README.md) · [Türkçe](README.tr.md) · [简体中文](README.zh-CN.md) · [日本語](README.ja.md) · [Español](README.es.md) · [Русский](README.ru.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [العربية](README.ar.md) · [Português (BR)](README.pt-BR.md) · [Italiano](README.it.md) · [한국어](README.ko.md) · [हिन्दी](README.hi.md) · [Bahasa Indonesia](README.id.md) · [Tiếng Việt](README.vi.md) · [Polski](README.pl.md) · [Nederlands](README.nl.md) · [Українська](README.uk.md) · [فارسی](README.fa.md) · [עברית](README.he.md) · [ไทย](README.th.md) · [বাংলা](README.bn.md) · [اردو](README.ur.md) · [Ελληνικά](README.el.md) · [Čeština](README.cs.md) · [Română](README.ro.md) · Magyar · [Svenska](README.sv.md) · [Azərbaycanca](README.az.md) · [Bahasa Melayu](README.ms.md)

![Windows](https://img.shields.io/badge/Windows-10%2F11-blue) ![GPU](https://img.shields.io/badge/NVIDIA-4%20GB%20(sm__61)-76b900) ![License](https://img.shields.io/badge/code-MIT-green) ![Status](https://img.shields.io/badge/status-clean--root%20test%20pending-orange)

> **30 másodpercben:** egy 4 GB-os videókártya egyetlen menetben el tud készíteni egy 209 képkockás (8.7 s) MiniMax H3 videót: egy gépen ellenőrizve (GTX 1050 Ti 4 GB; a `kur.ps1` teljes telepítése üres mappában még nincs végigellenőrizve) [mért: 209 képkocka a kiadási binárissal a `uret.ps1`-en keresztül, U209 futás; a latent bájtra azonos a fejlesztői build futásával; a képkockák és a hang a videóban azonosak, a fájl sha-ja a konténer miatt eltér; a bizonyítékokat a szerzők őrzik, ebben a tárolóban nincsenek]; `-InitImg` mellett (kép videóvá) legfeljebb 192 képkocka (8.0 s) [mért: B192 futás]; 209 képkocka kb. 57 percig tart, az alapértelmezett időkorlát 80 perc [mért: U209 futás]; a futtatást az alábbi 3 lépés mutatja.

VideoTurko: stable-diffusion.cpp memóriapatchek és receptek a MiniMax H3 (szövegből videó) futtatásához 4 GB-os GTX 1050 Ti-n, legfeljebb 209 képkocka (8.7 s) egyetlen menetben; kép videóvá (`-InitImg`) legfeljebb 192 képkocka (8.0 s) (a 209 képkockát bájtlánc igazolja; az 56 és 141 képkockás ellenőrzéseken az eredmény bájtra azonos volt a patchek nélküli futással).

## Gyorsindítás (Windows, 3 lépés)
**Állapot: az alábbi telepítő és futtató szkriptek még készülnek, a tiszta mappás teszt még hátravan; amíg ez nem sikerül, nem állítjuk, hogy bármi működik (lásd: „Állapot és korlátok”).**

1. **Töltsd le** ezt a tárolót (zöld **Code** gomb, majd **Download ZIP**), és csomagold ki egy RÖVID útvonalra, például `C:\vt`.
2. **Telepítsd**: nyiss egy PowerShellt ebben a mappában (írd be a `powershell` szót a Fájlkezelő címsorába), és futtasd:
   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File scripts\kur.ps1
   ```
   A telepítés gyökere a mappa, ahová kicsomagoltad az archívumot (a motor az `engine\bin` mappába kerül, a modellek a `model` mappába); más hely használatához előbb állítsd be a `VT_ROOT` környezeti változót. A szkript ellenőrzi a GPU-t, az illesztőprogramot, a RAM-ot és a lemezt, letölti a motort és a modelleket (a motor zip-jeit és az újonnan letöltött modellfájlokat sha256-tal ellenőrzi; az a modellfájl, amely már ott van és a mérete helyes, csak méretre van ellenőrizve, a teljes sha256-ellenőrzést a `scripts\modelleri_indir.ps1 -Dogrula` végzi), lefuttat egy rövid valódi próbát, és csak akkor írja ki a READY-t, ha az átment [tervezett: a `kur.ps1` még nem futott végig tiszta mappában; ezt a mondatot a tiszta mappás teszt után frissítjük]. Az `-ExecutionPolicy Bypass` csak erre az egy folyamatra érvényes; mint minden telepítőt, előbb olvasd el a `scripts\kur.ps1`-et.
   A motor zip-fájlja a GitHubon közzétett v0.1.0 kiadásból töltődik le (közzétéve: 2026-11-19; a sha256-ja rögzítve van a `kur.ps1`-ben). Internet nélkül vagy saját builddel adj meg helyi zip-fájlokat: `-MotorZip <path> -CudaZip <path>`. A helyi zip-fájlt ugyanazzal a rögzített sha256-tal ellenőrzi (a mellette lévő `.sha256` fájlt figyelmen kívül hagyja), ezért a kiadási zipnek kell lennie; saját buildhez előbb állítsd be a `VT_MOTOR_SHA256` / `VT_CUDA_SHA256` változót annak sha256-jára. Rossz sha256 esetén a szkript 1-es kóddal leáll. Az `engine\bin` mappába csak `.exe` és `.dll` kerül; a licencek és a README az `engine\lisanslar\<zip name>\` mappába. [a kiadás előtt kipróbálva a dist zip-ekkel: a melletti `.sha256` és az önhivatkozásra figyelmeztetés, a bináris és a DLL-ek a helyükre kerültek, az `sd-cli --help` lefutott; a telepített binárisok sha-ja egyezett (`c5cebe78...`, `e5d3d329...`); a modelllépést és a `kur.ps1` 5 képkockás próbáját valódi GPU-n MÉG NEM futtattuk]
   **A modell licence:** a modelllépés előtt a telepítő kiírja a licenc összefoglalóját (`docs/LISANS_KABUL.txt`, teljes szöveg: `docs/LISANS_UYARISI.md`: MiniMax H3 Community License, a generált videókra is kiterjedő területi korlátok, kereskedelmi és MI-jelölési szabályok), és elfogadást kér (`E` = igen). Előbb olvasd el. Felügyelet nélküli futtatáshoz megadhatod a `-LisansKabul E` kapcsolót, ami azt jelenti, hogy te magad elolvastad és elfogadtad a licencet; ne add meg más helyett. (MI-ügynököknek: kövessétek az `AGENTS.md`-t; soha ne írjatok E-t a felhasználó beleegyezése nélkül.) Elfogadás nélkül a `kur.ps1` 2-es kilépési kóddal leáll, és nem tölt le modellt.
3. **Generálj**: tedd a promptot egy szövegfájlba (egy angol bekezdés, opcionálisan egy `audio:` mondat), és futtasd:
   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File scripts\uret.ps1 -Istem istem.txt -Kare 209
   ```
   A `-Kare` a 17k+5 rácsot követi (56, 73, ... 192, 209); alapértelmezés 209 (8.7 s), a leghosszabb általunk lefedett hossz. A VAE külön folyamatban fut, és soha nem csempézett (tiling) [valódi motorfutás a `uret.ps1`-en keresztül a kiadási binárissal, külön folyamatú VAE, átment az U209 futásban].

   Prompt-írási útmutató: [`docs/ISTEM_YAZIMI.md`](docs/ISTEM_YAZIMI.md) (egyetlen megszakítatlan felvétel mintája, egyenlő időszeletek, két teljes példa).

| Követelmény | Érték |
|---|---|
| Operációs rendszer | Windows 10/11, 64 bites |
| GPU | NVIDIA, 4 GB vagy több; csak GTX 1050 Ti-n (sm_61) tesztelve; kicsi a tartalék (3777/4096 MiB 209 képkockánál): egy terhelt képernyő vagy böngésző megszakíthatja a futást; más 4 GB-os kártyát nem próbáltunk |
| RAM | 16 GB (csúcs kb. 11 GB; zárd be a többi programot) |
| Lemez | 32 GiB vagy több szabad hely, a modellek SSD-n (lehetőleg NVMe) |
| Letöltés | motor zip 36.8 MB + CUDA futtatókörnyezet zip 567.5 MB [mért] + modellek 31,473,112,040 bájt (kb. 29.3 GiB) [elolvasva: a méretek a `scripts/modeller.json`-ban]; összesen kb. 30 GiB |
| Modellek | nem tartozékok; a telepítő a MiniMax licenc alapján tölti le őket (lásd az alábbi figyelmeztetést). A modellek (29.3 GiB, 31,473,112,040 bájt a `scripts/modeller.json`-ban) sem ebben a tárolóban, sem a kiadásban nincsenek: a GitHub fájl- és kiadásméret-korlátai érvényesek, a `kur.ps1` pedig a hivatalos forrásból tölti le őket sha256-ellenőrzéssel. |

A `kur.ps1` kilépési kódjai: 0 READY, 1 hiba, 2 felhasználói beavatkozás kell (licenc, vagy még nincs kiadás/zip), 3 nincs elég hardver vagy lemezhely, 4 leállítva (DUR fájl). A `uret.ps1` csak akkor fogad el egy futást, ha az `.avi` létezik, a képkockák száma helyes és a naplók tiszták [mért: egy valódi futás a `uret.ps1`-en keresztül a kiadási binárissal, U209 futás, 209 képkocka, az ellenőrzés átment]. A `uret.ps1` kilépési kódjai: 0 DONE (a minőségi ellenőrzés átment), 1 hiba vagy érvénytelen kimenet (beleértve a hangsáv nélküli videót), 2 leállítva (DUR fájl), 5 `KAPI RED` (a minőségi ellenőrzés megbukott: a klipet nem fogadtuk el, a döntés a tiéd), 6 az ellenőrzést nem sikerült lefuttatni (a klipet nem fogadtuk el). Részletek az AGENTS.md-ben. [mért: 0, 1 (néma videó), 5 és 6 kilépési kód hamis motorral és hamis ellenőrzéssel készült forgatókönyvekben; valódi motorral: 0-s kilépési kód az U209 futásban]

### Hibaelhárítás (részletek: `docs/SIK_HATALAR.md`)
| Ezt látod | Mit jelent, mit tegyél |
|---|---|
| `STATUS_DLL_NOT_FOUND` / `cudart64_12.dll not found` (#13) | Ne indítsd kézzel az `sd-cli.exe`-t; futtasd a `scripts\kur.ps1`-et, amely a helyére teszi a CUDA DLL-eket. |
| `failed during weight preparation` a `blocks.0`-nál (#1, #3, #5) | Nincs elég VRAM a memóriakapunál: használj kevesebb képkockát a 17k+5 rácsból, zárd be a GPU-t használó többi programot, hagyd a mellékelt kapcsolókat. |
| `retrying with temporal tiling` (#6) | A VAE csempézésre váltott; a kimenet minőségi célra érvénytelen. Futtasd újra. |
| A futás az időkorlátnál véget ér, nincs videó (#7) | Emeld a `-TavanDk` értékét hosszú klipekhez (alapértelmezett időkorlát: 80 perc 209 képkockára, a `uret.ps1` állítja be; a mi 209 képkockás futásunk 57 percig tartott [mért: U209 futás]). |
| A kilépési kód üres, de „finished” áll (#14) | A burkoló szkript túl korán olvasta a kilépési kódot; futtasd újra, és ellenőrizd, hogy a videófájl létezik. |
| A rendszer lelassul, lapozás van (#18) | A motor kb. 10-11 GB RAM-ot használ; zárd be a böngészőket és a többi programot. |
| sha256-eltérés / a letöltés sikertelen | Általában megszakadt a letöltés: futtasd újra ugyanazt a parancsot, az ellenőrzött fájlokat kihagyja. |

### Újdonságok a v0.1.1-ben: további kapcsolók (részletek: `AGENTS.md`, `docs/SIK_HATALAR.md` 19-23)
Ezek nélkül a kapcsolók nélkül 4 GB-os kártyán semmi sem változik (a referenciánkhoz mért 56 képkockás bájtellenőrzés a v0.1.1-gyel is újra átment [mért]). Ha látni szeretnéd, mi futna le, add hozzá a `-Kuru` kapcsolót bármelyik parancshoz.
- `-EndImg`: az utolsó képkockát is megadhatod (első és utolsó képkocka, „FLF”); a felső határ 8 GB alatti kártyán 175 képkocka (192 nem fért bele 4 GB-ba), 8 GB-os vagy nagyobb kártyán 192. A mi GTX 1050 Ti kártyánkon mindig két folyamatban fut: 56 képkocka 1040 s, 175 képkocka 2887 s (48 perc), mindkét futás átment a minőségi ellenőrzésen [mért]. Prompttippek: `docs/ISTEM_YAZIMI.md`.
- `-W` / `-H`: más méretek, például álló 384x640; 32 többszörösei, a terület legalább 640x384 (ennél kisebb soha). 4 GB-on nem teszteltük; 8 GB alatti kártyákon a program elutasítja azokat a méreteket, amelyek túllépik a legnagyobb mért feladatunkat. A minőségi ellenőrzés küszöbei 640x384-re vannak kalibrálva.
- `-TekAsama`: kettő helyett egy folyamat, csak nagy kártyákhoz; magától soha nem kapcsol be.
- Újabb GPU-k (compute capability 7.0+, pl. RTX 20/30/40): a `GGML_CUDA_CUBLAS_COMPUTE_TYPE=f32` automatikusan beállítódik, hacsak nem állítottad be magad; ez a bejelentő RTX 4070 Ti kártyáján megszüntette a 141 vagy több képkockánál jelentkező teljesen fekete videót [felhasználó jelentette, issue #1]. Python + OpenCV nélkül az `uret.ps1` most már a GPU-feladat előtt leáll 6-os kilépési kóddal (nem készül videó, nincs félrevezető RED).
- Köszönet @SinanC73 felhasználónak az RTX 4070 Ti-n készült jelentésért, amely ezekhez a változtatásokhoz vezetett ([issue #1](https://github.com/alexturkey/VideoTurko/issues/1)).

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

## Mi ez
Kisméretű memória- és ütemezési patchek a stable-diffusion.cpp-hez, valamint a futtatási recept, ellenőrzések és mérések, amelyek lehetővé teszik, hogy a MiniMax H3 (33B DiT; mi a HyperFlow Flash 13.7B Q4_K_M GGUF-et futtatjuk; a 32B Qwen3-VL szövegkódoló külön van) egy 4 GB-os, Pascal generációs GPU-n fusson (GTX 1050 Ti, 16 GB rendszermemória).
- Egy menetben ténylegesen előállított, és a minőségi ellenőrzéseinken átment hosszak: 56, 141, 158, 175, 192, 209 képkocka 640x384-ben, 24 fps mellett (209 képkocka = 8.7 s), a H3 saját generált hangjával [mért: 209 képkocka a kiadási binárissal a `uret.ps1`-en keresztül, U209 futás; a latent bájtra azonos a fejlesztői build futásával; a képkockák és a hang a videóban azonosak, a fájl sha-ja a konténer miatt eltér; a bizonyítékokat a szerzők őrzik, ebben a tárolóban nincsenek]. A 209 a leghosszabb hossz, amelyet végignéztünk és simának találtunk [felhasználó jelentette, 2026-11-19, a videót végignézte; fájl: F209V2 kimenet, 8.708 s].
- **A bájtazonossági állítás, becsületesen körülhatárolva:** a patchek nélküli referenciával való bájtazonosságot csak 56 és 141 képkockára ellenőriztük. 158/175/192/209 képkockánál ugyanazokat a kapcsolókat és ugyanazt a binárisláncot használtuk; közvetlen bájtreferencia nincs (a patchek nélküli build ezeket a hosszakat ezen a GPU-n nem tudja futtatni).
- A minőségi beállításokat soha nem csökkentjük: ugyanaz a modell és kvantálás, 6 lépés, cfg 1, 640x384, ugyanaz a seed, csempézés nélküli VAE.
- Nem állítjuk, hogy mi vagyunk az elsők: kerestünk, és nem találtunk külső példát erre 4 GB-on, ami nem bizonyíték arra, hogy ilyen nincs.

## Felépítés
- `patches/` patchek a rögzített stable-diffusion.cpp commit ellen (lásd az ottani megjegyzéseket)
- `scripts/` fordítás, futtatás, külön folyamatú VAE, ellenőrző és konzisztencia-segédszkriptek (`doku_norm.py`: lásd az alábbi skálamegjegyzést)
- `docs/KURULUM.md` hardver, fordítás és futtatás lépései (EN+TR)
- `docs/YAMALAR.md` patchlista, `docs/KANITLAR.md` bizonyítékok, `docs/KAPILAR.md` minőségi ellenőrzések táblázata, `docs/OLCUMLER.md` mérések, `docs/SIK_HATALAR.md` gyakori hibák, `docs/LISANS_UYARISI.md` a licenc pontjainak teljes listája
- `scripts/` rövid tárgymutató: `hiz_kos3.ps1` futtató burkoló (a `-Kuru` kiírja a pontos parancsot), `uretim_kapi.ps1` minőségi ellenőrzés, `dikis_denetim.py` varratellenőrzés, `doku_norm.py` textúrára normált zaj, `bayt_kiyas.py` bájtösszehasonlítás, `derleme_sablonu.ps1` fordítási sablon (csak a Visual Studio telemetriai segédfolyamatát, a `vctip.exe`-t állítja le, amely a fordítás megkezdése után indult, és amely különben percekig a fordítási folyamathoz kötve marad; a többi `vctip.exe` folyamatot békén hagyja)

## Minőségi ellenőrzések (hogyan fogadunk el egy eredményt)

Ez az ellenőrzés nem vizsgálja a mozgás konzisztenciáját (a tárgyak méretének vagy helyzetének ugrásait): az elfogadás előtt nézd végig az egész videót.
1. A képkockák száma helyes és van hang; a naplóban nincs memória miatti tartalékmegoldás és nincs ALLOC_FAILED sor.
2. Nyers zajellenőrzés: a mediánszűrő maradéka <= 1.5 (0-255 skála).
3. Textúrára normált zaj, `scripts/doku_norm.py` (a tároló saját verziója): N = medián maradék / Sobel-textúra, minden 6. képkockán. **Skálamegjegyzés:** ebben a verzióban a 10 mért klip N = 0.034-0.052 értéket ad (táblázat a `docs/KAPILAR.md`-ben; az F192/F209V2 utolsó negyedében eléri a 0.062-t), a kiegészítő ellenőrzés küszöbe N <= 0.065. Egy másik implementáció ugyanezeken a klipeken 0.028-0.036-ot mért, ezért a küszöbök verziók között NEM cserélhetők. Nagyon finom textúráknál (fűsorok) a tiszta N 0.075 volt, így a küszöb jelenetcsaládonként értendő. Az ajánlott kiegészítő ellenőrzés egy robusztus nagyfrekvenciás becslő (sigma-HH <= 1.5; tiszta klipek 0.74-1.19, hozzáadott s=2 zajnál 2.2-3.0).

Hatókör: a VideoTurko EGYETLEN menetről szól (legfeljebb 209 képkocka, kb. 8.7 s). Több rész összefűzését hosszabb klippé kipróbáltuk; a varratok látszottak (a jelenet nem folytatódik tisztán), ezért ez nem része a projektnek. Ha hosszabb klipekre van szükséged, találd ki a saját megoldásodat.
A beállítások a tieid: a 209 képkocka a mi tesztelt alapértelmezésünk egy 4 GB-os kártyán, nem korlát, amelyet használnod kellene. Válassz tetszőleges képkockaszámot a 17k+5 rácsból (56, 73, ... 192, 209; lásd `docs/KURULUM.md`), változtasd a promptot, a seedet, a felbontást vagy bármely kapcsolót kedved szerint. A rövidebb klipek kevesebb memóriát és időt igényelnek; a nagyobb GPU-k többet is elbírhatnak.

## Figyelmeztetés a modell licencéről
**A VideoTurko csak patcheket és szkripteket tartalmaz (MIT); aki a modellt és a kimeneteit használja, maga felel a MiniMax licenc betartásáért.** Ez nem jogi tanács. Az alábbiakban a MiniMax H3 Community License (2026. augusztus 2.) kikötései szerepelnek összefoglalva, számozással; a licenc maga a kötelező érvényű: https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/LICENSE

Ez a tároló NEM tartalmaz modellsúlyokat (sem MiniMax H3, sem HyperFlow-H3-Flash GGUF, sem VAE fájlokat). A projekt nem áll kapcsolatban a MiniMax-szal, és a MiniMax nem támogatja. A kereskedelmi felhasználás NEM tiltott (ez nem kizárólag nem kereskedelmi célú licenc); a feltételek alább olvashatók.

**Terület (Applicable Territory)**
- **Preambulum, I.3, I.5:** az egész világ, KIVÉVE az Európai Uniót, az Egyesült Királyságot, a Koreai Köztársaságot és az Egyesült Államokat. A modell használata a licenc elfogadásának minősül.
- **II:** díjmentes, át nem ruházható, korlátozott licenc használatra, sokszorosításra, terjesztésre, származékos művek készítésére és módosításra, kizárólag a területen belül, a megállapodással és az Exhibit A-val összhangban. A kizárt területeken élők külön licencet kérhetnek a MiniMax-tól.
- **V.4:** a modell, származékai ÉS KIMENETEI (generált videó/hang) használata, sokszorosítása, módosítása, terjesztése vagy megjelenítése a területen kívül nem engedélyezett. **Tehát a generált videók közzététele vagy bemutatása az EU-ban, az Egyesült Királyságban, Dél-Koreában és az USA-ban a licenc hatókörén kívül esik.**
- **Exhibit A-1:** a területen kívüli használat sérti az Acceptable Use Policy-t.

**Terjesztés (III)** (ez a tároló nem terjeszti a modellt; ha te igen)
- **III.1:** adj minden átvevőnek egy másolatot a licencről. **III.2:** jelöld a módosított fájlokat feltűnő közleményekkel.
- **III.3:** Ajánlott (nem kötelező): "Powered by MiniMax H3" közlemény, MI-generálásra utaló azonosító az elkészített fájlokon, nyilvános ismertető.
- **III.4:** a terjesztést KÖTELEZŐEN kísérnie kell egy NOTICE fájlnak ezzel a szöveggel: "MiniMax H3 is licensed under the MiniMax H3 Community License Agreement, Copyright © 2026 MiniMax. All Rights Reserved."
- **Exhibit A-12:** tilos tartalmat bármely nyilvános környezetben közzétenni anélkül, hogy egyértelműen jeleznéd, hogy gépi generálású: a közzétett MI-generált videókat jelöld meg (teljes lista: `docs/LISANS_UYARISI.md`).
- **III (utolsó bekezdés):** a módosításaidhoz hozzáadhatod saját szerzői jogodat, de nem szabhatsz további vagy eltérő feltételeket a használatra és terjesztésre; a területi szabályok továbbra is érvényesek.

**Kereskedelmi feltételek (IV)**
- **IV.1:** ha kereskedelmi termékeid vagy szolgáltatásaid évi 20 millió USD-nél (vagy ennek megfelelő összegnél) nagyobb bevételt generálnak, ELŐZETES írásbeli engedélyt kell kérned az api@minimax.io címen (tárgy: "MiniMax H3 licensing - authorization request").
- **IV.2:** a modellt használó kereskedelmi termék vagy szolgáltatás felületén feltűnően szerepelnie kell a "MiniMax H3" feliratnak.

**Használati korlátozások (V)**
- **V.1:** tartsd be a hatályos jogot (beleértve a kereskedelmi megfelelőséget) és az Exhibit A-t. **V.2:** mindenkit, akinek hozzáférést adsz, köss olyan feltételekhez, amelyek legalább ennyire védőek, mint ezek a korlátozások, és értesítsd őket.
- **V.3:** a modellt vagy a KIMENETEIT nem használhatod semmilyen más MI-modell javítására (a MiniMax H3-on és származékain kívül). (I.11: a desztilláció és a szintetikus kimeneteken való tanítás „származékká” teszi a modellt; maguk a kimenetek nem származékok.)
- **V.5:** ha harmadik feleknek olyan terméket, szolgáltatást vagy üzemeltetett szolgáltatást kínálsz, amely a modellel kimeneteket generál: a működés előtt és során észszerű technikai és szervezési biztosítékok, bejelentési mechanizmus, haladéktalan kivizsgálás, valamint az ismétlődő jogsértők eltávolítása, letiltása vagy felfüggesztése szükséges.

**Védjegyek és jogok (VI)**
- **VI.1:** az általad készített származékos művek és modellszármazékok a tiéid (a MiniMax jogainak fenntartásával). **VI.2:** a MiniMax nevei és védjegyei nem tartoznak a licenc alá (a leíráshoz és terjesztéshez szükségesen túl); a "MiniMax H3" védjegy kizárólag a III.3 teljesítéséhez, a területen belül használható; ne sugalmazz kapcsolatot.
- **VI.3:** ha beperled a MiniMax-ot vagy bárkit azzal, hogy az anyagok vagy kimenetek sértik a jogaidat, minden licenced aznap megszűnik; megvéded és kármentesíted a MiniMax-ot a te vagy mások használatából és terjesztéséből eredő harmadik felek követelései ellen.
- **VI.4:** a MiniMax nem tart igényt a kimenetekre; te és a felhasználóid felelősek a kimenetekért és azok használatáért.

**Felelősségkizárás és megszűnés (VII, VIII, IX)**
- **VII.1:** nincs támogatási vagy frissítési kötelezettség. **VII.2:** a modellt és a kimeneteket "AS IS" módon, garancia nélkül adják; az alkalmasságról te döntesz, a kockázatot te viseled. **VII.3:** a MiniMax és kapcsolt vállalkozásai nem felelnek semmilyen kárért (a jog által megengedett mértékig).
- **VIII.1:** az elfogadással vagy a hozzáféréssel lép hatályba. **VIII.2:** szerződésszegés esetén a MiniMax megszüntetheti a licencet; abba kell hagynod a használatot és terjesztést, törölnöd kell a másolatokat és értesítened az átvevőket (a VI.1, VI.3, VII, IX érvényben marad).
- **IX:** Hongkong KKT joga; a hongkongi bíróságok kizárólagos illetékessége (az ENSZ CISG egyezménye kizárva).
- **Kiegészítő megjegyzés:** a MiniMax H3 kódolója a Qwen3-VL-32B-t használja (Apache 2.0).

**Elfogadható használati szabályzat (Exhibit A)** (a modellt, a származékokat és a kimeneteket NE használd erre)
- A-1 használat a területen kívül; A-2 jogszabályok vagy harmadik felek szellemi tulajdonának megsértése; A-3 önmagad vagy mások károsítása; A-4 a kimenetek kárt okozó célra való átalakítása vagy terjesztése; A-5 a biztosítékok megkerülése; A-6 kiskorúak kihasználása vagy károsítása; A-7 igazolhatóan hamis információ mások károsítására vagy választások befolyásolására; A-8 hamis online aktivitás (hamis értékelések stb.); A-9 rágalmazás, lejáratás, zaklatás; A-10 kártevő; A-11 személyes adatok mások károsítására; **A-12 tartalom közzététele bármely nyilvános környezetben (beleértve a botbejegyzéseket) anélkül, hogy egyértelműen és feltűnően jeleznéd, hogy gépi generálású**; A-13 megszemélyesítés beleegyezés nélkül; A-14 nagy kockázatú automatizált döntések kritikus területeken (bűnüldözés, bevándorlás, egészségügy, kritikus infrastruktúra, hitel, foglalkoztatás, lakhatás, oktatás, társadalmi pontozás, biztosítás stb.); A-15 más országok/régiók társadalmi, etikai, erkölcsi normáinak megsértése; A-16 erőszakos szélsőségesség/terrorizmus; A-17 védett tulajdonságok alapján történő megkülönböztetés vagy károsítás; A-18 kiszolgáltatott csoportok kihasználása; **A-19 katonai célok**; A-20 jogosulatlan vagy engedély nélküli szakmai tevékenység (pénzügyi, jogi, orvosi stb.).
- Megjegyzés: ez közérthető összefoglaló; kétség esetén a licenc angol szövege az irányadó.

## Bizonyítéki címkék

Egy készlet minden dokumentumhoz (a régebbi írásmódok zárójelben):
- **[mért]** (TR: ölçtüm, olctum): ebben a projektben lefuttatva, a bizonyíték útvonala létezik.
- **[elolvasva]** (TR: okudum yol, okudum): a forrást vagy szkriptet elolvastuk, de nem futtattuk.
- **[tervezett]** (TR: tasarım, tasarim): megtervezve, valódi futásban még nem láttuk.
- **[feltételezés]** (TR: tahmin): nem ellenőrzött.
- **[nem próbált]** (TR: denenmedi): soha nem futtatott.
- **[felhasználó jelentette]** (TR: kullanıcı bildirdi): a felhasználó közölte, dátummal; függetlenül nem mérve.
- **[számított]** (TR: hesap; régebbi írásmódok: calculated, hesap): mért bemenetekből levezetett szám, maga nem mért; a levezetés mellette áll. [proposal] / [öneri] a régebbi szövegben = [feltételezés].

A szögletes zárójelben használt futásnevek (saját elnevezéseink, nem a tároló fájljai): U209 = 209 képkocka a kiadási binárissal a `uret.ps1`-en keresztül; B209 és B192 = „kép videóvá” (`-InitImg`) futások 209 és 192 képkockán; B56VT2 = kiadási bináris, 56 képkocka, összevetve az 56 képkockás R0 bájtreferenciával; F209b, F209V2, F209V2K = 209 képkockás futások a fejlesztői buildön (részletek: `docs/OLCUMLER.md`).

## Ismert korlátok
- **Bájtbizonyíték** (hogyan reprodukálhatod magad: `docs/KANITLAR.md`, „R0 ve latent referansi nasil uretilir”; a mi sm_61 kártyánkon ellenőrizve, más GPU-kon előfordulhat, hogy nem bájtazonos [feltételezés]): a patchsorozatunkkal (memóriakapcsolók bekapcsolva) egy 56 képkockás futás sha256-ja `0979f156d548169b...` volt, azonos a referenciával [mért]; 141 képkockánál a latent sha256-ja `E5D028F8632BE4FE...` azonos volt (a 0013/0014 kapcsolókkal). A 158-tól 209 képkockáig nincs közvetlen bájtreferencia; a bizonyíték az ellenőrzési lánc. A számszerű ellenőrzések teljesítése nem garantál jó klipet: a mozgás időbeli konzisztenciáját szemmel ellenőrizzük (lásd `docs/KAPILAR.md`).
- **209 képkocka, melyik kapcsolókészlet:** a 209 képkockás bájtlánc bizonyítékát az F209V2 kapcsolókészlettel vettük fel a fejlesztői buildön (blokkvég-kapcsolók nélkül, a 0019/0020 patchek nélkül fordítva); a `uret.ps1` ezt a receptet használja 209 képkockához [elolvasva: a szkript; a valódi motorfutás a `uret.ps1`-en keresztül átment az U209 futásban].
- Egy kártyán (GTX 1050 Ti 4 GB) ellenőrizve; más kártyákat nem próbáltunk.
- **Melyik binárist mértük:** a 141 képkockás latentet és a bájtláncot a saját fejlesztői buildjeinken mértük. A letöltött kiadási bináris új fordítás: az 56 képkockás bájtellenőrzése átment (következő pont), a 209 képkockás futás a `uret.ps1`-en keresztül átment az ellenőrzésen (U209 futás, 3414 s, VRAM-csúcs 3777 MiB) [mért]; a fejlesztői build 209 képkockás futásához képest a latent bájtra azonos; a videóban a képkockák (md5) és a hang azonosak, az AVI fájl sha256-ja a konténer miatt eltér [mért] (lásd `docs/OLCUMLER.md`, 0. szakasz).
- **Kiadási bináris, 56 képkocka:** a kiadási bináris (sd-cli `c5cebe78...`, stable-diffusion.dll `e5d3d329...`) az R0-val bájtra azonos 56 képkockás eredményt adott (sha256 `0979f156d548169be03acd1a9d7617102a75333aa48a28d6bbfd1cc5fa3f604d`; képkockánkénti md5 és a hang azonos), közvetlenül, alapértelmezett kapcsolókkal futtatva (`SD_*` változók nélkül), kilépési kód 0, 601 s [mért: B56VT2 futás, 2026-11-19; a bizonyítékokat a szerzők őrzik, ebben a tárolóban nincsenek]. Hatókör: csak a mi sm_61 kártyánk és 56 képkocka; nem tiszta mappás telepítési teszt; a 141 képkockás latentet és a 209-es láncot a régebbi binárissal mértük, és ezzel NEM ismételtük meg [nem próbált]. Az első kísérlet (B56VT, segédszkripten keresztül) 58 s után némán véget ért, az ok ismeretlen [feltételezés: memóriaszűkület]; a második kísérlet közvetlenül az `sd-cli`-t futtatta.
- A telepítő és futtató szkripteket még nem ellenőriztük üres mappából (a tiszta mappás teszt hátravan).
- Útiterv és következő lépések: `ROADMAP.md`.

## Állapot és korlátok
- Egy gépen ellenőrizve (GTX 1050 Ti 4 GB, 16 GB RAM, i7-7700HQ). Más 4 GB-os kártyák és más RAM-méretek eltérően viselkedhetnek.
- **Alapértelmezés: 209 képkocka (8.7 s):** átment a minőségi ellenőrzéseinken (zaj 1.08, F209V2K futás) [mért: 209 képkocka a kiadási binárissal a `uret.ps1`-en keresztül, U209 futás; a latent bájtra azonos a fejlesztői build futásával; a képkockák és a hang a videóban azonosak, a fájl sha-ja a konténer miatt eltér; a bizonyítékokat a szerzők őrzik, ebben a tárolóban nincsenek]. 209 képkockánál a DiT VRAM-csúcsa 3777 MiB volt a 4096 MiB-ból (F209b és U209 futás; a teljes kártyára vonatkozó `nvidia-smi` leolvasás), kicsi a tartalék: más GPU-terhelés (a kijelző, egyéb alkalmazások) hibát okozhat a `blocks.0`-nál; csak GTX 1050 Ti-n tesztelve. A kijelző állapotát a futás alatt nem jegyeztük fel; ha a kijelződ ezen a kártyán fut, kevesebb VRAM áll rendelkezésre [feltételezés: kb. 100-300 MB-nyi Windows-kijelzőterhelés]; szükség esetén csatlakoztasd a kijelzőt az integrált grafikához [tanács, nem tesztelt]. A mintavételezés (sampling) 2730 s-ig tartott (U209 futás: 436-483 s-os lépések), a külön folyamatú VAE-dekódolás 173 s (a 2. szakasz összesen 193 s a hangdekódolással) [mért: U209 kiadási bináris; régebbi fejlesztői futások: 2664 s és 174 s]. Az 1. szakaszban a folyamaton belüli VAE kifogyott a memóriából, és időbeli csempézésre váltott (320 s); ez a kimenet el van vetve, a videó a csempézés nélküli 2. szakaszból származik. A RAM-csúcsot az U209 futásban nem mértük. A 209 képkockánál hosszabb klipek nem részei ennek a kiadásnak.
- **Kép videóvá (`-InitImg`):** kezdőképpel a plafon 192 képkocka (8.0 s 24 fps mellett) ezen a GPU-n: a 209 képkocka nem fért el (a 0. blokknál kb. 17.5 MB VRAM hiányzott: 2587 MB kellett, 2570 MB állt rendelkezésre); a 192 képkocka 3086 s alatt lefutott a `uret.ps1`-en keresztül 3783 MiB VRAM-csúccsal, az ellenőrzés átment [mért: B209 és B192 futás, 2026-11-20, egy jelenet; a bizonyítékokat a szerzők őrzik, ebben a tárolóban nincsenek]. Más GPU-kon nem próbáltuk [nem próbált].
- **A szabad RAM számít:** kb. 11 GB SZABAD RAM kell (a motorfolyamat kb. 11 GB-ot tart) [mért]. Túl kevés szabad RAM mellett a folyamat hibaüzenet nélkül meghalhat [feltételezés: egyszer láttuk kb. 300 MB szabad RAM mellett, amikor az `sd-cli` kb. 10 GB-ot tartott]. Futás közben ne nyiss meg más nagy programokat: egy 16 GB-os gépen csak kb. 0.3-0.5 GB marad szabadon, és memóriaszűkében a futás némán elhalhat. Indítás előtt zárd be a böngészőket, játékokat és más nagy programokat, és ellenőrizd a szabad RAM-ot.
- **A tiszta mappás teszt hátravan:** a telepítő és futtató szkripteket még nem ellenőriztük üres mappából kizárólag ezen útmutató alapján; ezt a szakaszt frissítjük, amikor a teszt (köztük az 56 képkockás bájtösszehasonlítás a referenciával) rögzítésre kerül.
- Generált videókat itt nem mellékelünk.

<!-- i18n-source: README.md sha256:0070eed33ffd -->
