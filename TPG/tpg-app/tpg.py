import networkx as nx
from fractions import Fraction

class TPG:
    def __init__(self, graph: nx.Graph, initial_B_nodes: list, q):
        self.G = graph.copy()
        # Accept string like "1/3", float, or Fraction
        self.q = Fraction(q).limit_denominator(10**9)
        self.p = Fraction(1) - self.q

        for node in self.G.nodes:
            self.G.nodes[node]['state'] = 'A'
        for node in initial_B_nodes:
            if node in self.G.nodes:
                self.G.nodes[node]['state'] = 'B'

    def get_system_snapshot(self):
        return tuple(sorted((node, data['state']) for node, data in self.G.nodes(data=True)))

    def play_turn(self):
        next_states = {}
        for node in self.G.nodes:
            neighbors = list(self.G.neighbors(node))
            total = len(neighbors)
            if total == 0:
                next_states[node] = self.G.nodes[node]['state']
                continue
            n_A = sum(1 for nb in neighbors if self.G.nodes[nb]['state'] == 'A')
            # Exact rational comparison: n_A/total > p  ⟺  n_A > p * total
            if Fraction(n_A, total) > self.p:
                next_states[node] = 'A'
            else:
                next_states[node] = 'B'
        for node, state in next_states.items():
            self.G.nodes[node]['state'] = state

    def get_graph_data(self):
        nodes = [{"id": n, "state": self.G.nodes[n]['state']} for n in self.G.nodes]
        edges = [{"from": u, "to": v} for u, v in self.G.edges]
        states = [self.G.nodes[n]['state'] for n in self.G.nodes]
        return {
            "nodes": nodes,
            "edges": edges,
            "a_count": states.count('A'),
            "b_count": states.count('B'),
        }
