"""
BDD Visualization
Renders BDDs as graphs using Graphviz
"""

from typing import Set
from bdd.node import BDDNode
from bdd.diagram import BDD

try:
    from graphviz import Digraph
    GRAPHVIZ_AVAILABLE = True
except ImportError:
    GRAPHVIZ_AVAILABLE = False
    print("Warning: graphviz not installed. Install with: pip install graphviz")


class BDDVisualizer:
    """
    Visualizes BDDs as directed graphs.
    
    Conventions:
    - Solid edges: True (high)
    - Dotted edges: False (low)
    - Rectangle nodes: Variables
    - Box nodes: Terminals
    """
    
    def __init__(self):
        self.visited = set()
    
    def visualize(self, bdd: BDD, filename: str = 'bdd', 
                  view: bool = True, format: str = 'png') -> str:
        """
        Visualize a BDD and save to file.
        
        Args:
            bdd: The BDD to visualize
            filename: Output filename (without extension)
            view: Whether to open the image after creation
            format: Output format ('png', 'pdf', 'svg')
            
        Returns:
            Path to generated file
        """
        if not GRAPHVIZ_AVAILABLE:
            raise ImportError("graphviz package not installed")
        
        # Create directed graph
        dot = Digraph(comment=f'BDD for {bdd.formula}')
        dot.attr(rankdir='TB')  # Top to bottom
        
        # Reset visited set
        self.visited.clear()
        
        # Build graph
        if bdd.root:
            self._add_node_to_graph(dot, bdd.root)
        
        # Render
        output_path = dot.render(filename, format=format, view=view, cleanup=True)
        
        return output_path
    
    def _add_node_to_graph(self, dot: Digraph, node: BDDNode):
        """Recursively add nodes and edges to graph."""
        if node.id in self.visited:
            return
        
        self.visited.add(node.id)
        node_id = str(node.id)
        
        if node.is_terminal:
            # Terminal node: box shape
            label = 'T' if node.value else 'F'
            color = 'green' if node.value else 'red'
            dot.node(node_id, label, shape='box', style='filled', 
                    fillcolor=color, fontcolor='white', fontsize='14')
        else:
            # Variable node: ellipse shape
            dot.node(node_id, node.label, shape='ellipse', 
                    style='filled', fillcolor='lightblue', fontsize='12')
            
            # Add edges
            # Low edge (False): dotted
            low_id = str(node.low.id)
            dot.edge(node_id, low_id, style='dotted', color='red', 
                    label='F', fontsize='10')
            
            # High edge (True): solid
            high_id = str(node.high.id)
            dot.edge(node_id, high_id, style='solid', color='green', 
                    label='T', fontsize='10')
            
            # Recursively add children
            self._add_node_to_graph(dot, node.low)
            self._add_node_to_graph(dot, node.high)
    
    def compare_bdds(self, bdd1: BDD, bdd2: BDD, 
                     filename: str = 'bdd_comparison',
                     labels: tuple = ('Before Reduction', 'After Reduction'),
                     view: bool = True) -> str:
        """
        Visualize two BDDs side-by-side for comparison.
        
        Args:
            bdd1: First BDD
            bdd2: Second BDD
            filename: Output filename
            labels: Labels for the two BDDs
            view: Whether to open the image
            
        Returns:
            Path to generated file
        """
        if not GRAPHVIZ_AVAILABLE:
            raise ImportError("graphviz package not installed")
        
        # Create graph with subgraphs
        dot = Digraph(comment='BDD Comparison')
        dot.attr(rankdir='TB')
        
        # First BDD
        with dot.subgraph(name='cluster_0') as c:
            c.attr(label=labels[0], fontsize='16')
            self.visited.clear()
            self._add_node_to_subgraph(c, bdd1.root, prefix='a_')
        
        # Second BDD
        with dot.subgraph(name='cluster_1') as c:
            c.attr(label=labels[1], fontsize='16')
            self.visited.clear()
            self._add_node_to_subgraph(c, bdd2.root, prefix='b_')
        
        # Render
        output_path = dot.render(filename, format='png', view=view, cleanup=True)
        
        return output_path
    
    def _add_node_to_subgraph(self, graph, node: BDDNode, prefix: str = ''):
        """Add nodes to a subgraph with prefix to avoid ID conflicts."""
        if node.id in self.visited:
            return
        
        self.visited.add(node.id)
        node_id = prefix + str(node.id)
        
        if node.is_terminal:
            label = 'T' if node.value else 'F'
            color = 'green' if node.value else 'red'
            graph.node(node_id, label, shape='box', style='filled', 
                      fillcolor=color, fontcolor='white', fontsize='14')
        else:
            graph.node(node_id, node.label, shape='ellipse', 
                      style='filled', fillcolor='lightblue', fontsize='12')
            
            low_id = prefix + str(node.low.id)
            graph.edge(node_id, low_id, style='dotted', color='red', 
                      label='F', fontsize='10')
            
            high_id = prefix + str(node.high.id)
            graph.edge(node_id, high_id, style='solid', color='green', 
                      label='T', fontsize='10')
            
            self._add_node_to_subgraph(graph, node.low, prefix)
            self._add_node_to_subgraph(graph, node.high, prefix)


def visualize_bdd(bdd: BDD, filename: str = 'bdd', view: bool = True) -> str:
    """
    Convenience function to visualize a BDD.
    
    Args:
        bdd: BDD to visualize
        filename: Output filename
        view: Whether to open the image
        
    Returns:
        Path to generated file
    """
    visualizer = BDDVisualizer()
    return visualizer.visualize(bdd, filename, view)


def compare_bdds(bdd_before: BDD, bdd_after: BDD, 
                 filename: str = 'comparison', view: bool = True) -> str:
    """
    Convenience function to compare two BDDs.
    
    Args:
        bdd_before: First BDD (typically unreduced)
        bdd_after: Second BDD (typically reduced)
        filename: Output filename
        view: Whether to open the image
        
    Returns:
        Path to generated file
    """
    visualizer = BDDVisualizer()
    return visualizer.compare_bdds(bdd_before, bdd_after, filename, view=view)