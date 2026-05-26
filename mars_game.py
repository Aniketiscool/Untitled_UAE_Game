import math
import random
import sys
import pygame

screen_width = 800
screen_height = 600

pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((screen_width, screen_height))


class Player:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
        self.movementspeed = 25.0    # pixels per second
        self.current_health = 100
        self.is_alive = True

    def main(self, screen):
        pygame.draw.circle(screen, (255, 0, 0), (self.x, self.y), self.radius)

    def movement(self, dt, keypressed):

        direction_x = 0
        direction_y = 0
        if keypressed[pygame.K_w] or keypressed[pygame.K_UP]:
            direction_y -= 1
        if keypressed[pygame.K_s] or keypressed[pygame.K_DOWN]:
            direction_y += 1
        if keypressed[pygame.K_a] or keypressed[pygame.K_LEFT]:
            direction_x -= 1
        if keypressed[pygame.K_d] or keypressed[pygame.K_RIGHT]:
            direction_x += 1

        dist = math.sqrt(direction_x ** 2 + direction_y ** 2)
        if dist > 0:
            direction_x /= dist
            direction_y /= dist    
            self.x += direction_x * self.movementspeed * dt
            self.y += direction_y * self.movementspeed * dt

        self.x = max(self.radius, min(screen_width - self.radius, self.x))
        self.y = max(self.radius, min(screen_height - self.radius, self.y))

player= Player(400, 300, 20)

def run_game():
    pygame.display.set_caption('Untitled_UAE_game')
    running = True
    dt = clock.tick(60) / 1000.0
    #reset()
    while running:
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        player.main(screen)
        player.movement(dt, pygame.key.get_pressed())
        pygame.display.flip()
    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    run_game()