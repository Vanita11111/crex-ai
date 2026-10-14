
import os
import requests
import gradio as gr

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

MODELS = [
    "gemini-3.8-flash",
    "gemini-3.5-flash-lite"
]

ADSENSE_CODE = """
<script async
src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-5565183897845006"
crossorigin="anonymous"></script>
"""

CUSTOM_CSS = """
.gradio-container {
    width: 100% !important;
    max-width: 100% !important;
    margin: 0 auto !important;
    padding: 20px 3% !important;
    box-sizing: border-box !important;
}

.gradio-container textarea,
.gradio-container input {
    box-sizing: border-box !important;
}

footer {
    visibility: hidden;
}

@media (max-width: 600px) {
    .gradio-container {
        padding: 12px !important;
    }
}
"""


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
                            "You are Crex AI, a helpful educational assistant "
                            "for Class 11, Class 12, JEE Main, JEE Advanced, "
                            "Mathematics, Physics, Chemistry, Coding and "
                            "general education.\n\n"
                            "Give accurate answers and show important steps. "
                            "Use simple plain-text mathematics. Avoid LaTeX.\n\n"
                            "User question:\n" + question
                        )
                    }
                ]
            }
        ],
        "generationConfig": {
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
        timeout=60
    )


def ask_crex(question):
    if not question or not question.strip():
        return "Please type a question."

    if not GEMINI_API_KEY:
        return (
            "Error: GEMINI_API_KEY is not configured. "
            "Add it under Environment Variables in Render."
        )

    last_error = ""

    for model in MODELS:
        try:
            response = ask_gemini(model, question)

            if response.status_code == 200:
                result = response.json()
                candidates = result.get("candidates", [])

                if candidates:
                    parts = (
                        candidates[0]
                        .get("content", {})
                        .get("parts", [])
                    )

                    answer_text = "\n".join(
                        part["text"]
                        for part in parts
                        if "text" in part
                    )

                    if answer_text:
                        return answer_text

                last_error = "The AI returned no answer."
                continue

            if response.status_code in (429, 500, 503):
                last_error = (
                    f"Model {model}: HTTP {response.status_code}"
                )
                continue

            return (
                f"Gemini API error (HTTP {response.status_code}).\n"
                + response.text[:1000]
            )

        except requests.exceptions.Timeout:
            last_error = "The AI request timed out."

        except requests.exceptions.RequestException as e:
            last_error = str(e)

        except (ValueError, KeyError, IndexError) as e:
            last_error = "Could not read the AI response: " + str(e)

    return (
        "Crex AI is temporarily unable to answer. Please try again.\n\n"
        "Technical message: " + last_error
    )


with gr.Blocks(title="Crex AI", css=CUSTOM_CSS) as app:

    gr.Markdown(
        "# 🤖 Crex AI\n\n"
        "JEE • Class 11–12 • Coding • General AI"
    )

    question = gr.Textbox(
        lines=5,
        label="Your Question",
        placeholder="Type your question here...",
        autofocus=True
    )

    ask_button = gr.Button(
        "Ask Crex AI",
        variant="primary"
    )

    answer = gr.Textbox(
        lines=15,
        label="Crex AI Answer",
        interactive=False
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


if __name__ == "__main__":
    app.launch(
        server_name="0.0.0.0",
        server_port=int(os.environ.get("PORT", "7860")),
        head=ADSENSE_CODE
    )
