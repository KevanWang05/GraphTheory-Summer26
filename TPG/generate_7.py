import json
import networkx as nx
from TPG_script import TPG 

def build_geojson_combination_matrix():
    atlas = nx.graph_atlas_g()
    size_7_graphs = [G for G in atlas if G.number_of_nodes() == 7 and nx.is_connected(G)]
    
    # 2. INPUT YOUR CHOSEN SETS HERE
    # The script will automatically generate every pairing between these two lists
    input_b_states = [[], 
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
                      [0,1,2,3,4,5,6]
                      ]
    
    input_q_values = [1/2, 1/3, 2/3, 1/4, 3/4, 1/5, 2/5, 3/5, 4/5, 1/6, 5/6]
    
    # Initialize the base GeoJSON structure
    geojson = {
        "type": "FeatureCollection",
        "features": []
    }
    
    # 3. Loop through rows (Graphs)
    for index, G in enumerate(size_7_graphs):
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