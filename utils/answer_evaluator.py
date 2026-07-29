from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def evaluate_answer(question, expected_answer, learner_answer):
    """
    Uses GPT to evaluate whether the learner's answer is
    correct, partially correct, or incorrect.
    """

    prompt = f"""
You are an experienced teacher.

Question:
{question}

Expected Answer:
{expected_answer}

Learner's Answer:
{learner_answer}

Evaluate the learner's answer.

Respond ONLY in valid JSON using this format:

{{
    "correct": true,
    "score": 92,
    "feedback": "..."
}}

Rules:
- "correct" should be true if the learner demonstrates the correct understanding, even if the wording differs.
- "score" should be between 0 and 100.
- "feedback" should sound like a supportive teacher.
- Do not include markdown.
- Do not include explanations outside the JSON.
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        temperature=0.3,
        messages=[
            {
                "role": "system",
                "content": "You are an encouraging classroom teacher."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    import json

    return json.loads(response.choices[0].message.content)