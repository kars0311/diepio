import pygame
import math
import random

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)

# Create the screen object
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Diep.io Singleplayer")

# Clock object to control game speed
clock = pygame.time.Clock()


# Tank class
class Tank:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 40
        self.speed = 5
        self.angle = 0
        self.color = BLUE
        self.bullets = []

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)
        # Draw the cannon
        cannon_length = 40
        end_x = self.x + math.cos(self.angle) * cannon_length
        end_y = self.y + math.sin(self.angle) * cannon_length
        pygame.draw.line(screen, BLACK, (self.x, self.y), (end_x, end_y), 5)

    def update(self, keys_pressed):
        if keys_pressed[pygame.K_w]:
            self.x += math.cos(self.angle) * self.speed
            self.y += math.sin(self.angle) * self.speed
        if keys_pressed[pygame.K_s]:
            self.x -= math.cos(self.angle) * self.speed
            self.y -= math.sin(self.angle) * self.speed
        if keys_pressed[pygame.K_a]:
            self.angle -= 0.05
        if keys_pressed[pygame.K_d]:
            self.angle += 0.05

        # Boundaries
        if self.x < 0: self.x = 0
        if self.x > SCREEN_WIDTH: self.x = SCREEN_WIDTH
        if self.y < 0: self.y = 0
        if self.y > SCREEN_HEIGHT: self.y = SCREEN_HEIGHT

    def shoot(self):
        # Create a bullet in the direction of the tank's angle
        bullet = Bullet(self.x, self.y, self.angle)
        self.bullets.append(bullet)


# Bullet class
class Bullet:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = 10
        self.radius = 5
        self.color = BLACK

    def update(self):
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)


# Enemy class
class Enemy:
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.size = 30
        self.color = RED
        self.speed = 2

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)

    def update(self):
        # Move randomly for now (simple AI)
        self.x += random.choice([-1, 1]) * self.speed
        self.y += random.choice([-1, 1]) * self.speed
        # Boundaries
        if self.x < 0: self.x = 0
        if self.x > SCREEN_WIDTH: self.x = SCREEN_WIDTH
        if self.y < 0: self.y = 0
        if self.y > SCREEN_HEIGHT: self.y = SCREEN_HEIGHT


def handle_collisions(bullets, enemies):
    for bullet in bullets:
        for enemy in enemies:
            dist = math.hypot(bullet.x - enemy.x, bullet.y - enemy.y)
            if dist < bullet.radius + enemy.size:
                bullets.remove(bullet)
                enemies.remove(enemy)
                break


# Main loop
def game_loop():
    tank = Tank(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    enemies = [Enemy() for _ in range(5)]
    running = True

    while running:
        screen.fill(WHITE)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    tank.shoot()

        # Get pressed keys
        keys_pressed = pygame.key.get_pressed()

        # Update tank and bullets
        tank.update(keys_pressed)
        for bullet in tank.bullets:
            bullet.update()

        # Update enemies
        for enemy in enemies:
            enemy.update()

        # Handle bullet-enemy collisions
        handle_collisions(tank.bullets, enemies)

        # Draw everything
        tank.draw()
        for bullet in tank.bullets:
            bullet.draw()
        for enemy in enemies:
            enemy.draw()

        # Update the screen
        pygame.display.flip()

        # Limit the frame rate
        clock.tick(60)


# Start the game
game_loop()

# Quit pygame
pygame.quit()