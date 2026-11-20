# Privacy / Gizlilik

## English (authoritative)

**Short version: VideoTurko has no telemetry. Its scripts use the network only to download the engine and the models, and only from the hosts listed below.** Nothing about you, your machine or your videos is uploaded.

### What the scripts fetch
| Host | What | Which script, when |
|---|---|---|
| `github.com` (its release downloads are redirected to `release-assets.githubusercontent.com` [measured: HTTP redirect seen 2026-11-20]) | engine zip and CUDA runtime zip of release v0.1.0 | `scripts/kur.ps1` (via `curl.exe`), only in the engine step; skipped if you give local zips with `-MotorZip` / `-CudaZip` |
| `huggingface.co` and `hf.co` sub-hosts (a redirect to `us.aws.cdn.hf.co` was seen [measured: 2026-11-20]) | the four model files, about 29.3 GiB (`scripts/modeller.json`) | `scripts/modelleri_indir.ps1`, only after you accept the model license; it refuses non-https and any other host |

Every download is checked against a pinned sha256 and stops on a mismatch. The zip step uses `curl -L`, which follows redirects without a host list; the sha256 check is what protects it [read: `scripts/kur.ps1`]. If you set `VT_MOTOR_URL` or `VT_CUDA_URL` yourself, you choose the host.

Like any download, the host sees your IP address and the ordinary request headers. We send nothing else: no account, no usernames, no GPU or system information, no usage data.

### What it does not do
No telemetry or analytics, no crash reports, no update check, no accounts or cookies, no network ports opened, no upload of prompts or videos. The optional MCP server (`mcp/`) talks only over stdio to the program that starts it. Image-to-video input and your prompts stay on your disk. [read: this version of `scripts/` and `mcp/`; see the check below]

### What stays on your computer
`engine\`, `model\`, and `runs\` (videos, logs, `runs\olaylar.txt`) inside the install folder, plus `model\.lisans_kabul.txt` (that you accepted the model license, and when). Logs can contain your folder path: remove it before you post a log in an issue.

### Outside our scripts
- GitHub processes what you post here (issues, pull requests, stars) under the GitHub Privacy Statement; it is public.
- The README on GitHub shows badges from `img.shields.io`; your browser requests them when you view the page. The scripts never do.
- The optional MCP server needs the `mcp` Python package (`pip`, PyPI) and the quality gate needs Python with OpenCV: installing them is your step, not done by our scripts.
- The model and its outputs are under the MiniMax license, not under this policy (`docs/LISANS_UYARISI.md`).

### Check it yourself (a few seconds, nothing is downloaded)
See what would be fetched: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\kur.ps1 -Kuru` (lines starting with `URL:`). See every network call in the code:
```powershell
Select-String -Path scripts\*.ps1,scripts\*.py,scripts\*.json,mcp\*.py -Pattern 'https?://|curl|HttpWebRequest|WebClient|Invoke-WebRequest|Invoke-RestMethod|urllib|socket'
```
Expected today: the hosts above and nothing else. If you find a call that is not listed here, please report it as in `SECURITY.md`. When a release adds a host, this file is updated in the same change.

## Türkçe

**Kısaca: VideoTurko'da telemetri yok. Betikler ağı yalnız motoru ve modelleri indirmek için, yalnız aşağıdaki adreslerden kullanır.** Sizin, makinenizin ya da videolarınızın hiçbir bilgisi yüklenmez.

### Betiklerin indirdikleri
| Adres | Ne | Hangi betik, ne zaman |
|---|---|---|
| `github.com` (indirmeler `release-assets.githubusercontent.com`'a yönlenir [ölçtüm: yönlendirme 2026-11-20'de görüldü]) | v0.1.0 sürümünün motor zip'i ve CUDA çalışma zip'i | `scripts/kur.ps1` (`curl.exe` ile), yalnız motor adımında; `-MotorZip` / `-CudaZip` ile yerel zip verirseniz atlanır |
| `huggingface.co` ve `hf.co` alt adresleri (`us.aws.cdn.hf.co`'ya yönlenme görüldü [ölçtüm: 2026-11-20]) | dört model dosyası, yaklaşık 29,3 GiB (`scripts/modeller.json`) | `scripts/modelleri_indir.ps1`, yalnız model lisansını kabul ettikten sonra; https dışını ve başka adresi reddeder |

Her indirme sabitlenmiş sha256'ya karşı denetlenir, uyuşmazsa durur. Zip adımı `curl -L` kullanır, yönlendirmeyi adres listesi olmadan izler; koruyan şey sha256 denetimidir [okudum: `scripts/kur.ps1`]. `VT_MOTOR_URL` ya da `VT_CUDA_URL`'yi kendiniz ayarlarsanız adresi siz seçmiş olursunuz.

Her indirmede olduğu gibi karşı taraf IP adresinizi ve olağan istek başlıklarını görür. Başka hiçbir şey göndermeyiz: hesap, kullanıcı adı, ekran kartı ya da sistem bilgisi, kullanım verisi yok.

### Yapmadıkları
Telemetri/analitik yok, çökme raporu yok, güncelleme denetimi yok, hesap ya da çerez yok, ağ portu açmaz, istem ya da video yüklemez. İsteğe bağlı MCP sunucusu (`mcp/`) yalnız onu başlatan programla stdio üzerinden konuşur. Resimden videoya girdiniz ve istemleriniz diskinizde kalır. [okudum: `scripts/` ve `mcp/` bu sürümde; aşağıdaki denetime bakın]

### Bilgisayarınızda kalanlar
Kurulum klasöründe `engine\`, `model\` ve `runs\` (videolar, günlükler, `runs\olaylar.txt`); ayrıca `model\.lisans_kabul.txt` (model lisansını kabul ettiğiniz ve zamanı). Günlüklerde klasör yolunuz olabilir: issue'ya günlük koymadan önce silin.

### Betiklerimizin dışında
- Burada paylaştığınız (issue, PR, yıldız) GitHub tarafından GitHub Gizlilik Bildirimi'ne göre işlenir ve herkese açıktır.
- GitHub'daki README `img.shields.io` rozetleri gösterir; sayfayı açınca tarayıcınız onları ister. Betikler istemez.
- İsteğe bağlı MCP sunucusu `mcp` Python paketini (`pip`, PyPI), kalite kapısı OpenCV'li Python'u ister: bunları kurmak sizin adımınızdır, betiklerimiz yapmaz.
- Model ve çıktıları MiniMax lisansındadır, bu metnin kapsamı dışındadır (`docs/LISANS_UYARISI.md`).

### Kendiniz denetleyin (birkaç saniye, hiçbir şey indirilmez)
Neyin indirileceğine bakın: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts\kur.ps1 -Kuru` (`URL:` ile başlayan satırlar). Koddaki bütün ağ çağrıları için yukarıdaki `Select-String` komutu. Bugün beklenen: yalnız yukarıdaki adresler. Listede olmayan bir çağrı bulursanız `SECURITY.md`'deki gibi bildirin. Bir sürüm yeni adres eklerse bu dosya aynı değişiklikte güncellenir.
