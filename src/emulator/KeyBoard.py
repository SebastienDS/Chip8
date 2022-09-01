from typing import Dict
import pygame


KEY_MAPPINGS = {
    pygame.K_x: 0x0,
    pygame.K_1: 0x1,
    pygame.K_2: 0x2,
    pygame.K_3: 0x3,
    pygame.K_a: 0x4,
    pygame.K_z: 0x5,
    pygame.K_e: 0x6,
    pygame.K_q: 0x7,
    pygame.K_s: 0x8,
    pygame.K_d: 0x9,
    pygame.K_w: 0xA,
    pygame.K_c: 0xB,
    pygame.K_4: 0xC,
    pygame.K_r: 0xD,
    pygame.K_f: 0xE,
    pygame.K_v: 0xF,
}

def get_key_from_value(d: Dict, val: int) -> int:
    keys = [k for k, v in d.items() if v == val]
    return keys[0]

class KeyBoard:
    def __init__(self):
        pass

    def wait_key_pressed(self) -> int:
        while True:
            event = pygame.event.wait()
            if event.type == pygame.QUIT:
                exit()
            elif event.type == pygame.KEYDOWN:
                key_value = KEY_MAPPINGS.get(event.key)
                if key_value is not None:
                    return key_value

    def key_pressed(self, key: int) -> bool:
        keys = pygame.key.get_pressed()
        mapped_key = get_key_from_value(KEY_MAPPINGS, key)
        return keys[mapped_key]