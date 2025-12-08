"""
Tests for BDD Visualization
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from bdd.diagram import BDD, create_bdd_from_string
from bdd.visualizer import visualize_bdd, compare_bdds, GRAPHVIZ_AVAILABLE
from bdd.formula import FormulaParser


def test_simple_visualization():
    """Test visualizing a simple BDD."""
    if not GRAPHVIZ_AVAILABLE:
        print("  Skipping: graphviz not available")
        return
    
    print("\n" + "="*60)
    print("Test: Visualizing p ∧ q")
    
    bdd = create_bdd_from_string("p & q")
    
    # Visualize (will open image)
    path = visualize_bdd(bdd, filename='test_simple', view=False)
    print(f"  Created visualization: {path}")


def test_textbook_example_visualization():
    """Test visualizing the textbook example before and after reduction."""
    if not GRAPHVIZ_AVAILABLE:
        print("   Skipping: graphviz not available")
        return
    
    print("\n" + "="*60)
    print("Test: Visualizing p ∨ (q ∧ r) - Textbook Example")
    
    # Create unreduced BDD
    formula = FormulaParser.parse_formula("p | (q & r)")
    bdd_unreduced = BDD(formula, variable_order=['p', 'q', 'r'])
    
    # Create reduced BDD
    bdd_reduced = BDD(formula, variable_order=['p', 'q', 'r'])
    stats = bdd_reduced.reduce()
    
    print(f"Unreduced: {bdd_unreduced.count_nodes()} nodes")
    print(f"Reduced: {bdd_reduced.count_nodes()} nodes")
    print(f"Reduction: {stats}")
    
    # Visualize unreduced
    path1 = visualize_bdd(bdd_unreduced, filename='textbook_unreduced', view=False)
    print(f"  Created unreduced visualization: {path1}")
    
    # Visualize reduced
    path2 = visualize_bdd(bdd_reduced, filename='textbook_reduced', view=False)
    print(f"  Created reduced visualization: {path2}")
    
    # Compare side-by-side
    path3 = compare_bdds(bdd_unreduced, bdd_reduced, 
                         filename='textbook_comparison', view=False)
    print(f"  Created comparison: {path3}")


def test_tautology_visualization():
    """Visualize a tautology."""
    if not GRAPHVIZ_AVAILABLE:
        print("   Skipping: graphviz not available")
        return
    
    print("\n" + "="*60)
    print("Test: Visualizing p ∨ ¬p (Tautology)")
    
    bdd = create_bdd_from_string("p | ~p")
    bdd.reduce()
    
    # Should be single TRUE node
    print(f"Nodes: {bdd.count_nodes()}")
    
    path = visualize_bdd(bdd, filename='tautology', view=False)
    print(f"  Created tautology visualization: {path}")


def test_contradiction_visualization():
    """Visualize a contradiction."""
    if not GRAPHVIZ_AVAILABLE:
        print("   Skipping: graphviz not available")
        return
    
    print("\n" + "="*60)
    print("Test: Visualizing p ∧ ¬p (Contradiction)")
    
    bdd = create_bdd_from_string("p & ~p")
    bdd.reduce()
    
    # Should be single FALSE node
    print(f"Nodes: {bdd.count_nodes()}")
    
    path = visualize_bdd(bdd, filename='contradiction', view=False)
    print(f"  Created contradiction visualization: {path}")


def test_complex_formula_visualization():
    """Visualize a more complex formula."""
    if not GRAPHVIZ_AVAILABLE:
        print("   Skipping: graphviz not available")
        return
    
    print("\n" + "="*60)
    print("Test: Visualizing (p ∧ q) ∨ (p ∧ r)")
    
    # Before reduction
    bdd_before = create_bdd_from_string("(p & q) | (p & r)")
    print(f"Before reduction: {bdd_before.count_nodes()} nodes")
    
    # After reduction
    bdd_after = create_bdd_from_string("(p & q) | (p & r)")
    stats = bdd_after.reduce()
    print(f"After reduction: {bdd_after.count_nodes()} nodes")
    print(f"Statistics: {stats}")
    
    # Compare
    path = compare_bdds(bdd_before, bdd_after, 
                       filename='complex_comparison', view=False)
    print(f"  Created comparison: {path}")


def test_all_visualizations_with_view():
    """Create all visualizations and open them."""
    if not GRAPHVIZ_AVAILABLE:
        print("   Skipping: graphviz not available")
        return
    
    print("\n" + "="*60)
    print("Creating all visualizations (will open in viewer)...")
    print("="*60)
    
    # 1. Textbook example comparison
    formula = FormulaParser.parse_formula("p | (q & r)")
    bdd_unreduced = BDD(formula, variable_order=['p', 'q', 'r'])
    bdd_reduced = BDD(formula, variable_order=['p', 'q', 'r'])
    bdd_reduced.reduce()
    
    compare_bdds(bdd_unreduced, bdd_reduced, 
                filename='final_textbook_comparison', view=True)
    
    print("  All visualizations created!")


if __name__ == "__main__":
    print("Testing BDD Visualization")
    print("="*60)
    
    if not GRAPHVIZ_AVAILABLE:
        print("\n   WARNING: graphviz not installed!")
        print("Install with: pip install graphviz")
        print("Also ensure system graphviz is installed:")
        print("  - macOS: brew install graphviz")
        print("  - Linux: sudo apt-get install graphviz")
        print("  - Windows: Download from graphviz.org")
    else:
        test_simple_visualization()
        test_textbook_example_visualization()
        test_tautology_visualization()
        test_contradiction_visualization()
        test_complex_formula_visualization()
        
        # Uncomment to open visualizations:
        # test_all_visualizations_with_view()
        
        print("\n" + "="*60)
        print(" All visualization tests passed!")
        print("\nGenerated files:")
        print("  - test_simple.png")
        print("  - textbook_unreduced.png")
        print("  - textbook_reduced.png")
        print("  - textbook_comparison.png")
        print("  - tautology.png")
        print("  - contradiction.png")
        print("  - complex_comparison.png")