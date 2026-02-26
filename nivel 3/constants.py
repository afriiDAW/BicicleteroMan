WIDTH = 480
HEIGHT = 700
ROAD_WIDTH = 300
ROAD_X = (WIDTH - ROAD_WIDTH) // 2
FPS = 60

# gameplay timings
# dog appears after this many milliseconds (40 seconds)
DOG_SPAWN_MS = 40000
# once spawned the dog stays active for this duration (15 seconds)
DOG_VISIBLE_MS = 15000
# after spawning or resetting on a new screen, the dog waits this long before
# beginning to chase the player (reduced per latest request)
DOG_ATTACK_DELAY_MS = 100
LEVEL_TIME_MS = 120000

# invulnerability duration after colliding with an obstacle (ms)
# this is the longer window the player gets when taking damage
INVULNERABILITY_MS = 1000

# invulnerability granted when the player changes screen (ms)
# remains shorter to give only a brief grace period
SCREEN_INVULNERABILITY_MS = 500

# starting lives for the player
START_LIVES = 5
