import random
import operator
import json

orientations = EAST, NORTH, WEST, SOUTH = [(1, 0), (0, 1), (-1, 0), (0, -1)]
turns = LEFT, RIGHT = (+1, -1)

def vector_add(a, b):
    return tuple(map(operator.add, a, b))

def turn_right(heading):
    return turn_heading(heading, RIGHT)

def turn_heading(heading, inc, headings=orientations):
    return headings[(headings.index(heading) + inc) % len(headings)]

def turn_left(heading):
    return turn_heading(heading, LEFT)

def isnumber(x):
    return hasattr(x, '__int__')

def print_table(table, header=None, sep='   ', numfmt='{}'):
    justs = ['rjust' if isnumber(x) else 'ljust' for x in table[0]]

    if header:
        table.insert(0, header)

    table = [[numfmt.format(x) if isnumber(x) else x for x in row]
             for row in table]

    sizes = list(map(lambda seq: max(map(len, seq)), list(zip(*[map(str, row) for row in table]))))

    for row in table:
        print(sep.join(getattr(str(x), j)(size) for (j, size, x) in zip(justs, sizes, row)))


class MDP:

    def __init__(self, init, actlist, terminals, transitions=None, reward=None, states=None, gamma=0.9):
        if not (0 < gamma <= 1):
            raise ValueError("An MDP must have 0 < gamma <= 1")

        # collect states from transitions table if not passed.
        self.states = states or self.get_states_from_transitions(transitions)

        self.init = init

        if isinstance(actlist, list):
            # if actlist is a list, all states have the same actions
            self.actlist = actlist

        elif isinstance(actlist, dict):
            # if actlist is a dict, different actions for each state
            self.actlist = actlist

        self.terminals = terminals
        self.transitions = transitions or {}
        if not self.transitions:
            print("Warning: Transition table is empty.")

        self.gamma = gamma

        self.reward = reward or {s: 0 for s in self.states}

        # self.check_consistency()

    def R(self, state):
        """Return a numeric reward for this state."""

        return self.reward[state]

    def T(self, state, action):
        """Transition model. From a state and an action, return a list
        of (probability, result-state) pairs."""

        if not self.transitions:
            raise ValueError("Transition model is missing")
        else:
            return self.transitions[state][action]

    def actions(self, state):
        if state in self.terminals:
            return [None]
        else:
            return self.actlist

    def get_states_from_transitions(self, transitions):
        if isinstance(transitions, dict):
            s1 = set(transitions.keys())
            s2 = set(tr[1] for actions in transitions.values()
                     for effects in actions.values()
                     for tr in effects)
            return s1.union(s2)
        else:
            print('Could not retrieve states from transitions')
            return None

    def check_consistency(self):

        # check that all states in transitions are valid
        assert set(self.states) == self.get_states_from_transitions(self.transitions)

        # check that init is a valid state
        assert self.init in self.states

        # check reward for each state
        assert set(self.reward.keys()) == set(self.states)

        # check that all terminals are valid states
        assert all(t in self.states for t in self.terminals)

        # check that probability distributions for all actions sum to 1
        for s1, actions in self.transitions.items():
            for a in actions.keys():
                s = 0
                for o in actions[a]:
                    s += o[0]
                assert abs(s - 1) < 0.001

class GridMDP(MDP):
    def __init__(self, grid, terminals, init=(0, 0), gamma=.9):
        grid.reverse()  # because we want row 0 on bottom, not on top
        reward = {}
        states = set()
        self.rows = len(grid)
        self.cols = len(grid[0])
        self.grid = grid
        for x in range(self.cols):
            for y in range(self.rows):
                if grid[y][x]:
                    states.add((x, y))
                    reward[(x, y)] = grid[y][x]
        self.states = states
        actlist = orientations
        transitions = {}
        for s in states:
            transitions[s] = {}
            for a in actlist:
                transitions[s][a] = self.calculate_T(s, a)
        MDP.__init__(self, init, actlist=actlist,
                     terminals=terminals, transitions=transitions,
                     reward=reward, states=states, gamma=gamma)

    def calculate_T(self, state, action):
        if action:
            return [(0.8, self.go(state, action)),
                    (0.1, self.go(state, turn_right(action))),
                    (0.1, self.go(state, turn_left(action)))]
        else:
            return [(0.0, state)]

    def T(self, state, action):
        return self.transitions[state][action] if action else [(0.0, state)]

    def go(self, state, direction):
        """Return the state that results from going in this direction."""

        state1 = vector_add(state, direction)
        return state1 if state1 in self.states else state

    def to_grid(self, mapping):
        """Convert a mapping from (x, y) to v into a [[..., v, ...]] grid."""

        return list(reversed([[mapping.get((x, y), None)
                               for x in range(self.cols)]
                              for y in range(self.rows)]))

    def to_dir(self, policy):
        chars = {(1, 0): 'R', (0, 1): 'U', (-1, 0): 'L', (0, -1): 'D', None: '.'}
        return self.to_grid({s: chars[a] for (s, a) in policy.items()})


