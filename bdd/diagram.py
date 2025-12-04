"""
BDD Diagram Implementation
Main class for constructing and manipulating Binary Decision Diagrams
A BDD is a data structure that represents a boolean function as a directed acyclic graph (DAG).
"""

from typing import List, Set, Dict, Optional, Tuple
from bdd.node import BDDNode, TERMINAL_TRUE, TERMINAL_FALSE
from bdd.formula import Formula, Variable, Not, And, Or, Implies, Iff
from bdd.truth_table import Interpretation, TruthTable


class BDD:
    """
    Binary Decision Diagram
    
    Represents a formula as a directed acyclic graph where:
    - Each internal node represents a variable decision
    - Each leaf represents a boolean value (T or F)
    - Edges represent variable assignments (solid = True, dotted = False)
    """
    
    def __init__(self, formula: Formula = None, variable_order: List[str] = None):
        """
        Initialize a BDD.
        
        Args:
            formula: The propositional logic formula to represent
            variable_order: Ordered list of variables (if None, derived from formula)
            CRITICAL: Variable order affects BDD size!
            # Example: p ∨ (q ∧ r)
                # Order ['p', 'q', 'r'] might create smaller BDD than ['q', 'r', 'p']
        """
        self.formula = formula
        self.root = None
        self.nodes = []  # All nodes in the BDD
        
        # Determine variable ordering
        if formula:
            all_vars = sorted(formula.get_variables())
            self.variable_order = variable_order if variable_order else all_vars
        else:
            self.variable_order = variable_order if variable_order else []
        
        # Build the BDD if formula provided
        if formula:
            self.root = self._build_from_formula()
    
    def _build_from_formula(self) -> BDDNode:
        """
        Build initial BDD from formula.
        Creates a complete binary tree.
        
        Returns:
            Root node of the constructed BDD
        """

        """
        Case 1: No variables (constant formula)
        Example: True ∧ False or just True
        Evaluate immediately with empty interpretation
        Return appropriate terminal
        """
        if not self.variable_order:
            # No variables - formula is constant
            # Evaluate with empty interpretation
            result = self.formula.evaluate(Interpretation({}))
            return TERMINAL_TRUE if result else TERMINAL_FALSE
        
        """
        Case 2: Has variables
        Start building from level 0 (first variable)
        Start with empty interpretation
        Call recursive tree builder
        """
        # Build complete binary tree
        return self._build_tree(0, Interpretation({}))
    
    def _build_tree(self, level: int, partial_interp: Interpretation) -> BDDNode:
        """
        Recursively build the BDD tree.
        
        Args:
            level: Current level in the tree (variable index)
            partial_interp: Partial interpretation built so far
            
        Returns:
            Root node of the subtree
        """
        # Base case: all variables assigned
        if level >= len(self.variable_order):
            # Evaluate formula with complete interpretation
            result = self.formula.evaluate(partial_interp)
            return TERMINAL_TRUE if result else TERMINAL_FALSE
        
        # Get current variable
        current_var = self.variable_order[level]
        
        # Create interpretation with current variable = False
        interp_false = partial_interp.copy()
        interp_false.assign(current_var, False)
        
        # Create interpretation with current variable = True
        interp_true = partial_interp.copy()
        interp_true.assign(current_var, True)
        
        # Recursively build left (False) and right (True) subtrees
        low_child = self._build_tree(level + 1, interp_false)
        high_child = self._build_tree(level + 1, interp_true)
        
        # Create node for current variable
        node = BDDNode.create_variable(current_var, low_child, high_child)
        self.nodes.append(node)
        
        """
               Call: _build_tree(0, {})
         Current var: 'p'

         Build low child (p=False):
           Call: _build_tree(1, {p: False})
             Current var: 'q'

             Build low child (p=False, q=False):
               Call: _build_tree(2, {p: False, q: False})
                 Base case! Evaluate: False ∧ False = False
                 Return: TERMINAL_FALSE

             Build high child (p=False, q=True):
               Call: _build_tree(2, {p: False, q: True})
                 Base case! Evaluate: False ∧ True = False
                 Return: TERMINAL_FALSE

             Create node: q with low=F, high=F
             Return: q_node

         Build high child (p=True):
           Call: _build_tree(1, {p: True})
             Current var: 'q'

             Build low child (p=True, q=False):
               Call: _build_tree(2, {p: True, q: False})
                 Base case! Evaluate: True ∧ False = False
                 Return: TERMINAL_FALSE

             Build high child (p=True, q=True):
               Call: _build_tree(2, {p: True, q: True})
                 Base case! Evaluate: True ∧ True = True
                 Return: TERMINAL_TRUE

             Create node: q with low=F, high=T
             Return: q_node

         Create node: p with low=q_node1, high=q_node2
         Return: p_node
        """

        return node #Return the node** as root of this subtree
    
    def evaluate(self, interpretation: Interpretation) -> bool:
        """
        Evaluate the BDD under a given interpretation.
        
        Args:
            interpretation: Variable assignments
            
        Returns:
            Boolean result

        While not at a terminal:
        - Look up current variable's value in interpretation
        - If True, follow high edge (solid)
        - If False, follow low edge (dotted)

        **Example:** Evaluate p=True, q=True in p ∧ q BDD:
            Start at: p
              p=True → Follow high edge → q node
            At: q
              q=True → Follow high edge → T terminal
            Result: True
        """
        if not self.root:
            raise ValueError("BDD has no root node")
        
        current = self.root
        
        # Traverse the BDD following the interpretation
        while not current.is_terminal:
            var_value = interpretation.get(current.label)
            if var_value is None:
                raise ValueError(f"Variable {current.label} not assigned in interpretation")
            
            # Follow high edge if True, low edge if False
            current = current.high if var_value else current.low
        
        return current.value
    
    def is_satisfiable(self) -> bool:
        """
        Check if the BDD represents a satisfiable formula.
        
        Returns:
            True if there exists at least one path to TRUE terminal
        """
        return self._has_path_to(self.root, True)
    
    def is_valid(self) -> bool:
        """
        Check if the BDD represents a valid (tautology) formula - true under all interpretations..
        
        Returns:
            Root itself is TRUE terminal → tautology
            True if all paths lead to TRUE terminal
        """
        return self.root == TERMINAL_TRUE or not self._has_path_to(self.root, False)
    
    def _has_path_to(self, node: BDDNode, target_value: bool) -> bool:
        """
        Check if there's a path from node to a terminal with target_value.
        
        Args:
            node: Starting node
            target_value: Target terminal value (True or False)
            
        Returns:
            True if path exists
        """
        if node.is_terminal:
            return node.value == target_value
        
        # Check if either child has a path to target
        return (self._has_path_to(node.low, target_value) or 
                self._has_path_to(node.high, target_value))
    
    def count_nodes(self) -> int:
        """Count total number of nodes in BDD."""
        visited = set()
        return self._count_nodes_recursive(self.root, visited)
    
    def _count_nodes_recursive(self, node: BDDNode, visited: Set[int]) -> int:
        """
        Recursively count nodes, avoiding duplicates.
        **Counts unique nodes in the BDD.**
        **Why track visited?**
        - BDD is a DAG (Directed Acyclic Graph)
        - Multiple nodes might point to same child
        - Don't want to count the same node twice!

        """
        if node is None or node.id in visited:
            return 0
        
        visited.add(node.id)
        
        if node.is_terminal:
            return 1
        
        count = 1  # Current node
        count += self._count_nodes_recursive(node.low, visited)
        count += self._count_nodes_recursive(node.high, visited)
        
        return count
    
    def get_all_nodes(self) -> List[BDDNode]:
        """Get list of all unique nodes in BDD."""
        visited = set()
        nodes = []
        self._collect_nodes(self.root, visited, nodes)
        return nodes
    
    def _collect_nodes(self, node: BDDNode, visited: Set[int], nodes: List[BDDNode]):
        """Recursively collect all nodes."""
        if node is None or node.id in visited:
            return
        
        visited.add(node.id)
        nodes.append(node)
        
        if not node.is_terminal:
            self._collect_nodes(node.low, visited, nodes)
            self._collect_nodes(node.high, visited, nodes)
    
    def __repr__(self):
        """String representation."""
        node_count = self.count_nodes()
        return f"BDD(formula={self.formula}, nodes={node_count}, vars={self.variable_order})"
    
    def __str__(self):
        """User-friendly string representation."""
        return self.__repr__()
    
    def reduce(self):
        """
        Reduce this BDD using Algorithm 5.3.
        Modifies the BDD in-place.
        
        Returns:
            Statistics about the reduction
        """
        from bdd.reduction import BDDReducer
        
        if not self.root:
            return {'nodes_removed': 0, 'nodes_merged': 0, 'total_reduced': 0}
        
        # Count nodes before reduction
        nodes_before = self.count_nodes()
        
        # Perform reduction
        reducer = BDDReducer()
        self.root = reducer.reduce(self.root)
        
        # Count nodes after reduction
        nodes_after = self.count_nodes()
        
        # Get statistics
        stats = reducer.get_statistics()
        stats['nodes_before'] = nodes_before
        stats['nodes_after'] = nodes_after
        
        return stats
    
    def is_reduced(self) -> bool:
        """
        Check if BDD is in reduced form.
        
        Returns:
            True if BDD has no redundant nodes or isomorphic sub-BDDs
        """
        if not self.root:
            return True
        
        visited = set()
        unique_signatures = set()
        
        return self._check_reduced(self.root, visited, unique_signatures)
    
    def _check_reduced(self, node: BDDNode, visited: Set[int], 
                       unique_signatures: Set[Tuple]) -> bool:
        """Helper to check if BDD is reduced."""
        if node.id in visited:
            return True
        
        visited.add(node.id)
        
        if node.is_terminal:
            return True
        
        # Check Step 1: No redundant nodes
        if node.low == node.high:
            return False  # Found redundant node
        
        # Check Step 2: No duplicate sub-BDDs
        signature = (node.label, id(node.low), id(node.high))
        if signature in unique_signatures:
            return False  # Found duplicate sub-BDD
        
        unique_signatures.add(signature)
        
        # Recursively check children
        return (self._check_reduced(node.low, visited, unique_signatures) and
                self._check_reduced(node.high, visited, unique_signatures))


def create_bdd_from_string(formula_str: str, variable_order: List[str] = None) -> BDD:

    """
    Convenience function to create BDD from formula string.
    
    Args:
        formula_str: String representation of formula (e.g., "p ∨ (q ∧ r)")
        variable_order: Optional variable ordering
        
    Returns:
        Constructed BDD
    """
    from bdd.formula import FormulaParser
    formula = FormulaParser.parse_formula(formula_str)
    return BDD(formula, variable_order)


