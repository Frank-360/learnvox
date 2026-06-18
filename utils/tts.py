from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

def generate_audio(text, output_file):

    response = client.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="coral",
        input=text
    )

    response.stream_to_file(output_file)