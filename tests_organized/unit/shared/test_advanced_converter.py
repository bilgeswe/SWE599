def test_validate_road_connections(self):
    """Test road connection validation"""
    # Create a simple network with valid connections
    net = sumolib.net.Net()
    
    # Create nodes
    node1 = net.addNode("node1", x=0, y=0)
    node2 = net.addNode("node2", x=100, y=0)
    node3 = net.addNode("node3", x=200, y=0)
    
    # Create edges with proper lane connections
    edge1 = net.addEdge("edge1", node1, node2, numLanes=2)
    edge2 = net.addEdge("edge2", node2, node3, numLanes=2)
    
    # Add lane connections
    edge1.addLane(0, speed=13.89, length=100)
    edge1.addLane(1, speed=13.89, length=100)
    edge2.addLane(0, speed=13.89, length=100)
    edge2.addLane(1, speed=13.89, length=100)
    
    # Create a junction
    junction = net.addJunction("junction1", node2, x=100, y=0)
    
    # Add connections
    net.addConnection(edge1, edge2, fromLane=0, toLane=0)
    net.addConnection(edge1, edge2, fromLane=1, toLane=1)
    
    # Validate connections
    self.assertTrue(self.converter.validate_road_connections(net))
    
    # Test with invalid connection (different number of lanes)
    edge3 = net.addEdge("edge3", node3, net.addNode("node4", x=300, y=0), numLanes=1)
    edge3.addLane(0, speed=13.89, length=100)
    net.addConnection(edge2, edge3, fromLane=0, toLane=0)
    self.assertFalse(self.converter.validate_road_connections(net))

def test_junction_connections(self):
    """Test junction connection handling."""
    parser = AdvancedSumoNetworkParser(self.test_net_file)
    parser.parse()
    
    # Test via lane validation
    # The test network has edge1 with lanes 0,1 and edge2 with lanes 0,1
    # The connection is from edge1_0 to edge2_0
    self.assertTrue(parser._is_valid_via_lane("edge1", "edge2", "edge1_0_edge2_0"))
    
    # Test invalid via lane
    self.assertFalse(parser._is_valid_via_lane("edge1", "edge2", "invalid_lane"))
    self.assertFalse(parser._is_valid_via_lane("edge1", "edge2", "edge1_2_edge2_0"))  # Lane 2 doesn't exist
    self.assertFalse(parser._is_valid_via_lane("edge1", "edge2", "edge1_0_edge2_2"))  # Lane 2 doesn't exist
    
    # Test junction connections
    net = sumolib.net.Net()
    
    # Create nodes
    node1 = net.addNode("node1", x=0, y=0)
    node2 = net.addNode("node2", x=100, y=0)
    node3 = net.addNode("node3", x=100, y=100)
    node4 = net.addNode("node4", x=200, y=0)
    
    # Create edges
    edge1 = net.addEdge("edge1", node1, node2, numLanes=2)
    edge2 = net.addEdge("edge2", node2, node3, numLanes=2)
    edge3 = net.addEdge("edge3", node2, node4, numLanes=2)
    
    # Add lane connections
    edge1.addLane(0, speed=13.89, length=100)
    edge1.addLane(1, speed=13.89, length=100)
    edge2.addLane(0, speed=13.89, length=100)
    edge2.addLane(1, speed=13.89, length=100)
    edge3.addLane(0, speed=13.89, length=100)
    edge3.addLane(1, speed=13.89, length=100)
    
    # Create a junction
    junction = net.addJunction("junction1", node2, x=100, y=0)
    
    # Add connections
    net.addConnection(edge1, edge2, fromLane=0, toLane=0)
    net.addConnection(edge1, edge2, fromLane=1, toLane=1)
    net.addConnection(edge1, edge3, fromLane=0, toLane=0)
    net.addConnection(edge1, edge3, fromLane=1, toLane=1)
    
    # Validate junction connections
    self.assertTrue(self.converter.validate_junction_connections(net))
    
    # Test with invalid connection (missing connection)
    edge4 = net.addEdge("edge4", node2, net.addNode("node5", x=100, y=-100), numLanes=2)
    edge4.addLane(0, speed=13.89, length=100)
    edge4.addLane(1, speed=13.89, length=100)
    self.assertFalse(self.converter.validate_junction_connections(net))

