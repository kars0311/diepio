import pygame
import math
import random
import time
import numpy as np

# Initialize pygame
pygame.init()

# Screen and world dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 1425, 900 #1440/780
WORLD_WIDTH, WORLD_HEIGHT = 5000, 5000
TILE_SIZE = 25

# Add these constants at the top of your file
UPGRADE_BUTTON_WIDTH = 150
UPGRADE_BUTTON_HEIGHT = 40
UPGRADE_BUTTON_MARGIN = 10

levels = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45])
scores = np.array([0, 4, 13, 28, 50, 78, 113, 157, 211, 275, 350, 437, 538, 655, 787, 938, 1109, 1301, 1516, 1757, 2026, 2325, 2658, 3026, 3433, 3883, 4379, 4925, 5525, 6184, 6907, 7698, 8537, 9426, 10368, 11367, 12426, 13549, 14739, 16000, 17337, 18754, 20256, 21849, 23536])

# Minimap visibility
minimap_visible = True  # Start with the minimap visible by default

# Minimap dimensions
MINIMAP_WIDTH = 200
MINIMAP_HEIGHT = 200
MINIMAP_SCALE = MINIMAP_WIDTH / WORLD_WIDTH

# Colors

DARK_GRAY = (170,170,170)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (241, 78, 85)
PINK = (255,150,150)
GREEN = (0, 255, 0)
AQUA = (0, 178, 225)
PENTAGONBLUE = (117, 141, 253)
SQUAREYELLOW = (255, 232, 105)
TRIANGLERED = (252,118,119)
CANNONGREY = (153, 153, 153)
HEALTHBARGREEN = (132, 227, 125)
SCREENGREY = (204, 204, 204)
GRIDLINEGREY = (193, 193, 193)
SCOREPROGRESSBARGREEN = (108, 240, 162)
CANNONOUTLINEGREY = (114, 114, 114)
HEALTHBAROUTLINE = (85, 85, 85)
SCOREBAROUTLINE = (61, 61, 61)

SQUAREOUTLINE = (191, 174, 78)
TRIANGLEOUTLINE = (189, 88, 89)
PENTAGONOUTLINE = (87, 106, 189)

ENEMYOUTLINE = (180, 58, 63)
TANKOUTLINE = (3, 133, 168)

OUTOFBOUNDSCREENGREY = (183, 183, 183)
OUTOFBOUNDSGRIDLINEGREY = (172, 172, 172)

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

