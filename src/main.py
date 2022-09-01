import sys
import logging
import pygame
from pathlib import Path
from emulator.Chip8 import Chip8
from emulator.Rom import Rom

pygame.init()
logging.basicConfig(level=logging.WARNING)

TIMER_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(TIMER_EVENT, 15)


rom = Rom(Path("roms", sys.argv[1]))

chip8 = Chip8()
chip8.load_rom(rom) 

while True:
    chip8.step()

    for event in pygame.event.get():
        if event.type in { pygame.QUIT, pygame.K_ESCAPE }:
            exit()
        elif event.type == TIMER_EVENT:
            chip8.update_timers()
    pygame.time.wait(1)