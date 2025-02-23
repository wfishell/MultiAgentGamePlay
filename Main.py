import pygame
import sys
import random
from typing import List, Tuple, Set
from dataclasses import dataclass
from enum import Enum
import time

# Game Constants
GRID_SIZE = 10
CELL_SIZE = 60
WINDOW_SIZE = GRID_SIZE * CELL_SIZE
NUM_COPS = 4
NUM_ROBBERS = 4
MAX_SAFETY_ZONE_STEPS = 2
MOVE_INTERVAL = 1.0  # Time between moves in seconds

# Colors
COLORS = {
    "background": (255, 255, 255),  # White
    "obstacle": (0, 0, 0),          # Black
    "grid_line": (128, 128, 128),   # Gray
    "cop": (0, 0, 255),             # Blue
    "robber": (255, 0, 0),          # Red
    "safety_zone": (0, 255, 0, 128) # Semi-transparent green
}

class AgentType(Enum):
    COP = "cop"
    ROBBER = "robber"

@dataclass
class Agent:
    pos: Tuple[int, int]
    agent_type: AgentType
    last_safety_zone: int = -1
    safety_zone_steps: int = 0

class CopsAndRobbersGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
        pygame.display.set_caption("Cops and Robbers Game")
        
        self.grid = self.generate_grid()
        self.safety_zones = self.generate_safety_zones()
        # Initialize cops first so that robbers can be placed safely (not adjacent to any cop)
        self.cops = self.initialize_agents(NUM_COPS, AgentType.COP)
        self.robbers = self.initialize_agents(NUM_ROBBERS, AgentType.ROBBER)
        
        self.clock = pygame.time.Clock()
        self.running = True
        self.last_move_time = time.time()

    def generate_grid(self) -> List[List[int]]:
        """Generate the game grid with obstacles"""
        return [
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

    def generate_safety_zones(self) -> List[Set[Tuple[int, int]]]:
        """Generate two 2x2 safety zones"""
        zones = []
        # First safety zone in top-left (if possible)
        zone1 = {(1, 1), (1, 2), (2, 1), (2, 2)}
        # Second safety zone in bottom-right (if possible)
        zone2 = {(7, 7), (7, 8), (8, 7), (8, 8)}
        zones.extend([zone1, zone2])
        return zones

    def initialize_agents(self, num_agents: int, agent_type: AgentType) -> List[Agent]:
        """Initialize agents at random valid positions.
           For robbers, ensure that they are not adjacent to any cop.
        """
        agents = []
        occupied_positions = set()
        attempts = 0
        
        while len(agents) < num_agents:
            attempts += 1
            if attempts > 1000:
                raise Exception("Too many attempts to place agents. Adjust grid or constraints.")
            x = random.randint(0, GRID_SIZE - 1)
            y = random.randint(0, GRID_SIZE - 1)
            pos = (x, y)
            if not self.is_valid_position(pos) or pos in occupied_positions:
                continue
            if self.is_in_or_adjacent_to_safety_zone(pos):
                continue
            # For robbers, also ensure they are not adjacent to any cop (satisfies initial safety condition)
            if agent_type == AgentType.ROBBER:
                if any(abs(x - cop.pos[0]) <= 1 and abs(y - cop.pos[1]) <= 1 for cop in self.cops):
                    continue
            agents.append(Agent(pos, agent_type))
            occupied_positions.add(pos)
                    
        return agents

    def is_valid_position(self, pos: Tuple[int, int]) -> bool:
        """Check if position is within bounds and not an obstacle"""
        x, y = pos
        return (0 <= x < GRID_SIZE and 
                0 <= y < GRID_SIZE and 
                self.grid[x][y] == 0)

    def is_in_safety_zone(self, pos: Tuple[int, int]) -> int:
        """Return safety zone index if position is in a safety zone, -1 otherwise"""
        for i, zone in enumerate(self.safety_zones):
            if pos in zone:
                return i
        return -1

    def is_in_or_adjacent_to_safety_zone(self, pos: Tuple[int, int]) -> bool:
        """Check if position is in or adjacent to any safety zone"""
        x, y = pos
        for zone in self.safety_zones:
            for zx, zy in zone:
                if abs(x - zx) <= 1 and abs(y - zy) <= 1:
                    return True
        return False

    def get_valid_moves(self, agent: Agent) -> List[Tuple[int, int]]:
        """Get all valid moves for an agent.
           Note: The option to 'stay in place' has been removed to encourage movement (GF(allAgentsMove)).
        """
        x, y = agent.pos
        possible_moves = [(x+dx, y+dy) for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]]
        valid_moves = []
        
        for move in possible_moves:
            if not self.is_valid_position(move):
                continue
                
            if agent.agent_type == AgentType.COP:
                # Cops must not move into or adjacent to any safety zone.
                if not self.is_in_or_adjacent_to_safety_zone(move):
                    valid_moves.append(move)
            else:  # ROBBER
                # Robbers must not move adjacent to any cop.
                if not any(abs(move[0] - cop.pos[0]) <= 1 and 
                           abs(move[1] - cop.pos[1]) <= 1 for cop in self.cops):
                    valid_moves.append(move)
                    
        return valid_moves

    def move_agents(self):
        """Move all agents according to game rules"""
        # Build set of occupied positions
        current_positions = {agent.pos for agent in self.cops + self.robbers}
        
        # Move cops (simple chase algorithm)
        for cop in self.cops:
            valid_moves = self.get_valid_moves(cop)
            # Exclude positions already occupied by another agent
            valid_moves = [move for move in valid_moves if move not in current_positions]
            if valid_moves:
                # Move towards the nearest robber
                nearest_robber = min(self.robbers, 
                                     key=lambda r: abs(r.pos[0] - cop.pos[0]) + abs(r.pos[1] - cop.pos[1]))
                best_move = min(valid_moves, 
                                key=lambda m: abs(m[0] - nearest_robber.pos[0]) + abs(m[1] - nearest_robber.pos[1]))
                current_positions.remove(cop.pos)
                cop.pos = best_move
                current_positions.add(cop.pos)

        # Move robbers (escape algorithm with bias towards safety zones)
        for robber in self.robbers:
            valid_moves = self.get_valid_moves(robber)
            valid_moves = [move for move in valid_moves if move not in current_positions]
            if valid_moves:
                # If there is at least one move that leads into a safety zone, prefer it
                safety_moves = [m for m in valid_moves if self.is_in_safety_zone(m) != -1]
                if safety_moves:
                    chosen_move = random.choice(safety_moves)
                    new_zone = self.is_in_safety_zone(chosen_move)
                    # If entering a different safety zone, record it as a visit
                    if new_zone != robber.last_safety_zone:
                        robber.last_safety_zone = new_zone
                    # Increment steps in safety zone; if too many, force leaving
                    robber.safety_zone_steps += 1
                    if robber.safety_zone_steps >= MAX_SAFETY_ZONE_STEPS:
                        non_safety_moves = [m for m in valid_moves if self.is_in_safety_zone(m) == -1]
                        if non_safety_moves:
                            chosen_move = random.choice(non_safety_moves)
                            robber.safety_zone_steps = 0
                else:
                    # If no safety move is available, choose the move that maximizes distance from cops
                    chosen_move = max(valid_moves, 
                                      key=lambda m: min(abs(m[0] - cop.pos[0]) + abs(m[1] - cop.pos[1]) for cop in self.cops))
                    robber.safety_zone_steps = 0  # Reset if leaving safety zone
                current_positions.remove(robber.pos)
                robber.pos = chosen_move
                current_positions.add(robber.pos)

    def draw(self):
        """Draw the game state"""
        self.screen.fill(COLORS["background"])
        
        # Draw grid and obstacles
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                if self.grid[i][j] == 1:
                    pygame.draw.rect(self.screen, COLORS["obstacle"],
                                     (j * CELL_SIZE, i * CELL_SIZE, CELL_SIZE, CELL_SIZE))

        # Draw safety zones
        for zone in self.safety_zones:
            for x, y in zone:
                surface = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                pygame.draw.rect(surface, COLORS["safety_zone"],
                                 (0, 0, CELL_SIZE, CELL_SIZE))
                self.screen.blit(surface, (y * CELL_SIZE, x * CELL_SIZE))

        # Draw agents
        for cop in self.cops:
            pygame.draw.circle(self.screen, COLORS["cop"],
                               (cop.pos[1] * CELL_SIZE + CELL_SIZE//2,
                                cop.pos[0] * CELL_SIZE + CELL_SIZE//2),
                               CELL_SIZE//3)

        for robber in self.robbers:
            pygame.draw.circle(self.screen, COLORS["robber"],
                               (robber.pos[1] * CELL_SIZE + CELL_SIZE//2,
                                robber.pos[0] * CELL_SIZE + CELL_SIZE//2),
                               CELL_SIZE//3)

        # Draw grid lines
        for i in range(GRID_SIZE + 1):
            pygame.draw.line(self.screen, COLORS["grid_line"],
                             (i * CELL_SIZE, 0),
                             (i * CELL_SIZE, WINDOW_SIZE))
            pygame.draw.line(self.screen, COLORS["grid_line"],
                             (0, i * CELL_SIZE),
                             (WINDOW_SIZE, i * CELL_SIZE))

        pygame.display.flip()

    def run(self):
        """Main game loop"""
        while self.running:
            current_time = time.time()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False

            # Move agents automatically based on time interval
            if current_time - self.last_move_time >= MOVE_INTERVAL:
                self.move_agents()
                self.last_move_time = current_time

            self.draw()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = CopsAndRobbersGame()
    game.run()
