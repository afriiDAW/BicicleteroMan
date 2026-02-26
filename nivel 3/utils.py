import pygame
import os
from constants import WIDTH, HEIGHT, ROAD_WIDTH, ROAD_X


def draw_road(surface):
    surface.fill((34, 139, 34))
    pygame.draw.rect(surface, (50, 50, 50), (ROAD_X, 0, ROAD_WIDTH, HEIGHT))
    lane_x = ROAD_X + ROAD_WIDTH // 2 - 2
    for y in range(0, HEIGHT, 40):
        pygame.draw.rect(surface, (255, 255, 255), (lane_x, y + (y // 40) % 2 * 20, 4, 20))


def draw_ui(surface, lives, score):
    font = pygame.font.SysFont(None, 28)
    lives_txt = font.render(f'Vidas: {lives}', True, (255, 255, 255))
    score_txt = font.render(f'Puntos: {score}', True, (255, 255, 255))
    surface.blit(lives_txt, (10, 10))
    # place score to the right of lives
    surface.blit(score_txt, (10 + lives_txt.get_width() + 20, 10))


def load_backgrounds(base_path, names, size):
    backgrounds = []
    for name in names:
        path = os.path.join(base_path, name)
        if os.path.exists(path):
            try:
                img = pygame.image.load(path).convert()
                img = pygame.transform.scale(img, size)
                backgrounds.append(img)
            except Exception:
                pass
    return backgrounds
