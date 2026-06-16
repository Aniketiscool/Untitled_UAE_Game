import math
import random
import pygame
import sys

pygame.init()

font = pygame.font.SysFont(None, 24)
title_font = pygame.font.SysFont(None, 167)
ui_font = pygame.font.SysFont(None, 28)
small_font = pygame.font.SysFont(None, 20)

##===============================GLOBAL VARIABLES==================================================#
screen_width = 1280
screen_height = 720
clock = pygame.time.Clock()
screen = pygame.display.set_mode((screen_width, screen_height))
Game_state = "title_screen"
player_state = "idle"
bullets = []
sword_swings = []
enemies = []
powerups = []
boulders = []
shockwaves = []
kill_count = 0
wave_number = 0
wave_target = 0
enemies_to_spawn = 0
wave_spawn_timer = 0.0
wave_message = ""
wave_message_time = 0.0
max_waves = 50


#=====sprites=====#

def run_game():
    pygame.display.set_caption('Untitled_UAE_game')
    while True:
        dt = clock.tick(60) / 1000.0
        screen.fill(pygame.Color("#D8AD64"))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_k:
                    player.is_alive = False

        update(dt)

        pygame.display.flip()

#================================================CLASSES==================================================#

class Player:
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = radius
        self.movementspeed = 300.0    # pixels per second
        self.current_health = 100
        self.max_health = 100
        self.max_ammo = 30
        self.ammo = 15

        self.is_alive= True
        self.attack_cooldown = 0.0
        self.weapon = "sword"
        self.weapon_swap_cooldown = 0.0
        self.sword_cooldown = 0.35
        self.damage_multiplier = 1.0
        self.bloodthirst_timer = 0.0
        self.bloodthirst_active = False
        self.bloodthirst_uses = 0
        self.Iframe_timer = 0.0
        self.ability_slots = ["Bloodthirst", "", ""]
           
    #draws player    
    def draw(self, screen):
        pygame.draw.circle(screen, (76, 20, 205), (self.x, self.y), self.radius)

    
    def movement(self, dt, keypressed):
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
        global player_state
        """manages player state based on actions for sprites

        Args:
            keypressed : key that is currently being pressed
        """
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
        if keypressed[pygame.K_SPACE] or pygame.mouse.get_pressed()[0]:
            player_state = "attacking"
        if keypressed[pygame.K_g] and self.weapon_swap_cooldown <= 0.0:
            if self.weapon == "sword":
                self.weapon = "gun"
            else:
                self.weapon = "sword"
            self.weapon_swap_cooldown = 0.67

class Bullet:
    speed = 550.0

    def __init__(self, x, y, vx, vy,):
        self.x = x
        self.y = y
        self.velocity_x = vx
        self.velocity_y = vy
        self.radius = 8
        self.color = (255, 220, 0)
        self.damage = 20

    def update(self, dt):
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt

    def draw(self, screen):
        rect = pygame.Rect(int(self.x) - 3, int(self.y) - 3, 8, 8)
        pygame.draw.rect(screen, self.color, rect)

class Boulder:
    speed = 280.0

    def __init__(self, x, y, vx, vy):
        self.x = x
        self.y = y
        self.velocity_x = vx
        self.velocity_y = vy
        self.radius = 14
        self.color = (90, 55, 15)
        self.damage = 20
        self.time_alive = 0.0
        self.exploded = False

    def update(self, dt):
        self.time_alive += dt
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)

class Shockwave:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.age = 0.0
        self.duration = 0.4
        self.max_radius = 120
        self.damage = 30
        self.hit_applied = False

    def update(self, dt):
        self.age += dt

    def draw(self, screen):
        progress = min(1.0, self.age / self.duration)
        radius = int(self.max_radius * progress)
        if radius > 0:
            alpha_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(alpha_surface, (255, 40, 40, 100), (radius, radius), radius)
            screen.blit(alpha_surface, (self.x - radius, self.y - radius))

    def is_expired(self):
        return self.age >= self.duration

class Powerup:
    def __init__(self, x, y, power_type):
        self.x = x
        self.y = y
        self.radius = 12
        self.type = power_type
        self.color = (0, 180, 255) if power_type == "ammo" else (0, 255, 120)

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        label = "A" if self.type == "ammo" else "+"
        label_text = font.render(label, True, (0, 0, 0))
        screen.blit(label_text, (int(self.x - label_text.get_width() / 2), int(self.y - label_text.get_height() / 2)))

    def apply(self, player):
        if self.type == "ammo":
            player.ammo = player.max_ammo
        elif self.type == "heal":
            player.current_health = player.max_health

    def collides_with(self, player):
        return math.hypot(player.x - self.x, player.y - self.y) <= self.radius + player.radius

