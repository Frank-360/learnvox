from enum import Enum


class TeacherState(Enum):

    WELCOME = "welcome"

    TEACHING = "teaching"

    WAITING_FOR_ANSWERS = "waiting_for_answers"

    EVALUATING = "evaluating"

    FEEDBACK = "feedback"

    REINFORCING = "reinforcing"

    FINISHED = "finished"