from enum import Enum


class ClassroomState(Enum):
    CREATED = "created"
    LOBBY = "lobby"
    AI_LEARNING = "ai_learning"
    READY = "ready"
    IN_SESSION = "in_session"
    COMPLETED = "completed"