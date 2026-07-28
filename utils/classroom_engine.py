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


# =====================================
# STUDY ROOM
# =====================================

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

        self.room.status = RoomStatus.TEACHING