def test_validate_traffic_signals(self):
    """Test traffic signal validation"""
    # Create a simple network with traffic signals
    net = sumolib.net.Net()
    
    # Create nodes
    node1 = net.addNode("node1", x=0, y=0)
    node2 = net.addNode("node2", x=100, y=0)
    node3 = net.addNode("node3", x=100, y=100)
    node4 = net.addNode("node4", x=200, y=0)
    
    # Create edges
    edge1 = net.addEdge("edge1", node1, node2, numLanes=2)
    edge2 = net.addEdge("edge2", node2, node3, numLanes=2)
    edge3 = net.addEdge("edge3", node2, node4, numLanes=2)
    
    # Add lane connections
    edge1.addLane(0, speed=13.89, length=100)
    edge1.addLane(1, speed=13.89, length=100)
    edge2.addLane(0, speed=13.89, length=100)
    edge2.addLane(1, speed=13.89, length=100)
    edge3.addLane(0, speed=13.89, length=100)
    edge3.addLane(1, speed=13.89, length=100)
    
    # Create a junction with traffic signals
    junction = net.addJunction("junction1", node2, x=100, y=0)
    junction.setType("traffic_light")
    
    # Add traffic light program
    tl_program = net.addTLS("tl1", node2)
    tl_program.addPhase(31, "GG")  # Green for both directions
    tl_program.addPhase(3, "yy")   # Yellow
    tl_program.addPhase(31, "rr")  # Red
    
    # Add connections
    net.addConnection(edge1, edge2, fromLane=0, toLane=0)
    net.addConnection(edge1, edge2, fromLane=1, toLane=1)
    net.addConnection(edge1, edge3, fromLane=0, toLane=0)
    net.addConnection(edge1, edge3, fromLane=1, toLane=1)
    
    # Validate traffic signals
    self.assertTrue(self.converter.validate_traffic_signals(net))
    
    # Test with invalid traffic signal (missing program)
    junction2 = net.addJunction("junction2", node3, x=100, y=100)
    junction2.setType("traffic_light")
    self.assertFalse(self.converter.validate_traffic_signals(net))

def test_validate_road_geometry(self):
    """Test road geometry validation"""
    # Create a simple network with valid geometry
    net = sumolib.net.Net()
    
    # Create nodes
    node1 = net.addNode("node1", x=0, y=0)
    node2 = net.addNode("node2", x=100, y=0)
    node3 = net.addNode("node3", x=100, y=100)
    
    # Create edges with proper geometry
    edge1 = net.addEdge("edge1", node1, node2, numLanes=2)
    edge2 = net.addEdge("edge2", node2, node3, numLanes=2)
    
    # Add lane connections with proper geometry
    edge1.addLane(0, speed=13.89, length=100)
    edge1.addLane(1, speed=13.89, length=100)
    edge2.addLane(0, speed=13.89, length=100)
    edge2.addLane(1, speed=13.89, length=100)
    
    # Add shape points for curved geometry
    edge1.setShape([(0, 0), (50, 0), (100, 0)])
    edge2.setShape([(100, 0), (100, 50), (100, 100)])
    
    # Validate road geometry
    self.assertTrue(self.converter.validate_road_geometry(net))
    
    # Test with invalid geometry (sharp angle)
    edge3 = net.addEdge("edge3", node3, net.addNode("node4", x=0, y=100), numLanes=2)
    edge3.addLane(0, speed=13.89, length=100)
    edge3.addLane(1, speed=13.89, length=100)
    edge3.setShape([(100, 100), (50, 100), (0, 100)])
    self.assertFalse(self.converter.validate_road_geometry(net))

def test_validate_lane_connections(self):
    """Test lane connection validation"""
    # Create a simple network with valid lane connections
    net = sumolib.net.Net()
    
    # Create nodes
    node1 = net.addNode("node1", x=0, y=0)
    node2 = net.addNode("node2", x=100, y=0)
    node3 = net.addNode("node3", x=200, y=0)
    
    # Create edges with proper lane connections
    edge1 = net.addEdge("edge1", node1, node2, numLanes=2)
    edge2 = net.addEdge("edge2", node2, node3, numLanes=2)
    
    # Add lane connections
    edge1.addLane(0, speed=13.89, length=100)
    edge1.addLane(1, speed=13.89, length=100)
    edge2.addLane(0, speed=13.89, length=100)
    edge2.addLane(1, speed=13.89, length=100)
    
    # Create a junction
    junction = net.addJunction("junction1", node2, x=100, y=0)
    
    # Add connections
    net.addConnection(edge1, edge2, fromLane=0, toLane=0)
    net.addConnection(edge1, edge2, fromLane=1, toLane=1)
    
    # Validate lane connections
    self.assertTrue(self.converter.validate_lane_connections(net))
    
    # Test with invalid connection (missing connection)
    edge3 = net.addEdge("edge3", node3, net.addNode("node4", x=300, y=0), numLanes=2)
    edge3.addLane(0, speed=13.89, length=100)
    edge3.addLane(1, speed=13.89, length=100)
    self.assertFalse(self.converter.validate_lane_connections(net))

