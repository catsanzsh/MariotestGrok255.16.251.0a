import pygame
import numpy as np
import asyncio
import platform

# Constants
SCREEN_WIDTH = 256
SCREEN_HEIGHT = 224
TILE_SIZE = 16
FPS = 60
SKY_COLOR = (135, 206, 235)
MARIO_COLOR = (255, 0, 0)
GOOMBA_COLOR = (139, 69, 19)

# Level maps
level_map_1_1 = [
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

level_map_1_2 = [
    "........................................",
    "........................................",
    "........................................",
    "........................................",
    "........................................",
    "............?B?.........?B?.............",
    "........................................",
    "........................................",
    "....................P.....P.............",
    "....................P.....P.............",
    "########################################",
    "########################################",
]

# Enemies
enemies_1_1 = [{"type": "goomba", "x": 320, "y": 176}]
enemies_1_2 = [
    {"type": "goomba", "x": 320, "y": 176},
    {"type": "goomba", "x": 400, "y": 176},
]

# Global variables
level_map = None
enemies = None
mario_x = 32
mario_y = 176
mario_width = 16
mario_height = 16
mario_vel_x = 0
mario_vel_y = 0
gravity = 1
jump_strength = -10
is_jumping = False
camera_x = 0
game_state = "menu"
running = True

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

# Draw menu function
def draw_menu(screen, font):
    screen.fill(SKY_COLOR)
    text1 = font.render("Select Level:", True, (0, 0, 0))
    text2 = font.render("1. Level 1-1", True, (0, 0, 0))
    text3 = font.render("2. Level 1-2", True, (0, 0, 0))
    screen.blit(text1, (50, 50))
    screen.blit(text2, (50, 100))
    screen.blit(text3, (50, 150))

# Reset game state
def reset_game():
    global marhoria_x, mario_y, mario_vel_x, mario_vel_y, is_jumping, camera_x
    mario_x = 32
    mario_y = 176
    mario_vel_x = 0
    mario_vel_y = 0
    is_jumping = False
    camera_x = 0

# Generate simple square wave sound
def generate_sound():
    sample_rate = 44100
    duration = 1.0  # 1 second
    frequency = 440  # A4 note
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    sound_data = (np.sign(np.sin(2 * np.pi * frequency * t)) * 32767 / 2).astype(np.int16)
    return pygame.sndarray.make_sound(np.column_stack((sound_data, sound_data)))

# Game setup
def setup():
    global screen, clock, font, sound
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Super Mario Bros")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)
    sound = generate_sound()

# Update game loop
def update_loop():
    global running, game_state, level_map, enemies, mario_x, mario_y, mario_vel_x, mario_vel_y, is_jumping, camera_x
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if game_state == "menu":
                if event.key == pygame.K_1:
                    level_map = level_map_1_1
                    enemies = enemies_1_1
                    reset_game()
                    game_state = "game"
                    sound.play(-1)
                elif event.key == pygame.K_2:
                    level_map = level_map_1_2
                    enemies = enemies_1_2
                    reset_game()
                    game_state = "game"
                    sound.play(-1)
            elif game_state == "game":
                if event.key == pygame.K_m:
                    game_state = "menu"
                    sound.stop()

    if game_state == "menu":
        draw_menu(screen, font)
    elif game_state == "game":
        level_width = len(level_map[0]) * TILE_SIZE
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

        # Update Mario with boundary checks
        mario_x += mario_vel_x
        if mario_x < 0:
            mario_x = 0
        elif mario_x > level_width - mario_width:
            mario_x = level_width - mario_width
        mario_y += mario_vel_y
        mario_vel_y += gravity
        if mario_y >= 176:  # Ground collision
            mario_y = 176
            mario_vel_y = 0
            is_jumping = False

        # Update camera
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

# Main async function
async def main():
    setup()
    while running:
        update_loop()
        await asyncio.sleep(1.0 / FPS)

# Run the game
if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())
