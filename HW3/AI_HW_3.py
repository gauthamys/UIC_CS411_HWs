"""BFS Search over 16 board game state space"""
import math

class Node:
    # Structure to define a single state in the state space graph
    def __init__(self, _board, _moves):
        self.board = _board
        self.moves = _moves

def readBoard():
    # read board from stdin
    boardStr = input().split()
    flatBoard = [int(x) for x in boardStr]
    board = [flatBoard[i:i+4] for i in range(0, len(flatBoard), 4)]
    print(board)

def getZeroPos(board):
    # get poisiton of empty tile (zero) on the board
    for i in range(4):
        for j in range(4):
            if board[i][j] == 0:
                return (i, j)

def up(posI, posJ, node):
    # perform the move "up" on the board and return the new board with the move
    upNode = Node(node.board, node.moves)
    upNode.moves += "U"
    pass

def down(posI, posJ, node):
    # perform the move "down" on the board and return the new board with the move
    pass

def left(posI, posJ, node):
    # perform the move "left" on the board and return the new board with the move
    pass

def right(posI, posJ, node):
    # perform the move "right" on the board and return the new board with the move
    pass

def createMoves(node):
    # return list of Nodes with appropriate move updates based on position of zero
    posI, posJ = getZeroPos(node.board)
    res = []
    pass

def search(board):
    GOAL = [
        [1, 2, 3, 4],
        [5, 6, 7, 8],
        [9, 10, 11, 12],
        [13, 14, 15, 0]
    ]

    startNode = Node(board, "")
    visited = set()
    q = []

    q.append(startNode)
    visited.add(startNode.board)

    nodes_expanded = 0
    
    while(len(q) != 0 and len(q) <= math.factorial(16)):
        curNode = q.pop(0)

        if curNode.board == GOAL:
            return curNode
        
        nextNodes = createMoves(curNode)
        nodes_expanded += 1

        for node in nextNodes:
            if node.board not in visited:
                q.append(node)
                visited.add(node.board)

if __name__ == "__main__":
    board = readBoard()
    res = search(board)

