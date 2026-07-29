from dataclasses import dataclass
from typing import Optional


@dataclass
class LessonBlock:
    id: int
    title: str

    # teaching | checkpoint | practice | summary
    block_type: str

    # Normal teaching content
    content: str = ""

    # Used for checkpoints and practice
    question: Optional[str] = None
    expected_answer: Optional[str] = None
    teacher_feedback: Optional[str] = None

    # Temporary (for backward compatibility)
    requires_response: bool = False


class LessonEngine:

    def __init__(self):
        self.blocks = []
        self.current = 0

    def add(self, block):
        self.blocks.append(block)

    def current_block(self):
        if self.current >= len(self.blocks):
            return None
        return self.blocks[self.current]

    def next(self):
        if self.current < len(self.blocks):
            self.current += 1
        return self.current_block()

    def previous(self):
        if self.current > 0:
            self.current -= 1
        return self.current_block()

    def reset(self):
        self.current = 0

    def is_finished(self):
        return self.current >= len(self.blocks)

    def progress(self):
        if len(self.blocks) == 0:
            return 0
        return round((self.current / len(self.blocks)) * 100)

    def total_blocks(self):
        return len(self.blocks)