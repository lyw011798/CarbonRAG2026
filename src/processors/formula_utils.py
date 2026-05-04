"""
formula_utils.py — Utilities for extracting and normalizing mathematical formulas
from PDF text, converting corrupted Unicode mathematical symbols to LaTeX format.

Handles:
- Unicode mathematical operators and symbols
- Subscripts and superscripts
- Mathematical variables and constants
- Fraction-like patterns
"""

import re
from typing import List, Tuple
from dataclasses import dataclass

# Mapping of corrupted/Unicode mathematical symbols to LaTeX equivalents
UNICODE_TO_LATEX_MAP = {
    # Operators and symbols
    '×': r'\times',
    '÷': r'\div',
    '∑': r'\sum',
    '∫': r'\int',
    '∂': r'\partial',
    '∆': r'\Delta',
    'Δ': r'\Delta',
    '∇': r'\nabla',
    '≈': r'\approx',
    '≠': r'\neq',
    '≤': r'\leq',
    '≥': r'\geq',
    '→': r'\rightarrow',
    '↓': r'\downarrow',
    '↑': r'\uparrow',
    '±': r'\pm',
    '∓': r'\mp',
    '∈': r'\in',
    '∉': r'\notin',
    '∞': r'\infty',
    '√': r'\sqrt',
    '∝': r'\propto',
    '∧': r'\wedge',
    '∨': r'\vee',
    '¬': r'\neg',
    '∀': r'\forall',
    '∃': r'\exists',
    # Common ligatures and special chars
    'ﬁ': 'fi',
    'ﬂ': 'fl',
}

# Unicode subscript mapping
SUBSCRIPT_MAP = {
    '₀': '0', '₁': '1', '₂': '2', '₃': '3', '₄': '4',
    '₅': '5', '₆': '6', '₇': '7', '₈': '8', '₉': '9',
    'ₐ': 'a', 'ₑ': 'e', 'ᵢ': 'i', 'ₒ': 'o', 'ᵤ': 'u',
    'ₓ': 'x', 'ᵥ': 'v', 'ₙ': 'n', 'ₜ': 't',
}

# Unicode superscript mapping
SUPERSCRIPT_MAP = {
    '⁰': '0', '¹': '1', '²': '2', '³': '3', '⁴': '4',
    '⁵': '5', '⁶': '6', '⁷': '7', '⁸': '8', '⁹': '9',
    'ᵃ': 'a', 'ᵇ': 'b', 'ᶜ': 'c', 'ᵈ': 'd', 'ᵉ': 'e',
    'ᶠ': 'f', 'ᵍ': 'g', 'ʰ': 'h', 'ⁱ': 'i', 'ʲ': 'j',
    'ᵏ': 'k', 'ˡ': 'l', 'ᵐ': 'm', 'ⁿ': 'n', 'ᵒ': 'o',
    'ᵖ': 'p', 'ʳ': 'r', 'ˢ': 's', 'ᵗ': 't', 'ᵘ': 'u',
    'ᵛ': 'v', 'ʷ': 'w', 'ˣ': 'x', 'ʸ': 'y', 'ᶻ': 'z',
    '⁺': '+', '⁻': '-', '⁼': '=',
    # Small capital letters used in abbreviations
    'ᴬ': 'A', 'ᴮ': 'B', 'ᴰ': 'D', 'ᴱ': 'E', 'ᴳ': 'G',
    'ᴸ': 'L', 'ᴾ': 'P', 'ᴿ': 'R', 'ᵀ': 'T', 'ᵁ': 'U',
    'ᴮᴸ': 'BL', 'ᴾᴿ': 'PR', 'ᴮᴬᵁ': 'BAU',
}

@dataclass
class FormulaSegment:
    """Represents a detected formula segment in text."""
    text: str
    is_formula: bool
    original_pos: Tuple[int, int]  # (start, end) positions in original text