class Enemy:
    def __init__(self, x, y, enemy_type="normal"):
        self.x = x
        self.y = y
        self.enemy_type = enemy_type
        self.attack_cooldown = 0.0

        if self.enemy_type == "tanker":
            self.radius = 24
            self.max_health = 200
            self.current_health = 200
            self.speed = 80.0
            self.color = (140, 20, 20)
            self.attack_damage = 20
            self.attack_delay = 1.2
            self.label = "Tank"
            self.boulder_cooldown = 0.0
            self.boulder_preparing = False
            self.boulder_prep_timer = 0.0
        elif self.enemy_type == "runner":
            self.radius = 14
            self.max_health = 50
            self.current_health = 50
            self.speed = 220.0
            self.color = (255, 130, 0)
            self.attack_damage = 8
            self.attack_delay = 0.7
            self.label = "Runner"
            self.boulder_cooldown = 0.0
            self.boulder_preparing = False
            self.boulder_prep_timer = 0.0
        else:
            self.radius = 18
            self.max_health = 80
            self.current_health = 80
            self.speed = 130.0
            self.color = (200, 30, 30)
            self.attack_damage = 10
            self.attack_delay = 1.0
            self.label = "Normal"
            self.boulder_cooldown = 0.0
            self.boulder_preparing = False
            self.boulder_prep_timer = 0.0

    def update(self, dt, enemies_list):
        self.attack_cooldown = max(0.0, self.attack_cooldown - dt)
        dx = player.x - self.x
        dy = player.y - self.y
        dist = math.hypot(dx, dy)
        
        if self.enemy_type == "tanker":
            self.boulder_cooldown = max(0.0, self.boulder_cooldown - dt)
            if self.boulder_preparing:
                self.boulder_prep_timer -= dt
                if self.boulder_prep_timer <= 0:
                    self.throw_boulder(dx, dy, dist)
                    self.boulder_preparing = False
                    self.boulder_cooldown = 8.0
            elif self.boulder_cooldown <= 0 and dist > self.radius + player.radius + 20 and dist < 350:
                self.boulder_preparing = True
                self.boulder_prep_timer = random.uniform(2.0, 3.0)
            if self.boulder_preparing:
                return
        
        if dist > 0:
            self.x += dx / dist * self.speed * dt
            self.y += dy / dist * self.speed * dt

        for enemy in enemies:
            if enemy is self:
                continue
            dx2 = self.x - enemy.x
            dy2 = self.y - enemy.y
            dist2 = math.hypot(dx2, dy2)
            min_dist = self.radius + enemy.radius + 2
            if dist2 > 0 and dist2 < min_dist:
                overlap = min_dist - dist2
                push_x = dx2 / dist2 * overlap * 0.5
                push_y = dy2 / dist2 * overlap * 0.5
                self.x += push_x
                self.y += push_y
                enemy.x -= push_x
                enemy.y -= push_y

        if self.attack_cooldown <= 0.0 and dist <= self.radius + player.radius + 4:
            if player.Iframe_timer <= 0.0:
                player.current_health = max(0, player.current_health - self.attack_damage)
                player.Iframe_timer = 0.8
            self.attack_cooldown = self.attack_delay

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
        health_text = font.render(str(self.current_health), True, (255, 255, 255))
        screen.blit(health_text, (int(self.x - health_text.get_width() / 2), int(self.y - self.radius - health_text.get_height() - 2)))
        label_text = font.render(self.label, True, (255, 255, 255))
        screen.blit(label_text, (int(self.x - label_text.get_width() / 2), int(self.y - label_text.get_height() / 2)))

    def throw_boulder(self, dx, dy, dist):
        if dist == 0:
            return
        vx = dx / dist * Boulder.speed
        vy = dy / dist * Boulder.speed
        boulders.append(Boulder(self.x, self.y, vx, vy))

    def is_dead(self):
        return self.current_health <= 0


def try_spawn_powerup(enemy):
    chance = {"tanker": 0.1, "normal": 0.05, "runner": 0.01}.get(enemy.enemy_type, 0.0)
    if random.random() < chance:
        power_type = random.choices(["ammo", "heal"], weights=[65, 35])[0]
        powerups.append(Powerup(enemy.x, enemy.y, power_type))


