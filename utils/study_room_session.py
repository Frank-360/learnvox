from utils.lesson_engine import LessonEngine
from utils.lesson_parser import parse_lesson


class StudyRoomSession:

    def __init__(self, lesson_text):

        self.engine = LessonEngine()

        blocks = parse_lesson(lesson_text)

        for block in blocks:
            self.engine.add(block)

    def current_block(self):
        return self.engine.current_block()

    def next_block(self):
        return self.engine.next()

    def progress(self):
        return self.engine.progress()

    def finished(self):
        return self.engine.is_finished()