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
		# velocidad máxima reducida
		self.speed = 5

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
		# permitir que el jugador alcance el borde superior (y detectarlo en el bucle principal)
		if self.rect.top < 0:
			self.rect.top = 0
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
		# y se establecerá desde el generador para posicionar obstáculos estáticos
		self.y = 0
		self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

	def update(self):
		# obstáculos estáticos: no se mueven
		pass

	def draw(self, surface):
		pygame.draw.rect(surface, (139, 69, 19), self.rect)


class Dog:
	def __init__(self, player):
		self.width = 40
		self.height = 40
		# aparecer aleatoriamente a la izquierda o derecha del nivel
		side = random.choice(('left', 'right'))
		if side == 'left':
			self.x = ROAD_X + 10
		else:
			self.x = ROAD_X + ROAD_WIDTH - self.width - 10
		# posición vertical aleatoria dentro del área de juego
		self.y = random.randint(60, HEIGHT - self.height - 60)
		self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
		# velocidad máxima igual a la del jugador (reducida)
		self.speed = player.speed

	def update(self, target_rect):
		# moverse hacia el jugador, con paso máximo igual a self.speed
		dx = target_rect.centerx - self.rect.centerx
		dy = target_rect.centery - self.rect.centery
		dist = (dx*dx + dy*dy) ** 0.5
		if dist <= 0:
			return
		step = min(self.speed, dist)
		self.rect.x += int(dx / dist * step)
		self.rect.y += int(dy / dist * step)
		# limitar a la carretera
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
	# mostrar temporizador si está disponible
	# (se le pasará `time_left_ms` como tercer argumento cuando exista)


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
	# generar obstáculos iniciales
	def generate_obstacles(avoid_rects=None, min_count=3, max_count=7):
		obs = []
		count = random.randint(min_count, max_count)
		attempts = 0
		while len(obs) < count and attempts < count * 20:
			attempts += 1
			o = Obstacle()
			# elegir una y aleatoria dentro de la carretera (evitar top/bottom extremos)
			o_y = random.randint(60, HEIGHT - o.height - 60)
			o.rect.y = o_y
			# evitar solapamiento con otros obstáculos
			collides = any(o.rect.colliderect(existing.rect) for existing in obs)
			# evitar solapamiento con rectángulos externos (jugador, perro, etc.)
			if avoid_rects:
				for r in avoid_rects:
					if o.rect.colliderect(r):
						collides = True
			if not collides:
				obs.append(o)
		# si por alguna razón no se generaron suficientes, devolver los que haya
		return obs

	# el perro aparece después de 10 segundos
	dog = None
	dog_timer = 0
	DOG_SPAWN_MS = 10000
	obstacles = generate_obstacles(avoid_rects=[player.rect])
	# temporizador de nivel (ms)
	LEVEL_TIME_MS = 120000  # 120 segundos
	level_time_left = LEVEL_TIME_MS
	level_complete = False

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
			if event.type == pygame.KEYDOWN and (game_over or level_complete):
				if event.key == pygame.K_r:
					# reiniciar juego
					player = Player()
					dog = None
					dog_timer = 0
					obstacles = generate_obstacles(avoid_rects=[player.rect])
					lives = 3
					invulnerable = False
					game_over = False
					level_time_left = LEVEL_TIME_MS
					level_complete = False

		keys = pygame.key.get_pressed()
		if not game_over and not level_complete:
			player.handle_input(keys)
			# decrementar temporizador
			level_time_left -= dt
			if level_time_left <= 0:
				level_time_left = 0
				level_complete = True

			# actualizar temporizador de aparición del perro
			if dog is None:
				dog_timer += dt
				if dog_timer >= DOG_SPAWN_MS:
					# crear perro y regenerar obstáculos evitando jugador y perro
					dog = Dog(player)
					obstacles = generate_obstacles(avoid_rects=[player.rect, dog.rect])

			# si el jugador toca el borde superior, cambiar fondo, regenerar obstáculos y reposicionarlo abajo
			if player.rect.top <= 0:
				if backgrounds:
					bg_index = (bg_index + 1) % len(backgrounds)
				bg_timer = 0
				# colocar jugador abajo
				player.rect.bottom = HEIGHT - 10
				# si el perro ya existe, recrearlo detrás del jugador y evitarlo al generar
				if dog:
					dog = Dog(player)
					obstacles = generate_obstacles(avoid_rects=[player.rect, dog.rect])
				else:
					obstacles = generate_obstacles(avoid_rects=[player.rect])

			# actualizar perro (persigue al jugador) solo si ya apareció
			if dog:
				dog.update(player.rect)

			# Los obstáculos son estáticos (no se actualizan aquí)

			# remove off-screen
			# mantener obstáculos dentro de la pantalla (no deberían moverse)
			obstacles = [o for o in obstacles if o.rect.top <= HEIGHT and o.rect.bottom >= 0]

			# collisions
			if not invulnerable:
				for ob in obstacles:
					if player.rect.colliderect(ob.rect):
						lives -= 1
						invulnerable = True
						invulnerable_start = now
						break
				# colisión con el perro se comporta igual que con un obstáculo
				if dog and not invulnerable and player.rect.colliderect(dog.rect):
					lives -= 1
					invulnerable = True
					invulnerable_start = now

			# handle invulnerability timeout
			if invulnerable and now - invulnerable_start >= 1000:
				invulnerable = False

			if lives <= 0:
				game_over = True

		# Nota: el cambio de fondo ya ocurre únicamente cuando el jugador
		# toca el borde superior de la pantalla. Se ha desactivado el cambio
		# automático por tiempo (antes dependía de `bg_timer`).

		# draw
		if backgrounds:
			screen.blit(backgrounds[bg_index], (0, 0))
		else:
			draw_road(screen)
		for ob in obstacles:
			ob.draw(screen)
		# dibujar perro (detrás del jugador) si existe
		if dog:
			dog.draw(screen)
		player.draw(screen, invulnerable=invulnerable)
		# mostrar tiempo restante en UI
		font = pygame.font.SysFont(None, 28)
		time_txt = font.render(f'Tiempo: {level_time_left//1000}s', True, (255,255,255))
		screen.blit(time_txt, (WIDTH - time_txt.get_width() - 10, 10))
		draw_ui(screen, lives)

		if game_over:
			font = pygame.font.SysFont(None, 48)
			txt = font.render('GAME OVER', True, (255, 0, 0))
			screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, HEIGHT // 2 - 30))
			small = pygame.font.SysFont(None, 24)
			hint = small.render('Presiona R para reiniciar', True, (255, 255, 255))
			screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT // 2 + 20))

		if level_complete:
			font = pygame.font.SysFont(None, 48)
			txt = font.render('NIVEL COMPLETADO', True, (0, 255, 0))
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
