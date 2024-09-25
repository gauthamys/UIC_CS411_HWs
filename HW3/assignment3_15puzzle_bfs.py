#CS 411 - Assignment 3 Solution
#Breadth First Search on 15 Puzzle
#Sarit Adhikari
#2021 Fall

import random
import math
import time
import psutil
import os
from collections import deque
import sys

#This class defines the state of the problem in terms of board configuration
class Board:
	def __init__(self,tiles):
		self.size = int(math.sqrt(len(tiles))) # defining length/width of the board
		self.tiles = tiles
	
	#This function returns the resulting state from taking particular action from current state
	def execute_action(self,action):
		new_tiles = self.tiles[:]
		empty_index = new_tiles.index('0')
		if action=='L':	
			if empty_index%self.size>0:
				new_tiles[empty_index-1],new_tiles[empty_index] = new_tiles[empty_index],new_tiles[empty_index-1]
		if action=='R':
			if empty_index%self.size<(self.size-1): 	
				new_tiles[empty_index+1],new_tiles[empty_index] = new_tiles[empty_index],new_tiles[empty_index+1]
		if action=='U':
			if empty_index-self.size>=0:
				new_tiles[empty_index-self.size],new_tiles[empty_index] = new_tiles[empty_index],new_tiles[empty_index-self.size]
		if action=='D':
			if empty_index+self.size < self.size*self.size:
				new_tiles[empty_index+self.size],new_tiles[empty_index] = new_tiles[empty_index],new_tiles[empty_index+self.size]
		return Board(new_tiles)
		

#This class defines the node on the search tree, consisting of state, parent and previous action		
class Node:
	def __init__(self,state,parent,action):
		self.state = state
		self.parent = parent
		self.action = action
	
	#Returns string representation of the state	
	def __repr__(self):
		return str(self.state.tiles)
	
	#Comparing current node with other node. They are equal if states are equal	
	def __eq__(self,other):
		return self.state.tiles == other.state.tiles
		
	def __hash__(self):
		return hash(tuple(self.state.tiles))

#Utility function to randomly generate 15-puzzle		
def generate_puzzle(size):
	numbers = list(range(size*size))
	random.shuffle(numbers)
	return Node(Board(numbers),None,None)

#This function returns the list of children obtained after simulating the actions on current node
def get_children(parent_node):
	children = []
	actions = ['L','R','U','D'] # left,right, up , down ; actions define direction of movement of empty tile
	for action in actions:
		child_state = parent_node.state.execute_action(action)
		child_node = Node(child_state,parent_node,action)
		children.append(child_node)
	return children

#This function backtracks from current node to reach initial configuration. The list of actions would constitute a solution path
def find_path(node):	
	path = []	
	while(node.parent is not None):
		path.append(node.action)
		node = node.parent
	path.reverse()
	return path

#This function runs breadth first search from the given root node and returns path, number of nodes expanded and total time taken	
def run_bfs(root_node):
	start_time = time.time()
	frontier = deque([root_node])
	explored = set()
	max_memory = 0
	while(len(frontier)>0):
		max_memory = max(max_memory, sys.getsizeof(frontier)+sys.getsizeof(explored))
		cur_time =time.time()
		cur_node = frontier.popleft()
		explored.add(cur_node)
		if(goal_test(cur_node.state.tiles)):
			path = find_path(cur_node)
			end_time = time.time()
			
			
			return path,len(explored),(end_time-start_time), max_memory
		for child in get_children(cur_node):
			if child in explored:
				continue
			else:
				frontier.append(child)
	print("frontier empty")	
	return False

#Main function accepting input from console , runnung bfs and showing output	
def main():
	#process = psutil.Process(os.getpid())
	#initial_memory = process.memory_info().rss / 1024.0
	initial = str(input("initial configuration: "))
	initial_list = initial.split(" ")
	root = Node(Board(initial_list),None,None)
	
	path, expanded_nodes, time_taken, memory_consumed = run_bfs(root)
	print("Moves: " + " ".join(path))
	print("Number of expanded Nodes: "+ str(expanded_nodes))
	print("Time Taken: " + str(time_taken))
	print("Max Memory (Bytes): " +  str(memory_consumed))
	#final_memory = process.memory_info().rss / 1024.0
	#print(str(final_memory-initial_memory)+" KB")

#Utility function checking if current state is goal state or not
def goal_test(cur_tiles):
	return cur_tiles == ['1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','0']	
	
if __name__=="__main__":main()	