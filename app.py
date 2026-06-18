#!/usr/bin/env python3
"""
app.py - VoxCPM2 Voice Cloner 完整網頁工具（簡潔友善版）
雙擊 start.bat → 打開瀏覽器 → 三步完成所有操作

用法：
  python app.py              # http://127.0.0.1:7860
  python app.py --port 8080
"""

import os, sys, time, threading, argparse
import numpy as np
import gradio as gr

REPO_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLE_RATE = 16000

# ────────────────────────────────────────────
#  Custom CSS for cleaner UI
# ────────────────────────────────────────────
CUSTOM_CSS = """
body { font-family: 'Segoe UI', 'Microsoft JhengHei', sans-serif; }
h2 { margin-top: 0.5em; color: #1a1a2e; }
.step-box {
    background: #f8f9fa; border-radius: 12px; padding: 20px; margin: 12px 0;
    border: 1px solid #e0e0e0;
}
.step-number {
    display: inline-block; width: 32px; height: 32px; line-height: 32px;
    text-align: center; background: #4a90d9; color: white; border-radius: 50%;
    font-weight: bold; margin-right: 8px;
}
.success-msg { color: #2d8a56; font-weight: bold; }
.error-msg { color: #c0392b; font-weight: bold; }
.hint { color: #888; font-size: 0.9em; }
.voice-card {
    padding: 8px 16px; margin: 4px 0; background: #e8f0fe;
    border-radius: 8px; font-size: 1.05em;
}
"""

# ────────────────────────────────────────────
#  Model (lazy-loaded, shared by all tabs)
# ────────────────────────────────────────────
_model = None
_model_lock = threading.Lock()
_device_info = None


def detect_device():
    gpu_type_file = os.path.join(REPO_DIR, ".gpu_type")
    if os.path.exists(gpu_type_file):
        with open(gpu_type_file, "r", encoding="utf-8") as f:
            return f.read().strip()
    import torch
    if torch.cuda.is_available():
        return "cuda"
    if hasattr(torch, "xpu") and torch.xpu.is_available():
        return "xpu"
    return "cpu"


def load_model(progress=None):
    global _model, _device_info
    if _model is not None:
        return _model, _device_info
    with _model_lock:
        if _model is not None:
            return _model, _device_info
        if progress:
            progress(0.1, desc="正在下載/載入 AI 模型（首次約需 2 分鐘）...")
        from voxcpm import VoxCPM
        dev = detect_device()
        if progress:
            progress(0.3, desc=f"模型載入中...（裝置: {dev}）")
        _model = VoxCPM.from_pretrained(
            "openbmb/VoxCPM2", load_denoiser=False, device=dev, optimize=False
        )
        dev_labels = {"cuda": "NVIDIA 顯卡", "xpu": "Intel 顯卡", "cpu": "CPU（較慢）"}
        _device_info = dev_labels.get(dev, dev)
        return _model, _device_info


# ────────────────────────────────────────────
#  Voice helpers
# ────────────────────────────────────────────
def list_voices():
    vdir = os.path.join(REPO_DIR, "voices")
    if not os.path.exists(vdir):
        return []
    voices = []
    for name in sorted(os.listdir(vdir)):
        p = os.path.join(vdir, name)
        if os.path.isdir(p) and os.path.exists(os.path.join(p, "ref_voice.wav")):
            voices.append(name)
    return voices


def get_voice_files(name):
    vdir = os.path.join(REPO_DIR, "voices", name)
    wav = os.path.join(vdir, "ref_voice.wav")
    prompt = os.path.join(vdir, "prompt.txt")
    txt = ""
    if os.path.exists(prompt):
        with open(prompt, "r", encoding="utf-8") as f:
            txt = f.read().strip()
    return wav, txt


def load_sample_text():
    path = os.path.join(REPO_DIR, "texts", "sample_text.txt")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    return ""