def test_validate_network_integrity(self):
    """Test network integrity validation"""
    # Create a simple network with valid integrity
    net = sumolib.net.Net()
    
    # Create nodes
    node1 = net.addNode("node1", x=0, y=0)
    node2 = net.addNode("node2", x=100, y=0)
    node3 = net.addNode("node3", x=200, y=0)
    
    # Create edges with proper connections
    edge1 = net.addEdge("edge1", node1, node2, numLanes=2)
    edge2 = net.addEdge("edge2", node2, node3, numLanes=2)
    
    # Add lane connections
    edge1.addLane(0, speed=13.89, length=100)
    edge1.addLane(1, speed=13.89, length=100)
    edge2.addLane(0, speed=13.89, length=100)
    edge2.addLane(1, speed=13.89, length=100)
    
    # Create a junction
    junction = net.addJunction("junction1", node2, x=100, y=0)
    
    # Add connections
    net.addConnection(edge1, edge2, fromLane=0, toLane=0)
    net.addConnection(edge1, edge2, fromLane=1, toLane=1)
    
    # Validate network integrity
    self.assertTrue(self.converter.validate_network_integrity(net))
    
    # Test with invalid integrity (disconnected edge)
    edge3 = net.addEdge("edge3", node3, net.addNode("node4", x=300, y=0), numLanes=2)
    edge3.addLane(0, speed=13.89, length=100)
    edge3.addLane(1, speed=13.89, length=100)
    self.assertFalse(self.converter.validate_network_integrity(net))

def test_validate_road_types(self):
    """Test road type validation"""
    # Create a simple network with valid road types
    net = sumolib.net.Net()
    
    # Create nodes
    node1 = net.addNode("node1", x=0, y=0)
    node2 = net.addNode("node2", x=100, y=0)
    node3 = net.addNode("node3", x=200, y=0)
    
    # Create edges with proper road types
    edge1 = net.addEdge("edge1", node1, node2, numLanes=2)
    edge2 = net.addEdge("edge2", node2, node3, numLanes=2)
    
    # Add lane connections
    edge1.addLane(0, speed=13.89, length=100)
    edge1.addLane(1, speed=13.89, length=100)
    edge2.addLane(0, speed=13.89, length=100)
    edge2.addLane(1, speed=13.89, length=100)
    
    # Set road types
    edge1.setType("highway")
    edge2.setType("highway")
    
    # Validate road types
    self.assertTrue(self.converter.validate_road_types(net))
    
    # Test with invalid road type
    edge3 = net.addEdge("edge3", node3, net.addNode("node4", x=300, y=0), numLanes=2)
    edge3.addLane(0, speed=13.89, length=100)
    edge3.addLane(1, speed=13.89, length=100)
    edge3.setType("invalid_type")
    self.assertFalse(self.converter.validate_road_types(net))

def test_validate_road_speed_limits(self):
    """Test road speed limit validation"""
    # Create a simple network with valid speed limits
    net = sumolib.net.Net()
    
    # Create nodes
    node1 = net.addNode("node1", x=0, y=0)
    node2 = net.addNode("node2", x=100, y=0)
    node3 = net.addNode("node3", x=200, y=0)
    
    # Create edges with proper speed limits
    edge1 = net.addEdge("edge1", node1, node2, numLanes=2)
    edge2 = net.addEdge("edge2", node2, node3, numLanes=2)
    
    # Add lane connections with proper speed limits
    edge1.addLane(0, speed=13.89, length=100)  # 50 km/h
    edge1.addLane(1, speed=13.89, length=100)  # 50 km/h
    edge2.addLane(0, speed=13.89, length=100)  # 50 km/h
    edge2.addLane(1, speed=13.89, length=100)  # 50 km/h
    
    # Validate speed limits
    self.assertTrue(self.converter.validate_road_speed_limits(net))
    
    # Test with invalid speed limit
    edge3 = net.addEdge("edge3", node3, net.addNode("node4", x=300, y=0), numLanes=2)
    edge3.addLane(0, speed=55.56, length=100)  # 200 km/h (too high)
    edge3.addLane(1, speed=55.56, length=100)  # 200 km/h (too high)
    self.assertFalse(self.converter.validate_road_speed_limits(net))

