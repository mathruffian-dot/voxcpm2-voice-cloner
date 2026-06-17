#!/usr/bin/env python3
"""
record.py - 麥克風錄音，取得 Ultimate Cloning 所需的參考音與逐字稿。

流程：
  1. 螢幕顯示一段固定文字（texts/sample_text.txt）
  2. 使用者對著麥克風朗讀
  3. 存成 ref_voice.wav（16kHz 單聲道）
  4. 文字內容即為逐字稿（prompt_text），不需 ASR

用法：
  python record.py              # 使用預設文字
  python record.py my_text.txt  # 使用自訂文字檔
"""

import os
import sys
import time
import wave
import numpy as np

SAMPLE_RATE = 16000
RECORD_SECONDS = 20
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), 'ref_voice.wav')


def load_text(filepath=None):
    """載入要朗讀的文字。"""
    if filepath is None:
        filepath = os.path.join(os.path.dirname(__file__), 'texts', 'sample_text.txt')
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read().strip()


def record_audio(seconds=RECORD_SECONDS, sr=SAMPLE_RATE):
    """從系統麥克風錄音，回傳 numpy array。"""
    import sounddevice as sd

    print(f'\n即將錄音 {seconds} 秒，取樣率 {sr}Hz。')
    print('準備好後按 Enter 開始...')
    input()

    print('錄音中...（請開始朗讀上面的文字）')
    print(f'剩餘: {seconds} 秒', end='', flush=True)
    audio = sd.rec(int(seconds * sr), samplerate=sr, channels=1, dtype=np.float32)
    for i in range(seconds, 0, -1):
        print(f'\r剩餘: {i:2d} 秒', end='', flush=True)
        time.sleep(1)
    print('\r錄音完成！          ')
    sd.wait()
    return audio.flatten()


def save_wav(audio, filepath, sr=SAMPLE_RATE):
    """存成 WAV 檔。"""
    audio_int16 = (audio * 32767).astype(np.int16)
    with wave.open(filepath, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(audio_int16.tobytes())
    duration = len(audio) / sr
    print(f'已存檔: {filepath} ({duration:.1f}s, {sr}Hz)')


def main():
    text_file = sys.argv[1] if len(sys.argv) > 1 else None
    text = load_text(text_file)

    print('=' * 60)
    print('  VoxCPM2 Voice Cloner - 參考音錄製')
    print('=' * 60)
    print()
    print('請朗讀以下文字（這段文字會作為逐字稿，請盡量自然地念）：')
    print()
    print('-' * 60)
    print(text)
    print('-' * 60)
    print()
    print(f'字數: {len(text.replace(" ", "").replace(",", "").replace("。", ""))} 字')
    print(f'預計朗讀時間: 約 {len(text) // 5} 秒')

    audio = record_audio()
    save_wav(audio, OUTPUT_FILE)

    print()
    print('參考音錄製完成！')
    print(f'  音檔: {OUTPUT_FILE}')
    print(f'  逐字稿: {text_file or "texts/sample_text.txt"}')
    print()
    print('下一步：執行 clone.py 生成你的克隆語音。')


if __name__ == '__main__':
    main()