# ────────────────────────────────────────────
#  Recording
# ────────────────────────────────────────────
def on_save_record(audio_mic, audio_upload, voice_name):
    audio_data = audio_mic or audio_upload
    if audio_data is None:
        return "⚠️ 請先按「開始錄音」按鈕，對著麥克風朗讀，錄完再按儲存。"
    if not voice_name or not voice_name.strip():
        return "⚠️ 請為你的聲音取一個名字。"
    name = voice_name.strip()

    try:
        sr, audio = audio_data
        if audio.ndim > 1:
            audio = audio.mean(axis=1)
        if sr != SAMPLE_RATE:
            import resampy
            audio = resampy.resample(audio, sr, SAMPLE_RATE)
        peak = np.abs(audio).max()
        if peak > 0 and peak < 0.01:
            return "⚠️ 錄到的音量太小，請靠近麥克風再錄一次。"
        if peak > 0:
            audio = audio / peak * 0.95

        vdir = os.path.join(REPO_DIR, "voices", name)
        os.makedirs(vdir, exist_ok=True)
        import soundfile as sf
        wav_path = os.path.join(vdir, "ref_voice.wav")
        sf.write(wav_path, audio.astype(np.float32), SAMPLE_RATE)
        prompt_path = os.path.join(vdir, "prompt.txt")
        with open(prompt_path, "w", encoding="utf-8") as f:
            f.write(load_sample_text())

        duration = len(audio) / SAMPLE_RATE
        return f"✅ 聲音「{name}」錄製成功！時長 {duration:.0f} 秒。\n\n👉 請切換到「生成語音」分頁開始使用。"
    except Exception as e:
        return f"❌ 儲存失敗：{e}"


# ────────────────────────────────────────────
#  Generation
# ────────────────────────────────────────────
def on_generate(voice_name, gen_text, progress=gr.Progress()):
    if not voice_name:
        return None, "⚠️ 請先「錄製聲音」，再來生成。"
    if not gen_text or not gen_text.strip():
        return None, "⚠️ 請輸入你想讓 AI 說的話。"
    try:
        progress(0.00, desc="載入 AI 模型中...")
        model, dev_info = load_model(progress)
        ref_wav, prompt_text = get_voice_files(voice_name)
        if not os.path.exists(ref_wav):
            return None, f"⚠️ 找不到「{voice_name}」的聲音檔。請先錄製。"

        progress(0.30, desc="正在生成語音...")
        t0 = time.time()
        wav = model.generate(
            text=gen_text.strip(),
            prompt_wav_path=ref_wav,
            prompt_text=prompt_text,
            reference_wav_path=ref_wav,
            cfg_value=1.5,
            inference_timesteps=10,
        )
        elapsed = time.time() - t0
        duration = len(wav) / model.tts_model.sample_rate

        import soundfile as sf
        out_path = os.path.join(REPO_DIR, "output", f"{voice_name}_{int(time.time())}.wav")
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        sf.write(out_path, wav, model.tts_model.sample_rate)

        info = f"✅ 完成！用「{voice_name}」的聲音生成，長度 {duration:.0f} 秒，花了 {elapsed:.0f} 秒。\n裝置: {dev_info}"
        return (model.tts_model.sample_rate, wav), info
    except Exception as e:
        return None, f"❌ 生成失敗：{e}"


