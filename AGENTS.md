# Agents：VoxCPM2 Voice Cloner 使用指南

本專案提供三個工具，Agent 應根據使用者自然語言指令自動選用。

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

- 預設用 `voices/` 內的前兩個聲音（用 `--a`、`--b` 指定聲音名；`voices/` 不進版控，請先自行錄製或用 voice design 生成）
- 輸出：`output/dialogue_<A>_<B>.wav`
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

執行 clone.py 或 dialogue.py 時會自動偵測裝置：
- NVIDIA GPU → CUDA 模式
- Intel Arc GPU → XPU 模式（需 patch，install.ps1 已處理）
- 無獨顯 → CPU 模式（較慢）

## 常見使用者指令對照

| 使用者說的 | Agent 應執行的 |
|-----------|---------------|
| 用王老師的聲音說「同學們早安」 | `python clone.py "同學們早安" --voice 王老師` |
| 讓王老師跟林主任對話 | 編輯 `dialogue.py` 的對話清單 → `python dialogue.py` |
| 錄製新的聲音 | 引導使用者開啟 `http://127.0.0.1:7860` 或執行 `record.py --voice <名稱>` |
| 有哪些已錄製的聲音 | `ls voices/` |
