from random import randint
from typing import Callable
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

SCREEN_WIDTH = 64
SCREEN_HEIGHT = 32


class Chip8:
    def __init__(self):
        self.memory = Memory(MAX_MEMORY)
        self.keyboard = KeyBoard()
        self.display = Display(SCREEN_WIDTH, SCREEN_HEIGHT, 10)
        self.registers = {
            RegisterType.GENERAL_PURPOSE: [Register(0) for _ in range(NUM_REGISTERS)],
            RegisterType.INDEX: Register(0),
            RegisterType.STACK_POINTER: Register(STACK_POINTER_START),
            RegisterType.PROGRAM_COUNTER: Register(PROGRAM_COUNTER_START),
            RegisterType.DELAY_TIMER: Register(0),
            RegisterType.SOUND_TIMER: Register(0)
        }

        self.load_fontset()

        self.operation_lookup = {
            0x0: self.clear_return,                  # 0nnn - subfunctions
            0x1: self.jump_to_address,               # 1nnn
            0x2: self.call_subroutine,               # 2nnn
            0x3: self.skip_if_reg_equal_val,         # 3xnn
            0x4: self.skip_if_reg_not_equal_val,     # 4xnn
            0x5: self.skip_if_reg_equal_reg,         # 5xy0
            0x6: self.move_value_to_reg,             # 6xnn
            0x7: self.add_value_to_reg,              # 7xnn
            0x8: self.execute_logical_instruction,   # 8nnn - subfunctions
            0x9: self.skip_if_reg_not_equal_reg,     # 9xy0
            0xA: self.load_index_reg_with_value,     # Annn
            0xB: self.jump_to_index_plus_value,      # Bnnn
            0xC: self.generate_random_number,        # Cxnn
            0xD: self.draw_sprite,                   # Dxyn
            0xE: self.keyboard_routines,             # Ennn - subfunctions
            0xF: self.misc_routines,                 # Fnnn - subfunctions
        }

        self.logical_operation_lookup = {
            0x0: self.move_reg_into_reg,             # 8xy0
            0x1: self.logical_or,                    # 8xy1
            0x2: self.logical_and,                   # 8xy2
            0x3: self.exclusive_or,                  # 8xy3
            0x4: self.add_reg_to_reg,                # 8xy4
            0x5: self.subtract_reg_from_reg,         # 8xy5
            0x6: self.right_shift_reg,               # 8xy6
            0x7: self.subtract_reg_from_reg1,        # 8xy7
            0xE: self.left_shift_reg,                # 8xyE
        }

        self.misc_operation_lookup = {
            0x07: self.move_delay_timer_into_reg,    # Fx07
            0x0A: self.wait_for_keypress,            # Fx0A
            0x15: self.move_reg_into_delay_timer,    # Fx15
            0x18: self.move_reg_into_sound_timer,    # Fx18
            0x1E: self.add_reg_into_index,           # Fx1E
            0x29: self.load_index_with_reg_sprite,   # Fx29
            0x33: self.store_bcd_in_memory,          # Fx33
            0x55: self.store_regs_in_memory,         # Fx55
            0x65: self.read_regs_from_memory,        # Fx65
        }

    def load_rom(self, rom: Rom):
        content = rom.load_data()
        for i, data in enumerate(content):
            self.memory.set(PROGRAM_COUNTER_START + i, data)
    
    def step(self):
        opcode = self.fetch_opcode()
        opcode_action = self.decode_opcode(opcode)
        self.execute_action(opcode_action, opcode)
        self.update_timers()
        self.next_instruction()

    def fetch_opcode(self) -> int:
        counter = self.registers[RegisterType.PROGRAM_COUNTER].get()
        return self.memory.get(counter) << 8 | self.memory.get(counter + 1)

    def decode_opcode(self, opcode: int) -> Callable[[int], None]:
        operation = (opcode & 0xF000) >> 12
        return self.operation_lookup[operation]

    def execute_action(opcode_action: Callable[[int], None], opcode):
        opcode_action(opcode)

    def update_timers(self):
        self.update_timer(self.registers[RegisterType.DELAY_TIMER])
        self.update_timer(self.registers[RegisterType.SOUND_TIMER])

    def update_timer(self, register: Register):
        if register.get() > 0:
            register.decrement()
        
    def next_instruction(self):
        self.registers[RegisterType.PROGRAM_COUNTER].add(2)

    def load_fontset(self):
        for i, font_value in enumerate(fontset):
            self.memory.set(i, font_value)

    def clear_return(self, opcode: int):
        operation = opcode & 0x00FF

        match operation:
            case 0x00E0:
                self.display.clear()
            case 0x00EE:
                self.return_from_subroutine()

    def return_from_subroutine(self, opcode: int):
        stack_pointer_register = self.registers[RegisterType.STACK_POINTER]
        program_counter_register = self.registers[RegisterType.PROGRAM_COUNTER]
        stack_pointer_register.add(-2)

        address = self.memory.get(stack_pointer_register) << 8 | self.memory.get(stack_pointer_register + 1)
        program_counter_register.set(address)

    def jump_to_address(self, opcode: int):
        address = opcode & 0x0FFF
        self.registers[RegisterType.PROGRAM_COUNTER].set(address)

    def call_subroutine(self, opcode: int):
        stack_pointer_register = self.registers[RegisterType.STACK_POINTER]
        program_counter_register = self.registers[RegisterType.PROGRAM_COUNTER]
        address = opcode & 0x0FFF

        self.memory.set(stack_pointer_register.get(), program_counter_register.get() & 0x00FF)
        self.memory.set(stack_pointer_register.get() + 1, (program_counter_register.get() & 0xFF00) >> 8)

        stack_pointer_register.add(2)
        program_counter_register.set(address)

    def skip_if_reg_equal_val(self, opcode: int):
        register = (opcode & 0x0F00) >> 8
        value = opcode & 0x00FF
        
        if self.registers[RegisterType.GENERAL_PURPOSE][register].get() == value:
            self.next_instruction()

    def skip_if_reg_not_equal_val(self, opcode: int):
        register = (opcode & 0x0F00) >> 8
        value = opcode & 0x00FF
        
        if self.registers[RegisterType.GENERAL_PURPOSE][register].get() != value:
            self.next_instruction()

    def skip_if_reg_equal_reg(self, opcode: int):
        general_registers = self.registers[RegisterType.GENERAL_PURPOSE]
        register1 = (opcode & 0x0F00) >> 8
        register2 = (opcode & 0x00F0) >> 4

        if general_registers[register1].get() == general_registers[register2].get():
            self.next_instruction()

    def move_value_to_reg(self, opcode: int):
        register = (opcode & 0x0F00) >> 8
        value = opcode & 0x00FF
        self.registers[RegisterType.GENERAL_PURPOSE][register].set(value)

    def add_value_to_reg(self, opcode: int):
        register = (opcode & 0x0F00) >> 8
        value = opcode & 0x00FF
        self.registers[RegisterType.GENERAL_PURPOSE][register].add(value)

    def execute_logical_instruction(self, opcode: int):
        operation = opcode & 0x000F
        executable_operation = self.logical_operation_lookup[operation]
        executable_operation(opcode)

    def move_reg_into_reg(self, opcode: int):
        general_registers = self.registers[RegisterType.GENERAL_PURPOSE]
        source = (opcode & 0x0F00) >> 8
        target = (opcode & 0x00F0) >> 4

        general_registers[source].set(general_registers[target].get())
    
    def logical_or(self, opcode: int):
        general_registers = self.registers[RegisterType.GENERAL_PURPOSE]
        source = (opcode & 0x0F00) >> 8
        target = (opcode & 0x00F0) >> 4

        result = general_registers[source].get() | general_registers[target].get()
        general_registers[source].set(result)

    def logical_and(self, opcode: int):
        general_registers = self.registers[RegisterType.GENERAL_PURPOSE]
        source = (opcode & 0x0F00) >> 8
        target = (opcode & 0x00F0) >> 4

        result = general_registers[source].get() & general_registers[target].get()
        general_registers[source].set(result)

    def exclusive_or(self, opcode: int):
        general_registers = self.registers[RegisterType.GENERAL_PURPOSE]
        source = (opcode & 0x0F00) >> 8
        target = (opcode & 0x00F0) >> 4

        result = general_registers[source].get() ^ general_registers[target].get()
        general_registers[source].set(result)

    def add_reg_to_reg(self, opcode: int):
        general_registers = self.registers[RegisterType.GENERAL_PURPOSE]
        source = (opcode & 0x0F00) >> 8
        target = (opcode & 0x00F0) >> 4

        result = general_registers[source].get() + general_registers[target].get()
        general_registers[source].set(result)
        general_registers[target].set(int(general_registers[source].get_overflow_flag())) 

    def subtract_reg_from_reg(self, opcode: int):
        general_registers = self.registers[RegisterType.GENERAL_PURPOSE]
        source = (opcode & 0x0F00) >> 8
        target = (opcode & 0x00F0) >> 4

        result = general_registers[source].get() - general_registers[target].get()
        general_registers[source].set(result)
        general_registers[0xF].set(int(general_registers[source].get_borrow_flag())) 

    def right_shift_reg(self, opcode: int):
        general_registers = self.registers[RegisterType.GENERAL_PURPOSE]
        source = (opcode & 0x0F00) >> 8

        least_significan_bit = general_registers[source].get() & 0x1
        general_registers[0xF].set(least_significan_bit) 
        general_registers[source].set(general_registers[source].get() >> 1)

    def subtract_reg_from_reg1(self, opcode: int):
        general_registers = self.registers[RegisterType.GENERAL_PURPOSE]
        source = (opcode & 0x0F00) >> 8
        target = (opcode & 0x00F0) >> 4

        result = general_registers[target].get() - general_registers[source].get()
        general_registers[source].set(result)
        general_registers[0xF].set(general_registers[source].get_borrow_flag()) 

    def left_shift_reg(self, opcode: int):
        general_registers = self.registers[RegisterType.GENERAL_PURPOSE]
        source = (opcode & 0x0F00) >> 8

        most_significant_bit = (general_registers[source].get() & 0x80) >> 8
        general_registers[0xF].set(most_significant_bit)
        general_registers[source].set(general_registers[source].get() << 1)

    def skip_if_reg_not_equal_reg(self, opcode: int):
        general_registers = self.registers[RegisterType.GENERAL_PURPOSE]
        register1 = (opcode & 0x0F00) >> 8
        register2 = (opcode & 0x00F0) >> 4

        if general_registers[register1].get() != general_registers[register2].get():
            self.next_instruction()

    def load_index_reg_with_value(self, opcode: int):
        value = opcode & 0x0FFF
        self.registers[RegisterType.INDEX].set(value)

    def jump_to_index_plus_value(self, opcode: int):
        address = opcode & 0x0FFF
        # destination = self.registers[RegisterType.INDEX].get() + address 
        destination = self.registers[RegisterType.GENERAL_PURPOSE][0x0].get() + address 
        self.registers[RegisterType.PROGRAM_COUNTER].set(destination)

    def generate_random_number(self, opcode: int):
        register = (opcode & 0x0F00) >> 8
        value = opcode & 0x00FF
        result = randint(0, 255) & value

        self.registers[RegisterType.GENERAL_PURPOSE][register].set(result)

    def draw_sprite(self, opcode: int):
        general_registers = self.registers[RegisterType.GENERAL_PURPOSE]

        register_x = (opcode & 0x0F00) >> 8
        register_y = (opcode & 0x00F0) >> 4
        n = opcode & 0x000F

        start_x = general_registers[register_x].get()
        start_y = general_registers[register_y].get()

        general_registers[0xF].set(0)

        for j in range(n):
            y = (start_y + j) % self.display.get_height()
            color_byte = self.memory.get(self.registers[RegisterType.INDEX].get() + j)

            for i in range(8):
                x = (start_x + i) % self.display.get_width()
                color = (color_byte >> (7 - i)) & 1
                pixel = self.display.get_pixel(x, y)

                flipped_pixel = general_registers[0xF].get() | (color & pixel)
                general_registers[0xF].set(flipped_pixel)

                self.display.set_pixel(x, y, pixel ^ color)

        self.display.update()

    def keyboard_routines(self, opcode: int):
        operation = opcode & 0x00FF
        register = (opcode & 0x0F00) >> 8

        key = self.registers[RegisterType.GENERAL_PURPOSE][register]
        
        match operation:
            case 0x9E:
                if self.keyboard.key_pressed(key):
                    self.next_instruction()
            case 0xA1:
                if not self.keyboard.key_pressed(key):
                    self.next_instruction()
        
    def misc_routines(self, opcode: int):
        operation = opcode & 0x00FF
        executable_operation = self.misc_operation_lookup[operation]
        executable_operation(opcode)

    def move_delay_timer_into_reg(self, opcode: int):
        register = (opcode & 0x0F00) >> 8
        delay_timer = self.registers[RegisterType.DELAY_TIMER].get()
        self.registers[RegisterType.GENERAL_PURPOSE][register].set(delay_timer)

    def wait_for_keypress(self, opcode: int):
        register = (opcode & 0x0F00) >> 8
        key_value = self.keyboard.wait_key_pressed()
        self.registers[RegisterType.GENERAL_PURPOSE][register].set(key_value)

    def move_reg_into_delay_timer(self, opcode: int):
        register = (opcode & 0x0F00) >> 8
        delay_timer = self.registers[RegisterType.GENERAL_PURPOSE][register].get()
        self.registers[RegisterType.DELAY_TIMER].set(delay_timer)

    def move_reg_into_sound_timer(self, opcode: int):
        register = (opcode & 0x0F00) >> 8
        sound_timer = self.registers[RegisterType.GENERAL_PURPOSE][register].get()
        self.registers[RegisterType.SOUND_TIMER].set(sound_timer)

    def add_reg_into_index(self, opcode: int):
        register = (opcode & 0x0F00) >> 8
        value = self.registers[RegisterType.GENERAL_PURPOSE][register].get()
        self.registers[RegisterType.INDEX].add(value)

    def load_index_with_reg_sprite(self, opcode: int):
        register = (opcode & 0x0F00) >> 8
        value = self.registers[RegisterType.GENERAL_PURPOSE][register].get()
        self.registers[RegisterType.INDEX].add(value * 5)

    def store_bcd_in_memory(self, opcode: int):
        register = (opcode & 0x0F00) >> 8
        index = self.registers[RegisterType.INDEX].get()
        value = self.registers[RegisterType.GENERAL_PURPOSE][register].get()
        bcd_value = "{:03d}".format(value)

        self.memory.set(index, int(bcd_value[0]))
        self.memory.set(index + 1, int(bcd_value[1]))
        self.memory.set(index + 2, int(bcd_value[2]))

    def store_regs_in_memory(self, opcode: int):
        last_register = (opcode & 0x0F00) >> 8
        index = self.registers[RegisterType.INDEX].get()

        for i in range(last_register + 1):
            content = self.registers[RegisterType.GENERAL_PURPOSE][i]
            self.memory.set(index + i, content)

    def read_regs_from_memory(self, opcode: int):
        last_register = (opcode & 0x0F00) >> 8
        index = self.registers[RegisterType.INDEX].get()

        for i in range(last_register + 1):
            register = self.registers[RegisterType.GENERAL_PURPOSE][i]
            content = self.memory.get(index + i)
            register.set(content)