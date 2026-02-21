import re
from typing import Dict, Any, List

def analyze_typescript_code(code: str) -> Dict[str, Any]:
    """
    Perform basic static analysis on TypeScript code.
    """
    issues = []
    lines = code.split('\n')

    for line_num, line in enumerate(lines, 1):
        stripped_line = line.strip()

        # 1. Missing semicolons (basic check, similar to JS)
        if (stripped_line and 
            not stripped_line.endswith((';', '{', '}', ':', ',')) and 
            not stripped_line.startswith(('if', 'for', 'while', 'function', 'class', 'const', 'let', 'var', '}', 'else', 'try', 'catch', 'finally', 'interface', 'type', 'enum'))):
            issues.append({
                "type": "linter",
                "tool": "builtin_ts",
                "severity": "warning",
                "line": line_num,
                "column": len(line) - len(line.lstrip()),
                "message": "Missing semicolon at end of statement.",
                "rule_id": "ts-semi"
            })

        # 2. Use of `var` instead of `let`/`const`
        if 'var ' in stripped_line:
            issues.append({
                "type": "linter",
                "tool": "builtin_ts",
                "severity": "warning",
                "line": line_num,
                "column": stripped_line.find('var'),
                "message": "Use 'let' or 'const' instead of 'var' for block scoping.",
                "rule_id": "ts-no-var"
            })
            
        # 3. Explicit `any` type usage (discouraged)
        if re.search(r':\s*any\b', stripped_line):
            issues.append({
                "type": "linter",
                "tool": "builtin_ts",
                "severity": "warning",
                "line": line_num,
                "column": stripped_line.find(': any'),
                "message": "Avoid using the 'any' type. Prefer specific types or 'unknown'.",
                "rule_id": "ts-no-any"
            })

        # 4. Console.log statements
        if 'console.log' in stripped_line:
            issues.append({
                "type": "linter",
                "tool": "builtin_ts",
                "severity": "info",
                "line": line_num,
                "column": stripped_line.find('console.log'),
                "message": "Unexpected console statement. Remove before production.",
                "rule_id": "ts-no-console"
            })

    return {
        "success": True,
        "language": "typescript",
        "linter_feedback": issues,
        "raw_output": "Built-in TypeScript analysis completed.",
        "errors": None,
        "return_code": 0
    }

def validate_typescript_syntax(code: str) -> Dict[str, Any]:
    """
    Basic TypeScript syntax validation (very limited, primarily for unclosed braces).
    """
    brace_count = code.count('{') - code.count('}')
    paren_count = code.count('(') - code.count(')')
    bracket_count = code.count('[') - code.count(']')

    if brace_count != 0:
        return {"valid": False, "error": "Syntax Error: Unmatched curly braces."}
    if paren_count != 0:
        return {"valid": False, "error": "Syntax Error: Unmatched parentheses."}
    if bracket_count != 0:
        return {"valid": False, "error": "Syntax Error: Unmatched square brackets."}

    return {"valid": True, "error": None}

# This file is now deprecated. TypeScript analysis is handled by ESLint in javascript_analyzer.py.
# Keeping it as a placeholder for clarity, but its content is effectively moved.
# You can delete this file if you prefer, but ensure all imports are updated.
