from pathlib import Path
from emulator.Chip8 import Chip8
from emulator.Rom import Rom

tetris = Rom(Path("roms", "TETRIS"))

chip8 = Chip8()
chip8.load_rom(tetris)
print(chip8.memory)
