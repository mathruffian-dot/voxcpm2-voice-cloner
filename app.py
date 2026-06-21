#!/usr/bin/env python3
"""
app.py - VoxCPM2 語音錄製工具
唯一的 UI：錄音 + 儲存。克隆與生成交由 AI Agent 處理。

用法：
  python app.py              # http://127.0.0.1:7860
"""

import os
import numpy as np
import gradio as gr

REPO_DIR = os.path.dirname(os.path.abspath(__file__))
SAMPLE_RATE = 16000

CUSTOM_CSS = """
body { font-family: 'Segoe UI', 'Microsoft JhengHei', sans-serif; }
.step-box { background:#f8f9fa; border-radius:12px; padding:20px; margin:12px 0; border:1px solid #e0e0e0; }
.success-msg { color:#2d8a56; font-weight:bold; }
"""


def list_voices():
    vdir = os.path.join(REPO_DIR, "voices")
    if not os.path.exists(vdir):
        return []
    return sorted(
        d for d in os.listdir(vdir)
        if os.path.isdir(os.path.join(vdir, d))
        and os.path.exists(os.path.join(vdir, d, "ref_voice.wav"))
    )


def load_sample_text():
    path = os.path.join(REPO_DIR, "texts", "sample_text.txt")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    return ""


def preprocess_audio(audio):
    audio = np.asarray(audio, dtype=np.float32)
    if len(audio) == 0:
        return audio, 0.0

    # Remove constant microphone offset, then trim only leading/trailing silence.
    audio = audio - float(np.mean(audio))
    peak = float(np.abs(audio).max())
    if peak <= 0:
        return audio, peak

    threshold = max(peak * 0.015, 0.003)
    voiced = np.flatnonzero(np.abs(audio) > threshold)
    if voiced.size:
        pad = int(SAMPLE_RATE * 0.2)
        start = max(0, int(voiced[0]) - pad)
        end = min(len(audio), int(voiced[-1]) + pad)
        audio = audio[start:end]
        peak = float(np.abs(audio).max())

    if peak > 0:
        audio = audio / peak * 0.95
    return audio, peak


def on_save(audio_mic, audio_upload, voice_name):
    audio_data = audio_mic or audio_upload
    if audio_data is None:
        return "⚠️ 請先按「開始錄音」錄下你的聲音。"
    if not voice_name or not voice_name.strip():
        return "⚠️ 請為你的聲音取一個名字。"

    name = voice_name.strip()
    try:
        if isinstance(audio_data, (str, os.PathLike)):
            import soundfile as sf
            audio, sr = sf.read(audio_data)
        else:
            sr, audio = audio_data

        if audio.ndim > 1:
            audio = audio.mean(axis=1)
        if sr != SAMPLE_RATE:
            import resampy
            audio = resampy.resample(audio, sr, SAMPLE_RATE)
        audio, peak = preprocess_audio(audio)
        if peak > 0 and peak < 0.01:
            return "⚠️ 錄到的音量太小，請靠近麥克風再錄一次。"

        vdir = os.path.join(REPO_DIR, "voices", name)
        os.makedirs(vdir, exist_ok=True)
        import soundfile as sf
        sf.write(os.path.join(vdir, "ref_voice.wav"), audio.astype(np.float32), SAMPLE_RATE)
        with open(os.path.join(vdir, "prompt.txt"), "w", encoding="utf-8") as f:
            f.write(load_sample_text())

        duration = len(audio) / SAMPLE_RATE
        existing = list_voices()
        voice_list = "、".join(existing)
        return (
            f"✅ 聲音「{name}」錄製成功！（{duration:.0f} 秒）\n\n"
            f"目前已錄製的聲音：{voice_list}\n\n"
            f"👉 接下來，你可以對 AI 說：\n"
            f"「 用 {name} 的聲音說一段話 」"
        )
    except Exception as e:
        return f"❌ 儲存失敗：{e}"


def build_ui():
    sample_text = load_sample_text()

    with gr.Blocks(title="VoxCPM2 錄音工具", css=CUSTOM_CSS) as app:
        gr.HTML("""
        <div style="text-align:center; margin-bottom:24px;">
          <h1 style="font-size:2em; margin-bottom:4px;">🎙️ VoxCPM2 語音錄製</h1>
          <p style="font-size:1.05em; color:#666;">錄下你的聲音，後續由 AI 幫你生成任何語音。</p>
        </div>
        """)

        with gr.Column(elem_classes="step-box"):
            gr.Markdown("## ✏️ 為聲音取名字")
            voice_name_input = gr.Textbox(
                label="",
                placeholder="例如：王老師、林主任...",
                show_label=False,
            )

        with gr.Column(elem_classes="step-box"):
            gr.Markdown("## 📖 請念這段文字")
            gr.HTML(
                f'<div style="background:#fff3cd; padding:16px; border-radius:8px; '
                f'font-size:1.1em; line-height:2; margin:8px 0;">{sample_text}</div>'
            )

        with gr.Column(elem_classes="step-box"):
            gr.Markdown("## 🎤 錄音並儲存")
            audio_mic = gr.Audio(
                label="",
                type="filepath",
                sources=["microphone"],
                show_label=False,
                format="wav",
                waveform_options=gr.WaveformOptions(show_recording_waveform=True),
            )

            gr.HTML('<div style="text-align:center; margin-top:8px;">'
                    '👆 錄完後按這裡儲存 👇</div>')

            with gr.Row():
                save_btn = gr.Button("⬇️ 儲存聲音", variant="primary", size="lg")

            with gr.Accordion("或上傳已錄好的音檔", open=False):
                audio_upload = gr.Audio(
                    label="",
                    type="filepath",
                    sources=["upload"],
                    show_label=False,
                    format="wav",
                )

        save_msg = gr.Textbox(label="", show_label=False, lines=5, interactive=False)

        save_btn.click(
            fn=on_save,
            inputs=[audio_mic, audio_upload, voice_name_input],
            outputs=[save_msg],
        )

        gr.HTML("""
        <div style="text-align:center; margin-top:24px; padding:12px; color:#999; font-size:0.85em;">
        VoxCPM2（Apache-2.0 可商用） |
        <a href="https://github.com/mathruffian-dot/voxcpm2-voice-cloner" target="_blank">GitHub</a>
        </div>
        """)

    return app


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--port", "-p", type=int, default=7860)
    args = p.parse_args()
    build_ui().launch(server_port=args.port, theme=gr.themes.Soft())
