from utils.study_room_generator import generate_study_room_lesson
from utils.lesson_parser import parse_lesson
from utils.lesson_engine import LessonEngine

from utils.classroom_engine import (
    ClassroomNotReadyError
)


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

        blocks = parse_lesson(lesson)

        engine = LessonEngine()

        for block in blocks:
            engine.add(block)

        session.lesson_engine = engine

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
            return "Today's lesson is complete."

        session.room.add_event(
            f"Teacher taught: {block.title}"
        )

        return block.content

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

        if not block.requires_response:
            return None

        session.active_question = block

        session.waiting_for_answers = True

        session.room.add_event(
            "Teacher asked a question."
        )

        return block.content