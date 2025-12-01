"""
Formula Parser for Propositional Logic
Parses string formulas into an Abstract Syntax Tree (AST)
"""

from typing import Set, List
from bdd.truth_table import Interpretation


class Formula:
    """Base class for all formula types."""
    
    def evaluate(self, interpretation: Interpretation) -> bool:
        """Evaluate formula under given interpretation."""
        raise NotImplementedError
    
    def get_variables(self) -> Set[str]:
        """Get all variables in the formula."""
        raise NotImplementedError
    
    def __repr__(self):
        raise NotImplementedError


class Variable(Formula):
    """Propositional variable (atom)."""
    
    def __init__(self, name: str):
        self.name = name # Represents a single propositional variable (like p, q, r). This is a leaf node in the AST - it doesn't contain other formulas.
    
    def evaluate(self, interpretation: Interpretation) -> bool:
        value = interpretation.get(self.name)
        if value is None:
            raise ValueError(f"Variable {self.name} not assigned in interpretation")
        return value
    
    def get_variables(self) -> Set[str]:
        return {self.name}
    
    def __repr__(self):
        return self.name
    
    def __eq__(self, other):
        return isinstance(other, Variable) and self.name == other.name
    
    def __hash__(self):
        return hash(('var', self.name))


class Not(Formula):
    """Negation: ¬A"""
    
    def __init__(self, operand: Formula):
        self.operand = operand # This is a unary operator - it takes one sub-formula. Example: ¬p has Variable('p') as its operand.
    
    """
    def evaluate(...):
    Recursive evaluation:
        Evaluate the operand (the sub-formula)
        Return the opposite (logical NOT)

    p = Variable('p')
    not_p = Not(p)
    interp = Interpretation({'p': True})
    result = not_p.evaluate(interp)  # Returns False (not True)

    """
    def evaluate(self, interpretation: Interpretation) -> bool:
        return not self.operand.evaluate(interpretation)
    
    """
    def get_variables(...):
    Gets variables from its operand.
    If operand is p, returns {'p'}.
    If operand is (p ∧ q), returns {'p', 'q'}.
    """
    def get_variables(self) -> Set[str]:
        return self.operand.get_variables() # Prints as: ¬p, ¬(p ∧ q), etc.
    
    def __repr__(self):
        return f"¬{self.operand}"
    
    def __eq__(self, other):
        return isinstance(other, Not) and self.operand == other.operand
    
    def __hash__(self):
        return hash(('not', self.operand))


class And(Formula):
    """Conjunction: A ∧ B, This is a binary operator - it takes two sub-formulas."""
    
    def __init__(self, left: Formula, right: Formula):
        self.left = left
        self.right = right

    """
    def evaluate(...):
    Recursive evaluation:
        Evaluate left sub-formula
        Evaluate right sub-formula
        Return their logical AND
    """    
    def evaluate(self, interpretation: Interpretation) -> bool:
        return self.left.evaluate(interpretation) and self.right.evaluate(interpretation)
    
    """
    def get_variables(...):
    Returns union (|) of variables from both sides.
        If left is p and right is q, returns {'p', 'q'}.
        If left is (p ∧ q) and right is r, returns {'p', 'q', 'r'}.
    """
    def get_variables(self) -> Set[str]:
        return self.left.get_variables() | self.right.get_variables()
    
    def __repr__(self):
        return f"({self.left} ∧ {self.right})" # Prints with parentheses: (p ∧ q), (p ∧ (q ∨ r)), etc.
    
    def __eq__(self, other):
        return isinstance(other, And) and self.left == other.left and self.right == other.right
    
    def __hash__(self):
        return hash(('and', self.left, self.right))


class Or(Formula):
    """Disjunction: A ∨ B"""
    
    def __init__(self, left: Formula, right: Formula):
        self.left = left
        self.right = right
    
    def evaluate(self, interpretation: Interpretation) -> bool:
        return self.left.evaluate(interpretation) or self.right.evaluate(interpretation)
    
    def get_variables(self) -> Set[str]:
        return self.left.get_variables() | self.right.get_variables()
    
    def __repr__(self):
        return f"({self.left} ∨ {self.right})"
    
    def __eq__(self, other):
        return isinstance(other, Or) and self.left == other.left and self.right == other.right
    
    def __hash__(self):
        return hash(('or', self.left, self.right))


class Implies(Formula):
    """Implication: A → B"""
    
    def __init__(self, left: Formula, right: Formula):
        self.left = left
        self.right = right
    
    def evaluate(self, interpretation: Interpretation) -> bool:
        # A → B is equivalent to ¬A ∨ B
        return (not self.left.evaluate(interpretation)) or self.right.evaluate(interpretation)
    
    def get_variables(self) -> Set[str]:
        return self.left.get_variables() | self.right.get_variables()
    
    def __repr__(self):
        return f"({self.left} → {self.right})"
    
    def __eq__(self, other):
        return isinstance(other, Implies) and self.left == other.left and self.right == other.right
    
    def __hash__(self):
        return hash(('implies', self.left, self.right))


class Iff(Formula):
    """Biconditional: A ↔ B"""
    
    def __init__(self, left: Formula, right: Formula):
        self.left = left
        self.right = right
    
    def evaluate(self, interpretation: Interpretation) -> bool:
        # A ↔ B is true when both have same truth value
        return self.left.evaluate(interpretation) == self.right.evaluate(interpretation)
    
    def get_variables(self) -> Set[str]:
        return self.left.get_variables() | self.right.get_variables()
    
    def __repr__(self):
        return f"({self.left} ↔ {self.right})"
    
    def __eq__(self, other):
        return isinstance(other, Iff) and self.left == other.left and self.right == other.right
    
    def __hash__(self):
        return hash(('iff', self.left, self.right))


