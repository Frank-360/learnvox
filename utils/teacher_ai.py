from utils.study_room_generator import generate_study_room_lesson
from utils.lesson_parser import parse_lesson
from utils.lesson_engine import LessonEngine

from utils.teacher_state import TeacherState

from utils.answer_evaluator import evaluate_answer, evaluate_class_answers

from utils.classroom_engine import (
    ClassroomNotReadyError
)

from enum import Enum

from datetime import datetime

from utils.classroom.state import ClassroomState


class TeachingDecision(Enum):
    CONTINUE = "continue"
    REVIEW = "review"
    RETEACH = "reteach"


class TeacherAI:

    def __init__(self, name="LearnVox"):
        self.name = name

    # -------------------------------------------------
    # WELCOME
    # -------------------------------------------------

    def greeting(self):

        hour = datetime.now().hour

        if hour < 12:
            return "Good morning"

        elif hour < 17:
            return "Good afternoon"

        return "Good evening"


    def welcome(self, room):

        learner_count = len(room.learners)

        if learner_count == 0:
            return (
                f"Good day! I'm {self.name}.\n\n"
                "I'm getting today's lesson ready.\n"
                "Once everyone has arrived and taken a seat, we'll begin."
            )

        elif learner_count == 1:
            return (
                f"Welcome, {room.learners[0].name}!\n\n"
                "I'm glad you're here.\n"
                "We'll begin as soon as the rest of the class is ready."
            )

        elif learner_count < 5:
            return (
                f"Welcome everyone!\n\n"
                f"I can see {learner_count} learners are in the classroom.\n"
                "Please take your seats and we'll begin shortly."
            )

        return (
                f"Excellent! All {learner_count} learners are here.\n\n"
                "Everyone is seated, and we're ready to begin today's lesson."
            )

    # -------------------------------------------------
    # CURRENT MESSAGE
    # -------------------------------------------------

    def get_current_message(self, session):
        """
        Returns the message the teacher should display.
        """

        if not session.lesson_started:
            return self.welcome(session.room)

        if session.waiting_for_answers:
            return self.ask_question(session)

        if session.lesson_engine is None:
            return "I'm preparing today's lesson..."

        return self.teach(session)

    # =====================================
    # CAN START?
    # =====================================

    def can_start(self, engine):

        return engine.everyone_ready()

    # =====================================
    # START CLASS
    # =====================================

    
    def start_class(self, session, engine):

    # TEMPORARILY DISABLED WHILE BUILDING THE TEACHING FLOW
    # if not self.can_start(engine):
    #     raise ClassroomNotReadyError(
    #         "Not everyone is ready."
    #     )

        if engine is not None and len(session.room.learners) > 0:
            engine.start_class()

        session.lesson_started = True
        session.teacher_state = TeacherState.TEACHING

        session.room.add_event(
            "Teacher started the class."
        )

        return (
            f"{self.greeting()} everyone!\n\n"
            f"I'm {self.name}, and I'll be guiding today's lesson.\n\n"
            f"Today we'll be learning:\n"
            f"{session.room.title}\n\n"
            "By the end of today's lesson, you'll have a solid understanding of this topic.\n\n"
            "Let's begin!"
        )

    # =====================================
    # PREPARE LESSON
    # =====================================

    def prepare_lesson(self, session, document):

        lesson = generate_study_room_lesson(document)

        lesson_title, blocks = parse_lesson(lesson)

        engine = LessonEngine()

        for block in blocks:
            engine.add(block)

        session.lesson_engine = engine

        session.room.title = lesson_title

        session.room.add_event(
            "Teacher prepared today's lesson."
        )

# =====================================
# TEACH
# =====================================


    def teach(self, session):

        if session.lesson_engine is None:
            return "I haven't prepared today's lesson yet."

        block = session.lesson_engine.current_block()

        if block is None:

            session.teacher_state = TeacherState.FINISHED

            return "Today's lesson is complete."

        session.teacher_state = TeacherState.TEACHING

        session.room.add_event(
            f"Teacher taught: {block.title}"
        )

        # ---------------------------------
        # QUESTION BLOCKS
        # ---------------------------------

        if block.block_type in ("checkpoint", "practice"):
            return self.ask_question(session)

        # ---------------------------------
        # TEACHING BLOCKS
        # ---------------------------------

        return block.content.strip()

    # =====================================
    # NEXT BLOCK
    # =====================================

    def next_block(self, session):

        print("NEXT BLOCK CALLED")
        print("Current block index:", session.lesson_engine.current)

        if session.lesson_engine is None:
            return None

        session.lesson_engine.next()

        print("New block index:", session.lesson_engine.current)

        return self.teach(session)

    # =====================================
    # ASK QUESTION
    # =====================================

    def ask_question(self, session):

        if session.lesson_engine is None:
            return None

        block = session.lesson_engine.current_block()

        if block is None:
            return None

        if block.block_type not in ("checkpoint", "practice"):
            return None

        session.active_question = block

        session.classroom_state = ClassroomState.WAITING_FOR_ANSWERS

        session.teacher_state = TeacherState.WAITING_FOR_ANSWERS

        session.waiting_for_answers = True


        session.room.add_event(
            f"Teacher asked: {block.question}"
        )

        return block.question