def test_validate_road_lengths(self):
    """Test road length validation"""
    # Create a simple network with valid road lengths
    net = sumolib.net.Net()
    
    # Create nodes
    node1 = net.addNode("node1", x=0, y=0)
    node2 = net.addNode("node2", x=100, y=0)
    node3 = net.addNode("node3", x=200, y=0)
    
    # Create edges with proper lengths
    edge1 = net.addEdge("edge1", node1, node2, numLanes=2)
    edge2 = net.addEdge("edge2", node2, node3, numLanes=2)
    
    # Add lane connections with proper lengths
    edge1.addLane(0, speed=13.89, length=100)
    edge1.addLane(1, speed=13.89, length=100)
    edge2.addLane(0, speed=13.89, length=100)
    edge2.addLane(1, speed=13.89, length=100)
    
    # Validate road lengths
    self.assertTrue(self.converter.validate_road_lengths(net))
    
    # Test with invalid length
    edge3 = net.addEdge("edge3", node3, net.addNode("node4", x=300, y=0), numLanes=2)
    edge3.addLane(0, speed=13.89, length=0)  # Zero length
    edge3.addLane(1, speed=13.89, length=0)  # Zero length
    self.assertFalse(self.converter.validate_road_lengths(net))

def test_validate_road_widths(self):
    """Test road width validation"""
    # Create a simple network with valid road widths
    net = sumolib.net.Net()
    
    # Create nodes
    node1 = net.addNode("node1", x=0, y=0)
    node2 = net.addNode("node2", x=100, y=0)
    node3 = net.addNode("node3", x=200, y=0)
    
    # Create edges with proper widths
    edge1 = net.addEdge("edge1", node1, node2, numLanes=2)
    edge2 = net.addEdge("edge2", node2, node3, numLanes=2)
    
    # Add lane connections with proper widths
    edge1.addLane(0, speed=13.89, length=100, width=3.5)
    edge1.addLane(1, speed=13.89, length=100, width=3.5)
    edge2.addLane(0, speed=13.89, length=100, width=3.5)
    edge2.addLane(1, speed=13.89, length=100, width=3.5)
    
    # Validate road widths
    self.assertTrue(self.converter.validate_road_widths(net))
    
    # Test with invalid width
    edge3 = net.addEdge("edge3", node3, net.addNode("node4", x=300, y=0), numLanes=2)
    edge3.addLane(0, speed=13.89, length=100, width=0)  # Zero width
    edge3.addLane(1, speed=13.89, length=100, width=0)  # Zero width
    self.assertFalse(self.converter.validate_road_widths(net))

def test_validate_road_elevations(self):
    """Test road elevation validation"""
    # Create a simple network with valid road elevations
    net = sumolib.net.Net()
    
    # Create nodes
    node1 = net.addNode("node1", x=0, y=0, z=0)
    node2 = net.addNode("node2", x=100, y=0, z=0)
    node3 = net.addNode("node3", x=200, y=0, z=0)
    
    # Create edges with proper elevations
    edge1 = net.addEdge("edge1", node1, node2, numLanes=2)
    edge2 = net.addEdge("edge2", node2, node3, numLanes=2)
    
    # Add lane connections with proper elevations
    edge1.addLane(0, speed=13.89, length=100)
    edge1.addLane(1, speed=13.89, length=100)
    edge2.addLane(0, speed=13.89, length=100)
    edge2.addLane(1, speed=13.89, length=100)
    
    # Validate road elevations
    self.assertTrue(self.converter.validate_road_elevations(net))
    
    # Test with invalid elevation
    edge3 = net.addEdge("edge3", node3, net.addNode("node4", x=300, y=0, z=100), numLanes=2)
    edge3.addLane(0, speed=13.89, length=100)
    edge3.addLane(1, speed=13.89, length=100)
    self.assertFalse(self.converter.validate_road_elevations(net))

def test_validate_road_curvature(self):
    """Test road curvature validation"""
    # Create a simple network with valid road curvature
    net = sumolib.net.Net()
    
    # Create nodes
    node1 = net.addNode("node1", x=0, y=0)
    node2 = net.addNode("node2", x=100, y=0)
    node3 = net.addNode("node3", x=200, y=0)
    
    # Create edges with proper curvature
    edge1 = net.addEdge("edge1", node1, node2, numLanes=2)
    edge2 = net.addEdge("edge2", node2, node3, numLanes=2)
    
    # Add lane connections with proper curvature
    edge1.addLane(0, speed=13.89, length=100)
    edge1.addLane(1, speed=13.89, length=100)
    edge2.addLane(0, speed=13.89, length=100)
    edge2.addLane(1, speed=13.89, length=100)
    
    # Add shape points for curved geometry
    edge1.setShape([(0, 0), (50, 0), (100, 0)])
    edge2.setShape([(100, 0), (150, 0), (200, 0)])
    
    # Validate road curvature
    self.assertTrue(self.converter.validate_road_curvature(net))
    
    # Test with invalid curvature
    edge3 = net.addEdge("edge3", node3, net.addNode("node4", x=300, y=0), numLanes=2)
    edge3.addLane(0, speed=13.89, length=100)
    edge3.addLane(1, speed=13.89, length=100)
    edge3.setShape([(200, 0), (250, 100), (300, 0)])  # Sharp curve
    self.assertFalse(self.converter.validate_road_curvature(net))

