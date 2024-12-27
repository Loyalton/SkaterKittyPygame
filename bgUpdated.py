import pygame as pg
import sys

pg.init()

width, height = 1280, 720
screen = pg.display.set_mode((width, height), pg.RESIZABLE)
clock = pg.time.Clock()

class World:
    def __init__(self, image_path, speed):
        self.background = pg.image.load(image_path).convert_alpha()
        self.bg_width = self.background.get_width()
        self.bg_height = self.background.get_height()
        self.bg_start_pos_x = 0
        self.speed = speed

    def update(self, dt):
        self.bg_start_pos_x = (self.bg_start_pos_x - self.speed * dt) % -self.bg_width

    def draw(self):
        screen.blit(self.background, (self.bg_start_pos_x, 0))
        screen.blit(self.background, (self.bg_start_pos_x + self.bg_width, 0))

# Instantiate background layers

bg_buildings = World("graphics/bgBuildings.png", 100)

layers = [bg_buildings]

running = True
while running:
    dt = clock.tick(60) / 1000  # Time delta in seconds

    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()

    screen.fill((0, 0, 0))  # Clear the screen

    for layer in layers:
        layer.update(dt)
        layer.draw()

    pg.display.flip()
