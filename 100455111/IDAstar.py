import random
import time
import csv
from datetime import datetime, timedelta

# Seed for generating random start states, based on the last 3 digits of a registration number.
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
            :param initial (list of list): Initial state of the puzzle.
            :param goal (list of list): Goal state of the puzzle.
        """
        # Convert lists to tuples for immutability and efficiency
        self.initial = tuple(tuple(row) for row in initial[2])
        self.goal = tuple(tuple(row) for row in goal[2])
        self.size = len(self.initial)  # Size of the puzzle.
        # Precompute goal positions for efficient lookup during heuristic calculation.
        self.goal_positions = {val: (r, c) for r, row in enumerate(self.goal) for c, val in enumerate(row)}

    def h_manhattan(self, state):
        """
        Calculate the Manhattan distance heuristic from the current state to the goal state.

        Args:
            :param state (tuple of tuple): Current state of the puzzle.

        Returns:
            :return int: The total Manhattan distance of all tiles from their goal positions.
        """
        distance = 0
        for r, row in enumerate(state):
            for c, val in enumerate(row):
                if val:  # Skip the blank tile.
                    goal_r, goal_c = self.goal_positions[val]
                    distance += abs(r - goal_r) + abs(c - goal_c)
        return distance

    def generate_successors(self, state):
        """
        Generate all possible successor states from the current state by moving the blank tile.

        Args:
            :param state (tuple of tuple): Current state of the puzzle.

        Returns:
            :return list of tuple of tuple: A list of all possible successor states.
        """
        zero_row, zero_col = next((r, c) for r, row in enumerate(state) for c, val in enumerate(row) if not val)
        successors = []
        zero_row, zero_col = self.find_zero_position(state)  # Find the blank tile position.

        # Potential moves: up, down, left, right.
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            new_r, new_c = zero_row + dr, zero_col + dc
            if 0 <= new_r < self.size and 0 <= new_c < self.size:
                new_state = list(map(list, state))  # Make a copy and swap tiles.
                new_state[zero_row][zero_col], new_state[new_r][new_c] = new_state[new_r][new_c], new_state[zero_row][
                    zero_col]
                successors.append(tuple(map(tuple, new_state)))  # Convert back to tuple of tuples.
        return successors

    def find_zero_position(self, state):
        """Find the position of the blank tile (zero) in the state."""
        for row_index, row in enumerate(state):
            if 0 in row:
                return (row_index, row.index(0))
        return None

    def ida_star(self):
        """
        Solve the puzzle using the IDA* algorithm with a specified timeout.


        Returns:
            :return tuple: A tuple containing the solution path (if found), the number of nodes opened, and whether a solution was found.
        """
        nodes_opened = [0]  # Track the number of nodes opened during the search

        def search(path, g, bound, start_time, nodes_opened):
            """
            Recursive search function to explore the state space within the cost bound.

            Args:
                :param path (list): The current path taken to reach the state.
                :param g (int): The cost to reach the current state from the initial state.
                :param bound (int): The current cost bound for the search.
                :param start_time (datetime): The start time of the search to track elapsed time.
                :param nodes_opened (list of int): A single-element list tracking the number of nodes opened.

            Returns:
                :return tuple: A tuple containing the minimum cost exceeding the bound if not found, whether a solution was found, and the number of nodes opened.
            """

            current = path[-1]
            f = g + self.h_manhattan(current)
            if f > bound or g > max_depth:
                return f, False, nodes_opened[0]
            if current == self.goal:
                return g, True, nodes_opened[0]  # Goal state reached.

            min_bound = float('inf')
            for s in self.generate_successors(current):
                if s not in path:  # Avoid cycles.
                    path.append(s)
                    t, found, nodes_opened_count = search(path, g + 1, bound, start_time, nodes_opened)
                    if found:
                        return t, True, nodes_opened_count  # Solution found.
                    if t < min_bound:
                        min_bound = t
                    path.pop()  # Backtrack.
                    nodes_opened[0] += 1
            return min_bound, False, nodes_opened[0]

        start_time = datetime.now()
        bound = self.h_manhattan(self.initial)  # Initial bound based on heuristic.
        print(f"Initial bound: {bound}")
        path = [self.initial]
        while True:
            t, found, nodes_opened_count = search(path, 0, bound, start_time, nodes_opened)
            if found:


                return path if found else None, nodes_opened_count
            elif bound >= max_depth:
                # If no progress, terminate search.

                return None, nodes_opened_count
            else:
                # Increase bound and continue search.

                bound = t


def solve_puzzle(start_state, goal_state):
    """
    Solve a single instance of the puzzle and return the solution metrics.

    Args:
        :param start_state (list): The initial state of the puzzle.
        :param goal_state (list): The goal state of the puzzle.

    Returns:
        :return tuple: A tuple containing the initial state, whether a solution was found, the number of moves, nodes opened, and computing time.
    """
    start_time = time.time()
    puzzle = Puzzle(start_state, goal_state)
    solution_path, nodes_opened = puzzle.ida_star()
    end_time = time.time()

    solution = solution_path is not None
    moves = len(solution_path) - 1 if solution else max_depth
    time_taken = end_time - start_time

    # Print the outcome after solving each puzzle.
    if solution:
        print(f"Solved successfully. Moves: {moves}, Nodes Opened: {nodes_opened}, Time: {time_taken:.4f} seconds")
    else:
        print(
            f"Could not be solved within the depth limit. Nodes Opened: {nodes_opened}, Time: {time_taken:.4f} seconds")

    return (start_state, solution, moves, nodes_opened, time_taken)


def generate_start_states(seed, num_states=10):
    """
    Generate a list of random start states for the puzzle based on the given seed.

    Args:
        :param seed (int): Seed value for random number generator.
        :param num_states (int): Number of start states to generate.

    Returns:
        :return list: A list of start states for the puzzle.
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
    """Main function to solve multiple puzzles and write the results to a CSV file."""
    print("Starting to solve multiple 8-puzzle instances using IDA* algorithm...")
    goal_state = [1, 1, [[1, 2, 3], [8, 0, 4], [7, 6, 5]]]
    start_states = generate_start_states(seed)

    with open('IDAstar_output.csv', 'w', newline='') as csvfile:
        fieldnames = ['Seed', 'Case Number', 'Start State', 'Solution Found', 'Number of Moves', 'Nodes Opened',
                      'Computing Time']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for i, start_state in enumerate(start_states, 1):
            print(f"\nStarting to solve puzzle {i} with initial state: {start_state[2]}")
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

    print("\nAll puzzles have been attempted. Results are saved in IDAstar_output.csv")


if __name__ == "__main__":
    main()