import os
import gradio as gr
import re
from transformers import pipeline

# ၁။ ဘာသာပြန်မော်ဒယ် ဖွင့်ခြင်း (အင်္ဂလိပ် -> မြန်မာ)
# ဒီနေရာမှာ မော်ဒယ်ကို အသုံးပြုထားပါတယ်။ ပထမဆုံးအကြိမ် run တဲ့အခါ ဒေါင်းလုဒ်ဆွဲဖို့ ခဏစောင့်ရပါမယ်။
translator = pipeline("translation", model="Helsinki-NLP/opus-mt-en-my")

# ၂။ SRT ဖိုင်ကို ခွဲခြမ်းစိတ်ဖြာခြင်း
def parse_srt(content):
    blocks = re.split(r'\n\s*\n', content.strip())
    subtitles = []
    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) >= 3:
            idx = lines[0].strip()
            timestamp = lines[1].strip()
            text = '\n'.join(lines[2:]).strip()
            subtitles.append((idx, timestamp, text))
    return subtitles

# ၃။ ဘာသာပြန်ခြင်း
def translate_text(text):
    if not text.strip():
        return text
    result = translator(text, max_length=512)
    return result[0]['translation_text']

def translate_srt(content):
    subtitles = parse_srt(content)
    output_blocks = []
    for idx, timestamp, text in subtitles:
        translated = translate_text(text)
        output_blocks.append(f"{idx}\n{timestamp}\n{translated}")
    return '\n\n'.join(output_blocks)

# ၄။ ဖိုင်တင်ပြီး ဘာသာပြန်ခြင်း လုပ်ဆောင်ချက်
def process(file):
    if file is None:
        return "SRT ဖိုင်တစ်ခု upload လုပ်ပါ"
    with open(file.name, 'r', encoding='utf-8') as f:
        content = f.read()
    translated = translate_srt(content)
    output_path = "/tmp/translated.srt"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(translated)
    return output_path

# ၅။ Gradio မျက်နှာပြင် တည်ဆောက်ခြင်း
with gr.Blocks(title="မြန်မာ SRT ဘာသာပြန်ကိရိယာ") as demo:
    gr.Markdown("## မြန်မာ SRT ဘာသာပြန်ကိရိယာ\nSRT ဖိုင်တစ်ခု upload လုပ်ပါ၊ စနစ်သည် အလိုအလျောက် မြန်မာဘာသာသို့ ဘာသာပြန်ပေးပါမည်။")
    with gr.Row():
        input_file = gr.File(label="SRT ဖိုင် upload လုပ်ပါ", file_types=[".srt"])
        output_file = gr.File(label="ဘာသာပြန်ပြီး SRT ကို ဒေါင်းလုဒ်လုပ်ပါ")
    btn = gr.Button("ဘာသာပြန်စတင်ပါ")
    btn.click(process, inputs=input_file, outputs=output_file)

# ၆။ Render အတွက် လိုအပ်တဲ့ ချိန်ညှိမှု (အရေးကြီးဆုံး)
demo.launch(
    server_name="0.0.0.0",
    server_port=int(os.environ.get("PORT", 7860))
)
