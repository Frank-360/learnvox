from openai import OpenAI
import os

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

def generate_takeaway(summary):

    prompt = f"""
You are an expert teacher.

Based on the lesson below, create a concise lesson takeaway.

Rules:
- 2 to 4 sentences.
- Focus on the most important concepts.
- Write in simple student-friendly language.
- Return only the takeaway text.

Lesson:

{summary}
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3
    )

    return response.choices[0].message.content.strip()