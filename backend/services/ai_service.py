import os
from openai import OpenAI

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = None
if OPENAI_API_KEY:
    client = OpenAI(api_key=OPENAI_API_KEY)

def get_ai_response(message: str) -> str:
    # Dummy mode
    if not client:
        return f"[DUMMY RESPONSE] You asked: {message}"

    # Real AI mode
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a college enquiry chatbot. "
                    "Answer clearly in simple English. "
                    "Limit answers to 3–5 lines."
                )
            },
            {"role": "user", "content": message}
        ],
        max_tokens=150,
        temperature=0.5
    )

    return response.choices[0].message.content.strip()
