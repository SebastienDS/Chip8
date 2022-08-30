from emulator.Display import Display
from emulator.Memory import Memory
from emulator.Rom import Rom
from emulator.Register import Register, RegisterType
from emulator.KeyBoard import KeyBoard
from fontset import fontset

MAX_MEMORY = 4096
NUM_REGISTERS = 16
STACK_POINTER_START = 0x52
PROGRAM_COUNTER_START = 0x200


class Chip8:
    def __init__(self):
        self.memory = Memory(MAX_MEMORY)
        self.registers = {
            RegisterType.GENERAL_PURPOSE: [Register(0) for _ in range(NUM_REGISTERS)],
            RegisterType.INDEX: Register(0),
            RegisterType.STACK_POINTER: Register(STACK_POINTER_START),
            RegisterType.PROGRAM_COUNTER: Register(PROGRAM_COUNTER_START),
            RegisterType.DELAY_TIMER: Register(0),
            RegisterType.SOUND_TIMER: Register(0)
        }
        self.keyboard = KeyBoard()
        self.display = Display()

        self._load_fontset()

    def load_rom(self, rom: Rom):
        content = rom.load_data()
        for i, data in enumerate(content):
            self.memory.set(PROGRAM_COUNTER_START + i, data)

    def _load_fontset(self):
        for i, font_value in enumerate(fontset):
            self.memory.set(i, font_value)