def test_validate_road_slopes(self):
    """Test road slope validation"""
    # Create a simple network with valid road slopes
    net = sumolib.net.Net()
    
    # Create nodes
    node1 = net.addNode("node1", x=0, y=0, z=0)
    node2 = net.addNode("node2", x=100, y=0, z=10)
    node3 = net.addNode("node3", x=200, y=0, z=20)
    
    # Create edges with proper slopes
    edge1 = net.addEdge("edge1", node1, node2, numLanes=2)
    edge2 = net.addEdge("edge2", node2, node3, numLanes=2)
    
    # Add lane connections with proper slopes
    edge1.addLane(0, speed=13.89, length=100)
    edge1.addLane(1, speed=13.89, length=100)
    edge2.addLane(0, speed=13.89, length=100)
    edge2.addLane(1, speed=13.89, length=100)
    
    # Validate road slopes
    self.assertTrue(self.converter.validate_road_slopes(net))
    
    # Test with invalid slope
    edge3 = net.addEdge("edge3", node3, net.addNode("node4", x=300, y=0, z=100), numLanes=2)
    edge3.addLane(0, speed=13.89, length=100)
    edge3.addLane(1, speed=13.89, length=100)
    self.assertFalse(self.converter.validate_road_slopes(net))

def test_validate_road_crossings(self):
    """Test road crossing validation"""
    # Create a simple network with valid road crossings
    net = sumolib.net.Net()
    
    # Create nodes
    node1 = net.addNode("node1", x=0, y=0)
    node2 = net.addNode("node2", x=100, y=0)
    node3 = net.addNode("node3", x=100, y=100)
    node4 = net.addNode("node4", x=200, y=0)
    
    # Create edges
    edge1 = net.addEdge("edge1", node1, node2, numLanes=2)
    edge2 = net.addEdge("edge2", node2, node3, numLanes=2)
    edge3 = net.addEdge("edge3", node2, node4, numLanes=2)
    
    # Add lane connections
    edge1.addLane(0, speed=13.89, length=100)
    edge1.addLane(1, speed=13.89, length=100)
    edge2.addLane(0, speed=13.89, length=100)
    edge2.addLane(1, speed=13.89, length=100)
    edge3.addLane(0, speed=13.89, length=100)
    edge3.addLane(1, speed=13.89, length=100)
    
    # Create a junction
    junction = net.addJunction("junction1", node2, x=100, y=0)
    
    # Add connections
    net.addConnection(edge1, edge2, fromLane=0, toLane=0)
    net.addConnection(edge1, edge2, fromLane=1, toLane=1)
    net.addConnection(edge1, edge3, fromLane=0, toLane=0)
    net.addConnection(edge1, edge3, fromLane=1, toLane=1)
    
    # Validate road crossings
    self.assertTrue(self.converter.validate_road_crossings(net))
    
    # Test with invalid crossing
    edge4 = net.addEdge("edge4", node3, net.addNode("node5", x=100, y=200), numLanes=2)
    edge4.addLane(0, speed=13.89, length=100)
    edge4.addLane(1, speed=13.89, length=100)
    edge5 = net.addEdge("edge5", net.addNode("node6", x=0, y=100), node3, numLanes=2)
    edge5.addLane(0, speed=13.89, length=100)
    edge5.addLane(1, speed=13.89, length=100)
    self.assertFalse(self.converter.validate_road_crossings(net))

def test_validate_road_signs(self):
    """Test road sign validation"""
    # Create a simple network with valid road signs
    net = sumolib.net.Net()
    
    # Create nodes
    node1 = net.addNode("node1", x=0, y=0)
    node2 = net.addNode("node2", x=100, y=0)
    node3 = net.addNode("node3", x=200, y=0)
    
    # Create edges with proper signs
    edge1 = net.addEdge("edge1", node1, node2, numLanes=2)
    edge2 = net.addEdge("edge2", node2, node3, numLanes=2)
    
    # Add lane connections
    edge1.addLane(0, speed=13.89, length=100)
    edge1.addLane(1, speed=13.89, length=100)
    edge2.addLane(0, speed=13.89, length=100)
    edge2.addLane(1, speed=13.89, length=100)
    
    # Add road signs
    edge1.addSign("speed_limit", "50")
    edge2.addSign("speed_limit", "50")
    
    # Validate road signs
    self.assertTrue(self.converter.validate_road_signs(net))
    
    # Test with invalid sign
    edge3 = net.addEdge("edge3", node3, net.addNode("node4", x=300, y=0), numLanes=2)
    edge3.addLane(0, speed=13.89, length=100)
    edge3.addLane(1, speed=13.89, length=100)
    edge3.addSign("invalid_sign", "invalid_value")
    self.assertFalse(self.converter.validate_road_signs(net))

