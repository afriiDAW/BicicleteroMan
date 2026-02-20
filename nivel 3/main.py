import pygame
import random
import sys
import os


WIDTH, HEIGHT = 480, 700
ROAD_WIDTH = 300
ROAD_X = (WIDTH - ROAD_WIDTH) // 2
FPS = 60


class Player:
	def __init__(self):
		self.width = 40
		self.height = 60
		self.x = WIDTH // 2 - self.width // 2
		self.y = HEIGHT - self.height - 30
		self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
		self.speed = 6

	def handle_input(self, keys):
		if keys[pygame.K_LEFT]:
			self.rect.x -= self.speed
		if keys[pygame.K_RIGHT]:
			self.rect.x += self.speed
		if keys[pygame.K_UP]:
			self.rect.y -= self.speed
		if keys[pygame.K_DOWN]:
			self.rect.y += self.speed

		# constrain to road
		if self.rect.left < ROAD_X + 10:
			self.rect.left = ROAD_X + 10
		if self.rect.right > ROAD_X + ROAD_WIDTH - 10:
			self.rect.right = ROAD_X + ROAD_WIDTH - 10
		if self.rect.top < 10:
			self.rect.top = 10
		if self.rect.bottom > HEIGHT - 10:
			self.rect.bottom = HEIGHT - 10

	def draw(self, surface, invulnerable=False):
		color = (30, 144, 255)
		if invulnerable:
			# blink effect
			if (pygame.time.get_ticks() // 100) % 2 == 0:
				color = (135, 206, 250)
			else:
				color = (255, 255, 255)
		pygame.draw.rect(surface, color, self.rect, border_radius=6)


class Obstacle:
	def __init__(self):
		self.width = random.randint(30, 80)
		self.height = random.randint(30, 80)
		self.x = random.randint(ROAD_X + 10, ROAD_X + ROAD_WIDTH - self.width - 10)
		self.y = -self.height
		self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
		self.speed = random.uniform(3.0, 6.0)

	def update(self):
		self.rect.y += self.speed

	def draw(self, surface):
		pygame.draw.rect(surface, (139, 69, 19), self.rect)


def draw_road(surface):
	surface.fill((34, 139, 34))
	pygame.draw.rect(surface, (50, 50, 50), (ROAD_X, 0, ROAD_WIDTH, HEIGHT))
	# road lines
	lane_x = ROAD_X + ROAD_WIDTH // 2 - 2
	for y in range(0, HEIGHT, 40):
		pygame.draw.rect(surface, (255, 255, 255), (lane_x, y + (y // 40) % 2 * 20, 4, 20))


def draw_ui(surface, lives):
	font = pygame.font.SysFont(None, 28)
	txt = font.render(f'Vidas: {lives}', True, (255, 255, 255))
	surface.blit(txt, (10, 10))


def main():
	pygame.init()
	screen = pygame.display.set_mode((WIDTH, HEIGHT))
	pygame.display.set_caption('Bici Obstáculos')
	clock = pygame.time.Clock()

	# cargar fondos si existen
	backgrounds = []
	base = os.path.dirname(__file__)
	for name in ('camino1.png', 'camino2.png', 'camino3.png'):
		path = os.path.join(base, name)
		if os.path.exists(path):
			try:
				img = pygame.image.load(path).convert()
				img = pygame.transform.scale(img, (WIDTH, HEIGHT))
				backgrounds.append(img)
			except Exception:
				pass

	bg_index = 0
	bg_timer = 0
	bg_delay = 3000  # ms entre cambios de fondo (3 segundos)

	player = Player()
	obstacles = []
	spawn_timer = 0
	spawn_delay = random.randint(700, 1400)

	lives = 3
	invulnerable = False
	invulnerable_start = 0
	game_over = False

	running = True
	while running:
		dt = clock.tick(FPS)
		now = pygame.time.get_ticks()

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
			if event.type == pygame.KEYDOWN and game_over:
				if event.key == pygame.K_r:
					# reiniciar juego
					player = Player()
					obstacles = []
					lives = 3
					invulnerable = False
					game_over = False

		keys = pygame.key.get_pressed()
		if not game_over:
			player.handle_input(keys)

			# spawn obstacles
			spawn_timer += dt
			if spawn_timer >= spawn_delay:
				obstacles.append(Obstacle())
				spawn_timer = 0
				spawn_delay = random.randint(600, 1400)

			# update obstacles
			for ob in obstacles:
				ob.update()

			# remove off-screen
			obstacles = [o for o in obstacles if o.rect.top <= HEIGHT]

			# collisions
			if not invulnerable:
				for ob in obstacles:
					if player.rect.colliderect(ob.rect):
						lives -= 1
						invulnerable = True
						invulnerable_start = now
						break

			# handle invulnerability timeout
			if invulnerable and now - invulnerable_start >= 1000:
				invulnerable = False

			if lives <= 0:
				game_over = True

		# actualizar alternancia de fondo
		if backgrounds:
			bg_timer += dt
			if bg_timer >= bg_delay:
				bg_index = (bg_index + 1) % len(backgrounds)
				bg_timer = 0

		# draw
		if backgrounds:
			screen.blit(backgrounds[bg_index], (0, 0))
		else:
			draw_road(screen)
		for ob in obstacles:
			ob.draw(screen)
		player.draw(screen, invulnerable=invulnerable)
		draw_ui(screen, lives)

		if game_over:
			font = pygame.font.SysFont(None, 48)
			txt = font.render('GAME OVER', True, (255, 0, 0))
			screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, HEIGHT // 2 - 30))
			small = pygame.font.SysFont(None, 24)
			hint = small.render('Presiona R para reiniciar', True, (255, 255, 255))
			screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT // 2 + 20))

		pygame.display.flip()

	pygame.quit()
	sys.exit()


if __name__ == '__main__':
	main()

# un objeto (perro) que persigue al jugador.
# que el jugador tenga una linterna y que solo pueda ver los bstaculos que esta enfrente de el pero los que estan a lo alrededor siguen apareciendo.
