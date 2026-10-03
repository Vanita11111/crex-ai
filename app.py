```python
import os
import re
import requests
import gradio as gr
from dotenv import load_dotenv

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")

API_URL = "https://router.huggingface.co/v1/chat/completions"
MODEL = "Qwen/Qwen3-8B"


def clean_answer(text):
    # Remove display math markers
    text = text.replace("$$", "")
    text = text.replace(r"\[", "")
    text = text.replace(r"\]", "")
    text = text.replace(r"\(", "")
    text = text.replace(r"\)", "")

    # Convert common LaTeX commands to readable text
    replacements = {
        r"\frac": "",
        r"\sqrt": "√",
        r"\times": "×",
        r"\div": "÷",
        r"\cdot": "·",
        r"\leq": "≤",
        r"\geq": "≥",
        r"\neq": "≠",
        r"\pm": "±",
        r"\alpha": "α",
        r"\beta": "β",
        r"\theta": "θ",
        r"\pi": "π",
        r"\infty": "∞",
        r"\rightarrow": "→",
        r"\Rightarrow": "⇒",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    # Remove remaining simple LaTeX commands such as \text, \mathrm, etc.
    text = re.sub(r"\\[a-zA-Z]+", "", text)

    # Remove LaTeX braces
    text = text.replace("{", "")
    text = text.replace("}", "")

    return text.strip()


def ask_crex(question):
    if not question.strip():
        return "Please type a question."

    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json"
    }

    data = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are Crex AI, a helpful educational AI assistant. "
                    "Answer Class 11, Class 12, JEE Main, JEE Advanced, coding, "
                    "mathematics, physics, chemistry and general questions. "
                    "Use plain text only. Never use LaTeX. "
                    "Do not use $, $$, \\frac, \\sqrt, \\begin, \\end, "
                    "or other LaTeX commands. "
                    "Write equations in normal readable text. "
                    "For example, write x^2 + 5x + 6 = 0. "
                    "Explain calculations step by step."
                )
            },
            {
                "role": "user",
                "content": question
            }
        ],
        "max_tokens": 800,
        "temperature": 0.5
    }

    try:
        response = requests.post(
            API_URL,
            headers=headers,
            json=data,
            timeout=120
        )

        if response.status_code != 200:
            return "AI error: " + response.text

        result = response.json()

        answer = result["choices"][0]["message"]["content"]

        return clean_answer(answer)

    except Exception as e:
        return "Connection error: " + str(e)


app = gr.Interface(
    fn=ask_crex,
    inputs=gr.Textbox(
        lines=5,
        placeholder="Ask Crex AI anything..."
    ),
    outputs=gr.Textbox(
        lines=15,
        label="Crex AI Answer"
    ),
    title="🤖 Crex AI",
    description="JEE • Class 11–12 • Coding • General AI"
)

app.launch(
    server_name="0.0.0.0",
    server_port=int(os.environ.get("PORT", 7860))
)
```
