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
    replacements = {
        r"\frac": "",
        r"\dfrac": "",
        r"\tfrac": "",
        r"\sqrt": "sqrt",
        r"\times": " x ",
        r"\cdot": " * ",
        r"\div": " / ",
        r"\leq": "<=",
        r"\geq": ">=",
        r"\neq": "!=",
        r"\pm": "+/-",
        r"\alpha": "alpha",
        r"\beta": "beta",
        r"\gamma": "gamma",
        r"\delta": "delta",
        r"\theta": "theta",
        r"\pi": "pi",
        r"\infty": "infinity",
        r"\rightarrow": "->",
        r"\Rightarrow": "=>",
        r"\left": "",
        r"\right": "",
        r"\text": "",
        r"\mathrm": "",
        r"\mathbf": "",
    }

    text = text.replace("$$", "")
    text = text.replace(r"\[", "")
    text = text.replace(r"\]", "")
    text = text.replace(r"\(", "")
    text = text.replace(r"\)", "")
    text = text.replace("$", "")

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(r"\\[a-zA-Z]+", "", text)
    text = text.replace("{", "")
    text = text.replace("}", "")

    return text.strip()


def ask_crex(question):
    if not question or not question.strip():
        return "Please type or speak a question."

    if not HF_TOKEN:
        return "Error: HF_TOKEN is not configured."

    headers = {
        "Authorization": "Bearer " + HF_TOKEN,
        "Content-Type": "application/json"
    }

    data = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are Crex AI. Answer educational questions about "
                    "Class 11, Class 12, JEE Main, JEE Advanced, mathematics, "
                    "physics, chemistry, coding and general topics. "
                    "NEVER use LaTeX. Write mathematics in simple plain text. "
                    "Example: x^2 + 5x + 6 = 0. "
                    "Use sqrt(25) instead of LaTeX. "
                    "Explain answers step by step."
                )
            },
            {
                "role": "user",
                "content": question
            }
        ],
        "max_tokens": 800,
        "temperature": 0.3
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


with gr.Blocks(title="Crex AI") as app:

    gr.Markdown(
        "# 🤖 Crex AI\n\n"
        "JEE • Class 11–12 • Coding • General AI"
    )

    question = gr.Textbox(
        lines=5,
        label="Your Question",
        placeholder="Type your question or use the microphone..."
    )

    mic_button = gr.Button("🎤 Speak")

    ask_button = gr.Button("Ask Crex AI")

    answer = gr.Textbox(
        lines=15,
        label="Crex AI Answer"
    )

    mic_button.click(
        fn=None,
        inputs=None,
        outputs=question,
        js="""
        async () => {
            const SpeechRecognition =
                window.SpeechRecognition ||
                window.webkitSpeechRecognition;

            if (!SpeechRecognition) {
                alert("Speech recognition is not supported. Please use Google Chrome.");
                return "";
            }

            const recognition = new SpeechRecognition();
            recognition.lang = "en-IN";
            recognition.interimResults = false;
            recognition.continuous = false;

            return await new Promise((resolve) => {
                recognition.onresult = (event) => {
                    resolve(event.results[0][0].transcript);
                };

                recognition.onerror = () => {
                    alert("Please allow microphone access and try again.");
                    resolve("");
                };

                recognition.start();
            });
        }
        """
    )

    ask_button.click(
        fn=ask_crex,
        inputs=question,
        outputs=answer
    )

    question.submit(
        fn=ask_crex,
        inputs=question,
        outputs=answer
    )


app.launch(
    server_name="0.0.0.0",
    server_port=int(os.environ.get("PORT", 7860))
)
