
import os
import requests
import gradio as gr

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

MODEL = "gemini-3.8-flash"


def ask_crex(question):
    if not question or not question.strip():
        return "Please type a question."

    if not GEMINI_API_KEY:
        return "Error: GEMINI_API_KEY is not configured in Render."

    url = (
        "https://generativelanguage.googleapis.com/v1beta/"
        "models/" + MODEL + ":generateContent"
    )

    prompt = (
        "You are Crex AI, a highly intelligent educational AI assistant.\n\n"
        "Help with Class 11, Class 12, JEE Main, JEE Advanced, "
        "Mathematics, Physics, Chemistry, Coding, Python and general "
        "educational questions.\n\n"
        "Think carefully before answering.\n"
        "For difficult questions, use deep reasoning and check your answer.\n"
        "For mathematics and science, show clear step-by-step working.\n"
        "Give accurate and understandable final answers.\n"
        "Use simple plain-text mathematics. Do not use LaTeX.\n\n"
        "User question:\n" + question
    )

    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
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
                "x-goog-api-key": GEMINI_API_KEY,
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
        return "Crex AI is taking too long. Please try again."

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

