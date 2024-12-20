import pygame
import math
import random
import time
import numpy as np

# Initialize pygame
pygame.init()

# Screen and world dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 1425, 900  # 1440/780
WORLD_WIDTH, WORLD_HEIGHT = 5000, 5000
TILE_SIZE = 25
BASE_TANK_SIZE = TILE_SIZE * 1.6  # 40 pixels
BASE_BULLET_SIZE = TILE_SIZE * 0.6  # 15 pixels
BASE_SQUARE_SIZE = TILE_SIZE * 1.6  # 40 pixels
BASE_TRIANGLE_SIZE = TILE_SIZE * 2.4  # 60 pixels
BASE_PENTAGON_SIZE = TILE_SIZE * 3.2  # 80 pixels
NORMAL_ZOOM = 1.0
SNIPER_ZOOM = 0.85

# Add these constants at the top of your file
UPGRADE_BUTTON_WIDTH = 150
UPGRADE_BUTTON_HEIGHT = 40
UPGRADE_BUTTON_MARGIN = 10

# attribute constants
ATTRIBUTE_BAR_HEIGHT = 20
ATTRIBUTES_X = 10  # X position of attributes section
ATTRIBUTES_Y = SCREEN_HEIGHT - 250  # Y position of attributes section
ATTRIBUTE_BAR_WIDTH = 200  # Width of attribute progress bar
ATTRIBUTE_SECTION_HEIGHT = 25  # Height of each attribute section
PLUS_BUTTON_SIZE = 20  # Size of the plus button

levels = np.array(
    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31,
     32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45])
scores = np.array(
    [0, 4, 13, 28, 50, 78, 113, 157, 211, 275, 350, 437, 538, 655, 787, 938, 1109, 1301, 1516, 1757, 2026, 2325, 2658,
     3026, 3433, 3883, 4379, 4925, 5525, 6184, 6907, 7698, 8537, 9426, 10368, 11367, 12426, 13549, 14739, 16000, 17337,
     18754, 20256, 21849, 23536])

# Minimap visibility
minimap_visible = True  # Start with the minimap visible by default

# Minimap dimensions
MINIMAP_WIDTH = 200
MINIMAP_HEIGHT = 200
MINIMAP_SCALE = MINIMAP_WIDTH / WORLD_WIDTH

# Colors

DARK_GRAY = (170, 170, 170)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (241, 78, 85)
PINK = (255, 150, 150)
GREEN = (0, 255, 0)
AQUA = (0, 178, 225)
PENTAGONBLUE = (117, 141, 253)
SQUAREYELLOW = (255, 232, 105)
TRIANGLERED = (252, 118, 119)
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

# Add these constants at the top of the file, after the other constants
NORMAL_ZOOM = 1.0
SNIPER_ZOOM = 0.7  # This will make everything appear 30% smaller, effectively increasing FOV

# Create the screen object
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Diep.io")

# Clock object to control game speed
clock = pygame.time.Clock()


