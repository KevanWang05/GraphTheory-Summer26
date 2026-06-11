import sys
import os
import json
import networkx as nx
import subprocess

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from TPG_script import TPG

def build_geojson_combination_matrix():
    home = os.path.expanduser("~")
    geng_path = os.path.join(home, "GraphTheory-Order8", "bin", "geng")
    output_file = "tpg_combo_matrix_order8.jsonl"

    input_b_states = [
        [], 
        [0], [1], [2], [3], 
        [0,1], [0,2], [0,3], [1,2], [1,3], [2,3],
        [0,1,2], [0,1,3], [0,2,3], [1,2,3],
        [0,1,2,3],
        [4], 
        [0,4], [1,4], [2,4], [3,4], 
        [0,1,4], [0,2,4], [0,3,4], [1,2,4], [1,3,4], [2,3,4],
        [0,1,2,4], [0,1,3,4], [0,2,3,4], [1,2,3,4],
        [0,1,2,3,4], 
        [5], 
        [0,5], [1,5], [2,5], [3,5], 
        [0,1,5], [0,2,5], [0,3,5], [1,2,5], [1,3,5], [2,3,5],
        [0,1,2,5], [0,1,3,5], [0,2,3,5], [1,2,3,5],
        [0,1,2,3,5],
        [4,5], 
        [0,4,5], [1,4,5], [2,4,5], [3,4,5], 
        [0,1,4,5], [0,2,4,5], [0,3,4,5], [1,2,4,5], [1,3,4,5], [2,3,4,5],
        [0,1,2,4,5], [0,1,3,4,5], [0,2,3,4,5], [1,2,3,4,5],
        [0,1,2,3,4,5],
        [6], 
        [0,6], [1,6], [2,6], [3,6], 
        [0,1,6], [0,2,6], [0,3,6], [1,2,6], [1,3,6], [2,3,6],
        [0,1,2,6], [0,1,3,6], [0,2,3,6], [1,2,3,6],
        [0,1,2,3,6],
        [4,6], 
        [0,4,6], [1,4,6], [2,4,6], [3,4,6], 
        [0,1,4,6], [0,2,4,6], [0,3,4,6], [1,2,4,6], [1,3,4,6], [2,3,4,6],
        [0,1,2,4,6], [0,1,3,4,6], [0,2,3,4,6], [1,2,3,4,6],
        [0,1,2,3,4,6], 
        [5,6], 
        [0,5,6], [1,5,6], [2,5,6], [3,5,6], 
        [0,1,5,6], [0,2,5,6], [0,3,5,6], [1,2,5,6], [1,3,5,6], [2,3,5,6],
        [0,1,2,5,6], [0,1,3,5,6], [0,2,3,5,6], [1,2,3,5,6],
        [0,1,2,3,5,6],
        [4,5,6], 
        [0,4,5,6], [1,4,5,6], [2,4,5,6], [3,4,5,6], 
        [0,1,4,5,6], [0,2,4,5,6], [0,3,4,5,6], [1,2,4,5,6], [1,3,4,5,6], [2,3,4,5,6],
        [0,1,2,4,5,6], [0,1,3,4,5,6], [0,2,3,4,5,6], [1,2,3,4,5,6],
        [0,1,2,3,4,5,6],
        [7], 
        [0,7], [1,7], [2,7], [3,7], 
        [0,1,7], [0,2,7], [0,3,7], [1,2,7], [1,3,7], [2,3,7],
        [0,1,2,7], [0,1,3,7], [0,2,3,7], [1,2,3,7],
        [0,1,2,3,7],
        [4,7], 
        [0,4,7], [1,4,7], [2,4,7], [3,4,7], 
        [0,1,4,7], [0,2,4,7], [0,3,4,7], [1,2,4,7], [1,3,4,7], [2,3,4,7],
        [0,1,2,4,7], [0,1,3,4,7], [0,2,3,4,7], [1,2,3,4,7],
        [0,1,2,3,4,7], 
        [5,7], 
        [0,5,7], [1,5,7], [2,5,7], [3,5,7], 
        [0,1,5,7], [0,2,5,7], [0,3,5,7], [1,2,5,7], [1,3,5,7], [2,3,5,7],
        [0,1,2,5,7], [0,1,3,5,7], [0,2,3,5,7], [1,2,3,5,7],
        [0,1,2,3,5,7],
        [4,5,7], 
        [0,4,5,7], [1,4,5,7], [2,4,5,7], [3,4,5,7], 
        [0,1,4,5,7], [0,2,4,5,7], [0,3,4,5,7], [1,2,4,5,7], [1,3,4,5,7], [2,3,4,5,7],
        [0,1,2,4,5,7], [0,1,3,4,5,7], [0,2,3,4,5,7], [1,2,3,4,5,7],
        [0,1,2,3,4,5,7],
        [6,7], 
        [0,6,7], [1,6,7], [2,6,7], [3,6,7], 
        [0,1,6,7], [0,2,6,7], [0,3,6,7], [1,2,6,7], [1,3,6,7], [2,3,6,7],
        [0,1,2,6,7], [0,1,3,6,7], [0,2,3,6,7], [1,2,3,6,7],
        [0,1,2,3,6,7],
        [4,6,7], 
        [0,4,6,7], [1,4,6,7], [2,4,6,7], [3,4,6,7], 
        [0,1,4,6,7], [0,2,4,6,7], [0,3,4,6,7], [1,2,4,6,7], [1,3,4,6,7], [2,3,4,6,7],
        [0,1,2,4,6,7], [0,1,3,4,6,7], [0,2,3,4,6,7], [1,2,3,4,6,7],
        [0,1,2,3,4,6,7], 
        [5,6,7], 
        [0,5,6,7], [1,5,6,7], [2,5,6,7], [3,5,6,7], 
        [0,1,5,6,7], [0,2,5,6,7], [0,3,5,6,7], [1,2,5,6,7], [1,3,5,6,7], [2,3,5,6,7],
        [0,1,2,5,6,7], [0,1,3,5,6,7], [0,2,3,5,6,7], [1,2,3,5,6,7],
        [0,1,2,3,5,6,7],
        [4,5,6,7], 
        [0,4,5,6,7], [1,4,5,6,7], [2,4,5,6,7], [3,4,5,6,7], 
        [0,1,4,5,6,7], [0,2,4,5,6,7], [0,3,4,5,6,7], [1,2,4,5,6,7], [1,3,4,5,6,7], [2,3,4,5,6,7],
        [0,1,2,4,5,6,7], [0,1,3,4,5,6,7], [0,2,3,4,5,6,7], [1,2,3,4,5,6,7],
        [0,1,2,3,4,5,6,7]
    ]

    input_q_values = [1/2, 1/3, 2/3, 1/4, 3/4, 1/5, 2/5, 3/5, 4/5, 1/6, 5/6,
                      1/7, 2/7, 3/7, 4/7, 5/7, 6/7]

    # Open the streaming file directly in append/write mode
    with open(output_file, "w") as f_out:
        # Start geng as a live stream background process
        process = subprocess.Popen([geng_path, '8', '-c'], stdout=subprocess.PIPE, text=True)
        
        index = 0
        for line in process.stdout:
            clean_line = line.strip()
            if not clean_line:
                continue
                
            # Parse only ONE graph topology into active RAM at a time
            G = nx.from_graph6_bytes(clean_line.encode())
            edges_string = str(sorted(list(G.edges())))
            graph_row_id = f"graph_order8_id_{index}_edges_{edges_string}"

            matrix_properties = {
                "graph_type_row": graph_row_id
            }

            for b_nodes in input_b_states:
                valid_b_nodes = [n for n in b_nodes if n in G.nodes()]
                for q in input_q_values:
                    column_key = f"initB_{b_nodes}_q_{q}"
                    
                    # Compute game matrix permutation state
                    game = TPG(graph=G, initial_B_nodes=valid_b_nodes, q=q)
                    result_code = game.run_to_equilibrium()
                    matrix_properties[column_key] = result_code

            # Package row immediately as a single GeoJSON Feature element line
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [0.0, 0.0]
                },
                "properties": matrix_properties
            }
            
            # Commit the string line to disk and flush memory immediately
            f_out.write(json.dumps(feature) + "\n")
            f_out.flush()

            # Status check-in every 50 graphs so you can track progress in cluster_run.log
            if index % 50 == 0:
                print(f"[STATUS] Successfully processed and saved graph row index: {index} / 11117")

            index += 1

        # Safely shut down subprocess streams
        process.stdout.close()
        process.wait()

    print(f"\n{'='*50}\nSuccess! Line-delimited matrix safely saved to '{output_file}'")

if __name__ == "__main__":
    build_geojson_combination_matrix()