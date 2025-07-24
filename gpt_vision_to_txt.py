import os
import re
import json
import base64
from io import BytesIO
from PIL import Image
from pdf2image import convert_from_path
import openai

openai.api_key = "***REMOVED***proj-aNwKecAWmlakLc34yIaF8YgIGc3gwmGSPXfBwrE3vsuWNwTkOsu4XMkyjwUwMf2YeTCOiEavEST3BlbkFJhbuZujnJS5gpbKODy7oXg6eR7F9ww1XhQ9fkM80utHdCE_tJ520NfzAcIVQMydpHIJCPNAVUYA"  # твой ключ

def image_to_base64(img: Image.Image):
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def ask_gpt_vision(img_base64):
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "You are reading an exam page containing multiple SAT-style questions. "
                            "Your task is to extract each question in a structured JSON format.\n\n"
                            "For every question found in the image, return a JSON object with:\n"
                            "- id: (e.g. \"q17\")\n"
                            "- passage: (text BEFORE the question, or null)\n"
                            "- question: (the question itself)\n"
                            "- choices: (list like [\"A. ...\", \"B. ...\"])\n"
                            "- has-table: true if any table/chart/image is visible nearby, false otherwise\n\n"
                            "⚠️ Do NOT merge passage and question.\n"
                            "Return a valid JSON array ONLY — no explanation, no markdown."
                        )
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{img_base64}"
                        }
                    }
                ]
            }],
            max_tokens=2000,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"⚠️ GPT API error: {e}")
        return None

def gpt_vision_to_txt(pdf_path, base_name):
    output_dir = os.path.join("raw_txt", base_name)
    os.makedirs(output_dir, exist_ok=True)

    # Конвертируем PDF в изображения (страницы)
    print(f"🔄 Converting PDF pages from {pdf_path} ...")
    pages = convert_from_path(pdf_path, dpi=200)

    for idx, img in enumerate(pages):
        b64 = image_to_base64(img)
        print(f"\n📄 Processing page {idx + 1}/{len(pages)} ...")

        gpt_reply = ask_gpt_vision(b64)
        if not gpt_reply:
            print("❌ Empty GPT reply.")
            continue

        # Save raw txt
        txt_path = os.path.join(output_dir, f"page_{idx + 1}.txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(gpt_reply)
        print(f"✅ Saved GPT reply to {txt_path}")

    print("🎉 All done!")

if __name__ == "__main__":
    # Пример: python3 gpt_vision_to_txt.py sources/December_v1_2024.pdf December_v1_2024
    import sys
    if len(sys.argv) < 3:
        print("❌ Укажи путь к PDF и base_name (например, sources/December_v1_2024.pdf December_v1_2024)")
        exit(1)
    gpt_vision_to_txt(sys.argv[1], sys.argv[2])