def test_validate_road_markings(self):
    """Test road marking validation"""
    # Create a simple network with valid road markings
    net = sumolib.net.Net()
    
    # Create nodes
    node1 = net.addNode("node1", x=0, y=0)
    node2 = net.addNode("node2", x=100, y=0)
    node3 = net.addNode("node3", x=200, y=0)
    
    # Create edges with proper markings
    edge1 = net.addEdge("edge1", node1, node2, numLanes=2)
    edge2 = net.addEdge("edge2", node2, node3, numLanes=2)
    
    # Add lane connections with proper markings
    edge1.addLane(0, speed=13.89, length=100)
    edge1.addLane(1, speed=13.89, length=100)
    edge2.addLane(0, speed=13.89, length=100)
    edge2.addLane(1, speed=13.89, length=100)
    
    # Add road markings
    edge1.addMarking("center_line", "solid")
    edge1.addMarking("lane_marking", "dashed")
    edge2.addMarking("center_line", "solid")
    edge2.addMarking("lane_marking", "dashed")
    
    # Validate road markings
    self.assertTrue(self.converter.validate_road_markings(net))
    
    # Test with invalid marking
    edge3 = net.addEdge("edge3", node3, net.addNode("node4", x=300, y=0), numLanes=2)
    edge3.addLane(0, speed=13.89, length=100)
    edge3.addLane(1, speed=13.89, length=100)
    edge3.addMarking("invalid_marking", "invalid_value")
    self.assertFalse(self.converter.validate_road_markings(net))

def test_validate_road_objects(self):
    """Test road object validation"""
    # Create a simple network with valid road objects
    net = sumolib.net.Net()
    
    # Create nodes
    node1 = net.addNode("node1", x=0, y=0)
    node2 = net.addNode("node2", x=100, y=0)
    node3 = net.addNode("node3", x=200, y=0)
    
    # Create edges with proper objects
    edge1 = net.addEdge("edge1", node1, node2, numLanes=2)
    edge2 = net.addEdge("edge2", node2, node3, numLanes=2)
    
    # Add lane connections with proper objects
    edge1.addLane(0, speed=13.89, length=100)
    edge1.addLane(1, speed=13.89, length=100)
    edge2.addLane(0, speed=13.89, length=100)
    edge2.addLane(1, speed=13.89, length=100)
    
    # Add road objects
    edge1.addObject("guardrail", "left")
    edge2.addObject("guardrail", "right")
    
    # Validate road objects
    self.assertTrue(self.converter.validate_road_objects(net))
    
    # Test with invalid object
    edge3 = net.addEdge("edge3", node3, net.addNode("node4", x=300, y=0), numLanes=2)
    edge3.addLane(0, speed=13.89, length=100)
    edge3.addLane(1, speed=13.89, length=100)
    edge3.addObject("invalid_object", "invalid_position")
    self.assertFalse(self.converter.validate_road_objects(net))

def test_validate_road_weather(self):
    """Test road weather validation"""
    # Create a simple network with valid road weather
    net = sumolib.net.Net()
    
    # Create nodes
    node1 = net.addNode("node1", x=0, y=0)
    node2 = net.addNode("node2", x=100, y=0)
    node3 = net.addNode("node3", x=200, y=0)
    
    # Create edges with proper weather
    edge1 = net.addEdge("edge1", node1, node2, numLanes=2)
    edge2 = net.addEdge("edge2", node2, node3, numLanes=2)
    
    # Add lane connections with proper weather
    edge1.addLane(0, speed=13.89, length=100)
    edge1.addLane(1, speed=13.89, length=100)
    edge2.addLane(0, speed=13.89, length=100)
    edge2.addLane(1, speed=13.89, length=100)
    
    # Add road weather
    edge1.setWeather("dry")
    edge2.setWeather("dry")
    
    # Validate road weather
    self.assertTrue(self.converter.validate_road_weather(net))
    
    # Test with invalid weather
    edge3 = net.addEdge("edge3", node3, net.addNode("node4", x=300, y=0), numLanes=2)
    edge3.addLane(0, speed=13.89, length=100)
    edge3.addLane(1, speed=13.89, length=100)
    edge3.setWeather("invalid_weather")
    self.assertFalse(self.converter.validate_road_weather(net))

