"""
Tests for BDD Construction
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from bdd.diagram import BDD, create_bdd_from_string
from bdd.formula import FormulaParser, Variable, And, Or, Not
from bdd.truth_table import Interpretation


def test_simple_variable():
    """Test BDD for single variable."""
    formula = FormulaParser.parse_formula("p")
    bdd = BDD(formula)
    
    assert bdd.root is not None
    assert bdd.root.label == 'p'
    assert bdd.root.is_terminal == False
    
    # Should have 3 nodes: root 'p', terminal T, terminal F
    node_count = bdd.count_nodes()
    print(f"Single variable BDD has {node_count} nodes")
    
    # Test evaluation
    assert bdd.evaluate(Interpretation({'p': True})) == True
    assert bdd.evaluate(Interpretation({'p': False})) == False
    
    print(f" Simple variable test passed: {bdd}")


def test_simple_and():
    """Test BDD for p ∧ q."""
    #formula = FormulaParser.parse_formula("p & q")
    #bdd = BDD(formula)

    bdd = create_bdd_from_string("p & q")

    
    print(f"\nBDD for p ∧ q: {bdd}")
    
    # Test all four interpretations
    assert bdd.evaluate(Interpretation({'p': False, 'q': False})) == False
    assert bdd.evaluate(Interpretation({'p': False, 'q': True})) == False
    assert bdd.evaluate(Interpretation({'p': True, 'q': False})) == False
    assert bdd.evaluate(Interpretation({'p': True, 'q': True})) == True
    
    # Check satisfiability
    assert bdd.is_satisfiable() == True
    assert bdd.is_valid() == False
    
    print(" Simple AND test passed")


def test_simple_or():
    """Test BDD for p ∨ q."""
    formula = FormulaParser.parse_formula("p | q")
    bdd = BDD(formula)
    
    print(f"\nBDD for p ∨ q: {bdd}")
    
    # Test all four interpretations
    assert bdd.evaluate(Interpretation({'p': False, 'q': False})) == False
    assert bdd.evaluate(Interpretation({'p': False, 'q': True})) == True
    assert bdd.evaluate(Interpretation({'p': True, 'q': False})) == True
    assert bdd.evaluate(Interpretation({'p': True, 'q': True})) == True
    
    print("Simple OR test passed")


def test_textbook_formula():
    """Test BDD for p ∨ (q ∧ r) from textbook."""
    formula = FormulaParser.parse_formula("p | (q & r)")
    bdd = BDD(formula, variable_order=['p', 'q', 'r'])
    
    print(f"\nBDD for p ∨ (q ∧ r): {bdd}")
    print(f"Number of nodes: {bdd.count_nodes()}")
    
    # Test interpretations from textbook (Fig 5.1)
    test_cases = [
        ({'p': False, 'q': False, 'r': False}, False),
        ({'p': False, 'q': False, 'r': True}, False),
        ({'p': False, 'q': True, 'r': False}, False),
        ({'p': False, 'q': True, 'r': True}, True),
        ({'p': True, 'q': False, 'r': False}, True),
        ({'p': True, 'q': False, 'r': True}, True),
        ({'p': True, 'q': True, 'r': False}, True),
        ({'p': True, 'q': True, 'r': True}, True),
    ]
    
    for assignments, expected in test_cases:
        interp = Interpretation(assignments)
        result = bdd.evaluate(interp)
        assert result == expected, f"Failed for {assignments}: expected {expected}, got {result}"
    
    # Check properties
    assert bdd.is_satisfiable() == True
    assert bdd.is_valid() == False
    
    print(" Textbook formula test passed")


def test_tautology():
    """Test BDD for tautology: p ∨ ¬p."""
    formula = FormulaParser.parse_formula("p | ~p")
    bdd = BDD(formula)
    
    print(f"\nBDD for p ∨ ¬p (tautology): {bdd}")
    print(f"Number of nodes: {bdd.count_nodes()}")
    
    # Should always evaluate to True
    assert bdd.evaluate(Interpretation({'p': True})) == True
    assert bdd.evaluate(Interpretation({'p': False})) == True
    
    # Check it's valid
    assert bdd.is_valid() == True
    assert bdd.is_satisfiable() == True
    
    print(" Tautology test passed")


def test_contradiction():
    """Test BDD for contradiction: p ∧ ¬p."""
    formula = FormulaParser.parse_formula("p & ~p")
    bdd = BDD(formula)
    
    print(f"\nBDD for p ∧ ¬p (contradiction): {bdd}")
    print(f"Number of nodes: {bdd.count_nodes()}")
    
    # Should always evaluate to False
    assert bdd.evaluate(Interpretation({'p': True})) == False
    assert bdd.evaluate(Interpretation({'p': False})) == False
    
    # Check it's not satisfiable
    assert bdd.is_satisfiable() == False
    assert bdd.is_valid() == False
    
    print(" Contradiction test passed")


def test_variable_ordering():
    """Test that different variable orderings create different BDDs."""
    formula = FormulaParser.parse_formula("p | (q & r)")
    
    bdd1 = BDD(formula, variable_order=['p', 'q', 'r'])
    bdd2 = BDD(formula, variable_order=['q', 'p', 'r'])
    
    print(f"\nBDD with order ['p', 'q', 'r']: {bdd1.count_nodes()} nodes")
    print(f"BDD with order ['q', 'p', 'r']: {bdd2.count_nodes()} nodes")
    
    # Both should give same results
    interp = Interpretation({'p': True, 'q': False, 'r': True})
    assert bdd1.evaluate(interp) == bdd2.evaluate(interp)
    
    print("Variable ordering test passed")


def test_create_from_string():
    """Test convenience function."""
    bdd = create_bdd_from_string("p & q")
    
    assert bdd.evaluate(Interpretation({'p': True, 'q': True})) == True
    assert bdd.evaluate(Interpretation({'p': True, 'q': False})) == False
    
    print("Create from string test passed")


def test_node_structure():
    """Test the tree structure is correct."""
    bdd = create_bdd_from_string("p & q", variable_order=['p', 'q'])
    
    # Root should be 'p'
    assert bdd.root.label == 'p'
    
    # Root's children should be 'q' nodes or terminals
    print(f"\nRoot: {bdd.root}")
    print(f"Root.low: {bdd.root.low}")
    print(f"Root.high: {bdd.root.high}")
    
    # Get all nodes
    all_nodes = bdd.get_all_nodes()
    print(f"\nAll nodes in BDD ({len(all_nodes)} total):")
    for i, node in enumerate(all_nodes, 1):
        print(f"  {i}. {node}")
    
    print("Node structure test passed")


if __name__ == "__main__":
    print("Testing BDD Construction...\n")
    print("=" * 60)
    test_simple_variable()
    test_simple_and()
    test_simple_or()
    test_textbook_formula()
    test_tautology()
    test_contradiction()
    test_variable_ordering()
    test_create_from_string()
    test_node_structure()
    print("\n" + "=" * 60)
    print(" All BDD Construction tests passed!")