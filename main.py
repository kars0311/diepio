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
PINK = (255,150,150)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

# Create the screen object
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Diep.io")

# Clock object to control game speed
clock = pygame.time.Clock()

def draw_menu(screen, clock):
    menu_font = pygame.font.Font(None, 74)
    option_font = pygame.font.Font(None, 50)

    title = menu_font.render("Diep.io", True, BLACK)
    option1 = option_font.render("1. Play with enemy bots", True, BLACK)
    option2 = option_font.render("2. Play without enemy bots", True, BLACK)

    while True:
        screen.fill(WHITE)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))
        screen.blit(option1, (SCREEN_WIDTH // 2 - option1.get_width() // 2, 300))
        screen.blit(option2, (SCREEN_WIDTH // 2 - option2.get_width() // 2, 400))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return True
                if event.key == pygame.K_2:
                    return False

        clock.tick(60)

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
        self.alive = True
        self.target = None
        # New attributes for barrel recoil
        self.barrel_recoil = 0
        self.max_barrel_recoil = 10
        self.barrel_recoil_speed = 1

    def draw(self, tank):
        if not self.alive:
            return  # Don't draw dead enemies

        screen_x = self.world_x - tank.world_x + tank.x
        screen_y = self.world_y - tank.world_y + tank.y

        # Calculate recoil-adjusted cannon length
        recoil_adjusted_length = self.cannon_length - self.barrel_recoil

        # Draw cannon with recoil
        cannon_end_x = screen_x + math.cos(self.angle) * recoil_adjusted_length
        cannon_end_y = screen_y + math.sin(self.angle) * recoil_adjusted_length
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

        # Draw health bar only if health is below max
        if self.health < self.max_health:
            health_bar_width = self.size * 2
            health_bar_height = 5
            health_percentage = self.health / self.max_health
            health_bar_color = RED if self.health < self.max_health / 2 else GREEN
            pygame.draw.rect(screen, health_bar_color, (
                int(screen_x - health_bar_width // 2),
                int(screen_y + self.size + 5),  # Move below the enemy
                int(health_bar_width * health_percentage),
                health_bar_height
            ))
            pygame.draw.rect(screen, BLACK, (
                int(screen_x - health_bar_width // 2),
                int(screen_y + self.size + 5),  # Move below the enemy
                health_bar_width,
                health_bar_height
            ), 1)

    def update(self, tank, shapes):
        if not self.alive:
            return

        # Define the boundary around the player
        boundary_width = SCREEN_WIDTH * 1.5
        boundary_height = SCREEN_HEIGHT * 1.5
        in_boundary = (abs(self.world_x - tank.world_x) < boundary_width / 2 and
                       abs(self.world_y - tank.world_y) < boundary_height / 2)

        if in_boundary:
            self.target_player(tank)
        else:
            self.target_nearest_shape(shapes)

        # Move towards the target
        if self.target:
            angle_to_target = math.atan2(self.target[1] - self.world_y, self.target[0] - self.world_x)
            self.world_x += math.cos(angle_to_target) * self.speed
            self.world_y += math.sin(angle_to_target) * self.speed
            self.angle = angle_to_target

        # Shoot at the target
        if self.shoot_cooldown <= 0 and self.target:
            self.shoot()
            self.shoot_cooldown = 60  # Shoot every second

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        # Update bullets
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.off_screen():
                self.bullets.remove(bullet)

        # Update barrel recoil
        if self.barrel_recoil > 0:
            self.barrel_recoil = max(0, self.barrel_recoil - self.barrel_recoil_speed)

    def target_player(self, tank):
        self.target = (tank.world_x, tank.world_y)

    def target_nearest_shape(self, shapes):
        nearest_shape = None
        min_distance = float('inf')
        for shape in shapes:
            if shape.alive:
                distance = math.sqrt((self.world_x - shape.world_x)**2 + (self.world_y - shape.world_y)**2)
                if distance < min_distance:
                    min_distance = distance
                    nearest_shape = shape
        if nearest_shape:
            self.target = (nearest_shape.world_x, nearest_shape.world_y)
        else:
            self.target = None

    def shoot(self):
        bullet_x = self.world_x + math.cos(self.angle) * self.size
        bullet_y = self.world_y + math.sin(self.angle) * self.size
        bullet_speed = 8
        bullet = Bullet(bullet_x, bullet_y, math.cos(self.angle) * bullet_speed, math.sin(self.angle) * bullet_speed, 1)
        self.bullets.append(bullet)

        # Apply barrel recoil
        self.barrel_recoil = self.max_barrel_recoil

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            self.alive = False  # Mark the enemy as dead
        return self.alive

    def check_collision_with_enemies(self, enemies):
        for enemy in enemies:
            distance = math.sqrt((self.world_x - enemy.world_x) ** 2 + (self.world_y - enemy.world_y) ** 2)
            if distance < self.size + enemy.size:
                angle = math.atan2(self.world_y - enemy.world_y, self.world_x - enemy.world_x)
                push_distance = (self.size + enemy.size) - distance
                self.world_x += math.cos(angle) * push_distance / 2
                self.world_y += math.sin(angle) * push_distance / 2
                enemy.world_x -= math.cos(angle) * push_distance / 2
                enemy.world_y -= math.sin(angle) * push_distance / 2

class Tank:
    def __init__(self):
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT // 2
        self.size = 40
        self.score=0
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
        # New attributes for barrel recoil
        self.barrel_recoil = 0
        self.max_barrel_recoil = 10
        self.barrel_recoil_speed = 1

    def draw(self):
        # Calculate recoil-adjusted cannon length
        recoil_adjusted_length = self.cannon_length - self.barrel_recoil

        # Draw cannon with recoil
        cannon_end_x = self.x + math.cos(self.angle) * recoil_adjusted_length
        cannon_end_y = self.y + math.sin(self.angle) * recoil_adjusted_length
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

        # Draw health bar only if health is below max
        if self.health < self.max_health:
            health_bar_width = self.size * 2
            health_bar_height = 5
            health_percentage = self.health / self.max_health
            health_bar_color = RED if self.health < self.max_health / 2 else GREEN
            pygame.draw.rect(screen, health_bar_color, (
                int(self.x - health_bar_width // 2),
                int(self.y + self.size + 5),  # Move below the tank
                int(health_bar_width * health_percentage),
                health_bar_height
            ))
            pygame.draw.rect(screen, BLACK, (
                int(self.x - health_bar_width // 2),
                int(self.y + self.size + 5),  # Move below the tank
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

        # Update barrel recoil
        if self.barrel_recoil > 0:
            self.barrel_recoil = max(0, self.barrel_recoil - self.barrel_recoil_speed)

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
            bullet = Bullet(bullet_x, bullet_y, math.cos(self.angle) * bullet_speed,
                            math.sin(self.angle) * bullet_speed, 0)
            self.bullets.append(bullet)

            # Apply recoil
            recoil_force = 0.2
            self.recoil_velocity_x -= math.cos(self.angle) * recoil_force
            self.recoil_velocity_y -= math.sin(self.angle) * recoil_force

            # Apply barrel recoil
            self.barrel_recoil = self.max_barrel_recoil

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
            if isinstance(attacker, Shape):
                killer_object = attacker.shape_type.capitalize()
            else:
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
                if shape.shape_type == "pentagon":
                    for angle in range(0, 360, 30):
                        point_x = self.world_x + math.cos(math.radians(angle)) * self.size
                        point_y = self.world_y + math.sin(math.radians(angle)) * self.size
                        if shape.point_inside_polygon(point_x, point_y):
                            self.take_damage(5, shape)
                            shape.take_damage(5, self)  # Pass self (tank) here
                            angle = math.atan2(self.world_y - shape.world_y, self.world_x - shape.world_x)
                            self.world_x += math.cos(angle) * 5
                            self.world_y += math.sin(angle) * 5
                            break
                else:
                    distance = math.sqrt((self.world_x - shape.world_x) ** 2 + (self.world_y - shape.world_y) ** 2)
                    if distance < self.size + shape.size // 2:
                        self.take_damage(5, shape)
                        shape.take_damage(5, self)  # Pass self (tank) here
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
        self.radius = 15
        self.color = AQUA
        self.lifespan = 400
        self.damage = 25 - (tankNum*15)
        self.tankNum = tankNum  # 0 for player, 1 for enemy
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

    def check_collision(self, shapes, tank):
        for shape in shapes:
            if shape.alive:
                if shape.shape_type == "pentagon":
                    if shape.point_inside_polygon(self.world_x, self.world_y):
                        shape.take_damage(self.damage, tank)
                        return True
                else:
                    distance = math.sqrt((self.world_x - shape.world_x) ** 2 + (self.world_y - shape.world_y) ** 2)
                    if distance < self.radius + shape.size // 2:
                        shape.take_damage(self.damage, tank)
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

    def check_collision_with_bullets(self, other_bullets):
        for other_bullet in other_bullets:
            if self.tankNum != other_bullet.tankNum:  # Only check collision between different types of bullets
                distance = math.sqrt((self.world_x - other_bullet.world_x) ** 2 + (self.world_y - other_bullet.world_y) ** 2)
                if distance < self.radius + other_bullet.radius:
                    return other_bullet
        return None

    def create_collision_effect(self):
        return BulletCollisionEffect(self.world_x, self.world_y, self.color)

class BulletCollisionEffect:
    def __init__(self, x, y, color):
        self.world_x = x
        self.world_y = y
        self.color = color
        self.radius = 5
        self.max_radius = 30
        self.growth_rate = 2
        self.fade_rate = 10
        self.alpha = 255

    def update(self):
        self.radius = min(self.radius + self.growth_rate, self.max_radius)
        self.alpha = max(0, self.alpha - self.fade_rate)

    def draw(self, tank):
        screen_x = int(self.world_x - tank.world_x + tank.x)
        screen_y = int(self.world_y - tank.world_y + tank.y)

        if 0 <= screen_x < SCREEN_WIDTH and 0 <= screen_y < SCREEN_HEIGHT:
            surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(surface, (*self.color, self.alpha), (self.radius, self.radius), self.radius)
            screen.blit(surface, (screen_x - self.radius, screen_y - self.radius))

    def is_finished(self):
        return self.alpha <= 0

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
        self.points = []

        if shape_type == "square":
            self.size, self.health, self.max_health, self.color = 40, 100, 100, YELLOW
        elif shape_type == "triangle":
            self.size, self.health, self.max_health, self.color = 60, 200, 200, RED
        elif shape_type == "pentagon":
            self.size, self.health, self.max_health, self.color = 80, 300, 300, BLUE

        self.alive = True
        self.update_points()  # Initialize the points after setting the size

    def update(self):
        self.angle += self.rotation_speed * self.rotation_direction
        self.update_points()

    def update_points(self):
        self.points = []
        if self.shape_type == "pentagon":
            for i in range(5):
                angle = self.angle + (math.pi * 2 * i / 5)
                point_x = self.world_x + math.cos(angle) * self.size // 2
                point_y = self.world_y + math.sin(angle) * self.size // 2
                self.points.append((point_x, point_y))

    def draw(self, tank):
        if not self.alive:
            return

        screen_x = self.world_x - tank.world_x + tank.x
        screen_y = self.world_y - tank.world_y + tank.y

        if self.shape_type == "square":
            top_left_x = screen_x - self.size // 2
            top_left_y = screen_y - self.size // 2
            pygame.draw.rect(screen, self.color, (top_left_x, top_left_y, self.size, self.size))
        elif self.shape_type == "triangle":
            points = []
            for i in range(3):
                angle = self.angle + (math.pi * 2 * i / 3)
                point_x = screen_x + math.cos(angle) * self.size // 2
                point_y = screen_y + math.sin(angle) * self.size // 2
                points.append((point_x, point_y))
            pygame.draw.polygon(screen, self.color, points)
        elif self.shape_type == "pentagon":
            screen_points = [(x - tank.world_x + tank.x, y - tank.world_y + tank.y) for x, y in self.points]
            pygame.draw.polygon(screen, self.color, screen_points)

        # Draw health bar only if health is below max
        if self.health < self.max_health:
            health_bar_width = self.size
            health_bar_height = 5
            health_percentage = self.health / self.max_health
            health_bar_color = RED if self.health < self.max_health / 2 else GREEN
            pygame.draw.rect(screen, health_bar_color, (
                int(screen_x - health_bar_width // 2),
                int(screen_y + self.size // 2 + 5),  # Move below the shape
                int(health_bar_width * health_percentage),
                health_bar_height
            ))
            pygame.draw.rect(screen, BLACK, (
                int(screen_x - health_bar_width // 2),
                int(screen_y + self.size // 2 + 5),  # Move below the shape
                health_bar_width,
                health_bar_height
            ), 1)

    def point_inside_polygon(self, x, y):
        n = len(self.points)
        inside = False
        p1x, p1y = self.points[0]
        for i in range(n + 1):
            p2x, p2y = self.points[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        return inside

    def take_damage(self, damage, tank=None):
        self.health -= damage
        if self.health <= 0:
            if tank:  # Only increase score if tank is provided
                if self.shape_type == "square":
                    tank.score += 10
                elif self.shape_type == "triangle":
                    tank.score += 25
                elif self.shape_type == "pentagon":
                    tank.score += 130
            self.regenerate()

    def regenerate(self):
        # Move the shape to a new random location in the world
        self.world_x = random.randint(100, WORLD_WIDTH - 100)
        self.world_y = random.randint(100, WORLD_HEIGHT - 100)

        # Reset health
        self.health = self.max_health

        # Mark the shape as alive
        self.alive = True

def draw_score(screen, score):
    font = pygame.font.SysFont(None, 36)
    score_text = font.render(f"Score: {score}", True, BLACK)
    score_rect = score_text.get_rect()
    score_rect.topright = (SCREEN_WIDTH - 10, 10)
    screen.blit(score_text, score_rect)

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


def death_screen(screen, clock, killer_object, survival_time, final_score):
    transparent_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    transparent_surface.fill((100, 100, 100, 200))

    font_large = pygame.font.Font(None, 74)
    font_medium = pygame.font.Font(None, 48)
    font_small = pygame.font.Font(None, 36)

    death_text = font_large.render("YOU DIED", True, RED)
    death_rect = death_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 150))

    if killer_object == "Shape":
        killer_text = font_medium.render(f"Killed by: Unknown Shape", True, WHITE)
    elif killer_object in ["Pentagon", "Triangle", "Square"]:
        killer_text = font_medium.render(f"Killed by: {killer_object}", True, WHITE)
    else:
        killer_text = font_medium.render(f"Killed by: {killer_object}", True, WHITE)
    killer_rect = killer_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))

    time_text = font_medium.render(f"Survival time: {format_time(survival_time)}", True, WHITE)
    time_rect = time_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 25))

    score_text = font_medium.render(f"Final Score: {final_score}", True, WHITE)
    score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 75))

    button_width, button_height = 200, 50
    button_x = SCREEN_WIDTH // 2 - button_width // 2
    button_y = SCREEN_HEIGHT // 2 + 150
    button_rect = pygame.Rect(button_x, button_y, button_width, button_height)
    button_collision_rect = pygame.Rect(button_x, button_y+50, button_width, button_height)
    button_text = font_small.render("Continue", True, BLACK)
    button_text_rect = button_text.get_rect(center=button_rect.center)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    if button_rect.collidepoint(event.pos):
                        return

        screen.blit(transparent_surface, (0, 0))
        screen.blit(death_text, death_rect)
        screen.blit(killer_text, killer_rect)
        screen.blit(time_text, time_rect)
        screen.blit(score_text, score_rect)

        # Change button color when hovered
        mouse_pos = pygame.mouse.get_pos()
        if button_collision_rect.collidepoint(mouse_pos):
            button_color = (200, 200, 200)  # Light gray when hovered
        else:
            button_color = WHITE

        pygame.draw.rect(screen, button_color, button_rect)
        pygame.draw.rect(screen, BLACK, button_rect, 2)  # Button border
        screen.blit(button_text, button_text_rect)

        pygame.display.flip()
        clock.tick(60)


def draw_world_border(tank):
    screen_x = tank.x - tank.world_x
    screen_y = tank.y - tank.world_y
    if screen_y > 0:
        pygame.draw.rect(screen, GRAY, (0, 0, SCREEN_WIDTH+20, screen_y))
    if screen_y + WORLD_HEIGHT < SCREEN_HEIGHT:
        pygame.draw.rect(screen, GRAY,
                         (0, screen_y + WORLD_HEIGHT, SCREEN_WIDTH+20, SCREEN_HEIGHT - (screen_y + WORLD_HEIGHT)))
    if screen_x > 0: #left border
        pygame.draw.rect(screen, GRAY, (0, 0, screen_x, SCREEN_HEIGHT))
    if screen_x + WORLD_WIDTH < SCREEN_WIDTH: #right border
        pygame.draw.rect(screen, GRAY,
                         (screen_x + WORLD_WIDTH, 0, SCREEN_WIDTH - (screen_x + WORLD_WIDTH)+20, SCREEN_HEIGHT))

def draw_minimap(tank, shapes, enemies, mode):
    minimap_x = SCREEN_WIDTH - MINIMAP_WIDTH - 10
    minimap_y = SCREEN_HEIGHT - MINIMAP_HEIGHT - 10

    # Draw the minimap background
    pygame.draw.rect(screen, BLACK, (minimap_x, minimap_y, MINIMAP_WIDTH, MINIMAP_HEIGHT))
    pygame.draw.rect(screen, WHITE, (minimap_x, minimap_y, MINIMAP_WIDTH, MINIMAP_HEIGHT), 2)

    # Draw the player
    if mode >= 1:
        player_minimap_x = minimap_x + int(tank.world_x * MINIMAP_SCALE)
        player_minimap_y = minimap_y + int(tank.world_y * MINIMAP_SCALE)
        pygame.draw.circle(screen, WHITE, (player_minimap_x, player_minimap_y), 5)

    # Draw the shapes
    if mode in [3, 4]:
        for shape in shapes:
            if shape.alive:
                shape_minimap_x = minimap_x + int(shape.world_x * MINIMAP_SCALE)
                shape_minimap_y = minimap_y + int(shape.world_y * MINIMAP_SCALE)
                if shape.shape_type == "square":
                    pygame.draw.rect(screen, shape.color, (shape_minimap_x - 2, shape_minimap_y - 2, 4, 4))
                elif shape.shape_type == "triangle":
                    pygame.draw.polygon(screen, shape.color, [
                        (shape_minimap_x, shape_minimap_y - 3),
                        (shape_minimap_x - 3, shape_minimap_y + 3),
                        (shape_minimap_x + 3, shape_minimap_y + 3)
                    ])
                elif shape.shape_type == "pentagon":
                    pygame.draw.circle(screen, shape.color, (shape_minimap_x, shape_minimap_y), 3)

    # Draw the enemies
    if mode in [2, 4]:
        for enemy in enemies:
            if enemy.alive:
                enemy_minimap_x = minimap_x + int(enemy.world_x * MINIMAP_SCALE)
                enemy_minimap_y = minimap_y + int(enemy.world_y * MINIMAP_SCALE)
                pygame.draw.circle(screen, PINK, (enemy_minimap_x, enemy_minimap_y), 3)

def draw_minimap_indicator(mode):
    font = pygame.font.SysFont(None, 24)
    mode_names = ["OFF", "Player Only", "Player + Enemies", "Player + Shapes", "All"]
    indicator_text = f"Minimap: {mode_names[mode]}"
    text_surface = font.render(indicator_text, True, BLACK)

    indicator_x = SCREEN_WIDTH - 200
    indicator_y = SCREEN_HEIGHT - 230 if mode > 0 else SCREEN_HEIGHT - 20

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

    # Show menu and get player choice
    include_enemies = draw_menu(screen, clock)
    if include_enemies is None:  # Player closed the window
        return

    tank = Tank()
    shapes = initialize_shapes()
    enemies = initialize_enemies() if include_enemies else []
    running = True
    minimap_mode = 0  # Start with all elements visible
    game_over = False
    start_time = time.time()
    killer_object = ""
    collision_effects = []

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
                    minimap_mode = (minimap_mode + 1) % 5

        if not game_over:
            keys_pressed = pygame.key.get_pressed()
            tank.update(keys_pressed)
            tank.rotate_to_mouse(pygame.mouse.get_pos())
            tank.handle_autofire()

            for shape in shapes:
                shape.update()

            if include_enemies:
                for enemy in enemies[:]:
                    if enemy.alive:
                        enemy.update(tank, shapes)
                    else:
                        enemies.remove(enemy)

                tank.check_collision_with_enemies([enemy for enemy in enemies if enemy.alive])

            tank.check_collision_with_shapes(shapes)

            # Handle player bullets
            for bullet in tank.bullets[:]:
                bullet.update()
                if bullet.off_screen():
                    collision_effects.append(bullet.create_collision_effect())
                    tank.bullets.remove(bullet)
                elif bullet.check_collision(shapes, tank):  # Pass tank here
                    collision_effects.append(bullet.create_collision_effect())
                    tank.bullets.remove(bullet)
                elif include_enemies:
                    enemy_bullet = bullet.check_collision_with_bullets([b for e in enemies for b in e.bullets])
                    if enemy_bullet:
                        collision_effects.append(bullet.create_collision_effect())
                        collision_effects.append(enemy_bullet.create_collision_effect())
                        tank.bullets.remove(bullet)
                        for enemy in enemies:
                            if enemy_bullet in enemy.bullets:
                                enemy.bullets.remove(enemy_bullet)
                                break
                    elif bullet.check_collision_with_enemies([enemy for enemy in enemies if enemy.alive]):
                        collision_effects.append(bullet.create_collision_effect())
                        tank.bullets.remove(bullet)

            # Handle enemy bullets
            if include_enemies:
                for enemy in enemies:
                    if enemy.alive:
                        enemy.check_collision_with_enemies(enemies)
                        for bullet in enemy.bullets[:]:
                            bullet.update()
                            if bullet.off_screen():
                                collision_effects.append(bullet.create_collision_effect())
                                enemy.bullets.remove(bullet)
                            else:
                                player_bullet = bullet.check_collision_with_bullets(tank.bullets)
                                if player_bullet:
                                    collision_effects.append(bullet.create_collision_effect())
                                    collision_effects.append(player_bullet.create_collision_effect())
                                    enemy.bullets.remove(bullet)
                                    tank.bullets.remove(player_bullet)
                                elif bullet.check_collision_with_tank(tank):
                                    collision_effects.append(bullet.create_collision_effect())
                                    enemy.bullets.remove(bullet)

        # Drawing
        draw_grid(tank)
        draw_world_border(tank)
        draw_score(screen, tank.score)


        for shape in shapes:
            shape.draw(tank)

        if include_enemies:
            for enemy in enemies:
                if enemy.alive:
                    enemy.draw(tank)
                    for bullet in enemy.bullets:
                        bullet.draw(tank)

        for effect in collision_effects[:]:
            effect.update()
            effect.draw(tank)
            if effect.is_finished():
                collision_effects.remove(effect)

        tank.draw()
        for bullet in tank.bullets:
            bullet.draw(tank)

        if minimap_mode > 0:
            draw_minimap(tank, shapes, enemies, minimap_mode)

        draw_autofire_indicator(tank)
        draw_autospin_indicator(tank)
        draw_minimap_indicator(minimap_mode)

        pygame.display.flip()
        clock.tick(60)

        if game_over:
            survival_time = time.time() - start_time
            death_screen(screen, clock, killer_object, survival_time, tank.score)
            game_over = False
            tank.respawn()
            tank.score = 0  # Reset score on respawn
            start_time = time.time()

    pygame.quit()

# Main game execution
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Diep.io")
    clock = pygame.time.Clock()
    game_loop()