class FormulaDetector:
    """Detects and extracts mathematical formulas from text."""
    
    # Patterns that suggest mathematical content
    FORMULA_INDICATORS = [
        r'[A-Za-z]\s*=',  # Variable = ...
        r'[×÷∆Δ±∑∫∂∇≈≠≤≥√]',  # Mathematical operators (avoid plain hyphen/plus false positives)
        r'CO₂|CO2|CO\_2',  # Common chemistry notation
        r'\b[A-Z]{1,3}[A-Z]?\b\s*=',  # Multi-letter variable
        r'[0-9]\s*[×÷/]\s*[0-9]',  # Fractional expressions
    ]
    
    def __init__(self):
        self.formula_pattern = re.compile(
            '|'.join(f'({p})' for p in self.FORMULA_INDICATORS),
            re.IGNORECASE
        )
    
    def is_likely_formula_line(self, text: str) -> bool:
        """Check if a line likely contains a formula."""
        # Remove extra whitespace
        text = text.strip()

        if not text:
            return False

        # If line is mostly CJK prose and has no clear math token, avoid false positives.
        cjk_count = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        alpha_count = sum(1 for c in text if c.isalpha())
        has_clear_math = any([
            bool(re.search(r'\\[A-Za-z]+', text)),
            bool(re.search(r'[∑∫∆Δ≤≥≈≠±√]', text)),
            bool(re.search(r'\b[A-Za-z]{1,12}(?:_[A-Za-z0-9]+)?\s*=\s*[-+]?\s*[A-Za-z0-9(]', text)),
            bool(re.search(r'\d+\s*/\s*\d+', text)),
            bool(re.search(r'\d+\s*[+\-*/=]\s*\d+', text)),
        ])
        if cjk_count > alpha_count and not has_clear_math:
            return False
        
        # Check if line contains formula indicators
        if self.formula_pattern.search(text):
            return True
        
        # Check for heavy mathematical symbol density
        math_chars = sum(1 for c in text if c in UNICODE_TO_LATEX_MAP or c in SUBSCRIPT_MAP or c in SUPERSCRIPT_MAP)
        if len(text) > 0 and math_chars / len(text) > 0.25:
            return True
        
        return False

    def is_strict_formula_line(self, text: str) -> bool:
        """High-precision check for actual equation-like lines.

        This is stricter than `is_likely_formula_line` and is used before
        inserting math wrappers to avoid prose false positives.
        """
        text = text.strip()
        if not text:
            return False

        # Explicit LaTeX command usage
        if re.search(r'\\[A-Za-z]+', text):
            return True

        # Named variable assignment (e.g., DOC = ..., TSOC_t = ...)
        if re.search(r'\b[A-Za-z][A-Za-z0-9_()]{0,20}\s*=\s*[-+]?\s*[A-Za-z0-9(]', text):
            return True

        # Numeric expression patterns and fractions
        if re.search(r'\d+\s*/\s*\d+', text):
            return True
        if re.search(r'\d+\s*[+\-*/]\s*\d+', text):
            return True

        # Summation/integral/sqrt symbols are strong formula indicators
        if re.search(r'[∑∫√]', text):
            return True

        return False


