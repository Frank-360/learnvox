import os
import json
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_flashcards(text):
    prompt = f"""
You are LearnVox AI.

You are creating interactive flashcards for a student who has just completed
an AI tutoring session.

Generate exactly 10 flashcards.

Rules:

- Keep each question short and clear.
- Each answer should be concise (1–3 sentences).
- Cover different concepts from the study material.
- Start with basic ideas before moving to harder concepts.
- Write questions that encourage active recall.
- Do not repeat information.
- Use simple language suitable for students.

Return ONLY valid JSON.

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