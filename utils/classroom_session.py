from dataclasses import dataclass, field
from datetime import datetime

from utils.teacher_state import TeacherState
from utils.classroom_engine import StudyRoom
from utils.teacher_ai import TeacherAI

from utils.lesson_engine import LessonEngine, LessonBlock

from utils.classroom_engine import ClassroomEngine

from utils.classroom_state import ClassroomState

from typing import List

from dataclasses import dataclass
from typing import Optional


@dataclass
class ClassroomSession:

    room: StudyRoom
    teacher: TeacherAI
    classroom_engine: ClassroomEngine | None = None

    class_started: bool = False

    last_transition: datetime = field(default_factory=datetime.utcnow)

    transition_seconds: int = 10

    current_lesson: Optional[str] = None

    # NEW
    current_message: str = ""

    # -------------------------------------
    # CLASSROOM STATE
    # -------------------------------------

    classroom_state: ClassroomState = ClassroomState.CREATED

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

        self.learner_answers[learner_name] = {

            "answer": answer,
            "submitted_at": datetime.utcnow(),
            "evaluation": None,
            "feedback": None

        }

        self.room.add_event(

            f"{learner_name} answered the current question."

        )

    def has_answered(self, learner_name):

        return learner_name in self.learner_answers


    def everyone_answered(self):

        if len(self.room.learners) == 0:
            return False

        return len(self.learner_answers) >= len(self.room.learners)


    def clear_answers(self):

        self.learner_answers.clear()