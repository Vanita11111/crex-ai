
import os
import requests
import gradio as gr

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Main model: strong reasoning + good speed
MODELS = [
    "gemini-3.8-flash",
    "gemini-3.5-flash-lite"
]


def ask_gemini(model, question):
    url = (
        "https://generativelanguage.googleapis.com/v1beta/"
        "models/" + model + ":generateContent"
    )

    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": (
                            "You are Crex AI, a fast and intelligent educational "
                            "assistant for Class 11, Class 12, JEE Main, JEE Advanced, "
                            "Mathematics, Physics, Chemistry, Coding and general "
                            "education.\n\n"
                            "Give accurate answers and show important steps. "
                            "Use simple plain-text mathematics. "
                            "Do not use LaTeX.\n\n"
                            "User question:\n" + question
                        )
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 600,
            "thinkingConfig": {
                "thinkingLevel": "medium"
            }
        }
    }

    return requests.post(
        url,
        headers={
            "x-goog-api-key": GEMINI_API_KEY,
            "Content-Type": "application/json"
        },
        json=data,
        timeout=20
    )


def ask_crex(question):
    if not question or not question.strip():
        return "Please type a question."

    if not GEMINI_API_KEY:
        return "Error: GEMINI_API_KEY is not configured in Render."

    last_error = ""

    for model in MODELS:
        try:
            response = ask_gemini(model, question)

            if response.status_code == 200:
                result = response.json()

                return result["candidates"][0]["content"]["parts"][0]["text"]

            # Automatically try the next model if Gemini is temporarily busy.
            if response.status_code in [429, 500, 503]:
                last_error = response.text
                continue

            return "Gemini error: " + response.text

        except requests.exceptions.Timeout:
            last_error = "The request took too long."
            continue

        except Exception as e:
            last_error = str(e)
            continue

    return (
        "Crex AI is temporarily busy. Please try again.\n\n"
        "Technical message: " + last_error
    )


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
    server_port=int(os.environ.get("PORT", 7860))
)


