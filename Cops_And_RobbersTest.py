import time
import random
import pygame
import sys
from typing import List, Tuple, Set

# --------------------------------------------------
# Environment Setup (Cops and Robbers Maze)
# ----------------------------------------------x----

# Environment constants
GRID_SIZE = 20
CELL_SIZE = 30
WINDOW_SIZE = GRID_SIZE * CELL_SIZE

# Color definitions
COLORS = {
    "background": (255, 255, 255),
    "obstacle": (0, 0, 0),
    "grid_line": (128, 128, 128),
    "cop": (255, 0, 0),
    "robber": (0, 0, 255),
    "safety_zone": (0, 255, 0)
}

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
pygame.display.set_caption("Cops and Robbers Maze")

# Safety zone top-left coordinates (each safety zone is 2x2)
SAFETY_ZONE_TOP_LEFTS = [(3, 3), (14, 14)]

def generate_maze() -> List[List[int]]:
    """
    Generate a random maze layout for the environment.
    0 represents a free (white) cell, 1 represents an obstacle.
    Then, carve out 2x2 safety zones (cells set to 2) at specified locations.
    """
    maze = []
    for _ in range(GRID_SIZE):
        row = [0 if random.random() > 0.2 else 1 for _ in range(GRID_SIZE)]
        maze.append(row)
    
    # Carve out safety zones as 2x2 blocks with value 2
    for (r, c) in SAFETY_ZONE_TOP_LEFTS:
        for i in range(2):
            for j in range(2):
                if 0 <= r + i < GRID_SIZE and 0 <= c + j < GRID_SIZE:
                    maze[r + i][c + j] = 2
    return maze

def draw_maze(maze: List[List[int]], cop_positions: List[Tuple[int, int]], robber_positions: List[Tuple[int, int]]) -> None:
    """
    Draw the maze, cops, robbers, and safety zones on the screen.
    """
    screen.fill(COLORS["background"])
    
    # Draw cells
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            cell = maze[i][j]
            if cell == 1:
                color = COLORS["obstacle"]
            elif cell == 2:
                color = COLORS["safety_zone"]
            else:
                continue  # free cell; no fill
            pygame.draw.rect(screen, color, (j * CELL_SIZE, i * CELL_SIZE, CELL_SIZE, CELL_SIZE))
    
    # Draw cops
    for cop_pos in cop_positions:
        pygame.draw.rect(screen, COLORS["cop"], (cop_pos[1] * CELL_SIZE, cop_pos[0] * CELL_SIZE, CELL_SIZE, CELL_SIZE))
    
    # Draw robbers
    for robber_pos in robber_positions:
        pygame.draw.rect(screen, COLORS["robber"], (robber_pos[1] * CELL_SIZE, robber_pos[0] * CELL_SIZE, CELL_SIZE, CELL_SIZE))
    
    # Draw grid lines
    for i in range(GRID_SIZE + 1):
        pygame.draw.line(screen, COLORS["grid_line"], (i * CELL_SIZE, 0), (i * CELL_SIZE, WINDOW_SIZE))
        pygame.draw.line(screen, COLORS["grid_line"], (0, i * CELL_SIZE), (WINDOW_SIZE, i * CELL_SIZE))

def get_valid_moves(pos: Tuple[int, int], maze: List[List[int]], allowed: Set[int]) -> List[Tuple[int, int]]:
    """
    Return valid moves for an agent at position 'pos'.
    Allowed cells have values in the 'allowed' set.
    Moves are up, down, left, right.
    """
    moves = []
    row, col = pos
    for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
        nr, nc = row + dr, col + dc
        if 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE:
            if maze[nr][nc] in allowed:
                moves.append((nr, nc))
    return moves

