import math
import random
import pygame
import sys

screen_width = 1280
screen_height = 720
player_state = "idle"
pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((screen_width, screen_height))
Game_state = "title_screen"

def run_game():
    pygame.display.set_caption('Untitled_UAE_game')
    while True:
        dt = clock.tick(60) / 1000.0
        screen.fill((0, 0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        update(dt)


        pygame.display.flip()
        print(player.x, player.y, player_state)

#================================================CLASSES==================================================#

class Player:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
        self.movementspeed = 300.0    # pixels per second
        self.current_health = 100
        self.damage = 20
        self.is_alive = True
        self.attack_cooldown = 0.5
           
    #draws player: REPLACE WITH SPRITE LATER       
    def draw(self, screen):
        pygame.draw.circle(screen, (126, 0, 126), (self.x, self.y), self.radius)

    
    def movement(self, dt, keypressed):
        """handles all player movement, including diagonal movement and keeping the player within the screen

        Args:
            dt (int): time since last frame
            keypressed (_type_): key that is currently being pressed
        """
        X_direction_to_move = 0
        Y_direction_to_move = 0 
        if keypressed[pygame.K_w] or keypressed[pygame.K_UP]:
            Y_direction_to_move -= 1
        if keypressed[pygame.K_s] or keypressed[pygame.K_DOWN]:
            Y_direction_to_move += 1
        if keypressed[pygame.K_a] or keypressed[pygame.K_LEFT]:
            X_direction_to_move -= 1
        if keypressed[pygame.K_d] or keypressed[pygame.K_RIGHT]:
            X_direction_to_move += 1

        #uses hypotenuse to stabilize diagonal movement
        dist= math.hypot(X_direction_to_move, Y_direction_to_move)
        if dist != 0:
            self.x += X_direction_to_move * self.movementspeed * dt
            self.y += Y_direction_to_move * self.movementspeed * dt

        #stops player form leaving the screen
        self.x = max(self.radius, min(screen_width - self.radius, self.x))
        self.y = max(self.radius, min(screen_height - self.radius, self.y))

    def state_machine(self,keypressed):
        """manages player state based on actions for sprites

        Args:
            keypressed : key that is currently being pressed
        """
        global player_state
        if keypressed[pygame.K_w] or keypressed[pygame.K_UP]:
            player_state = "moving_up"
        if keypressed[pygame.K_s] or keypressed[pygame.K_DOWN]:
            player_state = "moving_down"
        if keypressed[pygame.K_a] or keypressed[pygame.K_LEFT]:
            player_state = "moving_left"
        if keypressed[pygame.K_d] or keypressed[pygame.K_RIGHT]:
            player_state = "moving_right"
        if not (keypressed[pygame.K_w] or keypressed[pygame.K_UP] or keypressed[pygame.K_s] or keypressed[pygame.K_DOWN] or keypressed[pygame.K_a] or keypressed[pygame.K_LEFT] or keypressed[pygame.K_d] or keypressed[pygame.K_RIGHT]):
            player_state = "idle"
        if keypressed[pygame.K_SPACE] or keypressed[pygame.mouse.get_pressed()[0]]:
            player_state = "shooting"

class Bullet:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction
        self.speed = 500.0  # pixels per second
















#================================================METHODS==================================================#

def update(dt):
    #Activates the player methods        
        player.draw(screen)
        player.movement(dt, pygame.key.get_pressed())
        player.state_machine(pygame.key.get_pressed())


player= Player(screen_width // 2, 670, 20)


if __name__ == '__main__':
    run_game()