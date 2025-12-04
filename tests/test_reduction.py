"""
Tests for BDD Reduction Algorithm
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from bdd.diagram import BDD, create_bdd_from_string
from bdd.reduction import BDDReducer, reduce_bdd
from bdd.formula import FormulaParser
from bdd.truth_table import Interpretation


def test_reduce_simple():
    """Test reduction on simple formula."""
    bdd = create_bdd_from_string("p")
    
    print("\n" + "="*60)
    print("Testing: p")
    print(f"Before reduction: {bdd.count_nodes()} nodes")
    
    stats = bdd.reduce()
    
    print(f"After reduction: {bdd.count_nodes()} nodes")
    print(f"Statistics: {stats}")
    
    # Should still work correctly
    assert bdd.evaluate(Interpretation({'p': True})) == True
    assert bdd.evaluate(Interpretation({'p': False})) == False
    
    print("✅ Simple reduction test passed")


def test_reduce_textbook_example():
    """Test reduction on p ∨ (q ∧ r) - Example from textbook."""
    formula = FormulaParser.parse_formula("p | (q & r)")
    bdd = BDD(formula, variable_order=['p', 'q', 'r'])
    
    print("\n" + "="*60)
    print("Testing: p ∨ (q ∧ r)")
    print(f"Before reduction: {bdd.count_nodes()} nodes")
    
    # Verify unreduced BDD works
    assert bdd.evaluate(Interpretation({'p': True, 'q': False, 'r': False})) == True
    assert bdd.evaluate(Interpretation({'p': False, 'q': True, 'r': False})) == False
    assert bdd.evaluate(Interpretation({'p': False, 'q': True, 'r': True})) == True
    
    # Reduce
    stats = bdd.reduce()
    
    print(f"After reduction: {bdd.count_nodes()} nodes")
    print(f"Nodes removed: {stats['nodes_removed']}")
    print(f"Nodes merged: {stats['nodes_merged']}")
    print(f"Total reduction: {stats['total_reduced']}")
    
    # Verify reduced BDD still works correctly
    assert bdd.evaluate(Interpretation({'p': True, 'q': False, 'r': False})) == True
    assert bdd.evaluate(Interpretation({'p': False, 'q': True, 'r': False})) == False
    assert bdd.evaluate(Interpretation({'p': False, 'q': True, 'r': True})) == True
    
    # Should be reduced now
    assert bdd.is_reduced() == True
    
    # From textbook: reduced BDD should have 4 nodes (see Fig 5.3, page 100)
    # Root (p), left child (q), one (r) node, and 2 terminals
    assert bdd.count_nodes() <= 5  # Should be significantly smaller than 9
    
    print("✅ Textbook example reduction test passed")


def test_reduce_tautology():
    """Test reduction on tautology: p ∨ ¬p."""
    bdd = create_bdd_from_string("p | ~p")
    
    print("\n" + "="*60)
    print("Testing: p ∨ ¬p (tautology)")
    print(f"Before reduction: {bdd.count_nodes()} nodes")
    
    stats = bdd.reduce()
    
    print(f"After reduction: {bdd.count_nodes()} nodes")
    print(f"Statistics: {stats}")
    
    # Tautology should reduce to single TRUE terminal
    assert bdd.count_nodes() == 1
    assert bdd.root.is_terminal == True
    assert bdd.root.value == True
    
    # Should still evaluate correctly
    assert bdd.evaluate(Interpretation({'p': True})) == True
    assert bdd.evaluate(Interpretation({'p': False})) == True
    
    print("✅ Tautology reduction test passed")


def test_reduce_contradiction():
    """Test reduction on contradiction: p ∧ ¬p."""
    bdd = create_bdd_from_string("p & ~p")
    
    print("\n" + "="*60)
    print("Testing: p ∧ ¬p (contradiction)")
    print(f"Before reduction: {bdd.count_nodes()} nodes")
    
    stats = bdd.reduce()
    
    print(f"After reduction: {bdd.count_nodes()} nodes")
    print(f"Statistics: {stats}")
    
    # Contradiction should reduce to single FALSE terminal
    assert bdd.count_nodes() == 1
    assert bdd.root.is_terminal == True
    assert bdd.root.value == False
    
    # Should still evaluate correctly
    assert bdd.evaluate(Interpretation({'p': True})) == False
    assert bdd.evaluate(Interpretation({'p': False})) == False
    
    print("✅ Contradiction reduction test passed")


def test_reduction_preserves_semantics():
    """Test that reduction preserves the truth table."""
    formula_str = "p | (q & r)"
    
    # Create two BDDs - one we'll reduce, one we'll keep unreduced
    bdd_reduced = create_bdd_from_string(formula_str)
    bdd_unreduced = create_bdd_from_string(formula_str)
    
    # Reduce one
    bdd_reduced.reduce()
    
    print("\n" + "="*60)
    print("Testing semantics preservation")
    print(f"Unreduced: {bdd_unreduced.count_nodes()} nodes")
    print(f"Reduced: {bdd_reduced.count_nodes()} nodes")
    
    # Test all 8 interpretations
    from bdd.truth_table import TruthTable
    table = TruthTable(['p', 'q', 'r'])
    
    mismatches = 0
    for interp in table.generate_all_interpretations():
        result_unreduced = bdd_unreduced.evaluate(interp)
        result_reduced = bdd_reduced.evaluate(interp)
        
        if result_unreduced != result_reduced:
            print(f"  ❌ Mismatch at {interp}: unreduced={result_unreduced}, reduced={result_reduced}")
            mismatches += 1
    
    assert mismatches == 0, f"Found {mismatches} mismatches!"
    
    print("✅ Semantics preservation test passed")


def test_is_reduced_check():
    """Test the is_reduced() method."""
    bdd = create_bdd_from_string("p | (q & r)")
    
    print("\n" + "="*60)
    print("Testing is_reduced() check")
    
    # Before reduction
    print(f"Before reduction: is_reduced() = {bdd.is_reduced()}")
    # Note: might already be reduced due to terminal merging
    
    # After reduction
    bdd.reduce()
    print(f"After reduction: is_reduced() = {bdd.is_reduced()}")
    
    assert bdd.is_reduced() == True
    
    print("✅ is_reduced() check test passed")


def test_complex_formula():
    """Test reduction on more complex formula."""
    # (p ∧ q) ∨ (p ∧ r)
    bdd = create_bdd_from_string("(p & q) | (p & r)")
    
    print("\n" + "="*60)
    print("Testing: (p ∧ q) ∨ (p ∧ r)")
    print(f"Before reduction: {bdd.count_nodes()} nodes")
    
    stats = bdd.reduce()
    
    print(f"After reduction: {bdd.count_nodes()} nodes")
    print(f"Reduction statistics: {stats}")
    
    # Test some interpretations
    assert bdd.evaluate(Interpretation({'p': True, 'q': True, 'r': False})) == True
    assert bdd.evaluate(Interpretation({'p': True, 'q': False, 'r': True})) == True
    assert bdd.evaluate(Interpretation({'p': False, 'q': True, 'r': True})) == False
    
    assert bdd.is_reduced() == True
    
    print("✅ Complex formula reduction test passed")


def test_xor_formula():
    """Test XOR formula from textbook: p ⊕ q ⊕ r."""
    # XOR: (p | q | r) & ~(p & q) & ~(p & r) & ~(q & r)
    # Or simpler: odd number of true variables
    
    # We'll build: (p & ~q & ~r) | (~p & q & ~r) | (~p & ~q & r) | (p & q & r)
    formula_str = "(p & ~q & ~r) | (~p & q & ~r) | (~p & ~q & r) | (p & q & r)"
    
    bdd = create_bdd_from_string(formula_str, variable_order=['p', 'q', 'r'])
    
    print("\n" + "="*60)
    print("Testing: p ⊕ q ⊕ r")
    print(f"Before reduction: {bdd.count_nodes()} nodes")
    
    stats = bdd.reduce()
    
    print(f"After reduction: {bdd.count_nodes()} nodes")
    print(f"Statistics: {stats}")
    
    # Verify XOR behavior (odd number of Trues)
    assert bdd.evaluate(Interpretation({'p': True, 'q': True, 'r': True})) == True   # 3 trues (odd)
    assert bdd.evaluate(Interpretation({'p': True, 'q': True, 'r': False})) == False # 2 trues (even)
    assert bdd.evaluate(Interpretation({'p': True, 'q': False, 'r': True})) == False # 2 trues (even)
    assert bdd.evaluate(Interpretation({'p': False, 'q': True, 'r': True})) == False # 2 trues (even)
    assert bdd.evaluate(Interpretation({'p': True, 'q': False, 'r': False})) == True  # 1 true (odd)
    
    print("✅ XOR formula reduction test passed")


if __name__ == "__main__":
    print("Testing BDD Reduction Algorithm")
    print("="*60)
    
    test_reduce_simple()
    test_reduce_textbook_example()
    test_reduce_tautology()
    test_reduce_contradiction()
    test_reduction_preserves_semantics()
    test_is_reduced_check()
    test_complex_formula()
    test_xor_formula()
    
    print("\n" + "="*60)
    print("🎉 All BDD Reduction tests passed!")