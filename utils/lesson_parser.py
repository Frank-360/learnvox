import re

from utils.lesson_engine import LessonBlock


def parse_lesson(lesson_text):
    """
    Converts an AI-generated lesson into LessonBlocks
    and extracts the lesson title.
    """

    sections = re.split(
        r"^##\s+",
        lesson_text,
        flags=re.MULTILINE
    )

    sections = [s.strip() for s in sections if s.strip()]

    # ----------------------------------
    # LESSON TITLE
    # ----------------------------------

    lesson_title = "Today's Lesson"

    if sections:
        lesson_title = sections[0].replace("#", "").strip()

        # Remove title so it doesn't become a lesson block
        sections = sections[1:]

    # ----------------------------------
    # LESSON BLOCKS
    # ----------------------------------

    blocks = []

    block_id = 1

    for section in sections:

        lines = section.split("\n", 1)

        title = lines[0].strip()

        body = lines[1].strip() if len(lines) > 1 else ""

        title_lower = title.lower()

        # ----------------------------------
        # DEFAULT VALUES
        # ----------------------------------

        block_type = "teaching"

        content = body

        question = None
        expected_answer = None
        teacher_feedback = None

        requires_response = False

        # ==================================
        # INTRODUCTION
        # ==================================

        if "introduction" in title_lower:

            block_type = "introduction"

        # ==================================
        # CONCEPT
        # ==================================

        elif "concept" in title_lower:

            block_type = "concept"

        # ==================================
        # EXAMPLE
        # ==================================

        elif "example" in title_lower:

            block_type = "example"

        # ==================================
        # CHECK YOUR UNDERSTANDING
        # ==================================

        elif "check your understanding" in title_lower:

            block_type = "checkpoint"

            requires_response = True

            question_match = re.search(
                r"Question:\s*(.*?)\n\s*Expected Answer:",
                body,
                re.DOTALL
            )

            answer_match = re.search(
                r"Expected Answer:\s*(.*?)\n\s*Teacher Feedback:",
                body,
                re.DOTALL
            )

            feedback_match = re.search(
                r"Teacher Feedback:\s*(.*)",
                body,
                re.DOTALL
            )

            question = (
                question_match.group(1).strip()
                if question_match else ""
            )

            expected_answer = (
                answer_match.group(1).strip()
                if answer_match else ""
            )

            teacher_feedback = (
                feedback_match.group(1).strip()
                if feedback_match else ""
            )

            content = ""

        # ==================================
        # PRACTICE
        # ==================================

        elif "practice" in title_lower:

            block_type = "practice"

            requires_response = True

            task_match = re.search(
                r"Task:\s*(.*?)\n\s*Expected Answer:",
                body,
                re.DOTALL
            )

            answer_match = re.search(
                r"Expected Answer:\s*(.*?)\n\s*Teacher Feedback:",
                body,
                re.DOTALL
            )

            feedback_match = re.search(
                r"Teacher Feedback:\s*(.*)",
                body,
                re.DOTALL
            )

            question = (
                task_match.group(1).strip()
                if task_match else ""
            )

            expected_answer = (
                answer_match.group(1).strip()
                if answer_match else ""
            )

            teacher_feedback = (
                feedback_match.group(1).strip()
                if feedback_match else ""
            )

            content = ""

        # ==================================
        # SUMMARY
        # ==================================

        elif "summary" in title_lower:

            block_type = "summary"

        # ==================================
        # CREATE LESSON BLOCK
        # ==================================

        blocks.append(

            LessonBlock(
                id=block_id,
                title=title,
                block_type=block_type,
                content=content,
                question=question,
                expected_answer=expected_answer,
                teacher_feedback=teacher_feedback,
                requires_response=requires_response
            )

        )

        block_id += 1

    return lesson_title, blocks