# Writing a single-scene prompt / Tek sahne istemi yazımı (EN + TR)

EN first, TR below ([Türkçe bölüm](#türkçe)). Evidence labels are the ones defined in README.md: **[measured]** = run in this project; **[experience]** = what we saw in a few runs, not a controlled test; **[guess]** = unverified.

## English

VideoTurko makes ONE continuous scene per run (up to 209 frames, 8.7 s; with `-InitImg` up to 192 frames, 8.0 s). The prompt pattern below is what we used for the two runs shown at the end. It is a starting point, not a rule: change anything.

The prompt file is one English paragraph (see `scripts/uret.ps1 -Istem`). Four parts, in this order:

### 1. One continuous shot sentence
Start with: `One continuous shot with no cuts, no edits and no transitions, one smooth camera path throughout:` (or, for a fixed camera, `..., static camera at the robot's eye level:`).
The model is asked for a single pass with no scene changes; one clip is one scene (the project does not chain parts, see README.md "Scope"). [experience: we kept this sentence in both example runs; we did not compare against prompts without it]

### 2. Four equal time slices, one event and one camera move each
- Duration = frames / 24 fps. 209 frames = 8.7 s, 192 frames = 8.0 s, 141 frames = 5.9 s, 56 frames = 2.3 s.
- Split the duration into 4 equal slices and write them as `[0 to 2.2 s] ... [2.2 to 4.4 s] ... [4.4 to 6.5 s] ... [6.5 to 8.7 s] ...` (209 frames: 8.7 / 4 is about 2.2 s, rounded).
- Each slice gets ONE event and ONE camera movement (follow, pull back, rise, hold). Do not pack several actions into one slice.
- Why: slices give the story a pace and stop it from rushing or stalling [guess; we did not test one slice against four]. One action per slice is easier to check when you watch the result [experience].

### 3. Fixed identity
After the slices, one sentence that never changes: the subject (what it looks like, colours, markings), the place, the era or season, and the style (for example `photorealistic live-action war film, 35mm film grain, realistic physics` or `3D animated film style`). Repeating the same identity words in the slices is fine. [experience: both examples kept the subject recognisable for the whole clip; two runs, not a statistic]

### 4. Sound
The prompt may end with one `audio:` sentence in layers: foreground, mid, background (for example `audio: foreground roaring engine ..., mid wind and mud splashes, background tense low string drone ...`).
If you do not want speech, say `no narration, no speech` (add `no music` if you want none). [experience: our two videos had no speech with this sentence; not tested without it]

### Extra rules for `-InitImg` (image-to-video)
- Cap: 192 frames (8.0 s), slices of 2.0 s each: `[0 to 2.0 s] [2.0 to 4.0 s] [4.0 to 6.0 s] [6.0 to 8.0 s]`. 209 frames did not fit in 4 GB with `-InitImg` (about 17.5 MB of VRAM short) [measured: runs B209 and B192].
- Add a sentence that keeps the first frame: `Same robot design, colors and text as the first frame throughout` (replace "robot" with your subject; name the text or design that must stay).
- Describe what moves; the init image already gives the look. Use the init image at the video size (the B192 run used a 640x384 image) [measured: file used in that run].
- If a landmark or a specific background must appear, put it in the still and let the prompt describe only the motion and the sound: on an RTX 3070 the text-only prompt made up the skyline, the init image kept the tower for 8 s [user-reported, PR #7; details: `docs/RTX3070_STOCK_SDCPP.md`].

### First and last frame (`-EndImg`, "FLF")
FLF means first-last frame: you give the frame the clip starts on (`-InitImg`) and the frame it must end on (`-EndImg`); the model fills the motion between them.
- When it helps: the end state is known and the model gets the mechanics wrong without it. A community report: a telescopic mast rose together with its basket with only a start image; with the end frame the body stayed still and the sections extended upward [user-reported, issue #1, RTX 4070 Ti; 107 and 141 frames passed the gates there].
- Both images at the video size (640x384 by default, or your `-W`/`-H`), same framing and lighting; change only what should move.
- The prompt describes the motion from the first to the last frame in the time slices; keep the "Same ... as the first frame throughout" sentence and name what changes in the last slice.
- Cap: 175 frames on cards under 8 GB (192 did not fit on 4 GB; `-InitImg` alone stays at 192); 192 on 8 GB+ cards (not measured by us). Time slices for 175 frames (7.3 s): `[0 to 1.8 s] [1.8 to 3.6 s] [3.6 to 5.5 s] [5.5 to 7.3 s]`. On our GTX 1050 Ti (4 GB) it always runs in two processes (one process ran out of VRAM even at 56 frames): 56 frames 1040 s (VRAM peak 3597 MiB), 175 frames 2887 s = 48 min (3721 MiB), both passed the gate; 192 frames did not fit [measured, 2026-11-20]. `-EndImg` without `-InitImg` is supported by the engine but [not tried].
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\uret.ps1 -Istem istem.txt -Kare 141 -InitImg ilk_kare.png -EndImg son_kare.png
```

### Two full examples
Both clips were generated with `scripts/uret.ps1`. These prompts are the exact text of the run files; you can paste them as `istem.txt`.

**A. Plane, 209 frames (8.7 s), text-to-video.** [measured: run U209, release binary: quality gates passed; frames and audio identical to the development-build run; no visible jump when we watched the whole clip (by eye)]

```text
One continuous shot with no cuts, no edits and no transitions, one smooth camera path throughout: [0 to 2.2 s] the camera follows close behind and slightly above the plane at its speed, keeping it centered, as the plane descends in a steep smooth dive over wet green fields toward the muddy road. [2.2 to 4.4 s] the plane levels out low over the road and opens fire, wing machine guns flashing, a fast line of bullet impacts kicking mud along the road, the infantry diving into the roadside ditch, while the camera pulls back and drifts right. [4.4 to 6.5 s] the plane flashes past low and begins to climb while the camera rises smoothly to a right diagonal high angle showing both the plane and the soldiers in the ditch. [6.5 to 8.7 s] the plane banks away into the gray sky growing smaller as the camera holds a wide frame and the dust settles. a single-engine World War II fighter plane in gray-green camouflage with a black and white cross on its wings, a muddy French country road lined with poplar trees and a roadside ditch, American infantry in olive drab uniforms and round steel helmets, overcast gray 1944 sky; photorealistic live-action war film, 35mm film grain, realistic physics; audio: foreground roaring engine growing louder then machine gun bursts then a passing roar fading, mid wind and mud splashes, background tense low string drone rising then resolving; no narration, no speech
```

**B. Mascot, 192 frames (8.0 s), image-to-video (`-InitImg`).** [measured: run B192: quality gates passed, no visible jump by eye, 3086 s total on the GTX 1050 Ti] The init image (the mascot's first frame, a small round-headed robot with the word VideoTurko on its red patched body) is NOT part of this repository; the prompt describes it so you can make your own. Here the camera is fixed instead of moving, so the first sentence says `static camera at the robot's eye level`.

```text
One continuous shot with no cuts, no edits and no transitions, static camera at the robot's eye level: [0 to 2.0 s] the small round-headed robot with a curved screen face, a red patched body with the word VideoTurko and a short antenna with a red tassel rolls slowly toward the camera on its three little wheels across the warm wooden floor. [2.0 to 4.0 s] it stops, tilts its dome head curiously, its two glowing pixel eyes blink once. [4.0 to 6.0 s] its pixel eyes turn into happy curved smiling eyes, the antenna and red tassel wobble, it lifts one small claw hand and waves shyly. [6.0 to 8.0 s] it does a tiny happy wiggle and the little projector lens on its chest glows softly while it keeps looking at the camera. Same robot design, colors and text as the first frame throughout, warm soft studio light, shallow depth of field, 3D animated film style; audio: soft electric servo whirrs and wheel rolling on wood, two cute short electronic beeps, a gentle happy chirp, quiet warm ambient room tone; no narration, no speech, no music
```

### Limits (read this)
- Two examples are not proof. We have not compared this pattern with other prompt styles; every "why" above is [experience] or [guess].
- The quality gate does NOT check motion consistency (object scale or position jumps): **watch the whole video** before you accept it (see "Quality gates" in README.md and `docs/KAPILAR.md`).
- The footage you make is subject to the MiniMax H3 license terms for outputs (see README.md "Model license warning").

---

## Türkçe

VideoTurko her çalıştırmada TEK kesintisiz sahne üretir (en çok 209 kare, 8,7 sn; `-InitImg` ile en çok 192 kare, 8,0 sn). Aşağıdaki istem kalıbı, sonda gösterilen iki çalıştırmada kullandığımız kalıptır. Başlangıç noktasıdır, kural değildir: istediğini değiştir.

İstem dosyası tek paragraf İngilizce metindir (`scripts/uret.ps1 -Istem`). Dört parça, bu sırayla:

### 1. Kesintisiz çekim cümlesi
Şununla başla: `One continuous shot with no cuts, no edits and no transitions, one smooth camera path throughout:` (kamera sabitse: `..., static camera at the robot's eye level:`).
Modelden tek geçişte, sahne değişimi olmayan bir görüntü istenir; bir klip bir sahnedir (proje parça zincirlemez, README.md "Scope"). [deneyimimiz: iki örnek çalıştırmada da bu cümleyi tuttuk; cümlesiz istemle karşılaştırmadık]

### 2. Dört eşit zaman dilimi, her birinde tek olay ve tek kamera hareketi
- Süre = kare sayısı / 24 kare/sn. 209 kare = 8,7 sn, 192 kare = 8,0 sn, 141 kare = 5,9 sn, 56 kare = 2,3 sn.
- Süreyi 4 eşit dilime böl ve `[0 to 2.2 s] ... [2.2 to 4.4 s] ... [4.4 to 6.5 s] ... [6.5 to 8.7 s] ...` diye yaz (209 kare: 8,7 / 4 yaklaşık 2,2 sn, yuvarlanmış).
- Her dilime TEK olay ve TEK kamera hareketi ver (takip, geri çekilme, yükselme, sabit kalma). Bir dilime birkaç eylem sığdırma.
- Neden: dilimler hikayeye tempo verir, acele etmesini ya da oyalanmasını önler [tahmin; bir dilimi dört dilimle karşılaştırmadık]. Dilim başına tek eylem, sonucu izlerken kontrol etmeyi kolaylaştırır [deneyimimiz].

### 3. Sabit kimlik
Dilimlerden sonra hiç değişmeyen bir cümle: özne (görünüşü, renkleri, işaretleri), mekân, dönem ya da mevsim ve stil (örneğin `photorealistic live-action war film, 35mm film grain, realistic physics` ya da `3D animated film style`). Aynı kimlik sözcüklerini dilimlerde tekrar etmek sorun değil. [deneyimimiz: iki örnekte de özne bütün klip boyunca tanınır kaldı; iki çalıştırma, istatistik değil]

### 4. Ses
İstem, katmanlı tek bir `audio:` cümlesiyle bitebilir: önde, ortada, arkada (örneğin `audio: foreground roaring engine ..., mid wind and mud splashes, background tense low string drone ...`).
Konuşma istemiyorsan `no narration, no speech` yaz (müzik de istemiyorsan `no music` ekle). [deneyimimiz: iki videomuzda bu cümleyle konuşma çıkmadı; cümlesiz denemedik]

### `-InitImg` (resimden video) için ek kurallar
- Tavan: 192 kare (8,0 sn); dilimler 2'şer sn: `[0 to 2.0 s] [2.0 to 4.0 s] [4.0 to 6.0 s] [6.0 to 8.0 s]`. 209 kare 4 GB'da `-InitImg` ile sığmadı (yaklaşık 17,5 MB VRAM eksik) [ölçtüm: B209 ve B192 koşuları].
- İlk kareyi koruyan bir cümle ekle: `Same robot design, colors and text as the first frame throughout` ("robot" yerine kendi öznen; kalması gereken yazıyı ya da tasarımı adlandır).
- Yalnızca neyin hareket ettiğini anlat; görünümü başlangıç görseli zaten verir. Başlangıç görselini video boyutunda kullan (B192 koşusu 640x384 görsel kullandı) [ölçtüm: o koşuda kullanılan dosya].

### İlk ve son kare (`-EndImg`, "FLF")
FLF, İngilizce "first-last frame" yani ilk-son kare demektir: klibin başladığı kareyi (`-InitImg`) ve bitmesi gereken kareyi (`-EndImg`) verirsin; aradaki hareketi model doldurur.
- Ne zaman işe yarar: bitiş durumu belli ve model onsuz mekaniği yanlış kuruyor. Topluluk raporu: yalnız başlangıç görseliyle teleskopik direk sepetiyle birlikte kalkıyordu; bitiş karesi verilince gövde sabit kaldı, kesitler yukarı açıldı [kullanıcı bildirdi, issue #1, RTX 4070 Ti; orada 107 ve 141 kare kapıdan geçti].
- İki görsel de video boyutunda olsun (varsayılan 640x384 ya da senin `-W`/`-H` değerin), aynı kadraj ve ışık; yalnız hareket etmesi gereken şey değişsin.
- İstem, dilimler içinde ilk kareden son kareye hareketi anlatır; "Same ... as the first frame throughout" cümlesini tut, son dilimde neyin değiştiğini adlandır.
- Tavan: 8 GB altı kartta 175 kare (192 kare 4 GB'a sığmadı; yalnız `-InitImg` ile tavan 192 kalır); 8 GB ve üstünde 192 (bizce ölçülmedi). 175 kare (7,3 sn) için dilimler: `[0 to 1.8 s] [1.8 to 3.6 s] [3.6 to 5.5 s] [5.5 to 7.3 s]`. Bizim GTX 1050 Ti'de (4 GB) her zaman iki süreçte koşar (tek süreç 56 karede bile VRAM'e sığmadı): 56 kare 1040 sn (VRAM tepe 3597 MiB), 175 kare 2887 sn = 48 dk (3721 MiB), ikisi de kapıdan geçti; 192 kare sığmadı [ölçtüm, 2026-11-20]. `-InitImg` olmadan yalnız `-EndImg` motorda var ama [denenmedi].
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\uret.ps1 -Istem istem.txt -Kare 141 -InitImg ilk_kare.png -EndImg son_kare.png
```

### İki tam örnek
İki klip de `scripts/uret.ps1` ile üretildi. Aşağıdaki istemler çalıştırma dosyalarının birebir metnidir; `istem.txt` olarak yapıştırabilirsin (yukarıdaki İngilizce bölümdeki kod bloklarıyla aynıdır: A uçak, B maskot).

**A. Uçak, 209 kare (8,7 sn), metinden video.** [ölçtüm: U209 koşusu, yayın ikilisiyle: kalite kapıları geçti; kareler ve ses geliştirme derlemesiyle aynı; tüm klibi izlediğimizde gözle sıçrama görmedik]

**B. Maskot, 192 kare (8,0 sn), resimden video (`-InitImg`).** [ölçtüm: B192 koşusu: kalite kapıları geçti, gözle sıçrama yok, GTX 1050 Ti'de toplam 3086 sn] Başlangıç görseli (maskotun ilk karesi: kırmızı yamalı gövdesinde VideoTurko yazan küçük, yuvarlak kafalı bir robot) bu depoda YOK; istem onu tarif eder, kendi görselini yapabilirsin. Burada kamera hareket etmek yerine sabit olduğu için ilk cümle `static camera at the robot's eye level` der.

### Sınırlar (oku)
- İki örnek kanıt değildir. Bu kalıbı başka istem biçimleriyle karşılaştırmadık; yukarıdaki her "neden" [deneyimimiz] ya da [tahmin] etiketlidir.
- Kalite kapısı hareket tutarlılığını (nesne ölçeği veya konum sıçramaları) DENETLEMEZ: kabul etmeden önce **videonun tamamını izle** (README.md "Quality gates", `docs/KAPILAR.md`).
- Ürettiğin görüntü, MiniMax H3 lisansının çıktı koşullarına tabidir (README.md "Model license warning").
