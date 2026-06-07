import networkx as nx

class TPG:
    def __init__(self, graph: nx.Graph, initial_B_nodes: list, q: float):
        """
        Inputs:
        - graph: A NetworkX Graph instance representing the network topology.
        - initial_B_nodes: A list of nodes that start in state 'B'. All others start as 'A'.
        - q: The payout parameter (0 <= q <= 1).
        """
        self.G = graph.copy()
        self.q = q
        self.p = 1 - q
        
        # Initialize all nodes to 'A' first, then flip specified ones to 'B'
        for node in self.G.nodes:
            self.G.nodes[node]['state'] = 'A'
        for node in initial_B_nodes:
            if node in self.G.nodes:
                self.G.nodes[node]['state'] = 'B'

    def get_highest_degree_node(self):
        """Returns the node with the highest degree and its degree value."""
        if not self.G.nodes: return None, 0
        node = max(self.G.nodes, key=self.G.degree)
        return node, self.G.degree(node)

    def get_lowest_degree_node(self):
        """Returns the node with the lowest degree and its degree value."""
        if not self.G.nodes: return None, 0
        node = min(self.G.nodes, key=self.G.degree)
        return node, self.G.degree(node)

    def get_system_snapshot(self):
        """Returns an immutable representation of all node states to check for equilibrium."""
        return tuple(sorted((node, data['state']) for node, data in self.G.nodes(data=True)))

    def play_turn(self):
        """Executes one simultaneous turn where every node picks its next state."""
        next_states = {}
        
        for node in self.G.nodes:
            neighbors = list(self.G.neighbors(node))
            total_neighbors = len(neighbors)
            
            # Isolated nodes (degree 0) have no neighbors to get payouts from.
            # We can default them to remain in their current state.
            if total_neighbors == 0:
                next_states[node] = self.G.nodes[node]['state']
                continue
                
            # Count current neighbors in state A
            n_A = sum(1 for neighbor in neighbors if self.G.nodes[neighbor]['state'] == 'A')
            
            # Use our derived mathematical rule: fraction of A neighbors >= 1 - q
            fraction_A = n_A / total_neighbors
            
            if fraction_A > self.p:
                next_states[node] = 'A'
            else:
                next_states[node] = 'B'
                
        # Simultaneously apply the new states to the backend graph
        for node, new_state in next_states.items():
            self.G.nodes[node]['state'] = new_state

    def run_to_equilibrium(self, max_turns=100):
        """Runs the simulation until a 1-period or 2-period equilibrium is detected.
        Displays Turn 0 explicitly.
        """
        initial_snapshot = self.get_system_snapshot()
        history = [initial_snapshot]
        
        # Count total A's and B's in the initial snapshot
        initial_states = [state for node, state in initial_snapshot]
        init_A_count = initial_states.count('A')
        init_B_count = initial_states.count('B')
        
        # System Info Header
        max_node, max_deg = self.get_highest_degree_node()
        min_node, min_deg = self.get_lowest_degree_node()
        print(f"System Info: Max Degree Node is {max_node} ({max_deg}), Min Degree Node is {min_node} ({min_deg})")
        print("-" * 50)
        
        # Explicitly display Turn 0
        print(f"Turn 0: A={init_A_count}, B={init_B_count}")

        for turn in range(1, max_turns + 1):
            self.play_turn()
            current_snapshot = self.get_system_snapshot()
            
            # Count total A's and B's for logging current turn
            states = [data['state'] for _, data in self.G.nodes(data=True)]
            print(f"Turn {turn}: A={states.count('A')}, B={states.count('B')}")
            
            # 1-Period Equilibrium check
            if current_snapshot == history[-1]:
                print(f"Static Fixed Point Equilibrium reached at turn {turn-1}!")
                return 1
                
            # 2-Period Equilibrium check
            if len(history) >= 2 and current_snapshot == history[-2]:
                print(f"2-Period Oscillating Equilibrium (Limit Cycle) detected at turn {turn-2}!")
                return 2
                
            history.append(current_snapshot)
            
        print("Reached max turns without converging to a 1 or 2 period state.")
        return 3

G = nx.Graph()

# Add a bunch of raw nodes without mentioning states
G.add_nodes_from([1,2,3,4,5,6])
G.add_edges_from([(1,4), (1,6), (2,4), (2,5), (3,4), (3,5), (5,6)])

# Pick which ones should be 'B'
initial_B = [4,5,6]

# Assign states automatically based on your list
for node in G.nodes:
    G.nodes[node]['state'] = 'B' if node in initial_B else 'A'

test = TPG(G, initial_B, 0.5)
test.run_to_equilibrium()