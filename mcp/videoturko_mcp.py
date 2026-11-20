"""VideoTurko MCP sunucusu: yerel MiniMax H3 (sd-cli) metinden/resimden video uretimi.

Araclar: status, generate_video, job_status, cancel_job, list_jobs.
Uretim uzun surer; generate_video isi ayri surecte baslatir ve job_id dondurur.
Tek GPU: ayni anda yalniz bir is calisir.
Sure rakamlari (RTX 5060 Laptop: 209 kare 356 s) docs/RTX5060_TEST_RAPORU.md'den [kullanici bildirdi, biz olcmedik].
"""
import codecs, ctypes, json, os, re, subprocess, time, uuid
from ctypes import wintypes
from pathlib import Path
from mcp.server.fastmcp import FastMCP

ROOT = Path(os.environ.get("VT_ROOT", Path(__file__).resolve().parent.parent))
MODEL = Path(os.environ.get("VT_MODEL_DIR", ROOT / "model"))
JOBS = ROOT / "runs" / "mcp_jobs"
if (ROOT / "engine" / "bin_sm120" / "sd-cli.exe").exists():  # RTX 5060 (sm_120) yerel derleme varsa otomatik sec
    os.environ.setdefault("VT_ENGINE_BIN", str(ROOT / "engine" / "bin_sm120"))
JOBS.mkdir(parents=True, exist_ok=True)
FILES = ["minimax_h3_fl2va_hyperflow_flash_14b-Q4_K_M.gguf", "qwen3vl_32b_minimax_h3-Q4_K_M.gguf",
         "minimax_h3_sol_vae_fp16.safetensors", "minimax_h3_audio_vae_fp32.safetensors"]
MAX_FRAMES = int(os.environ.get("VT_MCP_MAX_FRAMES", "209"))  # Varsayilan ust sinir 209 kare (init_image <= 192)
VALID = [5 + 17 * k for k in range(13) if 5 + 17 * k <= MAX_FRAMES]
CANCEL_WAIT = int(os.environ.get("VT_MCP_CANCEL_WAIT", "40"))  # DUR icin nazik bekleme (sn); uret.ps1 ~5 sn'de bir bakar
CF = getattr(subprocess, "CREATE_NO_WINDOW", 0)  # yardimci sureclerde pencere acma

mcp = FastMCP("videoturko")


