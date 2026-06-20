"""
tpg_cluster.py
===================
Optimized for cluster environments. Writes results directly to files.
Samples simple, connected graphs whose MAXIMUM degree is exactly MAX_DEGREE
(i.e. at least one node has degree == MAX_DEGREE, and no node exceeds it),
then runs the TPG (threshold/majority) dynamics until equilibrium.

Usage:
    python tpg_cluster.py <max_degree>

Example:
    python tpg_cluster.py 3
    python tpg_cluster.py 4
    python tpg_cluster.py 5
"""

import sys
from fractions import Fraction
import networkx as nx

# ────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ────────────────────────────────────────────────────────────────────────
N = 50              # Number of nodes
Q = "0.501"
MAX_GRAPHS = 100_000

# Dynamically generate initial B sets based on current N
# Enforces a rolling window of 24 nodes up to N
INITIAL_B_SETS = [list(range(i, i + 24)) for i in range(N - 23)] if N >= 24 else [list(range(N))]


def generate_exact_max_deg_connected_graph(n: int, max_deg: int) -> nx.Graph:
    """
    Generates a simple, connected graph on n nodes whose maximum degree is
    EXACTLY max_deg (no node exceeds max_deg, and at least one node attains it).
    Uses an Erdos-Renyi graph with targeted edge density, filtered for constraints.
    """
    # Target average degree slightly below max_deg to increase acceptance rate
    p_edge = (max_deg - 0.5) / n

    while True:
        G = nx.fast_gnp_random_graph(n, p_edge)

        # fast_gnp_random_graph already guarantees a simple graph
        # (no self-loops, no parallel edges).

        # Enforce connectivity
        if not nx.is_connected(G):
            continue

        degrees = dict(G.degree()).values()
        highest = max(degrees)

        # Enforce that the maximum degree is exactly max_deg
        if highest == max_deg:
            return G
        # else: highest < max_deg or highest > max_deg -> resample


def run_tpg(G: nx.Graph, initial_b: list, q_frac: Fraction, max_turns: int = 10_000) -> str:
    """
    Runs the TPG update rule synchronously until the state reaches a fixed
    point or a 2-cycle (equilibrium), or max_turns is hit.
    Returns 'all_B' if every node ends in state B, else 'mixed_or_A'.
    """
    p = Fraction(1) - q_frac
    state = {node: 'B' if node in initial_b else 'A' for node in G.nodes}
    prev_prev_snapshot = None
    prev_snapshot = tuple(sorted(state.items()))

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
        prev_snapshot = snapshot

    b_count = sum(1 for s in state.values() if s == 'B')
    if b_count == len(G.nodes):
        return 'all_B'
    return 'mixed_or_A'


def main():
    if len(sys.argv) < 2:
        print("Usage: python tpg_cluster.py <max_degree>")
        sys.exit(1)

    try:
        max_degree = int(sys.argv[1])
    except ValueError:
        print("Error: Degree argument must be an integer.")
        sys.exit(1)

    q_frac = Fraction(Q).limit_denominator(10**12)

    print(f"Starting TPG Random Search (N={N}, Max Degree={max_degree}, Q={Q})...")
    print(f"Total initial B sets to evaluate per graph: {len(INITIAL_B_SETS)}")
    sys.stdout.flush()

    for graph_idx in range(1, MAX_GRAPHS + 1):
        G = generate_exact_max_deg_connected_graph(N, max_degree)

        for initial_b in INITIAL_B_SETS:
            result = run_tpg(G, initial_b, q_frac)

            if result == 'all_B':
                # SUCCESS: write graph + initial set to file, named by max_degree
                output_filename = f"tpg_success_delta{max_degree}.txt"
                with open(output_filename, "w") as f:
                    f.write(f"Match found on random graph index: {graph_idx}\n")
                    f.write(f"Max Degree Constraint: {max_degree}\n")
                    f.write(f"Initial B-State Set:\n{initial_b}\n\n")
                    f.write("Degrees:\n")
                    for node, deg in sorted(G.degree()):
                        f.write(f"Node {node}: degree {deg}\n")
                    f.write("\nEdges:\n")
                    for edge in sorted(G.edges):
                        f.write(f"{edge[0]} {edge[1]}\n")

                print(f"Success! Output written to {output_filename}")
                sys.exit(0)

        if graph_idx % 1000 == 0:
            print(f"  ...evaluated {graph_idx} graphs (max_degree={max_degree})")
            sys.stdout.flush()

    # EXHAUSTED: write tracking file, named by max_degree
    exhausted_filename = f"true_delta{max_degree}.txt"
    with open(exhausted_filename, "w") as f:
        f.write(f"true for delta {max_degree}\n")
    print(f"Completed {MAX_GRAPHS} evaluations. No matching graph found. "
          f"'{exhausted_filename}' generated.")
    sys.exit(0)


if __name__ == "__main__":
    main()
