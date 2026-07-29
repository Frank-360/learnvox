from utils.study_room import StudyRoom
from utils.classroom_engine import ClassroomEngine
from utils.teacher_ai import TeacherAI
from utils.classroom_session import ClassroomSession
from utils.room_code import generate_room_code


def create_study_room(title, host_id, rooms, sessions):

    room_code = generate_room_code()

    room = StudyRoom(
        room_id=room_code,
        title=title,
        host_id=host_id
    )

    engine = ClassroomEngine(room)

    teacher = TeacherAI()

    class_session = ClassroomSession(
        room=room,
        teacher=teacher,
        classroom_engine=engine
    )

    rooms[room_code] = engine
    sessions[room_code] = class_session

    return room_code