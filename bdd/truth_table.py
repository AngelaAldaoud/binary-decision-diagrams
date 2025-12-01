"""
Truth Table Implementation
Represents truth tables for propositional logic formulas
"""

from typing import Dict, List, Tuple
from bdd.node import BDDNode, TERMINAL_TRUE, TERMINAL_FALSE


class Interpretation:
    """
    Represents an interpretation (assignment of truth values to variables).

    What is an interpretation?
    An interpretation is an assignment of truth values to variables. For example:
    
    p = True, q = False, r = True
    This is ONE possible way to assign values to your variables
    
    Think of it like filling in a row of a truth table.

    """
    
    def __init__(self, assignments: Dict[str, bool] = None):
        """
        Initialize an interpretation.
        
        Args:
            assignments: Dictionary mapping variable names to boolean values
                        e.g., {'p': True, 'q': False, 'r': True}
        """
        self.assignments = assignments if assignments else {}
    
    def assign(self, variable: str, value: bool):
        """Assign a truth value to a variable.
            Simple method to add or update a variable's value.
        """
        self.assignments[variable] = value
    
    def get(self, variable: str) -> bool:
        """
        Get the truth value assigned to a variable.
        
        Returns:
            Boolean value, or None if variable not assigned
        """
        return self.assignments.get(variable)
    
    def is_complete(self, variables: List[str]) -> bool:
        """
        Check if interpretation assigns values to all variables.
        
        Args:
            variables: List of all variables that need assignment
            
        Returns:
            True if all variables are assigned
        """

        #Why it matters: In a truth table, each row must assign values to ALL variables.
        return all(var in self.assignments for var in variables)
    
    def copy(self):
        """Creates an independent copy of the interpretation."""
        return Interpretation(self.assignments.copy())
    
    def __repr__(self):
        """String representation."""
        items = [f"{var}={val}" for var, val in sorted(self.assignments.items())]
        return f"I({', '.join(items)})"
    
    def __str__(self):
        """User-friendly representation."""
        return self.__repr__()
    
    def __eq__(self, other):
        """Check equality of interpretations."""
        if not isinstance(other, Interpretation):
            return False
        return self.assignments == other.assignments
    
    def __hash__(self):
        """Hash for use in sets and dictionaries."""
        return hash(tuple(sorted(self.assignments.items())))


