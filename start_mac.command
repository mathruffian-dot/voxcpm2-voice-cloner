#!/bin/zsh

set -e
cd "${0:A:h}"

if [[ ! -x .venv/bin/python ]]; then
  echo "找不到 Python 環境，請先完成安裝。"
  read "?按 Enter 關閉..."
  exit 1
fi

echo "正在啟動 VoxCPM2 錄音介面..."
echo "若瀏覽器沒有自動開啟，請前往 http://127.0.0.1:7860"
echo "關閉此視窗即可停止服務。"
.venv/bin/python app.py --port 7860
