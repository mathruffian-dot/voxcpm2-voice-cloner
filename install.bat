@echo off
chcp 65001 >nul
title VoxCPM2 Voice Cloner - 安裝中...
cd /d "%~dp0"

echo ============================================
echo   VoxCPM2 Voice Cloner - 一鍵安裝
echo ============================================
echo.
echo 本安裝需要：
echo   - Python 3.10~3.12（若無會自動用 uv 安裝）
echo   -約 5GB 硬碟空間（模型權重）
echo   - 麥克風
echo.

:: ========== 檢查 Python ==========
where python >nul 2>&1
if errorlevel 1 (
    echo [錯誤] 找不到 Python，請先安裝 Python 3.10~3.12
    echo 下載: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo Python 已就緒，開始安裝...
echo.

:: ========== 執行安裝腳本 ==========
where pwsh >nul 2>&1
if errorlevel 1 (
    powershell.exe -ExecutionPolicy Bypass -File "install.ps1"
) else (
    pwsh -ExecutionPolicy Bypass -File "install.ps1"
)

if errorlevel 1 (
    echo.
    echo [錯誤] 安裝失敗，請查看上方錯誤訊息。
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================
echo   安裝完成！
echo   關閉此視窗，雙擊 start.bat 即可使用。
echo ============================================
echo.
pause
