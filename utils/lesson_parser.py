import re

from utils.lesson_engine import LessonBlock


def parse_lesson(lesson_text):
    """
    Converts an AI-generated lesson into LessonBlocks.
    """

    sections = re.split(r"^##\s+", lesson_text, flags=re.MULTILINE)

    blocks = []

    block_id = 1

    for section in sections:

        section = section.strip()

        if not section:
            continue

        lines = section.split("\n", 1)

        title = lines[0].strip()

        content = lines[1].strip() if len(lines) > 1 else ""

        requires_response = any(
            phrase in title.lower()
            for phrase in [
                "check your understanding",
                "your turn",
                "practice",
                "question",
                "exercise"
            ]
        )

        blocks.append(
            LessonBlock(
                id=block_id,
                title=title,
                content=content,
                requires_response=requires_response
            )
        )

        block_id += 1

    return blocks