import time
import pygame
import sys
import random
from collections import deque
from typing import List, Tuple

# --------------------------------------------------
# Environment Setup (Warehouse Grid)
# --------------------------------------------------

# Environment constants
GRID_SIZE = 10
CELL_SIZE = 60
WINDOW_SIZE = GRID_SIZE * CELL_SIZE

# Color definitions
COLORS = {
    "background": (255, 255, 255),
    "obstacle": (0, 0, 0),
    "robot": (0, 255, 0),
    "package": (255, 0, 0),
    "delivered_package": (128, 128, 128),
    "grid_line": (128, 128, 128)
}

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
pygame.display.set_caption("Warehouse Package Delivery")

class Robot:
    def __init__(self, initial_pos, delivery_zone):
        self.pos = initial_pos  # (row, col)
        self.delivery_zone = delivery_zone  # (row_min, col_min, row_max, col_max)
        self.state = "navigating"  # or "carrying"
        self.package = None  # Reference to the package object if carrying
        self.plan = []  # List of positions computed by the planner

class Package:
    def __init__(self, pos, delivery_zone):
        self.pos = pos  # (row, col)
        self.delivery_zone = delivery_zone  # (row_min, col_min, row_max, col_max)

def generate_warehouse_grid() -> List[List[int]]:
    """Generate a grid layout for the warehouse environment."""
    grid = [[0 for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
    # Add static obstacles (cell walls)
    for i in range(GRID_SIZE):
        grid[0][i] = 1
        grid[GRID_SIZE - 1][i] = 1
        grid[i][0] = 1
        grid[i][GRID_SIZE - 1] = 1
    # Add delivery zones (marked as 2)
    for i in range(2, 6):
        for j in range(2, 6):
            grid[i][j] = 2
            grid[i][GRID_SIZE - j - 1] = 2
    return grid

def draw_warehouse_grid(grid: List[List[int]], robots: List[Robot],
                          packages: List[Package], delivered_packages: List[Tuple[int, int]]) -> None:
    """Draw the warehouse grid, robots, packages, and delivered packages."""
    screen.fill(COLORS["background"])
    # Draw obstacles and delivery zones
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            if grid[i][j] == 1:
                pygame.draw.rect(screen, COLORS["obstacle"],
                                 (j * CELL_SIZE, i * CELL_SIZE, CELL_SIZE, CELL_SIZE))
            elif grid[i][j] == 2:
                pygame.draw.rect(screen, COLORS["delivered_package"],
                                 (j * CELL_SIZE, i * CELL_SIZE, CELL_SIZE, CELL_SIZE))
    # Draw robots
    for robot in robots:
        pygame.draw.rect(screen, COLORS["robot"],
                         (robot.pos[1] * CELL_SIZE, robot.pos[0] * CELL_SIZE, CELL_SIZE, CELL_SIZE))
    # Draw packages
    for package in packages:
        pygame.draw.rect(screen, COLORS["package"],
                         (package.pos[1] * CELL_SIZE, package.pos[0] * CELL_SIZE, CELL_SIZE, CELL_SIZE))
    # Draw delivered packages
    for pos in delivered_packages:
        pygame.draw.rect(screen, COLORS["delivered_package"],
                         (pos[1] * CELL_SIZE, pos[0] * CELL_SIZE, CELL_SIZE, CELL_SIZE))
    # Draw grid lines
    for i in range(GRID_SIZE + 1):
        pygame.draw.line(screen, COLORS["grid_line"],
                         (i * CELL_SIZE, 0), (i * CELL_SIZE, WINDOW_SIZE))
        pygame.draw.line(screen, COLORS["grid_line"],
                         (0, i * CELL_SIZE), (WINDOW_SIZE, i * CELL_SIZE))

def is_valid_move(grid: List[List[int]], pos: Tuple[int, int]) -> bool:
    """Check if a move to the given position is valid."""
    r, c = pos
    if r < 0 or r >= GRID_SIZE or c < 0 or c >= GRID_SIZE:
        return False
    # Allow moves on free space (0) or delivery zone (2)
    return grid[r][c] in (0, 2)

def run_environment():
    """Main loop to run the warehouse package delivery environment."""
    global global_grid, global_robots, global_packages
    global_grid = generate_warehouse_grid()
    # Create two robots with different delivery zones
    global_robots = [
        Robot((1, 1), (2, 2, 5, 5)),
        Robot((GRID_SIZE - 2, GRID_SIZE - 2), (2, GRID_SIZE - 5, 5, GRID_SIZE - 2))
    ]
    global_packages = [
        Package((4, 4), (2, 2, 5, 5)),
        Package((4, GRID_SIZE - 5), (2, GRID_SIZE - 5, 5, GRID_SIZE - 2))
    ]
    delivered_packages = []
    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Simple reactive behavior for each robot
        for robot in global_robots:
            # If navigating, plan a path to the nearest package
            if robot.state == "navigating":
                if global_packages:
                    target = min(global_packages, key=lambda p: abs(p.pos[0] - robot.pos[0]) + abs(p.pos[1] - robot.pos[1])).pos
                    robot.plan = find_path(global_grid, robot.pos, target)
                    if robot.plan and len(robot.plan) > 1:
                        robot.pos = robot.plan[1]
            # If carrying, plan a path to the center of the delivery zone
            elif robot.state == "carrying":
                zone = robot.delivery_zone
                target = ((zone[0] + zone[2]) // 2, (zone[1] + zone[3]) // 2)
                robot.plan = find_path(global_grid, robot.pos, target)
                if robot.plan and len(robot.plan) > 1:
                    robot.pos = robot.plan[1]

        # Package pickup: if a robot reaches a package, pick it up.
        remaining_packages = []
        for package in global_packages:
            picked = False
            for robot in global_robots:
                if robot.state == "navigating" and robot.pos == package.pos:
                    robot.state = "carrying"
                    robot.package = package
                    picked = True
                    break
            if not picked:
                remaining_packages.append(package)
        global_packages = remaining_packages

        # Package delivery: if a robot carrying a package reaches its delivery zone, deliver it.
        for robot in global_robots:
            if robot.state == "carrying":
                zone = robot.delivery_zone
                if zone[0] <= robot.pos[0] <= zone[2] and zone[1] <= robot.pos[1] <= zone[3]:
                    delivered_packages.append(robot.pos)
                    robot.state = "navigating"
                    robot.package = None

        # Generate new packages if all have been delivered
        if not global_packages:
            global_packages = generate_new_packages()

        draw_warehouse_grid(global_grid, global_robots, global_packages, delivered_packages)
        pygame.display.flip()
        clock.tick(5)  # Slow down for visualization

    pygame.quit()
    sys.exit()

def generate_new_packages() -> List[Package]:
    """Generate new packages at random spawn points not on obstacles or occupied by robots."""
    new_packages = []
    attempts = 0
    while len(new_packages) < 2 and attempts < 50:
        r = random.randint(1, GRID_SIZE - 2)
        c = random.randint(1, GRID_SIZE - 2)
        if global_grid[r][c] == 0 and all(robot.pos != (r, c) for robot in global_robots):
            # Assign package to a delivery zone based on position
            if r < GRID_SIZE // 2:
                new_packages.append(Package((r, c), (2, 2, 5, 5)))
            else:
                new_packages.append(Package((r, c), (2, GRID_SIZE - 5, 5, GRID_SIZE - 2)))
        attempts += 1
    return new_packages

def find_path(grid: List[List[int]], start: Tuple[int, int], goal: Tuple[int, int]) -> List[Tuple[int, int]]:
    """Find a shortest path from start to goal using BFS."""
    queue = deque([start])
    came_from = {start: None}
    while queue:
        current = queue.popleft()
        if current == goal:
            break
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            next_pos = (current[0] + dx, current[1] + dy)
            if (0 <= next_pos[0] < GRID_SIZE and 0 <= next_pos[1] < GRID_SIZE and
                    grid[next_pos[0]][next_pos[1]] != 1 and next_pos not in came_from):
                queue.append(next_pos)
                came_from[next_pos] = current
    if goal not in came_from:
        return []
    # Reconstruct path
    path = []
    current = goal
    while current is not None:
        path.append(current)
        current = came_from[current]
    path.reverse()
    return path

# --------------------------------------------------
# Reactive Planning Manager (Warehouse Package Delivery)
# --------------------------------------------------

def create_groups(ltl_constraints: List[str]) -> List[List[str]]:
    """Create groups based on the LTL constraints."""
    groups = []
    current_group = []
    for constraint in ltl_constraints:
        if constraint.startswith("G("):
            if current_group:
                groups.append(current_group)
            current_group = [constraint]
        else:
            current_group.append(constraint)
    if current_group:
        groups.append(current_group)
    return groups

def initialize_status(num_groups: int) -> Tuple[List[bool], List[bool]]:
    """Initialize flags for each group."""
    replan_flags = [False] * num_groups
    dispatch_flags = [False] * num_groups
    return replan_flags, dispatch_flags

def detect_input() -> bool:
    """Detect external input: generate new packages if none remain."""
    global global_packages
    return len(global_packages) == 0

def check_agent_status(agent_index: int) -> bool:
    """Check the status of an agent (robot) for replanning.
       Returns True if the robot is blocked (e.g., no valid moves).
    """
    robot = global_robots[agent_index]
    # Check adjacent cells; if none are valid, then the robot is stuck.
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        next_pos = (robot.pos[0] + dx, robot.pos[1] + dy)
        if is_valid_move(global_grid, next_pos):
            return False
    return True

def compute_planning_specification(current_constraints, status_parameters) -> str:
    """Compute the planning specification based on current constraints.
       For simulation purposes, simply return a combined string.
    """
    return " & ".join(current_constraints)

def plan_path(transition_system: List[List[int]], planning_spec: str, robot: Robot,
              dispatch_flag: bool, dispatch_fn) -> None:
    """Plan a new path for the given robot using BFS.
       If the robot is navigating, plan a path to the nearest package.
       If carrying, plan a path to the center of its delivery zone.
    """
    target = None
    if robot.state == "navigating":
        if global_packages:
            target = min(global_packages, key=lambda p: abs(p.pos[0] - robot.pos[0]) + abs(p.pos[1] - robot.pos[1])).pos
    elif robot.state == "carrying":
        zone = robot.delivery_zone
        target = ((zone[0] + zone[2]) // 2, (zone[1] + zone[3]) // 2)
    if target is None:
        return
    path = find_path(transition_system, robot.pos, target)
    if path and len(path) > 1:
        next_step = path[1]
        dispatch_fn(robot, next_step)
        robot.plan = path

def dispatch_agent(robot: Robot, next_step: Tuple[int, int]) -> None:
    """Dispatch a new plan for the robot by moving it to the next step if valid."""
    if is_valid_move(global_grid, next_step):
        robot.pos = next_step

def verify_constraint(group: List[str], transition_system: List[List[int]]) -> bool:
    """Check if the planning constraint for the group is satisfied.
       For robots, ensure no two robots share the same grid cell.
       For packages, check if all packages have been delivered.
    """
    # For robot groups (assume first len(global_robots) groups)
    if group and group[0].startswith("G("):
        positions = [robot.pos for robot in global_robots]
        return len(positions) == len(set(positions))
    # For package groups, consider constraints satisfied if no packages remain.
    return len(global_packages) == 0

def reset_group_constraint(group: List[str], original_group: List[str]) -> List[str]:
    """Reset the group's constraint to its original value."""
    return original_group

def main_manager(transition_systems: List[List[int]], ltl_constraints: List[str]) -> None:
    """Main manager function running continuously to update and replan agent trajectories."""
    global global_grid, global_robots, global_packages
    # For simulation, assume global_grid, global_robots, and global_packages are already defined.
    groups = create_groups(ltl_constraints)
    original_groups = [grp.copy() for grp in groups]
    num_groups = len(global_robots)  # Assume one group per robot
    replan_flags, dispatch_flags = initialize_status(num_groups)
    planning_specs = [None] * num_groups

    while True:
        for idx in range(num_groups):
            robot = global_robots[idx]
            # Assume robot is free initially.
            planning_free = True
            replan_flags[idx] = False

            # Check for external input (e.g., new packages) or if the robot is stuck.
            if detect_input() or check_agent_status(idx):
                planning_free = False
                replan_flags[idx] = True

            # Set planning specification based on current constraints.
            if planning_free:
                planning_specs[idx] = compute_planning_specification(groups[idx], None)
            else:
                planning_specs[idx] = compute_planning_specification(groups[idx], None)

            # If replanning is needed, compute and execute a new plan.
            if replan_flags[idx]:
                plan_path(global_grid, planning_specs[idx], robot, dispatch_flags[idx], dispatch_agent)
                dispatch_flags[idx] = False
                replan_flags[idx] = False

            # Verify constraint satisfaction.
            if verify_constraint(groups[idx], global_grid):
                groups[idx] = reset_group_constraint(groups[idx], original_groups[idx])
        time.sleep(0.1)

# --------------------------------------------------
# Main entry point
# --------------------------------------------------

if __name__ == "__main__":
    # Run the environment in the main thread.
    try:
        run_environment()
    except Exception as e:
        print("Exiting environment loop:", e)
