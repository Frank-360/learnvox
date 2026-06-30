import json
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def generate_quiz(document):

    system_prompt = """
    You are LearnVox AI.

    You are creating an intelligent quiz for a student after completing an AI tutoring session.

    Return ONLY valid JSON.

    Generate exactly 10 multiple-choice questions.

    Rules:

    - Four answer options.
    - Only one correct answer.
    - Questions should become progressively more challenging.
    - Cover different concepts from the uploaded document.
    - Write clear and natural questions.
    - Avoid trick questions.
    - Make the explanations educational.
    - Each explanation should teach WHY the correct answer is correct.
    - Keep explanations between 20 and 60 words.
    - Do not mention option numbers.

    Return ONLY this JSON structure.

    {
    "questions":[
        {
        "question":"",
        "options":[
            "",
            "",
            "",
            ""
        ],
        "answer":0,
        "explanation":""
        }
    ]
    }

    The answer field must be the option index:

    0
    1
    2
    3

    Return JSON only.

    Do not include markdown.

    Do not include code fences.
    """

    response = client.chat.completions.create(

        model="gpt-4.1-mini",

        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": document
            }
        ]

    )

    return json.loads(
        response.choices[0].message.content
    )