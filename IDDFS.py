import random
import time
import csv


class PuzzleSolver:
    def __init__(self, n=3, seed=111):
        self.n = n  # Puzzle dimension
        random.seed(seed)

    def generate_random_states(self, num_states=10):
        template_state = list(range(8, -1, -1))
        random.seed(111)
        start_states = []
        for i in range(num_states):
            shuffled_state = template_state[:]
            random.shuffle(shuffled_state)
            grid = [shuffled_state[i:i + 3] for i in range(0, 9, 3)]
            blank_pos = next((r, c) for r, row in enumerate(grid) for c, val in enumerate(row) if val == 0)
            start_states.append([*blank_pos, grid])
        return start_states




    def state_to_matrix(self, state):
        matrix = tuple(state[i:i + self.n] for i in range(0, self.n ** 2, self.n))
        zero_position = next((i, row.index(0)) for i, row in enumerate(matrix) if 0 in row)
        return zero_position + (matrix,)

    def generate_start_states(self, template_state, count=10):
        start_states = []
        for _ in range(count):
            shuffled_list = random.sample([item for sublist in template_state[2] for item in sublist], self.n ** 2)
            shuffled_matrix = tuple(tuple(shuffled_list[i:i + self.n]) for i in range(0, self.n ** 2, self.n))
            blank_position = shuffled_list.index(0)
            blank_x, blank_y = divmod(blank_position, self.n)
            start_states.append((blank_x, blank_y, shuffled_matrix))
        return start_states

    @staticmethod
    def get_children(node):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Up, Down, Left, Right
        children = []
        x, y, matrix = node.state
        n = len(matrix)
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < n and 0 <= ny < n:
                swapped_matrix = [list(row) for row in matrix]
                swapped_matrix[x][y], swapped_matrix[nx][ny] = swapped_matrix[nx][ny], swapped_matrix[x][y]
                children.append(Node((nx, ny, tuple(map(tuple, swapped_matrix))), node, (dx, dy), node.depth + 1))
        return children

    def iddfs(self, root, goal, max_depth):
        for depth in range(max_depth + 1):
            visited = set()
            result, nodes_opened = self.dls(root, goal, depth, visited, 0)
            if result is not None:
                return result, nodes_opened
        return None, nodes_opened

    def dls(self, node, goal, depth, visited, nodes_opened):
        if node.depth > depth:
            return None, nodes_opened
        nodes_opened += 1
        visited.add((node.state[0], node.state[1], tuple(map(tuple, node.state[2]))))

        if node.state == goal:
            return node, nodes_opened
        for child in self.get_children(node):
            if child.state not in visited:
                result, nodes_opened = self.dls(child, goal, depth, visited, nodes_opened)
                if result is not None:
                    return result, nodes_opened
        return None, nodes_opened

    def solve_puzzle(self, start_state, goal_state, max_depth=30):
        root = Node(start_state)
        start_time = time.time()
        solution, nodes_opened = self.iddfs(root, goal_state, max_depth)
        end_time = time.time()
        moves = solution.depth if solution else 0
        found_solution = 1 if solution else 0
        computing_time = end_time - start_time
        return start_state, found_solution, moves, nodes_opened, computing_time

    @staticmethod
    def save_results_to_csv(results, filename="IDDFS_output.csv"):
        headers = ["Case_Id", "Start_State", "Solution_Found", "Num_Moves", "Num_Nodes_Opened", "Computing_Time"]
        with open(filename, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(headers)
            for case_num, data in enumerate(results, 1):
                writer.writerow([case_num] + list(data))


class Node:
    def __init__(self, state, parent=None, action=None, depth=0):
        self.state = state
        self.parent = parent
        self.action = action
        self.depth = depth

    def __eq__(self, other):
        return self.state == other.state

    def __hash__(self):
        return hash(self.state)


# Usage example
solver = PuzzleSolver()
goal_state = (1, 1, ((1, 2, 3), (8, 0, 4), (7, 6, 5)))
#template_state = solver.generate_solvable_state()
start_states = solver.generate_random_states()
results = [solver.solve_puzzle(start_state, goal_state) for start_state in start_states]
solver.save_results_to_csv(results)
