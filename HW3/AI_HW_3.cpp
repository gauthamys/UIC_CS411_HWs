#include<iostream>
#include<queue>
#include<unordered_set>
#include<sstream>
#include<chrono>
#include <sys/resource.h>
#include <unistd.h>
#include<functional>

using namespace std;
using namespace std::chrono;

struct Vector2DHash {
    std::size_t operator()(const std::vector<std::vector<int>>& vec) const {
        std::size_t hash = 0;
        std::hash<int> hasher;

        for (const auto& row : vec) {
            std::size_t rowHash = 0;
            for (const auto& element : row) {
                rowHash ^= hasher(element) + 0x9e3779b9 + (rowHash << 6) + (rowHash >> 2);
            }
            hash ^= rowHash + 0x9e3779b9 + (hash << 6) + (hash >> 2); // Combine row hashes
        }

        return hash;
    }
};

struct Vector2DEqual {
    bool operator()(const std::vector<std::vector<int>>& lhs, const std::vector<std::vector<int>>& rhs) const {
        return lhs == rhs; // Use the built-in equality operator for vectors
    }
};

// GOAL state
const vector<vector<int>> GOAL = {
        {1, 2, 3, 4},
        {5, 6, 7, 8},
        {9, 10, 11, 12},
        {13, 14, 15, 0}
    };

class Node {
    // Node structure defined to represent a single state in the state space
    // moves:   the sequence of moves performed to reach this state from the start state
    // board:   state of the board at this state
    public:
        vector<vector<int>> board;
        string moves;
        Node(vector<vector<int>> _board, string _moves) {
            this->board = _board;
            this->moves = _moves;
        }
};

pair<int, int> getZeroPos(vector<vector<int>> board) {
    // Get the index of the 0 (empty) element on the board
    for(int i=0; i<4; i++) {
        for(int j=0; j<4; j++) {
            if(board[i][j] == 0) return {i, j};
        }
    }
    return {0, 0};
}

vector<vector<int>> readBoard() {
    // function to form the start board from stdin
    vector<vector<int>> board(4, vector<int>(4));
    string line;
    getline(cin, line);
    istringstream iss(line);
    for (int i = 0; i < 4; ++i) {
        for (int j = 0; j < 4; ++j) {
            if (!(iss >> board[i][j])) {
                cerr << "Invalid input. Please enter 16 integers." << endl;
            }
        }
    }
    return board;
}

vector<Node*> createMoves(Node* node) {
    // function to return a vector of next possible states from the given state "node"
    // 1.   get the index of zero element i, j
    // 2.   based on i, j move either up, down, left or right
    // 3.   for each move possible, swap the move index with the zero index and track the move
    // 4.   for every move, create a new node with the new board formed after the move and the move used
    pair<int, int> zeroPos = getZeroPos(node->board);
    int i = zeroPos.first, j = zeroPos.second;
    
    vector<pair<int, int>> blankIndices;    // indices to track new position of empty element
    string moves;                           // moves corresponding to each move in blankIndices
    vector<Node*> res;

    if(i + 1 < 4){                          // DOWN
        blankIndices.push_back({i + 1, j});
        moves += "D";
    }
    if(j + 1 < 4){                          // RIGHT
        blankIndices.push_back({i, j + 1});
        moves += "R";
    }
    if(j - 1 >= 0){                         // LEFT
        blankIndices.push_back({i, j - 1});
        moves += "L";
    } 
    if(i - 1 >= 0){                         // UP
        blankIndices.push_back({i - 1, j});
        moves += "U";
    }

    for(int k = 0; k < blankIndices.size(); k++) { // for each move in blankIndices, create a new node with the move in moves and append to list and return
        Node* newNode = new Node(node->board, node->moves);
        pair<int, int> index = {blankIndices[k].first, blankIndices[k].second};
        swap(newNode->board[i][j], newNode->board[index.first][index.second]);
        newNode->moves += moves[k];
        res.push_back(newNode);
    }
    return res;
}

Node search(vector<vector<int>> board){
    // BFS Algorithm to perform search in state space of the 16 square game
    queue<Node*> q; // queue
    unordered_set<vector<vector<int>>, Vector2DHash, Vector2DEqual> visited; // hashset to keep track of visited nodes
    Node* startNode = new Node(board, "");
    int expanded = 0;

    q.push(startNode);
    visited.insert(startNode->board);

    while(!q.empty() && visited.size() < tgamma(17)) { // number of states possible is 16 factorial and tgamma(i) calculates (i-1) factorial
        Node* curNode = q.front();
        q.pop();

        if(curNode->board == GOAL) {
            cout << "Number of Nodes expanded: " << expanded << endl;
            return *curNode;
        }

        vector<Node*> nextNodes = createMoves(curNode); // traverse the children of the node
        expanded++;

        for(Node* node: nextNodes) {
            if(visited.find(node->board) == visited.end()){ // if node is not in visited, insert it to the visited set
                q.push(node);
                visited.insert(node->board);
            }
        }
    }

    // goal unreachable
    vector<vector<int>> emptyBoard;
    return Node(emptyBoard, "GOAL state unreachable");
}

int main() {
    vector<vector<int>> board = readBoard();
    struct rusage usage;
    
    auto start = high_resolution_clock::now();
    Node res = search(board);
    auto end = high_resolution_clock::now();
    
    getrusage(RUSAGE_SELF, &usage);
    duration<double> duration = end - start;

    cout << "Moves: " << res.moves << endl;
    cout << "Time Taken: " << duration.count() << endl;
    cout << "Memory Used: " << usage.ru_maxrss << endl;

    return 0;
}
