from flask import Flask, render_template, request
import os
import markdown
import time
import json


from utils.pdf_reader import extract_text
from utils.summarizer import summarize
from utils.tts import generate_audio
from utils.database import save_user
from utils.quiz_generator import generate_quiz
from utils.takeaway_generator import generate_takeaway
from utils.tutor import ask_tutor

app = Flask(__name__)

app.config["CHAT_HISTORY"] = []

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

    # User details
    full_name = request.form["full_name"]
    institution = request.form["institution"]
    email = request.form["email"]

    print("USER:", full_name)
    print("INSTITUTION:", institution)
    print("EMAIL:", email)

    # Uploaded file
    file = request.files["file"]

    filepath = os.path.join(
        app.config["UPLOAD_FOLDER"],
        file.filename
    )

    file.save(filepath)

    # Save user record

# save_user(
#     full_name,
#     institution,
#     email,
#     file.filename
# )



    start_time = time.time()

    # Extract PDF text
    text = extract_text(filepath)
    app.config["CURRENT_DOCUMENT"] = text
    app.config["CHAT_HISTORY"] = []

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
    print("PDF Extraction:", time.time() - start_time)

    # Generate lesson summary
    summary = summarize(text)
    takeaway = generate_takeaway(summary)

    print("Summary Generation:", time.time() - start_time)

    # Generate audio lesson
    audio_path = "static/audio/summary.mp3"
    
    audio_summary = summary[:2500]

    generate_audio(
    audio_summary,
    audio_path
)       

    print("Audio Generation:", time.time() - start_time)

        # Generate quiz
    quiz_json = generate_quiz(summary)

    print("\n========== QUIZ JSON ==========")
    print(quiz_json)
    print("================================\n")

    try:
        quiz = json.loads(quiz_json)

    except json.JSONDecodeError as e:
        print("JSON ERROR:", e)

        quiz = [
            {
                "question": "Quiz generation failed.",
                "options": [
                    "Please try again",
                    "",
                    "",
                    ""
                ],
                "answer": 0,
                "explanation": str(e)
            }
        ]

    print("Quiz Generation:", time.time() - start_time)

    # Convert markdown summary to HTML
    html_summary = markdown.markdown(summary)

    return render_template(
    "index.html",
    summary=html_summary,
    audio_file=audio_path,
    quiz=quiz,
    takeaway=takeaway
)

@app.route("/ask", methods=["POST"])
def ask():

    question = request.form["question"]

    document_text = app.config.get(
        "CURRENT_DOCUMENT",
        ""
    )

    chat_history = app.config.get(
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

    app.config["CHAT_HISTORY"] = chat_history

    return answer

if __name__ == "__main__":
    app.run(debug=True)