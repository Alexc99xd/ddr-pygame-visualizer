import pygame
import sys
import json

# Initialize Pygame
pygame.init()

# Screen dimensions and setup
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 1050
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('DDR-like Game')
# Slider variables
slider_rect = pygame.Rect(300, 300, 400, 10)  # Slider bar
handle_rect = pygame.Rect(300, 290, 20, 30)  # Slider handle
slider_min = 0.1  # Minimum speed
slider_max = 1.0  # Maximum speed
slider_value = 1.0  # Default speed

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
BUTTON_COLOR = (0, 255, 0)

# Load and resize images (arrows to 150x150)
arrow_images = {
    'left': pygame.image.load('left_arrow.png').convert_alpha(),
    'down': pygame.image.load('down_arrow.png').convert_alpha(),
    'up': pygame.image.load('up_arrow.png').convert_alpha(),
    'right': pygame.image.load('right_arrow.png').convert_alpha()
}
for direction, image in arrow_images.items():
    arrow_images[direction] = pygame.transform.scale(image, (150, 150))

# Game settings (default values)
scroll_speed = 12
game_mode = "standard"  # or "reverse"
arrow_file = "input.json"

# Arrow positions
arrow_positions = {
    'left': 250,
    'down': 400,
    'up': 550,
    'right': 700
}

# Ghost steps (target zone)
ghost_steps = pygame.sprite.Group()

# Global game start flag and start time
game_started = False
start_time = None


class GhostStep(pygame.sprite.Sprite):
    def __init__(self, direction, x_position, y_position):
        super().__init__()
        self.image = arrow_images[direction]
        self.image.set_alpha(128)  # Make it semi-transparent
        self.rect = self.image.get_rect(center=(x_position, y_position))

class Arrow(pygame.sprite.Sprite):
    def __init__(self, direction, x_position, start_y, time_appearance, foot=None):
        super().__init__()
        self.direction = direction
        self.image = arrow_images[self.direction].copy()  # Copy the base arrow image
        self.rect = self.image.get_rect(center=(x_position, start_y))
        self.speed = scroll_speed
        self.time_appearance = time_appearance
        self.killed = False
        self.foot = foot  # Optional foot indicator ("L" or "R")

        # Overlay the foot text if provided
        if self.foot:
            self._overlay_foot_text()

    def _overlay_foot_text(self):
        """Render the foot ('L' or 'R') onto the arrow image."""
        font = pygame.font.SysFont('Arial', 80, bold=True)  # Slightly larger font size
        text_color = (255, 0, 0)  # Red color for the text
        text_surface = font.render(self.foot, True, text_color)

        # Position the text at the center of the arrow image
        text_rect = text_surface.get_rect(center=self.image.get_rect().center)

        # Blit the text onto the arrow image
        self.image.blit(text_surface, text_rect)

    def update(self, current_time):
        if self.killed:
            return

        if current_time >= self.time_appearance:
            if game_mode == "standard":
                self.rect.y -= self.speed * time_factor
            elif game_mode == "reverse":
                self.rect.y += self.speed * time_factor

        # Kill the arrow if it moves off-screen
        if self.rect.y > SCREEN_HEIGHT - 175 or self.rect.y < 0:
            self.kill()


# Parse input file
def parse_input_file(filename):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error loading input file: {e}")
        sys.exit()