# ────────────────────────────────────────────
#  Dialogue
# ────────────────────────────────────────────
def on_dialogue(script, progress=gr.Progress()):
    lines = []
    for line in script.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        sep = "：" if "：" in line else ":" if ":" in line else None
        if not sep:
            continue
        speaker, text = line.split(sep, 1)
        lines.append((speaker.strip(), text.strip()))

    if len(lines) < 2:
        return None, "⚠️ 請至少寫兩句對話，格式：說話者：內容"

    try:
        progress(0.00, desc="載入模型中...")
        model, _ = load_model(progress)

        speakers = set(s for s, _ in lines)
        voice_data = {}
        for spk in speakers:
            ref_wav, prompt_text = get_voice_files(spk)
            if not os.path.exists(ref_wav):
                return None, f"⚠️ 找不到「{spk}」的聲音。請先錄製。"
            voice_data[spk] = (ref_wav, prompt_text)

        clips = []
        for i, (speaker, text) in enumerate(lines):
            progress(0.1 + 0.85 * (i / len(lines)), desc=f"生成 {speaker} 的台詞中...")
            ref_wav, prompt_text = voice_data[speaker]
            wav = model.generate(
                text=text,
                prompt_wav_path=ref_wav,
                prompt_text=prompt_text,
                reference_wav_path=ref_wav,
                cfg_value=1.5,
                inference_timesteps=10,
            )
            pause = np.zeros(int(0.35 * model.tts_model.sample_rate), dtype=wav.dtype)
            clips.append(wav)
            clips.append(pause)

        full_audio = np.concatenate(clips)
        duration = len(full_audio) / model.tts_model.sample_rate

        import soundfile as sf
        out_path = os.path.join(REPO_DIR, "output", f"dialogue_{int(time.time())}.wav")
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        sf.write(out_path, full_audio, model.tts_model.sample_rate)

        return (model.tts_model.sample_rate, full_audio), f"✅ 對話完成！{len(lines)} 句，共 {duration:.0f} 秒。"
    except Exception as e:
        return None, f"❌ 生成失敗：{e}"


