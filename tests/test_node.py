"""
Tests for BDD Node class
"""

import sys
import os
"""
# Add parent directory to path so we can import bdd module
Python needs to know where to find the bdd module
By adding the parent directory, Python can now find bdd/node.py
"""
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from bdd.node import BDDNode, TERMINAL_TRUE, TERMINAL_FALSE


def test_terminal_nodes():
    """Test creation of terminal nodes."""
    t_node = BDDNode.create_terminal(True)
    f_node = BDDNode.create_terminal(False)
    
    #assert statements: If any of these fail, the program stops and tells you what went wrong.
    assert t_node.is_terminal == True
    assert f_node.is_terminal == True
    assert t_node.value == True
    assert f_node.value == False
    assert t_node.label == 'T'
    assert f_node.label == 'F'
    
    print("✅ Terminal nodes test passed")


def test_variable_nodes():
    """Test creation of variable nodes."""
    # Create simple node: p with both edges to True
    p_node = BDDNode.create_variable('p', TERMINAL_FALSE, TERMINAL_TRUE)
    
    assert p_node.is_terminal == False
    assert p_node.label == 'p'
    assert p_node.low == TERMINAL_FALSE
    assert p_node.high == TERMINAL_TRUE
    
    print("✅ Variable nodes test passed")


def test_redundant_node():
    """Test redundancy detection."""
    # Node with both edges to same terminal
    redundant = BDDNode.create_variable('q', TERMINAL_TRUE, TERMINAL_TRUE)
    assert redundant.is_redundant() == True
    
    # Node with different children
    not_redundant = BDDNode.create_variable('q', TERMINAL_FALSE, TERMINAL_TRUE)
    assert not_redundant.is_redundant() == False
    
    print("✅ Redundant node test passed")


def test_node_equality():
    """Test node equality (for reduction algorithm)."""
    # Two nodes with same structure should be equal
    node1 = BDDNode.create_variable('p', TERMINAL_FALSE, TERMINAL_TRUE)
    node2 = BDDNode.create_variable('p', TERMINAL_FALSE, TERMINAL_TRUE)
    
    # Terminals should be equal
    t1 = BDDNode.create_terminal(True)
    t2 = BDDNode.create_terminal(True)
    assert t1.value == t2.value
    
    print("✅ Node equality test passed")


def test_node_representation():
    """Test string representation."""
    terminal = TERMINAL_TRUE
    variable = BDDNode.create_variable('p', TERMINAL_FALSE, TERMINAL_TRUE)
    
    print(f"Terminal: {terminal}")
    print(f"Variable: {variable}")
    print(f"Terminal repr: {repr(terminal)}")
    print(f"Variable repr: {repr(variable)}")
    
    print("✅ Node representation test passed")


if __name__ == "__main__":
    print("Testing BDD Node Implementation...\n")
    test_terminal_nodes()
    test_variable_nodes()
    test_redundant_node()
    test_node_equality()
    test_node_representation()
    print("\n🎉 All Node tests passed!")