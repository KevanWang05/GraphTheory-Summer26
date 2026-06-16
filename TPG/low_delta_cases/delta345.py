"""
tpg_cluster.py
===================
Optimized for cluster environments. Writes results directly to files.
Modified to sample simple, connected graphs with maximum degree 3.
"""

import sys
import os
from fractions import Fraction
import networkx as nx
import random

# ────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ────────────────────────────────────────────────────────────────────────
N = 50              # Adjustable number of nodes
MAX_DEGREE = 3      # Maximum allowable degree for any node
Q = "0.501"         
MAX_GRAPHS = 100_000

# Dynamically generate initial B sets based on current N
# Enforces a rolling window of 24 nodes up to N
INITIAL_B_SETS = [list(range(i, i + 24)) for i in range(N - 23)] if N >= 24 else [list(range(N))]

def generate_max_deg_connected_graph(n: int, max_deg: int) -> nx.Graph:
    """
    Generates a simple, connected graph with a maximum degree of `max_deg`.
    Uses an Erdos-Renyi graph with targeted edge density, filtered for constraints.
    """
    # Target average degree slightly below max_deg to increase acceptance rate
    p_edge = (max_deg - 0.5) / n 
    
    while True:
        G = nx.fast_gnp_random_graph(n, p_edge)
        
        # Enforce simple graph constraints (no self-loops, no parallel edges)
        # fast_gnp_random_graph already guarantees a simple graph.
        
        # Enforce connectivity
        if not nx.is_connected(G):
            continue
            
        # Enforce maximum degree constraint
        if max(dict(G.degree()).values()) <= max_deg:
            return G

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

import sys
# ... keep the rest of your imports and functions the same ...

def main():
    # 1. Read MAX_DEGREE from command line argument, fallback to a default if not provided
    global MAX_DEGREE
    if len(sys.argv) > 1:
        try:
            MAX_DEGREE = int(sys.argv[1])
        except ValueError:
            print("Error: Degree argument must be an integer.")
            sys.exit(1)
            
    q_frac = Fraction(Q).limit_denominator(10**12)
    
    print(f"Starting TPG Random Search (N={N}, Max Degree={MAX_DEGREE}, Q={Q})...")
    print(f"Total initial B sets to evaluate per graph: {len(INITIAL_B_SETS)}")

    for graph_idx in range(1, MAX_GRAPHS + 1):
        G = generate_max_deg_connected_graph(N, MAX_DEGREE)

        for initial_b in INITIAL_B_SETS:
            result = run_tpg(G, initial_b, q_frac)

            if result == 'all_B':
                # SUCCESS: Append the delta value to the filename
                output_filename = f"tpg_success_delta{MAX_DEGREE}.txt"
                with open(output_filename, "w") as f:
                    f.write(f"Match found on random graph index: {graph_idx}\n")
                    f.write(f"Max Degree Constraint: {MAX_DEGREE}\n")
                    f.write(f"Initial B-State Set:\n{initial_b}\n\n")
                    f.write("Degrees:\n")
                    for node, deg in sorted(G.degree()):
                        f.write(f"Node {node}: degree {deg}\n")
                    f.write("\nEdges:\n")
                    for edge in sorted(G.edges):
                        f.write(f"{edge[0]} {edge[1]}\n")
                
                print(f"Success! Output written to {output_filename}")
                sys.exit(0) 

    # EXHAUSTED: Append the delta value to the exhausted tracking file
    exhausted_filename = f"true_delta{MAX_DEGREE}"
    with open(exhausted_filename, "w") as f:
        f.write(f"true for delta {MAX_DEGREE}\n")
    print(f"Completed {MAX_GRAPHS} evaluations. No matching graph found. '{exhausted_filename}' generated.")
    sys.exit(0)

if __name__ == "__main__":
    main()