import pygame


KEY_MAPPINGS = {
    pygame.K_g: 0x0,
    pygame.K_4: 0x1,
    pygame.K_5: 0x2,
    pygame.K_6: 0x3,
    pygame.K_7: 0x4,
    pygame.K_r: 0x5,
    pygame.K_t: 0x6,
    pygame.K_y: 0x7,
    pygame.K_u: 0x8,
    pygame.K_f: 0x9,
    pygame.K_h: 0xA,
    pygame.K_j: 0xB,
    pygame.K_v: 0xC,
    pygame.K_b: 0xD,
    pygame.K_n: 0xE,
    pygame.K_m: 0xF,
}


class KeyBoard:
    def __init__(self):
        pass

    def wait_key_pressed(self) -> int:
        while True:
            event = pygame.event.wait()
            if event.type == pygame.KEYDOWN:
                key_value = KEY_MAPPINGS.get(event.key)
                if key_value is not None:
                    return key_value