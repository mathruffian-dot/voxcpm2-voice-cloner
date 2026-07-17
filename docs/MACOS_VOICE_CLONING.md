# macOS Apple Silicon 聲音克隆指南

本指南適用於 Apple Silicon Mac。模型、聲音樣本與輸出音檔只保留在本機，不會提交到 Git。

> 只能克隆本人聲音，或已取得聲音本人明確同意的聲音。對外發布時應標示為 AI 合成語音，不得用於冒充、詐騙或誤導。

## 系統需求

- Apple Silicon Mac
- 建議至少 16 GB 記憶體
- 約 10 GB 可用空間
- 瀏覽器與麥克風
- 首次下載模型約 4.7 GB

## 安裝

在 Finder 中雙擊 `install_mac.command`。它會：

1. 安裝 `uv`。
2. 建立 Python 3.12 虛擬環境。
3. 安裝 PyTorch、VoxCPM、Gradio 與聲音處理套件。
4. 將預設裝置設為 Apple MPS。

也可以在終端機執行：

```bash
./install_mac.command
```

## 錄製參考聲音

1. 雙擊 `start_mac.command`。
2. 保持終端機視窗開啟。
3. 在瀏覽器開啟 `http://127.0.0.1:7860`。
4. 輸入聲音名稱並允許麥克風權限。
5. 自然朗讀完整文字後儲存。

建議錄音 15–30 秒、16 kHz、單聲道、無背景音樂。`prompt.txt` 必須與實際錄音逐字一致。

錄音會儲存在：

```text
voices/<聲音名稱>/ref_voice.wav
voices/<聲音名稱>/prompt.txt
```

## 生成克隆語音

Apple Silicon 建議使用 MPS 半精度，以降低記憶體需求：

```bash
source .venv/bin/activate
VOXCPM_MPS_DTYPE=float16 python clone.py \
  "要生成的內容" \
  --voice "聲音名稱" \
  --output "output/result.wav" \
  --device mps
```

例如：

```bash
VOXCPM_MPS_DTYPE=float16 .venv/bin/python clone.py \
  "嗨，大家好。希望你今天心情愉快。" \
  --voice "小葵的聲音" \
  --output "output/小葵_問候.wav" \
  --device mps
```

VoxCPM 官方程式指出 MPS 半精度可能有數值偏差，完成後必須人工試聽。若有異常，可改用 CPU：

```bash
.venv/bin/python clone.py \
  "要生成的內容" \
  --voice "聲音名稱" \
  --output "output/result.wav" \
  --device cpu
```

CPU 相容性較高，但 Apple Silicon 上可能非常慢。

## 讓 AI Agent 操作

將這個 GitHub 專案交給 AI Agent 後，可以使用自然語言指令：

```text
請依照 AGENTS.md 與 docs/MACOS_VOICE_CLONING.md 安裝環境，
使用「小葵的聲音」說「嗨，大家好」，並回傳生成的 WAV 音檔。
```

Agent 應依序：

1. 確認聲音本人已同意克隆。
2. 確認 `voices/<名稱>/ref_voice.wav` 與 `prompt.txt` 存在。
3. 使用 Python 3.12 虛擬環境。
4. Apple Silicon 優先嘗試 MPS `float16`。
5. 將成果寫入 `output/`，並回傳音檔。

聲音樣本不會存在 GitHub。每位使用者仍需在自己的電腦錄音，或自行安全地提供已獲授權的參考音檔。

## 常見問題

### `127.0.0.1` 拒絕連線

確認 `start_mac.command` 的終端機視窗仍開著，且出現：

```text
Running on local URL: http://127.0.0.1:7860
```

### 找不到聲音

```bash
ls voices
```

`--voice` 後面的名稱必須與資料夾名稱完全一致。

### MPS out of memory

關閉占用大量記憶體的程式，並確認已設定 `VOXCPM_MPS_DTYPE=float16`。不要解除 PyTorch MPS 記憶體安全上限，以免系統失去回應。

### 第一次生成很久

第一次會下載約 4.7 GB 模型。每次新程序仍需重新載入模型；生成短句測試後，再分段處理長內容。
