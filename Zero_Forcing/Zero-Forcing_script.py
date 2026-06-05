from collections import Counter
import networkx as nx

class ZeroForcing:

    def __init__(self, graph: nx.Graph, initial_set: set):
        self.G = graph.copy()
        self.initial_set = initial_set

        # Set initial states
        for node in self.G.nodes:
            self.G.nodes[node]['state'] = 'black' if node in self.initial_set else 'white'
    
    def apply_zero_forcing_rule(self) -> bool:
        """Applies the zero forcing rule. Returns True if changes occurred."""
        new_states = {}
        for node in self.G.nodes:
            if self.G.nodes[node]['state'] == 'black':
                white_neighbors = [n for n in self.G.neighbors(node) if self.G.nodes[n]['state'] == 'white']
                if len(white_neighbors) == 1:
                    new_states[white_neighbors[0]] = 'black'
        
        if not new_states:
            return False
            
        for node, state in new_states.items():
            self.G.nodes[node]['state'] = state
        return True

    def get_current_counts(self):
        """Helper to count current black and white nodes."""
        states = [data['state'] for _, data in self.G.nodes(data=True)]
        counts = Counter(states)
        return counts.get('black', 0), counts.get('white', 0)

    def run_to_final_state(self):
        """
        Runs the zero forcing process to equilibrium.
        Automatically prints live step updates, final tallies, 
        and lists the final black nodes.
        """
        print("--- Starting Zero Forcing Simulation ---")
        
        step = 0
        black_cnt, white_cnt = self.get_current_counts()
        print(f"Step {step} (Initial): {black_cnt} Black nodes, {white_cnt} White nodes")
        
        # Run until equilibrium (stuck)
        while True:
            step += 1
            changed = self.apply_zero_forcing_rule()
            black_cnt, white_cnt = self.get_current_counts()
            
            if not changed:
                print(f"\n[Stuck] No new black nodes introduced at Step {step}.")
                break
                
            print(f"Step {step}: {black_cnt} Black nodes, {white_cnt} White nodes")

        # Gather final black node identifiers
        final_black_nodes = [node for node, data in self.G.nodes(data=True) if data['state'] == 'black']
        
        # Automatically print the final breakdown
        print("\n--- Final Summary ---")
        print(f"Total Black Nodes: {len(final_black_nodes)}")
        print(f"Total White Nodes: {white_cnt}")
        print(f"List of final Black nodes: {sorted(final_black_nodes)}")
        print("-" * 36)
        
        return final_black_nodes
    
G = None
G = nx.Graph()

# Add nodes
G.add_nodes_from(range(100))
for i in range(99):
    G.add_edge(i, i+1)

# Pick which ones should be 'black'
initial_B = set([49,50])

test = ZeroForcing(G, initial_B)
test.run_to_final_state()