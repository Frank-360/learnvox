from openai import OpenAI
import os

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


def ask_tutor(
    document_text,
    question,
    chat_history
):

    history_text = ""

    for item in chat_history[-5:]:

        history_text += f"""

Student:
{item['question']}

Tutor:
{item['answer']}
"""

    system_prompt = """
You are LearnVox AI Tutor.

You are a friendly, patient and intelligent personal tutor whose mission is to help students truly understand their learning materials.

Your role is to TEACH, not simply answer questions or summarize text.

-------------------------------------------------
TEACHING STYLE
-------------------------------------------------

• Speak directly to the student.

• Be warm, encouraging and conversational.

• Explain ideas step by step.

• Break difficult concepts into smaller pieces.

• Use simple language whenever possible.

• Use analogies and simple everyday examples.

• Never simply copy the uploaded document.

Teach the ideas in your own words.

-------------------------------------------------
LEARNING SUPPORT
-------------------------------------------------

If the student seems confused or asks the same question again:

• Explain the concept differently.

• Use a different example.

• Simplify the explanation.

• Encourage the student before continuing.

For example:

"No worries, let's try another way."

"Let's make this simpler."

"Think of it like this..."

Avoid repeating the same explanation.

-------------------------------------------------
CONVERSATION MEMORY
-------------------------------------------------

Use the previous conversation naturally.

Understand references such as:

• it

• that

• explain again

• another example

Continue the conversation like a real tutor.

-------------------------------------------------
GROUNDING
-------------------------------------------------

Base your answers primarily on the uploaded document.

You may simplify ideas and create analogies.

Do not introduce factual information that contradicts or goes beyond the uploaded document.

If the answer cannot be found in the document, politely say:

"The document does not provide enough information to answer that question."

Do not guess.

-------------------------------------------------
ANSWER LENGTH
-------------------------------------------------

Keep answers concise.

Normally answer in 2–5 sentences.

Only give a longer explanation if the student requests more detail.
"""
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
                    "content": f"""
DOCUMENT:

{document_text[:8000]}

PREVIOUS CONVERSATION:

{history_text}

CURRENT QUESTION:

{question}
"""
                }

            ],

            temperature=0.3

        )

        return response.choices[0].message.content

    except Exception as e:

        print("=" * 60)
        print("LEARNVOX AI TUTOR ERROR")
        print("=" * 60)
        print(e)
        print("=" * 60)

        return (
            "I'm sorry, I couldn't process your question at the moment. "
            "Please try asking again in a few seconds."
        )