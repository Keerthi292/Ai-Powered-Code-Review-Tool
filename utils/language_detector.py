import re
from typing import Optional, Dict, Any, List
from config import LANGUAGE_PATTERNS, FILE_EXTENSIONS, LANGUAGE_INFO 

def detect_language(code: str, filename: Optional[str] = None) -> str:
    """
    Detect the programming language of the given code.
    
    Args:
        code: Source code string
        filename: Optional filename for extension-based detection
        
    Returns:
        Detected language name ('python', 'javascript', etc., or 'unknown')
    """
    if not code.strip():
        return "unknown"
    
    if filename:
        lang_from_extension = detect_language_from_filename(filename)
        if lang_from_extension != "unknown":
            return lang_from_extension
    
    # Then try shebang detection (if patterns are defined in LANGUAGE_INFO)
    lang_from_shebang = detect_language_from_shebang(code)
    if lang_from_shebang != "unknown":
        return lang_from_shebang
    
    # Finally, use pattern matching
    return detect_language_from_patterns(code)

def detect_language_from_filename(filename: str) -> str:
    """
    Detect language from file extension.
    
    Args:
        filename: Name of the file
        
    Returns:
        Language name or 'unknown'
    """
    if not filename:
        return "unknown"
    
    # Get file extension
    extension = None
    if '.' in filename:
        extension = '.' + filename.split('.')[-1].lower()
    
    return FILE_EXTENSIONS.get(extension, "unknown")

def detect_language_from_shebang(code: str) -> str:
    """
    Detect language from shebang line.
    
    Args:
        code: Source code string
        
    Returns:
        Language name or 'unknown'
    """
    lines = code.split('\n')
    if not lines:
        return "unknown"
    
    first_line = lines[0].strip()
    if not first_line.startswith('#!'):
        return "unknown"
    
    # Check against known shebang patterns
    for language, info in LANGUAGE_INFO.items():
        for pattern in info.get('shebang_patterns', []):
            if re.search(pattern, first_line, re.IGNORECASE):
                return language
    
    return "unknown"

