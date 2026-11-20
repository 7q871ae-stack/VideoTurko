@echo off
rem VideoTurko tani.cmd. EN: double-click, or run in cmd, to make a privacy-filtered diagnosis report (scripts\tani.ps1): it prints it and writes tani_raporu.txt in this folder. Drag that file into your issue. Nothing is sent anywhere. Extra flags go to scripts\tani.ps1, e.g. tani.cmd -Json or tani.cmd -KartSatiri.
rem TR: cift tikla ya da cmd icinde calistir; gizlilik suzgecinden gecmis bir teshis raporu uretir (scripts\tani.ps1): ekrana yazar ve bu klasorde tani_raporu.txt dosyasina kaydeder. Dosyayi issue'nuza surukleyin. Hicbir yere gonderilmez. Ek bayraklar scripts\tani.ps1 dosyasina gider, orn. tani.cmd -Json ya da tani.cmd -KartSatiri.
rem Exit codes / cikis kodlari: 0 report made / rapor uretildi, 6 could not run / calismadi. Env: VT_POWERSHELL, VT_NO_PAUSE=1, VT_PAUSE=1 (as in kur.cmd / kur.cmd ile ayni).
rem No labels and no multi-line blocks on purpose: this file still works if a download converted it to LF line endings.
setlocal
for /f "tokens=2 delims=:" %%a in ('chcp') do set "VT_ESKI_CP=%%a"
chcp 65001 >nul
cd /d "%~dp0"
if not defined VT_POWERSHELL set "VT_POWERSHELL=powershell.exe"
echo VideoTurko tani.cmd: making the report / rapor hazirlaniyor (about 10 s / yaklasik 10 sn). Nothing is sent / hicbir sey gonderilmez.
call "%VT_POWERSHELL%" -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\tani.ps1" -Cikti "%~dp0tani_raporu.txt" %*
set "VT_KOD=%ERRORLEVEL%"
echo.
echo File / dosya: tani_raporu.txt (this folder / bu klasor). Read it, then drag it into your issue / okuyun, sonra issue'ya surukleyin. Filter is a rough pattern, not a guarantee / suzgec kaba bir desendir, garanti degil.
chcp %VT_ESKI_CP% >nul
set "VT_CIFT="
echo %cmdcmdline% | "%SystemRoot%\System32\find.exe" /i "%~f0" >nul && set "VT_CIFT=1"
if "%VT_PAUSE%"=="1" set "VT_CIFT=1"
if "%VT_NO_PAUSE%"=="1" set "VT_CIFT="
if defined VT_CIFT pause
endlocal & exit /b %VT_KOD%
