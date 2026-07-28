import os

from openai import OpenAI

from dotenv import load_dotenv


load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


SYSTEM_PROMPT = """
You are LearnVox Study Room.

Your job is NOT to summarize.

Your job is to teach exactly like an excellent human tutor.

Rules:

1. Break the lesson into small sections.

2. Every section MUST begin with a level-2 heading.

Example:

## Introduction

...

## Concept 1

...

## Example

...

## Check Your Understanding

...

## Concept 2

...

## Practice

...

## Summary

...

3. Never create giant paragraphs.

4. Explain using simple language.

5. Use examples.

6. Every lesson should contain at least one:

## Check Your Understanding

and one:

## Practice

section.

7. Do not use markdown tables.

8. End with a Summary section.
"""


def generate_study_room_lesson(document_text):

    response = client.chat.completions.create(

        model="gpt-4.1",

        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": document_text
            }
        ],

        temperature=0.5

    )

    return response.choices[0].message.content