def is_on_screen(world_x, world_y, size, tank):
    """Helper function to check if an object is visible on screen"""
    # Calculate screen coordinates
    screen_x = (world_x - tank.world_x) * tank.zoom + tank.x
    screen_y = (world_y - tank.world_y) * tank.zoom + tank.y

    # Add padding equal to the object's size
    padding = size * tank.zoom

    # Check if object is within screen bounds (with padding)
    return (-padding <= screen_x <= SCREEN_WIDTH + padding and
            -padding <= screen_y <= SCREEN_HEIGHT + padding)


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
        self.base_size = BASE_TANK_SIZE
        self.size = self.base_size
        self.speed = speed
        self.angle = 0
        self.color = color
        self.bullets = []
        self.shoot_cooldown = 0
        self.cannon_length = TILE_SIZE * 3  # 75 pixels
        self.cannon_thickness = TILE_SIZE * 1.2  # 30 pixels
        self.health = 500
        self.max_health = 500
        self.alive = True
        self.barrel_recoil = [0]
        self.max_barrel_recoil = TILE_SIZE * 0.4  # 10 pixels
        self.barrel_recoil_speed = TILE_SIZE * 0.04  # 1 pixel
        self.score = 500
        self.tank_type = "basic"
        self.recoil_velocity_x = 0
        self.recoil_velocity_y = 0
        self.recoil_dampening = 0.45
        self.max_recoil_speed = TILE_SIZE * 0.08  # 2 pixels
        self.regen_rate = 0.1
        self.regen_cooldown = 0
        self.regen_cooldown_max = 180
        self.zoom = NORMAL_ZOOM
        self.auto_turret_recoil = 0  # Add this line for auto turret recoil

    def adjust_dimensions(self):
        """Adjust dimensions based on zoom level"""
        self.size = int(self.base_size * self.zoom)
        self.cannon_thickness = int(30 * self.zoom)
        if self.tank_type == "sniper":
            self.cannon_length = int(90 * self.zoom)
        elif self.tank_type == "machine_gun":
            self.cannon_length = int(70 * self.zoom)
        elif self.tank_type == "twin":
            self.cannon_length = int(80 * self.zoom)
            self.cannon_separation = int(self.base_size * 1.0 * self.zoom)
        elif self.tank_type == "flank":
            self.front_cannon_length = int(75 * self.zoom)
            self.back_cannon_length = int(60 * self.zoom)
        elif self.tank_type == "gunner":
            self.cannon_length = int(70 * self.zoom)
            self.cannon_thickness = int(10 * self.zoom)  # Thinner cannons
            self.cannon_separation = int(self.base_size * 0.3 * self.zoom)  # Space between cannons
        else:
            self.cannon_length = int(75 * self.zoom)

    def draw(self, screen):
        if not self.alive:
            return

        # Calculate screen position
        screen_x = (self.world_x - self.world_x + self.x)
        screen_y = (self.world_y - self.world_y + self.y)

        # Early return if tank is not visible
        if not is_on_screen(self.world_x, self.world_y, self.size + self.cannon_length, self):
            return

        # Scale sizes based on zoom
        drawn_size = int(self.size * self.zoom)
        drawn_cannon_length = int(self.cannon_length * self.zoom)
        drawn_cannon_thickness = int(self.cannon_thickness * self.zoom)

        if self.tank_type == "auto_quad":

            # 1. Draw quad tank cannons first

            base_angles = [0, math.pi / 2, math.pi, 3 * math.pi / 2]  # Right, Down, Left, Up

            for i, angle in enumerate(base_angles):
                actual_angle = angle + self.angle

                recoil_adjusted_length = drawn_cannon_length - (self.barrel_recoil[i] * self.zoom)

                cannon_end_x = screen_x + math.cos(actual_angle) * recoil_adjusted_length

                cannon_end_y = screen_y + math.sin(actual_angle) * recoil_adjusted_length

                # Draw main tank's cannons

                perpendicular_angle = actual_angle + math.pi / 2

                half_thickness = drawn_cannon_thickness / 2

                outline_thickness = max(1, int(3 * self.zoom))

                # Draw cannon outline

                outline_offset_x = math.cos(perpendicular_angle) * (half_thickness + outline_thickness)

                outline_offset_y = math.sin(perpendicular_angle) * (half_thickness + outline_thickness)

                outline_corners = [

                    (screen_x + outline_offset_x, screen_y + outline_offset_y),

                    (screen_x - outline_offset_x, screen_y - outline_offset_y),

                    (cannon_end_x - outline_offset_x, cannon_end_y - outline_offset_y),

                    (cannon_end_x + outline_offset_x, cannon_end_y + outline_offset_y)

                ]

                pygame.draw.polygon(screen, CANNONOUTLINEGREY, outline_corners)

                # Draw cannon fill

                corner_offset_x = math.cos(perpendicular_angle) * half_thickness

                corner_offset_y = math.sin(perpendicular_angle) * half_thickness

                cannon_corners = [

                    (screen_x + corner_offset_x, screen_y + corner_offset_y),

                    (screen_x - corner_offset_x, screen_y - corner_offset_y),

                    (cannon_end_x - corner_offset_x, cannon_end_y - corner_offset_y),

                    (cannon_end_x + corner_offset_x, cannon_end_y + corner_offset_y)

                ]

                pygame.draw.polygon(screen, CANNONGREY, cannon_corners)

                # Draw cannon end cap

                end_line_start = (cannon_end_x - outline_offset_x, cannon_end_y - outline_offset_y)

                end_line_end = (cannon_end_x + outline_offset_x, cannon_end_y + outline_offset_y)

                pygame.draw.line(screen, CANNONOUTLINEGREY, end_line_start, end_line_end, outline_thickness)

            # 2. Draw tank body and outline

            pygame.draw.circle(screen, TANKOUTLINE, (int(screen_x), int(screen_y)),

                               int(self.size * self.zoom) + int(4 * self.zoom))

            pygame.draw.circle(screen, self.color, (int(screen_x), int(screen_y)),

                               int(self.size * self.zoom))

            # 3. Draw auto turret cannon first

            turret_cannon_length = int(self.auto_turret_cannon_length * self.zoom)

            turret_cannon_width = int(self.auto_turret_cannon_width * self.zoom)

            recoil_adjusted_turret_length = turret_cannon_length - (self.auto_turret_recoil * self.zoom)

            cannon_start_x = int(screen_x)

            cannon_start_y = int(screen_y)

            cannon_end_x = cannon_start_x + int(math.cos(self.auto_turret_angle) * recoil_adjusted_turret_length)

            cannon_end_y = cannon_start_y + int(math.sin(self.auto_turret_angle) * recoil_adjusted_turret_length)

            perp_angle = self.auto_turret_angle + math.pi / 2

            half_width = turret_cannon_width / 2

            outline_width = int(2 * self.zoom)

            # Draw auto turret cannon outline

            perp_x = math.cos(perp_angle) * (half_width + outline_width)

            perp_y = math.sin(perp_angle) * (half_width + outline_width)

            outline_points = [

                (cannon_start_x + perp_x, cannon_start_y + perp_y),

                (cannon_start_x - perp_x, cannon_start_y - perp_y),

                (cannon_end_x - perp_x, cannon_end_y - perp_y),

                (cannon_end_x + perp_x, cannon_end_y + perp_y)

            ]

            pygame.draw.polygon(screen, CANNONOUTLINEGREY, outline_points)

            # Draw auto turret cannon fill

            perp_x = math.cos(perp_angle) * half_width

            perp_y = math.sin(perp_angle) * half_width

            cannon_points = [

                (cannon_start_x + perp_x, cannon_start_y + perp_y),

                (cannon_start_x - perp_x, cannon_start_y - perp_y),

                (cannon_end_x - perp_x, cannon_end_y - perp_y),

                (cannon_end_x + perp_x, cannon_end_y + perp_y)

            ]

            pygame.draw.polygon(screen, CANNONGREY, cannon_points)

            # Draw auto turret cannon end cap

            end_line_start = (cannon_end_x + math.cos(perp_angle) * half_width,

                              cannon_end_y + math.sin(perp_angle) * half_width)

            end_line_end = (cannon_end_x - math.cos(perp_angle) * half_width,

                            cannon_end_y - math.sin(perp_angle) * half_width)

            pygame.draw.line(screen, CANNONOUTLINEGREY, end_line_start, end_line_end, outline_width)

            # 4. Draw auto turret base last

            turret_size = int(self.auto_turret_size * self.zoom)

            pygame.draw.circle(screen, CANNONOUTLINEGREY, (int(screen_x), int(screen_y)),

                               turret_size + int(2 * self.zoom))

            pygame.draw.circle(screen, CANNONGREY, (int(screen_x), int(screen_y)), turret_size)

        elif self.tank_type == "auto_gunner":
            # 1. Draw gunner cannons first (bottom layer)
            cannon_configs = [
                (-3, False, 0.8),  # Top short cannon - thinner
                (-1.5, True, 1.3),  # Upper long cannon - normal thickness
                (1.5, True, 1.3),  # Lower long cannon - normal thickness
                (3, False, 0.8)  # Bottom short cannon - thinner
            ]

            for i, (pos, is_long, thickness_mult) in enumerate(cannon_configs):
                base_length = self.long_cannon_length if is_long else self.short_cannon_length
                drawn_base_length = int(base_length * self.zoom)
                recoil_adjusted_length = drawn_base_length - (self.barrel_recoil[i] * self.zoom)
                offset = pos * (self.cannon_separation * self.zoom)

                cannon_start_x = screen_x + math.cos(self.angle + math.pi / 2) * offset
                cannon_start_y = screen_y + math.sin(self.angle + math.pi / 2) * offset

                cannon_end_x = cannon_start_x + math.cos(self.angle) * recoil_adjusted_length
                cannon_end_y = cannon_start_y + math.sin(self.angle) * recoil_adjusted_length

                perpendicular_angle = self.angle + math.pi / 2
                outline_thickness = max(1, int(2 * self.zoom))
                current_thickness = drawn_cannon_thickness * thickness_mult

                outline_offset = current_thickness / 2 + outline_thickness
                outline_points = [
                    (cannon_start_x + math.cos(perpendicular_angle) * outline_offset,
                     cannon_start_y + math.sin(perpendicular_angle) * outline_offset),
                    (cannon_start_x - math.cos(perpendicular_angle) * outline_offset,
                     cannon_start_y - math.sin(perpendicular_angle) * outline_offset),
                    (cannon_end_x - math.cos(perpendicular_angle) * outline_offset,
                     cannon_end_y - math.sin(perpendicular_angle) * outline_offset),
                    (cannon_end_x + math.cos(perpendicular_angle) * outline_offset,
                     cannon_end_y + math.sin(perpendicular_angle) * outline_offset)
                ]

                pygame.draw.polygon(screen, CANNONOUTLINEGREY, outline_points)

                cannon_points = [
                    (cannon_start_x + math.cos(perpendicular_angle) * current_thickness / 2,
                     cannon_start_y + math.sin(perpendicular_angle) * current_thickness / 2),
                    (cannon_start_x - math.cos(perpendicular_angle) * current_thickness / 2,
                     cannon_start_y - math.sin(perpendicular_angle) * current_thickness / 2),
                    (cannon_end_x - math.cos(perpendicular_angle) * current_thickness / 2,
                     cannon_end_y - math.sin(perpendicular_angle) * current_thickness / 2),
                    (cannon_end_x + math.cos(perpendicular_angle) * current_thickness / 2,
                     cannon_end_y + math.sin(perpendicular_angle) * current_thickness / 2)
                ]

                pygame.draw.polygon(screen, CANNONGREY, cannon_points)

            # 2. Draw tank body and outline (middle layer)
            pygame.draw.circle(screen, TANKOUTLINE, (int(screen_x), int(screen_y)), drawn_size + int(4 * self.zoom))
            pygame.draw.circle(screen, self.color, (int(screen_x), int(screen_y)), drawn_size)

            # 3. Draw auto turret cannon (top layer)
            turret_cannon_length = int(self.auto_turret_cannon_length * self.zoom)
            turret_cannon_width = int(self.auto_turret_cannon_width * self.zoom)
            recoil_adjusted_turret_length = turret_cannon_length - (self.auto_turret_recoil * self.zoom)

            cannon_start_x = int(screen_x)
            cannon_start_y = int(screen_y)
            cannon_end_x = cannon_start_x + int(math.cos(self.auto_turret_angle) * recoil_adjusted_turret_length)
            cannon_end_y = cannon_start_y + int(math.sin(self.auto_turret_angle) * recoil_adjusted_turret_length)

            perp_angle = self.auto_turret_angle + math.pi / 2
            half_width = turret_cannon_width / 2
            outline_width = int(2 * self.zoom)

            perp_x = math.cos(perp_angle) * (half_width + outline_width)
            perp_y = math.sin(perp_angle) * (half_width + outline_width)

            outline_points = [
                (cannon_start_x + perp_x, cannon_start_y + perp_y),
                (cannon_start_x - perp_x, cannon_start_y - perp_y),
                (cannon_end_x - perp_x, cannon_end_y - perp_y),
                (cannon_end_x + perp_x, cannon_end_y + perp_y)
            ]
            pygame.draw.polygon(screen, CANNONOUTLINEGREY, outline_points)

            perp_x = math.cos(perp_angle) * half_width
            perp_y = math.sin(perp_angle) * half_width

            cannon_points = [
                (cannon_start_x + perp_x, cannon_start_y + perp_y),
                (cannon_start_x - perp_x, cannon_start_y - perp_y),
                (cannon_end_x - perp_x, cannon_end_y - perp_y),
                (cannon_end_x + perp_x, cannon_end_y + perp_y)
            ]
            pygame.draw.polygon(screen, CANNONGREY, cannon_points)

            # 4. Draw auto turret base on top of everything
            turret_size = int(self.auto_turret_size * self.zoom)
            pygame.draw.circle(screen, CANNONOUTLINEGREY, (int(screen_x), int(screen_y)),
                               turret_size + int(2 * self.zoom))
            pygame.draw.circle(screen, CANNONGREY, (int(screen_x), int(screen_y)), turret_size)
            # Add end cap outline
            end_line_start = (cannon_end_x - perp_x, cannon_end_y - perp_y)
            end_line_end = (cannon_end_x + perp_x, cannon_end_y + perp_y)
            pygame.draw.line(screen, CANNONOUTLINEGREY, end_line_start, end_line_end, outline_width)


        else:
            # Original tank type drawing code...
            if self.tank_type == "basic":
                self.draw_basic_cannon(screen, screen_x, screen_y, drawn_cannon_length, drawn_cannon_thickness)
            elif self.tank_type == "twin":
                self.draw_twin_cannons(screen, screen_x, screen_y, drawn_cannon_length, drawn_cannon_thickness)
            elif self.tank_type == "flank":
                self.draw_flank_cannons(screen, screen_x, screen_y, drawn_cannon_length, drawn_cannon_thickness)
            elif self.tank_type == "machine_gun":
                self.draw_machine_gun_cannon(screen, screen_x, screen_y, drawn_cannon_length, drawn_cannon_thickness)
            elif self.tank_type == "sniper":
                self.draw_sniper_cannon(screen, screen_x, screen_y, drawn_cannon_length, drawn_cannon_thickness)
            elif self.tank_type == "gunner":
                self.draw_gunner_cannons(screen, screen_x, screen_y, drawn_cannon_length, drawn_cannon_thickness)
            elif self.tank_type == "quad":
                self.draw_quad_cannons(screen, screen_x, screen_y, drawn_cannon_length, drawn_cannon_thickness)
            elif self.tank_type == "octo":
                self.draw_octo_cannons(screen, screen_x, screen_y, drawn_cannon_length, drawn_cannon_thickness)

            # Draw tank outline and body
            pygame.draw.circle(screen, TANKOUTLINE, (int(screen_x), int(screen_y)), drawn_size + int(4 * self.zoom))
            pygame.draw.circle(screen, self.color, (int(screen_x), int(screen_y)), drawn_size)

        self.draw_health_bar(screen, screen_x, screen_y, drawn_size)

    def draw_health_bar(self, screen, screen_x, screen_y, drawn_size):
        if self.health < self.max_health:
            health_bar_width = drawn_size * 2
            health_bar_height = TILE_SIZE * 0.2
            health_percentage = self.health / self.max_health
            health_bar_color = HEALTHBARGREEN
            pygame.draw.rect(screen, health_bar_color, (
                int(screen_x - health_bar_width // 2),
                int(screen_y + drawn_size + 5 * self.zoom),
                int(health_bar_width * health_percentage),
                health_bar_height
            ))
            pygame.draw.rect(screen, HEALTHBAROUTLINE, (
                int(screen_x - health_bar_width // 2),
                int(screen_y + drawn_size + 5 * self.zoom),
                health_bar_width,
                health_bar_height
            ), max(1, int(self.zoom)))

    def draw_basic_cannon(self, screen, screen_x, screen_y, drawn_cannon_length, drawn_cannon_thickness):
        recoil_adjusted_length = drawn_cannon_length - (self.barrel_recoil[0] * self.zoom)
        cannon_end_x = screen_x + math.cos(self.angle) * recoil_adjusted_length
        cannon_end_y = screen_y + math.sin(self.angle) * recoil_adjusted_length
        self.draw_cannon(screen, screen_x, screen_y, cannon_end_x, cannon_end_y, drawn_cannon_thickness)

    def draw_twin_cannons(self, screen, screen_x, screen_y, drawn_cannon_length, drawn_cannon_thickness):
        for i in [-1, 1]:
            recoil_adjusted_length = drawn_cannon_length - (self.barrel_recoil[(i + 1) // 2] * self.zoom)
            cannon_separation = self.cannon_separation * self.zoom
            cannon_start_x = screen_x + i * math.cos(self.angle + math.pi / 2) * cannon_separation / 2
            cannon_start_y = screen_y + i * math.sin(self.angle + math.pi / 2) * cannon_separation / 2
            cannon_start_x -= math.cos(self.angle) * (self.size * 0.1 * self.zoom)
            cannon_start_y -= math.sin(self.angle) * (self.size * 0.1 * self.zoom)
            cannon_end_x = cannon_start_x + math.cos(self.angle) * recoil_adjusted_length
            cannon_end_y = cannon_start_y + math.sin(self.angle) * recoil_adjusted_length
            self.draw_cannon(screen, cannon_start_x, cannon_start_y, cannon_end_x, cannon_end_y, drawn_cannon_thickness)

    def draw_flank_cannons(self, screen, screen_x, screen_y, drawn_cannon_length, drawn_cannon_thickness):
        # Front cannon
        front_recoil_adjusted_length = (self.front_cannon_length * self.zoom) - (self.barrel_recoil[0] * self.zoom)
        front_cannon_end_x = screen_x + math.cos(self.angle) * front_recoil_adjusted_length
        front_cannon_end_y = screen_y + math.sin(self.angle) * front_recoil_adjusted_length
        self.draw_cannon(screen, screen_x, screen_y, front_cannon_end_x, front_cannon_end_y, drawn_cannon_thickness)

        # Back cannon
        back_angle = self.angle + math.pi
        back_recoil_adjusted_length = (self.back_cannon_length * self.zoom) - (self.barrel_recoil[1] * self.zoom)
        back_cannon_end_x = screen_x + math.cos(back_angle) * back_recoil_adjusted_length
        back_cannon_end_y = screen_y + math.sin(back_angle) * back_recoil_adjusted_length
        self.draw_cannon(screen, screen_x, screen_y, back_cannon_end_x, back_cannon_end_y, drawn_cannon_thickness)

    def draw_machine_gun_cannon(self, screen, screen_x, screen_y, drawn_cannon_length, drawn_cannon_thickness):
        recoil_adjusted_length = drawn_cannon_length - (self.barrel_recoil[0] * self.zoom)
        cannon_end_x = screen_x + math.cos(self.angle) * recoil_adjusted_length
        cannon_end_y = screen_y + math.sin(self.angle) * recoil_adjusted_length

        base_width = drawn_cannon_thickness * 0.75
        tip_width = drawn_cannon_thickness * 1

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

        outline_thickness = max(1, int(3 * self.zoom))
        pygame.draw.lines(screen, CANNONOUTLINEGREY, True, cannon_corners, outline_thickness)

        end_line_start = (cannon_end_x - tip_offset_x, cannon_end_y - tip_offset_y)
        end_line_end = (cannon_end_x + tip_offset_x, cannon_end_y + tip_offset_y)
        pygame.draw.line(screen, CANNONOUTLINEGREY, end_line_start, end_line_end, outline_thickness)

    def draw_sniper_cannon(self, screen, screen_x, screen_y, drawn_cannon_length, drawn_cannon_thickness):
        recoil_adjusted_length = drawn_cannon_length - (self.barrel_recoil[0] * self.zoom)
        cannon_end_x = screen_x + math.cos(self.angle) * recoil_adjusted_length
        cannon_end_y = screen_y + math.sin(self.angle) * recoil_adjusted_length
        self.draw_cannon(screen, screen_x, screen_y, cannon_end_x, cannon_end_y, drawn_cannon_thickness)

    def draw_cannon(self, screen, start_x, start_y, end_x, end_y, drawn_thickness):
        perpendicular_angle = math.atan2(end_y - start_y, end_x - start_x) + math.pi / 2
        half_thickness = drawn_thickness / 2
        outline_thickness = max(1, int(3 * self.zoom))

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

    def draw_gunner_cannons(self, screen, screen_x, screen_y, drawn_cannon_length, drawn_cannon_thickness):
        # Define cannon positions and lengths
        # Format: (vertical_offset, is_long_cannon, thickness_multiplier)
        cannon_configs = [
            (-3, False, 0.8),  # Top short cannon - thinner
            (-1.5, True, 1.3),  # Upper long cannon - normal thickness
            (1.5, True, 1.3),  # Lower long cannon - normal thickness
            (3, False, 0.8)  # Bottom short cannon - thinner
        ]

        for i, (pos, is_long, thickness_mult) in enumerate(cannon_configs):
            # Use appropriate length based on cannon position
            base_length = self.long_cannon_length if is_long else self.short_cannon_length
            drawn_base_length = int(base_length * self.zoom)
            recoil_adjusted_length = drawn_base_length - (self.barrel_recoil[i] * self.zoom)
            offset = pos * (self.cannon_separation * self.zoom)

            # Calculate cannon start position
            cannon_start_x = screen_x + math.cos(self.angle + math.pi / 2) * offset
            cannon_start_y = screen_y + math.sin(self.angle + math.pi / 2) * offset

            # Calculate cannon end position
            cannon_end_x = cannon_start_x + math.cos(self.angle) * recoil_adjusted_length
            cannon_end_y = cannon_start_y + math.sin(self.angle) * recoil_adjusted_length

            # Draw cannon with outline
            perpendicular_angle = self.angle + math.pi / 2
            outline_thickness = max(1, int(2 * self.zoom))

            # Adjust thickness based on whether it's an inner or outer cannon
            current_thickness = drawn_cannon_thickness * thickness_mult

            # Calculate outline points with adjusted thickness
            outline_offset = current_thickness / 2 + outline_thickness
            outline_points = [
                (cannon_start_x + math.cos(perpendicular_angle) * outline_offset,
                 cannon_start_y + math.sin(perpendicular_angle) * outline_offset),
                (cannon_start_x - math.cos(perpendicular_angle) * outline_offset,
                 cannon_start_y - math.sin(perpendicular_angle) * outline_offset),
                (cannon_end_x - math.cos(perpendicular_angle) * outline_offset,
                 cannon_end_y - math.sin(perpendicular_angle) * outline_offset),
                (cannon_end_x + math.cos(perpendicular_angle) * outline_offset,
                 cannon_end_y + math.sin(perpendicular_angle) * outline_offset)
            ]

            # Draw cannon outline
            pygame.draw.polygon(screen, CANNONOUTLINEGREY, outline_points)

            # Calculate inner cannon points with adjusted thickness
            cannon_points = [
                (cannon_start_x + math.cos(perpendicular_angle) * current_thickness / 2,
                 cannon_start_y + math.sin(perpendicular_angle) * current_thickness / 2),
                (cannon_start_x - math.cos(perpendicular_angle) * current_thickness / 2,
                 cannon_start_y - math.sin(perpendicular_angle) * current_thickness / 2),
                (cannon_end_x - math.cos(perpendicular_angle) * current_thickness / 2,
                 cannon_end_y - math.sin(perpendicular_angle) * current_thickness / 2),
                (cannon_end_x + math.cos(perpendicular_angle) * current_thickness / 2,
                 cannon_end_y + math.sin(perpendicular_angle) * current_thickness / 2)
            ]

            # Draw inner cannon
            pygame.draw.polygon(screen, CANNONGREY, cannon_points)

    def draw_quad_cannons(self, screen, screen_x, screen_y, drawn_cannon_length, drawn_cannon_thickness):
        # Base angles for quad configuration, but add the tank's rotation
        base_angles = [0, math.pi / 2, math.pi, 3 * math.pi / 2]  # Right, Down, Left, Up

        for i, angle in enumerate(base_angles):
            # Add the tank's rotation angle to each cannon
            actual_angle = angle + self.angle

            # Calculate cannon endpoint with rotated angle
            drawn_length = (self.cannon_length - (self.barrel_recoil[i] * self.zoom)) * self.zoom
            cannon_end_x = screen_x + math.cos(actual_angle) * drawn_length
            cannon_end_y = screen_y + math.sin(actual_angle) * drawn_length

            self.draw_cannon(screen, screen_x, screen_y, cannon_end_x, cannon_end_y, drawn_cannon_thickness)

    def draw_auto_quad(self, screen, screen_x, screen_y, drawn_cannon_length, drawn_cannon_thickness):
        # 1. Draw base quad tank cannons first
        base_angles = [0, math.pi / 2, math.pi, 3 * math.pi / 2]  # Right, Down, Left, Up

        for i, angle in enumerate(base_angles):
            actual_angle = angle + self.angle
            recoil_adjusted_length = drawn_cannon_length - (self.barrel_recoil[i] * self.zoom)

            cannon_end_x = screen_x + math.cos(actual_angle) * recoil_adjusted_length
            cannon_end_y = screen_y + math.sin(actual_angle) * recoil_adjusted_length

            # Draw main tank's cannons
            perpendicular_angle = actual_angle + math.pi / 2
            half_thickness = drawn_cannon_thickness / 2
            outline_thickness = max(1, int(3 * self.zoom))

            # Draw cannon outline
            outline_offset_x = math.cos(perpendicular_angle) * (half_thickness + outline_thickness)
            outline_offset_y = math.sin(perpendicular_angle) * (half_thickness + outline_thickness)
            outline_corners = [
                (screen_x + outline_offset_x, screen_y + outline_offset_y),
                (screen_x - outline_offset_x, screen_y - outline_offset_y),
                (cannon_end_x - outline_offset_x, cannon_end_y - outline_offset_y),
                (cannon_end_x + outline_offset_x, cannon_end_y + outline_offset_y)
            ]
            pygame.draw.polygon(screen, CANNONOUTLINEGREY, outline_corners)

            # Draw cannon fill
            corner_offset_x = math.cos(perpendicular_angle) * half_thickness
            corner_offset_y = math.sin(perpendicular_angle) * half_thickness
            cannon_corners = [
                (screen_x + corner_offset_x, screen_y + corner_offset_y),
                (screen_x - corner_offset_x, screen_y - corner_offset_y),
                (cannon_end_x - corner_offset_x, cannon_end_y - corner_offset_y),
                (cannon_end_x + corner_offset_x, cannon_end_y + corner_offset_y)
            ]
            pygame.draw.polygon(screen, CANNONGREY, cannon_corners)

            # Draw cannon end cap
            end_line_start = (cannon_end_x - outline_offset_x, cannon_end_y - outline_offset_y)
            end_line_end = (cannon_end_x + outline_offset_x, cannon_end_y + outline_offset_y)
            pygame.draw.line(screen, CANNONOUTLINEGREY, end_line_start, end_line_end, outline_thickness)

        # 2. Draw tank body and outline
        pygame.draw.circle(screen, TANKOUTLINE, (int(screen_x), int(screen_y)),
                           int(self.size * self.zoom) + int(4 * self.zoom))
        pygame.draw.circle(screen, self.color, (int(screen_x), int(screen_y)),
                           int(self.size * self.zoom))

        # Draw auto turret base first (below the cannon)
        turret_size = int(self.auto_turret_size * self.zoom)
        pygame.draw.circle(screen, CANNONOUTLINEGREY, (int(screen_x), int(screen_y)),
                           turret_size + int(2 * self.zoom))
        pygame.draw.circle(screen, CANNONGREY, (int(screen_x), int(screen_y)), turret_size)

        # 3. Draw auto turret cannon last
        turret_cannon_length = int(self.auto_turret_cannon_length * self.zoom)
        turret_cannon_width = int(self.auto_turret_cannon_width * self.zoom)
        recoil_adjusted_turret_length = turret_cannon_length - (self.auto_turret_recoil * self.zoom)

        cannon_start_x = int(screen_x)
        cannon_start_y = int(screen_y)
        cannon_end_x = cannon_start_x + int(math.cos(self.auto_turret_angle) * recoil_adjusted_turret_length)
        cannon_end_y = cannon_start_y + int(math.sin(self.auto_turret_angle) * recoil_adjusted_turret_length)

        perp_angle = self.auto_turret_angle + math.pi / 2
        half_width = turret_cannon_width / 2
        outline_width = int(2 * self.zoom)

        # Draw cannon outline
        perp_x = math.cos(perp_angle) * (half_width + outline_width)
        perp_y = math.sin(perp_angle) * (half_width + outline_width)

        outline_points = [
            (cannon_start_x + perp_x, cannon_start_y + perp_y),
            (cannon_start_x - perp_x, cannon_start_y - perp_y),
            (cannon_end_x - perp_x, cannon_end_y - perp_y),
            (cannon_end_x + perp_x, cannon_end_y + perp_y)
        ]
        pygame.draw.polygon(screen, CANNONOUTLINEGREY, outline_points)

        # Draw cannon fill
        perp_x = math.cos(perp_angle) * half_width
        perp_y = math.sin(perp_angle) * half_width

        cannon_points = [
            (cannon_start_x + perp_x, cannon_start_y + perp_y),
            (cannon_start_x - perp_x, cannon_start_y - perp_y),
            (cannon_end_x - perp_x, cannon_end_y - perp_y),
            (cannon_end_x + perp_x, cannon_end_y + perp_y)
        ]
        pygame.draw.polygon(screen, CANNONGREY, cannon_points)

        # Draw cannon end cap
        end_line_start = (cannon_end_x + math.cos(perp_angle) * half_width,
                          cannon_end_y + math.sin(perp_angle) * half_width)
        end_line_end = (cannon_end_x - math.cos(perp_angle) * half_width,
                        cannon_end_y - math.sin(perp_angle) * half_width)
        pygame.draw.line(screen, CANNONOUTLINEGREY, end_line_start, end_line_end, outline_width)

    def draw_octo_cannons(self, screen, screen_x, screen_y, drawn_cannon_length, drawn_cannon_thickness):
        # Base angles for octo configuration (8 directions), but add the tank's rotation
        base_angles = [0, math.pi / 4, math.pi / 2, 3 * math.pi / 4, math.pi, 5 * math.pi / 4, 3 * math.pi / 2,
                       7 * math.pi / 4]
        # Right, Right-Down, Down, Left-Down, Left, Left-Up, Up, Right-Up

        for i, angle in enumerate(base_angles):
            # Add the tank's rotation angle to each cannon
            actual_angle = angle + self.angle

            # Calculate cannon endpoint with rotated angle
            recoil_adjusted_length = drawn_cannon_length - (self.barrel_recoil[i] * self.zoom)
            cannon_end_x = screen_x + math.cos(actual_angle) * recoil_adjusted_length
            cannon_end_y = screen_y + math.sin(actual_angle) * recoil_adjusted_length

            self.draw_cannon(screen, screen_x, screen_y, cannon_end_x, cannon_end_y, drawn_cannon_thickness)

    def create_bullet(self, x, y, angle):
        if isinstance(self, Player):
            # Apply bullet speed multiplier for player
            bullet_speed = self.base_stats["Bullet Speed"] * (1 + self.attribute_levels["Bullet Speed"] * 0.2)

            # Adjust speed based on tank type
            if self.tank_type == "sniper":
                bullet_speed = bullet_speed * 1.5  # Sniper gets 50% more base speed
            elif self.tank_type == "gunner" or self.tank_type == "auto_gunner":
                bullet_speed = bullet_speed * 1.2  # Gunner gets 20% more base speed

            # Calculate velocity components with the modified speed
            vel_x = math.cos(angle) * bullet_speed
            vel_y = math.sin(angle) * bullet_speed

            # Create bullet with tank-specific properties
            bullet = Bullet(x, y, vel_x, vel_y, 0, self)
            bullet.owner = self

            # Set bullet size based on tank type and firing source
            if self.tank_type == "gunner":
                bullet.base_radius = int(BASE_BULLET_SIZE * 0.4)  # 40% of normal size
                bullet.radius = bullet.base_radius
                bullet.damage = self.bullet_damage * 0.4  # Reduce damage to match size
            elif self.tank_type == "auto_quad":
                # Check if the bullet is being fired from the auto turret
                bullet_angle_diff = abs((angle - self.auto_turret_angle + math.pi) % (2 * math.pi) - math.pi)
                if bullet_angle_diff < 0.1:  # If angle is very close to auto turret angle
                    # Use same size as auto gunner's auto turret bullets
                    bullet.base_radius = int(BASE_BULLET_SIZE * 0.6)  # 60% of normal size
                    bullet.radius = bullet.base_radius
                    bullet.damage = self.bullet_damage * 0.6  # Adjust damage for auto turret
            elif self.tank_type == "auto_gunner":
                # Check if the bullet is being fired from the auto turret
                bullet_angle_diff = abs((angle - self.auto_turret_angle + math.pi) % (2 * math.pi) - math.pi)
                if bullet_angle_diff < 0.1:  # If angle is very close to auto turret angle
                    # Auto turret bullets are slightly bigger than gunner bullets
                    bullet.base_radius = int(BASE_BULLET_SIZE * 0.6)  # 60% of normal size
                    bullet.radius = bullet.base_radius
                    bullet.damage = self.bullet_damage * 0.6  # Adjust damage for auto turret
                else:
                    # Main gunner cannons use the same size as regular gunner
                    bullet.base_radius = int(BASE_BULLET_SIZE * 0.4)  # 40% of normal size
                    bullet.radius = bullet.base_radius
                    bullet.damage = self.bullet_damage * 0.4  # Regular gunner damage

            self.bullets.append(bullet)
        else:
            # Original enemy bullet creation logic
            bullet_speed = 12
            if self.tank_type == "sniper":
                bullet_speed = 16
            vel_x = math.cos(angle) * bullet_speed
            vel_y = math.sin(angle) * bullet_speed

            bullet = Bullet(x, y, vel_x, vel_y, 1, self)
            bullet.owner = self
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
        self.individual_score = 500
        self.level = 1

        # Set up tank-specific attributes
        if self.tank_type == "twin":
            self.cannon_separation = self.base_size * 1.0
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

        # Apply initial dimension adjustment
        self.adjust_dimensions()

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

        if not is_on_screen(self.world_x, self.world_y, self.base_size + self.cannon_length, tank):
            return

        # Calculate screen position using the player's zoom factor
        screen_x = int((self.world_x - tank.world_x) * tank.zoom + tank.x)
        screen_y = int((self.world_y - tank.world_y) * tank.zoom + tank.y)

        # Scale dimensions using the player's zoom
        drawn_size = int(self.base_size * tank.zoom)

        # Update cannon dimensions based on tank type and zoom
        if self.tank_type == "sniper":
            drawn_cannon_length = int(90 * tank.zoom)
            drawn_cannon_thickness = int(30 * tank.zoom)
        elif self.tank_type == "machine_gun":
            drawn_cannon_length = int(70 * tank.zoom)
            drawn_cannon_thickness = int(50 * tank.zoom)
        elif self.tank_type == "twin":
            drawn_cannon_length = int(80 * tank.zoom)
            drawn_cannon_thickness = int(30 * tank.zoom)
            self.cannon_separation = int(self.base_size * 1.0 * tank.zoom)
        elif self.tank_type == "flank":
            self.front_cannon_length = int(75 * tank.zoom)
            self.back_cannon_length = int(60 * tank.zoom)
            drawn_cannon_length = self.front_cannon_length
            drawn_cannon_thickness = int(30 * tank.zoom)
        else:  # basic tank
            drawn_cannon_length = int(75 * tank.zoom)
            drawn_cannon_thickness = int(30 * tank.zoom)

        if self.tank_type == "basic":
            self.draw_basic_cannon(screen, screen_x, screen_y, drawn_cannon_length, drawn_cannon_thickness)
        elif self.tank_type == "twin":
            self.draw_twin_cannons(screen, screen_x, screen_y, drawn_cannon_length, drawn_cannon_thickness)
        elif self.tank_type == "flank":
            self.draw_flank_cannons(screen, screen_x, screen_y, drawn_cannon_length, drawn_cannon_thickness)
        elif self.tank_type == "machine_gun":
            self.draw_machine_gun_cannon(screen, screen_x, screen_y, drawn_cannon_length, drawn_cannon_thickness)
        elif self.tank_type == "sniper":
            self.draw_sniper_cannon(screen, screen_x, screen_y, drawn_cannon_length, drawn_cannon_thickness)

        # Draw enemy outline and body with scaled size
        pygame.draw.circle(screen, ENEMYOUTLINE, (screen_x, screen_y), drawn_size + int(4 * tank.zoom))
        pygame.draw.circle(screen, self.color, (screen_x, screen_y), drawn_size)

        self.draw_health_bar(screen, screen_x, screen_y, drawn_size)

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
        self.attributes_surface = None
        self.attributes_need_update = True
        # Add attribute levels
        self.attribute_levels = {
            "Health Regen": 0,
            "Max Health": 0,
            "Body Damage": 0,
            "Bullet Speed": 0,
            "Bullet Penetration": 0,
            "Bullet Damage": 0,
            "Reload": 0,
            "Movement Speed": 0
        }
        self.available_points = 0
        self.max_attribute_level = 7
        # Add base stats
        self.base_stats = {
            "Health Regen": 0.1,
            "Max Health": 500,
            "Body Damage": 5,
            "Bullet Speed": 12,
            "Bullet Penetration": 1,
            "Bullet Damage": 25,
            "Reload": 15,
            "Movement Speed": 5
        }

        # Initialize derived stats
        self.base_reload = self.base_stats["Reload"]

        # Call update_stats to initialize all stats
        self.update_stats()
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
        # Add auto turret properties
        self.auto_turret_size = self.base_size * 0.6  # Turret size
        self.auto_turret_cannon_length = TILE_SIZE * 2  # 50 pixels
        self.auto_turret_cannon_width = TILE_SIZE * 0.4  # 10 pixels
        self.auto_turret_reload = 0
        self.auto_turret_reload_time = 20  # Shots every 1/3 second
        self.auto_turret_angle = 0
        self.upgrade_available = False
        # Add auto turret tracking
        self.nearest_target = None

    def update_stats(self):
        # Health Regen
        self.regen_rate = self.base_stats["Health Regen"] * (1 + self.attribute_levels["Health Regen"] * 0.5)

        # Max Health (20% increase per level)
        self.max_health = self.base_stats["Max Health"] * (1 + self.attribute_levels["Max Health"] * 0.2)

        # Body Damage (40% increase per level)
        self.body_damage = self.base_stats["Body Damage"] * (1 + self.attribute_levels["Body Damage"] * 0.4)

        # Bullet Speed (20% increase per level)
        bullet_speed_multiplier = 1 + self.attribute_levels["Bullet Speed"] * 0.2

        # Bullet Damage (40% increase per level)
        self.bullet_damage = self.base_stats["Bullet Damage"] * (1 + self.attribute_levels["Bullet Damage"] * 0.4)

        # Reload (15% decrease in cooldown per level)
        base_reload_time = self.base_stats["Reload"]
        if self.tank_type == "octo":
            base_reload_time = base_reload_time / 2  # Halve the base reload time for octo tank
        self.base_reload = base_reload_time / (1 + self.attribute_levels["Reload"] * 0.15)

        # Movement Speed (15% increase per level)
        self.speed = self.base_stats["Movement Speed"] * (1 + self.attribute_levels["Movement Speed"] * 0.15)

    def update_nearest_target(self, shapes, enemies):
        """Update nearest target for tanks with auto turrets"""
        if self.tank_type not in ["auto_gunner", "auto_quad"]:
            return

        nearest_distance = float('inf')
        nearest_target = None

        # Check shapes
        for shape in shapes:
            if shape.alive:
                distance = math.sqrt((self.world_x - shape.world_x) ** 2 + (self.world_y - shape.world_y) ** 2)
                if distance < nearest_distance and distance < SCREEN_WIDTH:  # Only target within view range
                    nearest_distance = distance
                    nearest_target = shape

        # Check enemies
        for enemy in enemies:
            if enemy.alive:
                distance = math.sqrt((self.world_x - enemy.world_x) ** 2 + (self.world_y - enemy.world_y) ** 2)
                if distance < nearest_distance and distance < SCREEN_WIDTH:  # Only target within view range
                    nearest_distance = distance
                    nearest_target = enemy

        self.nearest_target = nearest_target

        # Update auto turret angle if we have a target
        if self.nearest_target:
            target_angle = math.atan2(
                self.nearest_target.world_y - self.world_y,
                self.nearest_target.world_x - self.world_x
            )

            # Smoothly rotate towards target
            angle_diff = (target_angle - self.auto_turret_angle + math.pi) % (2 * math.pi) - math.pi
            rotation_speed = 0.1  # Adjust this value to control rotation speed
            if abs(angle_diff) > rotation_speed:
                if angle_diff > 0:
                    self.auto_turret_angle += rotation_speed
                else:
                    self.auto_turret_angle -= rotation_speed
            else:
                self.auto_turret_angle = target_angle

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
        self.zoom = SNIPER_ZOOM
        self.cannon_length = TILE_SIZE * 3.6  # 90 pixels
        self.cannon_thickness = TILE_SIZE * 1.2  # 30 pixels
        self.barrel_recoil = [0]
        self.fire_rate = 1
        self.upgrade_available = False

    def upgrade_to_gunner(self):
        self.tank_type = "gunner"
        # Adjust cannon lengths - center cannons longer than outer ones
        self.long_cannon_length = TILE_SIZE * 2.8  # 70 pixels for middle cannons
        self.short_cannon_length = TILE_SIZE * 2.4  # 60 pixels for outer cannons
        self.cannon_thickness = TILE_SIZE * 0.5  # 10 pixels
        self.barrel_recoil = [0, 0, 0, 0]  # One for each cannon
        self.cannon_separation = self.base_size * 0.3  # Smaller separation between cannons
        self.bullet_size_multiplier = 0.4  # Smaller bullets
        self.base_reload = self.base_stats["Reload"] * 0.6  # 40% faster base reload
        self.upgrade_available = False

    def upgrade_to_auto_gunner(self):
        self.tank_type = "auto_gunner"
        # Keep gunner's existing properties
        self.long_cannon_length = TILE_SIZE * 2.8  # 70 pixels for middle cannons
        self.short_cannon_length = TILE_SIZE * 2.4  # 60 pixels for outer cannons
        self.cannon_thickness = TILE_SIZE * 0.5  # 10 pixels
        self.barrel_recoil = [0, 0, 0, 0]  # One for each cannon
        self.cannon_separation = self.base_size * 0.3  # Smaller separation between cannons
        self.bullet_size_multiplier = 0.4  # Smaller bullets
        self.base_reload = self.base_stats["Reload"] * 0.6  # 40% faster base reload

        # Auto turret specific properties
        self.auto_turret_angle = 0
        self.auto_turret_reload = 0
        # Remove the fixed reload time since it will be calculated based on reload stat
        self.auto_turret_size = self.base_size * 0.6
        self.auto_turret_cannon_length = TILE_SIZE * 2
        self.auto_turret_cannon_width = TILE_SIZE * 0.6
        self.auto_turret_recoil = 0
        self.upgrade_available = False

    def upgrade_to_quad(self):
        self.tank_type = "quad"
        self.cannon_length = TILE_SIZE * 3  # 75 pixels
        self.cannon_thickness = TILE_SIZE * 1.2  # 30 pixels
        self.barrel_recoil = [0, 0, 0, 0]  # One for each direction
        self.upgrade_available = False

    def upgrade_to_auto_quad(self):
        self.tank_type = "auto_quad"
        # Keep quad tank properties
        self.cannon_length = TILE_SIZE * 3  # 75 pixels
        self.cannon_thickness = TILE_SIZE * 1.2  # 30 pixels
        self.barrel_recoil = [0, 0, 0, 0]  # One for each direction

        # Add auto turret properties
        self.auto_turret_angle = 0
        self.auto_turret_reload = 0
        self.auto_turret_size = self.base_size * 0.6  # Turret size
        self.auto_turret_cannon_length = TILE_SIZE * 2  # 50 pixels
        self.auto_turret_cannon_width = TILE_SIZE * 0.6  # 15 pixels
        self.auto_turret_recoil = 0
        self.upgrade_available = False

    def upgrade_to_octo(self):
        self.tank_type = "octo"
        self.cannon_length = TILE_SIZE * 3  # 75 pixels
        self.cannon_thickness = TILE_SIZE * 1.2  # 30 pixels
        self.barrel_recoil = [0, 0, 0, 0, 0, 0, 0, 0]  # One for each direction
        # Add firing pattern tracking
        self.octo_fire_group = 0  # 0 for plus formation, 1 for diagonal
        self.upgrade_available = False
        # The overall cooldown should be half of quad tank's cooldown
        self.base_reload = self.base_stats["Reload"] / 2
        self.update_stats()

    def update_level(self):
        previous_level = self.level
        self.level = np.searchsorted(scores, self.score, side='right')

        # Calculate points to award based on level change
        if self.level > previous_level:
            self.award_upgrade_points(previous_level, self.level)

    def level_up(self):
        if self.level < 45:
            previous_level = self.level
            self.level += 1
            self.score = scores[self.level - 1]

            # Calculate points for this level up
            if self.level >= 2 and self.level <= 28:
                self.available_points += 1
                self.attributes_need_update = True  # Mark for update
            elif self.level == 30:
                self.available_points += 1
                self.attributes_need_update = True  # Mark for update
            elif self.level > 30 and self.level <= 45 and (self.level - 30) % 3 == 0:
                self.available_points += 1
                self.attributes_need_update = True  # Mark for update

    def award_upgrade_points(self, previous_level, new_level):
        """Awards upgrade points based on level changes."""
        for level in range(previous_level + 1, new_level + 1):
            # Points from level 2-28 (27 points)
            if level >= 2 and level <= 28:
                self.available_points += 1
                self.attributes_need_update = True
            # Point at level 30 (1 point)
            elif level == 30:
                self.available_points += 1
                self.attributes_need_update = True
            # Points at levels 33, 36, 39, 42, 45 (5 points)
            elif level > 30 and level <= 45 and (level - 30) % 3 == 0:
                self.available_points += 1
                self.attributes_need_update = True

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
        # Existing movement code...
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

        # Update recoil and barrel recoil
        self.recoil_velocity_x *= self.recoil_dampening
        self.recoil_velocity_y *= self.recoil_dampening

        recoil_speed = math.sqrt(self.recoil_velocity_x ** 2 + self.recoil_velocity_y ** 2)
        if recoil_speed > self.max_recoil_speed:
            factor = self.max_recoil_speed / recoil_speed
            self.recoil_velocity_x *= factor
            self.recoil_velocity_y *= factor

        # Update barrel recoil
        for i in range(len(self.barrel_recoil)):
            if self.barrel_recoil[i] > 0:
                self.barrel_recoil[i] = max(0, self.barrel_recoil[i] - self.barrel_recoil_speed)

        # Auto turret update for auto_quad and auto_gunner
        if self.tank_type in ["auto_quad", "auto_gunner"]:
            if self.auto_turret_reload > 0:
                self.auto_turret_reload -= 1

            if self.auto_turret_reload <= 0 and self.nearest_target:
                # Calculate bullet position at the end of the turret cannon
                recoil_adjusted_length = self.auto_turret_cannon_length - self.auto_turret_recoil
                bullet_x = self.world_x + math.cos(self.auto_turret_angle) * (
                        recoil_adjusted_length + self.size * 0.3)
                bullet_y = self.world_y + math.sin(self.auto_turret_angle) * (
                        recoil_adjusted_length + self.size * 0.3)

                # Create bullet from auto turret
                self.create_bullet(bullet_x, bullet_y, self.auto_turret_angle)

                # Calculate auto turret reload time based on reload stat
                base_auto_turret_reload = 20
                reload_multiplier = 1 / (1 + self.attribute_levels["Reload"] * 0.15)
                self.auto_turret_reload = int(base_auto_turret_reload * reload_multiplier)

                # Add recoil when firing
                self.auto_turret_recoil = self.max_barrel_recoil * 0.7

        # Auto turret recoil recovery
        if self.auto_turret_recoil > 0:
            self.auto_turret_recoil = max(0, self.auto_turret_recoil - self.barrel_recoil_speed)

    def rotate_to_mouse(self, mouse_pos):
        if self.autospin:
            self.angle += 0.03
        else:
            dx, dy = mouse_pos[0] - self.x, mouse_pos[1] - self.y
            self.angle = math.atan2(dy, dx)

    def shoot(self):
        if self.shoot_cooldown <= 0:
            if self.tank_type == "basic":
                self.shoot_basic()
                self.shoot_cooldown = self.base_reload
            elif self.tank_type == "gunner":
                self.shoot_gunner()
                self.shoot_cooldown = self.base_reload * 0.4
            elif self.tank_type == "auto_gunner":
                self.shoot_gunner()  # Use the same gunner shooting mechanics
                self.shoot_cooldown = self.base_reload * 0.4
            elif self.tank_type == "quad":
                self.shoot_quad()
                self.shoot_cooldown = self.base_reload
            elif self.tank_type == "auto_quad":
                self.shoot_quad()  # Use the quad shooting mechanics
                self.shoot_cooldown = self.base_reload
            elif self.tank_type == "twin":
                self.shoot_twin()
                self.shoot_cooldown = self.base_reload / 2
            elif self.tank_type == "flank":
                self.shoot_flank()
                self.shoot_cooldown = self.base_reload
            elif self.tank_type == "machine_gun":
                self.shoot_machine_gun()
                self.shoot_cooldown = self.base_reload / 2
            elif self.tank_type == "sniper":
                self.shoot_sniper()
                self.shoot_cooldown = self.base_reload * 2
            elif self.tank_type == "octo":
                self.shoot_octo()
                self.shoot_cooldown = self.base_reload

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

    def shoot_gunner(self):
        # We'll only fire one bullet per shoot call now
        # Get the current firing phase (0-3) based on shot count
        phase = (getattr(self, 'gunner_shot_count', 0) % 4)

        # Initialize shot count if it doesn't exist
        if not hasattr(self, 'gunner_shot_count'):
            self.gunner_shot_count = 0

        # Define the firing sequence (2,3,1,4 in terms of 0-based indices)
        firing_sequence = [1, 2, 0, 3]  # Convert to 0-based indices
        current_turret = firing_sequence[phase]

        # Match cannon configurations but only fire from one
        cannon_configs = [
            (-3, False, 0.8),  # Turret 1 (index 0) - Left outer
            (-1.5, True, 1.3),  # Turret 2 (index 1) - Left inner
            (1.5, True, 1.3),  # Turret 3 (index 2) - Right inner
            (3, False, 0.8)  # Turret 4 (index 3) - Right outer
        ]

        # Get the configuration for the current turret
        pos, is_long, _ = cannon_configs[current_turret]

        # Calculate the offset based on cannon position
        offset = pos * self.cannon_separation

        # Calculate perpendicular offset for cannon position
        perp_x = math.cos(self.angle + math.pi / 2) * offset
        perp_y = math.sin(self.angle + math.pi / 2) * offset

        # Use appropriate length based on whether it's a long or short cannon
        base_length = self.long_cannon_length if is_long else self.short_cannon_length
        recoil_adjusted_length = base_length - self.barrel_recoil[current_turret]

        # Calculate cannon tip position
        cannon_tip_x = self.world_x + perp_x + math.cos(self.angle) * recoil_adjusted_length
        cannon_tip_y = self.world_y + perp_y + math.sin(self.angle) * recoil_adjusted_length

        # Create bullet at the exact cannon tip position
        self.create_bullet(cannon_tip_x, cannon_tip_y, self.angle)

        # Apply recoil only to the fired cannon
        self.barrel_recoil[current_turret] = self.max_barrel_recoil * 0.7

        # Add slight recoil to tank movement (reduced since it's only one bullet)
        recoil_force = 0.2
        self.recoil_velocity_x -= math.cos(self.angle) * recoil_force
        self.recoil_velocity_y -= math.sin(self.angle) * recoil_force

        # Increment the shot counter
        self.gunner_shot_count += 1

    def shoot_quad(self):
        # Calculate base angles but add the tank's current rotation
        base_angles = [0, math.pi / 2, math.pi, 3 * math.pi / 2]  # Right, Down, Left, Up

        for i, angle in enumerate(base_angles):
            # Add the tank's rotation angle to each cannon
            actual_angle = angle + self.angle

            # Calculate bullet spawn position
            bullet_x = self.world_x + math.cos(actual_angle) * self.size
            bullet_y = self.world_y + math.sin(actual_angle) * self.size

            # Create bullet with the correct angle
            self.create_bullet(bullet_x, bullet_y, actual_angle)
            self.barrel_recoil[i] = self.max_barrel_recoil

            # Add recoil effect
            recoil_force = 0.2
            self.recoil_velocity_x -= math.cos(actual_angle) * recoil_force
            self.recoil_velocity_y -= math.sin(actual_angle) * recoil_force

    def shoot_octo(self):
        current_time = pygame.time.get_ticks()

        # Calculate base angles but add the tank's current rotation
        # First four are plus formation (0°, 90°, 180°, 270°)
        # Second four are diagonal (45°, 135°, 225°, 315°)
        plus_angles = [0, math.pi / 2, math.pi, 3 * math.pi / 2]
        diagonal_angles = [math.pi / 4, 3 * math.pi / 4, 5 * math.pi / 4, 7 * math.pi / 4]

        # Select which group to fire based on timing
        firing_group = plus_angles if self.octo_fire_group == 0 else diagonal_angles

        # Fire the current group
        for i, angle in enumerate(firing_group):
            # Add the tank's rotation angle to each cannon
            actual_angle = angle + self.angle

            # Calculate bullet spawn position
            bullet_x = self.world_x + math.cos(actual_angle) * self.size
            bullet_y = self.world_y + math.sin(actual_angle) * self.size

            # Create bullet with the correct angle
            self.create_bullet(bullet_x, bullet_y, actual_angle)

            # Apply recoil to the appropriate cannon
            recoil_index = i if self.octo_fire_group == 0 else i + 4
            self.barrel_recoil[recoil_index] = self.max_barrel_recoil

            # Add recoil effect
            recoil_force = 0.2
            self.recoil_velocity_x -= math.cos(actual_angle) * recoil_force
            self.recoil_velocity_y -= math.sin(actual_angle) * recoil_force

        # Toggle the firing group for next time
        self.octo_fire_group = 1 - self.octo_fire_group

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
                enemy.take_damage(self.body_damage, self)  # Use body_damage here
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

        # Reset attribute points based on level when respawning
        self.available_points = 0
        self.attribute_levels = {
            "Health Regen": 0,
            "Max Health": 0,
            "Body Damage": 0,
            "Bullet Speed": 0,
            "Bullet Penetration": 0,
            "Bullet Damage": 0,
            "Reload": 0,
            "Movement Speed": 0
        }

        # Recalculate base_reload and other stats
        self.base_reload = self.base_stats["Reload"]
        self.update_stats()

        # Recalculate points based on current level
        for level in range(2, self.level + 1):
            if level <= 28:
                self.available_points += 1
            elif level == 30:
                self.available_points += 1
            elif level > 30 and level <= 45 and (level - 30) % 3 == 0:
                self.available_points += 1

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
                            # Pass self instead of tankNum
                            shape.take_damage(5, self)
                            angle = math.atan2(self.world_y - shape.world_y, self.world_x - shape.world_x)
                            self.world_x += math.cos(angle) * 5
                            self.world_y += math.sin(angle) * 5
                            break
                else:
                    distance = math.sqrt((self.world_x - shape.world_x) ** 2 + (self.world_y - shape.world_y) ** 2)
                    if distance < self.size + shape.size // 2:
                        self.take_damage(5, shape)
                        # Pass self instead of tankNum
                        shape.take_damage(5, self)
                        angle = math.atan2(self.world_y - shape.world_y, self.world_x - shape.world_x)
                        push_distance = (self.size + shape.size // 2) - distance
                        self.world_x += math.cos(angle) * push_distance / 2
                        self.world_y += math.sin(angle) * push_distance / 2
                        shape.world_x -= math.cos(angle) * push_distance / 2
                        shape.world_y -= math.sin(angle) * push_distance / 2

    def find_nearest_target(self, shapes, enemies):
        nearest_distance = float('inf')
        nearest_target = None

        # Check shapes
        for shape in shapes:
            if shape.alive:
                distance = math.sqrt((self.world_x - shape.world_x) ** 2 + (self.world_y - shape.world_y) ** 2)
                if distance < nearest_distance:
                    nearest_distance = distance
                    nearest_target = shape

        # Check enemies
        if enemies:
            for enemy in enemies:
                if enemy.alive:
                    distance = math.sqrt((self.world_x - enemy.world_x) ** 2 + (self.world_y - enemy.world_y) ** 2)
                    if distance < nearest_distance:
                        nearest_distance = distance
                        nearest_target = enemy

        return nearest_target


class Bullet:
    def __init__(self, x, y, vel_x, vel_y, tankNum, owner=None):
        self.world_x = x
        self.world_y = y
        self.initial_vel_x = vel_x  # Store initial velocities
        self.initial_vel_y = vel_y
        self.vel_x = vel_x
        self.vel_y = vel_y

        if owner and isinstance(owner, Player):
            # Get damage directly from the player's stats
            self.damage = owner.bullet_damage
        else:
            self.damage = 25 - (tankNum * 15)

        self.base_radius = BASE_BULLET_SIZE
        self.radius = self.base_radius
        self.lifespan = 100
        self.initial_lifespan = 200  # Store initial lifespan
        self.tankNum = tankNum
        self.color = AQUA if tankNum == 0 else RED
        self.bulletOutline = TANKOUTLINE if tankNum == 0 else ENEMYOUTLINE
        self.owner = owner

        # Enhanced speed decay parameters
        self.min_speed_multiplier = 0.3  # Bullet will slow down to 30% of initial speed
        self.speed_decay_start = 0.8  # Start slowing down when 80% of lifespan remains
        self.decay_exponent = 1.5  # Makes the decay curve more aggressive

    def update(self):
        # Calculate speed multiplier based on remaining lifespan
        life_fraction = self.lifespan / self.initial_lifespan

        if life_fraction <= self.speed_decay_start:
            # Calculate decay progress with non-linear curve
            decay_progress = 1.0 - (life_fraction / self.speed_decay_start)
            # Apply exponential curve to make decay more pronounced
            decay_progress = pow(decay_progress, self.decay_exponent)

            # Calculate speed multiplier
            speed_multiplier = 1.0 - (decay_progress * (1.0 - self.min_speed_multiplier))

            # Apply speed multiplier to current velocity
            self.vel_x = self.initial_vel_x * speed_multiplier
            self.vel_y = self.initial_vel_y * speed_multiplier

        # Update position with current velocity
        self.world_x += self.vel_x
        self.world_y += self.vel_y
        self.lifespan -= 1

        # Keep bullets within world bounds
        self.world_x = max(self.radius, min(WORLD_WIDTH - self.radius, self.world_x))
        self.world_y = max(self.radius, min(WORLD_HEIGHT - self.radius, self.world_y))

    # Rest of the Bullet class methods remain unchanged...
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

    def draw(self, tank):
        if not is_on_screen(self.world_x, self.world_y, self.base_radius * 2, tank):
            return

        screen_x = int((self.world_x - tank.world_x) * tank.zoom + tank.x)
        screen_y = int((self.world_y - tank.world_y) * tank.zoom + tank.y)

        if 0 <= screen_x < SCREEN_WIDTH and 0 <= screen_y < SCREEN_HEIGHT:
            drawn_radius = int(self.base_radius * tank.zoom)
            pygame.draw.circle(screen, self.bulletOutline, (screen_x, screen_y),
                               drawn_radius + int(4 * tank.zoom))
            pygame.draw.circle(screen, self.color, (screen_x, screen_y), drawn_radius)

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
                distance = math.sqrt(
                    (self.world_x - other_bullet.world_x) ** 2 + (self.world_y - other_bullet.world_y) ** 2)
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
        # Early return if effect is not visible
        if not is_on_screen(self.world_x, self.world_y, self.radius * 2, tank):
            return

        # Calculate screen position using tank's zoom factor
        screen_x = int((self.world_x - tank.world_x) * tank.zoom + tank.x)
        screen_y = int((self.world_y - tank.world_y) * tank.zoom + tank.y)

        # Scale radius with zoom factor
        drawn_radius = int(self.radius * tank.zoom)

        if 0 <= screen_x < SCREEN_WIDTH and 0 <= screen_y < SCREEN_HEIGHT:
            surface = pygame.Surface((drawn_radius * 2, drawn_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(surface, (*self.color, self.alpha), (drawn_radius, drawn_radius), drawn_radius)
            screen.blit(surface, (screen_x - drawn_radius, screen_y - drawn_radius))

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
    def __init__(self, x, y, shape_type, tank, outline_thickness=TILE_SIZE * 0.16):  # 4 pixels
        self.world_x = x
        self.world_y = y
        self.shape_type = shape_type
        self.angle = 0
        self.rotation_speed = random.uniform(0.01, 0.03)
        self.rotation_direction = random.choice([-1, 1])
        self.points = []
        self.base_outline_thickness = outline_thickness
        self.tank = tank

        if shape_type == "square":
            self.base_size = BASE_SQUARE_SIZE
        elif shape_type == "triangle":
            self.base_size = BASE_TRIANGLE_SIZE
        elif shape_type == "pentagon":
            self.base_size = BASE_PENTAGON_SIZE

        self.size = self.base_size
        self.health = {"square": 100, "triangle": 200, "pentagon": 300}[shape_type]
        self.max_health = self.health
        self.color = {"square": SQUAREYELLOW, "triangle": TRIANGLERED, "pentagon": PENTAGONBLUE}[shape_type]
        self.outline_color = {"square": SQUAREOUTLINE, "triangle": TRIANGLEOUTLINE, "pentagon": PENTAGONOUTLINE}[
            shape_type]
        self.alive = True
        self.update_points()

        self.orbit_radius = random.randint(TILE_SIZE, TILE_SIZE * 2)
        self.orbit_speed = random.uniform(0.005, 0.02)
        self.orbit_angle = random.uniform(0, 2 * math.pi)
        self.center_x = x
        self.center_y = y

    def take_damage(self, damage, attacker):
        self.health -= damage
        if self.health <= 0 and not isinstance(attacker, str):
            if isinstance(attacker, Player):
                # Player destroyed the shape (either by shooting or ramming)
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
            if (other.world_x - self.world_x) < 100 and (other.world_x - self.world_x) > -100 and (
                    other.world_y - self.world_y) < 100 and (other.world_y - self.world_y) > -100:
                if other != self and other.alive:
                    if self.check_collision(other):
                        self.resolve_collision(other)

    def update_points(self):
        self.points = []
        num_points = 5 if self.shape_type == "pentagon" else 4 if self.shape_type == "square" else 3
        for i in range(num_points):
            angle = self.angle + (math.pi * 2 * i / num_points)
            point_x = self.world_x + math.cos(angle) * self.base_size // 2
            point_y = self.world_y + math.sin(angle) * self.base_size // 2
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

        if not is_on_screen(self.world_x, self.world_y, self.base_size, tank):
            return

        screen_x = int((self.world_x - tank.world_x) * tank.zoom + tank.x)
        screen_y = int((self.world_y - tank.world_y) * tank.zoom + tank.y)

        scaled_size = int(self.base_size * tank.zoom)
        self.size = scaled_size  # Update size for collision detection

        screen_points = [
            (int((x - tank.world_x) * tank.zoom + tank.x),
             int((y - tank.world_y) * tank.zoom + tank.y))
            for x, y in self.points
        ]

        pygame.draw.polygon(screen, self.color, screen_points)
        pygame.draw.polygon(screen, self.outline_color, screen_points,
                            max(1, int(self.base_outline_thickness * tank.zoom)))

        if self.health < self.max_health:
            health_bar_width = self.base_size * tank.zoom
            health_bar_height = TILE_SIZE * 0.2
            health_percentage = self.health / self.max_health

            pygame.draw.rect(screen, HEALTHBARGREEN, (
                int(screen_x - health_bar_width // 2),
                int(screen_y + (self.base_size * tank.zoom // 2) + TILE_SIZE * 0.2 * tank.zoom),
                int(health_bar_width * health_percentage),
                int(health_bar_height)
            ))

            pygame.draw.rect(screen, HEALTHBAROUTLINE, (
                int(screen_x - health_bar_width // 2),
                int(screen_y + (self.base_size * tank.zoom // 2) + TILE_SIZE * 0.2 * tank.zoom),
                int(health_bar_width),
                int(health_bar_height)
            ), max(1, int(TILE_SIZE * 0.04 * tank.zoom)))  # 1 pixel outline relative to grid


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
    if tank.level >= 30 and tank.tank_type == "machine_gun":
        font = pygame.font.SysFont(None, 24)
        button_rect = pygame.Rect(UPGRADE_BUTTON_MARGIN, UPGRADE_BUTTON_MARGIN,
                                  UPGRADE_BUTTON_WIDTH, UPGRADE_BUTTON_HEIGHT)
        pygame.draw.rect(screen, WHITE, button_rect)
        pygame.draw.rect(screen, BLACK, button_rect, 2)

        text = font.render("Gunner", True, BLACK)
        text_rect = text.get_rect(center=button_rect.center)
        screen.blit(text, text_rect)
    # Add Quad Tank upgrade option for level 30 twin tanks
    if tank.level >= 30 and (tank.tank_type == "twin" or tank.tank_type == "flank"):
        font = pygame.font.SysFont(None, 24)
        button_rect = pygame.Rect(UPGRADE_BUTTON_MARGIN, UPGRADE_BUTTON_MARGIN,
                                  UPGRADE_BUTTON_WIDTH, UPGRADE_BUTTON_HEIGHT)
        pygame.draw.rect(screen, WHITE, button_rect)
        pygame.draw.rect(screen, BLACK, button_rect, 2)

        text = font.render("Quad Tank", True, BLACK)
        text_rect = text.get_rect(center=button_rect.center)
        screen.blit(text, text_rect)
    if tank.level >= 45 and tank.tank_type == "gunner":
        font = pygame.font.SysFont(None, 24)
        button_rect = pygame.Rect(UPGRADE_BUTTON_MARGIN, UPGRADE_BUTTON_MARGIN,
                                  UPGRADE_BUTTON_WIDTH, UPGRADE_BUTTON_HEIGHT)
        pygame.draw.rect(screen, WHITE, button_rect)
        pygame.draw.rect(screen, BLACK, button_rect, 2)

        text = font.render("Auto Gunner", True, BLACK)
        text_rect = text.get_rect(center=button_rect.center)
        screen.blit(text, text_rect)
    if tank.level >= 45 and tank.tank_type == "quad":
        font = pygame.font.SysFont(None, 24)
        button_y = UPGRADE_BUTTON_MARGIN

        for upgrade_type in ["Auto Quad", "Octo Tank"]:
            button_rect = pygame.Rect(UPGRADE_BUTTON_MARGIN, button_y,
                                      UPGRADE_BUTTON_WIDTH, UPGRADE_BUTTON_HEIGHT)
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

    if tank.level >= 30 and tank.tank_type == "machine_gun":
        button_rect = pygame.Rect(UPGRADE_BUTTON_MARGIN, UPGRADE_BUTTON_MARGIN,
                                  UPGRADE_BUTTON_WIDTH, UPGRADE_BUTTON_HEIGHT)
        if button_rect.collidepoint(mouse_pos):
            tank.upgrade_to_gunner()
            return True

    if tank.level >= 30 and (tank.tank_type == "twin" or tank.tank_type == "flank"):
        button_rect = pygame.Rect(UPGRADE_BUTTON_MARGIN, UPGRADE_BUTTON_MARGIN,
                                  UPGRADE_BUTTON_WIDTH, UPGRADE_BUTTON_HEIGHT)
        if button_rect.collidepoint(mouse_pos):
            tank.upgrade_to_quad()
            return True

    if tank.level >= 45 and tank.tank_type == "gunner":
        button_rect = pygame.Rect(UPGRADE_BUTTON_MARGIN, UPGRADE_BUTTON_MARGIN,
                                  UPGRADE_BUTTON_WIDTH, UPGRADE_BUTTON_HEIGHT)
        if button_rect.collidepoint(mouse_pos):
            tank.upgrade_to_auto_gunner()
            return True

    if tank.level >= 45 and tank.tank_type == "quad":
        # First button for Auto Quad
        auto_quad_rect = pygame.Rect(UPGRADE_BUTTON_MARGIN, UPGRADE_BUTTON_MARGIN,
                                     UPGRADE_BUTTON_WIDTH, UPGRADE_BUTTON_HEIGHT)
        # Second button for Octo Tank
        octo_rect = pygame.Rect(UPGRADE_BUTTON_MARGIN,
                                UPGRADE_BUTTON_MARGIN + UPGRADE_BUTTON_HEIGHT + UPGRADE_BUTTON_MARGIN,
                                UPGRADE_BUTTON_WIDTH, UPGRADE_BUTTON_HEIGHT)

        if auto_quad_rect.collidepoint(mouse_pos):
            tank.upgrade_to_auto_quad()
            return True
        elif octo_rect.collidepoint(mouse_pos):
            tank.upgrade_to_octo()
            return True

    return False

def create_attributes_surface(player):
    # Create a surface for attributes display
    ATTRIBUTES_SURFACE_WIDTH = ATTRIBUTE_BAR_WIDTH + 200
    ATTRIBUTES_SURFACE_HEIGHT = 300
    surface = pygame.Surface((ATTRIBUTES_SURFACE_WIDTH, ATTRIBUTES_SURFACE_HEIGHT), pygame.SRCALPHA)
    surface.fill((0, 0, 0, 0))

    # Draw available points indicator
    if player.available_points > 0:
        font = pygame.font.SysFont(None, 36)
        points_text = f"Upgrade Points: {player.available_points}"
        text_surface = font.render(points_text, True, RED)
        points_rect = text_surface.get_rect(topleft=(0, 0))
        surface.blit(text_surface, points_rect)

    # Draw attribute bars
    font = pygame.font.SysFont(None, 24)
    y = 50  # Start below points indicator

    # Store button positions for click detection
    player.upgrade_buttons = {}  # Add this as a class attribute to store button positions

    for attribute, level in player.attribute_levels.items():
        # Draw attribute name
        name_surface = font.render(attribute, True, BLACK)
        surface.blit(name_surface, (0, y))

        # Draw level bar background
        bar_rect = pygame.Rect(150, y, ATTRIBUTE_BAR_WIDTH, ATTRIBUTE_BAR_HEIGHT)
        pygame.draw.rect(surface, GRAY, bar_rect)

        # Draw filled portion of bar
        if level > 0:
            filled_width = int((ATTRIBUTE_BAR_WIDTH / player.max_attribute_level) * level)
            filled_rect = pygame.Rect(150, y, filled_width, ATTRIBUTE_BAR_HEIGHT)
            pygame.draw.rect(surface, GREEN, filled_rect)

        # Draw bar segments
        for i in range(player.max_attribute_level):
            segment_x = 150 + (ATTRIBUTE_BAR_WIDTH / player.max_attribute_level) * i
            pygame.draw.line(surface, BLACK,
                             (segment_x, y),
                             (segment_x, y + ATTRIBUTE_BAR_HEIGHT))

        # Draw plus button if upgrades available
        if player.available_points > 0 and level < player.max_attribute_level:
            button_x = 150 + ATTRIBUTE_BAR_WIDTH + 10
            button_rect = pygame.Rect(button_x, y, PLUS_BUTTON_SIZE, PLUS_BUTTON_SIZE)

            # Store the button position relative to the attribute surface
            player.upgrade_buttons[attribute] = {
                'rect': button_rect,
                'y_offset': y
            }

            pygame.draw.rect(surface, GREEN, button_rect)
            pygame.draw.rect(surface, BLACK, button_rect, 2)

            plus_font = pygame.font.SysFont(None, 30)
            plus_text = plus_font.render("+", True, BLACK)
            plus_rect = plus_text.get_rect(center=button_rect.center)
            surface.blit(plus_text, plus_rect)

        y += ATTRIBUTE_SECTION_HEIGHT

    return surface

def handle_attribute_upgrade(player, attribute_name=None, mouse_pos=None):
    if player.available_points <= 0:
        return False

    # Handle keyboard shortcuts
    if attribute_name is not None and isinstance(attribute_name, str):
        if player.attribute_levels[attribute_name] < player.max_attribute_level:
            player.attribute_levels[attribute_name] += 1
            player.available_points -= 1
            player.update_stats()
            player.attributes_need_update = True
            update_attribute_surface(player)
            return True
        return False

    # Handle mouse clicks
    if mouse_pos and hasattr(player, 'upgrade_buttons'):
        mouse_x, mouse_y = mouse_pos
        attributes_x = ATTRIBUTES_X
        attributes_y = ATTRIBUTES_Y - 50  # Adjust for the surface position offset

        # Check each button's absolute position
        for attribute, button_info in player.upgrade_buttons.items():
            absolute_rect = pygame.Rect(
                attributes_x + button_info['rect'].x,
                attributes_y + button_info['y_offset'],
                button_info['rect'].width,
                button_info['rect'].height
            )

            if absolute_rect.collidepoint(mouse_x, mouse_y):
                if player.attribute_levels[attribute] < player.max_attribute_level:
                    player.attribute_levels[attribute] += 1
                    player.available_points -= 1
                    player.update_stats()
                    player.attributes_need_update = True
                    update_attribute_surface(player)
                    return True

    return False

def update_attribute_surface(player):
    # Update the cached surface only when needed
    player.attributes_surface = create_attributes_surface(player)
    player.attributes_need_update = False

def draw_attributes(screen, player):
    # Create initial surface if it doesn't exist
    if not hasattr(player, 'attributes_surface') or player.attributes_need_update:
        update_attribute_surface(player)

    # Draw the cached surface
    screen.blit(player.attributes_surface, (ATTRIBUTES_X, ATTRIBUTES_Y - 50))

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
    scaled_tile_size = int(TILE_SIZE * tank.zoom)
    visible_width = int(SCREEN_WIDTH / tank.zoom)
    visible_height = int(SCREEN_HEIGHT / tank.zoom)

    cols = visible_width // TILE_SIZE + 2
    rows = visible_height // TILE_SIZE + 2

    offset_x = ((tank.world_x - tank.x / tank.zoom) % TILE_SIZE) * tank.zoom
    offset_y = ((tank.world_y - tank.y / tank.zoom) % TILE_SIZE) * tank.zoom

    start_world_x = tank.world_x - tank.x / tank.zoom
    start_world_y = tank.world_y - tank.y / tank.zoom

    for row in range(rows):
        for col in range(cols):
            tile_x = col * scaled_tile_size - offset_x
            tile_y = row * scaled_tile_size - offset_y

            world_tile_x = start_world_x + col * TILE_SIZE
            world_tile_y = start_world_y + row * TILE_SIZE

            if (0 <= world_tile_x < WORLD_WIDTH and 0 <= world_tile_y < WORLD_HEIGHT):
                pygame.draw.rect(screen, GRIDLINEGREY,
                                 (tile_x, tile_y, scaled_tile_size, scaled_tile_size), 1)
            else:
                pygame.draw.rect(screen, OUTOFBOUNDSCREENGREY,
                                 (tile_x, tile_y, scaled_tile_size, scaled_tile_size))
                pygame.draw.rect(screen, OUTOFBOUNDSGRIDLINEGREY,
                                 (tile_x, tile_y, scaled_tile_size, scaled_tile_size), 1)


def format_time(seconds):
    minutes, seconds = divmod(int(seconds), 60)
    return f"{minutes:02d}:{seconds:02d}"


def death_screen(screen, clock, killer_object, survival_time, final_score):
    transparent_surface = pygame.Surface((SCREEN_WIDTH + 20, SCREEN_HEIGHT), pygame.SRCALPHA)
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
        pygame.draw.rect(screen, GRAY, (0, 0, SCREEN_WIDTH + 20, screen_y))
    if screen_y + WORLD_HEIGHT < SCREEN_HEIGHT:
        pygame.draw.rect(screen, GRAY,
                         (0, screen_y + WORLD_HEIGHT, SCREEN_WIDTH + 20, SCREEN_HEIGHT - (screen_y + WORLD_HEIGHT)))
    if screen_x > 0:  # left border
        pygame.draw.rect(screen, GRAY, (0, 0, screen_x, SCREEN_HEIGHT))
    if screen_x + WORLD_WIDTH < SCREEN_WIDTH:  # right border
        pygame.draw.rect(screen, GRAY,
                         (screen_x + WORLD_WIDTH, 0, SCREEN_WIDTH - (screen_x + WORLD_WIDTH) + 20, SCREEN_HEIGHT))


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
                if event.button == 1:  # Left mouse button
                    # Handle attribute upgrades first
                    if handle_attribute_upgrade(player, mouse_pos=event.pos):
                        continue  # Skip other click handling if upgrade was successful
                    # Then handle tank upgrades
                    if handle_upgrade_click(player, event.pos):
                        continue  # Skip shooting if upgrade was successful
                    # Finally handle shooting
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
                # Add number key handling for attributes
                elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4,
                                   pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8]:
                    # Map number keys to attributes
                    attribute_map = {
                        pygame.K_1: "Health Regen",
                        pygame.K_2: "Max Health",
                        pygame.K_3: "Body Damage",
                        pygame.K_4: "Bullet Speed",
                        pygame.K_5: "Bullet Penetration",
                        pygame.K_6: "Bullet Damage",
                        pygame.K_7: "Reload",
                        pygame.K_8: "Movement Speed"
                    }
                    handle_attribute_upgrade(player, attribute_map[event.key])

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
            player.update_nearest_target(shapes, enemies if include_enemies else [])

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
        draw_attributes(screen, player)

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
            halfscore = scores[player.level // 2]
            player = Player()
            player.score = halfscore
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
