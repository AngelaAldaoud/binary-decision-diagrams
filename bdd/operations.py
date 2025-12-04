"""
BDD Operations
Implementation of logical operations on BDDs using Shannon Expansion
"""

from typing import Dict, Tuple
from bdd.node import BDDNode, TERMINAL_TRUE, TERMINAL_FALSE
from bdd.diagram import BDD
from bdd.formula import Formula


class BDDOperations:
    """
    Implements logical operations on BDDs.
    
    Uses Shannon Expansion:
    f = x·f[x←1] ∨ ¬x·f[x←0]
    
    Where f[x←v] means f with x replaced by value v.
    """
    
    def __init__(self):
        # Cache for apply operation: (op, node1_id, node2_id) -> result_node
        self.apply_cache: Dict[Tuple, BDDNode] = {}
        
        # Unique table for creating new nodes
        self.unique_table: Dict[Tuple, BDDNode] = {}
        
        # Initialize with terminals
        self.unique_table[('T', None, None)] = TERMINAL_TRUE
        self.unique_table[('F', None, None)] = TERMINAL_FALSE
    
    def apply(self, op: str, node1: BDDNode, node2: BDDNode) -> BDDNode:
        """
        Apply binary operation to two BDD nodes.
        
        Args:
            op: Operation ('AND', 'OR', 'XOR', 'IMPLIES', 'IFF')
            node1: First BDD node
            node2: Second BDD node
            
        Returns:
            Resulting BDD node
        """
        # Check cache
        cache_key = (op, id(node1), id(node2))
        if cache_key in self.apply_cache:
            return self.apply_cache[cache_key]
        
        # Base cases: both are terminals
        if node1.is_terminal and node2.is_terminal:
            result = self._apply_terminal(op, node1.value, node2.value)
            result_node = TERMINAL_TRUE if result else TERMINAL_FALSE
            self.apply_cache[cache_key] = result_node
            return result_node
        
        # Get variable ordering (process lower variable first)
        if node1.is_terminal:
            var = node2.label
            node1_low = node1
            node1_high = node1
            node2_low = node2.low
            node2_high = node2.high
        elif node2.is_terminal:
            var = node1.label
            node1_low = node1.low
            node1_high = node1.high
            node2_low = node2
            node2_high = node2
        else:
            # Both are variable nodes - use lexicographic order
            if node1.label <= node2.label:
                var = node1.label
                node1_low = node1.low
                node1_high = node1.high
                
                if node1.label == node2.label:
                    node2_low = node2.low
                    node2_high = node2.high
                else:
                    node2_low = node2
                    node2_high = node2
            else:
                var = node2.label
                node1_low = node1
                node1_high = node1
                node2_low = node2.low
                node2_high = node2.high
        
        # Shannon Expansion: recursively apply to low and high branches
        low_result = self.apply(op, node1_low, node2_low)
        high_result = self.apply(op, node1_high, node2_high)
        
        # Check for redundancy (both branches same)
        if low_result == high_result:
            self.apply_cache[cache_key] = low_result
            return low_result
        
        # Create new node (check unique table first)
        result_node = self._make_node(var, low_result, high_result)
        
        # Cache and return
        self.apply_cache[cache_key] = result_node
        return result_node
    
    def _apply_terminal(self, op: str, val1: bool, val2: bool) -> bool:
        """Apply operation to two boolean values."""
        if op == 'AND':
            return val1 and val2
        elif op == 'OR':
            return val1 or val2
        elif op == 'XOR':
            return val1 != val2
        elif op == 'IMPLIES':
            return (not val1) or val2
        elif op == 'IFF':
            return val1 == val2
        else:
            raise ValueError(f"Unknown operation: {op}")
    
    def _make_node(self, label: str, low: BDDNode, high: BDDNode) -> BDDNode:
        """
        Create a node, reusing existing nodes if possible (unique table).
        
        Args:
            label: Variable name
            low: Low child
            high: High child
            
        Returns:
            Node (either new or existing)
        """
        # Check unique table
        signature = (label, id(low), id(high))
        if signature in self.unique_table:
            return self.unique_table[signature]
        
        # Create new node
        new_node = BDDNode.create_variable(label, low, high)
        self.unique_table[signature] = new_node
        
        return new_node
    
    def apply_not(self, node: BDDNode) -> BDDNode:
        """
        Apply NOT operation to a BDD node.
        
        Args:
            node: BDD node to negate
            
        Returns:
            Negated BDD node
        """
        # Base case: terminal
        if node.is_terminal:
            return TERMINAL_TRUE if not node.value else TERMINAL_FALSE
        
        # Recursive case: negate both branches
        low_result = self.apply_not(node.low)
        high_result = self.apply_not(node.high)
        
        return self._make_node(node.label, low_result, high_result)
    
    def clear_cache(self):
        """Clear operation cache (for new operations)."""
        self.apply_cache.clear()


