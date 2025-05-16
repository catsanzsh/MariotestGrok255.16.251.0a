import pygame
import pyaudio
import wave
import threading

# Constants
SCREEN_WIDTH = 256
SCREEN_HEIGHT = 224
TILE_SIZE = 16
SKY_COLOR = (135, 206, 235)
MARIO_COLOR = (255, 0, 0)  # Red for Mario
GOOMBA_COLOR = (139, 69, 19)  # Brown for Goomba

# Simplified level 1-1 map (40 tiles wide)
level_map = [
    "........................................",
    "........................................",
    "........................................",
    "........................................",
    "........................................",
    "........................................",
    "............?B?.........................",
    "........................................",
    "........................................",
    "....................P...................",
    "....................P...................",
    "########################################",
    "########################################",
]

# Enemies (static Goomba for simplicity)
enemies = [{"type": "goomba", "x": 320, "y": 176}]

# Tile color function
def get_tile_color(tile):
    if tile == '#':
        return (139, 69, 19)  # Brown for ground
    elif tile == 'B':
        return (169, 169, 169)  # Gray for brick
    elif tile == '?':
        return (255, 255, 0)  # Yellow for question block
    elif tile == 'P':
        return (0, 128, 0)  # Green for pipe
    return (0, 0, 0)  # Black for unknown

# Draw level function
def draw_level(screen, level_map, camera_x):
    start_col = camera_x // TILE_SIZE
    end_col = start_col + (SCREEN_WIDTH // TILE_SIZE) + 1
    for row in range(len(level_map)):
        for col in range(start_col, min(end_col, len(level_map[row]))):
            tile = level_map[row][col]
            if tile != '.':
                x = col * TILE_SIZE - camera_x
                y = row * TILE_SIZE
                color = get_tile_color(tile)
                pygame.draw.rect(screen, color, (x, y, TILE_SIZE, TILE_SIZE))

# Audio playback function
audio_playing = True
def play_audio(filename):
    global audio_playing
    chunk = 1024
    p = pyaudio.PyAudio()
    wf = wave.open(filename, 'rb')
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)
    while audio_playing:
        data = wf.readframes(chunk)
        while data and audio_playing:
            stream.write(data)
            data = wf.readframes(chunk)
        wf.rewind()  # Loop audio
    stream.stop_stream()
    stream.close()
    p.terminate()

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Super Mario Bros 1-1")
clock = pygame.time.Clock()

# Mario setup
mario_x = 32
mario_y = 176
mario_width = 16
mario_height = 16
mario_vel_x = 0
mario_vel_y = 0
gravity = 1
jump_strength = -10
is_jumping = False

# Camera
camera_x = 0

# Start audio thread
audio_thread = threading.Thread(target=play_audio, args=("overworld.wav",))
audio_thread.start()

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Handle input
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        mario_vel_x = -2
    elif keys[pygame.K_RIGHT]:
        mario_vel_x = 2
    else:
        mario_vel_x = 0
    if keys[pygame.K_SPACE] and not is_jumping:
        mario_vel_y = jump_strength
        is_jumping = True

    # Update Mario
    mario_x += mario_vel_x
    mario_y += mario_vel_y
    mario_vel_y += gravity
    if mario_y >= 176:  # Ground collision
        mario_y = 176
        mario_vel_y = 0
        is_jumping = False

    # Update camera
    level_width = len(level_map[0]) * TILE_SIZE
    desired_camera_x = mario_x - SCREEN_WIDTH // 2
    camera_x = max(0, min(desired_camera_x, level_width - SCREEN_WIDTH))

    # Draw
    screen.fill(SKY_COLOR)
    draw_level(screen, level_map, camera_x)
    mario_screen_x = mario_x - camera_x
    if 0 <= mario_screen_x < SCREEN_WIDTH:
        pygame.draw.rect(screen, MARIO_COLOR, (mario_screen_x, mario_y, mario_width, mario_height))
    for enemy in enemies:
        enemy_screen_x = enemy["x"] - camera_x
        if 0 <= enemy_screen_x < SCREEN_WIDTH:
            pygame.draw.rect(screen, GOOMBA_COLOR, (enemy_screen_x, enemy["y"], 16, 16))

    pygame.display.flip()
    clock.tick(60)

# Cleanup
audio_playing = False
audio_thread.join()
pygame.quit()
