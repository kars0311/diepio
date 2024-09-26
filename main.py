import pygame
import math
import random

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 50  # Each tile is a 50x50 pixel square


# World dimensions
WORLD_WIDTH = 5000
WORLD_HEIGHT = 5000

# Minimap visibility
minimap_visible = True  # Start with the minimap visible by default

# Minimap dimensions
MINIMAP_WIDTH = 200
MINIMAP_HEIGHT = 200
MINIMAP_SCALE = MINIMAP_WIDTH / WORLD_WIDTH


# Colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255,255,0)
BORDER_COLOR = (255, 0, 0)  # Red for the world border


# Create the screen object
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Diep.io Terrain Generation")


# Clock object to control game speed
clock = pygame.time.Clock()

# Tank class
class Tank:
   def __init__(self):
       self.x = SCREEN_WIDTH // 2
       self.y = SCREEN_HEIGHT // 2
       self.size = 40  # Tank body size
       self.speed = 5
       self.angle = 0
       self.color = BLUE
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
       self.health = 500  # New: Player health
       self.max_health = 500  # New: Maximum player health


   # ... (other methods remain the same)


   def draw(self):
       # Calculate cannon end points
       cannon_end_x = self.x + math.cos(self.angle) * self.cannon_length
       cannon_end_y = self.y + math.sin(self.angle) * self.cannon_length


       # Calculate cannon corners
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


       # Draw the cannon as a polygon
       pygame.draw.polygon(screen, (150, 150, 150), cannon_corners)


       # Draw the tank body (circle)
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
       # Movement vector
       move_x = 0
       move_y = 0


       # Update movement based on key presses
       if keys_pressed[pygame.K_w]:
           move_y = -1
       if keys_pressed[pygame.K_s]:
           move_y = 1
       if keys_pressed[pygame.K_a]:
           move_x = -1
       if keys_pressed[pygame.K_d]:
           move_x = 1


       # Normalize movement to prevent diagonal speed boost
       if move_x != 0 or move_y != 0:
           magnitude = math.sqrt(move_x ** 2 + move_y ** 2)
           move_x /= magnitude
           move_y /= magnitude


       # Apply recoil
       move_x += self.recoil_velocity_x
       move_y += self.recoil_velocity_y


       # Update world coordinates
       self.world_x += move_x * self.speed
       self.world_y += move_y * self.speed


       # Clamp player's world position within world bounds (preventing from going off the edge)
       self.world_x = max(self.size, min(WORLD_WIDTH - self.size, self.world_x))
       self.world_y = max(self.size, min(WORLD_HEIGHT - self.size, self.world_y))


       # Apply dampening to recoil
       self.recoil_velocity_x *= self.recoil_dampening
       self.recoil_velocity_y *= self.recoil_dampening


       # Ensure recoil doesn't exceed maximum speed
       recoil_speed = math.sqrt(self.recoil_velocity_x ** 2 + self.recoil_velocity_y ** 2)
       if recoil_speed > self.max_recoil_speed:
           factor = self.max_recoil_speed / recoil_speed
           self.recoil_velocity_x *= factor
           self.recoil_velocity_y *= factor


   def rotate_to_mouse(self, mouse_pos):
       # Check if autospin is active
       if self.autospin:
           # Slowly rotate clockwise
           self.angle += 0.05  # Adjust the speed of the spin as desired
       else:
           # Calculate the angle to point towards the mouse
           dx = mouse_pos[0] - self.x
           dy = mouse_pos[1] - self.y
           self.angle = math.atan2(dy, dx)


   def shoot(self):
       # Calculate the position at the tip of the cannon
       bullet_x = self.world_x + math.cos(self.angle) * (self.cannon_length + self.size)
       bullet_y = self.world_y + math.sin(self.angle) * (self.cannon_length + self.size)


       # Create a new bullet and add it to the list
       bullet_speed = 10
       bullet = Bullet(bullet_x, bullet_y, math.cos(self.angle) * bullet_speed, math.sin(self.angle) * bullet_speed)
       self.bullets.append(bullet)


       # Apply recoil as a boost
       recoil_force = 0.2  # Reduced recoil force
       self.recoil_velocity_x -= math.cos(self.angle) * recoil_force
       self.recoil_velocity_y -= math.sin(self.angle) * recoil_force


   def handle_autofire(self):
       # Handle the autofire mechanism
       if self.autofire and self.shoot_cooldown <= 0:
           self.shoot()
           self.shoot_cooldown = 15  # Adjust cooldown for autofire rate
       if self.shoot_cooldown > 0:
           self.shoot_cooldown -= 1


   def take_damage(self, damage):
       self.health -= damage
       if self.health <= 0:
           self.health = 0
           print("Game Over!")  # You can implement a proper game over screen here


   def check_collision_with_shapes(self, shapes):
       for shape in shapes:
           if shape.alive:
               distance = math.sqrt((self.world_x - shape.world_x) ** 2 + (self.world_y - shape.world_y) ** 2)
               if distance < self.size + shape.size // 2:
                   damage_to_player = 5  # Adjust this value to change damage dealt to player
                   damage_to_shape = 10  # Adjust this value to change damage dealt to shape
                   self.take_damage(damage_to_player)
                   shape.take_damage(damage_to_shape)


                   # Push the tank away from the shape
                   angle = math.atan2(self.world_y - shape.world_y, self.world_x - shape.world_x)
                   push_distance = (self.size + shape.size // 2) - distance
                   self.world_x += math.cos(angle) * push_distance
                   self.world_y += math.sin(angle) * push_distance

# Bullet class with lifespan
class Bullet:
  def __init__(self, x, y, vel_x, vel_y):
      self.world_x = x
      self.world_y = y
      self.vel_x = vel_x
      self.vel_y = vel_y
      self.radius = 15
      self.color = BLUE
      self.lifespan = 120
      self.damage = 60  # Damage dealt by the bullet

  def update(self):
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
      return self.world_x < 0 or self.world_x > WORLD_WIDTH or self.world_y < 0 or self.world_y > WORLD_HEIGHT or self.lifespan <= 0


  def check_collision(self, shapes):
      for shape in shapes:
          if shape.alive:  # Only check collision with alive shapes
              distance = math.sqrt((self.world_x - shape.world_x) ** 2 + (self.world_y - shape.world_y) ** 2)
              if distance < self.radius + shape.size // 2:
                  shape.take_damage(self.damage)
                  return True
      return False


class Shape:
    def __init__(self, x, y, shape_type):
        self.world_x = x
        self.world_y = y
        self.shape_type = shape_type

        if shape_type == "square":
            self.size = 40
            self.health = 100
            self.max_health = 100
            self.color = YELLOW
        elif shape_type == "triangle":
            self.size = 60
            self.health = 200
            self.max_health = 200
            self.color = RED
        elif shape_type == "pentagon":
            self.size = 80
            self.health = 800
            self.max_health = 800
            self.color = BLUE

        self.alive = True

    def draw(self, tank):
        if not self.alive:
            return

        screen_x = self.world_x - tank.world_x + tank.x
        screen_y = self.world_y - tank.world_y + tank.y

        # Draw shapes based on their type
        if self.shape_type == "square":
            pygame.draw.rect(screen, self.color,
                             (screen_x - self.size // 2, screen_y - self.size // 2, self.size, self.size))
        elif self.shape_type == "triangle":
            points = [(screen_x, screen_y - self.size // 2),
                      (screen_x - self.size // 2, screen_y + self.size // 2),
                      (screen_x + self.size // 2, screen_y + self.size // 2)]
            pygame.draw.polygon(screen, self.color, points)
        elif self.shape_type == "pentagon":
            pygame.draw.circle(screen, self.color, (screen_x, screen_y), self.size // 2)

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
            self.regenerate()

    def regenerate(self):
        # Move the shape to a new random location in the world
        self.world_x = random.randint(100, WORLD_WIDTH - 100)
        self.world_y = random.randint(100, WORLD_HEIGHT - 100)

        # Reset health
        self.health = self.max_health

        # Mark the shape as alive
        self.alive = True


# Draw the autofire indicator
def draw_autofire_indicator(tank):
 font = pygame.font.SysFont(None, 24)
 autofire_text = "Autofire: ON" if tank.autofire else "Autofire: OFF"
 autofire_color = GREEN if tank.autofire else RED
 text_surface = font.render(autofire_text, True, autofire_color)
 screen.blit(text_surface, (10, 10))

# Draw the autospin indicator
def draw_autospin_indicator(tank):
 font = pygame.font.SysFont(None, 24)
 autospin_text = "Autospin: ON" if tank.autospin else "Autospin: OFF"
 autospin_color = GREEN if tank.autospin else RED
 text_surface = font.render(autospin_text, True, autospin_color)
 screen.blit(text_surface, (10, 40))  # Display below the autofire indicator

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
         pygame.draw.rect(screen, GRAY, (tile_x, tile_y, TILE_SIZE, TILE_SIZE), 1)

# Draw the world border
def draw_world_border(tank):
 screen_x = tank.x - tank.world_x
 screen_y = tank.y - tank.world_y
 world_rect = pygame.Rect(screen_x, screen_y, WORLD_WIDTH, WORLD_HEIGHT)
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

# Initialize a list of shapes in the game
shapes = [
]


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


for i in range(0,40):
    shapes.append(Shape(random.randint(100,4900),random.randint(100,4900),"square"))
    shapes.append(Shape(random.randint(100,4900),random.randint(100,4900),"triangle"))
    shapes.append(Shape(random.randint(100,4900),random.randint(100,4900),"pentagon"))

def game_loop():
    tank = Tank()
    running = True
    minimap_visible = True  # Track minimap visibility

    while running:
        screen.fill(WHITE)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                tank.shoot()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    tank.autofire = not tank.autofire
                if event.key == pygame.K_c:
                    tank.autospin = not tank.autospin
                if event.key == pygame.K_TAB:  # Toggle minimap with Tab
                    minimap_visible = not minimap_visible

        keys_pressed = pygame.key.get_pressed()
        tank.update(keys_pressed)
        tank.handle_autofire()
        mouse_pos = pygame.mouse.get_pos()
        tank.rotate_to_mouse(mouse_pos)

        # Check for collisions between tank and shapes
        tank.check_collision_with_shapes(shapes)

        # Draw the grid and world border
        draw_grid(tank)
        draw_world_border(tank)

        # Update and draw shapes
        for shape in shapes:
            shape.draw(tank)

        # Update and draw bullets
        for bullet in tank.bullets[:]:
            bullet.update()
            if bullet.check_collision(shapes):
                tank.bullets.remove(bullet)
            bullet.draw(tank)
            if bullet.off_screen():
                tank.bullets.remove(bullet)

        # Draw the tank
        tank.draw()

        # Draw the minimap if it's visible
        if minimap_visible:
            draw_minimap(tank, shapes)

        # Draw the minimap indicator
        draw_minimap_indicator(minimap_visible)

        # Draw the autofire and autospin indicators
        draw_autofire_indicator(tank)
        draw_autospin_indicator(tank)

        pygame.display.flip()
        clock.tick(60)

# Start the game
game_loop()


# Quit pygame
pygame.quit()