def detect_language_from_patterns(code: str) -> str:
    """
    Detect language using pattern matching with improved scoring and priority.
    
    Args:
        code: Source code string
        
    Returns:
        Language name or 'unknown'
    """
    language_scores = {}
    
    # First, check for very distinctive patterns that should take priority
    
    # HTML/CSS - Check first as it's most distinctive
    html_css_distinctive = [
        r'<!DOCTYPE\s+html>',
        r'<html[^>]*>',
        r'<head\s*>',
        r'<body[^>]*>',
        r'<div[^>]*>',
        r'<p[^>]*>',
        r'<style[^>]*>',
        r'</\w+>',
        r'\.[\w-]+\s*\{[^}]*\}',  # CSS class with rules
        r'#[\w-]+\s*\{[^}]*\}'   # CSS ID with rules
    ]
    
    # Python - very distinctive patterns
    python_distinctive = [
        r'def\s+\w+\s*$$[^)]*$$\s*:',
        r'class\s+\w+\s*$$[^)]*$$\s*:',
        r'if\s+__name__\s*==\s*[\'"]__main__[\'"]',
        r'elif\s+',
        r'from\s+\w+\s+import',
        r'import\s+\w+\s*$',
        r'@\w+\s*$',  # decorators
        r'lambda\s+\w*:',
        r'yield\s+',
        r'with\s+\w+.*:\s*$',
        r'try\s*:\s*$',
        r'except\s+.*:\s*$',
        r'print\s*\('
    ]
    
    # Java - very distinctive patterns
    java_distinctive = [
        r'public\s+class\s+\w+',
        r'public\s+static\s+void\s+main\s*\(',
        r'System\.out\.println',
        r'import\s+java\.',
        r'@Override',
        r'extends\s+\w+',
        r'implements\s+\w+',
        r'private\s+\w+\s+\w+\s*[;=]',
        r'public\s+\w+\s+\w+\s*[;=]'
    ]
    
    # C/C++ - very distinctive patterns  
    cpp_distinctive = [
        r'#include\s*<[^>]+>',
        r'std::\w+',
        r'cout\s*<<',
        r'cin\s*>>',
        r'#define\s+\w+',
        r'typedef\s+',
        r'malloc\s*\(',
        r'free\s*\(',
        r'int\s+main\s*\(',
        r'printf\s*\(',
        r'scanf\s*\('
    ]
    
    # TypeScript - very distinctive patterns
    ts_distinctive = [
        r':\s*\w+\s*[=;]',  # Type annotations
        r'interface\s+\w+\s*\{',
        r'type\s+\w+\s*=',
        r'public\s+\w+\s*:\s*\w+',
        r'private\s+\w+\s*:\s*\w+',
        r'protected\s+\w+\s*:\s*\w+',
        r'enum\s+\w+\s*\{',
        r'as\s+\w+',
        r'<\w+>',  # Generic types
        r'function\s+\w+\s*$$[^)]*$$\s*:\s*\w+'
    ]
    
    # Go - very distinctive patterns
    go_distinctive = [
        r'package\s+\w+',
        r'func\s+main\s*$$\s*$$',
        r'fmt\.Print',
        r':=\s*',
        r'go\s+\w+\s*\(',
        r'chan\s+\w+',
        r'defer\s+',
        r'range\s+',
        r'import\s*\(\s*$'
    ]
    
    # JavaScript - be more specific to avoid false positives
    javascript_distinctive = [
        r'function\s+\w+\s*$$[^)]*$$\s*\{',  # Function without type annotations
        r'const\s+\w+\s*=\s*function',
        r'let\s+\w+\s*=\s*function',
        r'var\s+\w+\s*=\s*function',
        r'=>\s*\{',
        r'console\.log\s*\(',
        r'document\.',
        r'window\.',
        r'require\s*\([\'"]',
        r'module\.exports\s*=',
        r'export\s+(default\s+)?function',
        r'import\s+.*from\s+[\'"]',
        r'async\s+function\s+\w+',
        r'await\s+\w+\s*\(',
        r'Promise\.',
        r'\.then\s*\(',
        r'\.catch\s*\('
    ]
    
    # Check distinctive patterns first with high scores
    distinctive_patterns = {
        'html_css': html_css_distinctive,
        'python': python_distinctive,
        'java': java_distinctive,
        'c_cpp': cpp_distinctive, 
        'typescript': ts_distinctive,
        'go': go_distinctive,
        'javascript': javascript_distinctive
    }
    
    # Score distinctive patterns with high weight
    for language, patterns in distinctive_patterns.items():
        score = 0
        for pattern in patterns:
            matches = len(re.findall(pattern, code, re.MULTILINE | re.IGNORECASE))
            if matches > 0:
                score += matches * 10  # High weight for distinctive patterns
        language_scores[language] = score
    
    # Additional negative scoring to prevent false positives
    
    # If HTML tags are present, it's definitely HTML/CSS, not TypeScript
    if re.search(r'</?[a-zA-Z][^>]*>', code):
        language_scores['html_css'] = language_scores.get('html_css', 0) + 50
        language_scores['typescript'] = max(0, language_scores.get('typescript', 0) - 30)
        language_scores['javascript'] = max(0, language_scores.get('javascript', 0) - 20)
    
    # If Python-specific syntax is present, it's definitely Python
    if (re.search(r'def\s+\w+\s*$$[^)]*$$\s*:', code) or 
        re.search(r'elif\s+', code) or
        re.search(r'if\s+__name__\s*==', code)):
        language_scores['python'] = language_scores.get('python', 0) + 50
        language_scores['javascript'] = max(0, language_scores.get('javascript', 0) - 30)
        language_scores['typescript'] = max(0, language_scores.get('typescript', 0) - 30)
    
    # If Java-specific syntax is present, it's definitely Java
    if (re.search(r'public\s+class\s+\w+', code) or 
        re.search(r'System\.out\.println', code) or
        re.search(r'public\s+static\s+void\s+main', code)):
        language_scores['java'] = language_scores.get('java', 0) + 50
        language_scores['javascript'] = max(0, language_scores.get('javascript', 0) - 30)
        language_scores['typescript'] = max(0, language_scores.get('typescript', 0) - 30)
    
    # If C/C++-specific syntax is present, it's definitely C/C++
    if (re.search(r'#include\s*<', code) or 
        re.search(r'std::', code) or
        re.search(r'cout\s*<<', code)):
        language_scores['c_cpp'] = language_scores.get('c_cpp', 0) + 50
        language_scores['javascript'] = max(0, language_scores.get('javascript', 0) - 30)
        language_scores['typescript'] = max(0, language_scores.get('typescript', 0) - 30)
    
    # If TypeScript-specific syntax is present, it's TypeScript not JavaScript
    if (re.search(r':\s*\w+\s*[=;]', code) or 
        re.search(r'interface\s+\w+', code) or
        re.search(r'type\s+\w+\s*=', code)):
        language_scores['typescript'] = language_scores.get('typescript', 0) + 50
        language_scores['javascript'] = max(0, language_scores.get('javascript', 0) - 30)
    
    # If Go-specific syntax is present, it's definitely Go
    if (re.search(r'package\s+\w+', code) or 
        re.search(r'func\s+main\s*$$\s*$$', code) or
        re.search(r'fmt\.', code)):
        language_scores['go'] = language_scores.get('go', 0) + 50
        language_scores['javascript'] = max(0, language_scores.get('javascript', 0) - 30)
        language_scores['typescript'] = max(0, language_scores.get('typescript', 0) - 30)
    
    # If no distinctive patterns matched strongly, fall back to general patterns
    if not any(score >= 10 for score in language_scores.values()):
        for language, patterns in LANGUAGE_PATTERNS.items():
            if language not in language_scores:
                language_scores[language] = 0
                
            for pattern in patterns:
                matches = len(re.findall(pattern, code, re.MULTILINE | re.IGNORECASE))
                # Give JavaScript lower weight to prevent false positives
                weight = 1 if language == 'javascript' else 2
                language_scores[language] += matches * weight
    
    # Return the language with the highest score
    if language_scores:
        best_language = max(language_scores, key=language_scores.get)
        best_score = language_scores[best_language]
        
        # Only return if we have a reasonable confidence
        if best_score >= 5:  # Lowered threshold slightly
            return best_language
    
    return "unknown"