# Superclass for Tank
class Tank:
    def __init__(self, x, y, size, speed, color):
        self.world_x = x
        self.world_y = y
        self.size = size
        self.speed = speed
        self.angle = 0
        self.color = color
        self.bullets = []
        self.shoot_cooldown = 0
        self.cannon_length = 75
        self.cannon_thickness = 30
        self.health = 500
        self.max_health = 500
        self.alive = True
        self.barrel_recoil = [0]
        self.max_barrel_recoil = 10
        self.barrel_recoil_speed = 1
        self.score = 500
        self.tank_type = "basic"
        self.recoil_velocity_x = 0
        self.recoil_velocity_y = 0
        self.recoil_dampening = 0.45
        self.max_recoil_speed = 2
        self.regen_rate = 0.1
        self.regen_cooldown = 0
        self.regen_cooldown_max = 180

    def draw(self, screen):
        if not self.alive:
            return

        screen_x = self.world_x - self.world_x + self.x
        screen_y = self.world_y - self.world_y + self.y

        if self.tank_type == "basic":
            self.draw_basic_cannon(screen, screen_x, screen_y)
        elif self.tank_type == "twin":
            self.draw_twin_cannons(screen, screen_x, screen_y)
        elif self.tank_type == "flank":
            self.draw_flank_cannons(screen, screen_x, screen_y)
        elif self.tank_type == "machine_gun":
            self.draw_machine_gun_cannon(screen, screen_x, screen_y)
        elif self.tank_type == "sniper":
            self.draw_sniper_cannon(screen, screen_x, screen_y)

        # Draw tank outline
        pygame.draw.circle(screen, TANKOUTLINE, (int(screen_x), int(screen_y)), self.size + 4)

        # Draw tank body
        pygame.draw.circle(screen, self.color, (int(screen_x), int(screen_y)), self.size)

        self.draw_health_bar(screen, screen_x, screen_y)

    def draw_health_bar(self, screen, screen_x, screen_y):
        if self.health < self.max_health:
            health_bar_width = self.size * 2
            health_bar_height = 5
            health_percentage = self.health / self.max_health
            health_bar_color = HEALTHBARGREEN
            pygame.draw.rect(screen, health_bar_color, (
                int(screen_x - health_bar_width // 2),
                int(screen_y + self.size + 5),
                int(health_bar_width * health_percentage),
                health_bar_height
            ))
            pygame.draw.rect(screen, HEALTHBAROUTLINE, (
                int(screen_x - health_bar_width // 2),
                int(screen_y + self.size + 5),
                health_bar_width,
                health_bar_height
            ), 1)

    def draw_cannon(self, screen, start_x, start_y, end_x, end_y):
        perpendicular_angle = math.atan2(end_y - start_y, end_x - start_x) + math.pi / 2
        half_thickness = self.cannon_thickness / 2
        outline_thickness = 3

        outline_offset_x = math.cos(perpendicular_angle) * (half_thickness + outline_thickness)
        outline_offset_y = math.sin(perpendicular_angle) * (half_thickness + outline_thickness)
        outline_corners = [
            (start_x + outline_offset_x, start_y + outline_offset_y),
            (start_x - outline_offset_x, start_y - outline_offset_y),
            (end_x - outline_offset_x, end_y - outline_offset_y),
            (end_x + outline_offset_x, end_y + outline_offset_y)
        ]

        pygame.draw.polygon(screen, CANNONOUTLINEGREY, outline_corners)

        corner_offset_x = math.cos(perpendicular_angle) * half_thickness
        corner_offset_y = math.sin(perpendicular_angle) * half_thickness
        cannon_corners = [
            (start_x + corner_offset_x, start_y + corner_offset_y),
            (start_x - corner_offset_x, start_y - corner_offset_y),
            (end_x - corner_offset_x, end_y - corner_offset_y),
            (end_x + corner_offset_x, end_y + corner_offset_y)
        ]

        pygame.draw.polygon(screen, CANNONGREY, cannon_corners)

        end_line_start = (end_x - outline_offset_x, end_y - outline_offset_y)
        end_line_end = (end_x + outline_offset_x, end_y + outline_offset_y)
        pygame.draw.line(screen, CANNONOUTLINEGREY, end_line_start, end_line_end, outline_thickness)

    def draw_basic_cannon(self, screen, screen_x, screen_y):
        recoil_adjusted_length = self.cannon_length - self.barrel_recoil[0]
        cannon_end_x = screen_x + math.cos(self.angle) * recoil_adjusted_length
        cannon_end_y = screen_y + math.sin(self.angle) * recoil_adjusted_length
        self.draw_cannon(screen, screen_x, screen_y, cannon_end_x, cannon_end_y)

    def draw_twin_cannons(self, screen, screen_x, screen_y):
        for i in [-1, 1]:
            recoil_adjusted_length = self.cannon_length - self.barrel_recoil[(i + 1) // 2]
            cannon_start_x = screen_x + i * math.cos(self.angle + math.pi / 2) * self.cannon_separation / 2
            cannon_start_y = screen_y + i * math.sin(self.angle + math.pi / 2) * self.cannon_separation / 2
            cannon_start_x -= math.cos(self.angle) * self.size * 0.1
            cannon_start_y -= math.sin(self.angle) * self.size * 0.1
            cannon_end_x = cannon_start_x + math.cos(self.angle) * recoil_adjusted_length
            cannon_end_y = cannon_start_y + math.sin(self.angle) * recoil_adjusted_length
            self.draw_cannon(screen, cannon_start_x, cannon_start_y, cannon_end_x, cannon_end_y)

    def draw_flank_cannons(self, screen, screen_x, screen_y):
        recoil_adjusted_length = self.front_cannon_length - self.barrel_recoil[0]
        front_cannon_end_x = screen_x + math.cos(self.angle) * recoil_adjusted_length
        front_cannon_end_y = screen_y + math.sin(self.angle) * recoil_adjusted_length
        self.draw_cannon(screen, screen_x, screen_y, front_cannon_end_x, front_cannon_end_y)

        back_angle = self.angle + math.pi
        recoil_adjusted_length = self.back_cannon_length - self.barrel_recoil[1]
        back_cannon_end_x = screen_x + math.cos(back_angle) * recoil_adjusted_length
        back_cannon_end_y = screen_y + math.sin(back_angle) * recoil_adjusted_length
        self.draw_cannon(screen, screen_x, screen_y, back_cannon_end_x, back_cannon_end_y)

    def draw_machine_gun_cannon(self, screen, screen_x, screen_y):
        recoil_adjusted_length = self.cannon_length - self.barrel_recoil[0]
        cannon_end_x = screen_x + math.cos(self.angle) * recoil_adjusted_length
        cannon_end_y = screen_y + math.sin(self.angle) * recoil_adjusted_length

        base_width = self.cannon_thickness * 0.75
        tip_width = self.cannon_thickness * 1

        perpendicular_angle = self.angle + math.pi / 2
        base_offset_x = math.cos(perpendicular_angle) * base_width / 2
        base_offset_y = math.sin(perpendicular_angle) * base_width / 2
        tip_offset_x = math.cos(perpendicular_angle) * tip_width / 2
        tip_offset_y = math.sin(perpendicular_angle) * tip_width / 2

        cannon_corners = [
            (screen_x + base_offset_x, screen_y + base_offset_y),
            (screen_x - base_offset_x, screen_y - base_offset_y),
            (cannon_end_x - tip_offset_x, cannon_end_y - tip_offset_y),
            (cannon_end_x + tip_offset_x, cannon_end_y + tip_offset_y)
        ]

        pygame.draw.polygon(screen, CANNONGREY, cannon_corners)

        outline_thickness = 3
        pygame.draw.lines(screen, CANNONOUTLINEGREY, True, cannon_corners, outline_thickness)

        end_line_start = (cannon_end_x - tip_offset_x, cannon_end_y - tip_offset_y)
        end_line_end = (cannon_end_x + tip_offset_x, cannon_end_y + tip_offset_y)
        pygame.draw.line(screen, CANNONOUTLINEGREY, end_line_start, end_line_end, outline_thickness)

    def draw_sniper_cannon(self, screen, screen_x, screen_y):
        recoil_adjusted_length = self.cannon_length - self.barrel_recoil[0]
        cannon_end_x = screen_x + math.cos(self.angle) * recoil_adjusted_length
        cannon_end_y = screen_y + math.sin(self.angle) * recoil_adjusted_length
        self.draw_cannon(screen, screen_x, screen_y, cannon_end_x, cannon_end_y)

    def create_bullet(self, x, y, angle):
        bullet_speed = 8
        if self.tank_type == "sniper":
            bullet_speed = 12
        bullet = Bullet(x, y, math.cos(angle) * bullet_speed, math.sin(angle) * bullet_speed, 1 if isinstance(self, Enemy) else 0)
        bullet.owner = self  # Set the owner reference
        self.bullets.append(bullet)

    def take_damage(self, damage, attacker=None):
        self.health -= damage
        if self.health <= 0:
            self.health = 0
            self.alive = False
        return self.alive

# Subclass for Enemy
class Enemy(Tank):
    enemy_count = 0  # Class variable to keep track of total enemies created
    def __init__(self, x, y):
        super().__init__(x, y, size=40, speed=3, color=RED)
        self.enemy_index = Enemy.enemy_count
        Enemy.enemy_count += 1
        self.target = None
        self.tank_type = random.choice(["basic", "twin", "flank", "machine_gun", "sniper"])
        self.individual_score = 500  # Initial score
        self.level = 1  # Add level tracking for enemies

        if self.tank_type == "twin":
            self.cannon_separation = self.size * 1.0
            self.cannon_length = 80
            self.next_cannon = 1
            self.barrel_recoil = [0, 0]
            self.twin_fire_mode = random.choice(["alternate", "simultaneous"])
        elif self.tank_type == "flank":
            self.front_cannon_length = 75
            self.back_cannon_length = 60
            self.barrel_recoil = [0, 0]
        elif self.tank_type == "machine_gun":
            self.cannon_length = 70
            self.cannon_thickness = 50
            self.barrel_recoil = [0]
            self.fire_rate = 5
        elif self.tank_type == "sniper":
            self.cannon_length = 90
            self.cannon_thickness = 30
            self.barrel_recoil = [0]
            self.fire_rate = 2

    def update_level(self):
        """Update enemy level based on score, just like player"""
        self.level = np.searchsorted(scores, self.individual_score, side='right')

    def regenerate(self, tank):
        while True:
            self.world_x = random.randint(50, WORLD_WIDTH - 50)
            self.world_y = random.randint(50, WORLD_HEIGHT - 50)
            distance = math.sqrt((self.world_x - tank.world_x) ** 2 + (self.world_y - tank.world_y) ** 2)
            if distance > 1000:
                break
        self.health = self.max_health
        self.alive = True

        # Update level before resetting score
        self.update_level()
        # Reset score to half of current level's score, just like player
        halfscore = scores[self.level // 2] if self.level > 1 else 500
        self.individual_score = halfscore

    def add_score(self, points):
        self.individual_score += points
        self.update_level()  # Update level when score changes

    def draw(self, tank):
        if not self.alive:
            return

        screen_x = self.world_x - tank.world_x + tank.x
        screen_y = self.world_y - tank.world_y + tank.y

        if self.tank_type == "basic":
            self.draw_basic_cannon(screen, screen_x, screen_y)
        elif self.tank_type == "twin":
            self.draw_twin_cannons(screen, screen_x, screen_y)
        elif self.tank_type == "flank":
            self.draw_flank_cannons(screen, screen_x, screen_y)
        elif self.tank_type == "machine_gun":
            self.draw_machine_gun_cannon(screen, screen_x, screen_y)
        elif self.tank_type == "sniper":
            self.draw_sniper_cannon(screen, screen_x, screen_y)

        # Draw enemy outline
        pygame.draw.circle(screen, ENEMYOUTLINE, (int(screen_x), int(screen_y)), self.size + 4)

        # Draw enemy body
        pygame.draw.circle(screen, self.color, (int(screen_x), int(screen_y)), self.size)

        self.draw_health_bar(screen, screen_x, screen_y)

    def update(self, tank, shapes):
        if not self.alive:
            return

        boundary_width = SCREEN_WIDTH * 1.5
        boundary_height = SCREEN_HEIGHT * 1.5
        in_boundary = (abs(self.world_x - tank.world_x) < boundary_width / 2 and
                       abs(self.world_y - tank.world_y) < boundary_height / 2)

        if in_boundary:
            self.target_player(tank)
        else:
            self.target_nearest_shape(shapes)

        if self.target:
            angle_to_target = math.atan2(self.target[1] - self.world_y, self.target[0] - self.world_x)
            self.world_x += math.cos(angle_to_target) * self.speed
            self.world_y += math.sin(angle_to_target) * self.speed
            self.angle = angle_to_target

        if self.shoot_cooldown <= 0 and self.target:
            self.shoot()
            if self.tank_type == "basic":
                self.shoot_cooldown = 25
            elif self.tank_type == "twin":
                if self.twin_fire_mode == "simultaneous":
                    self.shoot_cooldown = 20
                else:
                    self.shoot_cooldown = 10
            elif self.tank_type == "flank":
                self.shoot_cooldown = 25
            elif self.tank_type == "machine_gun":
                self.shoot_cooldown = 10
            elif self.tank_type == "sniper":
                self.shoot_cooldown = 30

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.off_screen():
                self.bullets.remove(bullet)

        for i in range(len(self.barrel_recoil)):
            if self.barrel_recoil[i] > 0:
                self.barrel_recoil[i] = max(0, self.barrel_recoil[i] - self.barrel_recoil_speed)

        self.check_collision_with_shapes(shapes, 1)

    def target_player(self, tank):
        self.target = (tank.world_x, tank.world_y)

    def target_nearest_shape(self, shapes):
        nearest_shape = None
        min_distance = float('inf')
        for shape in shapes:
            if shape.alive:
                distance = math.sqrt((self.world_x - shape.world_x) ** 2 + (self.world_y - shape.world_y) ** 2)
                if distance < min_distance:
                    min_distance = distance
                    nearest_shape = shape
        if nearest_shape:
            self.target = (nearest_shape.world_x, nearest_shape.world_y)
        else:
            self.target = None

    def shoot(self):
        if self.tank_type == "basic":
            self.shoot_basic()
        elif self.tank_type == "twin":
            self.shoot_twin()
        elif self.tank_type == "flank":
            self.shoot_flank()
        elif self.tank_type == "machine_gun":
            self.shoot_machine_gun()
        elif self.tank_type == "sniper":
            self.shoot_sniper()

    def shoot_basic(self):
        recoil_adjusted_length = self.cannon_length - self.barrel_recoil[0]
        bullet_x = self.world_x + math.cos(self.angle) * self.size
        bullet_y = self.world_y + math.sin(self.angle) * self.size
        self.create_bullet(bullet_x, bullet_y, self.angle)
        self.barrel_recoil[0] = self.max_barrel_recoil

    def shoot_twin(self):
        if self.twin_fire_mode == "alternate":
            self.shoot_twin_alternate()
        else:
            self.shoot_twin_simultaneous()

    def shoot_twin_alternate(self):
        i = 1 if self.next_cannon == 1 else -1
        recoil_adjusted_length = self.cannon_length - self.barrel_recoil[(i + 1) // 2]
        bullet_x = self.world_x + i * math.cos(self.angle + math.pi / 2) * self.cannon_separation / 2 + math.cos(
            self.angle) * self.size * 0.9
        bullet_y = self.world_y + i * math.sin(self.angle + math.pi / 2) * self.cannon_separation / 2 + math.sin(
            self.angle) * self.size * 0.9
        self.create_bullet(bullet_x, bullet_y, self.angle)
        self.barrel_recoil[(i + 1) // 2] = self.max_barrel_recoil
        self.next_cannon = 3 - self.next_cannon

    def shoot_twin_simultaneous(self):
        for i in [-1, 1]:
            recoil_adjusted_length = self.cannon_length - self.barrel_recoil[(i + 1) // 2]
            bullet_x = self.world_x + i * math.cos(
                self.angle + math.pi / 2) * self.cannon_separation / 2 + math.cos(self.angle) * self.size * 0.9
            bullet_y = self.world_y + i * math.sin(
                self.angle + math.pi / 2) * self.cannon_separation / 2 + math.sin(self.angle) * self.size * 0.9
            self.create_bullet(bullet_x, bullet_y, self.angle)
            self.barrel_recoil[(i + 1) // 2] = self.max_barrel_recoil

    def shoot_flank(self):
        front_bullet_x = self.world_x + math.cos(self.angle) * self.size
        front_bullet_y = self.world_y + math.sin(self.angle) * self.size
        self.create_bullet(front_bullet_x, front_bullet_y, self.angle)
        self.barrel_recoil[0] = self.max_barrel_recoil

        back_angle = self.angle + math.pi
        back_bullet_x = self.world_x + math.cos(back_angle) * self.size
        back_bullet_y = self.world_y + math.sin(back_angle) * self.size
        self.create_bullet(back_bullet_x, back_bullet_y, back_angle)
        self.barrel_recoil[1] = self.max_barrel_recoil

    def shoot_machine_gun(self):
        recoil_adjusted_length = self.cannon_length - self.barrel_recoil[0]
        spread = math.pi / 16
        for _ in range(self.fire_rate):
            angle = self.angle + random.uniform(-spread, spread)
            bullet_x = self.world_x + math.cos(angle) * self.size
            bullet_y = self.world_y + math.sin(angle) * self.size
        self.create_bullet(bullet_x, bullet_y, angle)
        self.barrel_recoil[0] = self.max_barrel_recoil

    def shoot_sniper(self):
        front_bullet_x = self.world_x + math.cos(self.angle) * self.size
        front_bullet_y = self.world_y + math.sin(self.angle) * self.size
        self.create_bullet(front_bullet_x, front_bullet_y, self.angle)
        self.barrel_recoil[0] = self.max_barrel_recoil

    def take_damage(self, damage, tank):
        super().take_damage(damage)
        if self.health <= 0:
            if isinstance(tank, Player):
                # Give score based on this enemy's individual score
                if self.individual_score < 23536:
                    tank.add_score(self.individual_score)
                else:
                    tank.add_score(23536)
            self.regenerate(tank)
        return self.alive

    def check_collision_with_enemies(self, enemies):
        for enemy in enemies:
            if enemy != self:
                distance = math.sqrt((self.world_x - enemy.world_x) ** 2 + (self.world_y - enemy.world_y) ** 2)
                if distance < self.size + enemy.size:
                    angle = math.atan2(self.world_y - enemy.world_y, self.world_x - enemy.world_x)
                    push_distance = (self.size + enemy.size) - distance
                    self.world_x += math.cos(angle) * push_distance / 2
                    self.world_y += math.sin(angle) * push_distance / 2
                    enemy.world_x -= math.cos(angle) * push_distance / 2
                    enemy.world_y -= math.sin(angle) * push_distance / 2

    def check_collision_with_shapes(self, shapes, tankNum):
        for shape in shapes:
            if shape.alive:
                if shape.shape_type == "pentagon":
                    for angle in range(0, 360, 30):
                        point_x = self.world_x + math.cos(math.radians(angle)) * self.size
                        point_y = self.world_y + math.sin(math.radians(angle)) * self.size
                        if shape.point_inside_polygon(point_x, point_y):
                            self.take_damage(5, shape)
                            shape.take_damage(5, tankNum)
                            angle = math.atan2(self.world_y - shape.world_y, self.world_x - shape.world_x)
                            self.world_x += math.cos(angle) * 5
                            self.world_y += math.sin(angle) * 5
                            break
                else:
                    distance = math.sqrt((self.world_x - shape.world_x) ** 2 + (self.world_y - shape.world_y) ** 2)
                    if distance < self.size + shape.size // 2:
                        self.take_damage(5, shape)
                        shape.take_damage(5, self)  # Pass the enemy instance instead of tankNum
                        angle = math.atan2(self.world_y - shape.world_y, self.world_x - shape.world_x)
                        push_distance = (self.size + shape.size // 2) - distance
                        self.world_x += math.cos(angle) * push_distance / 2
                        self.world_y += math.sin(angle) * push_distance / 2
                        shape.world_x -= math.cos(angle) * push_distance / 2
                        shape.world_y -= math.sin(angle) * push_distance / 2

# Subclass for Player
class Player(Tank):
    def __init__(self):
        super().__init__(WORLD_WIDTH // 2, WORLD_HEIGHT // 2, size=40, speed=5, color=AQUA)
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT // 2
        self.autofire = False
        self.autospin = False
        self.recoil_velocity_x = 0
        self.recoil_velocity_y = 0
        self.recoil_dampening = 0.45
        self.max_recoil_speed = 2
        self.regen_rate = 0.1
        self.regen_cooldown = 0
        self.regen_cooldown_max = 180
        self.level = 1
        self.score = 0
        self.upgrade_available = False

    def upgrade_to_twin(self):
        self.tank_type = "twin"
        self.cannon_separation = self.size * 1.0
        self.cannon_length = 80
        self.next_cannon = 1
        self.barrel_recoil = [0, 0]
        self.twin_fire_mode = "alternate"
        self.upgrade_available = False

    def upgrade_to_machine_gun(self):
        self.tank_type = "machine_gun"
        self.cannon_length = 70
        self.cannon_thickness = 50
        self.barrel_recoil = [0]
        self.fire_rate = 5
        self.upgrade_available = False

    def upgrade_to_flank_guard(self):
        self.tank_type = "flank"
        self.front_cannon_length = 75
        self.back_cannon_length = 60
        self.barrel_recoil = [0, 0]
        self.upgrade_available = False

    def upgrade_to_sniper(self):
        self.tank_type = "sniper"
        self.cannon_length = 90
        self.barrel_recoil = [0]
        self.fire_rate = 1
        self.upgrade_available = False

    def update_level(self):
        previous_level = self.level
        self.level = np.searchsorted(scores, self.score, side='right')

    def level_up(self):
        if self.level < 45:
            self.level += 1
            self.score = scores[self.level - 1]

    def get_progress_to_next_level(self):
        if self.level >= len(levels):
            return 1.0
        if self.level == len(levels) - 1:
            current_level_score = scores[self.level - 1]
            next_level_score = scores[self.level]
        else:
            current_level_score = scores[self.level - 1]
            next_level_score = scores[self.level]

        progress = (self.score - current_level_score) / (next_level_score - current_level_score)
        return min(max(progress, 0), 1)

    def update(self, keys_pressed):
        move_x, move_y = 0, 0
        if keys_pressed[pygame.K_w]: move_y = -1
        if keys_pressed[pygame.K_s]: move_y = 1
        if keys_pressed[pygame.K_a]: move_x = -1
        if keys_pressed[pygame.K_d]: move_x = 1

        if move_x != 0 or move_y != 0:
            magnitude = math.sqrt(move_x ** 2 + move_y ** 2)
            move_x, move_y = move_x / magnitude, move_y / magnitude
        move_x += self.recoil_velocity_x
        move_y += self.recoil_velocity_y

        self.world_x = max(self.size, min(WORLD_WIDTH - self.size, self.world_x + move_x * self.speed))
        self.world_y = max(self.size, min(WORLD_HEIGHT - self.size, self.world_y + move_y * self.speed))

        self.recoil_velocity_x *= self.recoil_dampening
        self.recoil_velocity_y *= self.recoil_dampening

        recoil_speed = math.sqrt(self.recoil_velocity_x ** 2 + self.recoil_velocity_y ** 2)
        if recoil_speed > self.max_recoil_speed:
            factor = self.max_recoil_speed / recoil_speed
            self.recoil_velocity_x *= factor
            self.recoil_velocity_y *= factor

        if self.health < self.max_health:
            if self.regen_cooldown > 0:
                self.regen_cooldown -= 1
            else:
                self.health = min(self.max_health, self.health + self.regen_rate)

        for i in range(len(self.barrel_recoil)):
            if self.barrel_recoil[i] > 0:
                self.barrel_recoil[i] = max(0, self.barrel_recoil[i] - self.barrel_recoil_speed)

    def rotate_to_mouse(self, mouse_pos):
        if self.autospin:
            self.angle += 0.05
        else:
            dx, dy = mouse_pos[0] - self.x, mouse_pos[1] - self.y
            self.angle = math.atan2(dy, dx)

    def shoot(self):
        if self.shoot_cooldown <= 0:
            if self.tank_type == "basic":
                self.shoot_basic()
                self.shoot_cooldown = 15
            elif self.tank_type == "twin":
                self.shoot_twin()
                self.shoot_cooldown = 7.5
            elif self.tank_type == "flank":
                self.shoot_flank()
                self.shoot_cooldown = 15
            elif self.tank_type == "machine_gun":
                self.shoot_machine_gun()
                self.shoot_cooldown = 7.5
            elif self.tank_type == "sniper":
                self.shoot_sniper()
                self.shoot_cooldown = 30

            recoil_force = 0.2
            self.recoil_velocity_x -= math.cos(self.angle) * recoil_force
            self.recoil_velocity_y -= math.sin(self.angle) * recoil_force

    def shoot_basic(self):
        bullet_x = self.world_x + math.cos(self.angle) * self.size
        bullet_y = self.world_y + math.sin(self.angle) * self.size
        self.create_bullet(bullet_x, bullet_y, self.angle)
        self.barrel_recoil[0] = self.max_barrel_recoil

    def shoot_twin(self):
        if self.twin_fire_mode == "alternate":
            self.shoot_twin_alternate()
        else:
            self.shoot_twin_simultaneous()

    def shoot_twin_alternate(self):
        i = 1 if self.next_cannon == 1 else -1
        recoil_adjusted_length = self.cannon_length - self.barrel_recoil[(i + 1) // 2]
        bullet_x = self.world_x + i * math.cos(self.angle + math.pi / 2) * self.cannon_separation / 2 + math.cos(
            self.angle) * self.size * 0.9
        bullet_y = self.world_y + i * math.sin(self.angle + math.pi / 2) * self.cannon_separation / 2 + math.sin(
            self.angle) * self.size * 0.9
        self.create_bullet(bullet_x, bullet_y, self.angle)
        self.barrel_recoil[(i + 1) // 2] = self.max_barrel_recoil
        self.next_cannon = 3 - self.next_cannon

    def shoot_twin_simultaneous(self):
        for i in [-1, 1]:
            recoil_adjusted_length = self.cannon_length - self.barrel_recoil[(i + 1) // 2]
            bullet_x = self.world_x + i * math.cos(self.angle + math.pi / 2) * self.cannon_separation / 2 + math.cos(
                self.angle) * self.size * 0.9
            bullet_y = self.world_y + i * math.sin(self.angle + math.pi / 2) * self.cannon_separation / 2 + math.sin(
                self.angle) * self.size * 0.9
            self.create_bullet(bullet_x, bullet_y, self.angle)
            self.barrel_recoil[(i + 1) // 2] = self.max_barrel_recoil

    def shoot_flank(self):
        front_bullet_x = self.world_x + math.cos(self.angle) * self.size
        front_bullet_y = self.world_y + math.sin(self.angle) * self.size
        self.create_bullet(front_bullet_x, front_bullet_y, self.angle)
        self.barrel_recoil[0] = self.max_barrel_recoil

        back_angle = self.angle + math.pi
        back_bullet_x = self.world_x + math.cos(back_angle) * self.size
        back_bullet_y = self.world_y + math.sin(back_angle) * self.size
        self.create_bullet(back_bullet_x, back_bullet_y, back_angle)
        self.barrel_recoil[1] = self.max_barrel_recoil

    def shoot_machine_gun(self):
        recoil_adjusted_length = self.cannon_length - self.barrel_recoil[0]
        spread = math.pi / 16
        for _ in range(self.fire_rate):
            angle = self.angle + random.uniform(-spread, spread)
            bullet_x = self.world_x + math.cos(angle) * self.size
            bullet_y = self.world_y + math.sin(angle) * self.size
        self.create_bullet(bullet_x, bullet_y, angle)
        self.barrel_recoil[0] = self.max_barrel_recoil

    def shoot_sniper(self):
        bullet_x = self.world_x + math.cos(self.angle) * self.size
        bullet_y = self.world_y + math.sin(self.angle) * self.size
        self.create_bullet(bullet_x, bullet_y, self.angle)
        self.barrel_recoil[0] = self.max_barrel_recoil

    def handle_autofire(self):
        if self.autofire and self.shoot_cooldown <= 0:
            self.shoot()
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def take_damage(self, damage, attacker=None):
        super().take_damage(damage)
        if self.health <= 0:
            self.health = 0
            self.tank_type = "basic"
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
                enemy.take_damage(5, self)
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

    def add_score(self, points):
        self.score += points
        self.update_level()

    def check_collision_with_shapes(self, shapes, tankNum):
        for shape in shapes:
            if shape.alive:
                if shape.shape_type == "pentagon":
                    for angle in range(0, 360, 30):
                        point_x = self.world_x + math.cos(math.radians(angle)) * self.size
                        point_y = self.world_y + math.sin(math.radians(angle)) * self.size
                        if shape.point_inside_polygon(point_x, point_y):
                            self.take_damage(5, shape)
                            shape.take_damage(5, tankNum)
                            angle = math.atan2(self.world_y - shape.world_y, self.world_x - shape.world_x)
                            self.world_x += math.cos(angle) * 5
                            self.world_y += math.sin(angle) * 5
                            break
                else:
                    distance = math.sqrt((self.world_x - shape.world_x) ** 2 + (self.world_y - shape.world_y) ** 2)
                    if distance < self.size + shape.size // 2:
                        self.take_damage(5, shape)
                        shape.take_damage(5, tankNum)
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
        self.lifespan = 200
        self.damage = 25 - (tankNum * 15)
        self.tankNum = tankNum  # 0 for player, 1 for enemy
        if tankNum == 0:
            self.color = AQUA
            self.bulletOutline = TANKOUTLINE
        if tankNum == 1:
            self.color = RED
            self.bulletOutline = ENEMYOUTLINE
        self.owner = None  # Store reference to the tank that fired this bullet

    def check_collision(self, shapes, attacker):
        for shape in shapes:
            if shape.alive:
                if shape.shape_type == "pentagon":
                    if shape.point_inside_polygon(self.world_x, self.world_y):
                        shape.take_damage(self.damage, attacker)
                        return True
                else:
                    distance = math.sqrt((self.world_x - shape.world_x) ** 2 + (self.world_y - shape.world_y) ** 2)
                    if distance < self.radius + shape.size // 2:
                        shape.take_damage(self.damage, attacker)
                        return True
        return False

    def update(self):
        self.world_x += self.vel_x
        self.world_y += self.vel_y
        self.lifespan -= 1

        self.world_x = max(self.radius, min(WORLD_WIDTH - self.radius, self.world_x))
        self.world_y = max(self.radius, min(WORLD_HEIGHT - self.radius, self.world_y))

    def draw(self, tank):
        screen_x = int(self.world_x - tank.world_x + tank.x)
        screen_y = int(self.world_y - tank.world_y + tank.y)

        if 0 <= screen_x < SCREEN_WIDTH and 0 <= screen_y < SCREEN_HEIGHT:
            pygame.draw.circle(screen, self.bulletOutline, (screen_x, screen_y), self.radius + 4)
            pygame.draw.circle(screen, self.color, (screen_x, screen_y), self.radius)

    def off_screen(self):
        return (self.world_x < self.radius or self.world_x > WORLD_WIDTH - self.radius or
                self.world_y < self.radius or self.world_y > WORLD_HEIGHT - self.radius or
                self.lifespan <= 0)

    def check_collision_with_enemies(self, enemies, tank):
        for enemy in enemies:
            distance = math.sqrt((self.world_x - enemy.world_x) ** 2 + (self.world_y - enemy.world_y) ** 2)
            if distance < self.radius + enemy.size:
                enemy.take_damage(self.damage, tank)
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
            if self.tankNum != other_bullet.tankNum:
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
    Enemy.enemy_count = 0  # Reset the enemy count before creating new enemies
    enemies = []
    for _ in range(5):
        x = random.randint(100, WORLD_WIDTH - 100)
        y = random.randint(100, WORLD_HEIGHT - 100)
        enemies.append(Enemy(x, y))
    return enemies

class Shape:
    def __init__(self, x, y, shape_type, tank, outline_thickness=4):
        self.world_x = x
        self.world_y = y
        self.shape_type = shape_type
        self.angle = 0
        self.rotation_speed = random.uniform(0.01, 0.03)
        self.rotation_direction = random.choice([-1, 1])
        self.points = []
        self.outline_thickness = outline_thickness
        self.tank = tank

        if shape_type == "square":
            self.size, self.health, self.max_health, self.color, self.outline_color = 40, 100, 100, SQUAREYELLOW, SQUAREOUTLINE
        elif shape_type == "triangle":
            self.size, self.health, self.max_health, self.color, self.outline_color = 60, 200, 200, TRIANGLERED, TRIANGLEOUTLINE
        elif shape_type == "pentagon":
            self.size, self.health, self.max_health, self.color, self.outline_color = 80, 300, 300, PENTAGONBLUE, PENTAGONOUTLINE

        self.alive = True
        self.update_points()

        # Attributes for circular movement
        self.orbit_radius = random.randint(25, 50)
        self.orbit_speed = random.uniform(0.005, 0.02)
        self.orbit_angle = random.uniform(0, 2 * math.pi)
        self.center_x = x
        self.center_y = y

    def take_damage(self, damage, attacker):
        self.health -= damage
        if self.health <= 0:
            if isinstance(attacker, Player):
                # Player destroyed the shape
                if self.shape_type == "square":
                    attacker.add_score(10)
                elif self.shape_type == "triangle":
                    attacker.add_score(25)
                elif self.shape_type == "pentagon":
                    attacker.add_score(130)
            elif isinstance(attacker, Enemy):
                # Enemy destroyed the shape
                if self.shape_type == "square":
                    attacker.add_score(10)
                elif self.shape_type == "triangle":
                    attacker.add_score(25)
                elif self.shape_type == "pentagon":
                    attacker.add_score(130)
            self.regenerate()

    def regenerate(self):
        self.world_x = random.randint(100, WORLD_WIDTH - 100)
        self.world_y = random.randint(100, WORLD_HEIGHT - 100)
        self.center_x = self.world_x
        self.center_y = self.world_y
        self.health = self.max_health
        self.alive = True
        self.orbit_angle = random.uniform(0, 2 * math.pi)

    def update(self, shapes):
        if not self.alive:
            return

        # Update rotation
        self.angle += self.rotation_speed * self.rotation_direction

        # Update circular movement
        self.orbit_angle += self.orbit_speed
        self.world_x = self.center_x + math.cos(self.orbit_angle) * self.orbit_radius
        self.world_y = self.center_y + math.sin(self.orbit_angle) * self.orbit_radius

        self.update_points()

        # Keep shapes within the world bounds
        self.world_x = max(self.size, min(WORLD_WIDTH - self.size, self.world_x))
        self.world_y = max(self.size, min(WORLD_HEIGHT - self.size, self.world_y))

        # Check for collisions with other shapes
        for other in shapes:
            if other != self and other.alive:
                if self.check_collision(other):
                    self.resolve_collision(other)

    def update_points(self):
        self.points = []
        num_points = 5 if self.shape_type == "pentagon" else 4 if self.shape_type == "square" else 3
        for i in range(num_points):
            angle = self.angle + (math.pi * 2 * i / num_points)
            point_x = self.world_x + math.cos(angle) * self.size // 2
            point_y = self.world_y + math.sin(angle) * self.size // 2
            self.points.append((point_x, point_y))

    def check_collision(self, other):
        distance = math.sqrt((self.world_x - other.world_x) ** 2 + (self.world_y - other.world_y) ** 2)
        return distance < (self.size + other.size) / 2

    def resolve_collision(self, other):
        # Calculate collision normal
        nx = other.world_x - self.world_x
        ny = other.world_y - self.world_y
        d = math.sqrt(nx * nx + ny * ny)
        nx /= d
        ny /= d

        # Move shapes apart to prevent sticking
        overlap = (self.size + other.size) / 2 - d
        self.world_x -= overlap * nx / 2
        self.world_y -= overlap * ny / 2
        other.world_x += overlap * nx / 2
        other.world_y += overlap * ny / 2

        # Adjust orbit centers after collision
        self.center_x = self.world_x - math.cos(self.orbit_angle) * self.orbit_radius
        self.center_y = self.world_y - math.sin(self.orbit_angle) * self.orbit_radius
        other.center_x = other.world_x - math.cos(other.orbit_angle) * other.orbit_radius
        other.center_y = other.world_y - math.sin(other.orbit_angle) * other.orbit_radius

    def point_inside_polygon(self, x, y):
        if self.shape_type != "pentagon":
            return False  # Only pentagons use this method

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

    def draw(self, tank):
        if not self.alive:
            return

        screen_x = self.world_x - tank.world_x + tank.x
        screen_y = self.world_y - tank.world_y + tank.y

        screen_points = [(x - tank.world_x + tank.x, y - tank.world_y + tank.y) for x, y in self.points]

        # Draw the filled shape
        pygame.draw.polygon(screen, self.color, screen_points)

        # Draw the outline with adjustable thickness
        pygame.draw.polygon(screen, self.outline_color, screen_points, self.outline_thickness)

        # Draw health bar only if health is below max
        if self.health < self.max_health:
            health_bar_width = self.size
            health_bar_height = 5
            health_percentage = self.health / self.max_health
            health_bar_color = HEALTHBARGREEN
            pygame.draw.rect(screen, health_bar_color, (
                int(screen_x - health_bar_width // 2),
                int(screen_y + self.size // 2 + 5),
                int(health_bar_width * health_percentage),
                health_bar_height
            ))
            pygame.draw.rect(screen, HEALTHBAROUTLINE, (
                int(screen_x - health_bar_width // 2),
                int(screen_y + self.size // 2 + 5),
                health_bar_width,
                health_bar_height
            ), 1)

def draw_upgrade_buttons(screen, tank):
    if tank.level >= 15 and tank.tank_type == "basic":
        font = pygame.font.SysFont(None, 24)
        button_y = UPGRADE_BUTTON_MARGIN

        for upgrade_type in ["Twin", "Machine Gun", "Flank Guard", "Sniper"]:
            button_rect = pygame.Rect(UPGRADE_BUTTON_MARGIN, button_y, UPGRADE_BUTTON_WIDTH, UPGRADE_BUTTON_HEIGHT)
            pygame.draw.rect(screen, WHITE, button_rect)
            pygame.draw.rect(screen, BLACK, button_rect, 2)

            text = font.render(upgrade_type, True, BLACK)
            text_rect = text.get_rect(center=button_rect.center)
            screen.blit(text, text_rect)

            button_y += UPGRADE_BUTTON_HEIGHT + UPGRADE_BUTTON_MARGIN

def handle_upgrade_click(tank, mouse_pos):
    if tank.level >= 15 and tank.tank_type == "basic":
        button_y = UPGRADE_BUTTON_MARGIN
        for upgrade_type in ["Twin", "Machine Gun", "Flank Guard", "Sniper"]:
            button_rect = pygame.Rect(UPGRADE_BUTTON_MARGIN, button_y, UPGRADE_BUTTON_WIDTH, UPGRADE_BUTTON_HEIGHT)
            if button_rect.collidepoint(mouse_pos):
                if upgrade_type == "Twin":
                    tank.upgrade_to_twin()
                elif upgrade_type == "Machine Gun":
                    tank.upgrade_to_machine_gun()
                elif upgrade_type == "Flank Guard":
                    tank.upgrade_to_flank_guard()
                elif upgrade_type == "Sniper":
                    tank.upgrade_to_sniper()
                return True
            button_y += UPGRADE_BUTTON_HEIGHT + UPGRADE_BUTTON_MARGIN
    return False

def draw_score(screen, score):
    font = pygame.font.SysFont(None, 36)
    score_text = font.render(f"Score: {score}", True, BLACK)
    score_rect = score_text.get_rect()
    score_rect.topright = (SCREEN_WIDTH - 10, 10)
    screen.blit(score_text, score_rect)

def draw_autofire_indicator(tank):
    font = pygame.font.SysFont(None, 24)
    autofire_text = "Autofire: ON" if tank.autofire else "Autofire: OFF"
    autofire_color = HEALTHBARGREEN if tank.autofire else RED
    text_surface = font.render(autofire_text, True, autofire_color)
    screen.blit(text_surface, (10, 10))

def draw_autospin_indicator(tank):
    font = pygame.font.SysFont(None, 24)
    autospin_text = "Autospin: ON" if tank.autospin else "Autospin: OFF"
    autospin_color = HEALTHBARGREEN if tank.autospin else RED
    text_surface = font.render(autospin_text, True, autospin_color)
    screen.blit(text_surface, (10, 40))

# Draw the grid-based terrain
def draw_grid(tank):
    cols = SCREEN_WIDTH // TILE_SIZE + 2  # Number of tiles needed to fill the width
    rows = SCREEN_HEIGHT // TILE_SIZE + 2  # Number of tiles needed to fill the height

    # Calculate the offset based on the player's world position and movement
    offset_x = (tank.world_x - tank.x) % TILE_SIZE
    offset_y = (tank.world_y - tank.y) % TILE_SIZE

    # Calculate the starting world coordinates of the visible area
    start_world_x = tank.world_x - tank.x
    start_world_y = tank.world_y - tank.y

    # Loop through rows and columns and draw tiles
    for row in range(rows):
        for col in range(cols):
            # Calculate tile position in screen coordinates
            tile_x = col * TILE_SIZE - offset_x
            tile_y = row * TILE_SIZE - offset_y

            # Calculate the world coordinates of this tile
            world_tile_x = start_world_x + col * TILE_SIZE
            world_tile_y = start_world_y + row * TILE_SIZE

            # Check if the tile is within the world bounds
            if (0 <= world_tile_x < WORLD_WIDTH and 0 <= world_tile_y < WORLD_HEIGHT):
                # Draw the normal grid tile
                pygame.draw.rect(screen, GRIDLINEGREY, (tile_x, tile_y, TILE_SIZE, TILE_SIZE), 1)
            else:
                # Fill the out-of-bounds tile
                pygame.draw.rect(screen, OUTOFBOUNDSCREENGREY, (tile_x, tile_y, TILE_SIZE, TILE_SIZE))
                # Draw the grid lines for out-of-bounds tiles
                pygame.draw.rect(screen, OUTOFBOUNDSGRIDLINEGREY, (tile_x, tile_y, TILE_SIZE, TILE_SIZE), 1)

def format_time(seconds):
    minutes, seconds = divmod(int(seconds), 60)
    return f"{minutes:02d}:{seconds:02d}"

def death_screen(screen, clock, killer_object, survival_time, final_score):
    transparent_surface = pygame.Surface((SCREEN_WIDTH+20, SCREEN_HEIGHT), pygame.SRCALPHA)
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
    button_collision_rect = pygame.Rect(button_x, button_y, button_width, button_height)
    button_text = font_small.render("Continue", True, BLACK)
    button_text_rect = button_text.get_rect(center=button_rect.center)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    if button_collision_rect.collidepoint(event.pos):
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

def initialize_shapes(tank):
    shapes = [
        Shape(1000, 1000, "square", tank),
        Shape(1200, 1200, "triangle", tank),
        Shape(1500, 1500, "pentagon", tank),
    ]
    for _ in range(50):
        shapes.append(Shape(random.randint(100, 4900), random.randint(100, 4900), "square", tank))
        shapes.append(Shape(random.randint(100, 4900), random.randint(100, 4900), "triangle", tank))
        shapes.append(Shape(random.randint(100, 4900), random.randint(100, 4900), "pentagon", tank))
    return shapes

def draw_level_info(screen, tank):
    font = pygame.font.SysFont(None, 36)
    level_text = font.render(f"Level: {tank.level}", True, BLACK)
    level_rect = level_text.get_rect()
    level_rect.bottomleft = (10, SCREEN_HEIGHT - 10)
    screen.blit(level_text, level_rect)

    # Draw progress bar
    progress = tank.get_progress_to_next_level()
    bar_width = 200
    bar_height = 20
    bar_x = level_rect.right + 20
    bar_y = SCREEN_HEIGHT - bar_height - 10

    # Background bar
    pygame.draw.rect(screen, SCOREBAROUTLINE, (bar_x, bar_y, bar_width, bar_height))
    # Progress bar
    pygame.draw.rect(screen, SCOREPROGRESSBARGREEN, (bar_x, bar_y, int(bar_width * progress), bar_height))
    # Border
    pygame.draw.rect(screen, BLACK, (bar_x, bar_y, bar_width, bar_height), 2)

    # Progress percentage
    progress_text = font.render(f"{progress:.0%}", True, BLACK)
    progress_rect = progress_text.get_rect()
    progress_rect.midleft = (bar_x + bar_width + 10, bar_y + bar_height // 2)
    screen.blit(progress_text, progress_rect)


def draw_leaderboard_tank(screen, x, y, tank_type, color, angle=0, scale=0.4):
    size = int(20 * scale)
    cannon_length = int(35 * scale)
    cannon_width = int(12 * scale)

    # Draw cannon(s) first, before the tank body
    if tank_type == "twin":
        offset = int(size * 0.3)
        for offset_y in [-offset, offset]:
            points = [
                (x - cannon_width // 2, y + offset_y),
                (x - cannon_width // 2, y + offset_y),
                (x + cannon_length, y + offset_y),
                (x + cannon_length, y + offset_y)
            ]
            pygame.draw.line(screen, CANNONOUTLINEGREY, (x, y + offset_y), (x + cannon_length, y + offset_y),
                             cannon_width + 2)
            pygame.draw.line(screen, CANNONGREY, (x, y + offset_y), (x + cannon_length, y + offset_y), cannon_width)
    elif tank_type == "flank":
        pygame.draw.line(screen, CANNONOUTLINEGREY, (x, y), (x + cannon_length, y), cannon_width + 2)
        pygame.draw.line(screen, CANNONGREY, (x, y), (x + cannon_length, y), cannon_width)
        pygame.draw.line(screen, CANNONOUTLINEGREY, (x, y), (x - cannon_length * 0.8, y), cannon_width + 2)
        pygame.draw.line(screen, CANNONGREY, (x, y), (x - cannon_length * 0.8, y), cannon_width)
    elif tank_type == "machine_gun":
        points = [
            (x - cannon_width // 2, y),
            (x + cannon_length, y - cannon_width),
            (x + cannon_length, y + cannon_width),
        ]
        pygame.draw.polygon(screen, CANNONOUTLINEGREY, points, 3)
        pygame.draw.polygon(screen, CANNONGREY, points)
    elif tank_type == "sniper":
        # REPLACE THESE TWO LINES
        pygame.draw.line(screen, CANNONOUTLINEGREY, (x, y), (x + cannon_length * 1.2, y), cannon_width - 2)
        pygame.draw.line(screen, CANNONGREY, (x, y), (x + cannon_length * 1.2, y), cannon_width - 4)
        # WITH THESE TWO LINES
        pygame.draw.line(screen, CANNONOUTLINEGREY, (x, y), (x + cannon_length * 1.2, y), cannon_width)
        pygame.draw.line(screen, CANNONGREY, (x, y), (x + cannon_length * 1.2, y), cannon_width - 2)
    else:  # basic tank
        pygame.draw.line(screen, CANNONOUTLINEGREY, (x, y), (x + cannon_length, y), cannon_width + 2)
        pygame.draw.line(screen, CANNONGREY, (x, y), (x + cannon_length, y), cannon_width)

    # Draw tank body and outline after the cannons
    outline_color = TANKOUTLINE if color == AQUA else ENEMYOUTLINE
    pygame.draw.circle(screen, outline_color, (x, y), size + 2)
    pygame.draw.circle(screen, color, (x, y), size)


def create_leaderboard_surface():
    # Constants for leaderboard
    LEADERBOARD_WIDTH = 250
    LEADERBOARD_HEIGHT = 300
    ENTRY_HEIGHT = 50
    PADDING = 10

    # Create static font objects
    font_title = pygame.font.SysFont(None, 36)
    font_entry = pygame.font.SysFont(None, 24)

    # Create the surface
    leaderboard_surface = pygame.Surface((LEADERBOARD_WIDTH, LEADERBOARD_HEIGHT), pygame.SRCALPHA)

    # Store important values in a dictionary for reuse
    return {
        'surface': leaderboard_surface,
        'width': LEADERBOARD_WIDTH,
        'height': LEADERBOARD_HEIGHT,
        'entry_height': ENTRY_HEIGHT,
        'padding': PADDING,
        'font_title': font_title,
        'font_entry': font_entry,
        'last_update': 0,
        'update_interval': 500,  # Update every 500ms
        'cached_scores': None
    }


def update_leaderboard_surface(leaderboard_info, player, enemies, current_time):
    # Check if it's time to update
    if (current_time - leaderboard_info['last_update'] < leaderboard_info['update_interval'] and
            leaderboard_info['cached_scores'] is not None):
        return False

    # Create list of all tanks and their scores
    scores_list = [{
        'score': player.score,
        'tank_type': player.tank_type,
        'color': player.color,
        'isPlayer': True
    }]

    scores_list.extend([{
        'score': enemy.individual_score,
        'tank_type': enemy.tank_type,
        'color': enemy.color,
        'isPlayer': False
    } for enemy in enemies if enemy.alive])

    # Sort by score
    scores_list.sort(key=lambda x: x['score'], reverse=True)

    # If scores haven't changed, don't update
    if scores_list == leaderboard_info['cached_scores']:
        return False

    leaderboard_info['cached_scores'] = scores_list
    leaderboard_info['last_update'] = current_time

    # Clear the surface
    leaderboard_info['surface'].fill((255, 255, 255, 180))

    # Draw title
    title_surface = leaderboard_info['font_title'].render("Leaderboard", True, BLACK)
    title_rect = title_surface.get_rect(
        centerx=leaderboard_info['width'] // 2,
        y=leaderboard_info['padding']
    )
    leaderboard_info['surface'].blit(title_surface, title_rect)

    # Draw entries
    for i, entry in enumerate(scores_list):
        y_pos = title_rect.height + leaderboard_info['padding'] * 2 + (i * leaderboard_info['entry_height'])

        # Draw rank
        rank_surface = leaderboard_info['font_entry'].render(f"#{i + 1}", True, BLACK)
        leaderboard_info['surface'].blit(rank_surface,
                                         (leaderboard_info['padding'], y_pos + leaderboard_info['entry_height'] // 4))

        # Draw tank
        tank_x = leaderboard_info['padding'] * 8
        tank_y = y_pos + leaderboard_info['entry_height'] // 2
        draw_leaderboard_tank(leaderboard_info['surface'], tank_x, tank_y,
                              entry['tank_type'], entry['color'])

        # Draw name
        name_surface = leaderboard_info['font_entry'].render(
            "You" if entry['isPlayer'] else "Enemy", True, BLACK)
        leaderboard_info['surface'].blit(name_surface,
                                         (leaderboard_info['padding'] * 14,
                                          y_pos + leaderboard_info['entry_height'] // 4))

        # Draw score
        score_surface = leaderboard_info['font_entry'].render(str(int(entry['score'])), True, BLACK)
        score_rect = score_surface.get_rect()
        score_rect.right = leaderboard_info['width'] - leaderboard_info['padding']
        score_rect.y = y_pos + leaderboard_info['entry_height'] // 4
        leaderboard_info['surface'].blit(score_surface, score_rect)

    return True


def draw_leaderboard(screen, leaderboard_info):
    # Position leaderboard in top right corner
    leaderboard_x = SCREEN_WIDTH - leaderboard_info['width'] - 10
    leaderboard_y = 40

    # Blit the pre-rendered surface
    screen.blit(leaderboard_info['surface'], (leaderboard_x, leaderboard_y))

def draw_leaderboard_indicator(visible):
    font = pygame.font.SysFont(None, 24)
    text = f"Leaderboard: {'ON' if visible else 'OFF'}"
    color = HEALTHBARGREEN if visible else RED
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, (10, 70))  # Position below autospin indicator

def game_loop():
    global game_over, killer_object

    include_enemies = draw_menu(screen, clock)
    if include_enemies is None:
        return

    player = Player()
    shapes = initialize_shapes(player)
    enemies = initialize_enemies() if include_enemies else []
    # Add this line right after creating enemies:
    leaderboard_info = create_leaderboard_surface()  # Add this line here
    running = True
    minimap_mode = 0
    leaderboard_visible = True  # Add this line
    game_over = False
    start_time = time.time()
    killer_object = ""
    collision_effects = []
    level_up_cooldown = 0
    level_up_cooldown_max = 15
    level_up_cooldown_min = 3
    level_up_hold_time = 0

    while running:
        screen.fill(SCREENGREY)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                if player.shoot_cooldown <= 0:
                    player.shoot()
                if event.button == 1:
                    if handle_upgrade_click(player, event.pos):
                        continue
                    if player.shoot_cooldown <= 0:
                        player.shoot()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    player.autofire = not player.autofire
                elif event.key == pygame.K_c:
                    player.autospin = not player.autospin
                elif event.key == pygame.K_o:
                    player.take_damage(player.health, "Self-Destruct")
                elif event.key == pygame.K_TAB:
                    minimap_mode = (minimap_mode + 1) % 5
                elif event.key == pygame.K_l:
                    leaderboard_visible = not leaderboard_visible

        keys = pygame.key.get_pressed()
        if keys[pygame.K_k]:
            if level_up_cooldown == 0:
                player.level_up()
                level_up_cooldown = max(level_up_cooldown_min,
                                        level_up_cooldown_max - level_up_hold_time // 2)
                level_up_hold_time += 1
            level_up_hold_time = min(level_up_hold_time + 1, 30)
        else:
            level_up_hold_time = 0

        if level_up_cooldown > 0:
            level_up_cooldown -= 1

        if not game_over:
            keys_pressed = pygame.key.get_pressed()
            player.update(keys_pressed)
            player.rotate_to_mouse(pygame.mouse.get_pos())
            player.handle_autofire()

            for shape in shapes:
                shape.update(shapes)

            if include_enemies:
                for enemy in enemies[:]:
                    if enemy.alive:
                        enemy.update(player, shapes)

                player.check_collision_with_enemies([enemy for enemy in enemies if enemy.alive])

            player.check_collision_with_shapes(shapes, 0)
            if include_enemies:
                for enemy in enemies:
                    if enemy.alive:
                        enemy.check_collision_with_shapes(shapes, 1)
            player.update_level()

            # Handle player bullets
            for bullet in player.bullets[:]:
                bullet.update()
                if bullet.off_screen():
                    collision_effects.append(bullet.create_collision_effect())
                    player.bullets.remove(bullet)
                elif bullet.check_collision(shapes, player):  # Pass player instance
                    collision_effects.append(bullet.create_collision_effect())
                    player.bullets.remove(bullet)
                elif include_enemies:
                    enemy_bullet = bullet.check_collision_with_bullets([b for e in enemies for b in e.bullets])
                    if enemy_bullet:
                        collision_effects.append(bullet.create_collision_effect())
                        collision_effects.append(enemy_bullet.create_collision_effect())
                        player.bullets.remove(bullet)
                        for enemy in enemies:
                            if enemy_bullet in enemy.bullets:
                                enemy.bullets.remove(enemy_bullet)
                                break
                    elif bullet.check_collision_with_enemies([enemy for enemy in enemies if enemy.alive], player):
                        collision_effects.append(bullet.create_collision_effect())
                        player.bullets.remove(bullet)

            # Handle enemy bullets
            if include_enemies:
                for enemy in enemies:
                    if enemy.alive:
                        for bullet in enemy.bullets[:]:
                            bullet.update()
                            if bullet.off_screen():
                                collision_effects.append(bullet.create_collision_effect())
                                enemy.bullets.remove(bullet)
                            elif bullet.check_collision(shapes, enemy):  # Pass enemy instance
                                collision_effects.append(bullet.create_collision_effect())
                                enemy.bullets.remove(bullet)
                            else:
                                player_bullet = bullet.check_collision_with_bullets(player.bullets)
                                if player_bullet:
                                    collision_effects.append(bullet.create_collision_effect())
                                    collision_effects.append(player_bullet.create_collision_effect())
                                    enemy.bullets.remove(bullet)
                                    player.bullets.remove(player_bullet)
                                elif bullet.check_collision_with_tank(player):
                                    collision_effects.append(bullet.create_collision_effect())
                                    enemy.bullets.remove(bullet)

        # Drawing
        draw_grid(player)
        draw_score(screen, player.score)
        draw_level_info(screen, player)

        for shape in shapes:
            shape.draw(player)

        if include_enemies:
            for enemy in enemies:
                if enemy.alive:
                    enemy.draw(player)
                    for bullet in enemy.bullets:
                        bullet.draw(player)

        for effect in collision_effects[:]:
            effect.update()
            effect.draw(player)
            if effect.is_finished():
                collision_effects.remove(effect)

        # In the drawing section of the game loop, add:
        player.draw(screen)
        for bullet in player.bullets:
            bullet.draw(player)

        draw_upgrade_buttons(screen, player)

        if minimap_mode > 0:
            draw_minimap(player, shapes, enemies, minimap_mode)
        draw_autofire_indicator(player)
        draw_autospin_indicator(player)

        draw_minimap_indicator(minimap_mode)

        # Add leaderboard drawing here
        if include_enemies and leaderboard_visible:
            update_leaderboard_surface(leaderboard_info, player, enemies, pygame.time.get_ticks())
            draw_leaderboard(screen, leaderboard_info)
        draw_leaderboard_indicator(leaderboard_visible)

        pygame.display.flip()
        clock.tick(60)

        if game_over:
            survival_time = time.time() - start_time
            death_screen(screen, clock, killer_object, survival_time, player.score)
            game_over = False
            halfscore = scores[player.level//2]
            player = Player()
            player.score=halfscore
            leaderboard_info = create_leaderboard_surface()  # Add this line here
            start_time = time.time()

    pygame.quit()

# Main game execution
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Diep.io")
    clock = pygame.time.Clock()
    game_loop()
