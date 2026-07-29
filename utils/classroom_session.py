from dataclasses import dataclass, field
from datetime import datetime

from utils.teacher_state import TeacherState
from utils.classroom_engine import StudyRoom
from utils.teacher_ai import TeacherAI

from utils.lesson_engine import LessonEngine, LessonBlock

from utils.classroom_engine import ClassroomEngine


@dataclass
class ClassroomSession:

    room: StudyRoom

    teacher: TeacherAI

    classroom_engine: ClassroomEngine | None = None

    started_at: datetime = field(default_factory=datetime.utcnow)

    # -------------------------------------
    # CLASS STATUS
    # -------------------------------------

    lesson_started: bool = False

    completed: bool = False

    teacher_state: TeacherState = TeacherState.WELCOME

    # -------------------------------------
    # LESSON
    # -------------------------------------

    lesson_engine: LessonEngine | None = None

    active_question: LessonBlock | None = None

    # -------------------------------------
    # QUESTIONS
    # -------------------------------------

    active_question = None

    waiting_for_answers: bool = False

    learner_answers: dict = field(default_factory=dict)

    # -------------------------------------
    # DISCUSSION
    # -------------------------------------

    discussion: list = field(default_factory=list)

    # -------------------------------------
    # START CLASS
    # -------------------------------------

    def start(self):

        self.lesson_started = True

        self.teacher_state = TeacherState.TEACHING

        self.room.add_event(
            "Class session started."
        )


    def finish(self):

        self.completed = True

        self.teacher_state = TeacherState.FINISHED

        self.room.add_event(
            "Class session finished."
        )


    def add_discussion(self, learner_name, message):

        self.discussion.append({

            "learner": learner_name,

            "message": message,

            "time": datetime.utcnow()

        })



    def submit_answer(self, learner_name, answer):

        self.learner_answers[learner_name] = answer

        self.room.add_event(

            f"{learner_name} answered the current question."

        )


    def clear_answers(self):

        self.learner_answers.clear()