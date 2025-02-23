import pygame
import random
import sys
from typing import List, Tuple

# Initialize Pygame
pygame.init()

# Constants
GRID_SIZE = 10
CELL_SIZE = 60
WINDOW_SIZE = GRID_SIZE * CELL_SIZE
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)

# Set up display
screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
pygame.display.set_caption("Connected Grid")

def is_valid_grid(grid: List[List[int]]) -> bool:
    """Check if all white cells are connected"""
    def find_first_white() -> Tuple[int, int]:
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                if grid[i][j] == 0:  # 0 represents white
                    return (i, j)
        return (-1, -1)
    
    def flood_fill(x: int, y: int, visited: set) -> None:
        if (x, y) in visited or x < 0 or y < 0 or x >= GRID_SIZE or y >= GRID_SIZE:
            return
        if grid[x][y] == 1:  # 1 represents black
            return
        
        visited.add((x, y))
        # Check all four directions
        flood_fill(x+1, y, visited)
        flood_fill(x-1, y, visited)
        flood_fill(x, y+1, visited)
        flood_fill(x, y-1, visited)

    # Find first white cell
    start = find_first_white()
    if start == (-1, -1):
        return False

    # Do flood fill from first white cell
    visited = set()
    flood_fill(start[0], start[1], visited)

    # Count all white cells
    white_count = sum(row.count(0) for row in grid)
    
    # Check if we visited all white cells
    return len(visited) == white_count

def generate_grid() -> List[List[int]]:
    """Generate a fixed grid with 20% black squares"""
    # Define a fixed grid
    grid = [
        [0, 0, 1, 0, 0, 0, 1, 0, 0, 0],
        [0, 1, 1, 0, 0, 0, 0, 0, 1, 0],
        [0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
        [0, 0, 1, 0, 0, 0, 0, 1, 0, 0],
        [0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
        [1, 0, 0, 0, 0, 1, 0, 1, 0, 0],
        [0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 1, 0, 0, 1, 0],
        [0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
        [0, 0, 1, 0, 0, 0, 0, 0, 0, 0]
    ]
    return grid

def draw_grid(grid: List[List[int]]) -> None:
    """Draw the grid on the screen"""
    screen.fill(WHITE)
    
    # Draw cells
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            if grid[i][j] == 1:
                pygame.draw.rect(screen, BLACK, 
                               (j * CELL_SIZE, i * CELL_SIZE, CELL_SIZE, CELL_SIZE))
    
    # Draw grid lines
    for i in range(GRID_SIZE + 1):
        pygame.draw.line(screen, GRAY, 
                        (i * CELL_SIZE, 0), 
                        (i * CELL_SIZE, WINDOW_SIZE))
        pygame.draw.line(screen, GRAY, 
                        (0, i * CELL_SIZE), 
                        (WINDOW_SIZE, i * CELL_SIZE))

def main():
    grid = generate_grid()
    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    grid = generate_grid()  # Generate new grid on spacebar

        draw_grid(grid)
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    try:
        main()
    finally:
        pygame.quit()
        sys.exit()