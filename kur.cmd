@echo off
rem VideoTurko kur.cmd. EN: double-click, or run in cmd, to install (engine, models, 5-frame check). Extra flags go to scripts\kur.ps1, e.g. kur.cmd -Kuru (dry run: reports only, changes nothing).
rem TR: cift tikla ya da cmd icinde calistir; kurulum yapar (motor, modeller, 5 karelik kontrol). Ek bayraklar scripts\kur.ps1 dosyasina gider, orn. kur.cmd -Kuru (kuru calisma: yalniz rapor, hicbir sey degistirmez).
rem Exit codes / cikis kodlari: 0 ok, 1 error, 2 license not accepted, 3 hardware or disk, 4 stopped. Codes: docs\SIK_HATALAR.md
rem Env: VT_POWERSHELL (path to powershell.exe if it is not on PATH), VT_NO_PAUSE=1 (never wait for a key), VT_PAUSE=1 (always wait).
rem No labels and no multi-line blocks on purpose: this file still works if a download converted it to LF line endings.
setlocal
for /f "tokens=2 delims=:" %%a in ('chcp') do set "VT_ESKI_CP=%%a"
chcp 65001 >nul
cd /d "%~dp0"
if not defined VT_POWERSHELL set "VT_POWERSHELL=powershell.exe"
echo VideoTurko kur.cmd: starting scripts\kur.ps1 / scripts\kur.ps1 basliyor. %*
call "%VT_POWERSHELL%" -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\kur.ps1" %*
set "VT_KOD=%ERRORLEVEL%"
echo.
echo Exit code / cikis kodu: %VT_KOD%  (0 = ok / tamam, 2 = license not accepted / lisans kabul edilmedi, 3 = hardware or disk not enough / donanim ya da disk yetersiz, 4 = stopped / durduruldu)
echo Codes and fixes / kodlar ve cozumler: docs\SIK_HATALAR.md
rem Double-click detection runs BEFORE the code page is restored: on a non-Turkish OEM code page the Turkish letters in the path no longer match.
set "VT_CIFT="
echo %cmdcmdline% | "%SystemRoot%\System32\find.exe" /i "%~f0" >nul && set "VT_CIFT=1"
chcp %VT_ESKI_CP% >nul
if "%VT_PAUSE%"=="1" set "VT_CIFT=1"
if "%VT_NO_PAUSE%"=="1" set "VT_CIFT="
if defined VT_CIFT pause
endlocal & exit /b %VT_KOD%