def _load_izin():
    """init_izin.py'yi dosya yolundan yukle (python -I ya da farkli cwd ile de calisir; yalniz stdlib)."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("vt_init_izin", Path(__file__).resolve().with_name("init_izin.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


_IZIN = _load_izin()


JID = re.compile(r"^\d{8}-\d{6}-[0-9a-f]{6}$")
LOCK = JOBS / ".lock"
# uret.ps1 cikis kodlari (scripts/uret.ps1): 0 gecti, 1 hata (throw), 2 DUR, 5 kapi RED, 6 kapi calismadi
GATE = {"0": "GECTI", "1": "HATA (log_tail, runs/olaylar.txt)", "2": "DURDURULDU (DUR)",
        "5": "RED (klip kabul edilmez; karar kullanicinin, docs/KAPILAR.md)",
        "6": "KAPI CALISMADI (klip kabul edilmedi sayilir; VT_PYTHON/opencv)"}
LISANS = "Kalite kapisi lisans uygunlugunu denetlemez: kullanim sorumlulugu sizindir (docs/LISANS_UYARISI.md)."
QUOTES = "'‘’‚‛"  # PowerShell bunlarin hepsini tek tirnak sayar

# --- surec denetimi: tasklist yerine kernel32 (yerel ayardan bagimsiz, PID yeniden kullanimina karsi baslama zamani) ---
_k = ctypes.WinDLL("kernel32", use_last_error=True)
_k.OpenProcess.restype = wintypes.HANDLE
_k.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
_k.GetProcessTimes.argtypes = [wintypes.HANDLE] + [ctypes.POINTER(wintypes.FILETIME)] * 4
_k.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
_k.CloseHandle.argtypes = [wintypes.HANDLE]


def _proc_info(pid):
    """(canli_mi, baslama_zamani_filetime) ya da None (PID yok/erisilemez)."""
    try:
        h = _k.OpenProcess(0x1000 | 0x100000, False, int(pid))  # QUERY_LIMITED_INFORMATION | SYNCHRONIZE
    except (TypeError, ValueError, OverflowError):
        return None
    if not h:
        return None
    try:
        t = [wintypes.FILETIME() for _ in range(4)]
        if not _k.GetProcessTimes(h, *[ctypes.byref(x) for x in t]):
            return None
        return _k.WaitForSingleObject(h, 0) == 0x102, (t[0].dwHighDateTime << 32) | t[0].dwLowDateTime
    finally:
        _k.CloseHandle(h)


def _alive(m):
    r = _proc_info(m.get("pid"))
    return bool(r and r[0] and r[1] == m.get("ctime"))  # ayni PID baska surece gectiyse baslama zamani tutmaz


def _meta(jid):
    if not JID.match(jid or ""):
        return None
    p = JOBS / jid / "job.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def _exit_code(d):
    ex = d / "exit.txt"
    return ex.read_text(encoding="utf-8-sig").strip() if ex.exists() else None


def _state(m):
    """running | done | rejected (kapi RED) | gate_not_run | cancelled | failed. 'done' yalniz cikis kodu 0."""
    d = JOBS / m["id"]
    if _alive(m):
        return "running"
    code = _exit_code(d)
    if code == "0" and (d / "video.avi").exists():
        return "done"
    if m.get("cancelled") or code == "2":
        return "cancelled"
    return {"5": "rejected", "6": "gate_not_run"}.get(code, "failed")


def _q(a):
    """PowerShell tek tirnakli dize: tum tirnak benzerleri ikilenir."""
    return "'" + re.sub("([" + QUOTES + "])", r"\1\1", str(a)) + "'"


@mcp.tool()
def status() -> dict:
    """Motor, model dosyalari ve GPU durumunu raporlar; uretime hazir mi soyler."""
    files = {f: (MODEL / f).exists() for f in FILES}
    sd = (Path(os.environ.get("VT_ENGINE_BIN", ROOT / "engine" / "bin")) / "sd-cli.exe").exists()
    try:
        gpu = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.used,memory.total", "--format=csv,noheader"],
                             capture_output=True, text=True, timeout=10, creationflags=CF).stdout.strip()
    except Exception as e:
        gpu = f"okunamadi: {e}"
    running = [m["id"] for m in map(_meta, os.listdir(JOBS)) if m and _state(m) == "running"]
    return {"ready": sd and all(files.values()), "engine": sd, "models": files, "gpu": gpu,
            "running_jobs": running, "valid_frames": VALID, "fps": 24, "resolution": "640x384",
            "init_image": _IZIN.goster(_IZIN.izinli_klasorler(ROOT, os.environ.get("VT_MCP_INIT_DIR")), ROOT)}


@mcp.tool()
def generate_video(prompt: str, frames: int = 209, seed: int = 42, init_image: str = "") -> dict:
    """Metinden (veya init_image ile resimden/onceki klipten) video uretimini baslatir.
    frames 17k+5 (5..209; init_image ile en fazla 192). 24 fps, 640x384.
    Hemen job_id doner; ilerlemeyi job_status ile izleyin. Bitti sayilmak icin job_status state == "done" olmali
    (kapi RED ise "rejected"). Kapi lisans uygunlugunu denetlemez.
    init_image YALNIZ kullanicinin verdigi dosya yolu olabilir (kendin bir yol secme); VT_MCP_INIT_DIR doluysa
    yalniz <ROOT>/girdi/ ve listedeki klasorler kabul edilir (status() "init_image" alani hangi kipte oldugunu soyler)."""
    if frames not in VALID:
        return {"error": f"frames {VALID} icinden olmali"}
    if not prompt or not prompt.strip() or len(prompt) > 20000:
        return {"error": "prompt bos olamaz ve en fazla 20000 karakter"}
    if not 0 <= seed <= 2**31 - 1:
        return {"error": "seed 0..2147483647 olmali"}
    if init_image:
        if os.environ.get("VT_MCP_ALLOW_INIT", "1") != "1":
            return {"error": "init_image VT_MCP_ALLOW_INIT ayari ile kapatildi"}
        if frames > 192:
            return {"error": "init_image ile en fazla 192 kare"}
        if any(c in init_image for c in "\r\n\0"):
            return {"error": "init_image yolunda satir sonu/NUL olamaz"}
        # VT_MCP_INIT_DIR yoksa eski acik davranis (ayni iletiler); doluysa izinli klasor denetimi (mcp/init_izin.py)
        p, err = _IZIN.yol_coz(init_image, ROOT, _IZIN.izinli_klasorler(ROOT, os.environ.get("VT_MCP_INIT_DIR")))
        if err:
            return {"error": err}
        init_image = str(p)
    try:
        fd = os.open(LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        if time.time() - LOCK.stat().st_mtime < 120:
            return {"error": "baska bir baslatma suruyor"}
        LOCK.unlink(missing_ok=True)
        fd = os.open(LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    os.close(fd)
    try:
        return _start(prompt, frames, seed, init_image)
    finally:
        LOCK.unlink(missing_ok=True)


def _gpu_lock_busy():
    """uret.ps1'in kendi kilidi (elle calistirilan uret.ps1 dahil): runs/gpu.kilit PID'i canliysa PID, degilse None."""
    try:
        pid = int((ROOT / "runs" / "gpu.kilit").read_text(encoding="ascii", errors="ignore").split()[0])
    except (OSError, ValueError, IndexError):
        return None
    r = _proc_info(pid)
    return pid if r and r[0] else None


def _start(prompt, frames, seed, init_image):
    st = status()
    if not st["ready"]:
        return {"error": "hazir degil", "status": st}
    if st["running_jobs"]:
        return {"error": "GPU mesgul", "running_jobs": st["running_jobs"]}
    if (ROOT / "DUR").exists():
        return {"error": "ROOT/DUR dosyasi var (onceki durdurmadan kalmis olabilir); silin ya da bilerek duruyorsa bekleyin"}
    busy = _gpu_lock_busy()
    if busy:
        return {"error": f"GPU baska bir uret.ps1 tarafindan kullaniliyor (PID {busy})"}
    jid = time.strftime("%Y%m%d-%H%M%S-") + uuid.uuid4().hex[:6]
    d = JOBS / jid
    d.mkdir()
    (d / "istem.txt").write_text(prompt, encoding="utf-8")
    args = ["-Istem", str(d / "istem.txt"), "-Kare", str(frames), "-Seed", str(seed), "-Cikti", str(d / "video.avi")]
    if init_image:
        args += ["-InitImg", init_image]
    # Is basina run.ps1 (utf-8-sig). uret.ps1 throw ederse de cikis kodu yazilir (throw -> 1), hata metni log'a eklenir.
    body = " ".join(a if i % 2 == 0 else _q(a) for i, a in enumerate(args))  # cift indeks = sabit parametre adi
    lines = ["$ErrorActionPreference = 'Continue'",
             f"Set-Location -LiteralPath {_q(ROOT)}",
             "$k = 1",
             "try {",
             "    $global:LASTEXITCODE = $null",
             f"    & {_q(ROOT / 'scripts' / 'uret.ps1')} {body} *> {_q(d / 'log.txt')}",
             "    if ($null -ne $LASTEXITCODE) { $k = $LASTEXITCODE }",
             "} catch {",
             "    $k = 1",
             f"    ($_ | Out-String) | Out-File -LiteralPath {_q(d / 'log.txt')} -Append -Encoding Unicode",
             "}",
             f"Set-Content -LiteralPath {_q(d / 'exit.txt')} -Value $k -Encoding ASCII",
             "exit $k"]
    (d / "run.ps1").write_text("\r\n".join(lines) + "\r\n", encoding="utf-8-sig")
    # MCP surecinden bagimsiz yasasin; pencere yok; yol bir dizgeye gomulmez (tirnak sorunu yok)
    try:
        p = subprocess.Popen(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(d / "run.ps1")],
                             stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                             creationflags=CF | subprocess.CREATE_NEW_PROCESS_GROUP, close_fds=True)
    except OSError as e:
        return {"error": f"powershell baslatilamadi: {e}"}
    info = _proc_info(p.pid)
    m = {"id": jid, "pid": p.pid, "ctime": info[1] if info else None, "frames": frames, "seed": seed,
         "init_image": init_image, "started": time.strftime("%Y-%m-%dT%H:%M:%S"), "output": str(d / "video.avi")}
    (d / "job.json").write_text(json.dumps(m, ensure_ascii=False, indent=1), encoding="utf-8")
    return {"job_id": jid, "state": "running", "output": m["output"], "seconds": round(frames / 24, 2)}


@mcp.tool()
def job_status(job_id: str, log_lines: int = 15) -> dict:
    """Isin durumu (running/done/rejected/gate_not_run/failed/cancelled), cikti yolu, cikis kodu ve log sonu.
    Yalniz state == "done" kapidan gecmis videodur; "rejected" video var ama kapi RED (kabul edilmez)."""
    m = _meta(job_id)
    if not m:
        return {"error": "is yok"}
    lp = JOBS / job_id / "log.txt"
    tail = []
    if lp.exists():
        b = lp.read_bytes()
        enc = "utf-16" if b[:2] in (codecs.BOM_UTF16_LE, codecs.BOM_UTF16_BE) or b[1:2] == bytes(1) else "utf-8"
        tail = [l for l in b.decode(enc, errors="replace").splitlines() if l.strip()][-max(1, min(log_lines, 200)):]
    code = _exit_code(JOBS / job_id)
    state = _state(m)
    out = {**m, "state": state, "exit_code": code, "gate": None if code is None else GATE.get(code, f"HATA (kod {code})"),
           "log_tail": tail}
    if code in ("0", "5"):
        out["license_note"] = LISANS
    if state == "failed" and code is None:
        out["note"] = "cikis kodu yok: surec disaridan oldurulmus olabilir"
    return out


@mcp.tool()
def cancel_job(job_id: str) -> dict:
    """Calisan isi durdurur: once DUR dosyasi (uret.ps1 temiz kapanir, ~5-10 sn), olmazsa sure sonunda surec agaci sonlandirilir."""
    m = _meta(job_id)
    if not m:
        return {"error": "is yok"}
    if _state(m) != "running":
        return {"job_id": job_id, "state": _state(m), "note": "calismiyor; islem yapilmadi"}
    dur = ROOT / "DUR"
    dur.write_text("mcp", encoding="utf-8")
    forced = False
    try:
        end = time.time() + CANCEL_WAIT
        while time.time() < end and _alive(m):
            time.sleep(1)
        if _alive(m):  # nazik durdurma yetmedi (ornegin kapi/ffprobe asamasi): agaci kapat
            forced = True
            subprocess.run(["taskkill", "/PID", str(m["pid"]), "/T", "/F"], capture_output=True, creationflags=CF)
            for _ in range(10):
                if not _alive(m):
                    break
                time.sleep(0.5)
    finally:
        dur.unlink(missing_ok=True)
    if forced:  # zorla oldurulen uret.ps1 kendi kilidini silemez
        kilit = ROOT / "runs" / "gpu.kilit"
        try:
            if kilit.read_text(encoding="ascii", errors="ignore").split()[0] == str(m["pid"]):
                kilit.unlink(missing_ok=True)
        except (OSError, IndexError):
            pass
    if _exit_code(JOBS / job_id) not in ("0", "5", "6"):
        m["cancelled"] = True
        (JOBS / job_id / "job.json").write_text(json.dumps(m, ensure_ascii=False, indent=1), encoding="utf-8")
    return {"job_id": job_id, "state": _state(m), "forced_kill": forced}


@mcp.tool()
def list_jobs(limit: int = 10) -> list:
    """Son isleri listeler."""
    out = []
    for jid in sorted(os.listdir(JOBS), reverse=True)[:max(1, limit)]:
        m = _meta(jid)
        if m:
            out.append({"job_id": jid, "state": _state(m), "frames": m["frames"], "output": m["output"]})
    return out


if __name__ == "__main__":
    mcp.run()