class FormulaConverter:
    """Converts corrupted/Unicode mathematical notation to LaTeX."""
    
    def __init__(self):
        self.detector = FormulaDetector()
    
    def normalize_unicode_math(self, text: str) -> str:
        """
        Replace corrupted Unicode mathematical symbols with plain text equivalents.
        
        Example:
            "𝐶𝑂₂ = 𝑇𝑆𝑂𝐶 × 44/12" → "CO2 = TSOC times 44/12"
        """
        result = text
        
        # First, handle special minus/dash characters and convert to standard minus
        result = result.replace('−', '-')  # Minus sign U+2212
        result = result.replace('‐', '-')  # Hyphen U+2010
        result = result.replace('–', '-')  # En dash
        result = result.replace('—', '-')  # Em dash
        
        # Replace mathematical operators
        for unicode_char, latex_repr in UNICODE_TO_LATEX_MAP.items():
            result = result.replace(unicode_char, latex_repr)
        
        # Handle subscripts: convert Unicode subscripts to plain text
        # This helps identify variable names (e.g., CO₂ → CO2)
        for unicode_sub, plain in SUBSCRIPT_MAP.items():
            result = result.replace(unicode_sub, plain)
        
        # Handle superscripts
        for unicode_sup, plain in SUPERSCRIPT_MAP.items():
            result = result.replace(unicode_sup, plain)
        
        # Remove mathematical alphabet variants (italic/bold Unicode chars)
        # These are usually in the range U+1D400-U+1D7FF
        result = self._remove_math_alphanumeric(result)
        
        return result
    
    def _remove_math_alphanumeric(self, text: str) -> str:
        """
        Remove mathematical alphanumeric symbols (like italic/bold Unicode variants)
        and replace with regular ASCII equivalents.
        
        Examples:
            𝐶 → C, 𝑻𝑺𝑶𝑪 → TSOC, 𝐗₁ → X1
        """
        result = []
        for char in text:
            code = ord(char)
            
            # Mathematical Alphanumeric Symbols block (U+1D400–U+1D7FF)
            if 0x1D400 <= code <= 0x1D7FF:
                # Try to find the base character
                # This is a simplified approach: extract ASCII equivalent
                mapped = self._map_math_alphanumeric(char)
                result.append(mapped)
            else:
                result.append(char)
        
        return ''.join(result)
    
    def _map_math_alphanumeric(self, char: str) -> str:
        """Map a mathematical alphanumeric symbol to its ASCII equivalent."""
        code = ord(char)
        
        # Math Bold uppercase (U+1D400–U+1D419)
        if 0x1D400 <= code <= 0x1D419:
            return chr(code - 0x1D400 + ord('A'))
        
        # Math Bold lowercase (U+1D41A–U+1D433)
        if 0x1D41A <= code <= 0x1D433:
            return chr(code - 0x1D41A + ord('a'))
        
        # Math Italic uppercase (U+1D434–U+1D44D)
        if 0x1D434 <= code <= 0x1D44D:
            return chr(code - 0x1D434 + ord('A'))
        
        # Math Italic lowercase (U+1D44E–U+1D467)
        if 0x1D44E <= code <= 0x1D467:
            return chr(code - 0x1D44E + ord('a'))
        
        # Math Bold Italic uppercase (U+1D468–U+1D481)
        if 0x1D468 <= code <= 0x1D481:
            return chr(code - 0x1D468 + ord('A'))
        
        # Math Bold Italic lowercase (U+1D482–U+1D49B)
        if 0x1D482 <= code <= 0x1D49B:
            return chr(code - 0x1D482 + ord('a'))
        
        # Math Bold digits (U+1D7CE–U+1D7D7)
        if 0x1D7CE <= code <= 0x1D7D7:
            return str(code - 0x1D7CE)
        
        # Default: return as-is (likely not a recognized math char)
        return char
    
    def to_latex(self, text: str, inline: bool = True) -> str:
        """
        Convert a formula string to LaTeX format.
        
        Args:
            text: The formula text (possibly with corrupted symbols)
            inline: If True, wrap in $...$; if False, wrap in $$...$$
        
        Returns:
            LaTeX-formatted string
        """
        # First, normalize Unicode symbols
        normalized = self.normalize_unicode_math(text)
        
        # Add spaces after LaTeX commands followed by letters (not already spaced)
        # e.g., \DeltaPE → \Delta PE
        normalized = re.sub(r'(\\[a-zA-Z]+)([A-Z])', r'\1 \2', normalized)
        
        # Remove excessive whitespace around operators (but preserve LaTeX commands)
        # First preserve \times by replacing it temporarily
        normalized = normalized.replace(r'\times', '__TIMES__')
        # Then handle other operators
        normalized = re.sub(r'\s*([=+\-×÷])\s*', r' \1 ', normalized)
        # Restore \times
        normalized = normalized.replace('__TIMES__', r'\times')
        
        # Detect and convert common patterns to LaTeX
        latex = self._pattern_to_latex(normalized)
        
        # Clean up excessive spaces
        latex = re.sub(r'\s+', ' ', latex).strip()
        
        # Wrap in appropriate delimiters
        if inline:
            return f"${latex}$"
        else:
            return f"$${latex}$$"
    
    def _pattern_to_latex(self, text: str) -> str:
        """
        Convert common patterns in normalized text to LaTeX.
        
        Examples:
            "CO2" → "CO_{2}"
            "TSOC^2" → "TSOC^{2}"
        """
        result = text
        
        # Fix spacing after LaTeX commands before regular letters (e.g., \Delta PE → \Delta PE)
        result = re.sub(r'(\\[a-zA-Z]+)\s*([A-Z]{2,})', r'\1 \2', result)
        # Also handle single letters after LaTeX: \Delta P E → \Delta PE
        result = re.sub(r'(\\[a-zA-Z]+)\s+([A-Z])\s+([A-Z])', r'\1 \2\3', result)
        
        
        # Convert common chemistry/variable notation: CO2, CO2_BL, etc.
        # Pattern: letter(s) followed by numbers/subscripts
        result = re.sub(
            r'([A-Za-z]+)(\d+(?:_[A-Za-z0-9]+)*)',
            lambda m: self._format_variable_with_subscript(m.group(1), m.group(2)),
            result
        )
        
        # Ensure fractions are properly formatted: a/b → \frac{a}{b}
        # Only convert if not already in LaTeX format
        def replace_fraction(match):
            # Don't convert if part of a LaTeX command
            if match.start() > 0 and result[match.start()-1] == '\\':
                return match.group(0)
            a, b = match.group(1), match.group(2)
            return f'\\frac{{{a}}}{{{b}}}'
        
        result = re.sub(
            r'([A-Za-z0-9_]+)\s*/\s*([A-Za-z0-9_]+)',
            replace_fraction,
            result
        )
        
        return result
    
    def _format_variable_with_subscript(self, var: str, subscript: str) -> str:
        """Format a variable with subscript in LaTeX."""
        # Extract the subscript part after underscore if exists
        if '_' in subscript:
            parts = subscript.split('_')
            base = parts[0]
            # Join remaining parts with underscore
            sub = '_'.join(parts[1:])
            return f"{var}_{{{base}_{{{sub}}}}}"
        else:
            return f"{var}_{{{subscript}}}"
    
    def process_text_with_formulas(self, text: str) -> str:
        """
        Process a text block, detecting formulas and wrapping them in LaTeX delimiters.
        
        Args:
            text: Multi-line text potentially containing formulas
        
        Returns:
            Text with detected formulas wrapped in $...$ or $$...$$
        """
        lines = text.split('\n')
        result = []
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Check if this line or group of lines is a formula
            if self.detector.is_likely_formula_line(line):
                # Collect consecutive formula lines
                formula_block = [line]
                j = i + 1
                
                # Look ahead for related formula lines (avoid collecting unrelated content)
                while j < len(lines) and len(formula_block) < 3:
                    next_line = lines[j]
                    # Continue only if next line is formula-like or an explicit continuation token.
                    continuation = bool(re.match(r'^\s*[=+\-*/,)]+\s*\S+', next_line))
                    if self.detector.is_likely_formula_line(next_line) or continuation:
                        formula_block.append(next_line)
                        j += 1
                    else:
                        break
                
                # Process the formula block
                formula_text = '\n'.join(formula_block)
                normalized = self.normalize_unicode_math(formula_text)

                # Only wrap when block contains strict equation-like content.
                strict_count = sum(1 for l in formula_block if self.detector.is_strict_formula_line(l))
                if strict_count == 0:
                    result.extend(formula_block)
                    i = j
                    continue
                
                # Multi-line formulas should use $$...$$
                if len(formula_block) > 1 or '\n' in normalized:
                    result.append(f"$$\n{normalized}\n$$")
                else:
                    result.append(f"${normalized}$")
                
                i = j
            else:
                # Regular text line
                result.append(line)
                i += 1
        
        processed = '\n'.join(result)

        # Post-filter: remove $$...$$ wrappers that are likely false positives
        def _is_real_math_block(block: str) -> bool:
            """Heuristic: decide if a $$...$$ block contains math.

            Returns True if block likely contains math; False if it's prose.
            """
            inner = block.strip()
            # If user LaTeX commands present, treat as math
            if '\\' in inner:
                return True

            lines = [l.strip() for l in inner.splitlines() if l.strip()]
            if not lines:
                return False

            # Keep only when strict equation-like content exists.
            strict_formula_like = sum(1 for l in lines if self.detector.is_strict_formula_line(l))
            if strict_formula_like > 0:
                return True

            # Count math-character density (operators, subscripts, superscripts)
            math_chars = sum(1 for c in inner if c in UNICODE_TO_LATEX_MAP or c in SUBSCRIPT_MAP or c in SUPERSCRIPT_MAP or c in '+-=*/^_%{}()')
            char_density = math_chars / max(1, len(inner))
            if char_density > 0.08:
                return True

            # If the block contains mostly CJK or long prose words, treat as non-math
            # Count letters vs CJK characters
            letters = sum(1 for c in inner if c.isalpha())
            cjk = sum(1 for c in inner if '\u4e00' <= c <= '\u9fff')
            if cjk > letters:
                return False

            return False

        # Replace false-positive $$ blocks with their inner text (remove wrappers)
        def _unwrap_false_positives(text_in: str) -> str:
            pattern = re.compile(r"\$\$\n(.*?)\n\$\$", re.DOTALL)

            def repl(m):
                inner = m.group(1)
                if _is_real_math_block(inner):
                    return m.group(0)
                # unwrap
                return inner

            return pattern.sub(repl, text_in)

        processed = _unwrap_false_positives(processed)
        return processed


def convert_corrupted_formulas_in_pdf(text: str) -> str:
    """
    Standalone function to process extracted PDF text and convert corrupted formulas to LaTeX.
    
    Args:
        text: Raw text extracted from PDF
    
    Returns:
        Text with formulas normalized and wrapped in LaTeX delimiters
    """
    converter = FormulaConverter()
    return converter.process_text_with_formulas(text)
