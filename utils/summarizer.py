from openai import OpenAI
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

# Get API key from environment
api_key = os.getenv("OPENAI_API_KEY")

# Create OpenAI client
client = OpenAI(api_key=api_key)

def summarize(text):

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": "Summarize this document into clear student-friendly notes."
            },
            {
                "role": "user",
                "content": text[:10000]
            }
        ]
    )

    return response.choices[0].message.content