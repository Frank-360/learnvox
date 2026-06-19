from flask import Flask, render_template, request
import os
import markdown
import time

from utils.pdf_reader import extract_text
from utils.summarizer import summarize
from utils.tts import generate_audio
from utils.database import save_user

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"
AUDIO_FOLDER = "static/audio"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(AUDIO_FOLDER, exist_ok=True)

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

    start_time = time.time()

# Extract PDF text
    text = extract_text(filepath)
    if len(text.strip()) == 0:
        return """
    <h2>Document Not Readable</h2>
    <p>
    This PDF appears to contain scanned images rather than selectable text.
    OCR support is coming soon.
    Please upload a text-based PDF for now.
    </p>
    """

    print("TEXT LENGTH:", len(text))
    print(text[:500])

    print("PDF Extraction:", time.time() - start_time)

# Generate summary
    summary = summarize(text)

    print("Summary Generation:", time.time() - start_time)

# Generate audio
    audio_path = "static/audio/summary.mp3"

    generate_audio(
        summary,
        audio_path
)

    print("Audio Generation:", time.time() - start_time)

    html_summary = markdown.markdown(summary)

    return render_template(
    "result.html",
    summary=html_summary
)
if __name__ == "__main__":
    app.run(debug=True)