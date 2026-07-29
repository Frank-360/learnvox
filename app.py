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
    jsonify,
    redirect
)

from utils.pdf_reader import extract_text

from utils.database import (
    save_or_update_user,
    can_use_quick_learn,
    can_use_deep_dive,
    increment_quick_learn,
    increment_deep_dive,
    increment_documents_uploaded,
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

from utils.classroom_engine import (
    StudyRoom,
    ClassroomEngine,
    Learner
)


app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "learnvox-secret-key")


# ======================================
# STUDY ROOMS (MVP)
# ======================================

from utils.teacher_ai import TeacherAI, TeachingDecision
from utils.classroom_session import ClassroomSession

rooms = {}
sessions = {}

default_room = StudyRoom(
    room_id="LV-001",
    title="Introduction to AI",
    host_id="frank"
)

room_engine = ClassroomEngine(default_room)

teacher = TeacherAI()

class_session = ClassroomSession(
    room=default_room,
    teacher=teacher,
    classroom_engine=room_engine
)


rooms[default_room.room_id] = room_engine
sessions[default_room.room_id] = class_session



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
# STUDY ROOM
# =====================================================

@app.route("/study-room")
def study_room_page():

    print("USER_NAME:", session.get("USER_NAME"))
    print("EMAIL:", session.get("EMAIL"))
    print("FILE_NAME:", session.get("FILE_NAME"))

    if not session.get("USER_NAME"):
        return redirect("/")

    engine = rooms["LV-001"]
    class_session = sessions["LV-001"]

    if not session.get("ROOM_USER_ID"):

        learner = Learner(
            id=str(len(engine.room.learners) + 1),
            name=session["USER_NAME"]
        )

        engine.join(learner)

        session["ROOM_USER_ID"] = learner.id
        session["ROOM_USER_NAME"] = learner.name

    # Always determine what the teacher should say
    teacher_message = class_session.teacher.get_current_message(
        class_session
    )

    show_next_button = (
        class_session.lesson_started
        and class_session.lesson_engine is not None
        and not class_session.lesson_engine.is_finished()
    )

    return render_template(
        "study_room.html",
        room=class_session.room,
        class_session=class_session,
        teacher_message=teacher_message,
        show_next_button=show_next_button
    )

# =====================================
# SUBMIT ANSWER
# =====================================

@app.route("/study-room/answer", methods=["POST"])
def submit_answer():

    print(">>> submit_answer route reached <<<")

    if not session.get("ROOM_USER_ID"):
        return jsonify({
            "success": False,
            "message": "Learner not found."
        })

    answer = request.form.get("answer", "").strip()

    if not answer:
        return jsonify({
            "success": False,
            "message": "Please enter an answer."
        })

    engine = rooms["LV-001"]
    class_session = sessions["LV-001"]

    learner = next(
        (
            l for l in engine.room.learners
            if l.id == session["ROOM_USER_ID"]
        ),
        None
    )

    if learner is None:
        return jsonify({
            "success": False,
            "message": "Learner not found."
        })

   # Record the learner's answer in the classroom
    learner = engine.submit_answer(
        learner.id,
        answer
    )

        # ==========================================
    # Evaluate this learner's answer
    # ==========================================

    result = class_session.teacher.evaluate_answer(
        class_session,
        learner,
        answer
    )

    # Save learner's evaluation
    learner.last_score = result["score"]
    learner.last_feedback = result["feedback"]
    learner.evaluation_complete = True
    learner.mastery_score = result["score"]

    # ==========================================
    # Wait for the rest of the class
    # ==========================================

    if engine.everyone_answered():

        # Teacher decides what to do with the whole class
        decision = class_session.teacher.decide_next_action(
            class_session
        )

        if decision["action"] == TeachingDecision.CONTINUE:

            class_session.teacher.next_block(class_session)

        elif decision["action"] == TeachingDecision.REVIEW:

            # We'll implement this next
            pass

        elif decision["action"] == TeachingDecision.RETEACH:

            # We'll implement this next
            pass

    else:

        # Other learners haven't answered yet
        decision = {
            "action": "waiting",
            "reason": "Waiting for the remaining learners to answer."
        }

    # ==========================================
    # Send response back to this learner
    # ==========================================

    return jsonify({
            "success": True,
            "correct": result["correct"],
            "score": result["score"],
            "feedback": result["feedback"],
            "decision": (
                decision["action"].value
                if isinstance(decision["action"], TeachingDecision)
                else decision["action"]
            ),
            "reason": decision["reason"]
        })
