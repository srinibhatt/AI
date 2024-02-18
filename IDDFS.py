import copy
import itertools
import random
import csv
import time

# Set the random seed for reproducibility
random.seed(123)  # Adjust the seed as needed


def move(state):
    [i, j, grid] = state
    n = len(grid)
    for pos in move_blank(i, j, n):
        i1, j1 = pos
        new_grid = copy.deepcopy(grid)
        new_grid[i][j], new_grid[i1][j1] = new_grid[i1][j1], new_grid[i][j]
        yield [i1, j1, new_grid]


def move_blank(i, j, n):
    if i + 1 < n:
        yield (i + 1, j)
    if i - 1 >= 0:
        yield (i - 1, j)
    if j + 1 < n:
        yield (i, j + 1)
    if j - 1 >= 0:
        yield (i, j - 1)


def generate_random_start_state(template, n):
    start_states = []
    for _ in range(n):
        shuffled = template[:]
        random.shuffle(shuffled)
        state = [shuffled.index(0) // 3, shuffled.index(0) % 3, [shuffled[i:i + 3] for i in range(0, 9, 3)]]
        start_states.append(state)
    return start_states


def solve_puzzle(start_state, goal_state):
    max_depth = 30

    def dfs(node, depth, nodes_opened):
        if depth == 0:
            return None, nodes_opened
        if node[2] == goal_state[2]:
            return [node], nodes_opened
        for next_state in move(node):
            nodes_opened += 1
            result, nodes_opened = dfs(next_state, depth - 1, nodes_opened)
            if result is not None:
                return [node] + result, nodes_opened
        return None, nodes_opened

    for depth in itertools.count(start=1):
        nodes_opened = 0
        start_time = time.time()
        result, nodes_opened = dfs(start_state, depth, nodes_opened)
        end_time = time.time()
        if result or depth == max_depth:
            solution_found = 1 if result else 0
            number_of_moves = len(result) - 1 if result else 0
            computing_time = end_time - start_time
            return start_state, solution_found, number_of_moves, nodes_opened, computing_time


def main():
    template = [8, 7, 6, 5, 4, 3, 2, 1, 0]
    goal_state = [1, 1, [[1, 2, 3], [8, 0, 4], [7, 6, 5]]]
    start_states = generate_random_start_state(template, 10)

    with open('IDDFS_output.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(
            ['Case number', 'Case start state', 'Solution found', 'Number of moves', 'Number of nodes opened',
             'Computing time'])

        for i, start_state in enumerate(start_states, start=1):
            _, solution_found, number_of_moves, nodes_opened, computing_time = solve_puzzle(start_state, goal_state)
            writer.writerow([i, str(start_state[2]), solution_found, number_of_moves, nodes_opened, computing_time])


if __name__ == "__main__":
    main()
