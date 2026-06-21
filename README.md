# VoxCPM2 Voice Cloner

用 VoxCPM2 克隆你的聲音，生成任意語音。全自動安裝，自動偵測 GPU。

**錄音走 UI，其他全部透過 AI Agent 自然語言操作。**

## 特色

- **自動偵測 GPU**：NVIDIA CUDA / Intel Arc XPU / CPU 三種模式自動切換
- ** Ultimate Cloning**：同時使用參考音 + 逐字稿，連語氣節奏都一起複製
- **網頁錄音**：`app.py` 提供簡潔錄音介面（取名 → 看稿 → 錄音 → 儲存）
- **自然語言操作**：錄完後，直接對 AI Agent 說「用王老師的聲音說一段話」，Agent 自動呼叫工具
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

## 快速開始（雙擊即可）

### 1. 安裝

雙擊 `install.bat`（或 `install.ps1`）。自動完成所有設定。

### 2. 錄音

雙擊 `start.bat` → 瀏覽器打開 → 取名 → 對著麥克風念稿 → 儲存。

預設朗讀稿約 60 字，使用簡體中文課堂講解語氣，適合老師直接錄製參考音。

錄音保存時會做輕量前處理：

- 轉成 16kHz 單聲道
- 移除固定麥克風偏移
- 裁掉開頭和結尾的長靜音
- 將音量標準化，避免聲音過小或過爆

這不是深度 AI 降噪。若環境噪音很大，最有效的做法仍是靠近麥克風、關閉風扇/空調直吹、使用耳麥或指向性麥克風，並重新錄一段乾淨參考音。

### 3. 使用（透過 AI Agent）

錄完後，直接對 AI Agent 說：

```
用王老師的聲音說「同學們早安，今天我們來上數學課」
```

Agent 會自動找到對應聲音、生成語音、回傳音檔。

> 💡 本專案設計為 **AI Agent 工具包**，人類只做錄音，其他交給 Agent。
5. 若為 Intel Arc，自動套用 XPU patch

### 2. 錄製參考音

有兩種方式：

**方式 A：網頁介面（推薦）**

```powershell
.\.venv\Scripts\python.exe webui_record.py
```

瀏覽器自動開啟，有錄音按鈕、逐字稿顯示，錄完自動存檔。

**方式 B：命令列**

```powershell
.\.venv\Scripts\python.exe record.py --voice 我的聲音
```

螢幕會顯示一段文字，對著麥克風自然地朗讀，念完按 Enter 停止。

### 3. 生成克隆語音

```powershell
.\.venv\Scripts\python.exe clone.py "你好，這是我的克隆聲音。" --voice 我的聲音
```

或從文字檔生成：

```powershell
.\.venv\Scripts\python.exe clone.py --file my_script.txt
```

輸出檔案預設在 `output/cloned_voice.wav`。

## 目錄結構

```
voxcpm2-voice-cloner/
├── app.py                    # 錄音 UI（唯一介面）
├── clone.py                  # Agent 工具：用聲音生成語音
├── dialogue.py               # Agent 工具：多聲音對話
├── record.py                 # 命令列錄音（備案）
├── start.bat                 # 雙擊啟動錄音 UI
├── install.bat               # 雙擊安裝
├── install.ps1               # 自動偵測 GPU + 安裝依賴
├── AGENTS.md                 # Agent 使用指南
├── texts/sample_text.txt     # 錄音時朗讀的文字
├── voices/                   # 已錄製的聲音（本地，不進版控）
├── patches/                  # Intel Arc XPU 支援
└── output/                   # 生成的語音
```

## 命令列工具（替代方案，不需 GUI 時可用）

## GPU 支援對照

| GPU | 模式 | PyTorch | 需要 patch | 效能（參考） |
|-----|------|---------|-----------|-------------|
| NVIDIA (CUDA 12+) | cuda | cu128 wheel | 不需要 | RTF ~0.3（RTX 4090） |
| Intel Arc (XPU) | xpu | xpu wheel | 需要（自動） | RTF ~2.0（Arc 140T） |
| AMD Radeon / Ryzen 內顯（Windows） | cpu | cpu wheel | 不需要 | 依 CPU 而定，通常較慢 |
| 無獨顯 | cpu | cpu wheel | 不需要 | RTF ~8.0 |

> RTF = 生成 N 秒語音所需的時間倍率，越低越快。

## AMD 電腦加速說明

在 Windows 上，AMD Radeon 內顯或獨顯目前不會被本專案自動用來加速 VoxCPM2。安裝腳本會安全地回落到 CPU 模式，能用但生成較慢。

可立即採用的提速方式：

- 生成短句時分段生成，再把音檔拼接到課件或剪輯工具中
- 儘量使用乾淨、時長適中的參考音，減少模型處理負擔
- 關閉其他大型程式，讓 CPU 和記憶體留給推理
- 若需要大量生成，優先使用 NVIDIA CUDA 或已驗證的 Intel Arc XPU 環境

待確認的 AMD GPU 路線：

- **ROCm**：主要面向 Linux，Windows 支援和模型相容性需逐機型確認
- **DirectML**：可能支援部分 PyTorch 工作流，但 VoxCPM2 目前沒有內建 DirectML 路徑
- **ONNX / 量化**：需要額外導出和驗證模型，屬於後續工程工作

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