# =====================================================
# JOIN STUDY ROOM
# =====================================================

@app.route("/join-room", methods=["POST"])
def join_room():

    room_engine = rooms["LV-001"]

    # Already joined?
    if session.get("ROOM_USER_ID"):

        return study_room_page()

    # Get user's LearnVox name
    name = session.get("USER_NAME")

    if not name:

        return "User session not found.", 400

    learner = Learner(

        id=str(len(room_engine.room.learners) + 1),

        name=name

    )

    room_engine.join(learner)

    session["ROOM_USER_ID"] = learner.id
    session["ROOM_USER_NAME"] = learner.name

    return study_room_page()


# =====================================================
# I'M READY
# =====================================================

@app.route("/ready", methods=["POST"])
def ready():

    learner_id = session.get("ROOM_USER_ID")

    if learner_id:

        engine = rooms["LV-001"]
        class_session = sessions["LV-001"]

        engine.mark_ready(learner_id)

        # Automatically start the class
        if engine.everyone_ready():

            class_session.teacher.start_class(
                class_session,
                engine
            )

    return redirect("/study-room")


# =====================================
# NEXT LESSON BLOCK
# =====================================

@app.route("/study-room/next", methods=["POST"])
def next_lesson():

    class_session = sessions["LV-001"]

    class_session.teacher.next_block(
        class_session
    )

    return redirect("/study-room")


@app.route("/study-room/question", methods=["POST"])
def study_room_question():

    class_session = sessions["LV-001"]

    question = request.form["question"]

    class_session.teacher.answer_student_question(
        class_session,
        question
    )

    return redirect("/study-room")




# =====================================================
# UPLOAD DOCUMENT
# =====================================================

@app.route("/upload", methods=["POST"])
def upload():

    # -------------------------
    # User Details
    # -------------------------

    full_name = request.form["full_name"]
    institution = request.form.get("institution", "").strip()
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
    
    increment_documents_uploaded(email)

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

    # -------------------------
    # Prepare Study Room Lesson
    # -------------------------

    class_session = sessions["LV-001"]

    class_session.teacher.prepare_lesson(
        class_session,
        text
    )

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

    document = session.get("CURRENT_DOCUMENT", "")

    if not document:

        return jsonify({
            "success": False,
            "message": "No document loaded."
        })

    email = session.get("EMAIL")

    if not email:

        return jsonify({
            "success": False,
            "message": "No user session found."
        }), 400

    allowed = can_use_deep_dive(email)

    if not allowed:

        user = get_user(email)

        return jsonify({

        "success": False,

        "upgrade": True,

       "daily_complete": user.get("plan") == "free",

        "quick_learn_used": user.get("quick_learn_used", 0),

        "deep_dive_used": user.get("deep_dive_used", 0),

        "documents_uploaded": user.get("documents_uploaded", 0),

        "message": "You've completed today's free learning."

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

# -------------------------
# Count successful Deep Dive
# -------------------------

    increment_deep_dive(email)

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


@app.route("/account")
def account():

    print("SESSION EMAIL:", session.get("EMAIL"))

    email = session.get("EMAIL")

    if not email:

        return jsonify({
            "success": False,
            "message": "No email in session"
        }), 400

    user = get_user(email)

    if not user:

        return jsonify({
            "success": False,
            "message": "Unable to retrieve your account."
        }), 500

    return jsonify({

        "success": True,

        "plan": user.get("plan", "free"),

        "subscription_status": user.get("subscription_status"),

        "quick_learn_used": user.get("quick_learn_used", 0),

        "deep_dive_used": user.get("deep_dive_used", 0),

        "quiz_used": user.get("quiz_used", 0),

        "flashcard_used": user.get("flashcard_used", 0),

        "documents_uploaded": user.get("documents_uploaded", 0)

    })

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
# AI CLASSROOM
# =====================================================

@app.route("/classroom")
def classroom_home():
    return render_template("classroom_home.html")


@app.route("/classroom/create")
def create_classroom():
    return render_template("create_classroom.html")


@app.route("/join")
def join_classroom():
    return render_template("join_classroom.html")

# =====================================================
# RUN APP
# =====================================================



print(app.url_map)

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)

