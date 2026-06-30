"""
tpg_cluster.py
===================
Builds k-regular graphs with a fixed initial A/B partition and fixed
counts of AA-edges and BB-edges (AB-edge count is derived). Runs the
threshold contagion process to completion on each of MAX_GRAPHS random
graphs satisfying that structure.

Returns:
  - "true" file if no graph among MAX_GRAPHS becomes B-contagious (all_B).
  - tpg_success_output.txt with the graph + initial state if one does.
"""

import sys
import random
from fractions import Fraction
import networkx as nx

# ────────────────────────────────────────────────────────────────────────
# CONFIGURATION  -- set these
# ────────────────────────────────────────────────────────────────────────
N_A = 10          # number of nodes starting in state 'A'
N_B = 8          # number of nodes starting in state 'B'
K   = 3          # degree of every node (graph is K-regular)
E_AA = 9         # number of edges with both endpoints initially 'A'
E_BB = 6         # number of edges with both endpoints initially 'B'
Q = "0.501"

MAX_GRAPHS = 10_000
MAX_CONSTRUCTION_TRIES = 100   # retries per graph before declaring infeasible

# ────────────────────────────────────────────────────────────────────────
# GRAPH CONSTRUCTION
# ────────────────────────────────────────────────────────────────────────

def check_feasibility(n_a: int, n_b: int, k: int, e_aa: int, e_bb: int) -> int:
    """Validate inputs and return the implied E_AB, or raise ValueError."""
    if n_a <= 0 or n_b <= 0 or k <= 0:
        raise ValueError("N_A, N_B, and K must be positive.")
    if e_aa < 0 or e_bb < 0:
        raise ValueError("E_AA and E_BB must be non-negative.")
    if 2 * e_aa > n_a * (n_a - 1):
        raise ValueError("E_AA is too large for a simple graph on N_A nodes.")
    if 2 * e_bb > n_b * (n_b - 1):
        raise ValueError("E_BB is too large for a simple graph on N_B nodes.")

    e_ab_from_a = n_a * k - 2 * e_aa
    e_ab_from_b = n_b * k - 2 * e_bb

    if e_ab_from_a != e_ab_from_b:
        raise ValueError(
            f"Infeasible configuration: implied AB-edge count differs from the "
            f"A side ({e_ab_from_a}) and B side ({e_ab_from_b}). "
            f"N_A*K - 2*E_AA must equal N_B*K - 2*E_BB."
        )
    e_ab = e_ab_from_a
    if e_ab < 0:
        raise ValueError("Implied E_AB is negative -- E_AA or E_BB is too large for K.")
    if e_ab > n_a * n_b:
        raise ValueError("Implied E_AB exceeds the maximum possible bipartite edges (N_A * N_B).")
    return e_ab


def random_bounded_degree_split(nodes: list, total: int, k: int) -> dict:
    """
    Randomly partitions `total` indivisible units among `nodes`, with each
    node receiving between 0 and k units (fully random allocation, not an
    even split).
    """
    if total < 0 or total > len(nodes) * k:
        raise ValueError("Infeasible degree split requested.")

    degs = {node: 0 for node in nodes}
    available = list(nodes)
    remaining = total

    while remaining > 0:
        if not available:
            raise ValueError("Infeasible degree split requested.")
        node = random.choice(available)
        degs[node] += 1
        remaining -= 1
        if degs[node] == k:
            available.remove(node)

    return degs


def try_match_stubs_within(stub_list: list):
    """
    Greedily pair up stubs within a single node set: each stub is matched to a
    random still-valid partner (no self-loop, no repeated edge), rather than
    relying on a single blind full-permutation pairing. Returns an edge set,
    or None if it gets stuck (caller should retry).
    """
    stubs = list(stub_list)
    random.shuffle(stubs)
    edges = set()
    while stubs:
        u = stubs.pop()
        order = list(range(len(stubs)))
        random.shuffle(order)
        matched = False
        for idx in order:
            v = stubs[idx]
            if v == u:
                continue
            e = (u, v) if u < v else (v, u)
            if e in edges:
                continue
            stubs.pop(idx)
            edges.add(e)
            matched = True
            break
        if not matched:
            return None
    return edges


def try_match_stubs_bipartite(stub_a: list, stub_b: list):
    """
    Greedily pair stubs from two disjoint node sets: each A-side stub is
    matched to a random still-valid B-side partner (no repeated edge).
    Returns an edge set, or None if it gets stuck (caller should retry).
    """
    if len(stub_a) != len(stub_b):
        return None
    a_list = list(stub_a)
    b_list = list(stub_b)
    random.shuffle(a_list)
    edges = set()
    while a_list:
        u = a_list.pop()
        order = list(range(len(b_list)))
        random.shuffle(order)
        matched = False
        for idx in order:
            v = b_list[idx]
            e = (u, v)
            if e in edges:
                continue
            b_list.pop(idx)
            edges.add(e)
            matched = True
            break
        if not matched:
            return None
    return edges


