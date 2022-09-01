from enum import Enum


class RegisterType(Enum):
    GENERAL_PURPOSE = 1,
    INDEX = 2,
    STACK_POINTER = 3,
    PROGRAM_COUNTER = 4,
    DELAY_TIMER = 5,
    SOUND_TIMER = 6


class Register:
    def __init__(self, content: int, max_values):
        self.content = content
        self.max_values = max_values
        self.overflow_flag = False
        self.borrow_flag = False

    def __str__(self) -> str:
        return f"Register({self.content})"

    def set(self, value: int):
        self.content = value
        self.resize_register()

    def get(self) -> int:
        return self.content

    def increment(self):
        self.add(1)

    def decrement(self):
        self.add(-1)

    def add(self, value: int):
        self.content += value
        self.resize_register()

    def resize_register(self):
        self.overflow_flag = False
        self.borrow_flag = False

        if self.content < 0:
            self.perform_borrow()
        else:
            self.perform_overflow()

    def perform_overflow(self):
        if self.content >= self.max_values:
            self.content -= self.max_values
            self.overflow_flag = True

    def perform_borrow(self):
        if self.content < 0:
            self.content += self.max_values
            self.borrow_flag = True

    def get_overflow_flag(self):
        return self.overflow_flag
    
    def get_borrow_flag(self):
        return self.borrow_flag