def handle_enemy_kill():
    global kill_count
    kill_count += 1
    if player.bloodthirst_active:
        player.bloodthirst_timer += 0.5


class Sword:
    remaining_hitbox_duration = 0.20
    range_distance = 100
    arc_angle = math.pi * 0.8
    segments = 12
    slash_cooldown = 0.35

    def __init__(self, player, dx, dy):
        self.player = player
        self.origin_x = player.x
        self.origin_y = player.y
        dist = math.hypot(dx, dy)
        if dist > 0:
            dx /= dist
            dy /= dist
            self.angle = math.atan2(dy, dx)
        else:
            self.angle = 0.0
        self.damage = 15
        self.color = (255, 220, 0)
        self.hit_applied = False

    def update(self, dt):
        self.remaining_hitbox_duration -= dt
        self.origin_x = self.player.x
        self.origin_y = self.player.y

    def hit_enemies(self, enemies_list):
        global kill_count
        if self.hit_applied:
            return
        half_angle = self.arc_angle / 2
        self.origin_x = self.player.x
        self.origin_y = self.player.y
        for enemy in enemies_list[:]:
            dx = enemy.x - self.origin_x
            dy = enemy.y - self.origin_y
            dist = math.hypot(dx, dy)
            if dist > self.range_distance + enemy.radius:
                continue
            enemy_angle = math.atan2(dy, dx)
            diff = math.atan2(math.sin(enemy_angle - self.angle), math.cos(enemy_angle - self.angle))
            if abs(diff) <= half_angle:
                damage = int(self.damage * self.player.damage_multiplier)
                enemy.current_health -= damage
                self.hit_applied = True
                if enemy.is_dead():
                    try_spawn_powerup(enemy)
                    enemies_list.remove(enemy)
                    handle_enemy_kill()

    def draw(self, screen):
        self.origin_x = self.player.x
        self.origin_y = self.player.y
        points = [(int(self.origin_x), int(self.origin_y))]
        half_angle = self.arc_angle / 2
        for i in range(self.segments + 1):
            step = -half_angle + (self.arc_angle * i / self.segments)
            angle = self.angle + step
            px = self.origin_x + math.cos(angle) * self.range_distance
            py = self.origin_y + math.sin(angle) * self.range_distance
            points.append((int(px), int(py)))
        pygame.draw.polygon(screen, self.color, points)

    def is_active(self):
        return self.remaining_hitbox_duration > 0

def fire_bullet():
    if player.ammo <= 0:
        return
    player.ammo -= 1
    mouse_x, mouse_y = pygame.mouse.get_pos()
    dx = mouse_x - player.x
    dy = mouse_y - player.y
    dist = math.hypot(dx, dy)
    if dist == 0:
        return
    vx = dx / dist * Bullet.speed
    vy = dy / dist * Bullet.speed
    damage = int(20 * player.damage_multiplier)
    bullet = Bullet(player.x, player.y, vx, vy)
    bullet.damage = damage
    bullets.append(bullet)

def swing_sword():
    mouse_x, mouse_y = pygame.mouse.get_pos()
    dx = mouse_x - player.x
    dy = mouse_y - player.y
    sword_swings.append(Sword(player, dx, dy))


