#!/bin/zsh

set -e
cd "${0:A:h}"

UV="$HOME/.local/bin/uv"

if [[ ! -x "$UV" ]]; then
  echo "正在安裝 uv..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
fi

echo "正在建立 Python 3.12 環境..."
"$UV" venv --python 3.12 .venv

echo "正在安裝 VoxCPM2 與錄音介面..."
"$UV" pip install --python .venv/bin/python \
  torch voxcpm sounddevice resampy gradio soundfile

echo "mps" > .gpu_type

echo ""
echo "安裝完成。請雙擊 start_mac.command 啟動錄音介面。"
read "?按 Enter 關閉..."