# ────────────────────────────────────────────
#  UI
# ────────────────────────────────────────────
def build_ui():
    sample_text = load_sample_text()
    current_voices = list_voices()

    with gr.Blocks(title="VoxCPM2 Voice Cloner", css=CUSTOM_CSS) as app:
        # ── Header ──
        gr.HTML("""
        <div style="text-align:center; margin-bottom:24px;">
          <h1 style="font-size:2em; margin-bottom:4px;">🎙️ VoxCPM2 語音複製工具</h1>
          <p style="font-size:1.1em; color:#666;">對著螢幕念一段文字，AI 就能用你的聲音說話。</p>
        </div>
        """)

        with gr.Tabs():
            # ═══════════════ TAB 1: 錄製 ═══════════════
            with gr.Tab("1. 錄製我的聲音", id="tab_record"):
                with gr.Column(elem_classes="step-box"):
                    gr.Markdown("## ✏️ 為你的聲音取個名字")
                    voice_name_input = gr.Textbox(
                        label="聲音名稱（例如：王老師、林主任）",
                        placeholder="取一個好記的名字...",
                    )

                with gr.Column(elem_classes="step-box"):
                    gr.Markdown("## 📖 請念這段文字")
                    gr.Markdown(
                        "💡 **請大聲、清楚地念出下面這段話。這段文字會用來訓練 AI 模仿你的語氣。**"
                    )
                    gr.Markdown(
                        f'<div style="background:#fff3cd; padding:16px; border-radius:8px; '
                        f'font-size:1.15em; line-height:2; margin:8px 0;">'
                        f'{sample_text}</div>'
                    )

                with gr.Column(elem_classes="step-box"):
                    gr.Markdown("## 🎤 錄音並儲存")
                    gr.Markdown("按下面這個按鈕開始錄音，念完按停止。")

                    audio_mic = gr.Audio(
                        label="",
                        type="numpy",
                        sources=["microphone"],
                        show_label=False,
                    )

                    gr.Markdown(
                        '<div style="text-align:center; margin-top:12px;">'
                        '👆 錄完後，按下面這個按鈕儲存 👇'
                        '</div>'
                    )
                    with gr.Row():
                        save_btn = gr.Button("⬇️ 儲存聲音", variant="primary", size="lg")

                    with gr.Accordion("或上傳已錄好的音檔（如果有麥克風問題）", open=False):
                        gr.Markdown("如果你已經用其他方式錄好聲音，可以直接上傳 WAV 或 MP3 檔。")
                        audio_upload = gr.Audio(
                            label="",
                            type="numpy",
                            sources=["upload"],
                            show_label=False,
                        )

                save_msg = gr.Textbox(label="", show_label=False, lines=3, interactive=False)

                save_btn.click(
                    fn=on_save_record,
                    inputs=[audio_mic, audio_upload, voice_name_input],
                    outputs=[save_msg],
                )

            # ═══════════════ TAB 2: 生成 ═══════════════
            with gr.Tab("2. 生成語音", id="tab_generate"):
                with gr.Column(elem_classes="step-box"):
                    gr.Markdown("## 🗣️ 選擇聲音")
                    voice_count = len(current_voices)
                    if voice_count == 0:
                        gr.Markdown(
                            "⚠️ **還沒有錄製任何聲音。**\n\n"
                            "請先切換到「錄製我的聲音」分頁，錄下你的聲音。"
                        )
                    else:
                        gr.Markdown(f"已錄製 **{voice_count}** 個聲音，請選擇一個：")

                    voice_select = gr.Dropdown(
                        label="",
                        choices=current_voices,
                        value=current_voices[0] if current_voices else None,
                        show_label=False,
                    )

                with gr.Column(elem_classes="step-box"):
                    gr.Markdown("## ✍️ 輸入文字")
                    gr.Markdown("寫下你想讓 AI 用你的聲音說的話。")
                    gen_text_input = gr.Textbox(
                        label="",
                        placeholder="例如：各位同學好，今天我們要來談一個很有趣的主題...",
                        lines=4,
                        show_label=False,
                    )

                gen_btn = gr.Button("開始生成語音", variant="primary", size="lg")
                gen_audio_output = gr.Audio(label="", show_label=False, interactive=False)
                gen_info = gr.Textbox(label="", show_label=False, lines=3, interactive=False)

                gen_btn.click(
                    fn=on_generate,
                    inputs=[voice_select, gen_text_input],
                    outputs=[gen_audio_output, gen_info],
                )

            # ═══════════════ TAB 3: 對話 ═══════════════
            with gr.Tab("3. 多人對話", id="tab_dialogue"):
                with gr.Column(elem_classes="step-box"):
                    gr.Markdown("## 💬 編寫對話腳本")
                    gr.Markdown(
                        "每行寫一句，格式：**說話者名稱：內容**\n"
                        "系統會自動用對應的聲音生成每一句，然後拼接成完整對話。"
                    )
                    dialogue_input = gr.Textbox(
                        label="",
                        value=(
                            "王老師：同學們，今天我們要分組討論。\n"
                            "林主任：沒錯，請大家先看一下桌上的講義。\n"
                            "王老師：有問題的可以隨時舉手發問喔。\n"
                            "林主任：好，那我們現在開始吧。"
                        ),
                        lines=8,
                        show_label=False,
                    )

                dialogue_btn = gr.Button("開始生成對話", variant="primary", size="lg")
                dialogue_audio = gr.Audio(label="", show_label=False, interactive=False)
                dialogue_info = gr.Textbox(label="", show_label=False, lines=2, interactive=False)

                dialogue_btn.click(
                    fn=on_dialogue,
                    inputs=[dialogue_input],
                    outputs=[dialogue_audio, dialogue_info],
                )

        # ── Footer ──
        gr.HTML("""
        <div style="text-align:center; margin-top:32px; padding:16px; color:#999; font-size:0.85em;">
          VoxCPM2 Voice Cloner &mdash; 使用 Apache-2.0 授權，可自由商用 |
          <a href="https://github.com/mathruffian-dot/voxcpm2-voice-cloner" target="_blank">GitHub</a>
        </div>
        """)

    return app


def main():
    parser = argparse.ArgumentParser(description="VoxCPM2 Voice Cloner")
    parser.add_argument("--port", "-p", type=int, default=7860)
    parser.add_argument("--share", action="store_true")
    args = parser.parse_args()

    app = build_ui()
    app.launch(server_port=args.port, share=args.share, theme=gr.themes.Soft())


if __name__ == "__main__":
    main()