def spawn_wave_enemy(enemy_type=None):
    edge = random.choice(["top", "bottom", "left", "right"])
    if edge == "top":
        x = random.randint(40, screen_width - 40)
        y = random.randint(40, screen_height // 3)
    elif edge == "bottom":
        x = random.randint(40, screen_width - 40)
        y = random.randint(screen_height * 2 // 3, screen_height - 40)
    elif edge == "left":
        x = random.randint(40, screen_width // 3)
        y = random.randint(40, screen_height - 40)
    else:
        x = random.randint(screen_width * 2 // 3, screen_width - 40)
        y = random.randint(40, screen_height - 40)
    if enemy_type is None:
        enemy_type = random.choices(["normal", "tanker", "runner"], weights=[40, 30, 30])[0]
    enemies.append(Enemy(x, y, enemy_type))


def spawn_enemies(count):
    for _ in range(count):
        spawn_wave_enemy()


def start_wave(global wave_number):
    global wave_target, enemies_to_spawn, wave_spawn_timer, wave_message, wave_message_time
    wave_target = 5 + wave_number // 1.25
    enemies_to_spawn = wave_target
    wave_spawn_timer = 0.15
    wave_message = f"Wave {wave_number}"
    wave_message_time = 3.0


def draw_health_bar():
    bar_x = 10
    bar_y = 10
    bar_width = 320
    bar_height = 28
    fill_width = int((player.current_health / player.max_health) * (bar_width - 4))
    pygame.draw.rect(screen, (20, 20, 35), (bar_x, bar_y, bar_width, bar_height), border_radius=8)
    pygame.draw.rect(screen, (220, 20, 20), (bar_x + 2, bar_y + 2, bar_width - 4, bar_height - 4), border_radius=6)
    pygame.draw.rect(screen, (80, 220, 120), (bar_x + 2, bar_y + 2, max(fill_width, 0), bar_height - 4), border_radius=6)

def draw_ability_slots():
    slot_x = 10
    slot_y = 80
    slot_width = 180
    slot_height = 60
    slot_gap = 10
    available_charges = kill_count // 20 - player.bloodthirst_uses
    for index in range(3):
        x = slot_x + index * (slot_width + slot_gap)
        slot_rect = pygame.Rect(x, slot_y, slot_width, slot_height)
        pygame.draw.rect(screen, (30, 30, 45), slot_rect, border_radius=10)
        pygame.draw.rect(screen, (120, 180, 240), slot_rect, width=2, border_radius=10)
        if index == 0:
            name = "Bloodthirst"
            status_color = (120, 255, 120) if available_charges > 0 else (255, 120, 120)
            label = ui_font.render(name, True, (255, 255, 255))
            screen.blit(label, (x + 10, slot_y + 8))
            count_label = small_font.render(f"Charges: {available_charges}", True, status_color)
            screen.blit(count_label, (x + 10, slot_y + 34))
            if player.bloodthirst_active:
                active_label = small_font.render(f"Active {player.bloodthirst_timer:.1f}s", True, (255, 255, 120))
                screen.blit(active_label, (x + 10, slot_y + 8 + label.get_height()))
        else:
            if player.ability_slots[index]:
                label = ui_font.render(player.ability_slots[index], True, (255, 255, 255))
                screen.blit(label, (x + 10, slot_y + 14))
            else:
                label = small_font.render("Empty Slot", True, (180, 180, 180))
                screen.blit(label, (x + 10, slot_y + 20))


def draw_title_screen():
    title = title_font.render("", True, (32, 32, 32))
    subtitle = ui_font.render("Click to begin", True, (32, 32, 32))
    screen.blit(title, (screen_width // 2 - title.get_width() // 2, screen_height // 2 - 120))
    screen.blit(subtitle, (screen_width // 2 - subtitle.get_width() // 2, screen_height // 2 - 20))
    controls = small_font.render("Move: WASD / Arrow keys  •  Shoot: Left Click / Space  •  Swap weapon: G", True, (32, 32, 32))
    screen.blit(controls, (screen_width // 2 - controls.get_width() // 2, screen_height // 2 + 40))


def draw_game_over_screen():
    title = title_font.render("Game Over", True, (200, 30, 30))
    subtitle = ui_font.render("Press R to retry mission", True, (255, 255, 255))
    screen.blit(title, (screen_width // 2 - title.get_width() // 2, screen_height // 2 - 150))
    screen.blit(subtitle, (screen_width // 2 - subtitle.get_width() // 2, screen_height // 2 - 10))
    stats = ui_font.render(f"Waves cleared: {wave_number}", True, (255, 255, 255))
    screen.blit(stats, (screen_width // 2 - stats.get_width() // 2, screen_height // 2 + 40))


def reset():
    global bullets, sword_swings, enemies, powerups, boulders, shockwaves, kill_count, wave_number, wave_target
    global enemies_to_spawn, wave_spawn_timer, wave_message, wave_message_time, Game_state, player_state
    bullets = []
    sword_swings = []
    enemies = []
    powerups = []
    boulders = []
    shockwaves = []
    kill_count = 0
    wave_number = 0
    wave_target = 0
    enemies_to_spawn = 0
    wave_spawn_timer = 0.0
    wave_message = ""
    wave_message_time = 0.0
    player.x = screen_width // 2
    player.y = 670
    player.current_health = player.max_health
    player.ammo = 15
    player.is_alive = True
    player.weapon = "sword"
    player.attack_cooldown = 0.0
    player.weapon_swap_cooldown = 0.0
    player.sword_cooldown = Sword.slash_cooldown
    player.damage_multiplier = 1.0
    player.bloodthirst_timer = 0.0
    player.bloodthirst_active = False
    player.bloodthirst_uses = 0
    player.Iframe_timer = 0.0
    player_state = "idle"
    Game_state = "playing"
    start_wave(1)


def update(dt):
    """handles all updates to the game

    Args:
        dt : time since last frame
    """
    global kill_count, enemies_to_spawn, wave_spawn_timer, wave_message, wave_message_time, wave_number, boulders, powerups, Game_state

    keys_pressed = pygame.key.get_pressed()

    if Game_state == "title_screen":
        draw_title_screen()
        if keys_pressed[pygame.K_RETURN] or keys_pressed[pygame.K_SPACE] or pygame.mouse.get_pressed()[0]:
            reset()
        return

    if Game_state == "game_over":
        draw_game_over_screen()
        if keys_pressed[pygame.K_r]:
            reset()
        return

    player.movement(dt, keys_pressed)
    player.state_machine(keys_pressed)

    player.attack_cooldown = max(0.0, player.attack_cooldown - dt)
    player.weapon_swap_cooldown = max(0.0, player.weapon_swap_cooldown - dt)

    if player_state == "attacking" and player.attack_cooldown <= 0.0:
        if player.weapon == "gun":
            fire_bullet()
            player.attack_cooldown = 0.30
        elif player.weapon == "sword":
            swing_sword()
            player.attack_cooldown = player.sword_cooldown

    if player.bloodthirst_active:
        player.bloodthirst_timer = max(0.0, player.bloodthirst_timer - dt)
        if player.bloodthirst_timer <= 0.0:
            player.bloodthirst_active = False
            player.damage_multiplier = 1.0
            player.sword_cooldown = Sword.slash_cooldown
            player.max_ammo = 30
            if player.ammo > player.max_ammo:
                player.ammo = player.max_ammo

    if player.Iframe_timer > 0.0:
        player.Iframe_timer = max(0.0, player.Iframe_timer - dt)

    if keys_pressed[pygame.K_x]:
        available_charges = kill_count // 20 - player.bloodthirst_uses
        if available_charges > 0 and not player.bloodthirst_active:
            player.bloodthirst_active = True
            player.bloodthirst_timer = 5.0
            player.bloodthirst_uses += 1
            player.damage_multiplier = 1.2
            player.sword_cooldown = 0.25
            player.max_ammo = 90
            player.ammo = max(player.ammo, player.max_ammo)

    if player.current_health <= 0:
        player.is_alive = False
        Game_state = "game_over"

    if not player.is_alive:
        draw_game_over_screen()
        return

    if len(enemies) == 0 and enemies_to_spawn == 0:
        if wave_number < max_waves:
            start_wave(wave_number + 1)
        elif wave_message != "All waves cleared!":
            wave_message = "All 50 waves cleared!"
            wave_message_time = 5.0

    if enemies_to_spawn > 0:
        wave_spawn_timer -= dt
        spawn_interval = max(0.1, 0.5 - wave_number * 0.006)
        if wave_spawn_timer <= 0:
            spawn_wave_enemy()
            enemies_to_spawn -= 1
            wave_spawn_timer += spawn_interval

    for bullet in bullets[:]:
        bullet.update(dt)
        for enemy in enemies:
            if math.hypot(bullet.x - enemy.x, bullet.y - enemy.y) <= bullet.radius + enemy.radius:
                enemy.current_health -= bullet.damage
                if enemy.is_dead():
                    try_spawn_powerup(enemy)
                    enemies.remove(enemy)
                    handle_enemy_kill()
                if bullet in bullets:
                    bullets.remove(bullet)
                break
        else:
            bullet.draw(screen)

    bullets[:] = [bullet for bullet in bullets if 0 <= bullet.x <= screen_width and 0 <= bullet.y <= screen_height]

    for boulder in boulders[:]:
        boulder.update(dt)
        if boulder.time_alive >= 5.0 and not boulder.exploded:
            shockwaves.append(Shockwave(boulder.x, boulder.y))
            boulder.exploded = True
            boulders.remove(boulder)
            continue
        if math.hypot(boulder.x - player.x, boulder.y - player.y) <= boulder.radius + player.radius:
            if player.Iframe_timer <= 0.0:
                player.current_health = max(0, player.current_health - boulder.damage)
                player.Iframe_timer = 0.8
            boulders.remove(boulder)
            continue
        if not (0 <= boulder.x <= screen_width and 0 <= boulder.y <= screen_height):
            boulders.remove(boulder)
            continue
        boulder.draw(screen)

    for powerup in powerups[:]:
        powerup.draw(screen)
        if powerup.collides_with(player):
            powerup.apply(player)
            powerups.remove(powerup)

    for shockwave in shockwaves[:]:
        shockwave.update(dt)
        shockwave.draw(screen)
        if not shockwave.hit_applied and shockwave.age < shockwave.duration:
            dx = player.x - shockwave.x
            dy = player.y - shockwave.y
            if math.hypot(dx, dy) <= shockwave.max_radius * (shockwave.age / shockwave.duration):
                if player.Iframe_timer <= 0.0:
                    player.current_health = max(0, player.current_health - shockwave.damage)
                    player.Iframe_timer = 0.8
                shockwave.hit_applied = True
        if shockwave.is_expired():
            shockwaves.remove(shockwave)

    for sword in sword_swings:
        sword.update(dt)
        sword.hit_enemies(enemies)
        sword.draw(screen)

    sword_swings[:] = [sword for sword in sword_swings if sword.is_active()]

    for enemy in enemies:
        enemy.update(dt, enemies)
        enemy.draw(screen)

    player.draw(screen)
    draw_health_bar()
    draw_ability_slots()
    kills_text = ui_font.render(f"Kills: {kill_count}", True, (255, 255, 255))
    screen.blit(kills_text, (10, 190))
    wave_text = ui_font.render(f"Wave: {wave_number}/{max_waves}", True, (255, 255, 255))
    screen.blit(wave_text, (10, 220))

    # bottom-right weapon/ammo UI
    icon_size = 36
    icon_padding = 12
    panel_padding = 16
    weapon_text = ui_font.render(f"{player.weapon.title()}", True, (245, 245, 245))
    ammo_text = ui_font.render(f"Ammo: {player.ammo}/{player.max_ammo}", True, (245, 245, 245))
    panel_width = max(icon_size, weapon_text.get_width(), ammo_text.get_width()) + panel_padding * 2
    panel_height = icon_size + panel_padding * 2
    panel_x = screen_width - panel_width - icon_padding
    panel_y = screen_height - panel_height - icon_padding
    pygame.draw.rect(screen, (20, 20, 35), (panel_x, panel_y, panel_width, panel_height), border_radius=10)
    pygame.draw.rect(screen, (120, 180, 240), (panel_x, panel_y, panel_width, panel_height), width=2, border_radius=10)

    icon_x = panel_x + panel_padding
    icon_y = panel_y + panel_padding
    if player.weapon == "gun":
        pygame.draw.rect(screen, (180, 180, 180), (icon_x + 6, icon_y + 10, icon_size - 12, 16), border_radius=6)
        pygame.draw.rect(screen, (240, 220, 120), (icon_x + icon_size - 10, icon_y + 14, 12, 8), border_radius=3)
        pygame.draw.rect(screen, (90, 90, 110), (icon_x + 4, icon_y + 8, 8, 20), border_radius=4)
    else:
        sword_points = [
            (icon_x + icon_size * 0.5, icon_y + 6),
            (icon_x + icon_size - 8, icon_y + icon_size - 10),
            (icon_x + icon_size * 0.5, icon_y + icon_size - 6),
            (icon_x + 8, icon_y + icon_size - 10)
        ]
        pygame.draw.polygon(screen, (240, 240, 240), sword_points)
        pygame.draw.line(screen, (180, 180, 180), (icon_x + icon_size * 0.5, icon_y + 6), (icon_x + icon_size * 0.5, icon_y + icon_size - 6), 6)

    text_x = icon_x + icon_size + panel_padding
    text_y = panel_y + panel_padding
    screen.blit(weapon_text, (text_x, text_y))
    screen.blit(ammo_text, (text_x, text_y + weapon_text.get_height() + 4))

    if wave_message_time > 0:
        wave_message_time -= dt
        msg_text = ui_font.render(wave_message, True, (255, 255, 255))
        screen.blit(msg_text, (screen_width // 2 - msg_text.get_width() // 2, 10))








#================================================METHODS==================================================#

player= Player(screen_width // 2, 670, 20)


if __name__ == '__main__':
    run_game()