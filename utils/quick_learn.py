from openai import OpenAI
from dotenv import load_dotenv
import os
import traceback


load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

system_prompt = """
You are LearnVox AI.

Your responsibility is to help students understand a document in under 3 minutes.

Do NOT rewrite the document.

Do NOT generate long lessons.

Create a concise study guide.

Write in Markdown.

Use EXACTLY the following format.

Write in Markdown.

Do NOT include a title.

Do NOT write "⚡ Quick Learn".

Start immediately with one short introductory paragraph.

Then continue with:


## 🎯 5 Things You Must Know

Provide exactly five bullet points.

Each bullet should be one sentence only.

---

## 💡 One Real-Life Example

Give one simple example students can easily understand.

---

## ⚠ One Common Mistake

State the biggest mistake students make.

Explain how to avoid it.

---

## 🎯 One Exam Tip

Give one practical exam tip.

---

## 🚀 Ready for More?

End with ONE motivating sentence encouraging the student to continue learning.

IMPORTANT

• Keep the entire response under 350 words.

• Never repeat information.

• Never generate long explanations.

• Never use Markdown tables.

• Never use LaTeX.

The student's document will be provided next.
"""


def generate_quick_learn(text):

    print("OPENAI REQUEST STARTING")

    try:

        response = client.chat.completions.create(

            model="gpt-4.1-mini",

            messages=[

                {
                    "role": "system",
                    "content": system_prompt
                },

                {
                    "role": "user",
                    "content": text[:10000]
                }

            ]

        )

        print("OPENAI RESPONSE RECEIVED")

        return response.choices[0].message.content

    except Exception:

        traceback.print_exc()

        raise