def build_constrained_graph(n_a: int, n_b: int, k: int, e_aa: int, e_bb: int,
                             e_ab: int, max_tries: int) -> nx.Graph:
    """
    Builds one simple K-regular graph on N_A 'A'-nodes and N_B 'B'-nodes with
    exactly e_aa AA-edges, e_bb BB-edges, and e_ab AB-edges. Raises
    RuntimeError if max_tries is exhausted without success.
    """
    a_nodes = list(range(n_a))
    b_nodes = list(range(n_a, n_a + n_b))

    for _ in range(max_tries):
        try:
            d_aa = random_bounded_degree_split(a_nodes, 2 * e_aa, k)
            d_bb = random_bounded_degree_split(b_nodes, 2 * e_bb, k)
        except ValueError:
            # degree split itself infeasible -- no point retrying further splits
            raise RuntimeError(
                "Infeasible: cannot allocate AA/BB stub counts across nodes "
                "within the [0, K] bound."
            )

        d_ab_a = {node: k - d_aa[node] for node in a_nodes}
        d_ab_b = {node: k - d_bb[node] for node in b_nodes}

        # sanity: AB stub totals must match e_ab on both sides (guaranteed by check_feasibility)
        stub_ab_a = sum(d_ab_a.values())
        stub_ab_b = sum(d_ab_b.values())
        if stub_ab_a != e_ab or stub_ab_b != e_ab:
            continue

        stub_aa = [node for node, d in d_aa.items() for _ in range(d)]
        stub_bb = [node for node, d in d_bb.items() for _ in range(d)]
        stub_ab_a_list = [node for node, d in d_ab_a.items() for _ in range(d)]
        stub_ab_b_list = [node for node, d in d_ab_b.items() for _ in range(d)]

        edges_aa = try_match_stubs_within(stub_aa)
        if edges_aa is None:
            continue
        edges_bb = try_match_stubs_within(stub_bb)
        if edges_bb is None:
            continue
        edges_ab = try_match_stubs_bipartite(stub_ab_a_list, stub_ab_b_list)
        if edges_ab is None:
            continue

        G = nx.Graph()
        G.add_nodes_from(a_nodes + b_nodes)
        G.add_edges_from(edges_aa)
        G.add_edges_from(edges_bb)
        G.add_edges_from(edges_ab)

        if all(d == k for _, d in G.degree()):
            return G
        # otherwise some node ended up isolated in one of the stub sets; retry

    raise RuntimeError(
        f"Infeasible: could not construct a valid graph after {max_tries} attempts "
        f"with N_A={n_a}, N_B={n_b}, K={k}, E_AA={e_aa}, E_BB={e_bb} (E_AB={e_ab})."
    )


# ────────────────────────────────────────────────────────────────────────
# CONTAGION SIMULATION
# ────────────────────────────────────────────────────────────────────────

def run_tpg(G: nx.Graph, initial_b: list, q_frac: Fraction, max_turns: int = 10_000) -> str:
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


# ────────────────────────────────────────────────────────────────────────
# MAIN
# ────────────────────────────────────────────────────────────────────────

def main():
    q_frac = Fraction(Q).limit_denominator(10**12)

    try:
        e_ab = check_feasibility(N_A, N_B, K, E_AA, E_BB)
    except ValueError as exc:
        print(f"INFEASIBLE CONFIGURATION: {exc}")
        sys.exit(1)

    initial_b = list(range(N_A, N_A + N_B))

    print(
        f"Starting TPG search (N_A={N_A}, N_B={N_B}, K={K}, "
        f"E_AA={E_AA}, E_BB={E_BB}, E_AB={e_ab}, Q={Q})..."
    )

    for graph_idx in range(1, MAX_GRAPHS + 1):
        try:
            G = build_constrained_graph(N_A, N_B, K, E_AA, E_BB, e_ab, MAX_CONSTRUCTION_TRIES)
        except RuntimeError as exc:
            print(f"INFEASIBLE: {exc}")
            sys.exit(1)

        result = run_tpg(G, initial_b, q_frac)

        if result == 'all_B':
            output_filename = "tpg_success_output.txt"
            with open(output_filename, "w") as f:
                f.write(f"Match found on random graph index: {graph_idx}\n")
                f.write(f"Initial A-nodes: {list(range(N_A))}\n")
                f.write(f"Initial B-nodes: {initial_b}\n")
                f.write(f"E_AA={E_AA}, E_BB={E_BB}, E_AB={e_ab}\n\n")
                f.write("Edges:\n")
                for edge in sorted(G.edges):
                    f.write(f"{edge[0]} {edge[1]}\n")

            print(f"Contagious graph found. Output written to {output_filename}")
            sys.exit(0)

    with open("true", "w") as f:
        f.write("true\n")
    print(f"Completed {MAX_GRAPHS:,} evaluations. No B-contagious graph found. 'true' file generated.")
    sys.exit(0)


if __name__ == "__main__":
    main()