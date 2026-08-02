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

    content = response.choices[0].message.content

    print("===== RAW AI RESPONSE =====")
    print(content)
    print("===========================")

    import json

    data = json.loads(content)

    print("===== PARSED JSON =====")
    print(data)
    print("=======================")

    return data

def evaluate_class_answers(
    question,
    expected_answer,
    learner_answers
):
    """
    Evaluates the understanding of the entire class.
    """

    prompt = f"""
You are LearnVox, an expert AI classroom teacher.

Question:
{question}

Expected Answer:
{expected_answer}

Learner Answers:
{learner_answers}

Evaluate EVERY learner's answer.

Then decide whether the class should:

- CONTINUE
- REVIEW
- RETEACH

Respond ONLY in valid JSON using this exact format:

{{
    "learners": [
        {{
            "name": "John",
            "correct": true,
            "score": 95,
            "feedback": "Excellent understanding."
        }}
    ],
    "decision": "CONTINUE",
    "teacher_feedback": "Excellent! Most of the class understood the concept. Let's continue."
}}

Rules:

- Return one learner object for EVERY learner.
- Preserve the learner names exactly as provided.
- "score" must be between 0 and 100.
- "correct" must be true or false.
- "feedback" should be encouraging and specific.
- "decision" must be exactly one of:
  CONTINUE
  REVIEW
  RETEACH
- Return ONLY valid JSON.
- Do not use markdown.
- Do not wrap the JSON in ```json.
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        temperature=0.3,
        messages=[
            {
                "role": "system",
                "content": "You are LearnVox, an expert classroom teacher."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    content = response.choices[0].message.content

    print("\n========== AI RESPONSE ==========")
    print(repr(content))
    print("=================================\n")

    import json

    return json.loads(content)