import pygame
import random
import sys
from typing import List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum, auto
import math

# Initialize Pygame and its font system
pygame.init()
pygame.font.init()

# Game Constants
WINDOW_SIZE = 800
GRID_SIZE = 20
GRID_COUNT = WINDOW_SIZE // GRID_SIZE
FPS = 60  # Increased for smoother animations
GAME_SPEED = 10  # Actual game update speed

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (50, 50, 255)
DARK_GREEN = (34, 139, 34)
GOLD = (255, 215, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
PURPLE = (147, 112, 219)

# UI Constants
MENU_FONT_SIZE = 64
BUTTON_FONT_SIZE = 36
SCORE_FONT_SIZE = 32
TITLE_FONT_SIZE = 72

class GameState(Enum):
    MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()

class Direction(Enum):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()

@dataclass
class Button:
    rect: pygame.Rect
    text: str
    action: str
    color: Tuple[int, int, int] = BLUE
    hover_color: Tuple[int, int, int] = PURPLE

class SnakeGame:
    def __init__(self) -> None:
        self.screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
        pygame.display.set_caption('Modern Snake Game')
        self.clock = pygame.time.Clock()
        
        # Load fonts
        self.title_font = pygame.font.Font(None, TITLE_FONT_SIZE)
        self.menu_font = pygame.font.Font(None, MENU_FONT_SIZE)
        self.button_font = pygame.font.Font(None, BUTTON_FONT_SIZE)
        self.score_font = pygame.font.Font(None, SCORE_FONT_SIZE)
        
        # Initialize game state
        self.game_state = GameState.MENU
        self.high_score = 0
        self.reset_game()
        
        # Create menu buttons
        button_width = 200
        button_height = 50
        button_x = WINDOW_SIZE // 2 - button_width // 2
        
        self.menu_buttons = [
            Button(
                pygame.Rect(button_x, 300, button_width, button_height),
                "Play Game",
                "play"
            ),
            Button(
                pygame.Rect(button_x, 380, button_width, button_height),
                "Quit",
                "quit"
            )
        ]
        
        self.pause_buttons = [
            Button(
                pygame.Rect(button_x, 300, button_width, button_height),
                "Resume",
                "resume"
            ),
            Button(
                pygame.Rect(button_x, 380, button_width, button_height),
                "Main Menu",
                "menu"
            )
        ]
        
        self.game_over_buttons = [
            Button(
                pygame.Rect(button_x, 300, button_width, button_height),
                "Play Again",
                "play"
            ),
            Button(
                pygame.Rect(button_x, 380, button_width, button_height),
                "Main Menu",
                "menu"
            )
        ]

    def reset_game(self) -> None:
        """Reset the game state to initial conditions."""
        self.snake: List[Tuple[int, int]] = [(GRID_COUNT // 2, GRID_COUNT // 2)]
        self.direction = Direction.RIGHT
        self.next_direction = Direction.RIGHT
        self.food = self.generate_food()
        self.score = 0
        self.frame_count = 0
        self.food_animation_offset = 0
        self.game_speed = GAME_SPEED

    def generate_food(self) -> Tuple[int, int]:
        """Generate food at a random position not occupied by the snake."""
        while True:
            food = (random.randint(0, GRID_COUNT - 1), random.randint(0, GRID_COUNT - 1))
            if food not in self.snake:
                return food

    def handle_input(self) -> bool:
        """Handle user input for movement and game control."""
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    if self.game_state == GameState.MENU:
                        for button in self.menu_buttons:
                            if button.rect.collidepoint(mouse_pos):
                                if button.action == "play":
                                    self.game_state = GameState.PLAYING
                                    self.reset_game()
                                elif button.action == "quit":
                                    return False
                                
                    elif self.game_state == GameState.PAUSED:
                        for button in self.pause_buttons:
                            if button.rect.collidepoint(mouse_pos):
                                if button.action == "resume":
                                    self.game_state = GameState.PLAYING
                                elif button.action == "menu":
                                    self.game_state = GameState.MENU
                                    
                    elif self.game_state == GameState.GAME_OVER:
                        for button in self.game_over_buttons:
                            if button.rect.collidepoint(mouse_pos):
                                if button.action == "play":
                                    self.game_state = GameState.PLAYING
                                    self.reset_game()
                                elif button.action == "menu":
                                    self.game_state = GameState.MENU
            
            if event.type == pygame.KEYDOWN:
                if self.game_state == GameState.PLAYING:
                    if event.key == pygame.K_ESCAPE:
                        self.game_state = GameState.PAUSED
                    self._handle_direction_change(event.key)
                elif self.game_state == GameState.PAUSED:
                    if event.key == pygame.K_ESCAPE:
                        self.game_state = GameState.PLAYING
        
        return True

    def _handle_direction_change(self, key: int) -> None:
        """Handle direction changes based on key press."""
        direction_map = {
            pygame.K_UP: (Direction.UP, Direction.DOWN),
            pygame.K_DOWN: (Direction.DOWN, Direction.UP),
            pygame.K_LEFT: (Direction.LEFT, Direction.RIGHT),
            pygame.K_RIGHT: (Direction.RIGHT, Direction.LEFT)
        }
        
        if key in direction_map:
            new_direction, opposite = direction_map[key]
            if self.direction != opposite:
                self.next_direction = new_direction

    def update(self) -> None:
        """Update game state including snake movement and collision detection."""
        if self.game_state != GameState.PLAYING:
            return

        self.frame_count += 1
        self.food_animation_offset = math.sin(self.frame_count * 0.1) * 4

        # Only update game logic at game speed
        if self.frame_count % (FPS // self.game_speed) != 0:
            return

        self.direction = self.next_direction
        
        # Get new head position
        head_x, head_y = self.snake[0]
        direction_updates = {
            Direction.UP: (0, -1),
            Direction.DOWN: (0, 1),
            Direction.LEFT: (-1, 0),
            Direction.RIGHT: (1, 0)
        }
        dx, dy = direction_updates[self.direction]
        new_head = (head_x + dx, head_y + dy)

        # Check for collisions
        if (new_head[0] < 0 or new_head[0] >= GRID_COUNT or
            new_head[1] < 0 or new_head[1] >= GRID_COUNT or
            new_head in self.snake):
            self.game_state = GameState.GAME_OVER
            self.high_score = max(self.high_score, self.score)
            return

        # Update snake position
        self.snake.insert(0, new_head)
        
        # Check if food is eaten
        if new_head == self.food:
            self.score += 1
            self.food = self.generate_food()
            # Increase game speed every 5 points
            if self.score % 5 == 0:
                self.game_speed = min(20, self.game_speed + 1)
        else:
            self.snake.pop()

    def draw_button(self, button: Button, mouse_pos: Tuple[int, int]) -> None:
        """Draw a button with hover effect."""
        color = button.hover_color if button.rect.collidepoint(mouse_pos) else button.color
        pygame.draw.rect(self.screen, color, button.rect, border_radius=10)
        pygame.draw.rect(self.screen, WHITE, button.rect, 2, border_radius=10)
        
        text = self.button_font.render(button.text, True, WHITE)
        text_rect = text.get_rect(center=button.rect.center)
        self.screen.blit(text, text_rect)

    def draw_menu(self) -> None:
        """Draw the main menu screen."""
        self.screen.fill(BLACK)
        
        # Draw title
        title = self.title_font.render("Snake Game", True, GREEN)
        title_rect = title.get_rect(center=(WINDOW_SIZE // 2, 150))
        self.screen.blit(title, title_rect)
        
        # Draw high score
        high_score_text = self.score_font.render(f"High Score: {self.high_score}", True, GOLD)
        high_score_rect = high_score_text.get_rect(center=(WINDOW_SIZE // 2, 230))
        self.screen.blit(high_score_text, high_score_rect)
        
        # Draw buttons
        mouse_pos = pygame.mouse.get_pos()
        for button in self.menu_buttons:
            self.draw_button(button, mouse_pos)

    def draw_game(self) -> None:
        """Draw the game screen."""
        self.screen.fill(BLACK)
        
        # Draw grid background
        for x in range(GRID_COUNT):
            for y in range(GRID_COUNT):
                if (x + y) % 2 == 0:
                    pygame.draw.rect(self.screen, DARK_GRAY,
                                  (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE))
        
        # Draw snake with gradient effect
        for i, segment in enumerate(self.snake):
            color_value = max(50, 255 - (i * 10))
            color = (50, color_value, 50)
            pygame.draw.rect(self.screen, color,
                           (segment[0] * GRID_SIZE + 1, segment[1] * GRID_SIZE + 1,
                            GRID_SIZE - 2, GRID_SIZE - 2),
                           border_radius=5)
        
        # Draw food with animation
        food_rect = pygame.Rect(
            self.food[0] * GRID_SIZE + 2,
            self.food[1] * GRID_SIZE + 2 + self.food_animation_offset,
            GRID_SIZE - 4,
            GRID_SIZE - 4
        )
        pygame.draw.rect(self.screen, RED, food_rect, border_radius=5)
        
        # Draw score
        score_text = self.score_font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # Draw high score
        high_score_text = self.score_font.render(f"High Score: {self.high_score}", True, GOLD)
        high_score_rect = high_score_text.get_rect(topright=(WINDOW_SIZE - 10, 10))
        self.screen.blit(high_score_text, high_score_rect)

    def draw_pause(self) -> None:
        """Draw the pause screen overlay."""
        # Add semi-transparent overlay
        overlay = pygame.Surface((WINDOW_SIZE, WINDOW_SIZE))
        overlay.fill(BLACK)
        overlay.set_alpha(128)
        self.screen.blit(overlay, (0, 0))
        
        # Draw "PAUSED" text
        pause_text = self.menu_font.render("PAUSED", True, WHITE)
        pause_rect = pause_text.get_rect(center=(WINDOW_SIZE // 2, 150))
        self.screen.blit(pause_text, pause_rect)
        
        # Draw buttons
        mouse_pos = pygame.mouse.get_pos()
        for button in self.pause_buttons:
            self.draw_button(button, mouse_pos)

    def draw_game_over(self) -> None:
        """Draw the game over screen overlay."""
        # Add semi-transparent overlay
        overlay = pygame.Surface((WINDOW_SIZE, WINDOW_SIZE))
        overlay.fill(BLACK)
        overlay.set_alpha(128)
        self.screen.blit(overlay, (0, 0))
        
        # Draw "GAME OVER" text
        game_over_text = self.menu_font.render("GAME OVER", True, RED)
        game_over_rect = game_over_text.get_rect(center=(WINDOW_SIZE // 2, 150))
        self.screen.blit(game_over_text, game_over_rect)
        
        # Draw final score
        score_text = self.score_font.render(f"Final Score: {self.score}", True, WHITE)
        score_rect = score_text.get_rect(center=(WINDOW_SIZE // 2, 230))
        self.screen.blit(score_text, score_rect)
        
        # Draw buttons
        mouse_pos = pygame.mouse.get_pos()
        for button in self.game_over_buttons:
            self.draw_button(button, mouse_pos)

    def draw(self) -> None:
        """Draw the current game state."""
        if self.game_state == GameState.MENU:
            self.draw_menu()
        else:
            self.draw_game()
            if self.game_state == GameState.PAUSED:
                self.draw_pause()
            elif self.game_state == GameState.GAME_OVER:
                self.draw_game_over()
        
        pygame.display.flip()

    def run(self) -> None:
        """Main game loop."""
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()

if __name__ == '__main__':
    game = SnakeGame()
    game.run()