def update_positions(maze: List[List[int]], cop_positions: List[Tuple[int, int]], robber_positions: List[Tuple[int, int]]) -> None:
    """
    Update positions for cops and robbers.
    Cops move only in free cells (maze value 0) while robbers can move in free cells or safety zones (0 or 2).
    Movement is random among available valid moves.
    """
    # Update cops
    new_cop_positions = []
    for pos in cop_positions:
        valid = get_valid_moves(pos, maze, allowed={0})
        if valid:
            new_pos = random.choice(valid)
        else:
            new_pos = pos
        new_cop_positions.append(new_pos)
    cop_positions[:] = new_cop_positions
    
    # Update robbers
    new_robber_positions = []
    for pos in robber_positions:
        valid = get_valid_moves(pos, maze, allowed={0, 2})
        # To avoid collision with cops, filter out moves that are occupied by a cop.
        valid = [move for move in valid if move not in cop_positions]
        if valid:
            new_pos = random.choice(valid)
        else:
            new_pos = pos
        new_robber_positions.append(new_pos)
    robber_positions[:] = new_robber_positions

def run_environment():
    """
    Main loop to run the Cops and Robbers Maze environment.
    Press SPACE to regenerate the maze.
    Agents move every second.
    """
    maze = generate_maze()
    cop_positions = [(0, 0), (0, 1), (1, 0), (1, 1)]  # Example initial cop positions
    robber_positions = [(3, 3), (3, 4), (4, 3), (4, 4)]  # Example initial robber positions
    running = True
    clock = pygame.time.Clock()
    last_move_time = time.time()
    MOVE_INTERVAL = 1.0  # seconds
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    maze = generate_maze()
        
        current_time = time.time()
        if current_time - last_move_time >= MOVE_INTERVAL:
            update_positions(maze, cop_positions, robber_positions)
            last_move_time = current_time
        
        draw_maze(maze, cop_positions, robber_positions)
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

# --------------------------------------------------
# Reactive Planning Manager (Cops and Robbers)
# --------------------------------------------------
# (Note: The reactive planning manager is preserved as a placeholder.
# Its integration with movement is not implemented in this version.)

def create_groups(ltl_constraints: List[str]) -> List[str]:
    """
    Create groups based on the LTL constraints.
    """
    groups = []
    for constraint in ltl_constraints:
        if "collision" in constraint:
            groups.append("collision")
        elif "adjacentToCop" in constraint:
            groups.append("adjacentToCop")
        elif "inSafetyZone" in constraint:
            groups.append("inSafetyZone")
        elif "stayInSafetyZoneForTooLong" in constraint:
            groups.append("stayInSafetyZoneForTooLong")
        elif "visitNewSafetyZone" in constraint:
            groups.append("visitNewSafetyZone")
        elif "allAgentsMove" in constraint:
            groups.append("allAgentsMove")
        elif "copsChaseRobbers" in constraint:
            groups.append("copsChaseRobbers")
    return groups

def initialize_status(num_groups: int) -> Tuple[List[bool], List[bool]]:
    """
    Initialize flags for each group.
    Returns two lists: one for replanning flags and one for dispatch flags.
    """
    replan_flags = [False] * num_groups
    dispatch_flags = [False] * num_groups
    return replan_flags, dispatch_flags

def detect_input(cop_positions: List[Tuple[int, int]], robber_positions: List[Tuple[int, int]]) -> bool:
    """
    Check if any robber is adjacent to a cop or in a safety zone.
    """
    for robber_pos in robber_positions:
        for cop_pos in cop_positions:
            # Check if robber is adjacent to cop
            if abs(robber_pos[0] - cop_pos[0]) <= 1 and abs(robber_pos[1] - cop_pos[1]) <= 1:
                return True
        # Check if robber is in a safety zone (using top-lefts, compare against 2x2 block)
        for (r, c) in SAFETY_ZONE_TOP_LEFTS:
            if r <= robber_pos[0] < r + 2 and c <= robber_pos[1] < c + 2:
                return True
    return False

def check_agent_status(agent_index: int, cop_positions: List[Tuple[int, int]], robber_positions: List[Tuple[int, int]]) -> bool:
    """
    Check if a robber is in a safety zone or adjacent to a cop.
    """
    robber_pos = robber_positions[agent_index]
    for cop_pos in cop_positions:
        if abs(robber_pos[0] - cop_pos[0]) <= 1 and abs(robber_pos[1] - cop_pos[1]) <= 1:
            return True
    for (r, c) in SAFETY_ZONE_TOP_LEFTS:
        if r <= robber_pos[0] < r + 2 and c <= robber_pos[1] < c + 2:
            return True
    return False