def bdd_and(bdd1: BDD, bdd2: BDD) -> BDD:
    """
    Compute BDD1 ∧ BDD2.
    
    Args:
        bdd1: First BDD
        bdd2: Second BDD
        
    Returns:
        New BDD representing conjunction
    """
    ops = BDDOperations()
    result_root = ops.apply('AND', bdd1.root, bdd2.root)
    
    # Create new BDD with result
    result_bdd = BDD()
    result_bdd.root = result_root
    result_bdd.variable_order = sorted(set(bdd1.variable_order + bdd2.variable_order))
    result_bdd.formula = None  # Combined formula
    
    return result_bdd


def bdd_or(bdd1: BDD, bdd2: BDD) -> BDD:
    """
    Compute BDD1 ∨ BDD2.
    
    Args:
        bdd1: First BDD
        bdd2: Second BDD
        
    Returns:
        New BDD representing disjunction
    """
    ops = BDDOperations()
    result_root = ops.apply('OR', bdd1.root, bdd2.root)
    
    result_bdd = BDD()
    result_bdd.root = result_root
    result_bdd.variable_order = sorted(set(bdd1.variable_order + bdd2.variable_order))
    result_bdd.formula = None
    
    return result_bdd


def bdd_not(bdd: BDD) -> BDD:
    """
    Compute ¬BDD.
    
    Args:
        bdd: BDD to negate
        
    Returns:
        New BDD representing negation
    """
    ops = BDDOperations()
    result_root = ops.apply_not(bdd.root)
    
    result_bdd = BDD()
    result_bdd.root = result_root
    result_bdd.variable_order = bdd.variable_order.copy()
    result_bdd.formula = None
    
    return result_bdd


def bdd_xor(bdd1: BDD, bdd2: BDD) -> BDD:
    """Compute BDD1 ⊕ BDD2."""
    ops = BDDOperations()
    result_root = ops.apply('XOR', bdd1.root, bdd2.root)
    
    result_bdd = BDD()
    result_bdd.root = result_root
    result_bdd.variable_order = sorted(set(bdd1.variable_order + bdd2.variable_order))
    result_bdd.formula = None
    
    return result_bdd


def bdd_implies(bdd1: BDD, bdd2: BDD) -> BDD:
    """Compute BDD1 → BDD2."""
    ops = BDDOperations()
    result_root = ops.apply('IMPLIES', bdd1.root, bdd2.root)
    
    result_bdd = BDD()
    result_bdd.root = result_root
    result_bdd.variable_order = sorted(set(bdd1.variable_order + bdd2.variable_order))
    result_bdd.formula = None
    
    return result_bdd


def bdd_iff(bdd1: BDD, bdd2: BDD) -> BDD:
    """Compute BDD1 ↔ BDD2."""
    ops = BDDOperations()
    result_root = ops.apply('IFF', bdd1.root, bdd2.root)
    
    result_bdd = BDD()
    result_bdd.root = result_root
    result_bdd.variable_order = sorted(set(bdd1.variable_order + bdd2.variable_order))
    result_bdd.formula = None
    
    return result_bdd


def are_equivalent(bdd1: BDD, bdd2: BDD) -> bool:
    """
    Check if two BDDs are logically equivalent.
    
    Two reduced BDDs are equivalent iff they have identical structure.
    
    Args:
        bdd1: First BDD
        bdd2: Second BDD
        
    Returns:
        True if BDDs represent the same boolean function
    """
    # Ensure both are reduced
    if not bdd1.is_reduced():
        bdd1_copy = BDD(bdd1.formula, bdd1.variable_order)
        bdd1_copy.root = bdd1.root
        bdd1_copy.reduce()
        bdd1 = bdd1_copy
    
    if not bdd2.is_reduced():
        bdd2_copy = BDD(bdd2.formula, bdd2.variable_order)
        bdd2_copy.root = bdd2.root
        bdd2_copy.reduce()
        bdd2 = bdd2_copy
    
    # Compare structures
    return _nodes_equal(bdd1.root, bdd2.root)


def _nodes_equal(node1: BDDNode, node2: BDDNode) -> bool:
    """Check if two nodes represent the same function."""
    # Both terminals
    if node1.is_terminal and node2.is_terminal:
        return node1.value == node2.value
    
    # One terminal, one not
    if node1.is_terminal or node2.is_terminal:
        return False
    
    # Both variables - check label and children
    if node1.label != node2.label:
        return False
    
    return (_nodes_equal(node1.low, node2.low) and 
            _nodes_equal(node1.high, node2.high))