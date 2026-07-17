# Agents：VoxCPM2 Voice Cloner 使用指南

本專案提供三個工具，Agent 應根據使用者自然語言指令自動選用。

## 首次設定

- Windows 10/11：執行 `install.bat` 或 `install.ps1`。
- Apple Silicon macOS：執行 `install_mac.command`。
- 完整跨平台說明：`docs/VOICE_CLONING_GUIDE.md`。
- 開始前必須確認聲音本人已同意被克隆；不得用於冒充、詐騙或誤導。

## 工具清單

### 1. clone.py — 用已錄製的聲音生成語音

```bash
python clone.py "要生成的文字" --voice <聲音名稱>
```

- `<聲音名稱>`：對應 `voices/<名稱>/` 目錄
- 輸出：`output/cloned_voice.wav`
- 首次執行會自動下載 VoxCPM2 模型（約 4.7GB）

範例：
```bash
python clone.py "同學們早安，今天我們來上數學課。" --voice 王老師
```

### 2. dialogue.py — 用多個聲音生成對話

```bash
python dialogue.py
```

- 預設使用 `三師爸` 和 `三帥媽` 的聲音
- 輸出：`output/dialogue_三師爸_三帥媽.wav`
- 若要自訂對話內容，編輯 `dialogue.py` 中的 `dialogue` 清單

### 3. record.py — 命令列錄音（無 UI 備案）

```bash
python record.py --voice <聲音名稱>
```

## 聲音管理

- 已錄製的聲音列表：`ls voices/`（目錄名即聲音名稱）
- 每個聲音目錄包含：
  - `ref_voice.wav` — 參考音檔（16kHz 單聲道）
  - `prompt.txt` — 逐字稿（錄音時念的文字）

## 裝置偵測

執行 clone.py 時會自動偵測裝置：
- NVIDIA GPU → CUDA 模式
- Intel Arc GPU → XPU 模式（需 patch，install.ps1 已處理）
- Apple Silicon → MPS 模式；記憶體不足時使用 `VOXCPM_MPS_DTYPE=float16`
- 無獨顯 → CPU 模式（較慢）

macOS MPS 範例：

```bash
VOXCPM_MPS_DTYPE=float16 .venv/bin/python clone.py "要生成的文字" --voice "聲音名稱" --device mps
```

## 常見使用者指令對照

| 使用者說的 | Agent 應執行的 |
|-----------|---------------|
| 用王老師的聲音說「同學們早安」 | `python clone.py "同學們早安" --voice 王老師` |
| 讓王老師跟林主任對話 | 編輯 `dialogue.py` 的對話清單 → `python dialogue.py` |
| 錄製新的聲音 | 引導使用者開啟 `http://127.0.0.1:7860` 或執行 `record.py --voice <名稱>` |
| 有哪些已錄製的聲音 | `ls voices/` |
