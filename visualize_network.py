import sumolib
import matplotlib.pyplot as plt
import numpy as np

def visualize_network(net_file):
    # Load the network
    net = sumolib.net.readNet(net_file)
    
    # Create a new figure
    fig, ax = plt.subplots(figsize=(15, 15))
    
    # Plot edges
    for edge in net.getEdges():
        # Get the shape of the edge
        shape = edge.getShape()
        x_coords = [point[0] for point in shape]
        y_coords = [point[1] for point in shape]
        
        # Plot the edge
        ax.plot(x_coords, y_coords, 'k-', linewidth=1)
        
        # Add edge ID at the midpoint
        if len(shape) > 1:
            mid_idx = len(shape) // 2
            ax.text(shape[mid_idx][0], shape[mid_idx][1], edge.getID(), fontsize=6)
    
    # Plot nodes
    for node in net.getNodes():
        pos = node.getCoord()
        ax.plot(pos[0], pos[1], 'ro', markersize=5)
        ax.text(pos[0], pos[1], node.getID(), fontsize=8)
    
    # Set equal aspect ratio
    ax.set_aspect('equal')
    
    # Add title and labels
    plt.title('Levent Road Network')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    
    # Save the plot
    plt.savefig('levent_network.png', dpi=300, bbox_inches='tight')
    print("Network visualization saved as 'levent_network.png'")
    
    # Show the plot
    plt.show()

if __name__ == "__main__":
    visualize_network("levent.net.xml") 