import pygame


pygame.init()

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

class Display:
    def __init__(self, width: int, height: int, scale: int):
        self.width = width
        self.height = height
        self.scale = scale
        self.screen = pygame.display.set_mode((self.width * self.scale, self.height * self.scale))
        self.buffer = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.changed = False

    def get_width(self) -> int:
        return self.width

    def get_height(self) -> int:
        return self.height

    def set_pixel(self, x: int, y: int, value: int):
        if self.buffer[y][x] != value:
            self.changed = True
        self.buffer[y][x] = value

    def get_pixel(self, x: int, y: int) -> int:
        return self.buffer[y][x]

    def update(self):
        if not self.changed:
            return

        for j in range(self.height):
            for i in range(self.width):
                color = WHITE if self.buffer[j][i] else BLACK
                rect = (i * self.scale, j * self.scale, self.scale, self.scale)
                pygame.draw.rect(self.screen, color, rect)

        pygame.display.flip()
        self.changed = False

    def clear(self):
        self.changed = True
        
        for j in range(self.height):
            for i in range(self.width):
                self.buffer[j][i] = 0
        self.update()