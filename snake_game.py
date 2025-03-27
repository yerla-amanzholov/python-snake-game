import pygame
import random
from typing import List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum, auto

# Initialize Pygame
pygame.init()

# Game Constants
WINDOW_SIZE = 800
GRID_SIZE = 20
GRID_COUNT = WINDOW_SIZE // GRID_SIZE
FPS = 10

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

class Direction(Enum):
    UP = auto()
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()

@dataclass
class GameState:
    score: int = 0
    game_over: bool = False

class SnakeGame:
    def __init__(self) -> None:
        self.screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
        pygame.display.set_caption('Snake Game')
        self.clock = pygame.time.Clock()
        self.reset_game()

    def reset_game(self) -> None:
        """Reset the game state to initial conditions."""
        self.snake: List[Tuple[int, int]] = [(GRID_COUNT // 2, GRID_COUNT // 2)]
        self.direction = Direction.RIGHT
        self.food = self.generate_food()
        self.state = GameState()

    def generate_food(self) -> Tuple[int, int]:
        """Generate food at a random position not occupied by the snake."""
        while True:
            food = (random.randint(0, GRID_COUNT - 1), random.randint(0, GRID_COUNT - 1))
            if food not in self.snake:
                return food

    def handle_input(self) -> bool:
        """Handle user input for movement and game control."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    return False
                if event.key == pygame.K_r and self.state.game_over:
                    self.reset_game()
                self._handle_direction_change(event.key)
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
                self.direction = new_direction

    def update(self) -> None:
        """Update game state including snake movement and collision detection."""
        if self.state.game_over:
            return

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
            self.state.game_over = True
            return

        # Update snake position
        self.snake.insert(0, new_head)
        
        # Check if food is eaten
        if new_head == self.food:
            self.state.score += 1
            self.food = self.generate_food()
        else:
            self.snake.pop()

    def draw(self) -> None:
        """Draw the game state to the screen."""
        self.screen.fill(BLACK)
        
        # Draw snake
        for segment in self.snake:
            pygame.draw.rect(self.screen, GREEN,
                           (segment[0] * GRID_SIZE, segment[1] * GRID_SIZE,
                            GRID_SIZE - 2, GRID_SIZE - 2))
        
        # Draw food
        pygame.draw.rect(self.screen, RED,
                        (self.food[0] * GRID_SIZE, self.food[1] * GRID_SIZE,
                         GRID_SIZE - 2, GRID_SIZE - 2))

        # Draw score
        self._draw_text(f'Score: {self.state.score}', 10, 10)

        # Draw game over message
        if self.state.game_over:
            self._draw_text('Game Over! Press R to restart', WINDOW_SIZE // 2 - 100, WINDOW_SIZE // 2)

        pygame.display.flip()

    def _draw_text(self, text: str, x: int, y: int) -> None:
        """Helper method to draw text on the screen."""
        font = pygame.font.Font(None, 36)
        text_surface = font.render(text, True, WHITE)
        self.screen.blit(text_surface, (x, y))

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