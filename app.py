```python
import os
import requests
import gradio as gr
from dotenv import load_dotenv

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")

API_URL = "https://router.huggingface.co/v1/chat/completions"
MODEL = "Qwen/Qwen3-8B"


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
                    "Help with Class 11, Class 12, JEE Main, JEE Advanced, "
                    "coding, mathematics, physics, chemistry and general questions. "
                    "Explain answers clearly and step by step. "
                    "Do NOT use LaTeX, LaTeX commands, or mathematical markup. "
                    "Write mathematics in simple plain text that is easy to read. "
                    "For example, write x^2 + 2x + 1 instead of LaTeX notation. "
                    "Use normal symbols such as +, -, ×, ÷, = and ^ when useful. "
                    "Keep answers clean, simple and easy to understand. "
                    "For school and JEE questions, show the calculation steps clearly."
                )
            },
            {
                "role": "user",
                "content": question
            }
        ],
        "max_tokens": 800,
        "temperature": 0.7
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

        return result["choices"][0]["message"]["content"]

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
