from flask import Flask, render_template, request
import os
import markdown

from utils.pdf_reader import extract_text
from utils.summarizer import summarize
from utils.tts import generate_audio
from utils.database import save_user

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"
AUDIO_FOLDER = "static/audio"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(AUDIO_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():

    
    full_name = request.form["full_name"]
    institution = request.form["institution"]
    email = request.form["email"]

    print(full_name)
    print(institution)
    print(email)

    file = request.files["file"]

    filepath = os.path.join(
        app.config["UPLOAD_FOLDER"],
        file.filename
    )

    file.save(filepath)

    save_user(
    full_name,
    institution,
    email,
    file.filename
    )

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

    return render_template(
    "result.html",
    summary=html_summary
)

    return render_template(
    "result.html",
    summary=html_summary
)

if __name__ == "__main__":
    app.run(debug=True)