@echo off
rem VideoTurko uret.cmd. EN: drag a prompt .txt file onto this file (or: uret.cmd prompt.txt) to make a FIRST video of 56 frames (about 11 min on a GTX 1050 Ti). With other arguments they go to scripts\uret.ps1 unchanged, e.g. uret.cmd -Istem x.txt -Kare 209.
rem TR: istem .txt dosyasini bu dosyanin ustune surukle (ya da: uret.cmd istem.txt): 56 karelik ILK video uretir (GTX 1050 Ti uzerinde yaklasik 11 dk). Baska arguman verirsen scripts\uret.ps1 dosyasina aynen gider, orn. uret.cmd -Istem x.txt -Kare 209.
rem Exit codes / cikis kodlari: 0 ok, 1 error, 2 stopped (DUR), 5 quality gate RED, 6 gate could not run. Codes: docs\SIK_HATALAR.md
rem Env: VT_POWERSHELL, VT_NO_PAUSE=1, VT_PAUSE=1 (see kur.cmd). No labels and no multi-line blocks on purpose (LF-safe).
setlocal
for /f "tokens=2 delims=:" %%a in ('chcp') do set "VT_ESKI_CP=%%a"
chcp 65001 >nul
cd /d "%~dp0"
if not defined VT_POWERSHELL set "VT_POWERSHELL=powershell.exe"
set "VT_KOD=0"
set "VT_CIFT="
echo %cmdcmdline% | "%SystemRoot%\System32\find.exe" /i "%~f0" >nul && set "VT_CIFT=1"
if "%~1"=="" echo VideoTurko uret.cmd: drag your prompt .txt file onto uret.cmd, or run: uret.cmd docs\ornek_istem_R0.txt  / istem .txt dosyani uret.cmd uzerine surukle ya da: uret.cmd docs\ornek_istem_R0.txt
if "%~1"=="" echo First video = 56 frames, about 11 min on a GTX 1050 Ti / ilk video = 56 kare, GTX 1050 Ti uzerinde yaklasik 11 dk. Other options: scripts\uret.ps1 -Istem ... -Kare ...
if not "%~1"=="" if "%~2"=="" if exist "%~1" echo VideoTurko uret.cmd: first video, 56 frames / ilk video, 56 kare: %~1
if not "%~1"=="" if "%~2"=="" if exist "%~1" call "%VT_POWERSHELL%" -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\uret.ps1" -Istem "%~1" -Kare 56
if not "%~1"=="" if "%~2"=="" if exist "%~1" set "VT_KOD=%ERRORLEVEL%"
if not "%~1"=="" if "%~2"=="" if not exist "%~1" echo File not found / dosya bulunamadi: %~1 . Usage / kullanim: uret.cmd docs\ornek_istem_R0.txt
if not "%~1"=="" if "%~2"=="" if not exist "%~1" set "VT_KOD=1"
if not "%~1"=="" if not "%~2"=="" call "%VT_POWERSHELL%" -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\uret.ps1" %*
if not "%~1"=="" if not "%~2"=="" set "VT_KOD=%ERRORLEVEL%"
echo.
echo Exit code / cikis kodu: %VT_KOD%  (0 = ok / tamam, 2 = stopped / durduruldu, 5 = quality gate RED / kalite kapisi RED, 6 = gate could not run / kapi calisamadi)
echo Codes and fixes / kodlar ve cozumler: docs\SIK_HATALAR.md
chcp %VT_ESKI_CP% >nul
if "%VT_PAUSE%"=="1" set "VT_CIFT=1"
if "%VT_NO_PAUSE%"=="1" set "VT_CIFT="
if defined VT_CIFT pause
endlocal & exit /b %VT_KOD%
