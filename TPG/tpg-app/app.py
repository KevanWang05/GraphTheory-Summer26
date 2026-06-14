from flask import Flask, request, jsonify, send_from_directory
import networkx as nx
from fractions import Fraction
from tpg import TPG

app = Flask(__name__, static_folder='static')

sim = None
turn = 0
history = []

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/init', methods=['POST'])
def init_simulation():
    global sim, turn, history
    data = request.get_json()
    q_raw = data.get('q', '0.5')
    nodes = data.get('nodes', [])
    edges = data.get('edges', [])
    initial_b = [int(n) for n in data.get('initial_b', [])]

    try:
        q = Fraction(q_raw).limit_denominator(10**9)
        if not (0 <= q <= 1):
            return jsonify({"error": "q must be between 0 and 1"}), 400
    except (ValueError, ZeroDivisionError):
        return jsonify({"error": f"Invalid q value: '{q_raw}'. Use a decimal (0.5) or fraction (1/3)."}), 400

    G = nx.Graph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)

    sim = TPG(G, initial_b, q)
    turn = 0
    history = [sim.get_system_snapshot()]

    return jsonify({"turn": turn, "equilibrium": None, "q_display": str(q), **sim.get_graph_data()})

@app.route('/step', methods=['POST'])
def step():
    global sim, turn, history
    if sim is None:
        return jsonify({"error": "Simulation not initialized"}), 400

    prev = sim.get_system_snapshot()
    sim.play_turn()
    turn += 1
    current = sim.get_system_snapshot()

    equilibrium = None
    if current == prev:
        equilibrium = "fixed"
    elif len(history) >= 2 and current == history[-2]:
        equilibrium = "cycle"

    history.append(current)
    return jsonify({"turn": turn, "equilibrium": equilibrium, **sim.get_graph_data()})

if __name__ == '__main__':
    app.run(debug=True)
