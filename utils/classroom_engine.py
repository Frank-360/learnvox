# =====================================
# IMPORTS
# =====================================

from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from typing import List


# =====================================
# ENUMS
# =====================================

class RoomStatus(Enum):

    WAITING = "waiting"

    READY_CHECK = "ready_check"

    STARTING = "starting"

    TEACHING = "teaching"

    DISCUSSION = "discussion"

    QUIZ = "quiz"

    REVIEW = "review"

    COMPLETED = "completed"

class DeliveryMode(Enum):
    TEXT = "text"
    AUDIO = "audio"
    VOICE = "voice"


class LearnerStatus(Enum):
    JOINED = "joined"
    READY = "ready"
    ANSWERING = "answering"
    DISCONNECTED = "disconnected"

class ClassroomNotReadyError(Exception):
    """Raised when someone tries to start a class before everyone is ready."""
    pass


# =====================================
# LEARNER
# =====================================

@dataclass
class Learner:
    id: str
    name: str

    delivery_mode: DeliveryMode = DeliveryMode.TEXT
    status: LearnerStatus = LearnerStatus.JOINED

    participation_score: int = 0
    mastery_score: float = 0.0

    # -------------------------------
    # Current checkpoint state
    # -------------------------------

    current_answer: str = ""

    has_answered: bool = False

    answer_time: datetime | None = None

    last_score: float = 0.0

    last_feedback: str = ""

    evaluation_complete: bool = False

    # -------------------------------
    # Live classroom state
    # -------------------------------

    hand_raised: bool = False

    connected: bool = True

# =====================================
# STUDY ROOM
# =====================================

from dataclasses import dataclass, field


@dataclass
class StudyRoom:
    room_id: str
    title: str
    host_id: str

    learners: List[Learner] = field(default_factory=list)

    status: RoomStatus = RoomStatus.WAITING

    current_block: int = 0

    created_at: datetime = field(default_factory=datetime.utcnow)

    events: List[str] = field(default_factory=list)

    def add_event(self, message: str):
        self.events.append(message)


# =====================================
# CLASSROOM ENGINE
# =====================================

class ClassroomEngine:

    def __init__(self, room: StudyRoom):
        self.room = room

    def join(self, learner: Learner):

        for existing in self.room.learners:

            if existing.id == learner.id:
                return

        self.room.learners.append(learner)

    def mark_ready(self, learner_id: str):

        for learner in self.room.learners:

            if learner.id == learner_id:
                learner.status = LearnerStatus.READY

    def everyone_ready(self):

        if len(self.room.learners) == 0:
            return False

        return all(
            learner.status == LearnerStatus.READY
            for learner in self.room.learners
        )

    def ready_count(self):

        return sum(
            learner.status == LearnerStatus.READY
            for learner in self.room.learners
        )

   
    def start_class(self):

        if not self.everyone_ready():
            raise ClassroomNotReadyError(
                "Not everyone is ready."
            )

    def submit_answer(self, learner_id: str, answer: str):

        for learner in self.room.learners:

            if learner.id == learner_id:

                learner.current_answer = answer
                learner.has_answered = True
                learner.answer_time = datetime.utcnow()

                learner.status = LearnerStatus.ANSWERING

                self.room.add_event(
                    f"{learner.name} submitted an answer."
                )

                return learner

        return None


    def answer_count(self):

        return sum(
            learner.has_answered
            for learner in self.room.learners
        )

    def waiting_learners(self):

        return [
            learner
            for learner in self.room.learners
            if not learner.has_answered
        ]

    def everyone_answered(self):

        print("===== CLASSROOM STATUS =====")

        for learner in self.room.learners:

            print(
                learner.name,
                "| answered:",
                learner.has_answered
            )

        print("============================")

        return all(
                learner.has_answered
                for learner in self.room.learners
            )


    def reset_answers(self):

        print(">>> RESETTING ANSWERS <<<")

        for learner in self.room.learners:

            print("Reset:", learner.name)

            learner.current_answer = ""
            learner.has_answered = False
            learner.answer_time = None

            learner.last_feedback = ""
            learner.last_score = 0.0

            learner.evaluation_complete = False

            learner.status = LearnerStatus.READY

        print(">>> RESET COMPLETE <<<")
    
    def average_score(self):

        evaluated = [
            learner.last_score
            for learner in self.room.learners
            if learner.evaluation_complete
        ]

        if not evaluated:
            return 0

        return round(sum(evaluated) / len(evaluated), 1)

    def evaluated_count(self):

        return sum(
            learner.evaluation_complete
            for learner in self.room.learners

        )

    def struggling_learners(self, threshold=60):

        return [
            learner
            for learner in self.room.learners
            if learner.evaluation_complete
            and learner.last_score < threshold
        ]


    