class FormulaParser:
    """
    Parser for propositional logic formulas.
    
    Supported operators:
    - NOT: ¬, ~, !
    - AND: ∧, &, /\\
    - OR: ∨, |, \\/
    - IMPLIES: →, ->, =>
    - IFF: ↔, <->, <=>
    
    Examples:
    - "p"
    - "p ∧ q"
    - "p ∨ (q ∧ r)"
    - "¬p → q"
    """
    
    def __init__(self, formula_str: str):
        self.original = formula_str
        self.tokens = self._tokenize(formula_str)
        self.pos = 0
    
    def _tokenize(self, s: str) -> List[str]:
        """Convert string to list of tokens."""
        # Normalize operators - IMPORTANT: Process multi-character operators BEFORE single characters
        s = s.replace('<->', '↔').replace('<=>', '↔')
        s = s.replace('->', '→').replace('=>', '→')
        s = s.replace('/\\', '∧')
        s = s.replace('\\/', '∨')
        
        # Now process single character operators
        s = s.replace('~', '¬').replace('!', '¬')
        s = s.replace('&', '∧')
        s = s.replace('|', '∨')
        
        #IMPORTANT: Multi-character operators (->, <->) must be processed BEFORE single characters, or -> would become two separate tokens!


        """

        The While loop:
        How it works:

            1- Skip whitespace: Spaces don't matter
            2- Single-char operators: (, ), ¬, ∧, ∨, →, ↔ → Add as token
            3- Variables: Start with letter, can contain letters/numbers/underscores
                Reads entire variable name: "x1" → one token "x1"
                Allows multi-character variables: "prop", "var_1"
            4- Unknown characters: Error!
        """
        tokens = []
        i = 0
        while i < len(s):
            if s[i].isspace():
                i += 1
                continue
            
            if s[i] in '()¬∧∨→↔':
                tokens.append(s[i])
                i += 1
            elif s[i].isalpha():
                # Variable name (can be multiple chars)
                var = ''
                while i < len(s) and (s[i].isalnum() or s[i] == '_'):
                    var += s[i]
                    i += 1
                tokens.append(var)
            else:
                raise ValueError(f"Unexpected character: {s[i]}")
        
        return tokens
    
    
    def _current_token(self):
        """Get current token without advancing."""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None
    
    def _consume(self, expected=None):
        """Consume current token and advance."""
        token = self._current_token()
        if expected and token != expected:
            raise ValueError(f"Expected '{expected}', got '{token}'")
        self.pos += 1
        return token
    

    """
    def parse(...):
    The Parsing Methods (Recursive Descent Parser)
    The parser uses operator precedence to build the correct AST.
    Precedence (lowest to highest):

        ↔ (Iff) - lowest
        → (Implies)
        ∨ (Or)
        ∧ (And)
        ¬ (Not)
        Variables and ( ) - highest

    Why does precedence matter?
    Consider: p ∨ q ∧ r
    With precedence:

        AND binds tighter than OR
        Parse as: p ∨ (q ∧ r)

    Without precedence:

        Ambiguous! Could be (p ∨ q) ∧ r
    """
    def parse(self) -> Formula:
        """Parse the formula."""
        result = self._parse_iff()
        if self.pos < len(self.tokens):
            raise ValueError(f"Unexpected token: {self.tokens[self.pos]}")
        return result
    
    def _parse_iff(self) -> Formula:
        """Parse biconditional (lowest precedence)."""
        left = self._parse_implies()
        
        while self._current_token() == '↔':
            self._consume('↔')
            right = self._parse_implies()
            left = Iff(left, right)
        
        return left
    

    """
    def _parse_implies(...):

    Parses implication (→).
    Key difference: Uses if instead of while!
    Why? Implication is right-associative.
    Example: p → q → r means p → (q → r), not (p → q) → r
    How it works:
        Parse left side
        If there's a →:
            Consume it
            Recursively parse right side (includes more →)
            Build Implies node
        Return result
    """
    def _parse_implies(self) -> Formula:
        """Parse implication."""
        left = self._parse_or()
        
        if self._current_token() == '→':
            self._consume('→')
            right = self._parse_implies()  # Right associative
            return Implies(left, right)
        
        return left
    
    def _parse_or(self) -> Formula:
        """Parse disjunction."""
        left = self._parse_and()
        
        while self._current_token() == '∨':
            self._consume('∨')
            right = self._parse_and()
            left = Or(left, right)
        
        return left
    
    def _parse_and(self) -> Formula:
        """Parse conjunction."""
        left = self._parse_not()
        
        while self._current_token() == '∧':
            self._consume('∧')
            right = self._parse_not()
            left = And(left, right)
        
        return left
    
    def _parse_not(self) -> Formula:
        """Parse negation."""
        if self._current_token() == '¬':
            self._consume('¬')
            operand = self._parse_not()  # Allow multiple negations Recursive to handle multiple negations: ¬¬p → Not(Not(p))
            return Not(operand)
        
        return self._parse_primary()
    
    def _parse_primary(self) -> Formula:
        """Parse primary expressions (variables and parenthesized formulas)."""
        token = self._current_token()
        
        if token == '(':
            self._consume('(')
            formula = self._parse_iff()
            self._consume(')')
            return formula
        
        if token and token[0].isalpha():
            var_name = self._consume()
            return Variable(var_name)
        
        raise ValueError(f"Unexpected token in primary: {token}")
    
    @staticmethod
    def parse_formula(formula_str: str) -> Formula:
        """
        Convenience method to parse a formula string.
        
        Args:
            formula_str: String representation of formula
            
        Returns:
            Parsed Formula object
        """
        parser = FormulaParser(formula_str)
        return parser.parse()