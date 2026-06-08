import math
import random
import pygame
import sys

pygame.init()

##===============================GLOBAL VARIABLES==================================================#
screen_width = 1280
screen_height = 720
player_state = "idle"
clock = pygame.time.Clock()
screen = pygame.display.set_mode((screen_width, screen_height))
Game_state = "title_screen"
bullets = []


#=====sprites=====#
bullet_sprite = pygame.image.load(r"C:\Users\anike\Desktop\Projects\Mars game\Untitled_mars_game\assets\bullet_sprite.png")
bullet_sprite = pygame.transform.scale(bullet_sprite, (20, 20))

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
        #print(player.x, player.y, player_state)

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
        self.attack_cooldown = 0.0
           
    #draws player    
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

    def shoot(self):
        pass

class Bullet:
    speed = 550.0

    def __init__(self, x, y, vx, vy, radius=8, color=(255, 220, 0)):
        self.x = x
        self.y = y
        self.velocity_x = vx
        self.velocity_y = vy
        self.radius = radius
        self.color = color

    def update(self, dt):
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt

    def draw(self, screen):
        rect = pygame.Rect(int(self.x) - 3, int(self.y) - 3, 8, 8)
        pygame.draw.rect(screen, self.color, rect)

def fire_bullet():
    mouse_x, mouse_y = pygame.mouse.get_pos()
    dx = mouse_x - player.x
    dy = mouse_y - player.y
    dist = math.hypot(dx, dy)
    if dist == 0:
        return
    vx = dx / dist * Bullet.speed
    vy = dy / dist * Bullet.speed
    bullets.append(Bullet(player.x, player.y, vx, vy, radius=8, color=(255,220,0)))

def update(dt):
    """handles all updates to the game

    Args:
        dt : time since last frame
    """


    keys_pressed = pygame.key.get_pressed()
    player.movement(dt, keys_pressed)
    player.state_machine(keys_pressed)

    player.attack_cooldown = max(0.0, player.attack_cooldown - dt)

    if pygame.mouse.get_pressed()[0] and player.attack_cooldown <= 0.0:
        fire_bullet()
        player.attack_cooldown = 0.30

    for bullet in bullets:
        bullet.update(dt)
        bullet.draw(screen)

    bullets[:] = [bullet for bullet in bullets if 0 <= bullet.x <= screen_width and 0 <= bullet.y <= screen_height]
    player.draw(screen)








#================================================METHODS==================================================#

player= Player(screen_width // 2, 670, 20)


if __name__ == '__main__':
    run_game()