import random
import time
import csv
from datetime import datetime, timedelta

# Seed for generating random start states. defaulted with last 3 digits for registration number.
seed = 111
# Maximum depth to limit the search. Adjust as needed.
max_depth = 30


class Puzzle:
    """
    A class to represent the 8-puzzle problem and solve it using the IDA* algorithm.

    Attributes:
        initial (tuple of tuple): Initial state of the puzzle.
        goal (tuple of tuple): Goal state of the puzzle.
        size (int): Size of the puzzle (number of rows/columns).
        goal_positions (dict): Precomputed positions of each value in the goal state for faster lookups.
    """

    def __init__(self, initial, goal):
        """
        Initialize the Puzzle with initial and goal states.

        Args:
            initial (list of list): Initial state of the puzzle.
            goal (list of list): Goal state of the puzzle.
        """
        # Convert lists to tuples for immutability and efficiency
        self.initial = tuple(tuple(row) for row in initial[2])
        self.goal = tuple(tuple(row) for row in goal[2])
        self.size = len(self.initial)
        # Precompute goal positions for all values for efficient lookup
        self.goal_positions = {val: (r, c) for r, row in enumerate(self.goal) for c, val in enumerate(row)}

    def h_manhattan(self, state):
        """
        Calculate the Manhattan distance heuristic from the current state to the goal state.

        Args:
            state (tuple of tuple): Current state of the puzzle.

        Returns:
            int: The total Manhattan distance of all tiles from their goal positions.
        """
        distance = 0
        for r, row in enumerate(state):
            for c, val in enumerate(row):
                if val:
                    goal_r, goal_c = self.goal_positions[val]
                    distance += abs(r - goal_r) + abs(c - goal_c)
        return distance

    def generate_successors(self, state):
        """
        Generate all possible successor states from the current state by moving the blank tile.

        Args:
            state (tuple of tuple): Current state of the puzzle.

        Returns:
            list of tuple of tuple: A list of all possible successor states.
        """
        zero_row, zero_col = next((r, c) for r, row in enumerate(state) for c, val in enumerate(row) if not val)
        successors = []
        # Possible moves for the blank tile
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            new_r, new_c = zero_row + dr, zero_col + dc
            if 0 <= new_r < self.size and 0 <= new_c < self.size:
                new_state = [list(row) for row in state]  # Convert to list to modify
                # Swap the blank tile with an adjacent tile
                new_state[zero_row][zero_col], new_state[new_r][new_c] = new_state[new_r][new_c], new_state[zero_row][
                    zero_col]
                # Convert back to tuple for immutability
                successors.append(tuple(tuple(row) for row in new_state))
        return successors

    def ida_star(self, timeout_seconds=1):
        """
        Solve the puzzle using the IDA* algorithm with a specified timeout.

        Args:
            timeout_seconds (int): The maximum allowed time in seconds to solve the puzzle.

        Returns:
            tuple: A tuple containing the solution path (if found), the number of nodes opened, and whether a solution was found.
        """
        nodes_opened = [0]  # Track the number of nodes opened during the search

        def search(path, g, bound, start_time, nodes_opened):
            """
            Recursive search function to explore the state space within the cost bound.

            Args:
                path (list): The current path taken to reach the state.
                g (int): The cost to reach the current state from the initial state.
                bound (int): The current cost bound for the search.
                start_time (datetime): The start time of the search to track elapsed time.
                nodes_opened (list of int): A single-element list tracking the number of nodes opened.

            Returns:
                tuple: A tuple containing the minimum cost exceeding the bound if not found, whether a solution was found, and the number of nodes opened.
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
                    t, found, nodes_opened_count = search(path, g + 1, bound, start_time, nodes_opened)
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

    Args:
        start_state (list): The initial state of the puzzle.
        goal_state (list): The goal state of the puzzle.

    Returns:
        tuple: A tuple containing the initial state, whether a solution was found, the number of moves, nodes opened, and computing time.
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

    Args:
        seed (int): Seed value for random number generator.
        num_states (int): Number of start states to generate.

    Returns:
        list: A list of start states for the puzzle.
    """
    template_state = list(range(8, -1, -1))
    random.seed(seed)
    start_states = []
    for _ in range(num_states):
        shuffled_state = template_state[:]
        random.shuffle(shuffled_state)
        grid = [shuffled_state[i:i + 3] for i in range(0, 9, 3)]
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
        fieldnames = ['Seed', 'Case Number', 'Start State', 'Solution Found', 'Number of Moves', 'Nodes Opened',
                      'Computing Time']
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
