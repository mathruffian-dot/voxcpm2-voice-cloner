@echo off
chcp 65001 >nul
title VoxCPM2 Voice Cloner - 啟動中...
cd /d "%~dp0"

:: ========== 檢查是否已安裝 ==========
if not exist ".venv\Scripts\python.exe" (
    echo ========================================
    echo   尚未安裝，請先雙擊 install.bat
    echo ========================================
    echo.
    pause
    exit /b 1
)

:: ========== 檢查是否有已錄製的聲音 ==========
if not exist "voices" (
    mkdir voices
)
set HAS_VOICE=0
for /d %%d in (voices\*) do (
    if exist "%%d\ref_voice.wav" set HAS_VOICE=1
)
if %HAS_VOICE%==0 (
    echo ========================================
    echo   尚未錄製聲音！
    echo   請先在 app.py 中錄製你的參考音。
    echo ========================================
    echo.
)

:: ========== 關閉舊的伺服器（如果有的話） ==========
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :7860') do (
    taskkill /f /pid %%a 2>nul
)

:: ========== 啟動伺服器 ==========
echo 正在啟動 VoxCPM2 Voice Cloner...
start "VoxCPM2 Server" ".venv\Scripts\python.exe" app.py

:: ========== 等待伺服器啟動 ==========
echo 等待伺服器啟動中...
:wait
timeout /t 1 /nobreak >nul
curl -s http://127.0.0.1:7860 >nul 2>&1
if errorlevel 1 goto wait

:: ========== 開啟瀏覽器 ==========
echo 啟動完成！正在打開瀏覽器...
start http://127.0.0.1:7860

echo.
echo 視窗可以關閉，伺服器會在背景持續執行。
echo 若要停止，按 Ctrl+C 或關閉「VoxCPM2 Server」視窗。
timeout /t 5 >nul
