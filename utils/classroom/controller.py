from utils.classroom.state import ClassroomState


class ClassroomController:

    def __init__(self, session):

        self.session = session

    @property
    def state(self):

        return self.session.classroom_state

    def set_state(self, state: ClassroomState):

        self.session.classroom_state = state