from enum import Enum

class ClassroomState(Enum):

    WAITING = "waiting"

    WELCOME = "welcome"

    INTRODUCTION = "introduction"

    TEACHING = "teaching"

    QUESTION = "question"

    WAITING_FOR_ANSWERS = "waiting_for_answers"

    EVALUATING = "evaluating"

    FEEDBACK = "feedback"

    LESSON_COMPLETE = "lesson_complete"

    COMPLETED = "completed"