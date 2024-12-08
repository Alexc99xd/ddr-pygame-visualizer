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
scroll_speed = 5
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
    def __init__(self, direction, x_position, start_y, time_appearance):
        super().__init__()
        self.direction = direction
        self.image = arrow_images[self.direction]
        self.rect = self.image.get_rect(center=(x_position, start_y))
        self.speed = scroll_speed
        self.time_appearance = time_appearance  # Time when this arrow should appear
        self.killed = False  # Track if the arrow is killed

    def update(self, current_time):
        if self.killed:
            return  # If the arrow is killed, don't do anything

        if current_time >= self.time_appearance:
            if game_mode == "standard":
                self.rect.y -= self.speed  # Move up (arrows appear from bottom)
            elif game_mode == "reverse":
                self.rect.y += self.speed  # Move down (arrows appear from top)

        # Ensure proper cleanup: Remove arrow if it goes off-screen
        if self.rect.y > SCREEN_HEIGHT-175 or self.rect.y < 0:  # More generous condition
            print(f"Arrow {self.direction} killed because it's off-screen.")
            self.kill()

    def kill(self):
        super().kill()  # This calls pygame's built-in kill method
        self.killed = True  # Mark this arrow as killed


# Parse input file
def parse_input_file(filename):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error loading input file: {e}")
        sys.exit()


# Main menu
def main_menu():
    global scroll_speed, game_mode, arrow_file, game_started

    font = pygame.font.SysFont('Arial', 32)
    clock = pygame.time.Clock()
    input_active = False
    input_text = arrow_file
    start_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 100, 200, 50)

    while True:
        screen.fill(GRAY)

        # Event handling
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
                    game_mode = "reverse"  # Switch to reverse mode
                elif event.key == pygame.K_s:
                    game_mode = "standard"  # Switch to standard mode
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    input_active = not input_active
                if start_button.collidepoint(event.pos):
                    game_started = True  # Set game_started to True when the button is clicked
                    return  # Start the game

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

        # Scroll Speed
        speed_label = font.render(f"Scroll Speed: {scroll_speed}", True, WHITE)
        screen.blit(speed_label, (50, 250))

        mode_label = font.render(f"Mode: {game_mode} (Press R for Reverse, S for Standard)", True, WHITE)
        screen.blit(mode_label, (50, 350))

        # Start button
        pygame.draw.rect(screen, BUTTON_COLOR, start_button)
        start_text = font.render("Start Game", True, BLACK)
        screen.blit(start_text, (start_button.x + start_button.width // 2 - start_text.get_width() // 2,
                                 start_button.y + start_button.height // 2 - start_text.get_height() // 2))

        pygame.display.flip()
        clock.tick(30)

def game_loop(input_data):
    global game_started, start_time

    clock = pygame.time.Clock()
    arrows_group = pygame.sprite.Group()

    # Create ghost steps based on the mode
    ghost_steps.empty()
    for direction, x_position in arrow_positions.items():
        if game_mode == "standard":
            y_position = 100  # Ghosts are at the top in standard mode
        elif game_mode == "reverse":
            y_position = SCREEN_HEIGHT - 100  # Ghosts are at the bottom in reverse mode
        ghost_steps.add(GhostStep(direction, x_position, y_position))

    # Initial position of arrows based on mode
    start_y = 100 if game_mode == "reverse" else SCREEN_HEIGHT  # Reverse: start from top, Standard: from bottom
    arrows_to_create = []

    # Record the start time when the game starts
    if game_started:
        start_time = pygame.time.get_ticks()  # Get the start time when the game starts
        print(f"Game started at {start_time}")  # Debugging log

    # Read the arrow data and set their appearance times
    for arrow in input_data:
        x_position = arrow_positions[arrow['direction']]
        # Adjust time to be relative to the start time
        time_appearance = (arrow['time'] - (pygame.time.get_ticks() - start_time))  # Time relative to start
        if time_appearance < 0:  # Time has already passed
            print(f"Warning: Arrow for direction {arrow['direction']} would appear in the past!")  # Debugging log
            continue  # Skip this arrow, it should not be created in the past
        new_arrow = Arrow(arrow['direction'], x_position, start_y, time_appearance)
        arrows_to_create.append(new_arrow)

    created_arrows = set()  # Track created arrows to prevent redundancy

    while True:
        screen.fill(BLACK)

        if game_started:  # Only start the game when the flag is True
            current_time = pygame.time.get_ticks() - start_time  # Get current time since the game started
            print(f"Current time: {current_time} (since start)")
            # Update arrows and check for time to spawn
            for arrow in arrows_to_create:
                if current_time >= arrow.time_appearance and arrow not in created_arrows:
                    arrows_group.add(arrow)
                    created_arrows.add(arrow)  # Mark the arrow as created

            arrows_group.update(current_time)  # Update only active arrows

        # Draw ghost steps and arrows
        ghost_steps.draw(screen)
        arrows_group.draw(screen)

        pygame.display.flip()
        clock.tick(60)

# Main execution
main_menu()
input_data = parse_input_file(arrow_file)
game_loop(input_data)
