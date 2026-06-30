import os
import json
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_flashcards(text):
    prompt = f"""
You are an expert tutor.

From the study material below, generate exactly 10 flashcards.

Return ONLY valid JSON in this format:

[
  {{
    "question":"...",
    "answer":"..."
  }}
]

Study Material:

{text[:12000]}
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.4
    )

    return json.loads(response.choices[0].message.content)