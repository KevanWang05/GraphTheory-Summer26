"""
tpg_cluster.py
===================
Optimized for cluster environments. Writes results directly to files.
"""

import sys
import os
from fractions import Fraction
import networkx as nx

# ────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ────────────────────────────────────────────────────────────────────────
N = 50           
K = 16           
Q = "0.501"      
MAX_GRAPHS = 100_000

INITIAL_B_SETS = [list(range(i, i + 24)) for i in range(27)]

def run_tpg(G: nx.Graph, initial_b: list, q_frac: Fraction, max_turns: int = 10_000) -> str:
    p = Fraction(1) - q_frac
    state = {node: 'B' if node in initial_b else 'A' for node in G.nodes}
    prev_prev_snapshot = None
    prev_snapshot      = tuple(sorted(state.items()))

    for _ in range(max_turns):
        next_state = {}
        for node in G.nodes:
            neighbors = list(G.neighbors(node))
            total = len(neighbors)
            if total == 0:
                next_state[node] = state[node]
                continue
            n_A = sum(1 for nb in neighbors if state[nb] == 'A')
            next_state[node] = 'A' if Fraction(n_A, total) > p else 'B'
        state = next_state

        snapshot = tuple(sorted(state.items()))
        if snapshot == prev_snapshot or snapshot == prev_prev_snapshot:
            break  
        prev_prev_snapshot = prev_snapshot
        prev_snapshot      = snapshot

    b_count = sum(1 for s in state.values() if s == 'B')
    if b_count == len(G.nodes):
        return 'all_B'
    return 'mixed_or_A'

def main():
    q_frac = Fraction(Q).limit_denominator(10**12)
    
    print(f"Starting TPG Random Search (N={N}, K={K}, Q={Q})...")

    for graph_idx in range(1, MAX_GRAPHS + 1):
        try:
            G = nx.random_graphs.random_regular_graph(d=K, n=N)
        except Exception:
            continue

        for initial_b in INITIAL_B_SETS:
            result = run_tpg(G, initial_b, q_frac)

            if result == 'all_B':
                # SUCCESS: Write data out and die immediately
                output_filename = "tpg_success_output.txt"
                with open(output_filename, "w") as f:
                    f.write(f"Match found on random graph index: {graph_idx}\n")
                    f.write(f"Initial B-State Set:\n{initial_b}\n\n")
                    f.write("Edges:\n")
                    for edge in sorted(G.edges):
                        f.write(f"{edge[0]} {edge[1]}\n")
                
                print(f"Success! Output written to {output_filename}")
                sys.exit(0) 

    # EXHAUSTED: Create a file named 'true' if no graph matched
    with open("true", "w") as f:
        f.write("true\n")
    print("Completed 100,000 evaluations. No matching graph found. 'true' file generated.")
    sys.exit(0)

if __name__ == "__main__":
    main()