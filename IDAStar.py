import random
import time
import csv
from datetime import datetime, timedelta

class Puzzle:
    def __init__(self, initial, goal):
        self.initial = initial[2]
        self.goal = goal[2]
        self.size = len(self.initial)
        self.goal_positions = {val: (r, c) for r, row in enumerate(self.goal) for c, val in enumerate(row)}

    def h_manhattan(self, state):
        distance = sum(abs(r - self.goal_positions[val][0]) + abs(c - self.goal_positions[val][1])
                       for r, row in enumerate(state) for c, val in enumerate(row) if val)
        return distance

    def generate_successors(self, state):
        zero_row, zero_col = next((r, c) for r, row in enumerate(state) for c, val in enumerate(row) if not val)
        successors = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            new_r, new_c = zero_row + dr, zero_col + dc
            if 0 <= new_r < self.size and 0 <= new_c < self.size:
                new_state = [list(row) for row in state]
                new_state[zero_row][zero_col], new_state[new_r][new_c] = new_state[new_r][new_c], new_state[zero_row][zero_col]
                successors.append(new_state)
        return successors

    def ida_star(self, max_depth=30, timeout_seconds=10):
        nodes_opened = [0]

        def search(path, g, bound, start_time, nodes_opened):
            nodes_opened[0] += 1
            current = path[-1]
            f = g + self.h_manhattan(current)
            if f > bound or g > max_depth or datetime.now() - start_time > timedelta(seconds=timeout_seconds):
                return f, False, nodes_opened[0]
            if current == self.goal:
                return g, True, nodes_opened[0]
            min_bound = float('inf')
            for s in self.generate_successors(current):
                if s not in path:
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
    start_time = time.time()
    puzzle = Puzzle(start_state, goal_state)
    solution_path, nodes_opened = puzzle.ida_star()
    end_time = time.time()

    solution = solution_path is not None
    moves = len(solution_path) - 1 if solution else 0
    time_taken = end_time - start_time

    return (start_state, solution, moves, nodes_opened, time_taken)

def generate_start_states(seed, num_states=10):
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
    seed = 123  # Replace with the last three digits of your student registration number
    goal_state = [1, 1, [[1, 2, 3], [8, 0, 4], [7, 6, 5]]]
    start_states = generate_start_states(seed)

    with open('IDAstar_output.csv', 'w', newline='') as csvfile:
        fieldnames = ['Case Number', 'Start State', 'Solution Found', 'Number of Moves', 'Nodes Opened', 'Computing Time']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for i, start_state in enumerate(start_states, 1):
            result = solve_puzzle(start_state, goal_state)
            writer.writerow({
                'Case Number': i,
                'Start State': str(result[0]),
                'Solution Found': 1 if result[1] else 0,
                'Number of Moves': result[2],
                'Nodes Opened': result[3],
                'Computing Time': result[4]
            })

if __name__ == "__main__":
    main()
