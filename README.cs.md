# VideoTurko

[English](README.md) · [Türkçe](README.tr.md) · [简体中文](README.zh-CN.md) · [日本語](README.ja.md) · [Español](README.es.md) · [Русский](README.ru.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [العربية](README.ar.md) · [Português (BR)](README.pt-BR.md) · [Italiano](README.it.md) · [한국어](README.ko.md) · [हिन्दी](README.hi.md) · [Bahasa Indonesia](README.id.md) · [Tiếng Việt](README.vi.md) · [Polski](README.pl.md) · [Nederlands](README.nl.md) · [Українська](README.uk.md) · [فارسی](README.fa.md) · [עברית](README.he.md) · [ไทย](README.th.md) · [বাংলা](README.bn.md) · [اردو](README.ur.md) · [Ελληνικά](README.el.md) · Čeština · [Română](README.ro.md) · [Magyar](README.hu.md) · [Svenska](README.sv.md) · [Azərbaycanca](README.az.md) · [Bahasa Melayu](README.ms.md)

![Windows](https://img.shields.io/badge/Windows-10%2F11-blue) ![GPU](https://img.shields.io/badge/NVIDIA-4%20GB%20(sm__61)-76b900) ![License](https://img.shields.io/badge/code-MIT-green) ![Status](https://img.shields.io/badge/status-clean--root%20test%20pending-orange)

> **Ve 30 sekundách:** grafická karta se 4 GB paměti dokáže na jeden průchod vytvořit video MiniMax H3 o 209 snímcích (8.7 s): ověřeno na jednom počítači (GTX 1050 Ti 4 GB; úplná instalace `kur.ps1` do prázdné složky zatím není ověřena od začátku do konce) [změřeno: 209 snímků s vydanou binárkou přes `uret.ps1`, běh U209; latent shodný bajt po bajtu s během na vývojovém sestavení; snímky a zvuk ve videu shodné, sha souboru se liší kvůli kontejneru; důkazy uchovávají autoři, v tomto repozitáři nejsou]; s `-InitImg` (obrázek na video) nejvýše 192 snímků (8.0 s) [změřeno: běh B192]; 209 snímků se počítá asi 57 min, výchozí časový limit je 80 min [změřeno: běh U209]; jak to spustit, ukazují 3 kroky níže.

VideoTurko: záplaty paměti pro stable-diffusion.cpp a postupy ke spuštění MiniMax H3 (text na video) na 4GB GTX 1050 Ti, až 209 snímků (8.7 s) na jeden průchod; obrázek na video (`-InitImg`) až 192 snímků (8.0 s) (209 snímků potvrzeno řetězcem bajtových kontrol; při kontrolách na 56 a 141 snímcích byl výsledek shodný bajt po bajtu s během bez záplat).

## Rychlý start (Windows, 3 kroky)
**Stav: níže uvedené instalační a spouštěcí skripty se teprve dokončují a test v čisté složce nebyl dosud proveden; dokud jím neprojdou, netvrdíme, že zde cokoli funguje (viz „Stav a omezení“).**

1. **Stáhněte** tento repozitář (zelené tlačítko **Code**, pak **Download ZIP**) a rozbalte do KRÁTKÉ cesty, například `C:\vt`.
2. **Nainstalujte**: otevřete PowerShell v této složce (do adresního řádku Průzkumníka napište `powershell`) a spusťte
   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File scripts\kur.ps1
   ```
   Kořenem instalace je složka, do které jste archiv rozbalili (engine jde do `engine\bin`, modely do `model`); chcete-li použít jiné místo, nejdříve nastavte proměnnou prostředí `VT_ROOT`. Skript zkontroluje GPU, ovladač, RAM a disk, stáhne engine a modely (zip archivy enginu a nově stažené soubory modelů se kontrolují sha256; soubor modelu, který už na místě je a má správnou velikost, se kontroluje jen podle velikosti, úplnou kontrolu sha256 spustí `scripts\modelleri_indir.ps1 -Dogrula`), provede krátký skutečný test a vypíše READY, jen když test prošel [dle návrhu: `kur.ps1` nebyl celý spuštěn v čisté složce; tato věta bude po testu v čisté složce aktualizována]. `-ExecutionPolicy Bypass` platí jen pro tento jeden proces; jako u každého instalátoru si nejdříve přečtěte `scripts\kur.ps1`.
   Dokud není vydání zveřejněno, krok s enginem skončí hláškou "release adresi/sha256 henuz yok"; zadejte lokální zip soubory: `-MotorZip <path> -CudaZip <path>`. U lokálního zipu a bez vestavěného sha256 vydání se použije soubor `.sha256` vedle zipu; odkazuje sám na sebe, není nezávislý: zachytí poškození souboru, ne záměrnou úpravu (bez tohoto souboru `kur.ps1` varuje "sha256 not verified"; chybný sha256 skript zastaví s kódem 1). Po vydání má vždy přednost vestavěný sha256 a soubor vedle se ignoruje. Do `engine\bin` se dostanou jen soubory `.exe` a `.dll`; licence a README jdou do `engine\lisanslar\<zip name>\`. [zkoušeno na dist zipech: `.sha256` vedle plus varování o odkazu na sebe samého, binárka a DLL umístěny, `sd-cli --help` proběhlo; sha nainstalovaných binárek souhlasila (`c5cebe78...`, `e5d3d329...`); krok s modely a 5snímkový test v `kur.ps1` na skutečném GPU JEŠTĚ NEBYLY spuštěny]
   **Licence modelu:** před krokem s modely instalátor vypíše shrnutí licence (`docs/LISANS_KABUL.txt`, plný text `docs/LISANS_UYARISI.md`: MiniMax H3 Community License, územní omezení platná i pro vygenerovaná videa, pravidla komerčního použití a označování AI) a požádá o souhlas (`E` = ano). Nejdříve si ji přečtěte. Pro běh bez obsluhy lze předat `-LisansKabul E`, což znamená, že jste licenci sami přečetli a přijali; nepřidávejte tento přepínač za někoho jiného. (AI agenti: řiďte se `AGENTS.md`; nikdy nezadávejte E bez souhlasu uživatele.) Bez souhlasu se `kur.ps1` zastaví s návratovým kódem 2 a nestáhne žádný model.
3. **Generujte**: prompt uložte do textového souboru (jeden odstavec v angličtině, volitelně věta `audio:`) a spusťte
   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File scripts\uret.ps1 -Istem istem.txt -Kare 209
   ```
   `-Kare` se řídí mřížkou 17k+5 (56, 73, ... 192, 209); výchozí je 209 (8.7 s), nejdelší délka, kterou pokrýváme. VAE běží v samostatném procesu a nikdy nepoužívá dlaždicování (tiling) [skutečný běh enginu přes `uret.ps1` s vydanou binárkou, VAE v samostatném procesu, prošel v běhu U209].

   Průvodce psaním promptu: [`docs/ISTEM_YAZIMI.md`](docs/ISTEM_YAZIMI.md) (vzor jednoho nepřerušeného záběru, stejně dlouhé časové úseky, dva úplné příklady).

| Požadavek | Hodnota |
|---|---|
| OS | Windows 10/11, 64bitový |
| GPU | NVIDIA, 4 GB nebo více; testováno jen na GTX 1050 Ti (sm_61); malá rezerva (3777/4096 MiB při 209 snímcích): vytížená obrazovka nebo prohlížeč mohou běh přerušit; jiné karty se 4 GB jsme nezkoušeli |
| RAM | 16 GB (špička asi 11 GB; zavřete ostatní programy) |
| Disk | 32 GiB nebo více volného místa, modely na SSD (ideálně NVMe) |
| Stahování | zip enginu 36.8 MB + zip běhového prostředí CUDA 567.5 MB [změřeno] + modely 31,473,112,040 bajtů (asi 29.3 GiB) [přečteno: velikosti v `scripts/modeller.json`]; celkem asi 30 GiB |
| Modely | nejsou součástí; instalátor je stahuje podle licence MiniMax (viz upozornění níže). Modely (29.3 GiB, 31,473,112,040 bajtů v `scripts/modeller.json`) nejsou ani v tomto repozitáři, ani ve vydání: platí limity GitHubu na velikost souborů a vydání a `kur.ps1` je stahuje z oficiálního zdroje s ověřením sha256. |

Návratové kódy `kur.ps1`: 0 READY, 1 chyba, 2 je potřeba vstup uživatele (licence, nebo zatím chybí vydání/zip), 3 nedostatečný hardware nebo disk, 4 zastaveno (soubor DUR). `uret.ps1` přijme běh, jen pokud existuje `.avi`, počet snímků sedí a logy jsou čisté [změřeno: jeden skutečný běh přes `uret.ps1` s vydanou binárkou, běh U209, 209 snímků, kontrola prošla]. Návratové kódy `uret.ps1`: 0 DONE (kontrola kvality prošla), 1 chyba nebo neplatný výstup (včetně videa bez zvukové stopy), 2 zastaveno (soubor DUR), 5 `KAPI RED` (kontrola kvality neprošla: klip nebyl přijat, rozhodnutí je na vás), 6 kontrolu nešlo provést (klip nebyl přijat). Podrobnosti v AGENTS.md. [změřeno: návratové kódy 0, 1 (video bez zvuku), 5 a 6 ve scénářích s falešným enginem a falešnou kontrolou; se skutečným enginem: kód 0 v běhu U209]

### Řešení potíží (podrobnosti: `docs/SIK_HATALAR.md`)
| Co vidíte | Co to znamená a co dělat |
|---|---|
| `STATUS_DLL_NOT_FOUND` / `cudart64_12.dll not found` (#13) | Nespouštějte `sd-cli.exe` ručně; spusťte `scripts\kur.ps1`, který DLL knihovny CUDA umístí na správné místo. |
| `failed during weight preparation` u `blocks.0` (#1, #3, #5) | Nedostatek VRAM u paměťové brány: použijte menší počet snímků z mřížky 17k+5, zavřete ostatní programy využívající GPU, ponechte dodané přepínače. |
| `retrying with temporal tiling` (#6) | VAE přešlo na dlaždicování; výstup je pro hodnocení kvality neplatný. Spusťte znovu. |
| Běh skončí na časovém limitu, bez videa (#7) | Zvyšte `-TavanDk` pro dlouhé klipy (výchozí časový limit: 80 min pro 209 snímků, nastavuje `uret.ps1`; náš běh na 209 snímků trval 57 min [změřeno: běh U209]). |
| Návratový kód prázdný, ale vypsáno „finished“ (#14) | Obalový skript přečetl návratový kód příliš brzy; spusťte znovu a ověřte, že soubor videa existuje. |
| Systém zpomaluje, probíhá odkládání do swapu (#18) | Engine používá asi 10-11 GB RAM; zavřete prohlížeče a ostatní programy. |
| Neshoda sha256 / stahování selhalo | Obvykle bylo stahování přerušeno: spusťte stejný příkaz znovu, ověřené soubory se přeskočí. |

## Co to je
Sada drobných záplat paměti a plánování pro stable-diffusion.cpp spolu s postupem spuštění, kontrolami a měřeními, díky nimž MiniMax H3 (DiT 33B; spouštíme GGUF HyperFlow Flash 13.7B Q4_K_M; 32B textový enkodér Qwen3-VL je zvlášť) běží na 4GB GPU generace Pascal (GTX 1050 Ti, 16 GB systémové paměti).
- Délky na jeden průchod, které jsme skutečně vytvořili a které prošly našimi kontrolami kvality: 56, 141, 158, 175, 192, 209 snímků v 640x384 při 24 fps (209 snímků = 8.7 s), se zvukem generovaným samotným H3 [změřeno: 209 snímků s vydanou binárkou přes `uret.ps1`, běh U209; latent shodný bajt po bajtu s během na vývojovém sestavení; snímky a zvuk ve videu shodné, sha souboru se liší kvůli kontejneru; důkazy uchovávají autoři, v tomto repozitáři nejsou]. 209 je nejdelší délka, kterou jsme zhlédli a shledali plynulou [hlášeno uživatelem, 2026-11-19, video zhlédnuto celé; soubor: výstup F209V2, 8.708 s].
- **Tvrzení o bajtové shodě, poctivě vymezené:** bajtová shoda s referencí bez záplat byla ověřena jen pro 56 a 141 snímků. Pro 158/175/192/209 snímků jsme použili stejné přepínače a stejný řetězec binárek; přímá bajtová reference neexistuje (sestavení bez záplat takové délky na tomto GPU nespustí).
- Nastavení kvality se nikdy nesnižuje: stejný model a kvantizace, 6 kroků, cfg 1, 640x384, stejný seed, VAE bez dlaždicování.
- Netvrdíme, že jsme první: hledali jsme a nenašli žádný vnější příklad tohoto na 4 GB, což není důkaz, že žádný neexistuje.

## Struktura
- `patches/` záplaty proti pevně zvolenému commitu stable-diffusion.cpp (viz poznámky tam)
- `scripts/` sestavení, spuštění, VAE v samostatném procesu, pomocné skripty kontrol a konzistence (`doku_norm.py`: viz poznámka o škále níže)
- `docs/KURULUM.md` hardware, sestavení a spuštění (EN+TR)
- `docs/YAMALAR.md` seznam záplat, `docs/KANITLAR.md` důkazy, `docs/KAPILAR.md` tabulka kontrol kvality, `docs/OLCUMLER.md` měření, `docs/SIK_HATALAR.md` časté chyby, `docs/LISANS_UYARISI.md` úplný výčet bodů licence
- `scripts/` stručný rejstřík: `hiz_kos3.ps1` obalový skript spuštění (`-Kuru` vypíše přesný příkaz), `uretim_kapi.ps1` kontrola kvality, `dikis_denetim.py` kontrola švů, `doku_norm.py` šum normalizovaný vůči textuře, `bayt_kiyas.py` bajtové porovnání, `derleme_sablonu.ps1` šablona sestavení (zastaví jen pomocný telemetrický proces Visual Studia `vctip.exe`, který se spustil až po zahájení vlastního sestavení a který by jinak držel proces sestavení připojený několik minut; ostatní procesy `vctip.exe` nechá být)

## Kontroly kvality (jak se výsledek přijímá)

Tato kontrola nehlídá konzistenci pohybu (skoky měřítka nebo polohy objektů): před přijetím zhlédněte celé video.
1. Počet snímků sedí a zvuk je přítomen; v logu nejsou žádné záložní postupy kvůli paměti ani řádky ALLOC_FAILED.
2. Kontrola surového šumu: zbytek po mediánovém filtru <= 1.5 (škála 0-255).
3. Šum normalizovaný vůči textuře, `scripts/doku_norm.py` (verze z tohoto repozitáře): N = mediánový zbytek / Sobelova textura, každý 6. snímek. **Poznámka o škále:** v této verzi dává 10 změřených klipů N = 0.034-0.052 (tabulka v `docs/KAPILAR.md`; v poslední čtvrtině F192/F209V2 dosahuje 0.062) a práh dodatečné kontroly je N <= 0.065. Jiná implementace naměřila na stejných klipech 0.028-0.036, takže prahy mezi verzemi NEJSOU zaměnitelné. U velmi jemných textur (řady trávy) bylo čisté N 0.075, práh se proto volí podle rodiny scén. Doporučená dodatečná kontrola: robustní odhad vysokých frekvencí (sigma-HH <= 1.5; čisté klipy 0.74-1.19, přidaný šum s=2 dává 2.2-3.0).

Rozsah: VideoTurko se týká JEDNOHO průchodu (až 209 snímků, asi 8.7 s). Spojování více částí do delšího klipu bylo zkoušeno; švy byly vidět (scéna na sebe čistě nenavazuje), proto to není součástí projektu. Chcete-li delší klipy, vymyslete si vlastní postup.
Nastavení je vaše: 209 snímků je naše ověřená výchozí hodnota na kartě se 4 GB, ne limit, který musíte dodržet. Zvolte libovolný počet snímků z mřížky 17k+5 (56, 73, ... 192, 209; viz `docs/KURULUM.md`), měňte prompt, seed, rozlišení nebo jakýkoli přepínač podle potřeby. Kratší klipy potřebují méně paměti a času; větší GPU jich mohou pojmout více.

## Upozornění k licenci modelu
**VideoTurko obsahuje jen záplaty a skripty (MIT); kdo používá model a jeho výstupy, odpovídá za licenci MiniMax sám.** Nejde o právní poradenství. Níže jsou body MiniMax H3 Community License (2. srpna 2026) ve shrnutí s čísly; závazná je samotná licence: https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/LICENSE

Tento repozitář NEOBSAHUJE žádné váhy modelů (žádné soubory MiniMax H3, GGUF HyperFlow-H3-Flash ani VAE). Projekt není s MiniMax spojen ani jí podporován. Komerční použití NENÍ zakázáno (nejde o nekomerční licenci); podmínky jsou níže.

**Území (Applicable Territory)**
- **Preambule, I.3, I.5:** celý svět, S VÝJIMKOU Evropské unie, Spojeného království, Korejské republiky a Spojených států. Používání modelu se považuje za přijetí licence.
- **II:** bezplatná, nepřenosná, omezená licence k používání, rozmnožování, šíření, vytváření odvozených děl a úpravám, pouze na území a v souladu se smlouvou a Exhibit A. Osoby na vyloučených územích mohou požádat MiniMax o samostatnou licenci.
- **V.4:** používání, rozmnožování, úpravy, šíření nebo zobrazování modelu, jeho odvozenin A VÝSTUPŮ (vygenerovaného videa a zvuku) mimo území není povoleno. **Zveřejňování nebo předvádění vygenerovaných videí v EU, Spojeném království, Jižní Koreji a USA je tedy mimo licenci.**
- **Exhibit A-1:** použití mimo území porušuje Acceptable Use Policy.

**Šíření (III)** (tento repozitář model nešíří; pokud jej šíříte vy)
- **III.1:** každému příjemci předejte kopii licence. **III.2:** upravené soubory označte nápadným upozorněním.
- **III.3:** Doporučeno (není povinné): upozornění "Powered by MiniMax H3", identifikátor AI generování na vytvořených souborech, veřejný popis práce.
- **III.4:** k šířené kopii MUSÍ být přiložen soubor NOTICE s textem: "MiniMax H3 is licensed under the MiniMax H3 Community License Agreement, Copyright © 2026 MiniMax. All Rights Reserved."
- **Exhibit A-12:** zveřejňování obsahu v jakémkoli veřejném prostředí bez jasného uvedení, že je generován strojově, je zakázáno: videa vygenerovaná AI při zveřejnění označte (úplný seznam: `docs/LISANS_UYARISI.md`).
- **III (poslední odstavec):** ke svým úpravám můžete přidat vlastní autorská práva, ale nesmíte stanovit dodatečné ani odlišné podmínky používání a šíření; územní pravidla platí dál.

**Komerční podmínky (IV)**
- **IV.1:** pokud vaše komerční produkty či služby generují více než 20 milionů USD (nebo ekvivalent) ročního obratu, získejte PŘEDEM písemné svolení na adrese api@minimax.io (předmět "MiniMax H3 licensing - authorization request").
- **IV.2:** v uživatelském rozhraní komerčního produktu či služby využívající model musí být nápadně uvedeno "MiniMax H3".

**Omezení použití (V)**
- **V.1:** dodržujte platné právo (včetně obchodní compliance) a Exhibit A. **V.2:** každého, komu zpřístupníte model, zavažte podmínkami alespoň tak ochrannými, jako jsou tato omezení, a informujte jej.
- **V.3:** model ani jeho VÝSTUPY nesmíte používat ke zlepšování jiného AI modelu (kromě MiniMax H3 a jeho odvozenin). (I.11: destilace a trénování na syntetických výstupech činí model „odvozeninou“; samotné výstupy odvozeninami nejsou.)
- **V.5:** pokud třetím stranám nabízíte produkt, službu nebo hostovanou službu, která pomocí modelu generuje výstupy: před spuštěním i po celou dobu provozu jsou nutná přiměřená technická a organizační opatření, mechanismus hlášení, neprodlené prošetření a odstranění, vypnutí či pozastavení opakovaných porušitelů.

**Ochranné známky a práva (VI)**
- **VI.1:** odvozená díla a odvozené modely, které vytvoříte, vlastníte vy (s výhradou práv MiniMax). **VI.2:** názvy a značky MiniMax nejsou licencovány (nad rámec toho, co je nutné k popisu a šíření); značku "MiniMax H3" lze použít jen k splnění III.3, na území; nenaznačujte spojení s MiniMax.
- **VI.3:** pokud žalujete MiniMax nebo kohokoli s tvrzením, že materiály či výstupy porušují vaše práva, všechny vaše licence zanikají týž den; MiniMax bráníte a odškodňujete ji vůči nárokům třetích stran vzniklým z vašeho nebo cizího použití a šíření.
- **VI.4:** MiniMax si na výstupy nenárokuje žádná práva; vy a vaši uživatelé odpovídáte za výstupy a jejich použití.

**Vyloučení záruk a zánik (VII, VIII, IX)**
- **VII.1:** žádná povinnost podpory ani aktualizací. **VII.2:** model a výstupy jsou poskytovány "AS IS", bez záruk; o vhodnosti rozhodujete vy a riziko nesete vy. **VII.3:** MiniMax a přidružené osoby neodpovídají za žádné škody (v rozsahu, který právo dovoluje).
- **VIII.1:** účinnost nastává přijetím nebo získáním přístupu. **VIII.2:** při porušení může MiniMax licenci ukončit; musíte přestat model používat a šířit, smazat kopie a informovat příjemce (VI.1, VI.3, VII, IX zůstávají v platnosti).
- **IX:** právo Zvláštní správní oblasti Hongkong; výhradní příslušnost hongkongských soudů (Úmluva OSN CISG vyloučena).
- **Dodatečná poznámka:** enkodér MiniMax H3 používá Qwen3-VL-32B (Apache 2.0).

**Zásady přijatelného použití (Exhibit A)** (model, odvozeniny ani výstupy NEPOUŽÍVEJTE k následujícímu)
- A-1 použití mimo území; A-2 porušování zákonů nebo duševního vlastnictví třetích stran; A-3 způsobení újmy sobě nebo druhým; A-4 přeúčelování či šíření výstupů ke škodě; A-5 obcházení ochranných opatření; A-6 vykořisťování nebo poškozování nezletilých; A-7 prokazatelně nepravdivé informace ke škodě druhých nebo k ovlivnění voleb; A-8 falešná online aktivita (falešné recenze apod.); A-9 pomluva, očerňování, obtěžování; A-10 malware; A-11 osobní údaje ke škodě druhých; **A-12 zveřejňování obsahu v jakémkoli veřejném prostředí (včetně příspěvků botů) bez jasného a nápadného uvedení, že je generován strojově**; A-13 vydávání se za jinou osobu bez souhlasu; A-14 automatizovaná rozhodnutí s vysokým rizikem v kritických oblastech (vymáhání práva, imigrace, zdraví, kritická infrastruktura, úvěry, zaměstnání, bydlení, vzdělávání, sociální scoring, pojištění apod.); A-15 porušování společenských, etických a morálních norem jiných zemí a regionů; A-16 násilný extremismus a terorismus; A-17 diskriminace nebo újma na základě chráněných charakteristik; A-18 vykořisťování zranitelných skupin; **A-19 vojenské účely**; A-20 neoprávněná nebo nelicencovaná odborná činnost (finanční, právní, lékařská apod.).
- Poznámka: jde o shrnutí srozumitelným jazykem; v případě pochybností rozhoduje anglický text licence.

## Štítky důkazů

Jedna sada pro všechny dokumenty (starší zápisy v závorkách):
- **[změřeno]** (TR: ölçtüm, olctum): provedeno v tomto projektu, cesta k důkazu existuje.
- **[přečteno]** (TR: okudum yol, okudum): zdroj nebo skript byl přečten, nespuštěn.
- **[dle návrhu]** (TR: tasarım, tasarim): navrženo, ve skutečném běhu zatím neviděno.
- **[odhad]** (TR: tahmin): neověřeno.
- **[nezkoušeno]** (TR: denenmedi): nikdy nespuštěno.
- **[hlášeno uživatelem]** (TR: kullanıcı bildirdi): uvedl uživatel, s datem; nezávisle neměřeno.
- **[vypočteno]** (TR: hesap; starší zápisy: calculated, hesap): číslo odvozené z naměřených vstupů, samo neměřené; odvození je napsáno vedle něj. [proposal] / [öneri] ve starším textu = [odhad].

Názvy běhů použité v hranatých závorkách (naše vlastní názvy, nejsou to soubory tohoto repozitáře): U209 = 209 snímků s vydanou binárkou přes `uret.ps1`; B209 a B192 = běhy „obrázek na video“ (`-InitImg`) na 209 a 192 snímcích; B56VT2 = vydaná binárka, 56 snímků, porovnáno s bajtovou referencí R0 pro 56 snímků; F209b, F209V2, F209V2K = běhy na 209 snímků na vývojovém sestavení (podrobnosti: `docs/OLCUMLER.md`).

## Známá omezení
- **Bajtový důkaz** (jak jej sami zopakovat: `docs/KANITLAR.md`, „R0 ve latent referansi nasil uretilir“; ověřeno na naší kartě sm_61, jiná GPU nemusí dávat bajtovou shodu [odhad]): s naší sérií záplat (paměťové přepínače zapnuty) dal běh na 56 snímků sha256 `0979f156d548169b...`, shodný s referencí [změřeno]; při 141 snímcích byl sha256 latentu `E5D028F8632BE4FE...` shodný (s přepínači 0013/0014). Pro snímky 158 až 209 přímá bajtová reference neexistuje; důkazem je řetězec kontrol. Úspěšné číselné kontroly nezaručují dobrý klip: konzistence pohybu v čase se kontroluje okem (viz `docs/KAPILAR.md`).
- **209 snímků, která sada přepínačů:** důkaz bajtového řetězce pro 209 snímků byl pořízen se sadou přepínačů F209V2 na vývojovém sestavení (bez přepínačů konce bloků, sestaveno bez záplat 0019/0020); `uret.ps1` tento postup pro 209 snímků používá [přečteno: skript; skutečný běh enginu přes `uret.ps1` prošel v běhu U209].
- Ověřeno na jedné kartě (GTX 1050 Ti 4 GB); jiné karty jsme nezkoušeli.
- **Která binárka byla měřena:** latent při 141 snímcích a bajtový řetězec byly změřeny na našich vývojových sestaveních. Vydaná binárka, kterou stahujete, je sestavena znovu: její bajtová kontrola na 56 snímcích prošla (další bod) a běh na 209 snímků přes `uret.ps1` prošel kontrolou (běh U209, 3414 s, špička VRAM 3777 MiB) [změřeno]; vůči běhu na 209 snímků na vývojovém sestavení je latent shodný bajt po bajtu; ve videu jsou snímky (md5) a zvuk shodné, sha256 souboru AVI se liší kvůli kontejneru [změřeno] (viz `docs/OLCUMLER.md`, oddíl 0).
- **Vydaná binárka, 56 snímků:** vydaná binárka (sd-cli `c5cebe78...`, stable-diffusion.dll `e5d3d329...`) dala výsledek na 56 snímků shodný bajt po bajtu s R0 (sha256 `0979f156d548169be03acd1a9d7617102a75333aa48a28d6bbfd1cc5fa3f604d`; md5 každého snímku a zvuk shodné), spuštěno přímo s výchozími přepínači (bez proměnných `SD_*`), návratový kód 0, 601 s [změřeno: běh B56VT2, 2026-11-19; důkazy uchovávají autoři, v tomto repozitáři nejsou]. Rozsah: jen naše karta sm_61 a 56 snímků; nejde o test instalace v čisté složce; latent při 141 snímcích a řetězec pro 209 byly změřeny se starší binárkou a s touto NEBYLY zopakovány [nezkoušeno]. První pokus (B56VT, přes pomocný skript) skončil bez hlášky po 58 s, příčina neznámá [odhad: nedostatek paměti]; druhý pokus spustil `sd-cli` přímo.
- Instalační a spouštěcí skripty zatím nebyly ověřeny z prázdné složky (test v čisté složce teprve čeká).
- Plán a další kroky: `ROADMAP.md`.

## Stav a omezení
- Ověřeno na jednom počítači (GTX 1050 Ti 4 GB, 16 GB RAM, i7-7700HQ). Jiné karty se 4 GB a jiné velikosti RAM se mohou chovat odlišně.
- **Výchozí 209 snímků (8.7 s):** prošlo našimi kontrolami kvality (šum 1.08, běh F209V2K) [změřeno: 209 snímků s vydanou binárkou přes `uret.ps1`, běh U209; latent shodný bajt po bajtu s během na vývojovém sestavení; snímky a zvuk ve videu shodné, sha souboru se liší kvůli kontejneru; důkazy uchovávají autoři, v tomto repozitáři nejsou]. Při 209 snímcích byla špička VRAM u DiT 3777 MiB ze 4096 MiB (běhy F209b a U209; údaj `nvidia-smi` za celou kartu), malá rezerva: jiné zatížení GPU (displej, další aplikace) může způsobit selhání u `blocks.0`; testováno jen na GTX 1050 Ti. Stav displeje během toho běhu nebyl zaznamenán; pokud displej běží na této kartě, je k dispozici méně VRAM [odhad: zátěž displeje ve Windows asi 100-300 MB]; v případě potřeby připojte displej k integrované grafice [rada, nezkoušeno]. Vzorkování (sampling) trvalo 2730 s (běh U209: kroky po 436-483 s) a dekódování VAE v samostatném procesu 173 s (etapa 2 celkem 193 s se zvukovým dekódováním) [změřeno: vydaná binárka v U209; starší běhy na vývojovém sestavení: 2664 s a 174 s]. V etapě 1 došla VAE v hlavním procesu paměť a přešla na časové dlaždicování (320 s); tento výstup se zahazuje, video pochází z etapy 2 bez dlaždicování. Špička RAM v U209 nebyla měřena. Klipy delší než 209 snímků nejsou součástí tohoto vydání.
- **Obrázek na video (`-InitImg`):** s vstupním obrázkem je na tomto GPU strop 192 snímků (8.0 s při 24 fps): 209 snímků se nevešlo (u bloku 0 chybělo asi 17.5 MB VRAM: potřeba 2587 MB, k dispozici 2570 MB); 192 snímků prošlo přes `uret.ps1` za 3086 s se špičkou VRAM 3783 MiB, kontrola prošla [změřeno: běhy B209 a B192, 2026-11-20, jedna scéna; důkazy uchovávají autoři, v tomto repozitáři nejsou]. Na jiných GPU nezkoušeno [nezkoušeno].
- **Na volné RAM záleží:** potřebujete asi 11 GB VOLNÉ RAM (proces enginu drží asi 11 GB) [změřeno]. Při příliš malé volné RAM může proces skončit bez chybové hlášky [odhad: jednou jsme to pozorovali při asi 300 MB volné RAM, když `sd-cli` držel asi 10 GB]. Za běhu neotevírejte další velké programy: na počítači s 16 GB zůstane volných jen asi 0.3-0.5 GB a při nedostatku paměti může běh tiše zahynout. Před spuštěním zavřete prohlížeče, hry a další velké programy a zkontrolujte volnou RAM.
- **Test v čisté složce teprve čeká:** instalační a spouštěcí skripty zatím nebyly ověřeny z prázdné složky jen podle těchto pokynů; oddíl bude aktualizován, až bude tento test (včetně bajtového porovnání 56 snímků s referencí) zaznamenán.
- Vygenerovaná videa zde nejsou dodávána.

<!-- i18n-source: README.md sha256:a72e4a0b2471 -->