def value_iteration(mdp, epsilon=0.001):
    """Solving an MDP by value iteration. [Figure 17.4]"""

    U1 = {s: 0 for s in mdp.states}  # Initialize U1 to zero for all states
    R, T, gamma = mdp.R, mdp.T, mdp.gamma

    iteration = 0  # To track the number of iterations

    while True:
        U = U1.copy()  # Copy U1 to U for updating in the next step
        delta = 0
        print(f"Iteration {iteration}:")  # Print iteration number

        for s in mdp.states:
            U1[s] = R(s) + gamma * max(
                sum(p * U[s1] for (p, s1) in T(s, a)) for a in mdp.actions(s)
            )
            delta = max(delta, abs(U1[s] - U[s]))

        # Format and print the utility values as a grid
        print("Utilities:")
        grid_values = mdp.to_grid(U1)
        for row in grid_values:
            print('   '.join(f"{v:.4f}" if v is not None else "None" for v in row))
        
        print("-" * 40)  # Separator for each iteration

        # Check convergence condition
        if delta <= epsilon * (1 - gamma) / gamma:
            return U1  # Return the final utility values

        iteration += 1  # Increment iteration count

def best_policy(mdp, U):
    """Given an MDP and a utility function U, determine the best policy,
    as a mapping from state to action. [Equation 17.4]"""

    pi = {}
    for s in mdp.states:
        pi[s] = max(mdp.actions(s), key=lambda a: expected_utility(a, s, U, mdp))
    return pi


def expected_utility(a, s, U, mdp):
    """The expected utility of doing a in state s, according to the MDP and U."""

    return sum(p * U[s1] for (p, s1) in mdp.T(s, a))

def policy_iteration(mdp):
    U = {s: 0 for s in mdp.states}
    pi = {s: random.choice(mdp.actions(s)) for s in mdp.states}
    while True:
        U = policy_evaluation(pi, U, mdp)
        unchanged = True
        for s in mdp.states:
            a = max(mdp.actions(s), key=lambda a: expected_utility(a, s, U, mdp))
            if a != pi[s]:
                pi[s] = a
                unchanged = False
        if unchanged:
            return pi


def policy_evaluation(pi, U, mdp, k=20):
    R, T, gamma = mdp.R, mdp.T, mdp.gamma
    for i in range(k):
        for s in mdp.states:
            U[s] = R(s) + gamma * sum(p * U[s1] for (p, s1) in T(s, pi[s]))
    return U

def load_gridmdp_from_file(filename):
    with open(filename, 'r') as file:
        data = json.load(file)

    # Extract grid, terminals, initial state, and gamma
    grid = data['grid']
    terminals = [tuple(terminal) for terminal in data['terminals']]
    init = tuple(data['initial_state'])
    gamma = data['gamma']

    # Reverse grid as the GridMDP class expects the rows to be in bottom-to-top order
    return GridMDP(grid=grid, terminals=terminals, init=init, gamma=gamma)


if __name__ == "__main__":
    # Load MDP from a JSON file
    sequential_decision_environment = load_gridmdp_from_file('gridmdp.json')

    # Apply value iteration
    pi = best_policy(sequential_decision_environment, value_iteration(sequential_decision_environment, .01))
    
    # Print the results
    print("Optimal Policy: ")
    print_table(sequential_decision_environment.to_dir(policy_iteration(sequential_decision_environment)))
