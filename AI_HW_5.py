import random
import math
import time
import psutil
import os
import sys
from queue import PriorityQueue

class Board:
    def __init__(self, tiles):
        self.size = int(math.sqrt(len(tiles)))  # defining length/width of the board
        self.tiles = tiles

    def execute_action(self, action):
        new_tiles = self.tiles[:]
        empty_index = new_tiles.index('0')
        if action == 'L':
            if empty_index % self.size > 0:
                new_tiles[empty_index - 1], new_tiles[empty_index] = new_tiles[empty_index], new_tiles[empty_index - 1]
        if action == 'R':
            if empty_index % self.size < (self.size - 1):
                new_tiles[empty_index + 1], new_tiles[empty_index] = new_tiles[empty_index], new_tiles[empty_index + 1]
        if action == 'U':
            if empty_index - self.size >= 0:
                new_tiles[empty_index - self.size], new_tiles[empty_index] = new_tiles[empty_index], new_tiles[empty_index - self.size]
        if action == 'D':
            if empty_index + self.size < self.size * self.size:
                new_tiles[empty_index + self.size], new_tiles[empty_index] = new_tiles[empty_index], new_tiles[empty_index + self.size]
        return Board(new_tiles)

class Node:
    def __init__(self, state, parent, action, cost=0, heuristic=0):
        self.state = state
        self.parent = parent
        self.action = action
        self.cost = cost  # g(n): cost to reach the current node
        self.heuristic = heuristic  # h(n): heuristic estimate to goal
        self.total_cost = self.cost + self.heuristic  # f(n) = g(n) + h(n)

    def __repr__(self):
        return str(self.state.tiles)

    def __eq__(self, other):
        return self.state.tiles == other.state.tiles

    def __hash__(self):
        return hash(tuple(self.state.tiles))

    def __lt__(self, other):
        """ Ensures that the priority queue uses the total cost f(n) to compare nodes """
        return self.total_cost < other.total_cost

def generate_puzzle(size):
    numbers = list(range(size * size))
    random.shuffle(numbers)
    return Node(Board(numbers), None, None)

def get_children(parent_node):
    children = []
    actions = ['L', 'R', 'U', 'D']  # left, right, up, down; actions define direction of movement of empty tile
    for action in actions:
        child_state = parent_node.state.execute_action(action)
        child_node = Node(child_state, parent_node, action, parent_node.cost + 1)
        children.append(child_node)
    return children

def find_path(node):
    path = []
    while node.parent is not None:
        path.append(node.action)
        node = node.parent
    path.reverse()
    return path

def misplaced_tiles(state):
    goal = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '0']
    return sum(1 for i in range(len(state.tiles)) if state.tiles[i] != goal[i] and state.tiles[i] != '0')

def manhattan_distance(state):
    goal_positions = {str(i): ((i - 1) // state.size, (i - 1) % state.size) for i in range(1, state.size * state.size)}
    goal_positions['0'] = (state.size - 1, state.size - 1)
    total_distance = 0
    for index, tile in enumerate(state.tiles):
        if tile != '0':
            goal_row, goal_col = goal_positions[tile]
            current_row, current_col = index // state.size, index % state.size
            total_distance += abs(current_row - goal_row) + abs(current_col - goal_col)
    return total_distance

def combined_heuristic(state, w1=1, w2=1):
    """
    Combined heuristic that takes both Manhattan distance and misplaced tiles into account.
    The weights w1 and w2 determine the contribution of each heuristic.
    """
    return w1 * manhattan_distance(state) + w2 * misplaced_tiles(state)

def a_star(root_node, heuristic_func):
    start_time = time.time()
    frontier = PriorityQueue()
    frontier.put((root_node.total_cost, root_node))
    explored = set()
    expanded = 0
    max_memory = 0

    while not frontier.empty():
        max_memory = max(max_memory, sys.getsizeof(frontier))
        current_cost, cur_node = frontier.get()
        expanded += 1

        if goal_test(cur_node.state.tiles):
            path = find_path(cur_node)
            end_time = time.time()
            return path, expanded, (end_time - start_time), max_memory

        explored.add(cur_node)

        for child in get_children(cur_node):
            if child in explored:
                continue
            child.heuristic = heuristic_func(child.state)
            child.total_cost = child.cost + child.heuristic
            frontier.put((child.total_cost, child))

    return False

def goal_test(cur_tiles):
    return cur_tiles == ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '0']

def main():
    initial = str(input("Initial configuration: "))
    initial_list = initial.split(" ")
    root = Node(Board(initial_list), None, None, cost=0, heuristic=0)

    # Use the combined heuristic (Manhattan + Misplaced Tiles)
    res = a_star(root, combined_heuristic)

    if res is not False:
        path, expanded_nodes, time_taken, memory_consumed = res
        print("Moves: " + " ".join(path))
        print("Number of expanded nodes: " + str(expanded_nodes))
        print("Time taken: " + str(time_taken))
        print("Max memory (Bytes): " + str(memory_consumed))
    else:
        print("No solution found")

if __name__ == "__main__":
    main()
