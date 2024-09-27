import pygame
import math
import random
import time

# Initialize pygame
pygame.init()

# Screen and world dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 1420, 900
WORLD_WIDTH, WORLD_HEIGHT = 5000, 5000
TILE_SIZE = 25

# Minimap visibility
minimap_visible = True  # Start with the minimap visible by default

# Minimap dimensions
MINIMAP_WIDTH = 200
MINIMAP_HEIGHT = 200
MINIMAP_SCALE = MINIMAP_WIDTH / WORLD_WIDTH

# Colors
AQUA = (63,180,223)
DARK_GRAY = (170,170,170)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

# Create the screen object
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Diep.io")

# Clock object to control game speed
clock = pygame.time.Clock()

class Enemy:
    def __init__(self, x, y):
        self.world_x = x
        self.world_y = y
        self.size = 40
        self.speed = 3
        self.angle = 0
        self.color = RED
        self.bullets = []
        self.shoot_cooldown = 0
        self.cannon_length = 75
        self.cannon_thickness = 35
        self.health = 500
        self.max_health = 500

    def draw(self, tank):
        screen_x = self.world_x - tank.world_x + tank.x
        screen_y = self.world_y - tank.world_y + tank.y

        # Draw cannon
        cannon_end_x = screen_x + math.cos(self.angle) * self.cannon_length
        cannon_end_y = screen_y + math.sin(self.angle) * self.cannon_length
        perpendicular_angle = self.angle + math.pi / 2
        half_thickness = self.cannon_thickness / 2
        corner_offset_x = math.cos(perpendicular_angle) * half_thickness
        corner_offset_y = math.sin(perpendicular_angle) * half_thickness
        cannon_corners = [
            (screen_x + corner_offset_x, screen_y + corner_offset_y),
            (screen_x - corner_offset_x, screen_y - corner_offset_y),
            (cannon_end_x - corner_offset_x, cannon_end_y - corner_offset_y),
            (cannon_end_x + corner_offset_x, cannon_end_y + corner_offset_y)
        ]
        pygame.draw.polygon(screen, (150, 150, 150), cannon_corners)

        # Draw enemy body
        pygame.draw.circle(screen, self.color, (int(screen_x), int(screen_y)), self.size)

        # Draw health bar
        health_bar_width = self.size * 2
        health_bar_height = 5
        health_percentage = self.health / self.max_health
        health_bar_color = RED if self.health < self.max_health / 2 else GREEN
        pygame.draw.rect(screen, health_bar_color, (
            int(screen_x - health_bar_width // 2),
            int(screen_y - self.size - 15),
            int(health_bar_width * health_percentage),
            health_bar_height
        ))
        pygame.draw.rect(screen, BLACK, (
            int(screen_x - health_bar_width // 2),
            int(screen_y - self.size - 15),
            health_bar_width,
            health_bar_height
        ), 1)

    def update(self, tank):
        # Simple AI: move towards the player
        angle_to_player = math.atan2(tank.world_y - self.world_y, tank.world_x - self.world_x)
        self.world_x += math.cos(angle_to_player) * self.speed
        self.world_y += math.sin(angle_to_player) * self.speed

        # Rotate towards the player
        self.angle = angle_to_player

        # Shoot at the player
        if self.shoot_cooldown <= 0:
            self.shoot()
            self.shoot_cooldown = 60  # Shoot every second

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        # Update bullets
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.off_screen():
                self.bullets.remove(bullet)

    def shoot(self):
        bullet_x = self.world_x + math.cos(self.angle) * self.size
        bullet_y = self.world_y + math.sin(self.angle) * self.size
        bullet_speed = 8
        bullet = Bullet(bullet_x, bullet_y, math.cos(self.angle) * bullet_speed, math.sin(self.angle) * bullet_speed, 1)
        self.bullets.append(bullet)

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            return True
        return False


class Tank:
    def __init__(self):
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT // 2
        self.size = 40
        self.speed = 5
        self.angle = 0
        self.color = AQUA
        self.world_x = WORLD_WIDTH // 2
        self.world_y = WORLD_HEIGHT // 2
        self.bullets = []
        self.autofire = False
        self.autospin = False
        self.shoot_cooldown = 0
        self.cannon_length = 75
        self.cannon_thickness = 35
        self.recoil_velocity_x = 0
        self.recoil_velocity_y = 0
        self.recoil_dampening = 0.45
        self.max_recoil_speed = 2
        self.health = 500
        self.max_health = 500
        self.regen_rate = 0.1
        self.regen_cooldown = 0
        self.regen_cooldown_max = 180

    def draw(self):
        # Draw cannon
        cannon_end_x = self.x + math.cos(self.angle) * self.cannon_length
        cannon_end_y = self.y + math.sin(self.angle) * self.cannon_length
        perpendicular_angle = self.angle + math.pi / 2
        half_thickness = self.cannon_thickness / 2
        corner_offset_x = math.cos(perpendicular_angle) * half_thickness
        corner_offset_y = math.sin(perpendicular_angle) * half_thickness
        cannon_corners = [
            (self.x + corner_offset_x, self.y + corner_offset_y),
            (self.x - corner_offset_x, self.y - corner_offset_y),
            (cannon_end_x - corner_offset_x, cannon_end_y - corner_offset_y),
            (cannon_end_x + corner_offset_x, cannon_end_y + corner_offset_y)
        ]
        pygame.draw.polygon(screen, (150, 150, 150), cannon_corners)

        # Draw tank body
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.size)

        # Draw health bar
        health_bar_width = self.size * 2
        health_bar_height = 5
        health_percentage = self.health / self.max_health
        health_bar_color = RED if self.health < self.max_health / 2 else GREEN
        pygame.draw.rect(screen, health_bar_color, (
            int(self.x - health_bar_width // 2),
            int(self.y - self.size - 15),
            int(health_bar_width * health_percentage),
            health_bar_height
        ))
        pygame.draw.rect(screen, BLACK, (
            int(self.x - health_bar_width // 2),
            int(self.y - self.size - 15),
            health_bar_width,
            health_bar_height
        ), 1)

    def update(self, keys_pressed):
        move_x, move_y = 0, 0
        if keys_pressed[pygame.K_w]: move_y = -1
        if keys_pressed[pygame.K_s]: move_y = 1
        if keys_pressed[pygame.K_a]: move_x = -1
        if keys_pressed[pygame.K_d]: move_x = 1

        # Normalize movement and apply recoil
        if move_x != 0 or move_y != 0:
            magnitude = math.sqrt(move_x ** 2 + move_y ** 2)
            move_x, move_y = move_x / magnitude, move_y / magnitude
        move_x += self.recoil_velocity_x
        move_y += self.recoil_velocity_y

        # Update world coordinates and clamp to world bounds
        self.world_x = max(self.size, min(WORLD_WIDTH - self.size, self.world_x + move_x * self.speed))
        self.world_y = max(self.size, min(WORLD_HEIGHT - self.size, self.world_y + move_y * self.speed))

        # Apply dampening to recoil
        self.recoil_velocity_x *= self.recoil_dampening
        self.recoil_velocity_y *= self.recoil_dampening

        # Ensure recoil doesn't exceed maximum speed
        recoil_speed = math.sqrt(self.recoil_velocity_x ** 2 + self.recoil_velocity_y ** 2)
        if recoil_speed > self.max_recoil_speed:
            factor = self.max_recoil_speed / recoil_speed
            self.recoil_velocity_x *= factor
            self.recoil_velocity_y *= factor

        # Handle health regeneration
        if self.health < self.max_health:
            if self.regen_cooldown > 0:
                self.regen_cooldown -= 1
            else:
                self.health = min(self.max_health, self.health + self.regen_rate)

    def rotate_to_mouse(self, mouse_pos):
        if self.autospin:
            self.angle += 0.05
        else:
            dx, dy = mouse_pos[0] - self.x, mouse_pos[1] - self.y
            self.angle = math.atan2(dy, dx)

    def shoot(self):
        if self.shoot_cooldown <= 0:
            bullet_x = self.world_x + math.cos(self.angle) * self.size
            bullet_y = self.world_y + math.sin(self.angle) * self.size
            bullet_speed = 10
            bullet = Bullet(bullet_x, bullet_y, math.cos(self.angle) * bullet_speed, math.sin(self.angle) * bullet_speed, 0)
            self.bullets.append(bullet)

            # Apply recoil
            recoil_force = 0.2
            self.recoil_velocity_x -= math.cos(self.angle) * recoil_force
            self.recoil_velocity_y -= math.sin(self.angle) * recoil_force

            self.shoot_cooldown = 15

    def handle_autofire(self):
        if self.autofire and self.shoot_cooldown <= 0:
            self.shoot()
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def take_damage(self, damage, attacker=None):
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            global game_over, killer_object
            game_over = True
            killer_object = attacker if attacker else "Unknown"
        self.regen_cooldown = self.regen_cooldown_max

    def check_collision_with_enemies(self, enemies):
        for enemy in enemies:
            distance = math.sqrt((self.world_x - enemy.world_x) ** 2 + (self.world_y - enemy.world_y) ** 2)
            if distance < self.size + enemy.size:
                self.take_damage(5, "Enemy")
                enemy.take_damage(5)
                angle = math.atan2(self.world_y - enemy.world_y, self.world_x - enemy.world_x)
                push_distance = (self.size + enemy.size) - distance
                self.world_x += math.cos(angle) * push_distance / 2
                self.world_y += math.sin(angle) * push_distance / 2
                enemy.world_x -= math.cos(angle) * push_distance / 2
                enemy.world_y -= math.sin(angle) * push_distance / 2

    def respawn(self):
        self.health = self.max_health
        self.world_x = random.randint(self.size, WORLD_WIDTH - self.size)
        self.world_y = random.randint(self.size, WORLD_HEIGHT - self.size)
        self.recoil_velocity_x = 0
        self.recoil_velocity_y = 0
        self.shoot_cooldown = 0
        self.regen_cooldown = 0

    def check_collision_with_shapes(self, shapes):
        for shape in shapes:
            if shape.alive:
                distance = math.sqrt((self.world_x - shape.world_x) ** 2 + (self.world_y - shape.world_y) ** 2)
                if distance < self.size + shape.size // 2:
                    self.take_damage(5, "Shape")
                    shape.take_damage(5)
                    angle = math.atan2(self.world_y - shape.world_y, self.world_x - shape.world_x)
                    push_distance = (self.size + shape.size // 2) - distance
                    self.world_x += math.cos(angle) * push_distance / 2
                    self.world_y += math.sin(angle) * push_distance / 2
                    shape.world_x -= math.cos(angle) * push_distance / 2
                    shape.world_y -= math.sin(angle) * push_distance / 2

class Bullet:
    def __init__(self, x, y, vel_x, vel_y, tankNum):
        self.world_x = x
        self.world_y = y
        self.vel_x = vel_x
        self.vel_y = vel_y
        self.radius = 10
        self.color = AQUA
        self.lifespan = 120
        self.damage = 25 - (tankNum*15);
        if tankNum == 0:
            self.color = AQUA
        if tankNum == 1:
            self.color = RED

    def update(self):
        self.world_x += self.vel_x
        self.world_y += self.vel_y
        self.lifespan -= 1
        if self.world_x - self.radius < 0 or self.world_x + self.radius > screen.get_width():
            self.world_x += self.vel_x
            self.world_y += self.vel_y
            self.lifespan -= 1
            if self.world_x - self.radius < 0 or self.world_x + self.radius > WORLD_WIDTH:
                self.vel_x = 0
            if self.world_y - self.radius < 0 or self.world_y + self.radius > WORLD_HEIGHT:
                self.vel_y = 0

    def draw(self, tank):
        screen_x = self.world_x - tank.world_x + tank.x
        screen_y = self.world_y - tank.world_y + tank.y
        pygame.draw.circle(screen, self.color, (int(screen_x), int(screen_y)), self.radius)

    def off_screen(self):
        return (self.world_x < 0 or self.world_x > WORLD_WIDTH or
                self.world_y < 0 or self.world_y > WORLD_HEIGHT or
                self.lifespan <= 0)

    def check_collision(self, shapes):
        for shape in shapes:
            if shape.alive:
                distance = math.sqrt((self.world_x - shape.world_x) ** 2 + (self.world_y - shape.world_y) ** 2)
                if distance < self.radius + shape.size // 2:
                    shape.take_damage(self.damage)
                    return True
        return False

    def check_collision_with_enemies(self, enemies):
        for enemy in enemies:
            distance = math.sqrt((self.world_x - enemy.world_x) ** 2 + (self.world_y - enemy.world_y) ** 2)
            if distance < self.radius + enemy.size:
                enemy.take_damage(self.damage)
                return True
        return False

    def check_collision_with_tank(self, tank):
        distance = math.sqrt((self.world_x - tank.world_x) ** 2 + (self.world_y - tank.world_y) ** 2)
        if distance < self.radius + tank.size:
            tank.take_damage(self.damage, "Enemy")
            return True
        return False

def initialize_enemies():
    enemies = []
    for _ in range(5):
        x = random.randint(100, WORLD_WIDTH - 100)
        y = random.randint(100, WORLD_HEIGHT - 100)
        enemies.append(Enemy(x, y))
    return enemies

class Shape:
    def __init__(self, x, y, shape_type):
        self.world_x = x
        self.world_y = y
        self.shape_type = shape_type
        self.angle = 0
        self.rotation_speed = random.uniform(0.01, 0.03)
        self.rotation_direction = random.choice([-1, 1])

        if shape_type == "square":
            self.size, self.health, self.max_health, self.color = 40, 100, 100, YELLOW
        elif shape_type == "triangle":
            self.size, self.health, self.max_health, self.color = 60, 200, 200, RED
        elif shape_type == "pentagon":
            self.size, self.health, self.max_health, self.color = 80, 300, 300, BLUE

        self.alive = True

    def update(self):
        self.angle += self.rotation_speed * self.rotation_direction

    def draw(self, tank):
        if not self.alive:
            return

        screen_x = self.world_x - tank.world_x + tank.x
        screen_y = self.world_y - tank.world_y + tank.y

        if self.shape_type == "square":
            top_left_x = screen_x - self.size // 2
            top_left_y = screen_y - self.size // 2
            pygame.draw.rect(screen, self.color, (top_left_x, top_left_y, self.size, self.size))
        else:
            points = []
            num_sides = 3 if self.shape_type == "triangle" else 5
            peak_angle = -math.pi / 2
            peak_x = screen_x + math.cos(peak_angle) * self.size // 2
            peak_y = screen_y + math.sin(peak_angle) * self.size // 2

            for i in range(num_sides):
                angle = self.angle + (math.pi * 2 * i / num_sides)
                point_x = peak_x + math.cos(angle) * self.size // 2
                point_y = peak_y + math.sin(angle) * self.size // 2
                points.append((point_x, point_y))

            pygame.draw.polygon(screen, self.color, points)

        # Draw health bar
        health_bar_width = self.size
        health_bar_height = 5
        health_percentage = self.health / self.max_health
        health_bar_color = RED if self.health < self.max_health / 2 else GREEN
        pygame.draw.rect(screen, health_bar_color, (
            int(screen_x - health_bar_width // 2), int(screen_y - self.size // 2 - 10),
            int(health_bar_width * health_percentage), health_bar_height))
        pygame.draw.rect(screen, BLACK, (
        int(screen_x - health_bar_width // 2), int(screen_y - self.size // 2 - 10), health_bar_width,
        health_bar_height), 1)

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.alive = False

def draw_autofire_indicator(tank):
    font = pygame.font.SysFont(None, 24)
    autofire_text = "Autofire: ON" if tank.autofire else "Autofire: OFF"
    autofire_color = GREEN if tank.autofire else RED
    text_surface = font.render(autofire_text, True, autofire_color)
    screen.blit(text_surface, (10, 10))

def draw_autospin_indicator(tank):
    font = pygame.font.SysFont(None, 24)
    autospin_text = "Autospin: ON" if tank.autospin else "Autospin: OFF"
    autospin_color = GREEN if tank.autospin else RED
    text_surface = font.render(autospin_text, True, autospin_color)
    screen.blit(text_surface, (10, 40))

# Draw the grid-based terrain
def draw_grid(tank):
    cols = SCREEN_WIDTH // TILE_SIZE + 2  # Number of tiles needed to fill the width
    rows = SCREEN_HEIGHT // TILE_SIZE + 2  # Number of tiles needed to fill the height
    # Calculate the offset based on the player's world position
    offset_x = tank.world_x % TILE_SIZE
    offset_y = tank.world_y % TILE_SIZE
    # Loop through rows and columns and draw tiles
    for row in range(rows):
        for col in range(cols):
            # Calculate tile position in world coordinates
            tile_x = col * TILE_SIZE - offset_x
            tile_y = row * TILE_SIZE - offset_y
            # Draw the grid tile
            pygame.draw.rect(screen, DARK_GRAY, (tile_x, tile_y, TILE_SIZE, TILE_SIZE), 1)

def format_time(seconds):
    minutes, seconds = divmod(int(seconds), 60)
    return f"{minutes:02d}:{seconds:02d}"

def death_screen(screen, clock, killer_object, survival_time):
    transparent_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    transparent_surface.fill((100, 100, 100, 200))

    font_large = pygame.font.Font(None, 74)
    font_medium = pygame.font.Font(None, 48)
    font_small = pygame.font.Font(None, 36)

    death_text = font_large.render("YOU DIED", True, RED)
    killer_text = font_medium.render(f"Killed by: {killer_object}", True, WHITE)
    time_text = font_medium.render(f"Survival time: {format_time(survival_time)}", True, WHITE)

    button_rect = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 100, 200, 50)
    button_text = font_small.render("Continue", True, BLACK)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    return

        screen.blit(transparent_surface, (0, 0))
        screen.blit(death_text, death_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100)))
        screen.blit(killer_text, killer_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)))
        screen.blit(time_text, time_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)))

        pygame.draw.rect(screen, WHITE, button_rect)
        screen.blit(button_text, button_text.get_rect(center=button_rect.center))

        pygame.display.flip()
        clock.tick(60)

