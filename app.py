
import os
import requests
import gradio as gr

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

API_URL = (
    "https://generativelanguage.googleapis.com/v1beta/"
    "models/gemini-3.8-flash:generateContent"
)


def ask_crex(question):
    if not question or not question.strip():
        return "Please type a question."

    if not GEMINI_API_KEY:
        return "Error: GEMINI_API_KEY is not configured in Render."

    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": (
                            "You are Crex AI, an educational AI assistant. "
                            "Help with Class 11, Class 12, JEE Main, JEE Advanced, "
                            "Mathematics, Physics, Chemistry, Coding and general "
                            "educational questions. "
                            "Explain answers clearly and step by step. "
                            "Never use LaTeX. Write mathematics in simple plain text. "
                            "For example, use sqrt(25) instead of LaTeX.\n\n"
                            "User question:\n"
                            + question
                        )
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": 800,
            "thinkingConfig": {
                "thinkingLevel": "low"
            }
        }
    }

    try:
        response = requests.post(
            API_URL,
            headers={
                "x-goog-api-key": GEMINI_API_KEY,
                "Content-Type": "application/json"
            },
            json=data,
            timeout=30
        )

        if response.status_code != 200:
            return "Gemini error: " + response.text

        result = response.json()

        answer = result["candidates"][0]["content"]["parts"][0]["text"]

        return answer

    except requests.exceptions.Timeout:
        return "The AI request timed out. Please try again."

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
        placeholder="Type your question here..."
    )

    ask_button = gr.Button("Ask Crex AI")

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
    server_port=int(os.environ.get("PO_

