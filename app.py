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
                "content": "You are Crex AI, a helpful educational AI assistant. Help with Class 11, Class 12, JEE Main, JEE Advanced, coding, mathematics, physics, chemistry and general questions. Explain clearly and step by step."
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

app.launch()