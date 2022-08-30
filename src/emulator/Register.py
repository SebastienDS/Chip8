from enum import Enum


class RegisterType(Enum):
    GENERAL_PURPOSE = 1,
    INDEX = 2,
    STACK_POINTER = 3,
    PROGRAM_COUNTER = 4,
    DELAY_TIMER = 5,
    SOUND_TIMER = 6


class Register:
    def __init__(self, content: int):
        self.content = content

    def __str__(self) -> str:
        return f"Register({self.content})"

    def set(self, value: int):
        self.content = value

    def get(self) -> int:
        return self.content