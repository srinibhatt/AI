import random
import time
import csv

# Define Student Registration number 100443924. So, last 3 digits for Seed set is 924
random.seed(111)

class Node:
    def __init__(self, state, parent=None, action=None, depth=0):
        self.state = state  # State is a tuple (x, y, matrix)
        self.parent = parent
        self.action = action
        self.depth = depth

    def __eq__(self, other):
        return self.state == other.state

    def __hash__(self):
        return hash(self.state)

def template_state_generator():
    while True:
        state = tuple(random.sample(range(9), 9))
        if is_solvable(state):
            matrix = tuple(state[i:i+3] for i in range(0, 9, 3))
            zero_position = next((i, row.index(0)) for i, row in enumerate(matrix) if 0 in row)
            return zero_position + (matrix,)

def is_solvable(state):
    inversions = sum(1 for i in range(len(state)) for j in range(i+1, len(state)) if state[j] and state[i] and state[i] > state[j])
    return inversions % 2 == 0

def generate_start_states(template_state, n=10):
    start_states = []
    for _ in range(n):
        shuffled_list = random.sample([item for sublist in template_state[2] for item in sublist], 9)
        shuffled_matrix = tuple(tuple(shuffled_list[i:i + 3]) for i in range(0, 9, 3))
        blank_position = shuffled_list.index(0)
        blank_x, blank_y = divmod(blank_position, 3)
        start_states.append((blank_x, blank_y, shuffled_matrix))
    return start_states

def get_children(node):
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Up, Down, Left, Right
    children = []
    x, y, matrix = node.state
    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if 0 <= nx < 3 and 0 <= ny < 3:
            swapped_matrix = list(map(list, matrix))
            swapped_matrix[x][y], swapped_matrix[nx][ny] = swapped_matrix[nx][ny], swapped_matrix[x][y]
            children.append(Node((nx, ny, tuple(map(tuple, swapped_matrix))), node, (dx, dy), node.depth + 1))
    return children

def iddfs(root, goal, max_depth):
    for depth in range(max_depth + 1):
        visited = set()
        result, nodes_opened = dls(root, goal, depth, visited, 0)
        if result is not None:
            return result, nodes_opened
    return None, nodes_opened

def dls(node, goal, depth, visited, nodes_opened):
    if node.depth > depth:
        return None, nodes_opened
    nodes_opened += 1
    visited.add(node.state)
    if node.state == goal:
        return node, nodes_opened
    for child in get_children(node):
        if child.state not in visited:
            result, nodes_opened = dls(child, goal, depth, visited, nodes_opened)
            if result is not None:
                return result, nodes_opened
    return None, nodes_opened

def solve_puzzle(start_state, goal_state):
    root = Node(start_state)
    max_depth = 30
    start_time = time.time()
    solution, nodes_opened = iddfs(root, goal_state, max_depth)
    end_time = time.time()

    if solution:
        moves = solution.depth
        found_solution = True
    else:
        moves = 0
        found_solution = False

    computing_time = end_time - start_time
    return (start_state, found_solution, moves, nodes_opened, computing_time)

def save_results_to_csv(results, filename="IDDFS_output_refactored.csv"):
    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Case_Id", "Start_State", "Solution_Found", "Num_Moves", "Num_Nodes_Opened", "Computing_Time"])
        for case_num, (start_state, solution_found, num_moves, num_nodes_opened, computing_time) in enumerate(results, 1):
            writer.writerow([case_num, str(start_state), int(solution_found), num_moves, num_nodes_opened, computing_time])

goal_state = (1, 1, ((1, 2, 3), (8, 0, 4), (7, 6, 5)))
template_state = template_state_generator()
start_states = generate_start_states(template_state, n=10)
results = [solve_puzzle(start_state, goal_state) for start_state in start_states]
save_results_to_csv(results)