def get_language_confidence(code: str, language: str) -> float:
    """
    Get confidence score for a specific language detection.
    
    Args:
        code: Source code string
        language: Language to check confidence for
        
    Returns:
        Confidence score between 0.0 and 1.0
    """
    if language not in LANGUAGE_PATTERNS:
        return 0.0
    
    patterns = LANGUAGE_PATTERNS[language]
    total_patterns = len(patterns)
    matched_patterns = 0
    
    for pattern in patterns:
        if re.search(pattern, code, re.MULTILINE | re.IGNORECASE):
            matched_patterns += 1
    
    return matched_patterns / total_patterns if total_patterns > 0 else 0.0

def analyze_code_characteristics(code: str) -> Dict[str, Any]:
    """
    Analyze various characteristics of the code.
    
    Args:
        code: Source code string
        
    Returns:
        Dictionary with code characteristics
    """
    lines = code.split('\n')
    
    characteristics = {
        "total_lines": len(lines),
        "non_empty_lines": len([line for line in lines if line.strip()]),
        "comment_lines": 0,
        "has_functions": False,
        "has_classes": False,
        "has_imports": False,
        "indentation_style": detect_indentation_style(code),
        "average_line_length": 0,
        "max_line_length": 0
    }
    
    # Count comment lines and analyze content
    for line in lines:
        stripped = line.strip()
        
        # Comment detection
        if stripped.startswith('#') or stripped.startswith('//') or stripped.startswith('/*'):
            characteristics["comment_lines"] += 1
        
        # Function detection
        if re.search(r'(def\s+\w+|function\s+\w+|func\s+\w+\(|public\s+\w+\s+\w+\()', line):
            characteristics["has_functions"] = True
        
        # Class detection
        if re.search(r'(class\s+\w+|public\s+class\s+\w+|interface\s+\w+)', line):
            characteristics["has_classes"] = True
        
        # Import detection
        if re.search(r'(import\s+|from\s+\w+\s+import|require\s*\()', line):
            characteristics["has_imports"] = True
        
        # Line length analysis
        line_length = len(line)
        characteristics["max_line_length"] = max(characteristics["max_line_length"], line_length)
    
    # Calculate average line length
    if characteristics["non_empty_lines"] > 0:
        total_length = sum(len(line) for line in lines if line.strip())
        characteristics["average_line_length"] = total_length / characteristics["non_empty_lines"]
    
    return characteristics

