#!/usr/bin/env python3
"""
clone.py - 用 VoxCPM2 Ultimate Cloning 生成你的克隆語音。

預設使用「三師爸」聲音。也可以用 --voice 指定其他聲音，或用 --reference/--text-file 自訂。

用法：
  python clone.py "你好，這是我的克隆聲音。"
  python clone.py "文字" --voice 三師爸
  python clone.py --file my_script.txt
  python clone.py "文字" --output output/my_voice.wav
  python clone.py "文字" --reference my_ref.wav --text-file my_ref_text.txt
"""

import os
import sys
import time
import argparse

REPO_DIR = os.path.dirname(os.path.abspath(__file__))

def detect_device():
    """從 install.ps1 產生的 .gpu_type 讀取，或自動偵測。"""
    gpu_type_file = os.path.join(REPO_DIR, '.gpu_type')
    if os.path.exists(gpu_type_file):
        with open(gpu_type_file, 'r', encoding='utf-8') as f:
            gpu_type = f.read().strip()
    else:
        import torch
        if torch.cuda.is_available():
            gpu_type = 'cuda'
        elif hasattr(torch, 'xpu') and torch.xpu.is_available():
            gpu_type = 'xpu'
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            gpu_type = 'mps'
        else:
            gpu_type = 'cpu'

    device_map = {'cuda': 'cuda', 'xpu': 'xpu', 'mps': 'mps', 'cpu': 'cpu'}
    return device_map.get(gpu_type, 'cpu')


def resolve_voice_files(voice, reference_override, text_override):
    """根據 voice 名稱解析參考音和逐字稿路徑。"""
    voice_dir = os.path.join(REPO_DIR, 'voices', voice)
    reference = reference_override or os.path.join(voice_dir, 'ref_voice.wav')
    text_file = text_override or os.path.join(voice_dir, 'prompt.txt')
    return reference, text_file


def main():
    parser = argparse.ArgumentParser(description='VoxCPM2 Ultimate Cloning 語音生成')
    parser.add_argument('text', nargs='?', help='要生成的文字')
    parser.add_argument('--file', '-f', help='從文字檔讀取要生成的內容')
    parser.add_argument('--output', '-o', default='output/cloned_voice.wav',
                        help='輸出檔案路徑（預設: output/cloned_voice.wav）')
    parser.add_argument('--voice', '-v', default='三師爸',
                        help='聲音名稱，對應 voices/ 目錄（預設: 三師爸）')
    parser.add_argument('--reference', '-r',
                        help='覆蓋參考音檔路徑（預設由 --voice 決定）')
    parser.add_argument('--text-file', '-t',
                        help='覆蓋逐字稿檔案路徑（預設由 --voice 決定）')
    parser.add_argument('--device', '-d', help='強制指定裝置 (cuda/xpu/mps/cpu)')
    args = parser.parse_args()

    # 取得要生成的文字
    if args.file:
        with open(args.file, 'r', encoding='utf-8') as f:
            gen_text = f.read().strip()
    elif args.text:
        gen_text = args.text
    else:
        print('錯誤：請提供要生成的文字，或用 --file 指定文字檔。')
        print('範例: python clone.py "你好，這是我的克隆聲音。"')
        sys.exit(1)

    # 根據 voice 名稱解析參考音和逐字稿
    reference, text_file = resolve_voice_files(args.voice, args.reference, args.text_file)

    # 檢查參考音檔
    if not os.path.exists(reference):
        print(f'錯誤：找不到參考音檔 {reference}')
        if args.voice:
            print(f'請先錄製「{args.voice}」聲音: python record.py --voice {args.voice}')
        sys.exit(1)

    # 讀取逐字稿
    if not os.path.exists(text_file):
        print(f'錯誤：找不到逐字稿檔案 {text_file}')
        sys.exit(1)
    with open(text_file, 'r', encoding='utf-8') as f:
        prompt_text = f.read().strip()

    # 偵測裝置
    device = args.device or detect_device()

    # 載入模型
    from voxcpm import VoxCPM
    import soundfile as sf

    print(f'聲音: {args.voice}')
    print(f'裝置: {device}')
    print('載入 VoxCPM2 模型（首次會下載權重，約 4.7GB）...')
    t0 = time.time()
    model = VoxCPM.from_pretrained(
        'openbmb/VoxCPM2',
        load_denoiser=False,
        device=device,
        optimize=False,
    )
    print(f'模型載入完成，耗時 {time.time()-t0:.1f}s')

    # 生成語音
    print(f'生成中（{len(gen_text)} 字）...')
    t1 = time.time()
    wav = model.generate(
        text=gen_text,
        prompt_wav_path=reference,
        prompt_text=prompt_text,
        reference_wav_path=reference,
        cfg_value=2.0,
        inference_timesteps=10,
    )
    elapsed = time.time() - t1
    duration = len(wav) / model.tts_model.sample_rate
    print(f'生成完成，耗時 {elapsed:.1f}s（語音長度 {duration:.1f}s，RTF={elapsed/duration:.1f}）')

    # 存檔
    os.makedirs(os.path.dirname(args.output) or '.', exist_ok=True)
    sf.write(args.output, wav, model.tts_model.sample_rate)
    print(f'已存檔: {args.output}')


if __name__ == '__main__':
    main()
