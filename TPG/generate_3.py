import json
import networkx as nx
from TPG_script import TPG 

def build_geojson_combination_matrix():
    atlas = nx.graph_atlas_g()
    size_3_graphs = [G for G in atlas if G.number_of_nodes() == 3 and nx.is_connected(G)]
    
    # 2. INPUT YOUR CHOSEN SETS HERE
    # The script will automatically generate every pairing between these two lists
    input_b_states = [[], [0], [1], [2], [0,1], [0,2], [1,2], [0,1,2]]
    
    input_q_values = [0.5]
    
    # Initialize the base GeoJSON structure
    geojson = {
        "type": "FeatureCollection",
        "features": []
    }
    
    # 3. Loop through rows (Graphs)
    for index, G in enumerate(size_3_graphs):
        edges_string = str(sorted(list(G.edges())))
        graph_row_id = f"graph_size3_id_{index}_edges_{edges_string}"
        
        # Start the property row dictionary
        matrix_properties = {
            "graph_type_row": graph_row_id
        }
        
        # 4. Cross-multiply your inputs to generate the columns dynamically
        for b_nodes in input_b_states:
            for q in input_q_values:
                # Create the clean column header name for this pairing
                column_key = f"initB_{b_nodes}_q_{q}"
                
                print(f"[RUNNING] Row: {graph_row_id} | Column: {column_key}")
                
                # Run the simulation game instance
                game = TPG(graph=G, initial_B_nodes=b_nodes, q=q)
                result_code = game.run_to_equilibrium()
                
                # Store the 1, 2, or 3 result code in the column cell
                matrix_properties[column_key] = result_code
                
        # 5. Pack this entire row's data into a GeoJSON Feature
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [0.0, 0.0]  # GeoJSON geometric requirement
            },
            "properties": matrix_properties
        }
        
        geojson["features"].append(feature)
        
    # 6. Save the final GeoJSON file
    output_file = "tpg_combo_matrix.geojson"
    with open(output_file, "w") as f:
        json.dump(geojson, f, indent=4)
        
    print(f"\n{'='*50}\nSuccess! Combination matrix saved to '{output_file}'")

if __name__ == "__main__":
    build_geojson_combination_matrix()