from openai import OpenAI
import os

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

def generate_quiz(text):

    prompt = f"""
    Create exactly 5 multiple-choice questions from the lesson below.

    Return ONLY a valid JSON array.

    Rules:
    - Return JSON only.
    - Do not use markdown.
    - Do not wrap the JSON in ```json blocks.
    - Each question must have exactly 4 options.
    - The answer field must contain the index of the correct answer:
    0 = first option
    1 = second option
    2 = third option
    3 = fourth option
    - Include a clear explanation of why the answer is correct.
    - Explanations should teach the concept, not just restate the answer.
    - Include a learning_point field containing the key concept the student should remember.

    Example:

    [
    {{
        "question": "What is photosynthesis?",
        "options": [
        "A process plants use to make food",
        "A type of animal",
        "A chemical element",
        "A weather condition"
        ],
        "answer": 0,
        "explanation": "Photosynthesis is the process by which plants use sunlight, water, and carbon dioxide to produce food.",
        "learning_point": "Plants make their own food through photosynthesis."
    }}
    ]

    Lesson:
    {text}
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
