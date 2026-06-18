from flask import Flask, render_template, request
import os
import markdown

from utils.pdf_reader import extract_text
from utils.summarizer import summarize
from utils.tts import generate_audio

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():

    file = request.files["file"]

    filepath = os.path.join(
        app.config["UPLOAD_FOLDER"],
        file.filename
    )

    # Save uploaded PDF
    file.save(filepath)

    # Extract text
    text = extract_text(filepath)

    # Generate summary
    summary = summarize(text)

    # Generate audio
    audio_path = "static/audio/summary.mp3"

    generate_audio(
        summary,
        audio_path
    )

    html_summary = markdown.markdown(summary)

    return f"""
        <h2>Summary</h2>
        {html_summary}

        <h2>Audio Version</h2>

        <audio controls>
            <source src="/static/audio/summary.mp3" type="audio/mpeg">
        </audio>
        """


if __name__ == "__main__":
    app.run(debug=True)