def detect_indentation_style(code: str) -> str:
    """
    Detect the indentation style used in the code.
    
    Args:
        code: Source code string
        
    Returns:
        Indentation style ('spaces', 'tabs', 'mixed', or 'none')
    """
    lines = code.split('\n')
    space_indented = 0
    tab_indented = 0
    
    for line in lines:
        if line.startswith('    '):  # 4 spaces
            space_indented += 1
        elif line.startswith('  '):   # 2 spaces
            space_indented += 1
        elif line.startswith('\t'):   # tab
            tab_indented += 1
    
    if space_indented > 0 and tab_indented > 0:
        return "mixed"
    elif space_indented > 0:
        return "spaces"
    elif tab_indented > 0:
        return "tabs"
    else:
        return "none"

def get_language_info(language: str) -> Dict[str, Any]:
    """
    Get detailed information about a programming language.
    
    Args:
        language: Language name
        
    Returns:
        Dictionary with language information
    """
    return LANGUAGE_INFO.get(language.lower(), {
        "name": language.title(),
        "extensions": [],
        "linter": "Unknown",
        "description": f"Programming language: {language}"
    })

def get_supported_languages() -> List[str]:
    """
    Get list of supported programming languages.
    
    Returns:
        List of supported language names
    """
    return list(LANGUAGE_INFO.keys())

def is_language_supported(language: str) -> bool:
    """
    Check if a programming language is supported.
    
    Args:
        language: Language name to check
        
    Returns:
        True if supported, False otherwise
    """
    return language.lower() in LANGUAGE_INFO

def detect_code_complexity(code: str) -> Dict[str, Any]:
    """
    Analyze code complexity metrics.
    
    Args:
        code: Source code string
        
    Returns:
        Dictionary with complexity metrics
    """
    lines = code.split('\n')
    
    complexity = {
        "cyclomatic_complexity": 1,  # Base complexity
        "nesting_depth": 0,
        "function_count": 0,
        "class_count": 0,
        "conditional_statements": 0,
        "loop_statements": 0
    }
    
    current_depth = 0
    max_depth = 0
    
    for line in lines:
        stripped = line.strip()
        
        # Count leading whitespace for nesting depth (simplified)
        if stripped:
            leading_spaces = len(line) - len(line.lstrip())
            # Heuristic for block start (Python-like)
            if re.search(r'(if|for|while|try|with|def|class|func|public class|private class|interface|enum)\s*[:({]', line):
                current_depth = leading_spaces // 4  # Assuming 4-space indentation
                max_depth = max(max_depth, current_depth)
        
        # Count various constructs
        if re.search(r'(def\s+\w+|function\s+\w+|func\s+\w+\(|public\s+\w+\s+\w+\()', line):
            complexity["function_count"] += 1
        
        if re.search(r'(class\s+\w+|public\s+class\s+\w+|interface\s+\w+)', line):
            complexity["class_count"] += 1
        
        if re.search(r'(if\s+|elif\s+|else\s*:|switch\s*\(|case\s+|default\s*:)', line):
            complexity["conditional_statements"] += 1
            complexity["cyclomatic_complexity"] += 1
        
        if re.search(r'(for\s+|while\s+|do\s+while)', line):
            complexity["loop_statements"] += 1
            complexity["cyclomatic_complexity"] += 1
    
    complexity["nesting_depth"] = max_depth
    
    return complexity
