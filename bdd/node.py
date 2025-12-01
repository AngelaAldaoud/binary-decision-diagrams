"""
BDD Node Implementation
Represents a node in a Binary Decision Diagram
"""

class BDDNode:
    """
    Represents a node in a Binary Decision Diagram.
    
    A node can be either:
    - A terminal node (leaf) with a boolean value
    - An internal node with a variable and two children (low/high)
    """
    
    # Class variable for generating unique IDs
    _id_counter = 0
    
    def __init__(self, label, low=None, high=None, is_terminal=False, value=None):
        """
        Initialize a BDD node.
        
        Args:
            label: Variable name (e.g., 'p', 'q', 'r') or terminal value ('T', 'F')
            low: Child node when variable is False (dotted edge)
            high: Child node when variable is True (solid edge)
            is_terminal: True if this is a leaf node
            value: Boolean value if terminal node (True/False)
        """
        self.id = BDDNode._id_counter
        BDDNode._id_counter += 1
        
        self.label = label
        self.low = low          # False edge (dotted)
        self.high = high        # True edge (solid)
        self.is_terminal = is_terminal
        self.value = value
    
    def __repr__(self):
        """String representation for debugging."""
        if self.is_terminal:
            return f"Terminal({self.value})"
        return f"Node(id={self.id}, label={self.label}, low={self.low.id if self.low else None}, high={self.high.id if self.high else None})"
    
    def __str__(self):
        """User-friendly string representation."""
        if self.is_terminal:
            return f"[{self.label}]"
        return f"({self.label})"
    
    def __hash__(self):
        """
        Hash function for node comparison.
        Two nodes are identical if they have same label and same children.
        This allows nodes to be used in sets and dictionaries. It creates a unique number (hash) based on the node's content.
        Why it matters: In BDD algorithms, we need to quickly check if we've already created a node with the same structure. Hash functions make this fast.
        """
        if self.is_terminal:
            return hash(('terminal', self.value))
        return hash((self.label, id(self.low), id(self.high)))
    
    def __eq__(self, other):
        """
        Equality check for nodes.
        Used in reduction algorithm to identify duplicate nodes.

        Logic:

            If comparing with non-BDDNode → False
            If both are terminals → equal if same value (both True or both False)
            If only one is terminal → False
            If both are variables → equal if same label and same children

            Why it matters: BDD reduction algorithms need to merge duplicate nodes. This tells us when nodes are duplicates.

        """
        if not isinstance(other, BDDNode):
            return False
        
        if self.is_terminal and other.is_terminal:
            return self.value == other.value
        
        if self.is_terminal or other.is_terminal:
            return False
        
        return (self.label == other.label and 
                self.low == other.low and 
                self.high == other.high)
    
    @staticmethod
    def create_terminal(value):
        """
        Factory method to create terminal nodes.
        
        Args:
            value: True or False
            
        Returns:
            BDDNode representing terminal T or F
        """


        """
        Why use this instead of calling __init__ directly?

            Cleaner, more readable code
            Ensures terminals are created correctly
            Enforces the pattern (label='T'/'F', is_terminal=True)
        """
        label = 'T' if value else 'F'
        return BDDNode(label=label, is_terminal=True, value=value)
    
    @staticmethod
    def create_variable(label, low, high):
        """
        Factory method to create variable nodes.
        
        Args:
            label: Variable name (e.g., 'p', 'q', 'r')
            low: Child when variable is False
            high: Child when variable is True
            
        Returns:
            BDDNode representing a variable
        """
        return BDDNode(label=label, low=low, high=high, is_terminal=False)
    
    def is_redundant(self):
        """
        Check if node is redundant (both edges point to same child).
        Used in reduction algorithm (Step 1).
        
        Returns:
            True if low and high point to same node

        This checks if a node is **redundant** - meaning both its False and True edges go to the same place.
        Both paths lead to True, so this node is pointless - we can skip it!

        """
        return not self.is_terminal and self.low == self.high

"""
# Create singleton terminal nodes to reuse
These create two global constants - one True terminal and one False terminal.
Why? In a BDD, there should only be ONE terminal True node and ONE terminal False node that everyone shares. This is more memory-efficient and follows BDD principles.
"""
TERMINAL_TRUE = BDDNode.create_terminal(True)
TERMINAL_FALSE = BDDNode.create_terminal(False)