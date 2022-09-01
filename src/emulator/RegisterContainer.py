from emulator.Register import Register


class RegisterContainer:
    def __init__(self, num_general_registers: int, pc_start: int, sp_start: int):
        self.general_purpose = [Register(0, 1 << 8) for _ in range(num_general_registers)]
        self.index = Register(0, 1 << 16)
        self.program_counter = Register(pc_start, 1 << 16)
        self.stack_pointer = Register(sp_start, 1 << 8)
        self.delay_timer = Register(0, 1 << 8)
        self.sound_timer = Register(0, 1 << 8)
