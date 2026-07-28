from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from utils.classroom_engine import StudyRoom
from utils.teacher_ai import TeacherAI


@dataclass
class ClassroomSession:

    room: StudyRoom

    teacher: TeacherAI

    started_at: datetime = field(default_factory=datetime.utcnow)

    lesson_started: bool = False

    active_block: int = 0

    active_question = None

    waiting_for_answers: bool = False

    learner_answers: dict = field(default_factory=dict)

    discussion: list = field(default_factory=list)

    completed: bool = False

    lesson_engine = None

    def start(self):

        self.lesson_started = True

        self.room.add_event("Class session started.")


    def finish(self):

        self.completed = True

        self.room.addself.current_question_event("Class session finished.")



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