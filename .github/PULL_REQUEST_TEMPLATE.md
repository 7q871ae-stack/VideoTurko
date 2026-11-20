<!-- One language is enough (English or Turkish); a maintainer adds the other. Tek dil yeter. Draft is fine. Taslak PR olur. -->

## What changes / Ne değişiyor
<!-- 1-3 sentences / 1-3 cümle -->

## Kind / Tür
- [ ] Docs or script (no GPU needed) / Belge ya da betik (GPU gerekmez)
- [ ] Patch or engine behaviour / Yama ya da motor davranışı
- [ ] GPU test report / Başka kartta test raporu

## Evidence / Kanıt
Label each claim: [measured] [read] [computed] [user-reported] [guess] ([ölçtüm] [okudum] [hesap] [kullanıcı bildirdi] [tahmin]).
<!-- paste the log or numbers, or write "none" / günlük ya da sayıyı yapıştırın, yoksa "yok" -->

## Checks / Kontroller
- [ ] `python -I -X utf8 scripts/denetim.py --hizli` result / sonuç: <!-- GECTI -->
- [ ] No personal paths, names, e-mails (use the GitHub no-reply address), tokens, model weights or videos / Kişisel yol, ad, e-posta, token, model, video yok
- [ ] Quality settings and the default command line unchanged (6 steps, cfg 1, 640x384, non-tiled VAE) / Kalite ayarları ve varsayılan komut satırı değişmedi

**Only for patches / Yalnız yama için:**
- [ ] 56-frame byte comparison against the reference, or marked experimental and default-off; patch files LF / 56 karede referansla bayt kıyası ya da deneysel + varsayılan kapalı; LF
