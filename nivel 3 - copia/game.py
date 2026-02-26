import pygame
import sys
import os
import random

from constants import (
    WIDTH,
    HEIGHT,
    FPS,
    DOG_SPAWN_MS,
    LEVEL_TIME_MS,
    INVULNERABILITY_MS,
    START_LIVES,
    DOG_VISIBLE_MS,
    SCREEN_INVULNERABILITY_MS,
    DOG_ATTACK_DELAY_MS,
    VISION_ANGLE,
    VISION_DISTANCE,
    SHOW_VISION_CONE,
)
from entities import Player, Obstacle, Dog
from utils import draw_road, draw_ui, load_backgrounds


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Bici Obstáculos')
        self.clock = pygame.time.Clock()

        base = os.path.dirname(__file__)
        self.backgrounds = load_backgrounds(base, ('camino1.png', 'camino2.png', 'camino3.png'), (WIDTH, HEIGHT))
        self.bg_index = 0

        self.player = Player()
        self.dog = None
        self.dog_timer = 0
        self.dog_visible_until = 0
        # keep a short history of player positions (timestamp, rect) to implement
        # the 0.5 second delay when the dog is active
        self.player_history = []  # list of (ms, pygame.Rect)
        self.obstacles = self.generate_obstacles(avoid_rects=[self.player.rect])

        self.level_time_left = LEVEL_TIME_MS
        self.level_complete = False
        self.lives = START_LIVES
        self.invulnerable = False
        self.invulnerable_start = 0
        # helps track how long the current invulnerability should last
        self.invulnerable_duration = 0
        self.game_over = False
        # score tracking
        self.score = 0
        # track how many lives have been earned from points
        self.lives_earned_from_score = 0

    def generate_obstacles(self, avoid_rects=None, min_count=3, max_count=7):
        obs = []
        count = random.randint(min_count, max_count)
        attempts = 0
        # minimum vertical gap between obstacles (based on player height)
        min_gap = getattr(self.player.rect, 'height', 60) + 20
        while len(obs) < count and attempts < count * 30:
            attempts += 1
            o = Obstacle()
            o_y = random.randint(60, HEIGHT - o.height - 60)
            o.rect.y = o_y
            o.y = o_y + o.radius  # keep y in sync with rect position
            collides = False

            # avoid direct rectangle overlap
            for existing in obs:
                if o.rect.colliderect(existing.rect):
                    collides = True
                    break
                # ensure vertical spacing between centers is at least min_gap
                vert_gap = abs(o.rect.centery - existing.rect.centery) - (o.height + existing.height) / 2
                if vert_gap < min_gap:
                    collides = True
                    break

            if not collides and avoid_rects:
                for r in avoid_rects:
                    if o.rect.colliderect(r):
                        collides = True
                        break
                    vert_gap = abs(o.rect.centery - r.centery) - (o.height + r.height) / 2
                    if vert_gap < min_gap:
                        collides = True
                        break

            if not collides:
                obs.append(o)

        return obs

    def reset_game(self):
        self.player = Player()
        self.dog = None
        self.dog_timer = 0
        self.obstacles = self.generate_obstacles(avoid_rects=[self.player.rect])
        self.lives = START_LIVES
        self.invulnerable = False
        self.invulnerable_duration = 0
        self.game_over = False
        self.level_time_left = LEVEL_TIME_MS
        self.level_complete = False
        self.score = 0
        self.lives_earned_from_score = 0

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN and (self.game_over or self.level_complete):
                if event.key == pygame.K_r:
                    self.reset_game()
        return True

    def update(self, dt):
        now = pygame.time.get_ticks()
        keys = pygame.key.get_pressed()
        if not self.game_over and not self.level_complete:
            self.player.handle_input(keys)
            self.level_time_left -= dt
            if self.level_time_left <= 0:
                self.level_time_left = 0
                self.level_complete = True

            if self.dog is None:
                self.dog_timer += dt
                if self.dog_timer >= DOG_SPAWN_MS:
                    # spawn the dog when enough time has elapsed
                    self.dog = Dog(self.player)
                    self.dog_spawn_time = now
                    # also start writing obstacles avoiding the dog
                    self.obstacles = self.generate_obstacles(avoid_rects=[self.player.rect, self.dog.rect])
                    self.dog_visible_until = now + DOG_VISIBLE_MS
                    self.dog_timer = 0

            if self.player.rect.top <= 0:
                # player moved past the top edge: change background and reset position
                if self.backgrounds:
                    self.bg_index = (self.bg_index + 1) % len(self.backgrounds)
                self.player.rect.bottom = HEIGHT - 10
                # give a brief invulnerability window after screen change
                self.invulnerable = True
                self.invulnerable_start = now
                self.invulnerable_duration = SCREEN_INVULNERABILITY_MS
                # award points for advancing
                self.score += 10
                # regenerate obstacles, possibly reposition dog
                if self.dog:
                    self.dog = Dog(self.player)
                    self.dog_spawn_time = now
                    self.obstacles = self.generate_obstacles(avoid_rects=[self.player.rect, self.dog.rect])
                else:
                    self.obstacles = self.generate_obstacles(avoid_rects=[self.player.rect])

            if self.dog:
                # only start moving after the attack delay has passed
                if now >= self.dog_spawn_time + DOG_ATTACK_DELAY_MS:
                    # chase a point where the player was 500ms ago (0.5s delay)
                    delayed_target = self._get_player_rect_with_delay(500, now)
                    self.dog.update(delayed_target)
                # disappear after visible duration
                if now >= self.dog_visible_until:
                    self.dog = None
                    self.dog_timer = 0

            self.obstacles = [o for o in self.obstacles if o.rect.top <= HEIGHT and o.rect.bottom >= 0]

            # append current player position to history and prune old entries
            self.player_history.append((now, self.player.rect.copy()))
            # keep only a couple seconds worth of history to save memory
            cutoff = now - 2000
            self.player_history = [(t, r) for (t, r) in self.player_history if t >= cutoff]

            # collisions: use take_damage to ensure invulnerability is respected
            def take_damage():
                if self.invulnerable:
                    return False
                self.lives -= 1
                self.score -= 30
                self.invulnerable = True
                self.invulnerable_start = now
                self.invulnerable_duration = INVULNERABILITY_MS
                if self.lives <= 0:
                    self.game_over = True
                return True

            for ob in self.obstacles:
                if self.player.rect.colliderect(ob.rect):
                    if take_damage():
                        break

            if self.dog and self.player.rect.colliderect(self.dog.rect):
                take_damage()

            # check whichever duration was applied last
            if self.invulnerable and now - self.invulnerable_start >= self.invulnerable_duration:
                self.invulnerable = False

            # grant a life for every 50 points accumulated
            lives_to_grant = self.score // 50
            if lives_to_grant > self.lives_earned_from_score:
                self.lives += lives_to_grant - self.lives_earned_from_score
                self.lives_earned_from_score = lives_to_grant

    def _get_player_rect_with_delay(self, delay_ms: int, now: int):
        """Return a rect from player history approximately ``delay_ms`` milliseconds ago.

        If the history doesn't go back far enough, return the current player rect.
        """
        target_time = now - delay_ms
        # iterate backwards for efficiency
        for t, rect in reversed(self.player_history):
            if t <= target_time:
                return rect.copy()
        # fallback: use current position
        return self.player.rect.copy()

    def _is_in_vision(self, rect: pygame.Rect) -> bool:
        """Return ``True`` if the given rect is within the player's vision cone.

        The cone is defined by the player's ``facing`` vector, the
        **VISION_ANGLE** and **VISION_DISTANCE** constants.  Objects outside
        the cone remain in the game for collisions but are not rendered.
        """
        # calculate vector from player centre to object centre
        p = pygame.math.Vector2(self.player.rect.center)
        o = pygame.math.Vector2(rect.center)
        vec = o - p
        dist = vec.length()
        if dist == 0:
            return True
        if dist > VISION_DISTANCE:
            return False
        # angle between facing direction and the object vector
        angle = self.player.facing.angle_to(vec)
        return abs(angle) <= VISION_ANGLE / 2

    def _draw_vision_cone(self):
        """Draw a translucent wedge showing the area the player can currently see."""
        p = pygame.math.Vector2(self.player.rect.center)
        # build boundary vectors by rotating the facing vector
        half = VISION_ANGLE / 2
        left = self.player.facing.rotate(half)
        right = self.player.facing.rotate(-half)
        dist = VISION_DISTANCE
        left_pt = p + left * dist
        right_pt = p + right * dist

        cone_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.polygon(cone_surf, (255, 255, 255, 40), [p, left_pt, right_pt])
        self.screen.blit(cone_surf, (0, 0))

    def draw(self):
        if self.backgrounds:
            self.screen.blit(self.backgrounds[self.bg_index], (0, 0))
        else:
            draw_road(self.screen)

        # optionally render the field‑of‑view cone for debugging/visual feedback
        if VISION_ANGLE and SHOW_VISION_CONE:
            self._draw_vision_cone()

        # only draw obstacles that fall within the player's vision cone
        for ob in self.obstacles:
            if self._is_in_vision(ob.rect):
                ob.draw(self.screen)
        if self.dog:
            # dogs remain visible regardless of vision, so the player isn't
            # ambushed by an unseen enemy (you can change this if desired)
            self.dog.draw(self.screen)
        self.player.draw(self.screen, invulnerable=self.invulnerable)

        font = pygame.font.SysFont(None, 28)
        time_txt = font.render(f'Tiempo: {self.level_time_left//1000}s', True, (255, 255, 255))
        self.screen.blit(time_txt, (WIDTH - time_txt.get_width() - 10, 10))
        draw_ui(self.screen, self.lives, self.score)

        if self.game_over:
            font = pygame.font.SysFont(None, 48)
            txt = font.render('GAME OVER', True, (255, 0, 0))
            self.screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, HEIGHT // 2 - 30))
            small = pygame.font.SysFont(None, 24)
            hint = small.render('Presiona R para reiniciar', True, (255, 255, 255))
            self.screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT // 2 + 20))

        if self.level_complete:
            font = pygame.font.SysFont(None, 48)
            txt = font.render('NIVEL COMPLETADO', True, (0, 255, 0))
            self.screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, HEIGHT // 2 - 30))
            small = pygame.font.SysFont(None, 24)
            hint = small.render('Presiona R para reiniciar', True, (255, 255, 255))
            self.screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT // 2 + 20))

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS)
            running = self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()
        sys.exit()
