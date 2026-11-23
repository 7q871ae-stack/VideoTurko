# VideoTurko kart.ps1: kart tanima ve scripts/kart_tablosu.json okuma. kur.ps1 ve uret.ps1 tarafindan nokta-kaynak (dot-source) yuklenir; tek basina calistirilmaz.
# EN: card parsing + lookup in the single data table scripts/kart_tablosu.json. Read-only: writes nothing, starts nothing, needs no network.
# Kalite ayarlari (6 adim, cfg 1, 640x384, karosuz VAE) bu tabloda yoktur: hicbir kartta degismez.

function Kart-CcOku([string]$s) {
    # "8.6" ya da "8,6" -> 8.6; okunamazsa -1.0
    $v = 0.0
    if ([double]::TryParse(("$s").Trim().Replace(',', '.'), [Globalization.NumberStyles]::Float, [Globalization.CultureInfo]::InvariantCulture, [ref]$v)) { return $v }
    return -1.0
}
function Kart-Satir-Coz([string]$satir) {
    # nvidia-smi --query-gpu=name,memory.total,driver_version,compute_cap --format=csv,noheader,nounits satiri.
    # Ad virgul icerebilir: son uc alan vram, surucu, cc; geri kalani ad. Okunamazsa $null.
    $f = @(("$satir") -split ',' | ForEach-Object { $_.Trim() })
    if ($f.Count -lt 2) { return $null }
    $cc = ''; $surucu = ''; $vramS = ''
    if ($f.Count -ge 4) { $cc = $f[$f.Count - 1]; $surucu = $f[$f.Count - 2]; $vramS = $f[$f.Count - 3]; $ad = ($f[0..($f.Count - 4)] -join ', ') }
    else { $ad = $f[0]; $vramS = $f[1] }
    $vram = 0.0
    if (-not [double]::TryParse($vramS, [Globalization.NumberStyles]::Float, [Globalization.CultureInfo]::InvariantCulture, [ref]$vram)) { $vram = -1.0 }
    return @{ ad = $ad; vram = $vram; surucu = $surucu; cc = (Kart-CcOku $cc) }
}
function Kart-Uretici([string]$ad) {
    # Kart adindan uretici: nvidia | amd | diger
    if ($ad -match 'NVIDIA|GeForce|GTX|RTX|Quadro|Tesla|\bTITAN\b') { return 'nvidia' }
    if ($ad -match 'AMD|Radeon|\bRX\s?\d|Instinct') { return 'amd' }
    return 'diger'
}
function Kart-Tablo-Oku([string]$yol) {
    return (Get-Content -LiteralPath $yol -Raw -Encoding UTF8 | ConvertFrom-Json)
}
function Kart-Sinif($tablo, [string]$uretici, [double]$cc) {
    # Sonuc: tablo satiri (id, motor, ek_ayar, durum, kanit, belge). nvidia + okunamayan cc -> nvidia_cc_okunamadi; bilinmeyen uretici -> diger_uretici.
    if ($uretici -eq 'nvidia') {
        if ($cc -lt 0) { return $tablo.nvidia_cc_okunamadi }
        foreach ($k in $tablo.kartlar) { if ($k.uretici -eq 'nvidia' -and $cc -ge [double]$k.cc_min -and $cc -lt [double]$k.cc_max) { return $k } }
        return $null   # 6.1 altindaki kart (kur.ps1 zaten reddeder)
    }
    if ($uretici -eq 'amd') { foreach ($k in $tablo.kartlar) { if ($k.uretici -eq 'amd') { return $k } } }
    return $tablo.diger_uretici
}
function Kart-Durum($sinif, [string]$ad) {
    # dogrulanmis | topluluk | denenmemis. 'dogrulanmis' yalniz sinifin dogrulanmis_kartlar listesindeki ada sahip kart icin gecerli (ayni mimarinin baska karti denenmemis sayilir).
    if ($null -eq $sinif) { return 'denenmemis' }
    if ($sinif.durum -eq 'dogrulanmis') {
        foreach ($d in @($sinif.dogrulanmis_kartlar)) { if ($ad -like "*$d*") { return 'dogrulanmis' } }
        return 'denenmemis'
    }
    return [string]$sinif.durum
}
function Kart-Ek-Env($sinif) {
    # Sinifin ek_ayar.env tablosu -> sirali hashtable (bos olabilir)
    $h = [ordered]@{}
    if ($sinif -and $sinif.ek_ayar -and $sinif.ek_ayar.env) { foreach ($p in $sinif.ek_ayar.env.PSObject.Properties) { $h[$p.Name] = [string]$p.Value } }
    return $h
}
function Kart-Ek-Model-Arg($sinif, [string]$ad) {
    # Sinifin ek_ayar.model_args.<ad> degeri ya da ''
    if ($sinif -and $sinif.ek_ayar -and $sinif.ek_ayar.model_args) { $p = $sinif.ek_ayar.model_args.PSObject.Properties[$ad]; if ($p) { return [string]$p.Value } }
    return ''
}
