"""
Tests for Truth Table and Interpretation classes
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from bdd.truth_table import Interpretation, TruthTable, PartialInterpretation


def test_interpretation_basic():
    """Test basic interpretation operations."""
    interp = Interpretation()
    
    # Test assignment
    interp.assign('p', True)
    interp.assign('q', False)
    
    assert interp.get('p') == True
    assert interp.get('q') == False
    assert interp.get('r') == None  # Unassigned
    
    # Test completeness
    assert interp.is_complete(['p', 'q']) == True
    assert interp.is_complete(['p', 'q', 'r']) == False
    
    print("✅ Basic interpretation test passed")


def test_interpretation_copy():
    """Test interpretation copying."""
    interp1 = Interpretation({'p': True, 'q': False})
    interp2 = interp1.copy()
    
    interp2.assign('p', False)
    
    # Original should be unchanged
    assert interp1.get('p') == True
    assert interp2.get('p') == False
    
    print("✅ Interpretation copy test passed")


def test_interpretation_equality():
    """Test interpretation equality."""
    interp1 = Interpretation({'p': True, 'q': False})
    interp2 = Interpretation({'p': True, 'q': False})
    interp3 = Interpretation({'p': False, 'q': False})
    
    assert interp1 == interp2
    assert interp1 != interp3
    
    print("✅ Interpretation equality test passed")


def test_truth_table_generation():
    """Test generation of all interpretations."""
    table = TruthTable(['p', 'q'])
    interpretations = table.generate_all_interpretations()
    
    # Should have 2^2 = 4 interpretations
    assert len(interpretations) == 4
    
    # Check they're all different
    assert len(set(interpretations)) == 4
    
    # Print them
    print("\nGenerated interpretations for ['p', 'q']:")
    for i, interp in enumerate(interpretations, 1):
        print(f"  {i}. {interp}")
    
    print("✅ Truth table generation test passed")


def test_truth_table_three_vars():
    """Test with three variables."""
    table = TruthTable(['p', 'q', 'r'])
    interpretations = table.generate_all_interpretations()
    
    # Should have 2^3 = 8 interpretations
    assert len(interpretations) == 8
    
    print(f"\n✅ Three variable test passed ({len(interpretations)} interpretations)")


def test_truth_table_evaluation():
    """Test truth table with actual formula evaluation."""
    # Formula: p ∨ q (p OR q)
    def p_or_q(interp: Interpretation) -> bool:
        p = interp.get('p')
        q = interp.get('q')
        return p or q
    
    table = TruthTable.from_function(['p', 'q'], p_or_q)
    
    # Print the table
    print("\nTruth table for p ∨ q:")
    print(table)
    
    # Check properties
    assert table.is_satisfiable() == True
    assert table.is_tautology() == False
    assert table.is_contradiction() == False
    
    # Should have 3 models (T,T), (T,F), (F,T)
    models = table.get_models()
    assert len(models) == 3
    
    print("✅ Truth table evaluation test passed")


def test_partial_interpretation():
    """Test partial interpretations."""
    partial = PartialInterpretation({'p': True})
    
    assert partial.is_defined_for('p') == True
    assert partial.is_defined_for('q') == False
    
    # Extend it
    extended = partial.extend('q', False)
    
    assert extended.is_defined_for('q') == True
    assert extended.get('q') == False
    
    # Original should be unchanged
    assert partial.is_defined_for('q') == False
    
    print("✅ Partial interpretation test passed")


def test_truth_table_complex():
    """Test with a more complex formula: p ∨ (q ∧ r)"""
    def formula(interp: Interpretation) -> bool:
        p = interp.get('p')
        q = interp.get('q')
        r = interp.get('r')
        return p or (q and r)
    
    table = TruthTable.from_function(['p', 'q', 'r'], formula)
    
    print("\nTruth table for p ∨ (q ∧ r):")
    print(table)
    
    models = table.get_models()
    print(f"\nNumber of satisfying interpretations: {len(models)}")
    
    assert table.is_satisfiable() == True
    
    print("✅ Complex formula test passed")


if __name__ == "__main__":
    print("Testing Truth Table Implementation...\n")
    test_interpretation_basic()
    test_interpretation_copy()
    test_interpretation_equality()
    test_truth_table_generation()
    test_truth_table_three_vars()
    test_truth_table_evaluation()
    test_partial_interpretation()
    test_truth_table_complex()
    print("\n🎉 All Truth Table tests passed!")