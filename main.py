import pygame
import math


# Initialize pygame
pygame.init()


# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
TILE_SIZE = 50  # Each tile is a 50x50 pixel square


# World dimensions
WORLD_WIDTH = 5000
WORLD_HEIGHT = 5000


# Colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
RED = (255, 0, 0)
GREEN = (0, 255, 0)


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
       self.world_x = WORLD_WIDTH // 2  # Player's position in the world coordinates
       self.world_y = WORLD_HEIGHT // 2  # Start tank in the middle of the world
       self.bullets = []  # List to hold bullets
       self.autofire = False  # Autofire state
       self.shoot_cooldown = 0  # Cooldown timer for autofire
       self.cannon_thickness = 10  # Thicker cannon like a Diep.io tank


   def draw(self):
       # Draw the tank body (circle)
       pygame.draw.circle(screen, self.color, (self.x, self.y), self.size)


       # Draw the cannon to indicate direction (thicker line for cannon)
       cannon_length = 50
       end_x = self.x + math.cos(self.angle) * cannon_length
       end_y = self.y + math.sin(self.angle) * cannon_length
       pygame.draw.line(screen, BLACK, (self.x, self.y), (end_x, end_y), self.cannon_thickness)


   def update(self, keys_pressed):
       # Update world coordinates based on movement
       if keys_pressed[pygame.K_w]:
           self.world_y -= self.speed  # Move the world down (player goes up)
       if keys_pressed[pygame.K_s]:
           self.world_y += self.speed  # Move the world up (player goes down)
       if keys_pressed[pygame.K_a]:
           self.world_x -= self.speed  # Move the world right (player goes left)
       if keys_pressed[pygame.K_d]:
           self.world_x += self.speed  # Move the world left (player goes right)


       # Clamp player's world position within world bounds (preventing from going off the edge)
       self.world_x = max(self.size, min(WORLD_WIDTH - self.size, self.world_x))
       self.world_y = max(self.size, min(WORLD_HEIGHT - self.size, self.world_y))


   def rotate_to_mouse(self, mouse_pos):
       # Calculate the angle to point towards the mouse
       dx = mouse_pos[0] - self.x
       dy = mouse_pos[1] - self.y
       self.angle = math.atan2(dy, dx)


   def shoot(self):
       # Create a new bullet and add it to the list
       bullet_speed = 10
       bullet = Bullet(self.world_x, self.world_y, math.cos(self.angle) * bullet_speed, math.sin(self.angle) * bullet_speed)
       self.bullets.append(bullet)


   def handle_autofire(self):
       # Handle the autofire mechanism
       if self.autofire and self.shoot_cooldown <= 0:
           self.shoot()
           self.shoot_cooldown = 15  # Adjust cooldown for autofire rate
       if self.shoot_cooldown > 0:
           self.shoot_cooldown -= 1


# Bullet class with lifespan
class Bullet:
   def __init__(self, x, y, vel_x, vel_y):
       self.world_x = x
       self.world_y = y
       self.vel_x = vel_x
       self.vel_y = vel_y
       self.radius = 10  # Larger bullet radius like in Diep.io
       self.color = RED
       self.lifespan = 120  # Bullet will last for 2 seconds (120 frames at 60 FPS)


   def update(self):
       # Move the bullet in world coordinates
       self.world_x += self.vel_x
       self.world_y += self.vel_y


       # Decrease lifespan over time
       self.lifespan -= 1


       # Prevent the bullet from going beyond the world bounds
       if self.world_x - self.radius < 0 or self.world_x + self.radius > WORLD_WIDTH:
           self.vel_x = 0  # Stop the bullet if it hits the world border
       if self.world_y - self.radius < 0 or self.world_y + self.radius > WORLD_HEIGHT:
           self.vel_y = 0


   def draw(self, tank):
       # Draw the bullet relative to the player's screen position
       screen_x = self.world_x - tank.world_x + tank.x
       screen_y = self.world_y - tank.world_y + tank.y
       pygame.draw.circle(screen, self.color, (int(screen_x), int(screen_y)), self.radius)


   def off_screen(self):
       # Check if the bullet is outside the world bounds or if its lifespan is over
       return self.world_x < 0 or self.world_x > WORLD_WIDTH or self.world_y < 0 or self.world_y > WORLD_HEIGHT or self.lifespan <= 0


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


# Draw the world border by filling the area outside the world with gray
def draw_world_border(tank):
   # Calculate the player's visible position in the world relative to the screen
   screen_x = tank.x - tank.world_x
   screen_y = tank.y - tank.world_y


   # Define the area that represents the world in screen coordinates
   world_rect = pygame.Rect(screen_x, screen_y, WORLD_WIDTH, WORLD_HEIGHT)


   # Fill gray areas outside the world bounds
   # Top gray area (above the world)
   if screen_y > 0:
       pygame.draw.rect(screen, GRAY, (0, 0, SCREEN_WIDTH, screen_y))
   # Bottom gray area (below the world)
   if screen_y + WORLD_HEIGHT < SCREEN_HEIGHT:
       pygame.draw.rect(screen, GRAY, (0, screen_y + WORLD_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT - (screen_y + WORLD_HEIGHT)))
   # Left gray area (left of the world)
   if screen_x > 0:
       pygame.draw.rect(screen, GRAY, (0, 0, screen_x, SCREEN_HEIGHT))
   # Right gray area (right of the world)
   if screen_x + WORLD_WIDTH < SCREEN_WIDTH:
       pygame.draw.rect(screen, GRAY, (screen_x + WORLD_WIDTH, 0, SCREEN_WIDTH - (screen_x + WORLD_WIDTH), SCREEN_HEIGHT))


# Draw the autofire indicator
def draw_autofire_indicator(tank):
   # Display autofire state at the top left of the screen
   font = pygame.font.SysFont(None, 24)
   autofire_text = "Autofire: ON" if tank.autofire else "Autofire: OFF"
   autofire_color = GREEN if tank.autofire else RED
   text_surface = font.render(autofire_text, True, autofire_color)
   screen.blit(text_surface, (10, 10))


# Main loop
def game_loop():
   tank = Tank()
   running = True


   while running:
       screen.fill(WHITE)


       # Event handling
       for event in pygame.event.get():
           if event.type == pygame.QUIT:
               running = False
           elif event.type == pygame.MOUSEBUTTONDOWN:  # Shoot when mouse button is pressed
               tank.shoot()
           elif event.type == pygame.KEYDOWN:
               if event.key == pygame.K_e:  # Toggle autofire on 'E' key press
                   tank.autofire = not tank.autofire


       # Get pressed keys
       keys_pressed = pygame.key.get_pressed()


       # Update tank movement (world coordinates change)
       tank.update(keys_pressed)


       # Handle autofire shooting
       tank.handle_autofire()


       # Get mouse position and rotate the tank to face the cursor
       mouse_pos = pygame.mouse.get_pos()
       tank.rotate_to_mouse(mouse_pos)


       # Draw the grid-based terrain
       draw_grid(tank)


       # Draw the world border (with gray outside)
       draw_world_border(tank)


       # Update and draw all bullets
       for bullet in tank.bullets[:]:
           bullet.update()
           bullet.draw(tank)


           # Remove bullet if it goes off-screen or its lifespan is over
           if bullet.off_screen():
               tank.bullets.remove(bullet)


       # Draw the tank in the center
       tank.draw()


       # Draw the autofire indicator
       draw_autofire_indicator(tank)


       # Update the screen
       pygame.display.flip()


       # Limit the frame rate
       clock.tick(60)


# Start the game
game_loop()


# Quit pygame
pygame.quit()



