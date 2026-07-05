import os
import time
import markdown
import traceback

import os

print("RUNNING APP:", os.path.abspath(__file__))


from flask import (
    Flask,
    render_template,
    request,
    session,
    jsonify
)

from utils.pdf_reader import extract_text

from utils.database import (
    save_or_update_user,
    can_use_quick_learn,
    increment_quick_learn,
    update_plan,
    get_user
)

from utils.tutor import ask_tutor

from utils.summarizer import generate_ai_lesson
from utils.quick_learn import generate_quick_learn
from utils.takeaway_generator import generate_takeaway
from utils.lesson_export import (
    create_lesson_doc,
    clean_filename
)
from utils.tts import generate_audio
from utils.quiz_generator import generate_quiz
from utils.flashcard_generator import generate_flashcards

from utils.paystack import (
    initialize_payment,
    verify_payment
)




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
    save_or_update_user(
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

    # -------------------------
# Store Session
# -------------------------

    session.clear()

    session["CURRENT_DOCUMENT"] = text
    session["CHAT_HISTORY"] = []

    session["USER_NAME"] = full_name
    session["EMAIL"] = email
    session["INSTITUTION"] = institution
    session["FILE_NAME"] = file.filename

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

    print("=" * 60)
    print("QUICK LEARN ROUTE ENTERED")
    print("=" * 60)

    try:

        # -------------------------
        # Get current document
        # -------------------------

        document = session.get("CURRENT_DOCUMENT", "")

        if not document:

            return jsonify({
                "success": False,
                "message": "No document loaded."
            }), 400

        # -------------------------
        # Get user email
        # -------------------------

        email = session.get("EMAIL")

        if not email:

            return jsonify({
                "success": False,
                "message": "No user session found."
            }), 400

        print("EMAIL:", email)

        # -------------------------
        # Check usage limit
        # -------------------------

        allowed = can_use_quick_learn(email)

        print("ALLOWED:", allowed)

        if not allowed:

            return jsonify({
                "success": False,
                "upgrade": True,
                "message": "You've reached today's free Quick Learn limit."
            })

        # -------------------------
        # Generate lesson
        # -------------------------

        print("Generating Quick Learn...")

        quick = generate_quick_learn(document)

        print("Quick Learn generated successfully.")

        # -------------------------
        # Count successful usage
        # -------------------------

        increment_quick_learn(email)

        print("Usage updated.")

        html = markdown.markdown(quick)

        return jsonify({

            "success": True,
            "quick": html

        })

    except Exception:

        traceback.print_exc()

        return jsonify({

            "success": False,
            "message": "Unable to generate Quick Learn."

        }), 500

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
    
    base_name = clean_filename(
    os.path.splitext(
        session.get("FILE_NAME", "lesson")
    )[0]
)

    audio_filename = f"audio/{base_name}.mp3"

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

    try:

        data = request.get_json()

        question = data.get("question", "")

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

        return jsonify({
            "answer": answer
        })

    except Exception as e:

        print("ASK ROUTE ERROR:", e)

        return jsonify({
            "answer": str(e)
        }), 500
    



@app.route("/pricing")
def pricing():
    return render_template("pricing.html")



@app.route("/pay", methods=["POST"])
def pay():

    email = session.get("EMAIL")

    if not email:

        return jsonify({
            "success": False,
            "message": "No active session."
        }), 400

    payment = initialize_payment(
        email=email,
        amount=1000
    )

    print("PAYSTACK RESPONSE:")
    print(payment)

    if not payment.get("status"):

        return jsonify({
            "success": False,
            "message": payment.get(
                "message",
                "Unable to initialize payment."
            )
        }), 500

    return jsonify({

        "success": True,

        "checkout_url": payment["data"]["authorization_url"]

    })

@app.route("/verify-payment")
def verify_payment_route():

    reference = request.args.get("reference")

    if not reference:
        return "No payment reference found."

    payment = verify_payment(reference)

    print("=" * 50)
    print("PAYMENT VERIFICATION")
    print(payment)
    print("=" * 50)

    if not payment.get("status"):
        return "Payment verification failed."

    data = payment.get("data", {})

    if data.get("status") != "success":
        return "Payment was not successful."

    # -----------------------------------------
    # Upgrade user to Founding Member
    # -----------------------------------------

    email = data.get("customer", {}).get("email")

    if not email:
        return "Unable to determine customer email."

    update_plan(email, "pro")

    return """
    <h2>🎉 Welcome to LearnVox Founding Membership!</h2>

    <p>
    Your subscription has been activated successfully.
    </p>

    <p>
    You now have:
    </p>

    <ul>
        <li>✅ Unlimited Quick Learn</li>
        <li>✅ Unlimited Deep Dive</li>
        <li>✅ Unlimited AI Tutor</li>
        <li>✅ Unlimited Quizzes</li>
        <li>✅ Unlimited Flashcards</li>
    </ul>

    <p>
    You can now return to LearnVox and continue learning.
    </p>
    """

# =====================================================
# RUN APP
# =====================================================



print(app.url_map)

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)



