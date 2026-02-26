import pygame
import sys
import os
import random

from constants import WIDTH, HEIGHT, FPS, DOG_SPAWN_MS, LEVEL_TIME_MS, INVULNERABILITY_MS, START_LIVES, DOG_VISIBLE_MS
from entities import Player, Obstacle, Dog
from utils import draw_road, draw_ui, load_backgrounds



if __name__ == '__main__':
    from game import Game

    Game().run()