def main_menu():
    global scroll_speed, game_mode, arrow_file, game_started, time_factor

    font = pygame.font.SysFont('Arial', 32)
    clock = pygame.time.Clock()
    input_active = False
    input_text = arrow_file
    start_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 100, 200, 50)

    # Slider variables
    slider_rect = pygame.Rect(300, 300, 400, 10)
    handle_rect = pygame.Rect(300 + slider_rect.width - 20, 290, 20, 30)  # Set handle to the far right for 1.0x
    time_factors = [0.1 * i for i in range(1, 11)]  # 0.1 to 1.0
    slider_width = slider_rect.width
    num_factors = len(time_factors)
    dragging = False
    time_factor = 1.0  # Default to 1.0x speed

    def calculate_time_factor(handle_x):
        index = round((handle_x - slider_rect.left) / slider_width * (num_factors - 1))
        return time_factors[index]

    while True:
        screen.fill(GRAY)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if input_active:
                    if event.key == pygame.K_RETURN:
                        arrow_file = input_text
                        return
                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    else:
                        input_text += event.unicode
                if event.key == pygame.K_UP:
                    scroll_speed += 1
                elif event.key == pygame.K_DOWN:
                    scroll_speed = max(1, scroll_speed - 1)
                elif event.key == pygame.K_r:
                    game_mode = "reverse"
                elif event.key == pygame.K_s:
                    game_mode = "standard"
            if event.type == pygame.MOUSEBUTTONDOWN:
                if slider_rect.collidepoint(event.pos) or handle_rect.collidepoint(event.pos):
                    dragging = True
                if start_button.collidepoint(event.pos):
                    game_started = True
                    time_factor = calculate_time_factor(handle_rect.centerx)  # Set time_factor from slider
                    return
            if event.type == pygame.MOUSEBUTTONUP:
                dragging = False
            if event.type == pygame.MOUSEMOTION and dragging:
                handle_rect.centerx = max(slider_rect.left,
                                          min(event.pos[0], slider_rect.right))
                time_factor = calculate_time_factor(handle_rect.centerx)

        # Draw UI
        screen.fill(BLACK)
        menu_title = font.render("DDR Game Settings", True, WHITE)
        screen.blit(menu_title, (SCREEN_WIDTH // 2 - menu_title.get_width() // 2, 50))

        file_label = font.render("Input JSON File:", True, WHITE)
        screen.blit(file_label, (50, 150))
        input_box = pygame.Rect(300, 140, 400, 40)
        pygame.draw.rect(screen, WHITE, input_box, 2)
        input_surface = font.render(input_text, True, WHITE)
        screen.blit(input_surface, (input_box.x + 10, input_box.y + 5))

        speed_label = font.render(f"Scroll Speed: {scroll_speed}", True, WHITE)
        screen.blit(speed_label, (50, 250))

        mode_label = font.render(f"Mode: {game_mode} (Press R for Reverse, S for Standard)", True, WHITE)
        screen.blit(mode_label, (50, 350))

        pygame.draw.rect(screen, WHITE, slider_rect)
        pygame.draw.rect(screen, BUTTON_COLOR, handle_rect)
        slider_value_label = font.render(f"Game Speed: {time_factor:.1f}x", True, WHITE)
        screen.blit(slider_value_label, (slider_rect.x + slider_rect.width // 2 - slider_value_label.get_width() // 2,
                                         slider_rect.y - 40))

        pygame.draw.rect(screen, BUTTON_COLOR, start_button)
        start_text = font.render("Start Game", True, BLACK)
        screen.blit(start_text, (start_button.x + start_button.width // 2 - start_text.get_width() // 2,
                                 start_button.y + start_button.height // 2 - start_text.get_height() // 2))

        pygame.display.flip()
        clock.tick(30)


def game_loop(input_data):
    global game_started, start_time, time_factor

    clock = pygame.time.Clock()
    arrows_group = pygame.sprite.Group()
    running = True

    # Create ghost steps based on the mode
    ghost_steps.empty()
    for direction, x_position in arrow_positions.items():
        y_position = 100 if game_mode == "standard" else SCREEN_HEIGHT - 100
        ghost_steps.add(GhostStep(direction, x_position, y_position))

    start_y = 100 if game_mode == "reverse" else SCREEN_HEIGHT
    arrows_to_create = []

    # Initialize the game start time
    if game_started:
        start_time = pygame.time.get_ticks()

    # Prepare arrows without scaling their appearance times
    for arrow in input_data:
        x_position = arrow_positions[arrow['direction']]
        time_appearance = arrow['time']
        foot = arrow.get('foot')  # Use .get() to avoid KeyError if 'foot' is missing
        new_arrow = Arrow(arrow['direction'], x_position, start_y, time_appearance, foot)
        arrows_to_create.append(new_arrow)


    created_arrows = set()

    while running:
        screen.fill(BLACK)

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:  # Key to go back to the main menu
                    running = False  # Exit the game loop
                    game_started = False  # Reset game state
                    return

        # Only process game logic if the game has started
        if game_started:
            current_time = pygame.time.get_ticks() - start_time

            # Create new arrows based on their appearance times
            for arrow in arrows_to_create:
                if current_time >= arrow.time_appearance and arrow not in created_arrows:
                    arrows_group.add(arrow)
                    created_arrows.add(arrow)

            # Update arrows with scaled movement
            arrows_group.update(current_time * time_factor)

        # Draw ghost steps and arrows
        ghost_steps.draw(screen)
        arrows_group.draw(screen)

        # Refresh display
        pygame.display.flip()

        # Maintain constant frame rate
        clock.tick(60)



while True:
    main_menu()
    input_data = parse_input_file(arrow_file)
    game_loop(input_data)

