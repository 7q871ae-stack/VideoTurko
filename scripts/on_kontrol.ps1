# VideoTurko on_kontrol.ps1 (pre-pull-request check / PR oncesi yerel kontrol)
# EN: Runs the repository checks (scripts/denetim.py --hizli) the way the maintainers' gate does. A few seconds, no GPU,
#     no network, writes no files. Run it before you open a pull request:
#       powershell -NoProfile -ExecutionPolicy Bypass -File scripts\on_kontrol.ps1
#     Needs Python 3 (python.org or the Microsoft Store). Optional: set VT_PYTHON to the python.exe you want to use.
# TR: Depo kontrollerini (scripts/denetim.py --hizli) bakimcilarin kapisiyla ayni sekilde calistirir. Birkac saniye,
#     GPU yok, ag yok, dosya yazmaz. Pull request acmadan once calistirin (komut yukarida).
#     Python 3 gerekir. Istege bagli: VT_PYTHON ile kullanmak istediginiz python.exe yolunu verin.
# Exit codes / cikis kodlari: 0 all green / hepsi yesil, 1 RED (a check found something) / KIRMIZI (bir kontrol bulgu verdi),
#   3 Python not found / Python bulunamadi, 6 a check could not run, not green / bir kontrol calismadi, yesil sayilmaz.
# Safe: it only reads files. It does not open windows, touch git, or change anything.
$ErrorActionPreference = 'Stop'
$kok = Split-Path -Parent $PSScriptRoot
$betik = Join-Path $PSScriptRoot 'denetim.py'

function Test-Python {
    param([string]$Yol, [string[]]$On)
    try {
        $c = Get-Command $Yol -ErrorAction Stop
        if ($c.CommandType -ne 'Application') { return $false }
        # The Microsoft Store stub is a python.exe that opens the Store instead of running: a real run tells them apart.
        $cikti = & $c.Source @On -I -c "import sys; print(sys.version_info[0])" 2>$null
        return ($LASTEXITCODE -eq 0 -and "$cikti".Trim() -eq '3')
    } catch { return $false }
}

$py = $null; $on = @()
if ($env:VT_PYTHON) {
    if (Test-Python $env:VT_PYTHON @()) { $py = (Get-Command $env:VT_PYTHON).Source }
} else {
    if (Test-Python 'py' @('-3')) { $py = (Get-Command 'py').Source; $on = @('-3') }
    elseif (Test-Python 'python' @()) { $py = (Get-Command 'python').Source }
}

if (-not $py) {
    Write-Host 'HATA: [VT-E-PYTHON] Python 3 bulunamadi. / Python 3 was not found.'
    Write-Host '  EN: Install Python 3 (https://www.python.org/downloads/, tick "Add python.exe to PATH"), open a NEW terminal and run this again.'
    Write-Host '      If Python is installed elsewhere, set VT_PYTHON to its python.exe path first.'
    Write-Host '  TR: Python 3 kurun (https://www.python.org/downloads/, "Add python.exe to PATH" kutusunu isaretleyin), YENI bir terminal acip tekrar calistirin.'
    Write-Host '      Python baska yerdeyse once VT_PYTHON ortam degiskenine python.exe yolunu yazin.'
    Write-Host 'SONUC: PYTHON YOK (cikis 3) / NO PYTHON (exit 3). You can still open the pull request; the maintainers run the same check. / Yine de PR acabilirsiniz; bakimcilar ayni kontrolu calistirir.'
    exit 3
}

Push-Location $kok
try {
    & $py @on -I -X utf8 $betik --hizli
    $kod = $LASTEXITCODE
} finally {
    Pop-Location
}

Write-Host ''
if ($kod -eq 0) {
    Write-Host 'on_kontrol: GECTI / PASSED (exit 0). Your change passes the quick local checks; this is not a security guarantee. / Degisiklik yerel hizli kontrolleri gecti; guvenlik garantisi degildir.'
} elseif ($kod -eq 1) {
    Write-Host 'on_kontrol: KIRMIZI / RED (exit 1). Fix the lines marked above, then run it again. Stuck? Open the pull request anyway and paste the output. / Yukaridaki isaretli satirlari duzeltip tekrar calistirin. Takildiysaniz PR acin, ciktiyi yapistirin.'
} else {
    Write-Host ('on_kontrol: KONTROL CALISMADI / A CHECK DID NOT RUN (exit ' + $kod + '): not green. Paste the output into your pull request. / Yesil sayilmaz; ciktiyi PR aciklamasina yapistirin.')
}
exit $kod
