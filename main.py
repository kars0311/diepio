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
       self.world_x = WORLD_WIDTH // 2  # Player's position in the world coordinates
       self.world_y = WORLD_HEIGHT // 2  # Start tank in the middle of the world
       self.bullets = []  # List to hold bullets
       self.autofire = False  # Autofire state
       self.autospin = False  # Autospin state
       self.shoot_cooldown = 0  # Cooldown timer for autofire
       self.cannon_length = 75
       self.cannon_thickness = 35  # Updated cannon thickness
       self.recoil_velocity_x = 0  # Recoil velocity in x direction
       self.recoil_velocity_y = 0  # Recoil velocity in y direction
       self.recoil_dampening = 0.95  # Dampening factor for recoil


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


       # Apply recoil
       recoil_force = 0.5  # Adjust this value to change the strength of the recoil
       self.recoil_velocity_x -= math.cos(self.angle) * recoil_force
       self.recoil_velocity_y -= math.sin(self.angle) * recoil_force


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
               if event.key == pygame.K_c:  # Toggle autospin on 'C' key press
                   tank.autospin = not tank.autospin
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
       # Draw the world border (before bullets, so bullets are on top)
       draw_world_border(tank)
       # Update and draw all bullets
       for bullet in tank.bullets[:]:
           bullet.update()
           bullet.draw(tank)
           if bullet.off_screen():
               tank.bullets.remove(bullet)
       # Draw the tank in the center
       tank.draw()
       # Draw the autofire and autospin indicators
       draw_autofire_indicator(tank)
       draw_autospin_indicator(tank)
       # Update the screen
       pygame.display.flip()
       # Limit the frame rate
       clock.tick(60)




# Start the game
game_loop()


# Quit pygame
pygame.quit()