# =====================================
# EVALUATE ANSWER
# =====================================

    def evaluate_answer(self, session, learner, answer):

        if session.lesson_engine is None:
            return {
                "correct": False,
                "score": 0,
                "feedback": "There is no active lesson."
            }

        block = session.lesson_engine.current_block()

        if block is None:

            session.teacher_state = TeacherState.FINISHED

            return {
                "correct": False,
                "score": 0,
                "feedback": "The lesson has already finished."
            }

        if block.block_type not in ("checkpoint", "practice"):
            return {
                "correct": False,
                "score": 0,
                "feedback": "There is no question to answer right now."
            }

        try:

            evaluation = evaluate_answer(
                block.question,
                block.expected_answer,
                answer
            )

            correct = evaluation["correct"]
            score = evaluation["score"]
            feedback = evaluation["feedback"]

        except Exception as e:

            print(f"Answer evaluation error: {e}")

            correct = False
            score = 0
            feedback = (
                "Sorry, I couldn't evaluate your answer right now. "
                "Please try again."
            )

        session.room.add_event(
            f"{learner.name} answered: {answer}"
        )

        return {
            "correct": correct,
            "score": score,
            "feedback": feedback
        }


    # =====================================
    # DECIDE NEXT ACTION
    # =====================================

    def decide_next_action(self, session):

        engine = session.classroom_engine

        average = engine.average_score()
        struggling = len(engine.struggling_learners())
        total = len(engine.room.learners)

        if total == 0:
            return {
                "action": TeachingDecision.CONTINUE,
                "reason": "No learners in the classroom."
            }

        if average >= 80 and struggling <= max(1, int(total * 0.2)):
            return {
                "action": TeachingDecision.CONTINUE,
                "reason": "Most learners understood the concept."
            }

        if average >= 60:
            return {
                "action": TeachingDecision.REVIEW,
                "reason": "Some learners need a brief review."
            }

        return {
            "action": TeachingDecision.RETEACH,
            "reason": "The class needs this concept explained again."
        }


    # =====================================
    # EVALUATE CLASS
    # =====================================

    def evaluate_class(self, session):

        print(">>> evaluate_class() called")

        #session.teacher_state = TeacherState.EVALUATING

        session.classroom_state = ClassroomState.EVALUATING

        learners = session.room.learners

        if not learners:
            return

        # Reset previous evaluations
        for learner in learners:

            learner.last_score = 0
            learner.last_feedback = ""
            learner.evaluation_complete = False

        # Evaluate every learner
        # Collect all learner answers
        learner_answers = []

        for learner in learners:

            learner_answers.append({
                "name": learner.name,
                "answer": learner.current_answer
            })

        block = session.lesson_engine.current_block()

        evaluation = evaluate_class_answers(
                block.question,
                block.expected_answer,
                learner_answers
            )

            # Save the evaluation for each learner
        results = {
                result["name"]: result
                for result in evaluation["learners"]
            }

        for learner in learners:

            result = results.get(learner.name)

            if result is None:
                continue

            learner.last_score = result["score"]
            learner.last_feedback = result["feedback"]
            learner.evaluation_complete = True

        decision = self.decide_next_action(session)

        # session.waiting_for_answers = False
        # session.teacher_state = TeacherState.FEEDBACK

        # session.classroom_state = ClassroomState.FEEDBACK

        action = decision["action"]

        if action == TeachingDecision.CONTINUE:

            session.teacher_feedback = (
                "Excellent! Most of the class understood the concept. "
                "Let's continue."
            )

        elif action == TeachingDecision.REVIEW:

            session.teacher_feedback = (
                "Good effort everyone. Let's briefly review this concept "
                "before moving on."
            )

        elif action == TeachingDecision.RETEACH:

            session.teacher_feedback = (
                "I noticed several learners are still struggling. "
                "Let me explain this concept in a different way."
            )

        print("Decision:", decision)
        print("Teacher State:", session.teacher_state)
        print("Teacher Feedback:", session.teacher_feedback)

        return decision