from utils.study_room_generator import generate_study_room_lesson
from utils.lesson_parser import parse_lesson
from utils.lesson_engine import LessonEngine

from utils.teacher_state import TeacherState

from utils.answer_evaluator import evaluate_answer

from utils.classroom_engine import (
    ClassroomNotReadyError
)

from enum import Enum


class TeachingDecision(Enum):
    CONTINUE = "continue"
    REVIEW = "review"
    RETEACH = "reteach"


class TeacherAI:

    def __init__(self, name="LearnVox Teacher"):
        self.name = name

    # -------------------------------------------------
    # WELCOME
    # -------------------------------------------------

    def welcome(self, room):

        learner_count = len(room.learners)

        if learner_count == 0:
            return (
                "Welcome! I'm preparing today's classroom. "
                "Once learners arrive, we'll begin today's lesson together."
            )

        elif learner_count == 1:
            return (
                f"Welcome back, {room.learners[0].name}. "
                "I'm glad you're here. We'll wait a little longer for the remaining learners."
            )

        elif learner_count < 5:
            return (
                f"Wonderful! {learner_count} learners are now in the classroom. "
                "Please get comfortable while everyone joins."
            )

        return (
            f"Excellent! {learner_count} learners are ready. "
            "We'll begin today's lesson very soon."
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

        if not self.can_start(engine):
            raise ClassroomNotReadyError(
                "Not everyone is ready."
            )

        engine.start_class()

        session.lesson_started = True
        session.teacher_state = TeacherState.TEACHING

        session.room.add_event(
            "Teacher started the class."
        )

        return (
            "Welcome everyone! "
            "Today's lesson is about to begin."
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

        if block.block_type in ("checkpoint", "practice"):
            return self.ask_question(session)

        return block.content.strip()

            # ---------------------------------
        # QUESTION BLOCKS
        # ---------------------------------

        if block.block_type in ("checkpoint", "practice"):
            return self.ask_question(session)

        # ---------------------------------
        # TEACHING BLOCKS
        # ---------------------------------

        session.teacher_state = TeacherState.TEACHING

        return block.content.strip()

    # =====================================
    # NEXT BLOCK
    # =====================================

    def next_block(self, session):

        if session.lesson_engine is None:
            return None

        session.lesson_engine.next()

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

        session.teacher_state = TeacherState.EVALUATING

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

        session.waiting_for_answers = False

        session.teacher_state = TeacherState.FEEDBACK

        session.room.add_event(
            f"{learner.name} answered: {answer}"
        )

        return {
            "correct": correct,
            "score": score,
            "feedback": feedback
        }

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