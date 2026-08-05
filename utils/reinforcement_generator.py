from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))



def generate_reinforcement(

    lesson_title,
    question,
    expected_answer,
    learner_answers,
    teacher_feedback

):

    prompt = f"""
You are LearnVox, an expert AI classroom teacher.

A class of learners has just completed a checkpoint question.

Your job is NOT to repeat the lesson.

Your job is to reinforce only the concept the learners misunderstood.

Lesson Title:
{lesson_title}

Checkpoint Question:
{question}

Expected Answer:
{expected_answer}

Learner Answers:
{learner_answers}

Teacher Feedback:
{teacher_feedback}

Instructions:

1. Identify the main misunderstanding shared by the class.

2. Explain ONLY that concept.

3. Use simple language.

4. Give one practical example or analogy.

5. Encourage the learners.

6. Keep the explanation under 200 words.

Return ONLY the reinforcement explanation.
"""

    response = client.responses.create(

        model="gpt-5.1",

        input=prompt
    )

    return response.output_text.strip()