class TruthTable:
    """
    Represents a truth table for a propositional logic formula.
    """
    
    def __init__(self, variables: List[str]):
        """
        Initialize a truth table.
        
        Args:
            variables: List of variable names in the formula (e.g., ['p', 'q', 'r'])
        """
        self.variables = sorted(variables)  # Keep consistent order
        self.rows: List[Tuple[Interpretation, bool]] = [] # Each row will be a tuple: (interpretation, result)

    
    def add_row(self, interpretation: Interpretation, result: bool):
        """
        Add a row to the truth table.
        
        Args:
            interpretation: The variable assignments for this row
            result: The truth value of the formula under this interpretation
        """
        self.rows.append((interpretation, result))
    
    def generate_all_interpretations(self) -> List[Interpretation]:
        """
        Generate all possible interpretations for the variables.
        Creates 2^n interpretations where n is the number of variables.
        
        Returns:
            List of all possible interpretations
        """
        if not self.variables:
            return [Interpretation()]
        
        interpretations = []
        n = len(self.variables)
        
        # Generate all 2^n combinations
        for i in range(2 ** n):
            interpretation = Interpretation()
            for j, var in enumerate(self.variables):
                # Check if j-th bit is set in i
                """
                i >> (n - 1 - j): Shift bits right to get to position j
                & 1: Check if the bit is 1 (True) or 0 (False)


                i >> (n - 1 - j) shifts the bits right to bring the j-th bit to position 0
                & 1 extracts just that bit (masks everything else)
                bool(bit_value) converts 0→False, 1→True

                Example Walkthrough
                    Let's say you have variables = ['A', 'B', 'C'], so n = 3:
                    When i = 5 (binary: 101):

                    j=0, var='A': shift right by (3-1-0)=2 → 101>>2 = 001 → &1 = 1 → A=True
                    j=1, var='B': shift right by (3-1-1)=1 → 101>>1 = 010 → &1 = 0 → B=False
                    j=2, var='C': shift right by (3-1-2)=0 → 101>>0 = 101 → &1 = 1 → C=True

                    Result: {A: True, B: False, C: True}

                    Great question! The >> operator is called the bitwise right shift operator. Let me explain what 101>>2 means.
                    101 >> 2 means: "shift the bits of 101 two positions to the right"
                    Original:     1 0 1
                                  ↓ ↓ ↓
                    Shift right 1: 0 1 (the rightmost 1 falls off)
                                  ↓ ↓
                    Shift right 2:  0 0 1 (the 0 falls off, result padded with 0 on left)
                """
                bit_value = (i >> (n - 1 - j)) & 1
                interpretation.assign(var, bool(bit_value))
            interpretations.append(interpretation)
        
        return interpretations
    
    def is_tautology(self) -> bool:
        """Check if the formula is a tautology (all rows are True).
            for _, result in self.rows: Iterate through rows, ignore interpretation
            all(result ...): Check if ALL results are True
        """
        return all(result for _, result in self.rows)
    
    def is_contradiction(self) -> bool:
        """Check if the formula is a contradiction (all rows are False)."""
        return all(not result for _, result in self.rows)
    
    def is_satisfiable(self) -> bool:
        """Check if the formula is satisfiable (at least one row is True)."""
        return any(result for _, result in self.rows)
    
    def get_models(self) -> List[Interpretation]:
        """
        Get all interpretations that satisfy the formula.
        
        Returns:
            List of interpretations where formula evaluates to True
        
        In another word , These are the "satisfying assignments" or "models" of the formula.
        """
        return [interp for interp, result in self.rows if result]
    
    def __repr__(self):
        """String representation."""
        return f"TruthTable(vars={self.variables}, rows={len(self.rows)})"
    
    def __str__(self):
        """
        Pretty-print the truth table.
        """
        if not self.rows:
            return "Empty truth table"
        
        # Header
        header = " | ".join(self.variables) + " | Result"
        separator = "-" * len(header)
        
        lines = [header, separator]
        
        # Rows
        for interpretation, result in self.rows:
            values = [str(interpretation.get(var))[0] for var in self.variables]  # T or F
            result_str = str(result)[0]
            row = " | ".join(values) + " |   " + result_str
            lines.append(row)
        
        return "\n".join(lines)
    
    @staticmethod
    def from_function(variables: List[str], eval_func):
        """
        Create a truth table by evaluating a function on all interpretations.
        
        Args:
            variables: List of variable names
            eval_func: Function that takes Interpretation and returns bool
            
        Returns:
            Complete TruthTable
        """

        """
        How to use it:
        1- Define a function that evaluates your formula:
        def p_or_q(interp: Interpretation) -> bool:
            p = interp.get('p')
            q = interp.get('q')
        return p or q
        2- Create the truth table:
            table = TruthTable.from_function(['p', 'q'], p_or_q)

        Note: What it does internally:

            Creates empty truth table
            Generates all possible interpretations
            For each interpretation, calls your function
            Adds each (interpretation, result) as a row

            This is very convenient! You just define your formula logic, and it generates the complete truth table automatically.

        """
        #Factory method to create a complete truth table from a formula function.
        table = TruthTable(variables)
        for interpretation in table.generate_all_interpretations():
            result = eval_func(interpretation)
            table.add_row(interpretation, result)
        return table


class PartialInterpretation(Interpretation):
    """
    Represents a partial interpretation (some variables may be unassigned).
    Used during BDD traversal when not all variables have been decided.

    What is a partial interpretation?
    A partial interpretation is like a regular interpretation, but some variables might not be assigned yet.
    Why do we need this?
    When traversing a BDD, you make decisions one variable at a time. After deciding p=True, you haven't decided q or r yet. A partial interpretation represents this intermediate state.
    """
    
    def __init__(self, assignments: Dict[str, bool] = None):
        super().__init__(assignments) #Just calls the parent Interpretation constructor. This means PartialInterpretation has all the methods of Interpretation plus its own additional methods.
    
    def is_defined_for(self, variable: str) -> bool:
        """Check if this partial interpretation assigns a value to the variable."""
        return variable in self.assignments
    
    def extend(self, variable: str, value: bool):
        """
        Extend the partial interpretation with a new assignment.
        
        Args:
            variable: Variable name to assign
            value: Boolean value to assign
            
        Returns:
            New PartialInterpretation with the extended assignment

            Why create a new one instead of modifying?
            During BDD traversal, you might explore multiple paths. You need to keep the original state to backtrack.

        """
        new_interp = PartialInterpretation(self.assignments.copy())
        new_interp.assign(variable, value)
        return new_interp