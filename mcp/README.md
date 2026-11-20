# VideoTurko MCP Sunucusu / MCP Server (TR + EN)

Yerel MiniMax H3 (`sd-cli`, CUDA) metinden/resimden video üretimini **stdio** tabanlı MCP (Model Context Protocol) araçları olarak sunar. Mevcut `scripts/uret.ps1` betiğini sarmalar; kalite ayarlarını veya kalite kapılarını değiştirmez.

Exposes local MiniMax H3 (`sd-cli`, CUDA) text-to-video and image-to-video generation over a **stdio** MCP server. Wraps `scripts/uret.ps1` directly without altering quality settings or quality gates.

---

## Özellikler / Highlights
- **Kare sınırları / Frame limits:** `17k+5` ızgarasında metinden en fazla **209 kare (8.7 s)**, `init_image` ile en fazla **192 kare (8.0 s)** (640×384, 24 fps).
- **Tek GPU kilidi / Single-GPU lock:** Aynı anda tek üretim işi çalıştırır; uzun işler ayrı bir PowerShell sürecinde arka planda koşar ve hemen `job_id` döner.
- **Motor seçimi / Engine selection:** Varsayılan olarak `engine/bin/sd-cli.exe` kullanılır; `<ROOT>/engine/bin_sm120/sd-cli.exe` varsa (ve `VT_ENGINE_BIN` ayarlanmadıysa) otomatik seçilir.

---

## Kurulum ve Çalıştırma / Setup & Usage

Gereksinim / Requirements: Python 3.10+ ve `mcp` paketi (`pip install "mcp>=1.2,<2"`; aralık [tahmin]: bu aralıkta hangi sürümün denendiği henüz yazılmadı). Yalnız Windows (süreç denetimi `kernel32`). MCP isteğe bağlıdır; ana hat (`uret.ps1`) bağımlılıksız kalır.

```json
{
  "mcpServers": {
    "videoturko": {
      "command": "python",
      "args": ["mcp/videoturko_mcp.py"],
      "cwd": "<ROOT>"
    }
  }
}
```

### Ortam Değişkenleri / Environment Variables
| Değişken / Variable | Varsayılan / Default | Açıklama / Description |
|---|---|---|
| `VT_ROOT` | `<repo root>` | VideoTurko kök klasörü / repository root |
| `VT_ENGINE_BIN` | `engine/bin_sm120` (varsa) veya `engine/bin` | `sd-cli.exe` klasörü / engine binary folder |
| `VT_MODEL_DIR` | `<VT_ROOT>/model` | Model ağırlıklarının klasörü / model weights directory |
| `VT_MCP_MAX_FRAMES` | `209` | İzin verilen en yüksek kare sayısı / max allowed frames |
| `VT_MCP_CANCEL_WAIT` | `40` | `cancel_job` için `DUR` sonrası nazik bekleme (sn) |
| `VT_MCP_ALLOW_INIT` | `1` | `0` yapılırsa `init_image` kapatılır / set `0` to disable `init_image` |

---

## Araçlar / Tools
- `status()`: Motor (`sd-cli.exe`), 4 model dosyası, GPU (`nvidia-smi`), çalışan işler ve geçerli kare listesini döner.
- `generate_video(prompt, frames=209, seed=42, init_image="")`: Arka planda üretim başlatır, `job_id` ve çıktı yolunu (`runs/mcp_jobs/<job_id>/video.avi`) döner.
- `job_status(job_id, log_lines=15)`: İş durumunu, `uret.ps1` çıkış kodunu, kalite kapısı sonucunu ve son log satırlarını döner. Yalnız `done` (çıkış kodu 0) kapıdan geçmiş videodur. Kapı lisans uygunluğunu denetlemez (`docs/LISANS_UYARISI.md`).

  | `state` | `uret.ps1` çıkış kodu | Anlam |
  |---|---|---|
  | `running` | - | süreç canlı (PID + başlama zamanı eşleşir) |
  | `done` | 0 | video var, kalite kapısı GEÇTİ |
  | `rejected` | 5 | video var ama kapı RED: kabul edilmez, karar kullanıcının |
  | `gate_not_run` | 6 | kapı çalışmadı (python/opencv yok): kabul edilmedi sayılır |
  | `cancelled` | 2 ya da iptal | `cancel_job` ile durduruldu |
  | `failed` | 1 / kodsuz | hata (`log_tail`, `runs/olaylar.txt`) ya da süreç dışarıdan öldürüldü |
- `cancel_job(job_id)`: önce `DUR` dosyası (uret.ps1 temiz kapanır; `VT_MCP_CANCEL_WAIT`=40 sn'ye kadar beklenir); olmazsa süreç ağacı sonlandırılır (`forced_kill: true`) ve `runs/gpu.kilit` temizlenir.
- `list_jobs(limit=10)`: Son işleri listeler.

---

## İlgili Belgeler / Related Docs
- Hızlı başlangıç / Quick start: [`../README.md`](../README.md)
- Kaynaktan derleme / Build from source: [`../docs/KURULUM.md`](../docs/KURULUM.md)
- Model lisansı / Model license: MiniMax H3 Community License ([`../docs/LISANS_UYARISI.md`](../docs/LISANS_UYARISI.md))
