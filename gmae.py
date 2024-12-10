import pygame
import sys
import json

pygame.init()

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 1050
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('DDR-like Game')
# Slider variables
slider_rect = pygame.Rect(300, 300, 400, 10)  
handle_rect = pygame.Rect(300, 290, 20, 30) 
slider_min = 0.1  # Minimum speed
slider_max = 1.0  # Maximum speed
slider_value = 1.0  # Default speed

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
BUTTON_COLOR = (0, 255, 0)

arrow_images = {
    'left': pygame.image.load('left_arrow.png').convert_alpha(),
    'down': pygame.image.load('down_arrow.png').convert_alpha(),
    'up': pygame.image.load('up_arrow.png').convert_alpha(),
    'right': pygame.image.load('right_arrow.png').convert_alpha()
}
for direction, image in arrow_images.items():
    arrow_images[direction] = pygame.transform.scale(image, (150, 150))


scroll_speed = 12
game_mode = "standard"  # or "reverse"
arrow_file = "input.json"
arrow_positions = {
    'left': 250,
    'down': 400,
    'up': 550,
    'right': 700
}
ghost_steps = pygame.sprite.Group()
game_started = False
start_time = None


class GhostStep(pygame.sprite.Sprite):
    def __init__(self, direction, x_position, y_position):
        super().__init__()
        self.image = arrow_images[direction]
        self.image.set_alpha(128)  # Make it semi-transparent
        self.rect = self.image.get_rect(center=(x_position, y_position))