def draw_world_border(tank):
    screen_x = tank.x - tank.world_x
    screen_y = tank.y - tank.world_y
    if screen_y > 0:
        pygame.draw.rect(screen, GRAY, (0, 0, SCREEN_WIDTH, screen_y))
    if screen_y + WORLD_HEIGHT < SCREEN_HEIGHT:
        pygame.draw.rect(screen, GRAY,
                         (0, screen_y + WORLD_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT - (screen_y + WORLD_HEIGHT)))
    if screen_x > 0:
        pygame.draw.rect(screen, GRAY, (0, 0, screen_x, SCREEN_HEIGHT))
    if screen_x + WORLD_WIDTH < SCREEN_WIDTH:
        pygame.draw.rect(screen, GRAY,
                         (screen_x + WORLD_WIDTH, 0, SCREEN_WIDTH - (screen_x + WORLD_WIDTH), SCREEN_HEIGHT))

def draw_minimap(tank, shapes):
    # Define the position of the minimap on the screen (bottom right)
    minimap_x = SCREEN_WIDTH - MINIMAP_WIDTH - 10  # 10px margin from right edge
    minimap_y = SCREEN_HEIGHT - MINIMAP_HEIGHT - 10  # 10px margin from bottom edge

    # Draw the minimap background
    pygame.draw.rect(screen, BLACK, (minimap_x, minimap_y, MINIMAP_WIDTH, MINIMAP_HEIGHT))
    pygame.draw.rect(screen, WHITE, (minimap_x, minimap_y, MINIMAP_WIDTH, MINIMAP_HEIGHT), 2)

    # Draw the player as a small dot on the minimap
    player_minimap_x = minimap_x + int(tank.world_x * MINIMAP_SCALE)
    player_minimap_y = minimap_y + int(tank.world_y * MINIMAP_SCALE)
    pygame.draw.circle(screen, BLUE, (player_minimap_x, player_minimap_y), 5)  # Player dot

    # Draw the shapes on the minimap
    for shape in shapes:
        if shape.alive:
            shape_minimap_x = minimap_x + int(shape.world_x * MINIMAP_SCALE)
            shape_minimap_y = minimap_y + int(shape.world_y * MINIMAP_SCALE)

            # Use smaller sizes on the minimap for shapes
            if shape.shape_type == "square":
                pygame.draw.rect(screen, shape.color,
                                 (shape_minimap_x - 2, shape_minimap_y - 2, 4, 4))  # Small square
            elif shape.shape_type == "triangle":
                pygame.draw.polygon(screen, shape.color,
                                    [(shape_minimap_x, shape_minimap_y - 3),
                                     (shape_minimap_x - 3, shape_minimap_y + 3),
                                     (shape_minimap_x + 3, shape_minimap_y + 3)])  # Small triangle
            elif shape.shape_type == "pentagon":
                pygame.draw.circle(screen, shape.color, (shape_minimap_x, shape_minimap_y), 3)  # Small circle

