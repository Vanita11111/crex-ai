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
    # Remove LaTeX delimiters
    text = re.sub(r"\$\$.*?\$\$", lambda m: m.group(0)[2:-2], text, flags=re.DOTALL)
    text = re.sub(r"\\\[|\u005c\]|\u005c\(|\u005c\)", "", text)

    # Common LaTeX commands
    replacements = {
        r"\frac": "",
        r"\dfrac": "",
        r"\tfrac": "",
        r"\sqrt": "√",
        r"\times": "×",
        r"\cdot": "·",
        r"\div": "÷",
        r"\leq": "≤",
        r"\geq": "≥",
        r"\neq": "≠",
        r"\pm": "±",
        r"\alpha": "α",
        r"\beta": "β",
        r"\gamma": "γ",
        r"\delta": "δ",
        r"\theta": "θ",
        r"\pi": "π",
        r"\infty": "∞",
        r"\rightarrow": "→",
        r"\Rightarrow": "⇒",
        r"\left": "",
        r"\right": "",
        r"\text": "",
        r"\mathrm": "",
        r"\mathbf": "",
        r"\begin": "",
        r"\end": "",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    # Remove remaining LaTeX commands
    text = re.sub(r"\\[a-zA-Z]+", "", text)

    # Remove LaTeX braces
    text = text.replace("{", "")
    text = text.replace("}", "")

    # Remove stray dollar signs
    text = text.replace("$", "")

    # Clean excessive spaces
    text = re.sub(r"[ \t]+", " ", text)

    return text.strip()


def ask_crex(question):
    if not question or not question.strip():
        return "Please type or speak a question."

    if not HF_TOKEN:
        return "Error: HF_TOKEN is not configured."

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

                    "IMPORTANT FORMATTING RULES: "
                    "Never use LaTeX or mathematical markup. "
                    "Never use dollar signs for mathematical formatting. "
                    "Never use commands such as \\frac, \\sqrt, \\alpha, "
                    "\\beta, \\begin or \\end. "
                    "Write everything as normal plain text. "

                    "For mathematics, use simple forms such as: "
                    "x^2 + 5x + 6 = 0, "
                    "sqrt(25) = 5, "
                    "2/3, "
                    "a × b = c. "

                    "Explain answers clearly and step by step. "
                    "Make the response easy for students and ordinary users to read."
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


# Browser microphone / speech-to-text button
mic_html = """
<div style="margin-bottom:10px;">
    <button
        id="crex-mic"
        style="
            padding:10px 16px;
            border-radius:10px;
            border:1px solid #aaa;
            background:white;
            cursor:pointer;
            font-size:15px;
        ">
        🎤 Speak
    </button>
    <span id="crex-mic-status" style="margin-left:10px;"></span>
</div>

<script>
(function() {
    const button = document.getElementById("crex-mic");
    const status = document.getElementById("crex-mic-status");

    if (!button) return;

    const SpeechRecognition =
        window.SpeechRecognition ||
        window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
        status.textContent =
            "Microphone speech is not supported in this browser.";
        button.disabled = true;
        return;
    }

    const recognition = new SpeechRecognition();

    recognition.lang = "en-IN";
    recognition.interimResults = false;
    recognition.continuous = false;

    button.onclick = function() {
        status.textContent = "Listening...";
        recognition.start();
    };

    recognition.onresult = function(event) {
        const transcript =
            event.results[0][0].transcript;

        const textarea =
            document.querySelector("#crex-question textarea");

        if (textarea) {
            textarea.value = transcript;
            textarea.dispatchEvent(
                new Event("input", { bubbles: true })
            );
            textarea.dispatchEvent(
                new Event("change", { bubbles: true })
            );
        }

        status.textContent = "Done ✓";
    };

    recognition.onerror = function(event) {
        status.textContent =
            "Microphone error: " + event.error;
    };

    recognition.onend = function() {
        if (status.textContent === "Listening...") {
            status.textContent = "";
        }
    };
})();
</script>
"""


with gr.Blocks(title="Crex AI") as app:

    gr.Markdown(
        """
        # 🤖 Crex AI
        **JEE • Class 11–12 • Coding • General AI**

        Ask your question by typing or using the microphone.
        """
    )

    gr.HTML(mic_html)

    question = gr.Textbox(
        lines=5,
        label="Your Question",
        placeholder="Type your question or click 🎤 Speak...",
        elem_id="crex-question"
    )

    ask_button = gr.Button("Ask Crex AI 🚀")

    answer = gr.Textbox(
        lines=15,
        label="Crex AI Answer"
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
```
