import os
import time

from flask import Flask, render_template, request, session

from utils.pdf_reader import extract_text
from utils.database import save_user
from utils.tutor import ask_tutor


app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "learnvox-secret-key")

UPLOAD_FOLDER = "static/uploads"
AUDIO_FOLDER = "static/audio"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(AUDIO_FOLDER, exist_ok=True)


# =====================================================
# HOME
# =====================================================

@app.route("/")
def home():
    return render_template("index.html")


# =====================================================
# UPLOAD DOCUMENT
# =====================================================

@app.route("/upload", methods=["POST"])
def upload():

    # -------------------------
    # User Details
    # -------------------------

    full_name = request.form["full_name"]
    institution = request.form["institution"]
    email = request.form["email"]

    print("USER:", full_name)
    print("INSTITUTION:", institution)
    print("EMAIL:", email)

    # -------------------------
    # Uploaded File
    # -------------------------

    file = request.files["file"]

    if file.filename == "":
        return "No file selected."

    filepath = os.path.join(
        app.config["UPLOAD_FOLDER"],
        file.filename
    )

    file.save(filepath)

    # -------------------------
    # Save User
    # -------------------------

    save_user(
        full_name,
        institution,
        email,
        file.filename
    )

    start_time = time.time()

    # -------------------------
    # Extract PDF
    # -------------------------

    text = extract_text(filepath)

    if len(text.strip()) == 0:

        return """
        <h2>Document Not Readable</h2>

        <p>

        This PDF appears to contain scanned images rather than selectable text.

        OCR support is coming soon.

        Please upload a text-based PDF.

        </p>
        """

    print("TEXT LENGTH:", len(text))
    print("Extraction Time:", time.time() - start_time)

    # -------------------------
    # Store Session
    # -------------------------

    session.clear()

    session["CURRENT_DOCUMENT"] = text
    session["CHAT_HISTORY"] = []

    session["USER_NAME"] = full_name
    session["INSTITUTION"] = institution
    session["FILE_NAME"] = file.filename

    print("Document stored successfully.")

    # -------------------------
    # Open AI Tutor Dashboard
    # -------------------------

    return render_template(
        "tutor.html",
        name=full_name,
        filename=file.filename
    )


# =====================================================
# AI TUTOR CHAT
# =====================================================

@app.route("/ask", methods=["POST"])
def ask():

    question = request.form["question"]

    document_text = session.get(
        "CURRENT_DOCUMENT",
        ""
    )

    chat_history = session.get(
        "CHAT_HISTORY",
        []
    )

    answer = ask_tutor(
        document_text,
        question,
        chat_history
    )

    chat_history.append(
        {
            "question": question,
            "answer": answer
        }
    )

    session["CHAT_HISTORY"] = chat_history

    return answer


# =====================================================
# RUN APP
# =====================================================

if __name__ == "__main__":
    app.run(debug=True)