def compute_planning_specification(current_constraints, status_parameters) -> str:
    """
    Compute the planning specification based on current constraints.
    This function should integrate safety, progress, and liveness conditions.
    """
    return "generic_spec"

def plan_path(transition_system, planning_spec, current_state, dispatch_flag, dispatch_fn) -> None:
    """
    Generic planner function to compute a new plan for an agent.
    """
    return

def dispatch_agent(agent_index: int, new_position: Tuple[int, int], cop_positions: List[Tuple[int, int]], robber_positions: List[Tuple[int, int]]) -> None:
    """
    Dispatch a robber to a new position, ensuring it doesn't collide with cops or obstacles.
    """
    robber_positions[agent_index] = new_position

def verify_constraint(group, transition_system) -> bool:
    """
    Check if the planning constraint for the group is satisfied.
    """
    return False

def reset_group_constraint(group, original_group):
    """
    Reset the group's constraint to its original value.
    """
    return original_group

def main_manager(transition_systems: List, ltl_constraints: List[str],
                 cop_positions: List[Tuple[int, int]], robber_positions: List[Tuple[int, int]]) -> None:
    """
    Main manager function running continuously to update and replan agent trajectories.
    """
    groups = create_groups(ltl_constraints)
    original_groups = groups.copy()
    num_groups = len(groups)
    replan_flags, dispatch_flags = initialize_status(num_groups)
    planning_specs = [None] * num_groups
    
    while True:
        for idx in range(num_groups):
            planning_free = True
            replan_flags[idx] = False
            
            if detect_input(cop_positions, robber_positions) or check_agent_status(idx, cop_positions, robber_positions):
                planning_free = False
                replan_flags[idx] = True
            
            if planning_free:
                planning_specs[idx] = "safe OR progress"
            else:
                planning_specs[idx] = "new OR recovery"
            
            if replan_flags[idx]:
                compute_planning_specification(groups[idx], None)
                plan_path(transition_systems[idx], planning_specs[idx], transition_systems[idx], dispatch_flags[idx], dispatch_agent)
                dispatch_flags[idx] = False
                replan_flags[idx] = False
            
            if verify_constraint(groups[idx], transition_systems[idx]):
                groups[idx] = reset_group_constraint(groups[idx], original_groups[idx])
        time.sleep(0.1)

# --------------------------------------------------
# Example JSON Reactive Synthesis Input
# --------------------------------------------------
example_reactive_input = {
    "ltl_formulation": "G(¬collision) & G(¬adjacentToCop) & GF(inSafetyZone) & G(¬stayInSafetyZoneForTooLong) & GF(visitNewSafetyZone) & GF(allAgentsMove) & GF(copsChaseRobbers)",
    "System_Player": {
        "name": "Robbers",
        "init": "¬inSafetyZone & ¬adjacentToCop",
        "safety": "¬collision & ¬adjacentToCop & ¬stayInSafetyZoneForTooLong",
        "prog": "GF(inSafetyZone) & GF(visitNewSafetyZone) & GF(allAgentsMove)"
    },
    "Environment_Player": {
        "name": "Cops",
        "init": "¬inSafetyZone & ¬adjacentToRobber",
        "safety": "¬collision & ¬inSafetyZone & ¬adjacentToSafetyZone",
        "prog": "GF(allAgentsMove) & GF(copsChaseRobbers)"
    },
    "Inputs": ["robberPositions", "copPositions", "mazeLayout"],
    "Outputs": ["robberMoves", "copMoves"]
}

# --------------------------------------------------
# Main entry point for testing
# --------------------------------------------------
if __name__ == "__main__":
    try:
        run_environment()
    except Exception as e:
        print("Exiting environment loop:", e)
