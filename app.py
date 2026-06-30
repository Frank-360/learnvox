import os
import time
import markdown

from flask import (
    Flask,
    render_template,
    request,
    session,
    jsonify
)

from utils.pdf_reader import extract_text
from utils.database import save_user
from utils.tutor import ask_tutor

from utils.summarizer import generate_ai_lesson
from utils.quick_learn import generate_quick_learn
from utils.takeaway_generator import generate_takeaway
from utils.lesson_export import create_lesson_doc
from utils.tts import generate_audio
from utils.quiz_generator import generate_quiz
from utils.flashcard_generator import generate_flashcards




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
# QUICK LEARN
# =====================================================

@app.route("/quick-learn", methods=["POST"])
def quick_learn():

    document = session.get(
        "CURRENT_DOCUMENT",
        ""
    )

    if not document:

        return jsonify({

            "success": False,

            "message": "No document loaded."

        })

    quick = generate_quick_learn(document)

    html = markdown.markdown(quick)

    return jsonify({

        "success": True,

        "quick": html

    })

# =====================================================
# SUMMARY MODE
# =====================================================

@app.route("/summary", methods=["POST"])
def summary():

    document = session.get(
        "CURRENT_DOCUMENT",
        ""
    )

    if not document:

        return jsonify({

            "success": False,
            "message": "No document loaded."

        })

    lesson = generate_ai_lesson(document)

    takeaway = generate_takeaway(lesson)

    lesson_file = create_lesson_doc(
    session.get("USER_NAME"),
    session.get("INSTITUTION"),
    lesson,
    takeaway,
    session.get("FILE_NAME")
)
    audio_filename = f"audio/{session.get('FILE_NAME','lesson')}.mp3"

    audio_path = os.path.join(
        "static",
        audio_filename
    )

    generate_audio(
        lesson,
        audio_path
    )

    html_lesson = markdown.markdown(lesson)

    return jsonify({

    "success": True,

    "lesson": html_lesson,

    "takeaway": takeaway,

    "lesson_file": lesson_file,

    "audio_file": "/static/" + audio_filename

})

# =====================================================
# QUIZ
# =====================================================

@app.route("/quiz", methods=["POST"])
def quiz():

    document = session.get(
        "CURRENT_DOCUMENT",
        ""
    )

    if not document:

        return jsonify({

            "success": False,

            "message": "No document loaded."

        })

    quiz = generate_quiz(document)

    return jsonify({

        "success": True,

        "quiz": quiz

    })


@app.route("/flashcards")
def flashcards():

    text = session.get("CURRENT_DOCUMENT")

    if not text:
        return "No document uploaded."

    cards = generate_flashcards(text)

    return jsonify({
    "success": True,
    "flashcards": cards
})



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