# VoxCPM2 Voice Cloner

用 VoxCPM2 克隆你的聲音，生成任意語音。全自動安裝，自動偵測 GPU，零程式碼操作。

## 特色

- **自動偵測 GPU**：NVIDIA CUDA / Intel Arc XPU / CPU 三種模式自動切換
- ** Ultimate Cloning**：同時使用參考音 + 逐字稿，連語氣節奏都一起複製
- **麥克風錄音**：內建錄音腳本，給你一段文字朗讀即可，逐字稿自動取得
- **Apache-2.0 授權**：VoxCPM2 模型可商用

## 系統需求

- Windows 10/11（Linux/Mac 可自行調整 install 腳本）
- Python 3.10–3.12（安裝腳本會用 uv 自動建立 3.12 環境）
- 顯卡（擇一）：
  - NVIDIA GPU（CUDA 12+，約 8GB VRAM）
  - Intel Arc GPU（XPU，約 8GB VRAM，需自動 patch）
  - 無獨顯也可用 CPU（較慢，RTF 約 8x）
- 約 5GB 硬碟空間（模型權重）
- 麥克風

## 快速開始

### 1. 安裝

```powershell
git clone https://github.com/mathruffian-dot/voxcpm2-voice-cloner.git
cd voxcpm2-voice-cloner
.\install.ps1
```

安裝腳本會自動：
1. 建立 Python 3.12 虛擬環境
2. 偵測你的 GPU 類型
3. 安裝對應版本的 PyTorch
4. 安裝 voxcpm + sounddevice
5. 若為 Intel Arc，自動套用 XPU patch

### 2. 錄製參考音

```powershell
.\.venv\Scripts\python.exe record.py
```

螢幕會顯示一段文字，請對著麥克風自然地朗讀。錄完會存成 `ref_voice.wav`。

> 你念的文字就是逐字稿，不需要額外做語音辨識。

### 3. 生成克隆語音

```powershell
.\.venv\Scripts\python.exe clone.py "你好，這是我的克隆聲音。"
```

或從文字檔生成：

```powershell
.\.venv\Scripts\python.exe clone.py --file my_script.txt
```

輸出檔案預設在 `output/cloned_voice.wav`。

## 目錄結構

```
voxcpm2-voice-cloner/
├── install.ps1              # 自動安裝腳本（偵測 GPU + 建環境）
├── record.py                # 麥克風錄音，取得參考音 + 逐字稿
├── clone.py                 # Ultimate Cloning 語音生成
├── texts/
│   └── sample_text.txt      # 給使用者朗讀的範例文字
├── patches/
│   ├── utils.py             # XPU device 支援 patch（Intel Arc 用）
│   └── repatch_xpu.ps1      # voxcpm 更新後自動重 patch
├── output/                  # 生成的語音輸出於此
├── ref_voice.wav            # 錄音後產生（.gitignore 排除）
└── .gpu_type                # 安裝時記錄的 GPU 類型（.gitignore 排除）
```

## GPU 支援對照

| GPU | 模式 | PyTorch | 需要 patch | 效能（參考） |
|-----|------|---------|-----------|-------------|
| NVIDIA (CUDA 12+) | cuda | cu128 wheel | 不需要 | RTF ~0.3（RTX 4090） |
| Intel Arc (XPU) | xpu | xpu wheel | 需要（自動） | RTF ~2.0（Arc 140T） |
| 無獨顯 | cpu | cpu wheel | 不需要 | RTF ~8.0 |

> RTF = 生成 N 秒語音所需的時間倍率，越低越快。

## Intel Arc (XPU) 注意事項

VoxCPM2 官方目前只支援 NVIDIA CUDA。Intel Arc 的 XPU 支援透過 patch 實現：

- `install.ps1` 會自動套用 patch
- 若 `pip install -U voxcpm` 更新了套件，patch 會被覆蓋
- 執行 `patches\repatch_xpu.ps1` 即可恢復：

```powershell
.\patches\repatch_xpu.ps1
```

### 根治計畫

本專案已向 [OpenBMB/VoxCPM](https://github.com/OpenBMB/VoxCPM) 提交 XPU 支援 PR（對應 [Issue #215](https://github.com/OpenBMB/VoxCPM/issues/215)）。官方合併後，patch 機制將自動退役，`pip install voxcpm` 即原生支援 Intel Arc。

## 授權

- VoxCPM2 模型與程式碼：[Apache-2.0](https://github.com/OpenBMB/VoxCPM/blob/main/LICENSE)（可商用）
- 本專案腳本：MIT
