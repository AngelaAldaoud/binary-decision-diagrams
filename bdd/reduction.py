"""
BDD Reduction Algorithm
Implementation of Algorithm 5.3 from textbook (page 99)
"""

from typing import Dict, Set, Tuple
from bdd.node import BDDNode, TERMINAL_TRUE, TERMINAL_FALSE


class BDDReducer:
    """
    Implements the BDD reduction algorithm.
    
    Reduces a BDD by:
    1. Merging duplicate terminal nodes
    2. Removing redundant nodes (Step 1)
    3. Merging isomorphic sub-BDDs (Step 2)

    """
    
    def __init__(self):

        """
        unique_table: Hash table for detecting duplicate subtrees
            Key: Tuple of (label, low_child_id, high_child_id)
            Value: The canonical node with this structure
            Purpose: Implements Step 2 (merging isomorphic sub-BDDs)
        Terminal nodes: Canonical True/False terminals that everyone shares
        """
        # Hash table: (label, low_id, high_id) -> node
        # Used to detect isomorphic sub-BDDs (Step 2)
        self.unique_table: Dict[Tuple, BDDNode] = {}
        
        # Terminal nodes (always reuse these)
        self.terminal_true = TERMINAL_TRUE
        self.terminal_false = TERMINAL_FALSE
        
        # Statistics
        self.nodes_removed = 0
        self.nodes_merged = 0
    
    def reduce(self, root: BDDNode) -> BDDNode:
        """
        Reduce a BDD according to Algorithm 5.3.
        
        Args:
            root: Root node of BDD to reduce
            
        Returns:
            Root node of reduced BDD
        """
        # Reset state
        self.unique_table.clear()
        self.nodes_removed = 0
        self.nodes_merged = 0
        
        # Step 0: Initialize unique table with terminals
        self.unique_table[('T', None, None)] = self.terminal_true
        self.unique_table[('F', None, None)] = self.terminal_false
        
        # Perform reduction
        reduced_root = self._reduce_recursive(root)
        
        return reduced_root
    
    def _reduce_recursive(self, node: BDDNode) -> BDDNode:
        """
        Recursively reduce BDD from bottom-up.
        
        Args:
            node: Current node to reduce
            
        Returns:
            Reduced version of node (may be same node, new node, or merged node)
        """
        # Base case: terminal nodes
        if node.is_terminal:
            # Always use canonical terminals
            return self.terminal_true if node.value else self.terminal_false
        
        # Recursively reduce children first (bottom-up)
        reduced_low = self._reduce_recursive(node.low)
        reduced_high = self._reduce_recursive(node.high)
        
        # Step 1: Check if node is redundant
        # "If both outgoing edges point to the same node, delete this node"
        if reduced_low == reduced_high:
            self.nodes_removed += 1
            return reduced_low  # Skip this node, return child directly
        
        # Step 2: Check if isomorphic sub-BDD already exists
        # "If two nodes are roots of identical sub-BDDs, delete one"
        node_signature = (node.label, id(reduced_low), id(reduced_high))
        
        if node_signature in self.unique_table:
            # Found identical sub-BDD - reuse existing node
            self.nodes_merged += 1
            return self.unique_table[node_signature]
        
        # Create new reduced node
        reduced_node = BDDNode.create_variable(node.label, reduced_low, reduced_high)
        
        # Add to unique table
        self.unique_table[node_signature] = reduced_node
        
        return reduced_node
    
    def get_statistics(self) -> Dict[str, int]:
        """Get reduction statistics."""
        return {
            'nodes_removed': self.nodes_removed,
            'nodes_merged': self.nodes_merged,
            'total_reduced': self.nodes_removed + self.nodes_merged
        }


def reduce_bdd(root: BDDNode) -> BDDNode:
    """
    Convenience function to reduce a BDD.
    
    Args:
        root: Root node of BDD to reduce
        
    Returns:
        Root node of reduced BDD
    """
    reducer = BDDReducer()
    return reducer.reduce(root)