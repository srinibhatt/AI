import random
import time
import csv
from datetime import datetime, timedelta

# Seed for generating random start states. Can be replaced with any integer.
seed = 111
# Maximum depth to limit the search. Adjust as needed.
max_depth = 30

class Puzzle:
    """
    A class to represent the 8-puzzle problem and solve it using the IDA* algorithm.
    """
    def __init__(self, initial, goal):
        # Initial and goal states of the puzzle
        self.initial = initial[2]
        self.goal = goal[2]
        # Size of the puzzle
        self.size = len(self.initial)
        # Precompute goal positions for all values for efficient lookup
        self.goal_positions = {val: (r, c) for r, row in enumerate(self.goal) for c, val in enumerate(row)}

    def h_manhattan(self, state):
        """
        Calculate the Manhattan distance heuristic from the current state to the goal state.
        """
        distance = sum(abs(r - self.goal_positions[val][0]) + abs(c - self.goal_positions[val][1])
                       for r, row in enumerate(state) for c, val in enumerate(row) if val)
        return distance

    def generate_successors(self, state):
        """
        Generate all possible successor states from the current state by moving the blank tile.
        """
        zero_row, zero_col = next((r, c) for r, row in enumerate(state) for c, val in enumerate(row) if not val)
        successors = []
        # Possible moves for the blank tile
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            new_r, new_c = zero_row + dr, zero_col + dc
            if 0 <= new_r < self.size and 0 <= new_c < self.size:
                new_state = [list(row) for row in state]
                new_state[zero_row][zero_col], new_state[new_r][new_c] = new_state[new_r][new_c], new_state[zero_row][zero_col]
                successors.append(new_state)
        return successors

    def ida_star(self, timeout_seconds=1):
        """
        Solve the puzzle using the IDA* algorithm with a specified timeout.
        """
        nodes_opened = [0]  # Track the number of nodes opened during the search

        def search(path, g, bound, start_time, nodes_opened):
            """
            Recursive search function to explore the state space within the cost bound.
            """
            nodes_opened[0] += 1
            current = path[-1]
            f = g + self.h_manhattan(current)
            # Terminate search based on bound, max depth, or timeout
            if f > bound or g > max_depth or datetime.now() - start_time > timedelta(seconds=timeout_seconds):
                return f, False, nodes_opened[0]
            if current == self.goal:
                return g, True, nodes_opened[0]
            min_bound = float('inf')
            for s in self.generate_successors(current):
                if s not in path:  # Avoid cycles
                    path.append(s)
                    t, found, nodes_opened_count = search(path, g+1, bound, start_time, nodes_opened)
                    if found:
                        return t, True, nodes_opened_count
                    if t < min_bound:
                        min_bound = t
                    path.pop()
            return min_bound, False, nodes_opened[0]

        start_time = datetime.now()
        bound = self.h_manhattan(self.initial)
        path = [self.initial]
        while True:
            t, found, nodes_opened_count = search(path, 0, bound, start_time, nodes_opened)
            if found or datetime.now() - start_time > timedelta(seconds=timeout_seconds):
                return path if found else None, nodes_opened_count
            bound = t

def solve_puzzle(start_state, goal_state):
    """
    Solve a single instance of the puzzle and return the solution metrics.
    """
    start_time = time.time()
    puzzle = Puzzle(start_state, goal_state)
    solution_path, nodes_opened = puzzle.ida_star()
    end_time = time.time()

    solution = solution_path is not None
    moves = len(solution_path) - 1 if solution else max_depth
    time_taken = end_time - start_time

    return (start_state, solution, moves, nodes_opened, time_taken)

def generate_start_states(seed, num_states=10):
    """
    Generate a list of random start states for the puzzle based on the given seed.
    """
    template_state = list(range(8, -1, -1))
    random.seed(seed)
    start_states = []
    for _ in range(num_states):
        shuffled_state = template_state[:]
        random.shuffle(shuffled_state)
        grid = [shuffled_state[i:i+3] for i in range(0, 9, 3)]
        blank_pos = next((r, c) for r, row in enumerate(grid) for c, val in enumerate(row) if val == 0)
        start_states.append([*blank_pos, grid])
    return start_states

def main():
    """
    Main function to solve multiple puzzles and write the results to a CSV file.
    """
    goal_state = [1, 1, [[1, 2, 3], [8, 0, 4], [7, 6, 5]]]
    start_states = generate_start_states(seed)

    with open('IDAstar_output.csv', 'w', newline='') as csvfile:
        fieldnames = ['Seed', 'Case Number', 'Start State', 'Solution Found', 'Number of Moves', 'Nodes Opened', 'Computing Time']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for i, start_state in enumerate(start_states, 1):
            result = solve_puzzle(start_state, goal_state)
            writer.writerow({
                'Seed': seed,
                'Case Number': i,
                'Start State': str(result[0]),
                'Solution Found': 1 if result[1] else 0,
                'Number of Moves': result[2],
                'Nodes Opened': result[3],
                'Computing Time': result[4]
            })

if __name__ == "__main__":
    main()
