"""
Tests for Formula Parser
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from bdd.formula import *
from bdd.truth_table import Interpretation


def test_variable():
    """Test simple variable."""
    p = Variable('p')
    
    interp_true = Interpretation({'p': True})
    interp_false = Interpretation({'p': False})
    
    assert p.evaluate(interp_true) == True
    assert p.evaluate(interp_false) == False
    assert p.get_variables() == {'p'}
    
    print(f" Variable test passed: {p}")


def test_not():
    """Test negation."""
    p = Variable('p')
    not_p = Not(p)
    
    interp_true = Interpretation({'p': True})
    interp_false = Interpretation({'p': False})
    
    assert not_p.evaluate(interp_true) == False
    assert not_p.evaluate(interp_false) == True
    
    print(f" NOT test passed: {not_p}")


def test_and():
    """Test conjunction."""
    p = Variable('p')
    q = Variable('q')
    p_and_q = And(p, q)
    
    assert p_and_q.evaluate(Interpretation({'p': True, 'q': True})) == True
    assert p_and_q.evaluate(Interpretation({'p': True, 'q': False})) == False
    assert p_and_q.evaluate(Interpretation({'p': False, 'q': True})) == False
    assert p_and_q.evaluate(Interpretation({'p': False, 'q': False})) == False
    
    print(f" AND test passed: {p_and_q}")


def test_or():
    """Test disjunction."""
    p = Variable('p')
    q = Variable('q')
    p_or_q = Or(p, q)
    
    assert p_or_q.evaluate(Interpretation({'p': True, 'q': True})) == True
    assert p_or_q.evaluate(Interpretation({'p': True, 'q': False})) == True
    assert p_or_q.evaluate(Interpretation({'p': False, 'q': True})) == True
    assert p_or_q.evaluate(Interpretation({'p': False, 'q': False})) == False
    
    print(f"OR test passed: {p_or_q}")


def test_complex_formula():
    """Test p ∨ (q ∧ r) from textbook."""
    p = Variable('p')
    q = Variable('q')
    r = Variable('r')
    formula = Or(p, And(q, r))
    
    # Test cases from Fig 5.1
    assert formula.evaluate(Interpretation({'p': False, 'q': False, 'r': False})) == False
    assert formula.evaluate(Interpretation({'p': False, 'q': True, 'r': False})) == False
    assert formula.evaluate(Interpretation({'p': False, 'q': True, 'r': True})) == True
    assert formula.evaluate(Interpretation({'p': True, 'q': False, 'r': False})) == True
    
    print(f"Complex formula test passed: {formula}")


def test_parser_simple():
    """Test parsing simple formulas."""
    # Parse "p"
    p = FormulaParser.parse_formula("p")
    assert isinstance(p, Variable)
    assert p.name == 'p'
    
    # Parse "p ∧ q"
    p_and_q = FormulaParser.parse_formula("p ∧ q")
    assert isinstance(p_and_q, And)
    
    # Parse "p ∨ q"
    p_or_q = FormulaParser.parse_formula("p ∨ q")
    assert isinstance(p_or_q, Or)
    
    # Parse "¬p"
    not_p = FormulaParser.parse_formula("¬p")
    assert isinstance(not_p, Not)
    
    print(" Simple parser tests passed")


def test_parser_with_parentheses():
    """Test parsing with parentheses."""
    # Parse "p ∨ (q ∧ r)"
    formula = FormulaParser.parse_formula("p ∨ (q ∧ r)")
    
    assert isinstance(formula, Or)
    assert isinstance(formula.left, Variable)
    assert isinstance(formula.right, And)
    
    # Test evaluation
    assert formula.evaluate(Interpretation({'p': True, 'q': False, 'r': False})) == True
    assert formula.evaluate(Interpretation({'p': False, 'q': True, 'r': True})) == True
    assert formula.evaluate(Interpretation({'p': False, 'q': True, 'r': False})) == False
    
    print(f" Parser with parentheses passed: {formula}")


def test_parser_alternative_syntax():
    """Test alternative operator syntax."""
    # Using & for AND
    f1 = FormulaParser.parse_formula("p & q")
    assert isinstance(f1, And)
    
    # Using | for OR
    f2 = FormulaParser.parse_formula("p | q")
    assert isinstance(f2, Or)
    
    # Using ~ for NOT
    f3 = FormulaParser.parse_formula("~p")
    assert isinstance(f3, Not)
    
    # Using -> for IMPLIES
    f4 = FormulaParser.parse_formula("p -> q")
    assert isinstance(f4, Implies)
    
    print("  Alternative syntax test passed")


def test_implies_and_iff():
    """Test implication and biconditional."""
    # p → q
    implies = FormulaParser.parse_formula("p -> q")
    assert implies.evaluate(Interpretation({'p': False, 'q': False})) == True
    assert implies.evaluate(Interpretation({'p': False, 'q': True})) == True
    assert implies.evaluate(Interpretation({'p': True, 'q': False})) == False
    assert implies.evaluate(Interpretation({'p': True, 'q': True})) == True
    
    # p ↔ q
    iff = FormulaParser.parse_formula("p <-> q")
    assert iff.evaluate(Interpretation({'p': False, 'q': False})) == True
    assert iff.evaluate(Interpretation({'p': False, 'q': True})) == False
    assert iff.evaluate(Interpretation({'p': True, 'q': False})) == False
    assert iff.evaluate(Interpretation({'p': True, 'q': True})) == True
    
    print("  Implies and Iff test passed")


def test_get_variables():
    """Test variable extraction."""
    formula = FormulaParser.parse_formula("p ∨ (q ∧ r)")
    variables = formula.get_variables()
    
    assert variables == {'p', 'q', 'r'}
    
    print(f"  Variable extraction test passed: {variables}")


def test_textbook_example():
    """Test exact example from textbook page 96."""
    formula = FormulaParser.parse_formula("p ∨ (q ∧ r)")
    
    print(f"\nTextbook formula: {formula}")
    print(f"Variables: {formula.get_variables()}")
    
    # Create truth table
    from bdd.truth_table import TruthTable
    
    def eval_func(interp):
        return formula.evaluate(interp)
    
    table = TruthTable.from_function(['p', 'q', 'r'], eval_func)
    print("\nTruth table:")
    print(table)
    
    models = table.get_models()
    print(f"\nNumber of satisfying interpretations: {len(models)}")
    
    print("  Textbook example test passed")


if __name__ == "__main__":
    print("Testing Formula Parser...\n")
    test_variable()
    test_not()
    test_and()
    test_or()
    test_complex_formula()
    test_parser_simple()
    test_parser_with_parentheses()
    test_parser_alternative_syntax()
    test_implies_and_iff()
    test_get_variables()
    test_textbook_example()
    print("\n All Formula Parser tests passed!")