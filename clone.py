#!/usr/bin/env python3
"""
clone.py - 用 VoxCPM2 Ultimate Cloning 生成你的克隆語音。

需要先執行 record.py 錄製參考音。

用法：
  python clone.py "你好，這是我的克隆聲音。"
  python clone.py --file my_script.txt
  python clone.py "文字" --output output/my_voice.wav
"""

import os
import sys
import time
import argparse

def detect_device():
    """從 install.ps1 產生的 .gpu_type 讀取，或自動偵測。"""
    gpu_type_file = os.path.join(os.path.dirname(__file__), '.gpu_type')
    if os.path.exists(gpu_type_file):
        with open(gpu_type_file, 'r', encoding='utf-8') as f:
            gpu_type = f.read().strip()
    else:
        import torch
        if torch.cuda.is_available():
            gpu_type = 'cuda'
        elif hasattr(torch, 'xpu') and torch.xpu.is_available():
            gpu_type = 'xpu'
        else:
            gpu_type = 'cpu'

    device_map = {'cuda': 'cuda', 'xpu': 'xpu', 'cpu': 'cpu'}
    return device_map.get(gpu_type, 'cpu')


def main():
    parser = argparse.ArgumentParser(description='VoxCPM2 Ultimate Cloning 語音生成')
    parser.add_argument('text', nargs='?', help='要生成的文字')
    parser.add_argument('--file', '-f', help='從文字檔讀取要生成的內容')
    parser.add_argument('--output', '-o', default='output/cloned_voice.wav',
                        help='輸出檔案路徑（預設: output/cloned_voice.wav）')
    parser.add_argument('--reference', '-r', default='ref_voice.wav',
                        help='參考音檔路徑（預設: ref_voice.wav）')
    parser.add_argument('--text-file', '-t', default='texts/sample_text.txt',
                        help='參考音的逐字稿檔案（預設: texts/sample_text.txt）')
    parser.add_argument('--device', '-d', help='強制指定裝置 (cuda/xpu/cpu)')
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

    # 檢查參考音檔
    if not os.path.exists(args.reference):
        print(f'錯誤：找不到參考音檔 {args.reference}')
        print('請先執行: python record.py')
        sys.exit(1)

    # 讀取逐字稿
    if not os.path.exists(args.text_file):
        print(f'錯誤：找不到逐字稿檔案 {args.text_file}')
        sys.exit(1)
    with open(args.text_file, 'r', encoding='utf-8') as f:
        prompt_text = f.read().strip()

    # 偵測裝置
    device = args.device or detect_device()

    # 載入模型
    from voxcpm import VoxCPM
    import soundfile as sf

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
        prompt_wav_path=args.reference,
        prompt_text=prompt_text,
        reference_wav_path=args.reference,
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
