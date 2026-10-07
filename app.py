import os
import requests
import gradio as gr

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def ask_crex(question):
    if not question.strip():
        return "Please type a question."

    if not GEMINI_API_KEY:
        return "GEMINI_API_KEY is missing."

    url = (
        "https://generativelanguage.googleapis.com/v1beta/"
        "models/gemini-2.5-flash:generateContent?key="
        + GEMINI_API_KEY
    )

    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": (
                            "You are Crex AI. Answer clearly and step by step. "
                            "Never use LaTeX. Use simple plain text mathematics.\n\n"
                            + question
                        )
                    }
                ]
            }
        ]
    }

    try:
        r = requests.post(url, json=data, timeout=30)

        if r.status_code != 200:
            return "Gemini error: " + r.text

        result = r.json()
        return result["candidates"][0]["content"]["parts"][0]["text"]

    except Exception as e:
        return "Connection error: " + str(e)


with gr.Blocks(title="Crex AI") as app:
    gr.Markdown("# 🤖 Crex AI\nJEE • Class 11–12 • Coding • General AI")

    question = gr.Textbox(
        label="Your Question",
        placeholder="Type your question here..."
    )

    ask = gr.Button("Ask Crex AI")

    answer = gr.Textbox(
        label="Crex AI Answer",
        lines=15
    )

    ask.click(
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
