"""
Tests for BDD Operations (Apply, Shannon Expansion, Equivalence)
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from bdd.diagram import BDD, create_bdd_from_string
from bdd.operations import *
from bdd.truth_table import Interpretation
from bdd.formula import FormulaParser


def test_bdd_and():
    """Test BDD AND operation."""
    print("\n" + "="*60)
    print("Test: BDD AND operation")
    
    # Create two simple BDDs: p and q
    bdd_p = create_bdd_from_string("p")
    bdd_q = create_bdd_from_string("q")
    
    # Compute p ∧ q
    bdd_result = bdd_and(bdd_p, bdd_q)
    
    print(f"p: {bdd_p.count_nodes()} nodes")
    print(f"q: {bdd_q.count_nodes()} nodes")
    print(f"p ∧ q: {bdd_result.count_nodes()} nodes")
    
    # Test all interpretations
    assert bdd_result.evaluate(Interpretation({'p': False, 'q': False})) == False
    assert bdd_result.evaluate(Interpretation({'p': False, 'q': True})) == False
    assert bdd_result.evaluate(Interpretation({'p': True, 'q': False})) == False
    assert bdd_result.evaluate(Interpretation({'p': True, 'q': True})) == True
    
    print("✅ BDD AND test passed")


def test_bdd_or():
    """Test BDD OR operation."""
    print("\n" + "="*60)
    print("Test: BDD OR operation")
    
    bdd_p = create_bdd_from_string("p")
    bdd_q = create_bdd_from_string("q")
    
    # Compute p ∨ q
    bdd_result = bdd_or(bdd_p, bdd_q)
    
    print(f"p ∨ q: {bdd_result.count_nodes()} nodes")
    
    # Test all interpretations
    assert bdd_result.evaluate(Interpretation({'p': False, 'q': False})) == False
    assert bdd_result.evaluate(Interpretation({'p': False, 'q': True})) == True
    assert bdd_result.evaluate(Interpretation({'p': True, 'q': False})) == True
    assert bdd_result.evaluate(Interpretation({'p': True, 'q': True})) == True
    
    print("✅ BDD OR test passed")


def test_bdd_not():
    """Test BDD NOT operation."""
    print("\n" + "="*60)
    print("Test: BDD NOT operation")
    
    bdd_p = create_bdd_from_string("p")
    
    # Compute ¬p
    bdd_result = bdd_not(bdd_p)
    
    print(f"p: {bdd_p.count_nodes()} nodes")
    print(f"¬p: {bdd_result.count_nodes()} nodes")
    
    # Test
    assert bdd_result.evaluate(Interpretation({'p': True})) == False
    assert bdd_result.evaluate(Interpretation({'p': False})) == True
    
    print("✅ BDD NOT test passed")


def test_complex_operation():
    """Test complex operation: (p ∧ q) ∨ (p ∧ r)."""
    print("\n" + "="*60)
    print("Test: Complex operation (p ∧ q) ∨ (p ∧ r)")
    
    # Build using operations
    bdd_p = create_bdd_from_string("p")
    bdd_q = create_bdd_from_string("q")
    bdd_r = create_bdd_from_string("r")
    
    # Compute (p ∧ q)
    bdd_pq = bdd_and(bdd_p, bdd_q)
    print(f"(p ∧ q): {bdd_pq.count_nodes()} nodes")
    
    # Compute (p ∧ r)
    bdd_pr = bdd_and(bdd_p, bdd_r)
    print(f"(p ∧ r): {bdd_pr.count_nodes()} nodes")
    
    # Compute (p ∧ q) ∨ (p ∧ r)
    bdd_result = bdd_or(bdd_pq, bdd_pr)
    print(f"(p ∧ q) ∨ (p ∧ r): {bdd_result.count_nodes()} nodes")
    
    # Test some interpretations
    assert bdd_result.evaluate(Interpretation({'p': True, 'q': True, 'r': False})) == True
    assert bdd_result.evaluate(Interpretation({'p': True, 'q': False, 'r': True})) == True
    assert bdd_result.evaluate(Interpretation({'p': False, 'q': True, 'r': True})) == False
    assert bdd_result.evaluate(Interpretation({'p': True, 'q': True, 'r': True})) == True
    
    print("✅ Complex operation test passed")


def test_equivalence_checking():
    """Test equivalence checking between BDDs."""
    print("\n" + "="*60)
    print("Test: Equivalence checking")
    
    # Two different ways to express the same formula
    bdd1 = create_bdd_from_string("(p & q) | (p & r)")
    bdd2 = create_bdd_from_string("p & (q | r)")  # De Morgan's law
    
    # Reduce both
    bdd1.reduce()
    bdd2.reduce()
    
    print(f"BDD1: {bdd1.count_nodes()} nodes")
    print(f"BDD2: {bdd2.count_nodes()} nodes")
    
    # Check equivalence
    equivalent = are_equivalent(bdd1, bdd2)
    print(f"Are equivalent: {equivalent}")
    
    assert equivalent == True
    
    # Test non-equivalent BDDs
    bdd3 = create_bdd_from_string("p | q")
    bdd4 = create_bdd_from_string("p & q")
    
    bdd3.reduce()
    bdd4.reduce()
    
    equivalent2 = are_equivalent(bdd3, bdd4)
    print(f"p|q ≡ p&q: {equivalent2}")
    
    assert equivalent2 == False
    
    print("✅ Equivalence checking test passed")


def test_shannon_expansion():
    """Test that operations use Shannon expansion correctly."""
    print("\n" + "="*60)
    print("Test: Shannon expansion verification")
    
    # Build p ∨ q using operations
    bdd_p = create_bdd_from_string("p")
    bdd_q = create_bdd_from_string("q")
    bdd_op = bdd_or(bdd_p, bdd_q)
    
    # Build p ∨ q directly from formula
    bdd_direct = create_bdd_from_string("p | q")
    
    # Reduce both
    bdd_op.reduce()
    bdd_direct.reduce()
    
    print(f"Via operations: {bdd_op.count_nodes()} nodes")
    print(f"Direct formula: {bdd_direct.count_nodes()} nodes")
    
    # Should be equivalent
    assert are_equivalent(bdd_op, bdd_direct)
    
    print("✅ Shannon expansion test passed")


def test_xor_operation():
    """Test XOR operation."""
    print("\n" + "="*60)
    print("Test: XOR operation")
    
    bdd_p = create_bdd_from_string("p")
    bdd_q = create_bdd_from_string("q")
    
    # Compute p ⊕ q
    bdd_result = bdd_xor(bdd_p, bdd_q)
    
    print(f"p ⊕ q: {bdd_result.count_nodes()} nodes")
    
    # Test XOR truth table
    assert bdd_result.evaluate(Interpretation({'p': False, 'q': False})) == False
    assert bdd_result.evaluate(Interpretation({'p': False, 'q': True})) == True
    assert bdd_result.evaluate(Interpretation({'p': True, 'q': False})) == True
    assert bdd_result.evaluate(Interpretation({'p': True, 'q': True})) == False
    
    print("✅ XOR operation test passed")


def test_implies_operation():
    """Test IMPLIES operation."""
    print("\n" + "="*60)
    print("Test: IMPLIES operation")
    
    bdd_p = create_bdd_from_string("p")
    bdd_q = create_bdd_from_string("q")
    
    # Compute p → q
    bdd_result = bdd_implies(bdd_p, bdd_q)
    
    print(f"p → q: {bdd_result.count_nodes()} nodes")
    
    # Test implies truth table
    assert bdd_result.evaluate(Interpretation({'p': False, 'q': False})) == True
    assert bdd_result.evaluate(Interpretation({'p': False, 'q': True})) == True
    assert bdd_result.evaluate(Interpretation({'p': True, 'q': False})) == False
    assert bdd_result.evaluate(Interpretation({'p': True, 'q': True})) == True
    
    print("✅ IMPLIES operation test passed")


def test_satisfiability():
    """Test satisfiability checking."""
    print("\n" + "="*60)
    print("Test: Satisfiability testing")
    
    # Satisfiable formula
    bdd_sat = create_bdd_from_string("p | q")
    assert bdd_sat.is_satisfiable() == True
    print("p | q is satisfiable: ✓")
    
    # Tautology
    bdd_valid = create_bdd_from_string("p | ~p")
    bdd_valid.reduce()
    assert bdd_valid.is_valid() == True
    assert bdd_valid.is_satisfiable() == True
    print("p | ~p is valid (tautology): ✓")
    
    # Contradiction
    bdd_unsat = create_bdd_from_string("p & ~p")
    bdd_unsat.reduce()
    assert bdd_unsat.is_satisfiable() == False
    assert bdd_unsat.is_valid() == False
    print("p & ~p is unsatisfiable (contradiction): ✓")
    
    print("✅ Satisfiability testing passed")


def test_textbook_operations():
    """Test operations on textbook example p ∨ (q ∧ r)."""
    print("\n" + "="*60)
    print("Test: Operations on textbook example")
    
    # Build p ∨ (q ∧ r) using operations
    bdd_p = create_bdd_from_string("p")
    bdd_q = create_bdd_from_string("q")
    bdd_r = create_bdd_from_string("r")
    
    bdd_qr = bdd_and(bdd_q, bdd_r)
    bdd_result = bdd_or(bdd_p, bdd_qr)
    
    # Build directly
    bdd_direct = create_bdd_from_string("p | (q & r)")
    
    # Reduce both
    bdd_result.reduce()
    bdd_direct.reduce()
    
    print(f"Via operations: {bdd_result.count_nodes()} nodes")
    print(f"Direct: {bdd_direct.count_nodes()} nodes")
    
    # Should be equivalent
    assert are_equivalent(bdd_result, bdd_direct)
    
    print("✅ Textbook operations test passed")


if __name__ == "__main__":
    print("Testing BDD Operations (Apply & Shannon Expansion)")
    print("="*60)
    
    test_bdd_and()
    test_bdd_or()
    test_bdd_not()
    test_complex_operation()
    test_equivalence_checking()
    test_shannon_expansion()
    test_xor_operation()
    test_implies_operation()
    test_satisfiability()
    test_textbook_operations()
    
    print("\n" + "="*60)
    print("🎉 All BDD Operations tests passed!")