def draw_minimap_indicator(minimap_visible):
    font = pygame.font.SysFont(None, 24)
    indicator_text = "Minimap: ON" if minimap_visible else "Minimap: OFF"
    text_surface = font.render(indicator_text, True, BLACK)

    # Position of the indicator (bottom-right corner or above minimap)
    if minimap_visible:
        # Place the indicator slightly above the minimap
        indicator_x = SCREEN_WIDTH - 120  # Slightly offset from the minimap
        indicator_y = SCREEN_HEIGHT - 230  # Above the minimap
    else:
        # Place the indicator in the bottom-right corner when minimap is off
        indicator_x = SCREEN_WIDTH - 120
        indicator_y = SCREEN_HEIGHT - 20

    # Draw the text indicator on the screen
    screen.blit(text_surface, (indicator_x, indicator_y))

def initialize_shapes():
    shapes = [
        Shape(1000, 1000, "square"),
        Shape(1200, 1200, "triangle"),
        Shape(1500, 1500, "pentagon"),
    ]
    for _ in range(50):
        shapes.append(Shape(random.randint(100, 4900), random.randint(100, 4900), "square"))
        shapes.append(Shape(random.randint(100, 4900), random.randint(100, 4900), "triangle"))
        shapes.append(Shape(random.randint(100, 4900), random.randint(100, 4900), "pentagon"))
    return shapes

