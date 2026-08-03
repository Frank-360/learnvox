from utils.teacher_state import TeacherState

from datetime import datetime, timedelta


class ClassroomController:

    def __init__(self, session):

        self.session = session
        self.teacher = session.teacher
        self.lesson = session.lesson_engine
        self.engine = session.classroom_engine

    # =====================================
    # START CLASS
    # =====================================

    def start(self):

        self.session.current_message = self.teacher.start_class(
            self.session,
            self.engine
        )

        self.session.last_transition = datetime.utcnow()

        return self.session.current_message

    # =====================================
    # SHOULD ADVANCE?
    # =====================================

    def should_advance(self):

        if self.session.waiting_for_answers:
            return False

        elapsed = datetime.utcnow() - self.session.last_transition

        return elapsed >= timedelta(
            seconds=self.session.transition_seconds
        )

    # =====================================
    # ADVANCE
    # =====================================

    def advance(self):

        if not self.should_advance():
            return False

        self.session.current_message = self.teacher.next_block(
            self.session
        )

        self.session.last_transition = datetime.utcnow()

        return True

    # =====================================
    # TEACH
    # =====================================

    def teach(self):

        self.session.current_message = self.teacher.next_block(
            self.session
        )

        return self.session.current_message

    # =====================================
    # SUBMIT ANSWER
    # =====================================

    def submit_answer(self, learner_id, answer):

        print("----- Learners in room -----")
        for l in self.session.room.learners:
            print(l.id, l.name)
        print("----------------------------")
        print("Looking for learner:", learner_id)

        # Find learner
        learner = next(
            (
                l for l in self.session.room.learners
                if l.id == learner_id
            ),
            None
        )

        if learner is None:
            return {
                "status": "learner_not_found"
            }

        # Store answer on the Learner object
        self.engine.submit_answer(
            learner.id,
            answer
        )

        # Wait until everyone has answered
        if not self.engine.everyone_answered():
            return {
                "status": "waiting"
            }

        # Evaluate class
        return self.evaluate()

    # =====================================
    # EVERYONE ANSWERED?
    # =====================================


    def everyone_answered(self):

        return self.engine.everyone_answered()

    # =====================================
    # EVALUATE
    # =====================================

    def evaluate(self):

        return self.teacher.evaluate_class(
            self.session
        )

    # =====================================
    # CONTINUE LESSON
    # =====================================

    def continue_lesson(self):

        self.session.clear_answers()

        self.session.waiting_for_answers = False

        self.session.active_question = None

        self.session.current_message = self.teacher.next_block(
            self.session
        )

        self.session.last_transition = datetime.utcnow()

        return self.session.current_message