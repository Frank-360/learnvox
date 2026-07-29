import random
import string


def generate_room_code(length=6):
    """
    Generates a room code like:
    A7K9QX
    """

    alphabet = string.ascii_uppercase + string.digits

    return "".join(
        random.choice(alphabet)
        for _ in range(length)
    )