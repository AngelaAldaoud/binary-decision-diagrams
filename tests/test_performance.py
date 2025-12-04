"""
Performance Benchmarks for BDD Operations
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import time
from bdd.diagram import BDD, create_bdd_from_string
from bdd.operations import bdd_and, bdd_or, bdd_xor, are_equivalent
from bdd.formula import FormulaParser


def benchmark_construction(formula_str: str, name: str):
    """Benchmark BDD construction time."""
    print(f"\n{'='*60}")
    print(f"Benchmark: {name}")
    print(f"Formula: {formula_str}")
    
    start_time = time.time()
    bdd = create_bdd_from_string(formula_str)
    construction_time = time.time() - start_time
    
    nodes_before = bdd.count_nodes()
    
    start_time = time.time()
    stats = bdd.reduce()
    reduction_time = time.time() - start_time
    
    nodes_after = bdd.count_nodes()
    
    print(f"Construction time: {construction_time*1000:.2f} ms")
    print(f"Nodes before reduction: {nodes_before}")
    print(f"Reduction time: {reduction_time*1000:.2f} ms")
    print(f"Nodes after reduction: {nodes_after}")
    print(f"Reduction ratio: {nodes_before/nodes_after if nodes_after > 0 else 'N/A':.2f}x")
    print(f"Total time: {(construction_time + reduction_time)*1000:.2f} ms")
    
    return {
        'name': name,
        'construction_time': construction_time,
        'reduction_time': reduction_time,
        'nodes_before': nodes_before,
        'nodes_after': nodes_after,
        'total_time': construction_time + reduction_time
    }


def benchmark_operations():
    """Benchmark BDD operations."""
    print(f"\n{'='*60}")
    print("Benchmark: BDD Operations")
    
    # Create test BDDs
    bdd_p = create_bdd_from_string("p")
    bdd_q = create_bdd_from_string("q")
    bdd_r = create_bdd_from_string("r")
    
    # Benchmark AND
    start = time.time()
    for _ in range(100):
        result = bdd_and(bdd_p, bdd_q)
    and_time = (time.time() - start) / 100
    print(f"AND operation: {and_time*1000:.3f} ms (avg over 100)")
    
    # Benchmark OR
    start = time.time()
    for _ in range(100):
        result = bdd_or(bdd_p, bdd_q)
    or_time = (time.time() - start) / 100
    print(f"OR operation: {or_time*1000:.3f} ms (avg over 100)")
    
    # Benchmark XOR
    start = time.time()
    for _ in range(100):
        result = bdd_xor(bdd_p, bdd_q)
    xor_time = (time.time() - start) / 100
    print(f"XOR operation: {xor_time*1000:.3f} ms (avg over 100)")
    
    # Benchmark complex operation
    start = time.time()
    for _ in range(100):
        pq = bdd_and(bdd_p, bdd_q)
        pr = bdd_and(bdd_p, bdd_r)
        result = bdd_or(pq, pr)
    complex_time = (time.time() - start) / 100
    print(f"Complex operation (p∧q)∨(p∧r): {complex_time*1000:.3f} ms (avg over 100)")


def benchmark_equivalence():
    """Benchmark equivalence checking."""
    print(f"\n{'='*60}")
    print("Benchmark: Equivalence Checking")
    
    # Create equivalent BDDs
    bdd1 = create_bdd_from_string("(p & q) | (p & r)")
    bdd2 = create_bdd_from_string("p & (q | r)")
    
    bdd1.reduce()
    bdd2.reduce()
    
    start = time.time()
    for _ in range(1000):
        result = are_equivalent(bdd1, bdd2)
    equiv_time = (time.time() - start) / 1000
    
    print(f"Equivalence check: {equiv_time*1000:.3f} ms (avg over 1000)")
    print(f"Result: {result}")


def benchmark_variable_scaling():
    """Test how performance scales with number of variables."""
    print(f"\n{'='*60}")
    print("Benchmark: Variable Scaling")
    print(f"{'Variables':<12} {'Nodes':<10} {'Reduced':<10} {'Time (ms)':<12}")
    print("-" * 50)
    
    results = []
    
    # Test formulas with increasing variables
    for n in range(2, 8):
        # Create formula: (x1 & x2) | (x3 & x4) | ... 
        terms = []
        for i in range(0, n, 2):
            if i+1 < n:
                terms.append(f"(x{i} & x{i+1})")
            else:
                terms.append(f"x{i}")
        
        formula_str = " | ".join(terms)
        
        start = time.time()
        bdd = create_bdd_from_string(formula_str)
        nodes_before = bdd.count_nodes()
        bdd.reduce()
        nodes_after = bdd.count_nodes()
        elapsed = (time.time() - start) * 1000
        
        print(f"{n:<12} {nodes_before:<10} {nodes_after:<10} {elapsed:<12.2f}")
        
        results.append({
            'variables': n,
            'nodes_before': nodes_before,
            'nodes_after': nodes_after,
            'time': elapsed
        })
    
    return results


def benchmark_worst_case():
    """Test worst case: XOR chain (no reduction possible)."""
    print(f"\n{'='*60}")
    print("Benchmark: Worst Case (XOR chain - minimal reduction)")
    
    # XOR chains have minimal reduction
    for n in range(2, 6):
        vars = [f"x{i}" for i in range(n)]
        formula_str = " ^ ".join(vars)  # XOR using ^
        
        # Convert XOR to proper formula
        # x1 ^ x2 = (x1 | x2) & ~(x1 & x2)
        formula_parts = []
        result = vars[0]
        for i in range(1, n):
            # Build incrementally
            result = f"(({result} | {vars[i]}) & ~({result} & {vars[i]}))"
        
        start = time.time()
        bdd = create_bdd_from_string(result)
        nodes_before = bdd.count_nodes()
        bdd.reduce()
        nodes_after = bdd.count_nodes()
        elapsed = (time.time() - start) * 1000
        
        print(f"{n} variables: {nodes_before} → {nodes_after} nodes, {elapsed:.2f} ms")


def run_all_benchmarks():
    """Run complete benchmark suite."""
    print("\n" + "="*60)
    print("BDD PERFORMANCE BENCHMARK SUITE")
    print("="*60)
    
    # Test cases from textbook
    results = []
    
    results.append(benchmark_construction(
        "p & q",
        "Simple conjunction"
    ))
    
    results.append(benchmark_construction(
        "p | q",
        "Simple disjunction"
    ))
    
    results.append(benchmark_construction(
        "p | (q & r)",
        "Textbook example"
    ))
    
    results.append(benchmark_construction(
        "(p & q) | (p & r)",
        "Distributive law"
    ))
    
    results.append(benchmark_construction(
        "p | ~p",
        "Tautology"
    ))
    
    results.append(benchmark_construction(
        "p & ~p",
        "Contradiction"
    ))
    
    results.append(benchmark_construction(
        "(p & q & r) | (p & ~q & r) | (~p & q & r)",
        "Complex 3-variable formula"
    ))
    
    # Operations benchmarks
    benchmark_operations()
    
    # Equivalence checking
    benchmark_equivalence()
    
    # Scaling tests
    scaling_results = benchmark_variable_scaling()
    
    # Worst case
    benchmark_worst_case()
    
    # Summary
    print(f"\n{'='*60}")
    print("BENCHMARK SUMMARY")
    print("="*60)
    print(f"{'Test':<30} {'Total Time':<15} {'Reduction':<15}")
    print("-" * 60)
    
    for r in results:
        print(f"{r['name']:<30} {r['total_time']*1000:>10.2f} ms  {r['nodes_before']:>4} → {r['nodes_after']:>4}")
    
    print("\n✅ All benchmarks completed!")


if __name__ == "__main__":
    run_all_benchmarks()