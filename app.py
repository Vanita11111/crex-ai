
import os
import requests
import gradio as gr

API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = "gemini-3.8-flash"


def ask_crex(question):
    if not question.strip():
        return "Please type a question."

    if not API_KEY:
        return "Error: GEMINI_API_KEY is not configured."

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"

    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": f"""
You are Crex AI, a powerful educational AI assistant.

Help with:
- Class 11 and 12
- JEE Main and JEE Advanced
- Mathematics
- Physics
- Chemistry
- Coding and Python
- General education

Think deeply and carefully before answering.
For difficult problems, verify your reasoning.
For Mathematics and Physics, show clear step-by-step solutions.
Give accurate and easy-to-understand answers.
Use plain text mathematics, not LaTeX.

Question:
{question}
"""
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
            "thinkingConfig": {
                "thinkingLevel": "high"
            }
        }
    }

    try:
        response = requests.post(
            url,
            headers={
                "x-goog-api-key": API_KEY,
                "Content-Type": "application/json"
            },
            json=data,
            timeout=60
        )

        if response.status_code != 200:
            return "Gemini error: " + response.text

        result = response.json()

        return result["candidates"][0]["content"]["parts"][0]["text"]

    except requests.exceptions.Timeout:
        return "The request took too long. Please try again."

    except Exception as e:
        return "Crex AI error: " + str(e)


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

    ask = gr.Button("Ask Crex AI")

    answer = gr.Textbox(
        lines=15,
        label="Crex AI Answer"
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

