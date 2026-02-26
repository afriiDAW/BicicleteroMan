import pygame
import random
from constants import WIDTH, HEIGHT, ROAD_WIDTH, ROAD_X


class Player:
    def __init__(self):
        self.width = 40
        self.height = 60
        self.x = WIDTH // 2 - self.width // 2
        self.y = HEIGHT - self.height - 30
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.speed = 5
        # facing vector used for vision cone; initially pointing up
        self.facing = pygame.math.Vector2(0, -1)

    def handle_input(self, keys):
        # compute movement delta.  the facing vector is updated based on the
        # *last* direction of movement (horizontal or vertical) so that the
        # vision cone points in the direction the player is currently heading.
        dx = 0
        dy = 0
        if keys[pygame.K_LEFT]:
            dx -= self.speed
        if keys[pygame.K_RIGHT]:
            dx += self.speed
        if keys[pygame.K_UP]:
            dy -= self.speed
        if keys[pygame.K_DOWN]:
            dy += self.speed

        # horizontal takes priority over vertical when both are pressed, since
        # the user explicitly wanted left/right to flip the cone sideways.
        if dx < 0:
            self.facing = pygame.math.Vector2(-1, 0)
        elif dx > 0:
            self.facing = pygame.math.Vector2(1, 0)
        elif dy < 0:
            self.facing = pygame.math.Vector2(0, -1)
        elif dy > 0:
            self.facing = pygame.math.Vector2(0, 1)

        self.rect.x += dx
        self.rect.y += dy

        # constrain to road
        if self.rect.left < ROAD_X + 10:
            self.rect.left = ROAD_X + 10
        if self.rect.right > ROAD_X + ROAD_WIDTH - 10:
            self.rect.right = ROAD_X + ROAD_WIDTH - 10
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT - 10:
            self.rect.bottom = HEIGHT - 10

    def draw(self, surface, invulnerable=False):
        color = (30, 144, 255)
        if invulnerable:
            if (pygame.time.get_ticks() // 100) % 2 == 0:
                color = (135, 206, 250)
            else:
                color = (255, 255, 255)
        pygame.draw.rect(surface, color, self.rect, border_radius=6)


class Obstacle:
    def __init__(self):
        # obstacles are now circles defined by radius
        self.radius = random.randint(15, 40)
        self.x = random.randint(ROAD_X + self.radius + 10, ROAD_X + ROAD_WIDTH - self.radius - 10)
        self.y = 0
        # keep rect for collision detection, centered at the circle
        self.rect = pygame.Rect(self.x - self.radius, self.y - self.radius, 
                                 self.radius * 2, self.radius * 2)
        # for convenience store width/height
        self.width = self.radius * 2
        self.height = self.radius * 2

    def update(self):
        pass

    def draw(self, surface):
        pygame.draw.circle(surface, (139, 69, 19), (self.x, self.y), self.radius)


class Dog:
    def __init__(self, player):
        self.width = 40
        self.height = 40
        # spawn at bottom edge like the player
        side = random.choice(('left', 'right'))
        if side == 'left':
            self.x = ROAD_X + 10
        else:
            self.x = ROAD_X + ROAD_WIDTH - self.width - 10
        # always start on the lower border of the screen
        self.y = HEIGHT - self.height - 30
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.speed = player.speed

    def update(self, target_rect):
        dx = target_rect.centerx - self.rect.centerx
        dy = target_rect.centery - self.rect.centery
        dist = (dx * dx + dy * dy) ** 0.5
        if dist <= 0:
            return
        step = min(self.speed, dist)
        self.rect.x += int(dx / dist * step)
        self.rect.y += int(dy / dist * step)
        if self.rect.left < ROAD_X + 10:
            self.rect.left = ROAD_X + 10
        if self.rect.right > ROAD_X + ROAD_WIDTH - 10:
            self.rect.right = ROAD_X + ROAD_WIDTH - 10
        if self.rect.top < 10:
            self.rect.top = 10
        if self.rect.bottom > HEIGHT - 10:
            self.rect.bottom = HEIGHT - 10

    def draw(self, surface):
        pygame.draw.rect(surface, (200, 0, 0), self.rect, border_radius=6)
