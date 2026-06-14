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
G.add_nodes_from(range(50))
G.add_edges_from([(0,3),(0,4),(0,5),(0,11),(0,17),(0,19),(0,20),(0,26),(0,28),(0,29),(0,30),(0,31),(0,32),(0,38),(0,47),(0,48)])
G.add_edges_from([(1,4),(1,6),(1,7),(1,8),(1,11),(1,16),(1,18),(1,20),(1,29),(1,35),(1,36),(1,37),(1,38),(1,42),(1,43),(1,48)])
G.add_edges_from([(2,3),(2,5),(2,6),(2,8),(2,12),(2,17),(2,22),(2,25),(2,31),(2,33),(2,34),(2,36),(2,40),(2,41),(2,42),(2,46)])
G.add_edges_from([(3,5),(3,8),(3,9),(3,13),(3,16),(3,19),(3,29),(3,30),(3,31),(3,32),(3,33),(3,34),(3,36),(3,48)])
G.add_edges_from([(4,7),(4,8),(4,11),(4,14),(4,17),(4,18),(4,21),(4,24),(4,27),(4,29),(4,30),(4,37),(4,41),(4,43)])
G.add_edges_from([(5,6),(5,11),(5,17),(5,23),(5,24),(5,27),(5,32),(5,37),(5,39),(5,40),(5,44),(5,45),(5,47)])
G.add_edges_from([(6,7),(6,11),(6,15),(6,24),(6,26),(6,27),(6,36),(6,37),(6,38),(6,40),(6,41),(6,46),(6,48)])
G.add_edges_from([(7,8),(7,10),(7,12),(7,15),(7,21),(7,28),(7,29),(7,37),(7,39),(7,40),(7,42),(7,47),(7,48)])
G.add_edges_from([(8,9),(8,18),(8,19),(8,23),(8,24),(8,31),(8,32),(8,40),(8,41),(8,47),(8,49)])
G.add_edges_from([(9,10),(9,11),(9,14),(9,19),(9,21),(9,23),(9,26),(9,27),(9,29),(9,30),(9,33),(9,38),(9,42),(9,44)])
G.add_edges_from([(10,15),(10,19),(10,20),(10,24),(10,25),(10,27),(10,28),(10,31),(10,34),(10,38),(10,41),(10,46),(10,47),(10,49)])
G.add_edges_from([(11,19),(11,22),(11,23),(11,25),(11,28),(11,39),(11,40),(11,42),(11,47),(11,49)])
G.add_edges_from([(12,14),(12,16),(12,17),(12,21),(12,22),(12,25),(12,30),(12,32),(12,33),(12,40),(12,41),(12,43),(12,45),(12,46)])
G.add_edges_from([(13,14),(13,18),(13,27),(13,29),(13,30),(13,31),(13,35),(13,36),(13,37),(13,40),(13,41),(13,42),(13,44),(13,46),(13,48)])
G.add_edges_from([(14,16),(14,21),(14,26),(14,27),(14,29),(14,31),(14,35),(14,38),(14,43),(14,46),(14,47),(14,49)])
G.add_edges_from([(15,17),(15,21),(15,22),(15,23),(15,24),(15,25),(15,28),(15,31),(15,34),(15,41),(15,44),(15,47),(15,49)])
G.add_edges_from([(16,20),(16,22),(16,24),(16,25),(16,28),(16,30),(16,32),(16,33),(16,35),(16,44),(16,45),(16,47)])
G.add_edges_from([(17,18),(17,20),(17,23),(17,28),(17,37),(17,39),(17,41),(17,43),(17,46),(17,49)])
G.add_edges_from([(18,20),(18,22),(18,24),(18,25),(18,26),(18,30),(18,32),(18,36),(18,39),(18,48),(18,49)])
G.add_edges_from([(19,23),(19,26),(19,34),(19,35),(19,38),(19,40),(19,42),(19,45),(19,46),(19,48)])
G.add_edges_from([(20,22),(20,24),(20,31),(20,32),(20,36),(20,37),(20,38),(20,43),(20,44),(20,45)])
G.add_edges_from([(21,22),(21,26),(21,30),(21,33),(21,35),(21,36),(21,37),(21,40),(21,43),(21,44)])
G.add_edges_from([(22,30),(22,32),(22,33),(22,35),(22,43),(22,45),(22,46),(22,47)])
G.add_edges_from([(23,29),(23,30),(23,32),(23,35),(23,36),(23,37),(23,38),(23,41),(23,49)])
G.add_edges_from([(24,27),(24,28),(24,31),(24,33),(24,34),(24,38),(24,49)])
G.add_edges_from([(25,26),(25,27),(25,29),(25,36),(25,41),(25,43),(25,45),(25,48),(25,49)])
G.add_edges_from([(26,30),(26,31),(26,33),(26,37),(26,45),(26,46),(26,47),(26,48)])
G.add_edges_from([(27,34),(27,35),(27,39),(27,42),(27,44),(27,45),(27,48)])
G.add_edges_from([(28,30),(28,34),(28,38),(28,39),(28,40),(28,42),(28,44),(28,47)])
G.add_edges_from([(29,35),(29,39),(29,42),(29,43),(29,46),(29,47)])
G.add_edges_from([(30,33),(30,42),(30,43)])
G.add_edges_from([(31,32),(31,33),(31,34),(31,37),(31,39)])
G.add_edges_from([(32,34),(32,36),(32,37),(32,42),(32,43)])
G.add_edges_from([(33,34),(33,44),(33,46),(33,48),(33,49)])
G.add_edges_from([(34,35),(34,39),(34,43),(34,44),(34,47)])
G.add_edges_from([(35,36),(35,39),(35,40),(35,44),(35,49)])
G.add_edges_from([(36,39),(36,45),(36,46),(36,47)])
G.add_edges_from([(37,39),(37,40),(37,45)])
G.add_edges_from([(38,40),(38,41),(38,42),(38,46),(38,49)])
G.add_edges_from([(39,41),(39,44),(39,45)])
G.add_edges_from([(40,42),(40,43)])
G.add_edges_from([(41,42),(41,45),(41,48)])
G.add_edges_from([(42,48)])
G.add_edges_from([(43,44),(43,49)])
G.add_edges_from([(44,45),(44,48)])
G.add_edges_from([(45,46),(45,49)])
G.add_edges_from([(46,49)])
G.add_edges_from([(47,48)])

# Pick which ones should be 'B'
initial_B = [14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37]

# Assign states automatically based on your list
for node in G.nodes:
    G.nodes[node]['state'] = 'B' if node in initial_B else 'A'

test = TPG(G, initial_B, 0.51)
test.run_to_equilibrium()