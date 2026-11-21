# VideoTurko

[English](README.md) · [Türkçe](README.tr.md) · [简体中文](README.zh-CN.md) · [日本語](README.ja.md) · [Español](README.es.md) · [Русский](README.ru.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [العربية](README.ar.md) · [Português (BR)](README.pt-BR.md) · [Italiano](README.it.md) · [한국어](README.ko.md) · [हिन्दी](README.hi.md) · [Bahasa Indonesia](README.id.md) · [Tiếng Việt](README.vi.md) · [Polski](README.pl.md) · Nederlands · [Українська](README.uk.md) · [فارسی](README.fa.md) · [עברית](README.he.md) · [ไทย](README.th.md) · [বাংলা](README.bn.md) · [اردو](README.ur.md) · [Ελληνικά](README.el.md) · [Čeština](README.cs.md) · [Română](README.ro.md) · [Magyar](README.hu.md) · [Svenska](README.sv.md) · [Azərbaycanca](README.az.md) · [Bahasa Melayu](README.ms.md)

De vertalingen volgen deze Engelse README. Als een vertaling afwijkt of achterloopt, geldt de Engelse tekst, vooral voor de licentie- en beveiligingstekst ([`SECURITY.md`](SECURITY.md) en [`docs/LISANS_UYARISI.md`](docs/LISANS_UYARISI.md) worden alleen in het Engels en Turks bijgehouden).

![Windows](https://img.shields.io/badge/Windows-10%2F11-blue) ![GPU](https://img.shields.io/badge/NVIDIA-4%20GB%20(sm__61)-76b900) ![License](https://img.shields.io/badge/code-MIT-green) ![Status](https://img.shields.io/badge/status-clean--root%20test%20pending-orange)

> **Voor je begint (licentie, gebied):** deze repository is MIT en bevat alleen patches en scripts. Het MiniMax H3-model dat ze downloadt valt onder de MiniMax H3 Community License: het geldigheidsgebied sluit de Europese Unie, het Verenigd Koninkrijk, Zuid-Korea en de Verenigde Staten uit, en het model, afgeleide werken **en uitvoer (de video’s die je genereert)** mogen daar niet worden gebruikt, verspreid of getoond (V.4). Commercieel gebruik is toegestaan binnen de licentievoorwaarden. Lees [`docs/LISANS_UYARISI.md`](docs/LISANS_UYARISI.md) vóór de installatie; dit is geen juridisch advies.

> **In 30 seconden:** een videokaart met 4 GB kan in één pass een MiniMax H3-video van 209 frames (8,7 s) maken: geverifieerd op één machine (GTX 1050 Ti 4 GB; een volledige `kur.ps1`-installatie in een lege map is nog niet end-to-end geverifieerd) [gemeten: 209 frames met de release-binary via `uret.ps1`, run U209; latent byte-identiek aan de run met de ontwikkelbuild; frames en audio in de video identiek, de sha van het bestand verschilt door de container; het bewijs wordt bewaard door de auteurs, niet in deze repo]; met `-InitImg` (image-to-video) maximaal 192 frames (8,0 s) [gemeten: run B192]; 209 frames duren ongeveer 57 min, de standaard tijdslimiet is 80 min [gemeten: run U209]; de 3 stappen hieronder laten zien hoe je het draait.

VideoTurko: geheugenpatches voor stable-diffusion.cpp en recepten om MiniMax H3 text-to-video op een GTX 1050 Ti van 4 GB te draaien, tot 209 frames (8,7 s) in één pass; image-to-video (`-InitImg`) tot 192 frames (8,0 s) (209 frames geverifieerd via een bytereeks; byte-identiek aan de run zonder patches bij de controles met 56 en 141 frames).

## Snel starten (Windows, 3 stappen)
**Status: de installatie- en runscripts hieronder worden nog afgerond en de clean-root-test staat nog open; er wordt niets beweerd over de werking totdat die test geslaagd is (zie "Status en grenzen").**

1. **Download** deze repository (groene knop **Code**, dan **Download ZIP**) en pak hem uit in een KORTE map, bijvoorbeeld `C:\vt`.
2. **Installeren: dubbelklik op `kur.cmd`** (er opent een zwart venster dat elke stap toont; sluiten stopt de installatie, opnieuw uitvoeren gaat verder waar het bleef: een half gedownload modelbestand wordt hervat [gelezen: het downloadscript bewaart een `.part`-bestand en gaat daarvandaan verder; een volledige hervatting van 29 GiB is niet gemeten]). Waarschuwt Windows voor het gedownloade bestand, gebruik dan het PowerShell-commando hieronder [advies, niet getest met een gedownloade ZIP]. Liever de opdrachtregel? Open PowerShell in die map (typ `powershell` in de adresbalk van Verkenner) en voer dezelfde installatie uit:
   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File scripts\kur.ps1
   ```
   De installatiemap is de map die je hebt uitgepakt (de engine komt in `engine\bin`, de modellen in `model`); wil je een andere plek, zet dan eerst de omgevingsvariabele `VT_ROOT`. Het script controleert GPU, driver, RAM en schijf, haalt de engine en de modellen op (engine-zips en nieuw gedownloade modelbestanden worden met sha256 gecontroleerd; een modelbestand dat al aanwezig is met de juiste grootte wordt alleen op grootte gecontroleerd, `scripts\modelleri_indir.ps1 -Dogrula` voert de volledige sha256-controle uit), doet een korte echte controle en toont READY alleen als die controle geslaagd is [ontwerp: `kur.ps1` is nog niet volledig uitgevoerd in een schone map; deze zin wordt bijgewerkt na de test in een schone map]. `-ExecutionPolicy Bypass` geldt alleen voor dit ene proces; lees `scripts\kur.ps1` eerst, zoals bij elk installatieprogramma.
   De engine-zip komt uit de GitHub-release v0.1.0 (gepubliceerd op 2026-11-19; de sha256 ervan staat vast in `kur.ps1`). Offline of met een eigen build geef je lokale zips mee: `-MotorZip <path> -CudaZip <path>`. Een lokale zip wordt tegen dezelfde vastgezette sha256 gecontroleerd (een `.sha256`-bestand ernaast wordt genegeerd), dus het moet de release-zip zijn; voor een eigen build zet je eerst `VT_MOTOR_SHA256` / `VT_CUDA_SHA256` op de sha256 ervan. Een onjuiste sha256 stopt met exit 1. Alleen `.exe`/`.dll` gaan naar `engine\bin`; licenties en README gaan naar `engine\lisanslar\<zip name>\`. [vóór de release geprobeerd met de dist-zips: het sidecar-bestand `.sha256` plus de waarschuwing dat het naar zichzelf verwijst, binary en DLL's geplaatst, `sd-cli --help` draaide; de sha's van de geïnstalleerde binaries kwamen overeen (`c5cebe78...`, `e5d3d329...`); de modelstap en de 5-frame-controle van `kur.ps1` zijn nog NIET op een echte GPU uitgevoerd]
   **Modellicentie:** vóór de modelstap toont het installatieprogramma de samenvatting van de licentie (`docs/LISANS_KABUL.txt`, volledige tekst `docs/LISANS_UYARISI.md`: MiniMax H3 Community License, gebiedsbeperkingen die ook voor gegenereerde video's gelden, regels voor commercieel gebruik en AI-labels) en vraagt of je akkoord gaat (`E` = ja). Lees die eerst. Voor onbeheerde runs kun je `-LisansKabul E` meegeven; dat betekent dat je de licentie zelf hebt gelezen en geaccepteerd; voeg het niet toe namens iemand anders. (AI-agents: volg `AGENTS.md`; typ nooit E zonder toestemming van de gebruiker.) Zonder acceptatie stopt `kur.ps1` met exitcode 2 en downloadt geen model.
3. **Je eerste video (56 frames, ongeveer 11 min op onze GTX 1050 Ti** [gemeten: 641 s, run R0, `docs/OLCUMLER.md`; andere kaarten niet gemeten]**)**: wanneer het installatieprogramma `HAZIR / READY` afdrukt, voer uit
   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File scripts\uret.ps1 -Istem docs\ornek_istem_R0.txt -Kare 56
   ```
   (snelkoppeling: sleep een prompt-tekstbestand op `uret.cmd`, of voer `uret.cmd docs\ornek_istem_R0.txt` uit: dezelfde run van 56 frames). De video staat in `runs\`. Schrijf daarna je eigen prompt in een tekstbestand (één Engelse alinea, optionele `audio:`-zin) en draai de langste clip die we dekken (standaard, ongeveer 57 min [gemeten: run U209]):
   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File scripts\uret.ps1 -Istem istem.txt -Kare 209
   ```
   `-Kare` volgt het 17k+5-raster (56, 73, ... 192, 209); standaard 209 (8,7 s), de langste lengte die we afdekken. De VAE draait in een apart proces, nooit getiled [een echte engine-run via `uret.ps1` met de release-binary, VAE in apart proces, geslaagd in run U209].

   Gids voor het schrijven van een prompt: [`docs/ISTEM_YAZIMI.md`](docs/ISTEM_YAZIMI.md) (patroon van één ononderbroken opname, gelijke tijdvakken, twee volledige voorbeelden).

| Vereiste | Waarde |
|---|---|
| Besturingssysteem | Windows 10/11, 64-bit |
| GPU | NVIDIA, 4 GB of meer; alleen getest op GTX 1050 Ti (sm_61); kleine marge (3777/4096 MiB bij 209 frames): een drukke desktop of browser kan de run laten mislukken; geen andere 4 GB-kaart geprobeerd |
| RAM | 16 GB (piek ongeveer 11 GB; sluit andere programma's) |
| Schijf | minstens 32 GiB vrij (40 GiB of meer aanbevolen: tussen 32 en 40 toont het installatieprogramma een waarschuwing, `[VT-W-DISK-PAY]` [gemeten: `-Kuru`-runs met gesimuleerde schijf]), modellen op een SSD (bij voorkeur NVMe) |
| Download | engine-zip 36,8 MB + CUDA-runtime-zip 567,5 MB [gemeten] + modellen 31.473.112.040 bytes (ongeveer 29,3 GiB) [gelezen: groottes in `scripts/modeller.json`]; in totaal ongeveer 30 GiB |
| Modellen | niet meegeleverd; worden door het installatieprogramma opgehaald onder de MiniMax-licentie (zie waarschuwing hieronder). De modellen (29,3 GiB, 31.473.112.040 bytes in `scripts/modeller.json`) staan niet in deze repository of release: de limieten van GitHub voor bestands- en releasegrootte gelden, en `kur.ps1` downloadt ze van de officiële bron met sha256-verificatie. |

Exitcodes van `kur.ps1`: 0 READY, 1 fout, 2 invoer van de gebruiker nodig (licentie, of nog geen release/zip), 3 hardware of schijf onvoldoende, 4 gestopt (DUR-bestand). `uret.ps1` accepteert een run alleen als het `.avi`-bestand bestaat, het aantal frames klopt en de logs schoon zijn [gemeten: één echte run via `uret.ps1` met de release-binary, run U209, 209 frames, poort geslaagd]. Exitcodes van `uret.ps1`: 0 DONE (kwaliteitspoort geslaagd), 1 fout of ongeldige uitvoer (inclusief een video zonder audiostream), 2 gestopt (DUR-bestand), 5 `KAPI RED` (kwaliteitspoort niet gehaald: clip niet geaccepteerd, de beslissing is aan jou), 6 poort kon niet draaien (clip niet geaccepteerd). Details in AGENTS.md. [gemeten: exitcodes 0, 1 (stille video), 5 en 6 in scenario's met een nep-engine en een nep-poort; echte engine: exit 0 in run U209]

### Problemen oplossen (details: `docs/SIK_HATALAR.md`)
Foutregels van onze scripts dragen een vaste code, bijvoorbeeld `HATA: [VT-E-DLL] ...` of `UYARI: [VT-W-DISK-PAY] ...`. Zoek de code op in [`docs/SIK_HATALAR.md`](docs/SIK_HATALAR.md) (ankervoorbeeld `#vt-e-dll`) of in `docs/hata_imzalari.json` en zet de code in je issue. De eerste kolom van de tabel hieronder blijft zoals afgedrukt (vertaal codes en logtekst niet).

| Wat je ziet | Wat het betekent, wat je doet |
|---|---|
| `STATUS_DLL_NOT_FOUND` / `cudart64_12.dll not found` (#13) | Start `sd-cli.exe` niet met de hand; voer `scripts\kur.ps1` uit, dat de CUDA-DLL's op hun plek zet. |
| `failed during weight preparation` bij `blocks.0` (#1, #3, #5) | Te weinig VRAM bij de geheugenpoort: gebruik een kleiner aantal frames op het 17k+5-raster, sluit andere GPU-programma's, houd de meegeleverde vlaggen aan. |
| `retrying with temporal tiling` (#6) | De VAE viel terug op tiling; de uitvoer is ongeldig voor kwaliteitsdoeleinden. Draai opnieuw. |
| Run eindigt bij de tijdslimiet, geen video (#7) | Verhoog `-TavanDk` voor lange clips (standaard tijdslimiet: 80 min voor 209 frames, ingesteld door `uret.ps1`; onze run van 209 frames duurde 57 min [gemeten: run U209]). |
| Exitcode leeg maar "finished" (#14) | De wrapper las de exitcode te vroeg; draai opnieuw en controleer of het videobestand bestaat. |
| Systeem wordt traag, swapping (#18) | De engine gebruikt ongeveer 10-11 GB RAM; sluit browsers en andere programma's. |
| sha256-mismatch / download mislukt | Meestal een onderbroken download: voer dezelfde opdracht opnieuw uit, geverifieerde bestanden worden overgeslagen. |

**Vast of nieuwsgierig?** [`SUPPORT.md`](SUPPORT.md) (waar je vragen stelt; reactietijden zijn doelen, geen toezeggingen) · [`PRIVACY.md`](PRIVACY.md) (geen telemetrie; het netwerk wordt alleen gebruikt om de engine en modellen te downloaden, van de vermelde hosts) · [`SECURITY.md`](SECURITY.md) (privémelding) · [`CONTRIBUTING.md`](CONTRIBUTING.md) (eerste pull request in 5 stappen; voor documenten en scripts is geen GPU nodig).

### Nieuw in v0.1.1: meer opties (details: `AGENTS.md`, `docs/SIK_HATALAR.md` 19-23)
Zonder deze opties verandert er niets op een kaart van 4 GB (de bytecontrole van 56 frames tegen onze referentie is met v0.1.1 opnieuw geslaagd [gemeten]). Zet `-Kuru` achter een willekeurige opdracht om te zien wat er zou draaien.
- `-EndImg`: geef ook het laatste frame mee (eerste en laatste frame, "FLF"); maximaal 175 frames op kaarten onder 8 GB (192 paste niet op 4 GB), 192 op kaarten van 8 GB en meer. Op onze GTX 1050 Ti draait dit altijd in twee processen: 56 frames 1040 s, 175 frames 2887 s (48 min), beide slaagden voor de poort [gemeten]. Tips voor de prompt: `docs/ISTEM_YAZIMI.md`.
- `-W` / `-H`: andere formaten, bijvoorbeeld staand 384x640; veelvouden van 32, oppervlak minstens 640x384 (nooit kleiner). Niet getest op 4 GB; op kaarten onder 8 GB worden formaten geweigerd die groter zijn dan onze grootste gemeten run. De drempels van de kwaliteitspoort zijn gekalibreerd op 640x384.
- `-TekAsama`: één proces in plaats van twee, alleen voor grote kaarten; wordt nooit automatisch ingeschakeld.
- Nieuwere GPU's (compute capability 7.0+, bijv. RTX 20/30/40): `GGML_CUDA_CUBLAS_COMPUTE_TYPE=f32` wordt automatisch gezet, tenzij je het zelf instelt; dit verhielp een volledig zwarte video bij 141 frames of meer op de RTX 4070 Ti van de melder [gemeld door gebruiker, issue #1]. Zonder Python + OpenCV stopt `uret.ps1` nu vóór de GPU-taak met exit 6 (geen video gemaakt, geen misleidende RED).
- Dank aan @SinanC73 voor het rapport over de RTX 4070 Ti dat tot deze wijzigingen leidde ([issue #1](https://github.com/alexturkey/VideoTurko/issues/1)).

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

## Welke kaart heb ik? (alleen links)

De waarde van deze repo zijn de patches die het model in 4 GB laten passen, plus de kwaliteitspoorten. Voor andere kaarten is de kant-en-klare stable-diffusion.cpp CUDA-release een OPTIE: wij hebben die niet gemeten en onze kwaliteitspoorten zijn er niet op uitgevoerd. Onze eigen metingen betreffen één kaart (GTX 1050 Ti 4 GB). Al het andere zijn meldingen uit de community: we linken ernaar en staan er niet voor in.

| Uw opstelling | Waar kijken | Bewijs |
|---|---|---|
| GTX 1050 Ti 4 GB (onze release-zip) | deze README, `docs/OLCUMLER.md` | [gemeten] |
| Andere NVIDIA-kaarten (compute capability 7.0+: RTX 20/30/40) | `docs/KART_PROFILLERI.md` (`uret.ps1` zet `f32` automatisch aan; kant-en-klare stable-diffusion.cpp CUDA-release: een optie, door ons niet gemeten [niet geprobeerd]) | [gemeld door gebruiker] |
| RTX 50-serie | `docs/KURULUM.md`, `docs/RTX5060_TEST_RAPORU.md` | [gemeld door gebruiker, PR #3] |
| AMD / non-NVIDIA | `docs/AMD_ROCM.md` (community-notitie, niet officieel ondersteund; de release-engine is CUDA) | [gemeld door gebruiker, PR #4] |
| Een langere film van meerdere clips | `docs/KLIP_ZINCIRI.md`, `scripts/zincir.py` | [gemeld door gebruiker]; kwaliteit van aaneengeschakelde films door ons niet gemeten [niet geprobeerd] |

Licentie: het accepteren van de MiniMax H3-licentie (`docs/LISANS_KABUL.txt`) geldt op elke route; de acceptatiestap van `kur.ps1` draait niet met de kant-en-klare release.

## Wat dit is
Een set kleine geheugen- en planningspatches voor stable-diffusion.cpp, plus het runrecept, de controles en de metingen waarmee MiniMax H3 (33B DiT; wij draaien de HyperFlow Flash 13.7B Q4_K_M GGUF; de Qwen3-VL-tekstencoder van 32B staat apart) op een Pascal-GPU van 4 GB (GTX 1050 Ti, 16 GB systeem-RAM) kan draaien.
- Lengtes in één pass die we echt hebben gemaakt en die onze kwaliteitspoorten hebben gehaald: 56, 141, 158, 175, 192, 209 frames op 640x384, 24 fps (209 frames = 8,7 s), met de eigen gegenereerde audio van H3 [gemeten: 209 frames met de release-binary via `uret.ps1`, run U209; latent byte-identiek aan de run met de ontwikkelbuild; frames en audio in de video identiek, de sha van het bestand verschilt door de container; het bewijs wordt bewaard door de auteurs, niet in deze repo]. 209 is de langste lengte die we hebben bekeken en vloeiend vonden [gemeld door gebruiker, 2026-11-19, video volledig bekeken; bestand: uitvoer F209V2, 8,708 s].
- **Byte-identiek, eerlijk afgebakend:** uitvoer is alleen voor 56 en 141 frames byte-identiek bevonden aan de referentie zonder patches. Voor 158/175/192/209 frames gebruikten we dezelfde vlaggen en dezelfde binaryketen; er is geen directe bytereferentie (de build zonder patches kan die lengtes op deze GPU niet draaien).
- Kwaliteitsinstellingen worden nooit verlaagd: hetzelfde model en dezelfde quantisatie, 6 stappen, cfg 1, 640x384, dezelfde seed, VAE zonder tiling.
- We beweren niet de eerste te zijn: we hebben gezocht en vonden geen extern voorbeeld hiervan op 4 GB, wat geen bewijs is dat er geen bestaat.

## Indeling
- `patches/` patches tegen een vastgepinde commit van stable-diffusion.cpp (zie de notities daar)
- `scripts/` build, run, VAE in apart proces, hulpmiddelen voor poort en consistentie (`doku_norm.py`: zie de opmerking over de schaal hieronder)
- `docs/KURULUM.md` hardware, build en run-stappen (EN+TR)
- `docs/YAMALAR.md` lijst van patches, `docs/KANITLAR.md` bewijs, `docs/KAPILAR.md` tabel met kwaliteitspoorten, `docs/OLCUMLER.md` metingen, `docs/SIK_HATALAR.md` veelgemaakte fouten, `docs/LISANS_UYARISI.md` alle licentiepunten
- `scripts/` korte index: `hiz_kos3.ps1` run-wrapper (`-Kuru` toont de exacte opdracht), `uretim_kapi.ps1` kwaliteitspoort, `dikis_denetim.py` naadcontrole, `doku_norm.py` textuurgenormaliseerde ruis, `bayt_kiyas.py` bytevergelijking, `derleme_sablonu.ps1` buildsjabloon (stopt alleen de telemetriehelper van Visual Studio, `vctip.exe`, die na het begin van de eigen build is gestart en anders het buildproces minutenlang vasthoudt; andere `vctip.exe`-processen blijven met rust gelaten)

## Kwaliteitspoorten (hoe een resultaat wordt geaccepteerd)

Deze poort controleert de bewegingsconsistentie (sprongen in schaal of positie van objecten) niet: bekijk de hele video voordat je hem accepteert.
1. Aantal frames en audio aanwezig; geen geheugenfallback of ALLOC_FAILED-regels in de log.
2. Poort voor ruwe ruis: residu van het medianfilter <= 1,5 (schaal 0-255).
3. Textuurgenormaliseerde ruis, `scripts/doku_norm.py` (de versie van deze repo): N = mediaan van het residu / Sobel-textuur, elk 6e frame. **Opmerking over de schaal:** in deze versie geven de 10 gemeten clips N = 0,034-0,052 (tabel in `docs/KAPILAR.md`; het laatste kwart van F192/F209V2 komt op 0,062) en de drempel van de extra poort is N <= 0,065. Een andere implementatie mat 0,028-0,036 op dezelfde clips, dus drempels zijn NIET uitwisselbaar tussen versies. Bij zeer fijne texturen (rijen gras) was een schone N 0,075, dus de drempel geldt per scènefamilie. Een robuuste hoogfrequentieschatter (sigma-HH <= 1,5; schoon 0,74-1,19, toegevoegde ruis s=2 geeft 2,2-3,0) is de aanbevolen extra poort.

Reikwijdte: VideoTurko gaat over ÉÉN enkele doorgang (tot 209 frames, ongeveer 8,7 s). Onze eigen test met aaneenschakelen liet zichtbare naden zien (de scène loopt niet netjes door), dus langere films horen niet bij wat wij verifiëren. Voor aaneenschakelen is er de community-gids `docs/KLIP_ZINCIRI.md` en onze hulptool alleen voor CPU `scripts/zincir.py` (`plan`, `son-kare`, `bagla`; hij start de engine nooit); de kwaliteit van aaneengeschakelde films hebben we niet gemeten [niet geprobeerd], controleer dus elke naad met het oog en met `scripts/dikis_denetim.py`.
Je instellingen zijn van jou: 209 frames is onze geteste standaard op een kaart van 4 GB, geen grens die je moet aanhouden. Kies elk aantal frames op het 17k+5-raster (56, 73, ... 192, 209; zie `docs/KURULUM.md`), pas de prompt, seed, resolutie of elke vlag aan zoals je wilt. Kortere clips vragen minder geheugen en tijd; grotere GPU's kunnen er meer in kwijt.

## Waarschuwing over de modellicentie
**VideoTurko bevat alleen patches en scripts (MIT); wie het model en de uitvoer ervan gebruikt, is zelf verantwoordelijk voor de MiniMax-licentie.** Geen juridisch advies. Hieronder staan de bepalingen van de MiniMax H3 Community License (2 augustus 2026) samengevat met hun nummers; de licentie zelf is bindend: https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/LICENSE

De MIT-licentie van deze repository dekt de modelgewichten niet; zie [`NOTICE`](NOTICE). Deze repo bevat GEEN modelgewichten (geen MiniMax H3-, HyperFlow-H3-Flash-GGUF- of VAE-bestanden). Dit project is niet verbonden aan MiniMax en wordt niet door MiniMax onderschreven. Commercieel gebruik is NIET verboden (het is geen niet-commerciële licentie); de voorwaarden staan hieronder.

**Gebied (Applicable Territory)**
- **Preambule, I.3, I.5:** Wereldwijd, MET UITZONDERING VAN de Europese Unie, het Verenigd Koninkrijk, de Republiek Korea en de Verenigde Staten. Gebruik van het model geldt als acceptatie van de licentie.
- **II:** Royaltyvrije, niet-overdraagbare, beperkte licentie om te gebruiken, te reproduceren, te distribueren, afgeleide werken te maken en te wijzigen, alleen binnen het gebied en in overeenstemming met de overeenkomst en Exhibit A. Personen in uitgesloten gebieden kunnen MiniMax om een aparte licentie vragen.
- **V.4:** Het gebruiken, reproduceren, wijzigen, distribueren of tonen van het model, zijn afgeleiden EN UITVOER (gegenereerde video/audio) buiten het gebied is niet toegestaan. **Het publiceren of tonen van gegenereerde video's in de EU/het VK/Zuid-Korea/de VS valt dus buiten de licentie.**
- **Exhibit A-1:** Gebruik buiten het gebied schendt het Acceptable Use Policy.

**Distributie (III)** (deze repo distribueert het model niet; als jij dat wel doet)
- **III.1:** Geef elke ontvanger een kopie van de licentie. **III.2:** Markeer gewijzigde bestanden met duidelijke vermeldingen.
- **III.3:** Aangemoedigd (niet verplicht): de vermelding "Powered by MiniMax H3", een AI-generatie-identificatie op geproduceerde bestanden, een openbare toelichting.
- **III.4:** Distributies MOETEN vergezeld gaan van een NOTICE-bestand met: "MiniMax H3 is licensed under the MiniMax H3 Community License Agreement, Copyright © 2026 MiniMax. All Rights Reserved."
- **Exhibit A-12:** het publiceren van content in een openbare omgeving zonder duidelijk te vermelden dat die door een machine is gegenereerd is verboden: label AI-gegenereerde video's wanneer je ze publiceert (volledige lijst: `docs/LISANS_UYARISI.md`).
- **III (laatste alinea):** Je mag je eigen auteursrecht op je wijzigingen vermelden, maar je mag geen aanvullende of afwijkende voorwaarden voor gebruik/distributie opleggen; de gebiedsregels blijven gelden.

**Commerciële voorwaarden (IV)**
- **IV.1:** Als je commerciële producten/diensten meer dan USD 20 miljoen (of het equivalent) jaaromzet genereren, vraag dan VOORAF schriftelijke toestemming aan api@minimax.io (onderwerp "MiniMax H3 licensing - authorization request").
- **IV.2:** De gebruikersinterface van een commercieel product/een commerciële dienst die het model gebruikt, moet "MiniMax H3" duidelijk zichtbaar tonen.

**Gebruiksbeperkingen (V)**
- **V.1:** Houd je aan de toepasselijke wetgeving (inclusief handelsnaleving) en Exhibit A. **V.2:** Verbind iedereen aan wie je toegang geeft aan voorwaarden die minstens even beschermend zijn als deze beperkingen en breng hen op de hoogte.
- **V.3:** Je mag het model of de UITVOER ervan niet gebruiken om een ander AI-model te verbeteren (anders dan MiniMax H3 en zijn afgeleiden). (I.11: distillatie en training op synthetische uitvoer maken een model tot een "derivative"; de uitvoer zelf is geen afgeleide.)
- **V.5:** Als je aan derden een product/dienst/gehoste dienst aanbiedt die met het model uitvoer genereert: voor en tijdens de exploitatie redelijke technische en organisatorische waarborgen, een meldmechanisme, snel onderzoek, en verwijdering/uitschakeling/opschorting van herhaalde overtreders.

**Handelsmerk en rechten (VI)**
- **VI.1:** De afgeleide werken en modelafgeleiden die je maakt zijn van jou (onder voorbehoud van de rechten van MiniMax). **VI.2:** Namen/merken van MiniMax worden niet in licentie gegeven (behalve wat nodig is om te beschrijven en te distribueren); het merk "MiniMax H3" mag alleen worden gebruikt om aan III.3 te voldoen, binnen het gebied; wek geen indruk van verbondenheid.
- **VI.3:** Als je MiniMax of wie dan ook aanklaagt met de bewering dat de materialen/uitvoer jouw rechten schenden, eindigen al je licenties op die dag; jij verdedigt en vrijwaart MiniMax tegen claims van derden die voortvloeien uit jouw gebruik/distributie of dat van anderen.
- **VI.4:** MiniMax claimt geen rechten op uitvoer; jij en je gebruikers zijn verantwoordelijk voor de uitvoer en het gebruik ervan.

**Disclaimers en beëindiging (VII, VIII, IX)**
- **VII.1:** Geen verplichting tot ondersteuning/updates. **VII.2:** Model en uitvoer worden geleverd "AS IS", zonder garanties; jij bepaalt de geschiktheid en neemt het risico. **VII.3:** MiniMax en verbonden bedrijven zijn niet aansprakelijk voor enige schade (voor zover de wet dat toestaat).
- **VIII.1:** Gaat in bij acceptatie/toegang. **VIII.2:** Bij schending kan MiniMax beëindigen; jij moet het gebruik/de distributie stoppen, kopieën verwijderen en ontvangers op de hoogte brengen (VI.1, VI.3, VII, IX blijven van kracht).
- **IX:** Recht van de Speciale Administratieve Regio Hongkong; exclusieve bevoegdheid van de rechtbanken van Hongkong (het VN-Verdrag inzake internationale koop, CISG, is uitgesloten).
- **Aanvullende opmerking:** de encoder van MiniMax H3 gebruikt Qwen3-VL-32B (Apache 2.0).

**Acceptable Use Policy (Exhibit A)** (gebruik het model, afgeleiden of uitvoer NIET voor)
- A-1 gebruik buiten het gebied; A-2 schending van wetten of IP van derden; A-3 schade aan jezelf of anderen; A-4 uitvoer hergebruiken/distribueren om schade te berokkenen; A-5 waarborgen omzeilen; A-6 uitbuiten/schaden van minderjarigen; A-7 aantoonbaar onjuiste informatie om anderen te schaden of verkiezingen te beïnvloeden; A-8 nepbetrokkenheid online (nepreviews enz.); A-9 smaad, minachting, intimidatie; A-10 malware; A-11 persoonsgegevens om anderen te schaden; **A-12 het publiceren van content in een openbare omgeving (inclusief posts van bots) zonder duidelijk en prominent te vermelden dat die door een machine is gegenereerd**; A-13 imitatie zonder toestemming; A-14 geautomatiseerde beslissingen met hoog risico in kritieke domeinen (rechtshandhaving, immigratie, gezondheid, kritieke infrastructuur, krediet, werkgelegenheid, huisvesting, onderwijs, sociale scoring, verzekeringen enz.); A-15 schending van de sociale, ethische en morele normen van andere landen/regio's; A-16 gewelddadig extremisme/terrorisme; A-17 discriminatie/schade op basis van beschermde kenmerken; A-18 uitbuiten van kwetsbare groepen; **A-19 militaire doeleinden**; A-20 ongeautoriseerde/niet-gelicentieerde beroepsactiviteit (financieel, juridisch, medisch enz.).
- Opmerking: dit is een samenvatting in gewone taal, geen juridisch advies; bij twijfel is de Engelse licentietekst leidend.

## Bewijslabels

Eén set voor alle documenten (oudere schrijfwijzen tussen haakjes):
- **[gemeten]** (TR: ölçtüm, olctum): uitgevoerd in dit project, bewijspad bestaat.
- **[gelezen]** (TR: okudum yol, okudum): bron of script gelezen, niet uitgevoerd.
- **[ontwerp]** (TR: tasarım, tasarim): ontworpen, nog niet in een echte run gezien.
- **[gok]** (TR: tahmin): niet geverifieerd.
- **[niet geprobeerd]** (TR: denenmedi): nooit uitgevoerd.
- **[gemeld door gebruiker]** (TR: kullanıcı bildirdi): door de gebruiker verklaard, met datum; niet onafhankelijk gemeten.
- **[berekend]** (TR: hesap; oudere schrijfwijzen: calculated, hesap): een getal afgeleid uit gemeten invoer, zelf niet gemeten; de afleiding staat ernaast. [voorstel] / [öneri] in oudere tekst = [gok].

Gebruikte runnamen tussen haakjes (onze eigen runnamen, geen bestanden in deze repo): U209 = 209 frames met de release-binary via `uret.ps1`; B209 en B192 = image-to-video-runs (`-InitImg`) op 209 en 192 frames; B56VT2 = release-binary, 56 frames, vergeleken met de bytereferentie R0 van 56 frames; F209b, F209V2, F209V2K = runs van 209 frames op de ontwikkelbuild (details: `docs/OLCUMLER.md`).

## Bekende beperkingen
- **Bytebewijs** (zelf reproduceren: `docs/KANITLAR.md`, "R0 ve latent referansi nasil uretilir"; geverifieerd op onze sm_61-kaart, andere GPU's zijn mogelijk niet byte-identiek [gok]): met onze patchreeks (geheugenvlaggen aan) gaf een run van 56 frames sha256 `0979f156d548169b...`, identiek aan de referentie [gemeten]; bij 141 frames was de latent-sha256 `E5D028F8632BE4FE...` identiek (met de vlaggen 0013/0014). Voor 158 tot 209 frames is er geen directe bytereferentie; de keten van poorten is het bewijs. Het halen van de numerieke poorten garandeert geen goede clip: bewegingsconsistentie in de tijd wordt met het oog gecontroleerd (zie `docs/KAPILAR.md`).
- **209 frames, welke vlaggenset:** het bytekettingbewijs voor 209 frames is verzameld met de vlaggenset F209V2 op de ontwikkelbuild (geen blokstaartvlaggen, gebouwd zonder patches 0019/0020); `uret.ps1` gebruikt dit recept voor 209 frames [gelezen: het script; een echte engine-run via `uret.ps1` slaagde in run U209].
- Door ons geverifieerd op één kaart (GTX 1050 Ti 4 GB); externe meldingen over andere kaarten staan met hun labels in `docs/KART_PROFILLERI.md` [gemeld door gebruiker].
- **Welke binary is gemeten:** de latent van 141 frames en de bytereeks zijn gemeten met onze ontwikkelbuilds. De release-binary die je downloadt is een verse build: de bytepoort voor 56 frames slaagde (volgend punt) en een run van 209 frames via `uret.ps1` haalde de poort (run U209, 3414 s, VRAM-piek 3777 MiB) [gemeten]; ten opzichte van de run van 209 frames met de ontwikkelbuild is de latent byte-identiek; in de video zijn de frames (md5) en de audio identiek, de sha256 van het AVI-bestand verschilt door de container [gemeten] (zie `docs/OLCUMLER.md`, sectie 0).
- **Release-binary, 56 frames:** de release-binary (sd-cli `c5cebe78...`, stable-diffusion.dll `e5d3d329...`) gaf een resultaat van 56 frames dat byte-identiek is aan R0 (sha256 `0979f156d548169be03acd1a9d7617102a75333aa48a28d6bbfd1cc5fa3f604d`; md5 per frame en audio identiek), direct gedraaid met standaardvlaggen (geen `SD_*`-variabelen), exitcode 0, 601 s [gemeten: run B56VT2, 2026-11-19; het bewijs wordt bewaard door de auteurs, niet in deze repo]. Reikwijdte: alleen onze sm_61-kaart en 56 frames; geen clean-root-installatietest; de latent van 141 frames en de keten van 209 zijn met de oudere binary gemeten en daarmee NIET herhaald [niet geprobeerd]. Een eerste poging (B56VT, via een hulpscript) eindigde na 58 s zonder melding, oorzaak onbekend [gok: geheugendruk]; de tweede poging draaide `sd-cli` direct.
- De installatie- en runscripts zijn nog niet vanuit een lege map geverifieerd (clean-root-test staat nog open).
- Roadmap en volgende stappen: `ROADMAP.md`.

## Status en grenzen
- Geverifieerd op één machine (GTX 1050 Ti 4 GB, 16 GB RAM, i7-7700HQ). Andere 4 GB-kaarten en andere hoeveelheden RAM kunnen afwijken.
- **Standaard 209 frames (8,7 s):** haalde onze kwaliteitspoorten (ruis 1,08, run F209V2K) [gemeten: 209 frames met de release-binary via `uret.ps1`, run U209; latent byte-identiek aan de run met de ontwikkelbuild; frames en audio in de video identiek, de sha van het bestand verschilt door de container; het bewijs wordt bewaard door de auteurs, niet in deze repo]. Bij 209 frames was de VRAM-piek van de DiT 3777 MiB van 4096 MiB (runs F209b en U209; meting van de hele kaart met `nvidia-smi`), een kleine marge: andere GPU-belasting (het beeldscherm, andere toepassingen) kan de run bij `blocks.0` laten mislukken; alleen getest op een GTX 1050 Ti. De toestand van het beeldscherm tijdens die run is niet vastgelegd; als je beeldscherm op deze kaart draait, is er minder VRAM beschikbaar [gok: een Windows-schermbelasting van ongeveer 100-300 MB]; sluit zo nodig het beeldscherm aan op een geïntegreerde GPU [advies, niet getest]. Sampling duurde 2730 s (run U209: stappen van 436-483 s) en het VAE-decoderen in een apart proces 173 s (fase 2 in totaal 193 s met het decoderen van de audio) [gemeten: U209 release-binary; oudere ontwikkelruns: 2664 s en 174 s]. In fase 1 liep de VAE in hetzelfde proces zonder geheugen en viel terug op temporele tiling (320 s); die uitvoer wordt weggegooid, de video komt uit fase 2 zonder tiling. De piek van het RAM-gebruik is in U209 niet gemeten. Clips langer dan 209 frames maken geen deel uit van deze release.
- **Image-to-video (`-InitImg`):** met een init-afbeelding is de limiet op deze GPU 192 frames (8,0 s bij 24 fps): 209 frames pasten niet (ongeveer 17,5 MB VRAM tekort bij blok 0: nodig 2587 MB, beschikbaar 2570 MB); 192 frames liepen via `uret.ps1` in 3086 s met een VRAM-piek van 3783 MiB en de poort werd gehaald [gemeten: runs B209 en B192, 2026-11-20, één scène; het bewijs wordt bewaard door de auteurs, niet in deze repo]. Niet geprobeerd op andere GPU's [niet geprobeerd].
- **Vrij RAM is belangrijk:** je hebt ongeveer 11 GB VRIJ RAM nodig (het engineproces neemt ongeveer 11 GB in beslag) [gemeten]. Bij te weinig vrij RAM kan het proces zonder foutmelding sterven [gok: we zagen het één keer met ongeveer 300 MB vrij RAM terwijl `sd-cli` ongeveer 10 GB vasthield]. Open tijdens de run geen andere grote programma's: op een machine met 16 GB blijft maar ongeveer 0,3-0,5 GB vrij, en onder geheugendruk kan de run stilletjes sterven. Sluit voor je begint browsers, games en andere grote programma's en controleer het vrije RAM.
- **Clean-root-test staat nog open:** de installatie- en runscripts zijn nog niet vanuit een lege map geverifieerd met alleen deze instructies; deze sectie wordt bijgewerkt wanneer die test (inclusief een bytevergelijking van 56 frames met de referentie) is vastgelegd.
- Hier worden geen gegenereerde video's meegeleverd.

<!-- i18n-source: README.md sha256:322506e84cdc -->