def test_validate_road_visibility(self):
    """Test road visibility validation"""
    # Create a simple network with valid road visibility
    net = sumolib.net.Net()
    
    # Create nodes
    node1 = net.addNode("node1", x=0, y=0)
    node2 = net.addNode("node2", x=100, y=0)
    node3 = net.addNode("node3", x=200, y=0)
    
    # Create edges with proper visibility
    edge1 = net.addEdge("edge1", node1, node2, numLanes=2)
    edge2 = net.addEdge("edge2", node2, node3, numLanes=2)
    
    # Add lane connections with proper visibility
    edge1.addLane(0, speed=13.89, length=100)
    edge1.addLane(1, speed=13.89, length=100)
    edge2.addLane(0, speed=13.89, length=100)
    edge2.addLane(1, speed=13.89, length=100)
    
    # Add road visibility
    edge1.setVisibility(1000)  # 1000 meters visibility
    edge2.setVisibility(1000)  # 1000 meters visibility
    
    # Validate road visibility
    self.assertTrue(self.converter.validate_road_visibility(net))
    
    # Test with invalid visibility
    edge3 = net.addEdge("edge3", node3, net.addNode("node4", x=300, y=0), numLanes=2)
    edge3.addLane(0, speed=13.89, length=100)
    edge3.addLane(1, speed=13.89, length=100)
    edge3.setVisibility(0)  # Zero visibility
    self.assertFalse(self.converter.validate_road_visibility(net))

def test_validate_road_lighting(self):
    """Test road lighting validation"""
    # Create a simple network with valid road lighting
    net = sumolib.net.Net()
    
    # Create nodes
    node1 = net.addNode("node1", x=0, y=0)
    node2 = net.addNode("node2", x=100, y=0)
    node3 = net.addNode("node3", x=200, y=0)
    
    # Create edges with proper lighting
    edge1 = net.addEdge("edge1", node1, node2, numLanes=2)
    edge2 = net.addEdge("edge2", node2, node3, numLanes=2)
    
    # Add lane connections with proper lighting
    edge1.addLane(0, speed=13.89, length=100)
    edge1.addLane(1, speed=13.89, length=100)
    edge2.addLane(0, speed=13.89, length=100)
    edge2.addLane(1, speed=13.89, length=100)
    
    # Add road lighting
    edge1.setLighting("day")
    edge2.setLighting("day")
    
    # Validate road lighting
    self.assertTrue(self.converter.validate_road_lighting(net))
    
    # Test with invalid lighting
    edge3 = net.addEdge("edge3", node3, net.addNode("node4", x=300, y=0), numLanes=2)
    edge3.addLane(0, speed=13.89, length=100)
    edge3.addLane(1, speed=13.89, length=100)
    edge3.setLighting("invalid_lighting")
    self.assertFalse(self.converter.validate_road_lighting(net))

def test_validate_road_traffic(self):
    """Test road traffic validation"""
    # Create a simple network with valid road traffic
    net = sumolib.net.Net()
    
    # Create nodes
    node1 = net.addNode("node1", x=0, y=0)
    node2 = net.addNode("node2", x=100, y=0)
    node3 = net.addNode("node3", x=200, y=0)
    
    # Create edges with proper traffic
    edge1 = net.addEdge("edge1", node1, node2, numLanes=2)
    edge2 = net.addEdge("edge2", node2, node3, numLanes=2)
    
    # Add lane connections with proper traffic
    edge1.addLane(0, speed=13.89, length=100)
    edge1.addLane(1, speed=13.89, length=100)
    edge2.addLane(0, speed=13.89, length=100)
    edge2.addLane(1, speed=13.89, length=100)
    
    # Add road traffic
    edge1.setTraffic("light")
    edge2.setTraffic("light")
    
    # Validate road traffic
    self.assertTrue(self.converter.validate_road_traffic(net))
    
    # Test with invalid traffic
    edge3 = net.addEdge("edge3", node3, net.addNode("node4", x=300, y=0), numLanes=2)
    edge3.addLane(0, speed=13.89, length=100)
    edge3.addLane(1, speed=13.89, length=100)
    edge3.setTraffic("invalid_traffic")
    self.assertFalse(self.converter.validate_road_traffic(net))

def test_validate_road_emergency(self):
    """Test road emergency validation"""
    # Create a simple network with valid road emergency
    net = sumolib.net.Net()
    
    # Create nodes
    node1 = net.addNode("node1", x=0, y=0)
    node2 = net.addNode("node2", x=100, y=0)
    node3 = net.addNode("node3", x=200, y=0)
    
    # Create edges with proper emergency
    edge1 = net.addEdge("edge1", node1, node2, numLanes=2)
    edge2 = net.addEdge("edge2", node2, node3, numLanes=2)
    
    # Add lane connections with proper emergency
    edge1.addLane(0, speed=13.89, length=100)
    edge1.addLane(1, speed=13.89, length=100)
    edge2.addLane(0, speed=13.89, length=100)
    edge2.addLane(1, speed=13.89, length=100)
    
    # Add road emergency
    edge1.setEmergency("none")
    edge2.setEmergency("none")
    
    # Validate road emergency
    self.assertTrue(self.converter.validate_road_emergency(net))
    
    # Test with invalid emergency
    edge3 = net.addEdge("edge3", node3, net.addNode("node4", x=300, y=0), numLanes=2)
    edge3.addLane(0, speed=13.89, length=100)
    edge3.addLane(1, speed=13.89, length=100)
    edge3.setEmergency("invalid_emergency")
    self.assertFalse(self.converter.validate_road_emergency(net))