class Arrow(pygame.sprite.Sprite):
    def __init__(self, direction, x_position, start_y, time_appearance, foot=None, time_end=None):
        super().__init__()
        self.direction = direction
        self.image = arrow_images[self.direction].copy() 
        self.rect = self.image.get_rect(center=(x_position, start_y))
        self.speed = scroll_speed
        self.time_appearance = time_appearance
        self.time_end = time_end  
        self.killed = False
        self.foot = foot
        if self.foot:
            self._overlay_foot_text()

    def _overlay_foot_text(self):
        """Render the foot ('L' or 'R') onto the arrow image."""
        font = pygame.font.SysFont('Arial', 85, bold=True) #change font size here
        text_color = (255, 0, 0) 
        text_surface = font.render(self.foot, True, text_color)
        text_rect = text_surface.get_rect(center=self.image.get_rect().center)
        self.image.blit(text_surface, text_rect)

    def update(self, current_time):
        if self.killed:
            return

        if current_time >= self.time_appearance:
            if game_mode == "standard":
                self.rect.y -= self.speed * time_factor
            elif game_mode == "reverse":
                self.rect.y += self.speed * time_factor

        # Kill the arrow if it moves off-screen in standard mode or reverse mode
        if (game_mode == "standard" and self.rect.y <= 0) or (game_mode == "reverse" and self.rect.y >= SCREEN_HEIGHT - 175):
            self.kill()

    def draw_hold_indicator(self, surface):
        #Probably deleting because i am not using this
        if self.time_end:
            total_time = self.time_end - self.time_appearance
            if game_mode == "standard":
                y_end_position = self.rect.y - total_time * self.speed * time_factor
            elif game_mode == "reverse":
                y_end_position = self.rect.y - total_time * self.speed * time_factor

            # Draw the hold rectangle from time_appearance to time_end
            hold_rect = pygame.Rect(self.rect.x - 75, self.rect.y, 150, y_end_position - self.rect.y)
            pygame.draw.rect(surface, (255, 255, 0), hold_rect, 3) 
            pygame.draw.rect(surface, (255, 255, 0, 50), hold_rect)  

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
    slider_rect = pygame.Rect(300, 300, 400, 10)
    handle_rect = pygame.Rect(300 + slider_rect.width - 20, 290, 20, 30) 
    time_factors = [0.1 * i for i in range(1, 11)]  # 0.1 to 1.0 ... change later?
    slider_width = slider_rect.width
    num_factors = len(time_factors)
    dragging = False
    time_factor = 1.0  

    def calculate_time_factor(handle_x):
        index = round((handle_x - slider_rect.left) / slider_width * (num_factors - 1))
        return time_factors[index]

    while True:
        screen.fill(GRAY)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    input_active = True
                else:
                    input_active = False 

                if slider_rect.collidepoint(event.pos) or handle_rect.collidepoint(event.pos):
                    dragging = True

                if start_button.collidepoint(event.pos):
                    game_started = True
                    time_factor = calculate_time_factor(handle_rect.centerx) 
                    return

            if event.type == pygame.MOUSEBUTTONUP:
                dragging = False

            if event.type == pygame.MOUSEMOTION and dragging:
                handle_rect.centerx = max(slider_rect.left,
                                          min(event.pos[0], slider_rect.right))
                time_factor = calculate_time_factor(handle_rect.centerx)

            # this the input field
            if event.type == pygame.KEYDOWN:
                if input_active: 
                    if event.key == pygame.K_RETURN:
                        arrow_file = input_text
                        input_active = False  
                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    else:
                        input_text += event.unicode
                else:  
                    if event.key == pygame.K_UP:
                        scroll_speed += 1
                    elif event.key == pygame.K_DOWN:
                        scroll_speed = max(1, scroll_speed - 1)
                    elif event.key == pygame.K_r:
                        game_mode = "reverse"
                    elif event.key == pygame.K_s:
                        game_mode = "standard"

        screen.fill(BLACK)
        menu_title = font.render("DDR Game Settings", True, WHITE)
        screen.blit(menu_title, (SCREEN_WIDTH // 2 - menu_title.get_width() // 2, 50))

        # Input box
        file_label = font.render("Input JSON File:", True, WHITE)
        screen.blit(file_label, (50, 150))
        input_box = pygame.Rect(300, 140, 400, 40)
        pygame.draw.rect(screen, WHITE, input_box, 2 if input_active else 1) 
        input_surface = font.render(input_text, True, WHITE)
        screen.blit(input_surface, (input_box.x + 10, input_box.y + 5))

        # Scroll speed which is just based on how much the arrow moves... oh well
        speed_label = font.render(f"Scroll Speed: {scroll_speed} Press Up/down arrow to change", True, WHITE)
        screen.blit(speed_label, (50, 250))

        # Game mode
        mode_label = font.render(f"Mode: {game_mode} (Press R for Reverse, S for Standard)", True, WHITE)
        screen.blit(mode_label, (50, 350))

        # mario 64 Slider
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

    if game_started:
        start_time = pygame.time.get_ticks()

    # Loop over the input data and add arrows based on time and time_end
    for arrow in input_data:
        x_position = arrow_positions[arrow['direction']]
        time_appearance = arrow['time']
        time_end = arrow.get('time_end')  
        foot = arrow.get('foot') 

        # yoooo a hold
        if time_end:
            current_time = time_appearance
            while current_time <= time_end:
                new_arrow = Arrow(arrow['direction'], x_position, start_y, current_time, foot, time_end)
                arrows_to_create.append(new_arrow)
                current_time += 17  # Add a new arrow every 17 ms to "mimic" a hold LOL
        else:
            # If no time_end, then it's a regular arrow not a hold
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
                if event.key == pygame.K_q:  
                    running = False 
                    game_started = False  
                    return


        if game_started:
            current_time = pygame.time.get_ticks() - start_time

            for arrow in arrows_to_create:
                if current_time >= arrow.time_appearance and arrow not in created_arrows:
                    arrows_group.add(arrow)
                    created_arrows.add(arrow)

            # Update arrows with scaled time frame like 0.5x
            arrows_group.update(current_time * time_factor)

        #Draw ghost steps and arrows
        ghost_steps.draw(screen)
        arrows_group.draw(screen)

        for arrow in arrows_group:
            arrow.draw_hold_indicator(screen)

        pygame.display.flip()
        # 60fps
        clock.tick(60)


# da game

while True:
    main_menu()
    input_data = parse_input_file(arrow_file)
    game_loop(input_data)