def game_loop():
    global game_over, killer_object
    tank = Tank()
    shapes = initialize_shapes()
    enemies = initialize_enemies()
    running = True
    minimap_visible = True
    game_over = False
    start_time = time.time()
    killer_object = ""

    while running:
        screen.fill(GRAY)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                if tank.shoot_cooldown <= 0:
                    tank.shoot()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    tank.autofire = not tank.autofire
                if event.key == pygame.K_c:
                    tank.autospin = not tank.autospin
                if event.key == pygame.K_o:
                    tank.take_damage(tank.health, "Self-Destruct")
                if event.key == pygame.K_TAB:
                    minimap_visible = not minimap_visible

        if not game_over:
            keys_pressed = pygame.key.get_pressed()
            tank.update(keys_pressed)
            tank.rotate_to_mouse(pygame.mouse.get_pos())
            tank.handle_autofire()

            for shape in shapes:
                shape.update()

            for enemy in enemies:
                enemy.update(tank)

            # Handle collisions
            tank.check_collision_with_enemies(enemies)
            tank.check_collision_with_shapes(shapes)

            for bullet in tank.bullets[:]:
                bullet.update()
                if bullet.off_screen():
                    tank.bullets.remove(bullet)
                elif bullet.check_collision(shapes):
                    tank.bullets.remove(bullet)
                elif bullet.check_collision_with_enemies(enemies):
                    tank.bullets.remove(bullet)

            for enemy in enemies[:]:
                for bullet in enemy.bullets[:]:
                    bullet.update()
                    if bullet.off_screen():
                        enemy.bullets.remove(bullet)
                    elif bullet.check_collision_with_tank(tank):
                        enemy.bullets.remove(bullet)

        # Drawing
        draw_grid(tank)
        draw_world_border(tank)

        for shape in shapes:
            shape.draw(tank)

        for enemy in enemies:
            enemy.draw(tank)
            for bullet in enemy.bullets:
                bullet.draw(tank)

        tank.draw()
        for bullet in tank.bullets:
            bullet.draw(tank)

        if minimap_visible:
            draw_minimap(tank, shapes)

        draw_autofire_indicator(tank)
        draw_autospin_indicator(tank)
        draw_minimap_indicator(minimap_visible)

        pygame.display.flip()
        clock.tick(60)

        if game_over:
            survival_time = time.time() - start_time
            death_screen(screen, clock, killer_object, survival_time)
            game_over = False
            tank.respawn()
            start_time = time.time()

    pygame.quit()

# Main game execution
if __name__ == "__main__":
    game_loop()
