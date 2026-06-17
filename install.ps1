# install.ps1 - VoxCPM2 Voice Cloner 自動安裝腳本
# 自動偵測 GPU 類型，安裝對應的 PyTorch + voxcpm
#
# 用法：.\install.ps1
#
# GPU 偵測邏輯：
#   NVIDIA (CUDA)  → pip install torch --index-url .../cu128
#   Intel Arc (XPU)→ pip install torch --index-url .../xpu + 自動 patch
#   無獨顯 (CPU)   → pip install torch --index-url .../cpu

$ErrorActionPreference = 'Stop'
$venvName = '.venv'
$venvPython = Join-Path $venvName 'Scripts\python.exe'
$venvPip = Join-Path $venvName 'Scripts\pip.exe'

Write-Host ''
Write-Host '============================================' -ForegroundColor Cyan
Write-Host '  VoxCPM2 Voice Cloner - Auto Installer' -ForegroundColor Cyan
Write-Host '============================================' -ForegroundColor Cyan
Write-Host ''

# --- Step 1: 檢查 uv ---
Write-Host '[1/6] 檢查 uv 套件管理器...' -ForegroundColor Yellow
$uv = Get-Command uv -ErrorAction SilentlyContinue
if (-not $uv) {
    Write-Host '  uv 未安裝，正在安裝...' -ForegroundColor Yellow
    pip install -U uv
} else {
    Write-Host "  uv 已安裝: $($uv.Source)" -ForegroundColor Green
}

# --- Step 2: 建立 Python 3.12 venv ---
Write-Host '[2/6] 建立 Python 3.12 虛擬環境...' -ForegroundColor Yellow
if (Test-Path $venvPython) {
    Write-Host "  $venvName 已存在，跳過建立。" -ForegroundColor Green
} else {
    uv venv --python 3.12 $venvName
    Write-Host "  venv 建立完成: $venvName" -ForegroundColor Green
}

# --- Step 3: 偵測 GPU ---
Write-Host '[3/6] 偵測 GPU 類型...' -ForegroundColor Yellow
$gpuType = 'cpu'
$gpuName = ''

$videoControllers = Get-CimInstance Win32_VideoController -ErrorAction SilentlyContinue
foreach ($vc in $videoControllers) {
    $name = $vc.Name
    if ($name -match 'NVIDIA') {
        $gpuType = 'cuda'
        $gpuName = $name
        break
    }
    if ($name -match 'Intel.*Arc|Arc.*Intel|Arc\(TM\)') {
        $gpuType = 'xpu'
        $gpuName = $name
        break
    }
}

switch ($gpuType) {
    'cuda' {
        Write-Host "  偵測到 NVIDIA GPU: $gpuName" -ForegroundColor Green
        Write-Host '  → 安裝 CUDA 版 PyTorch' -ForegroundColor Green
        $torchIndex = 'https://download.pytorch.org/whl/cu128'
    }
    'xpu' {
        Write-Host "  偵測到 Intel Arc GPU: $gpuName" -ForegroundColor Green
        Write-Host '  → 安裝 XPU 版 PyTorch（含自動 patch）' -ForegroundColor Green
        $torchIndex = 'https://download.pytorch.org/whl/xpu'
    }
    default {
        Write-Host '  未偵測到獨立 GPU，使用 CPU 模式。' -ForegroundColor Yellow
        Write-Host '  → 安裝 CPU 版 PyTorch（推理會較慢）' -ForegroundColor Yellow
        $torchIndex = 'https://download.pytorch.org/whl/cpu'
    }
}

# --- Step 4: 安裝 PyTorch ---
Write-Host '[4/6] 安裝 PyTorch...' -ForegroundColor Yellow
$torchVer = if ($gpuType -eq 'xpu') { 'torch==2.12.0+xpu' } else { 'torch' }
if ($gpuType -eq 'xpu') {
    uv pip install --python $venvPython $torchVer --index-url $torchIndex
} else {
    uv pip install --python $venvPython torch --index-url $torchIndex
}
Write-Host "  PyTorch 安裝完成。" -ForegroundColor Green

# --- Step 5: 安裝 voxcpm + sounddevice ---
Write-Host '[5/6] 安裝 voxcpm + sounddevice...' -ForegroundColor Yellow
uv pip install --python $venvPython voxcpm sounddevice
Write-Host "  voxcpm + sounddevice 安裝完成。" -ForegroundColor Green

# --- Step 6: XPU 自動 patch ---
if ($gpuType -eq 'xpu') {
    Write-Host '[6/6] 套用 XPU patch...' -ForegroundColor Yellow
    $repatchScript = Join-Path $PSScriptRoot 'patches\repatch_xpu.ps1'
    if (Test-Path $repatchScript) {
        & $repatchScript
    } else {
        Write-Host '  警告: 找不到 patches\repatch_xpu.ps1，跳過 patch。' -ForegroundColor Red
        Write-Host '  Intel Arc GPU 需要手動執行 patch 才能使用。' -ForegroundColor Red
    }
} else {
    Write-Host '[6/6] 無需 patch（非 XPU 模式）。' -ForegroundColor Green
}

# --- 驗證 ---
Write-Host ''
Write-Host '============================================' -ForegroundColor Cyan
Write-Host '  安裝完成！' -ForegroundColor Cyan
Write-Host '============================================' -ForegroundColor Cyan
Write-Host ''
Write-Host 'GPU 模式: ' -NoNewline
switch ($gpuType) {
    'cuda' { Write-Host 'NVIDIA CUDA' -ForegroundColor Green }
    'xpu'  { Write-Host 'Intel XPU (patched)' -ForegroundColor Green }
    default { Write-Host 'CPU（較慢）' -ForegroundColor Yellow }
}
Write-Host ''
Write-Host '下一步：' -ForegroundColor Cyan
Write-Host '  1. 錄製參考音：.\.venv\Scripts\python.exe record.py'
Write-Host '  2. 生成語音：.\.venv\Scripts\python.exe clone.py "你想說的文字"'
Write-Host ''

# 儲存 GPU 類型供其他腳本讀取
[IO.File]::WriteAllText((Join-Path $PSScriptRoot '.gpu_type'), $gpuType)
