from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class ClassroomEventType(Enum):

    CLASS_STARTED = "class_started"

    LESSON_STARTED = "lesson_started"

    BLOCK_STARTED = "block_started"

    QUESTION_ASKED = "question_asked"

    ANSWER_SUBMITTED = "answer_submitted"

    EVALUATION_COMPLETED = "evaluation_completed"

    FEEDBACK_GIVEN = "feedback_given"

    LESSON_COMPLETED = "lesson_completed"


@dataclass
class ClassroomEvent:

    event_type: ClassroomEventType

    message: str

    timestamp: datetime = datetime.utcnow()