def test_validate_road_construction(self):
    """Test road construction validation"""
    # Create a simple network with valid road construction
    net = sumolib.net.Net()
    
    # Create nodes
    node1 = net.addNode("node1", x=0, y=0)
    node2 = net.addNode("node2", x=100, y=0)
    node3 = net.addNode("node3", x=200, y=0)
    
    # Create edges with proper construction
    edge1 = net.addEdge("edge1", node1, node2, numLanes=2)
    edge2 = net.addEdge("edge2", node2, node3, numLanes=2)
    
    # Add lane connections with proper construction
    edge1.addLane(0, speed=13.89, length=100)
    edge1.addLane(1, speed=13.89, length=100)
    edge2.addLane(0, speed=13.89, length=100)
    edge2.addLane(1, speed=13.89, length=100)
    
    # Add road construction
    edge1.setConstruction("none")
    edge2.setConstruction("none")
    
    # Validate road construction
    self.assertTrue(self.converter.validate_road_construction(net))
    
    # Test with invalid construction
    edge3 = net.addEdge("edge3", node3, net.addNode("node4", x=300, y=0), numLanes=2)
    edge3.addLane(0, speed=13.89, length=100)
    edge3.addLane(1, speed=13.89, length=100)
    edge3.setConstruction("invalid_construction")
    self.assertFalse(self.converter.validate_road_construction(net))

def test_validate_road_incidents(self):
    """Test road incident validation"""
    # Create a simple network with valid road incidents
    net = sumolib.net.Net()
    
    # Create nodes
    node1 = net.addNode("node1", x=0, y=0)
    node2 = net.addNode("node2", x=100, y=0)
    node3 = net.addNode("node3", x=200, y=0)
    
    # Create edges with proper incidents
    edge1 = net.addEdge("edge1", node1, node2, numLanes=2)
    edge2 = net.addEdge("edge2", node2, node3, numLanes=2)
    
    # Add lane connections with proper incidents
    edge1.addLane(0, speed=13.89, length=100)
    edge1.addLane(1, speed=13.89, length=100)
    edge2.addLane(0, speed=13.89, length=100)
    edge2.addLane(1, speed=13.89, length=100)
    
    # Add road incidents
    edge1.setIncident("none")
    edge2.setIncident("none")
    
    # Validate road incidents
    self.assertTrue(self.converter.validate_road_incidents(net))
    
    # Test with invalid incident
    edge3 = net.addEdge("edge3", node3, net.addNode("node4", x=300, y=0), numLanes=2)
    edge3.addLane(0, speed=13.89, length=100)
    edge3.addLane(1, speed=13.89, length=100)
    edge3.setIncident("invalid_incident")
    self.assertFalse(self.converter.validate_road_incidents(net))

def test_validate_road_weather_conditions(self):
    """Test road weather conditions validation"""
    # Create a simple network with valid road weather conditions
    net = sumolib.net.Net()
    
    # Create nodes
    node1 = net.addNode("node1", x=0, y=0)
    node2 = net.addNode("node2", x=100, y=0)
    node3 = net.addNode("node3", x=200, y=0)
    
    # Create edges with proper weather conditions
    edge1 = net.addEdge("edge1", node1, node2, numLanes=2)
    edge2 = net.addEdge("edge2", node2, node3, numLanes=2)
    
    # Add lane connections with proper weather conditions
    edge1.addLane(0, speed=13.89, length=100)
    edge1.addLane(1, speed=13.89, length=100)
    edge2.addLane(0, speed=13.89, length=100)
    edge2.addLane(1, speed=13.89, length=100)
    
    # Add road weather conditions
    edge1.setWeatherConditions("clear")
    edge2.setWeatherConditions("clear")
    
    # Validate road weather conditions
    self.assertTrue(self.converter.validate_road_weather_conditions(net))
    
    # Test with invalid weather conditions
    edge3 = net.addEdge("edge3", node3, net.addNode("node4", x=300, y=0), numLanes=2)
    edge3.addLane(0, speed=13.89, length=100)
    edge3.addLane(1, speed=13.89, length=100)
    edge3.setWeatherConditions("invalid_weather_conditions")
    self.assertFalse(self.converter.validate_road_weather_conditions(net)) 