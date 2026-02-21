import os
import re
from typing import Dict, Any, List

# ================================
# API CONFIGURATION
# ================================

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4o-mini"
OPENAI_MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "2000"))
OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.3"))
OPENAI_TIMEOUT = int(os.getenv("OPENAI_TIMEOUT", "30"))

# ================================
# LINTER CONFIGURATION
# ================================

# Pylint Configuration
PYLINT_CONFIG = {
    "disable": [
        "C0114",  # missing-module-docstring
        "C0115",  # missing-class-docstring
        "C0116",  # missing-function-docstring
        "R0903",  # too-few-public-methods
        "C0103",  # invalid-name
        "W0613",  # unused-argument (for demos)
    ],
    "enable": [
        "W0611",  # unused-import
        "W0612",  # unused-variable
        "E1101",  # no-member
        "E0602",  # undefined-variable
    ],
    "output_format": "json",
    "score": False,
    "reports": False,
    "max_line_length": 100,
    "good_names": ["i", "j", "k", "ex", "Run", "_", "id", "pk"],
    "bad_names": ["foo", "bar", "baz", "toto", "tutu", "tata"]
}

# ESLint Configuration (for JavaScript and TypeScript)
ESLINT_CONFIG = {
    "extends": ["eslint:recommended"],
    "parserOptions": {
        "ecmaVersion": 2021,
        "sourceType": "module", # Use module for modern JS/TS
        "ecmaFeatures": {
            "jsx": True
        }
    },
    "env": {
        "browser": True,
        "node": True,
        "es6": True
    },
    "rules": {
        "no-unused-vars": "warn",
        "no-console": "off",
        "no-undef": "warn",
        "semi": ["warn", "always"],
        "quotes": ["warn", "single"],
        "indent": ["warn", 2],
        "no-trailing-spaces": "warn",
        "eol-last": "warn",
        "no-multiple-empty-lines": ["warn", {"max": 2}],
        "brace-style": ["warn", "1tbs"],
        "comma-dangle": ["warn", "never"],
        "no-var": "warn",
        "prefer-const": "warn",
        "arrow-spacing": "warn",
        # TypeScript specific rules (requires @typescript-eslint/parser and plugins)
        "@typescript-eslint/no-unused-vars": ["warn", { "argsIgnorePattern": "^_" }],
        "@typescript-eslint/explicit-function-return-type": "off",
        "@typescript-eslint/no-explicit-any": "warn"
    },
    # Add settings for TypeScript if @typescript-eslint/parser is used
    "settings": {
        "import/resolver": {
            "node": {
                "extensions": [".js", ".jsx", ".ts", ".tsx"]
            }
        }
    }
}

# Checkstyle Configuration (for Java)
# This is a placeholder. In a real scenario, you'd point to a .xml config file.
CHECKSTYLE_CONFIG = {
    "path": "checkstyle-8.36-all.jar", # Path to your Checkstyle JAR
    "config_file": "google_checks.xml", # Or sun_checks.xml, or your custom config
    "rules": [
        "MissingJavadocMethod",
        "EmptyBlock",
        "UnusedImports",
        "LineLength",
        "VisibilityModifier"
    ]
}

# Cppcheck Configuration (for C/C++)
CPPCHECK_CONFIG = {
    "enable": "all", # Enable all checks
    "suppress": [],  # List of checks to suppress
    "platform": "unix64" # or win64, etc.
}


# Stylelint Configuration (for HTML/CSS)
STYLELINT_CONFIG = {
    "extends": ["stylelint-config-standard"], # A popular base config
    "rules": {
        "indentation": 2,
        "selector-list-comma-newline-after": "always",
        "block-closing-brace-newline-after": "always",
        "declaration-colon-space-after": "always",
        "declaration-no-important": True, # Disallow !important
        "color-no-invalid-hex": True,
        "unit-no-unknown": True,
        "property-no-unknown": True,
        "no-empty-source": True,
        "no-duplicate-selectors": True,
        "no-descending-specificity": True
    }
}


# ================================
# UI CONFIGURATION
# ================================

# Severity Colors and Icons (Updated with new emojis)
SEVERITY_COLORS: Dict[str, str] = {
    "error": "🟥", # High severity
    "high": "🟥",  # High severity
    "warning": "🟧", # Medium severity
    "medium": "🟧", # Medium severity
    "info": "🟩",   # Low severity
    "low": "🟩",    # Low severity
    "suggestion": "💡", # AI suggestion
    "fixable": "🔧" # Fixable issue
}

# Severity Priority (for sorting)
SEVERITY_PRIORITY: Dict[str, int] = {
    "critical": 5,
    "error": 4,
    "high": 4,
    "warning": 3,
    "medium": 3,
    "info": 2,
    "low": 1,
    "convention": 1,
    "refactor": 2,
    "suggestion": 2 # AI suggestions are generally medium/low priority
}

# UI Theme Colors
UI_COLORS = {
    "primary": "#667eea",
    "secondary": "#764ba2",
    "success": "#28a745",
    "warning": "#ffc107",
    "danger": "#dc3545",
    "info": "#17a2b8",
    "light": "#f8f9fa",
    "dark": "#343a40"
}

# ================================
# LANGUAGE DETECTION
# ================================

# Language Detection Patterns (Improved for better accuracy and less overlap)
LANGUAGE_PATTERNS = {
    "python": [
        r"def\s+\w+\s*$$[^)]*$$\s*:",   # function definitions with colon
        r"class\s+\w+\s*$$[^)]*$$\s*:", # class definitions with colon  
        r"import\s+\w+$",               # import statements (end of line)
        r"from\s+\w+\s+import",         # from import statements
        r"if\s+__name__\s*==\s*['\"]__main__['\"]",  # main guard
        r"print\s*\(",                  # print function
        r"elif\s+",                     # elif statements (Python-specific)
        r"^\s*#[^!]",                   # comments starting with # (not shebang)
        r"@\w+\s*$",                    # decorators (end of line)
        r"lambda\s+\w+:",               # lambda functions with colon
        r"yield\s+",                    # yield statements
        r"with\s+\w+.*:\s*$",           # with statements with colon
        r"try\s*:\s*$",                 # try blocks with colon
        r"except\s+.*:\s*$",            # except blocks with colon
        r"finally\s*:\s*$",             # finally blocks with colon
    ],
    "javascript": [
        r"function\s+\w+\s*$$[^)]*$$\s*\{", # function declarations with brace
        r"const\s+\w+\s*=\s*function",      # const function assignments
        r"let\s+\w+\s*=\s*function",        # let function assignments
        r"var\s+\w+\s*=\s*function",        # var function assignments
        r"=>\s*\{",                         # arrow functions with braces
        r"console\.log\s*\(",               # console.log (JS-specific)
        r"document\.",                      # DOM access (browser JS)
        r"window\.",                        # window object (browser JS)
        r"require\s*\(['\"]",               # require statements with quotes
        r"module\.exports\s*=",             # module exports
        r"export\s+(default\s+)?function",  # ES6 function exports
        r"import\s+.*from\s+['\"]",         # ES6 imports with quotes
        r"async\s+function\s+\w+",          # async functions
        r"await\s+\w+\s*\(",                # await expressions
        r"Promise\.",                       # Promise usage
        r"\.then\s*\(",                     # Promise then
        r"\.catch\s*\(",                    # Promise catch
        r"//.*$",                           # single line comments
        r"/\*.*?\*/",                       # multi-line comments
    ],
    "java": [
        r"public\s+class\s+\w+\s*\{",       # public class definition
        r"public\s+static\s+void\s+main\s*\(", # main method
        r"System\.out\.println\s*\(",       # print statement
        r"import\s+java\.\w+",              # java import statement
        r"import\s+\w+(\.\w+)*;\s*$",       # general import with semicolon
        r"new\s+\w+\s*\(",                  # object instantiation
        r"private\s+(static\s+)?\w+",       # private modifier
        r"protected\s+(static\s+)?\w+",     # protected modifier
        r"public\s+(static\s+)?\w+",        # public modifier
        r"final\s+\w+",                     # final keyword
        r"try\s*\{\s*$",                    # try block
        r"catch\s*\(\s*\w+",                # catch block
        r"throws\s+\w+Exception",           # throws declaration
        r"@Override\s*$",                   # annotation
        r"extends\s+\w+\s*\{",              # inheritance
        r"implements\s+\w+\s*\{",           # interface implementation
    ],
    "c_cpp": [
        r"#include\s*<[^>]+>\s*$",          # include directive with angle brackets
        r"#include\s*\"[^\"]+\"\s*$",       # include directive with quotes
        r"int\s+main\s*$$\s*(void\s*)?$$",  # main function
        r"std::\w+",                        # C++ standard library
        r"cout\s*<<",                       # C++ output
        r"cin\s*>>",                        # C++ input
        r"printf\s*\(",                     # C output
        r"scanf\s*\(",                      # C input
        r"namespace\s+\w+\s*\{",            # namespace
        r"class\s+\w+\s*\{\s*$",            # class definition with brace
        r"struct\s+\w+\s*\{\s*$",           # struct definition
        r"void\s+\w+\s*$$[^)]*$$\s*\{",     # void function
        r"return\s+0\s*;\s*$",              # common return
        r"#define\s+\w+",                   # macro definition
        r"typedef\s+\w+",                   # typedef
        r"malloc\s*\(",                     # memory allocation
        r"free\s*\(",                       # memory deallocation
    ],
    "typescript": [
        r"function\s+\w+\s*$$[^)]*$$\s*:\s*\w+", # function with return type
        r"const\s+\w+\s*:\s*\w+\s*=",       # typed const declaration
        r"let\s+\w+\s*:\s*\w+\s*(=|;)",     # typed let declaration
        r"interface\s+\w+\s*\{\s*$",        # interface definition
        r"type\s+\w+\s*=\s*\{",             # type alias with object
        r"public\s+\w+\s*:\s*\w+",          # class property with type
        r"private\s+\w+\s*:\s*\w+",         # private property with type
        r"protected\s+\w+\s*:\s*\w+",       # protected property with type
        r"import\s+type\s+\{",              # type-only import
        r"export\s+type\s+\w+",             # type export
        r"enum\s+\w+\s*\{\s*$",             # enum definition
        r"as\s+\w+\s*[;,\)]",               # type assertion
        r"<\w+>\s*\(",                      # generic function call
        r"implements\s+\w+\s*\{",           # interface implementation
        r"extends\s+\w+\s*\{",              # class/interface extension
    ],
    "go": [
        r"package\s+\w+\s*$",               # package declaration
        r"func\s+main\s*$$\s*$$\s*\{",      # main function
        r"func\s+\w+\s*$$[^)]*$$\s*\{",     # function definition
        r"fmt\.Print\w*\s*\(",              # print statement
        r"fmt\.Scan\w*\s*\(",               # scan statement
        r"import\s*\(\s*$",                 # import block
        r"import\s+\"[^\"]+\"\s*$",         # single import
        r"var\s+\w+\s+\w+\s*(=|$)",        # var declaration with type
        r"const\s+\w+\s+=",                 # const declaration
        r"\w+\s*:=\s*",                     # short variable declaration
        r"go\s+\w+\s*\(",                   # goroutine
        r"chan\s+\w+",                      # channel
        r"select\s*\{\s*$",                 # select statement
        r"defer\s+\w+\s*\(",                # defer statement
        r"range\s+\w+\s*\{",                # range keyword
        r"make\s*\(\s*\w+",                 # make function
    ],
    "html_css": [
        r"<!DOCTYPE\s+html>\s*$",           # HTML doctype
        r"<html[^>]*>\s*$",                 # HTML tag
        r"<head\s*>\s*$",                   # head tag
        r"<body[^>]*>\s*$",                 # body tag
        r"<div[^>]*>",                      # div tag
        r"<p\s*>",                          # paragraph tag
        r"<style[^>]*>\s*$",                # style tag
        r"<script[^>]*>\s*$",               # script tag
        r"</\w+>\s*$",                      # closing tag
        r"\.[\w-]+\s*\{[^}]*\}",            # CSS class selector with rules
        r"#[\w-]+\s*\{[^}]*\}",             # CSS ID selector with rules
        r"\w+\s*\{\s*[\w-]+\s*:",           # CSS element selector with property
        r"color\s*:\s*[^;]+;",              # CSS color property
        r"background-color\s*:\s*[^;]+;",   # CSS background property
        r"display\s*:\s*[^;]+;",            # CSS display property
        r"margin\s*:\s*[^;]+;",             # CSS margin property
        r"padding\s*:\s*[^;]+;",            # CSS padding property
    ]
}

# File Extensions Mapping
FILE_EXTENSIONS = {
    ".py": "python",
    ".pyw": "python",
    ".py3": "python",
    ".pyi": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".mjs": "javascript",
    ".cjs": "javascript",
    ".ts": "typescript",  # TypeScript
    ".tsx": "typescript", # TypeScript React
    ".java": "java",
    ".c": "c_cpp",
    ".cpp": "c_cpp",
    ".h": "c_cpp",
    ".hpp": "c_cpp",
    ".go": "go",
    ".html": "html_css",
    ".htm": "html_css",
    ".css": "html_css",
}

# Language Information (Expanded with specific linters)
LANGUAGE_INFO = {
    "python": {
        "name": "Python",
        "extensions": [".py", ".pyw", ".py3", ".pyi"],
        "linter": "Pylint",
        "description": "A high-level, interpreted programming language",
        "official_style_guide": "PEP 8",
        "common_frameworks": ["Django", "Flask", "FastAPI", "Pandas", "NumPy"],
        "file_patterns": ["*.py", "*.pyw"],
        "shebang_patterns": [r"#!/usr/bin/python", r"#!/usr/bin/env python"]
    },
    "javascript": {
        "name": "JavaScript",
        "extensions": [".js", ".jsx", ".mjs", ".cjs"],
        "linter": "ESLint",
        "description": "A dynamic programming language for web development",
        "official_style_guide": "Airbnb Style Guide",
        "common_frameworks": ["React", "Vue", "Angular", "Node.js", "Express"],
        "file_patterns": ["*.js", "*.jsx", "*.mjs"],
        "shebang_patterns": [r"#!/usr/bin/node", r"#!/usr/bin/env node"]
    },
    "java": {
        "name": "Java",
        "extensions": [".java"],
        "linter": "Checkstyle",
        "description": "A class-based, object-oriented programming language",
        "official_style_guide": "Oracle Code Conventions",
        "common_frameworks": ["Spring", "Hibernate", "Maven", "Gradle"],
        "file_patterns": ["*.java"],
        "shebang_patterns": []
    },
    "c_cpp": {
        "name": "C/C++",
        "extensions": [".c", ".cpp", ".h", ".hpp"],
        "linter": "Cppcheck",
        "description": "Powerful, high-performance languages for system programming",
        "official_style_guide": "Google C++ Style Guide",
        "common_frameworks": ["Qt", "Boost", "Unreal Engine"],
        "file_patterns": ["*.c", "*.cpp", "*.h"],
        "shebang_patterns": []
    },
    "typescript": {
        "name": "TypeScript",
        "extensions": [".ts", ".tsx"],
        "linter": "ESLint", # ESLint with TypeScript plugin
        "description": "A superset of JavaScript that adds static types",
        "official_style_guide": "TypeScript Deep Dive",
        "common_frameworks": ["Angular", "NestJS", "React (with TSX)"],
        "file_patterns": ["*.ts", "*.tsx"],
        "shebang_patterns": []
    },
    
    "html_css": {
        "name": "HTML/CSS",
        "extensions": [".html", ".htm", ".css"],
        "linter": "Stylelint",
        "description": "Markup and stylesheet languages for web pages",
        "official_style_guide": "Google HTML/CSS Style Guide",
        "common_frameworks": ["Bootstrap", "Tailwind CSS", "Materialize"],
        "file_patterns": ["*.html", "*.css"],
        "shebang_patterns": []
    }
}

# ================================
# AI PROMPT TEMPLATES
# ================================

# Base system prompts
SYSTEM_PROMPTS = {
    "code_reviewer": "You are an expert code reviewer with years of experience in software development. You provide constructive, specific, and actionable feedback in a friendly, conversational tone. Avoid overly technical jargon unless necessary, and always explain why a suggestion is beneficial. Provide quick fix examples when possible.",
    "python_expert": "You are a Python expert familiar with PEP 8, best practices, and modern Python features. Provide friendly, actionable advice.",
    "javascript_expert": "You are a JavaScript expert familiar with ES6+, modern frameworks, and web development best practices. Provide friendly, actionable advice.",
    "java_expert": "You are a Java expert familiar with common design patterns, best practices, and modern Java features. Provide friendly, actionable advice.",
    "c_cpp_expert": "You are a C/C++ expert familiar with performance optimization, memory management, and secure coding practices. Provide friendly, actionable advice.",
    "typescript_expert": "You are a TypeScript expert familiar with type safety, modern patterns, and best practices for large-scale applications. Provide friendly, actionable advice.",
    "go_expert": "You are a Go expert familiar with concurrency, error handling, and idiomatic Go programming. Provide friendly, actionable advice.",
    "html_css_expert": "You are an HTML/CSS expert familiar with web standards, accessibility, and responsive design. Provide friendly, actionable advice.",
}

# Detailed prompt templates (Updated for human-friendly suggestions)
AI_PROMPT_TEMPLATES: Dict[str, str] = {
    "python": """
You are an expert Python code reviewer. Your goal is to help developers write better, cleaner, and more efficient Python code.

Please analyze the following Python code and provide specific, actionable improvement suggestions. Explain *why* each suggestion is beneficial in a clear, conversational way, avoiding unnecessary jargon. If possible, include a quick code example showing the improvement.

Focus on these areas:
1.  **Readability & Style (PEP 8)**: Is the code easy to read and follow? Does it adhere to Python's style guide?
2.  **Pythonic Idioms**: Are there more "Pythonic" ways to achieve the same result?
3.  **Performance**: Can anything be optimized for speed or memory?
4.  **Error Handling**: Are edge cases handled gracefully?
5.  **Modern Python**: Can newer Python features (f-strings, type hints, etc.) improve the code?
6.  **Code Structure**: Is the code well-organized and modular?

Here's the Python code to review:
\`\`\`python
{code}
\`\`\`

Please provide your suggestions as a JSON array. Each object in the array should have the following format:
\`\`\`json
{{
  "type": "suggestion",
  "severity": "low|medium|high",
  "line": null, // Line number if applicable, otherwise null
  "message": "Your clear, conversational suggestion here.",
  "category": "readability|performance|error_handling|pythonic|modern|structure",
  "example": "Optional code snippet for a quick fix" // Use the correct language for the example
}}
\`\`\`
Focus on the most impactful and easy-to-understand improvements. Return only valid JSON.
""",
    
    "javascript": """
You are an expert JavaScript code reviewer. Your goal is to help developers write better, cleaner, and more efficient JavaScript code.

Please analyze the following JavaScript code and provide specific, actionable improvement suggestions. Explain *why* each suggestion is beneficial in a clear, conversational way, avoiding unnecessary jargon. If possible, include a quick code example showing the improvement.

Focus on these areas:
1.  **Modern JavaScript (ES6+)**: Can newer features like `const`/`let`, arrow functions, `async`/`await`, destructuring, etc., improve the code?
2.  **Readability & Maintainability**: Is the code easy to understand and maintain?
3.  **Performance**: Are there any performance bottlenecks or optimization opportunities?
4.  **Error Handling**: Are potential errors handled gracefully?
5.  **Code Structure**: Is the code well-organized and modular?
6.  **Security**: Are there any potential security vulnerabilities?

Here's the JavaScript code to review:
\`\`\`javascript
{code}
\`\`\`

Please provide your suggestions as a JSON array. Each object in the array should have the following format:
\`\`\`json
{{
  "type": "suggestion",
  "severity": "low|medium|high",
  "line": null, // Line number if applicable, otherwise null
  "message": "Your clear, conversational suggestion here.",
  "category": "modern|readability|performance|error_handling|structure|security",
  "example": "Optional code snippet for a quick fix" // Use the correct language for the example
}}
\`\`\`
Focus on the most impactful and easy-to-understand improvements. Return only valid JSON.
""",
    "java": """
You are an expert Java code reviewer. Your goal is to help developers write better, cleaner, and more efficient Java code.

Please analyze the following Java code and provide specific, actionable improvement suggestions. Explain *why* each suggestion is beneficial in a clear, conversational way, avoiding unnecessary jargon. If possible, include a quick code example showing the improvement.

Focus on these areas:
1.  **Object-Oriented Principles**: Proper use of encapsulation, inheritance, polymorphism.
2.  **Readability & Maintainability**: Is the code easy to understand and maintain?
3.  **Performance**: Can anything be optimized for speed or memory?
4.  **Error Handling**: Are exceptions handled gracefully?
5.  **Modern Java**: Can newer Java features (e.g., Streams, Records, Optional) improve the code?
6.  **Concurrency**: Are thread-safety issues addressed?

Here's the Java code to review:
\`\`\`java
{code}
\`\`\`

Please provide your suggestions as a JSON array. Each object in the array should have the following format:
\`\`\`json
{{
  "type": "suggestion",
  "severity": "low|medium|high",
  "line": null, // Line number if applicable, otherwise null
  "message": "Your clear, conversational suggestion here.",
  "category": "oop|readability|performance|error_handling|modern|concurrency",
  "example": "Optional code snippet for a quick fix"
}}
\`\`\`
Focus on the most impactful and easy-to-understand improvements. Return only valid JSON.
""",
    "c_cpp": """
You are an expert C/C++ code reviewer. Your goal is to help developers write better, cleaner, and more efficient C/C++ code.

Please analyze the following C/C++ code and provide specific, actionable improvement suggestions. Explain *why* each suggestion is beneficial in a clear, conversational way, avoiding unnecessary jargon. If possible, include a quick code example showing the improvement.

Focus on these areas:
1.  **Memory Management**: Proper use of `new`/`delete`, smart pointers, avoiding leaks.
2.  **Performance**: Optimization for speed, cache efficiency, avoiding unnecessary copies.
3.  **Security**: Buffer overflows, integer overflows, input validation.
4.  **Readability & Maintainability**: Is the code easy to understand and maintain?
5.  **Modern C++**: Use of C++11/14/17/20 features (e.g., auto, lambdas, move semantics).
6.  **Concurrency**: Thread safety, race conditions.

Here's the C/C++ code to review:
\`\`\`cpp
{code}
\`\`\`

Please provide your suggestions as a JSON array. Each object in the array should have the following format:
\`\`\`json
{{
  "type": "suggestion",
  "severity": "low|medium|high",
  "line": null, // Line number if applicable, otherwise null
  "message": "Your clear, conversational suggestion here.",
  "category": "memory|performance|security|readability|modern|concurrency",
  "example": "Optional code snippet for a quick fix"
}}
\`\`\`
Focus on the most impactful and easy-to-understand improvements. Return only valid JSON.
""",
    "typescript": """
You are an expert TypeScript code reviewer. Your goal is to help developers write better, cleaner, and more efficient TypeScript code.

Please analyze the following TypeScript code and provide specific, actionable improvement suggestions. Explain *why* each suggestion is beneficial in a clear, conversational way, avoiding unnecessary jargon. If possible, include a quick code example showing the improvement.

Focus on these areas:
1.  **Type Safety**: Proper use of types, interfaces, enums, avoiding `any`.
2.  **Modern TypeScript/JavaScript**: Use of ES6+ and TypeScript-specific features.
3.  **Readability & Maintainability**: Is the code easy to understand and maintain?
4.  **Error Handling**: Are potential errors handled gracefully?
5.  **Code Structure**: Is the code well-organized and modular?

Here's the TypeScript code to review:
\`\`\`typescript
{code}
\`\`\`

Please provide your suggestions as a JSON array. Each object in the array should have the following format:
\`\`\`json
{{
  "type": "suggestion",
  "severity": "low|medium|high",
  "line": null, // Line number if applicable, otherwise null
  "message": "Your clear, conversational suggestion here.",
  "category": "types|modern|readability|error_handling|structure",
  "example": "Optional code snippet for a quick fix"
}}
\`\`\`
Focus on the most impactful and easy-to-understand improvements. Return only valid JSON.
""",
    "go": """
You are an expert Go code reviewer. Your goal is to help developers write better, cleaner, and more efficient Go code.

Please analyze the following Go code and provide specific, actionable improvement suggestions. Explain *why* each suggestion is beneficial in a clear, conversational way, avoiding unnecessary jargon. If possible, include a quick code example showing the improvement.

Focus on these areas:
1.  **Idiomatic Go**: Adherence to Go's conventions and best practices.
2.  **Error Handling**: Proper error propagation and handling.
3.  **Concurrency**: Correct use of goroutines and channels, avoiding deadlocks/race conditions.
4.  **Performance**: Optimization for speed and resource usage.
5.  **Readability & Maintainability**: Is the code easy to understand and maintain?

Here's the Go code to review:
\`\`\`go
{code}
\`\`\`

Please provide your suggestions as a JSON array. Each object in the array should have the following format:
\`\`\`json
{{
  "type": "suggestion",
  "severity": "low|medium|high",
  "line": null, // Line number if applicable, otherwise null
  "message": "Your clear, conversational suggestion here.",
  "category": "idiomatic|error_handling|concurrency|performance|readability",
  "example": "Optional code snippet for a quick fix"
}}
\`\`\`
Focus on the most impactful and easy-to-understand improvements. Return only valid JSON.
""",
    "html_css": """
You are an expert HTML/CSS code reviewer. Your goal is to help developers write better, cleaner, and more efficient web frontends.

Please analyze the following HTML/CSS code and provide specific, actionable improvement suggestions. Explain *why* each suggestion is beneficial in a clear, conversational way, avoiding unnecessary jargon. If possible, include a quick code example showing the improvement.

Focus on these areas:
1.  **Accessibility (A11y)**: Semantic HTML, ARIA attributes, keyboard navigation.
2.  **Responsiveness**: How well does it adapt to different screen sizes?
3.  **Performance**: CSS optimization, image loading, render blocking.
4.  **Maintainability**: Clean CSS, BEM/utility-first, component-based structure.
5.  **Best Practices**: Valid HTML, proper CSS selectors, avoiding inline styles.
6.  **Cross-Browser Compatibility**: Ensuring consistent rendering across browsers.

Here's the HTML/CSS code to review:
\`\`\`html
{code}
\`\`\`

Please provide your suggestions as a JSON array. Each object in the array should have the following format:
\`\`\`json
{{
  "type": "suggestion",
  "severity": "low|medium|high",
  "line": null, // Line number if applicable, otherwise null
  "message": "Your clear, conversational suggestion here.",
  "category": "accessibility|responsiveness|performance|maintainability|best_practices|compatibility",
  "example": "Optional code snippet for a quick fix"
}}
\`\`\`
Focus on the most impactful and easy-to-understand improvements. Return only valid JSON.
"""
}

# ================================
# ANALYSIS CONFIGURATION
# ================================

# Analysis Limits
ANALYSIS_LIMITS = {
    "max_code_length": 50000,      # Maximum characters in code
    "max_lines": 2000,             # Maximum lines of code
    "timeout_seconds": 60,         # Maximum analysis time
    "max_ai_suggestions": 20,      # Maximum AI suggestions to return
    "max_linter_issues": 100       # Maximum linter issues to process
}

# Code Quality Thresholds
QUALITY_THRESHOLDS = {
    "excellent": {"max_issues": 0, "max_high_severity": 0},
    "good": {"max_issues": 3, "max_high_severity": 0},
    "fair": {"max_issues": 10, "max_high_severity": 2},
    "poor": {"max_issues": 20, "max_high_severity": 5},
    "critical": {"max_issues": float('inf'), "max_high_severity": float('inf')}
}

# ================================
# ERROR MESSAGES
# ================================

ERROR_MESSAGES = {
    "no_code": "No code provided for analysis",
    "code_too_long": f"Code exceeds maximum length of {ANALYSIS_LIMITS['max_code_length']} characters",
    "unsupported_language": "Unsupported programming language",
    "syntax_error": "Code contains syntax errors",
    "linter_not_found": "Required linter not installed",
    "api_key_missing": "OpenAI API key not configured",
    "api_rate_limit": "OpenAI API rate limit exceeded",
    "analysis_timeout": "Analysis timed out",
    "network_error": "Network connection error",
    "unknown_error": "An unexpected error occurred"
}

# Success Messages
SUCCESS_MESSAGES = {
    "analysis_complete": "Code analysis completed successfully",
    "no_issues": "No issues found - excellent code quality!",
    "minor_issues": "Minor issues found - overall good code quality",
    "improvements_available": "Several improvement opportunities identified"
}

# ================================
# EXPORT CONFIGURATION
# ================================

# Export formats
EXPORT_FORMATS = {
    "json": {
        "extension": ".json",
        "mime_type": "application/json",
        "description": "JSON format with complete analysis data"
    },
    "markdown": {
        "extension": ".md", 
        "mime_type": "text/markdown",
        "description": "Markdown report format"
    },
    "html": {
        "extension": ".html",
        "mime_type": "text/html", 
        "description": "HTML report format"
    }
}

# ================================
# UTILITY FUNCTIONS (using config values)
# These functions are tightly coupled to the config variables and are kept here.
# Language-related utility functions are in utils/language_detector.py
# ================================

def get_severity_icon(severity: str) -> str:
    """Get the icon for a given severity level."""
    return SEVERITY_COLORS.get(severity.lower(), "⚪")

def get_severity_priority(severity: str) -> int:
    """Get the priority number for a given severity level."""
    return SEVERITY_PRIORITY.get(severity.lower(), 0)

def is_code_too_long(code: str) -> bool:
    """Check if code exceeds length limits."""
    return len(code) > ANALYSIS_LIMITS["max_code_length"] or len(code.splitlines()) > ANALYSIS_LIMITS["max_lines"]

def get_quality_rating(total_issues: int, high_severity_count: int) -> str:
    """Determine code quality rating based on issue counts."""
    for rating, thresholds in QUALITY_THRESHOLDS.items():
        if (total_issues <= thresholds["max_issues"] and 
            high_severity_count <= thresholds["max_high_severity"]):
            return rating
    return "critical"

def validate_openai_config() -> Dict[str, Any]:
    """Validate OpenAI configuration."""
    return {
        "api_key_set": bool(OPENAI_API_KEY),
        "model": OPENAI_MODEL,
        "max_tokens": OPENAI_MAX_TOKENS,
        "temperature": OPENAI_TEMPERATURE,
        "timeout": OPENAI_TIMEOUT
    }

# ================================
# ENVIRONMENT VALIDATION
# ================================

def validate_environment() -> Dict[str, Any]:
    """Validate the environment setup."""
    validation_results = {
        "openai": validate_openai_config(),
        "python_version": {
            "major": 3,
            "minor": 8,
            "supported": True
        },
        "required_packages": {
            "streamlit": True,
            "openai": True,
            "pylint": True
        },
        "optional_tools": {
            "nodejs": False,  # Will be checked at runtime
            "eslint": False,   # Will be checked at runtime
            "java": False,     # Will be checked at runtime
            "checkstyle": False, # Will be checked at runtime
            "cppcheck": False, # Will be checked at runtime
            "go": False,       # Will be checked at runtime
            "staticcheck": False, # Will be checked at runtime
            "stylelint": False # Will be checked at runtime
        }
    }
    
    return validation_results

# ================================
# DEFAULT CONFIGURATIONS
# ================================

# Default code examples for testing
DEFAULT_CODE_EXAMPLES = {
    "python": '''def calculate_factorial(n):
    """Calculate factorial of a number."""
    if n < 0:
        return None
    elif n == 0 or n == 1:
        return 1
    else:
        result = 1
        for i in range(2, n + 1):
            result *= i
    return result

# Example usage
if __name__ == "__main__":
    number = 5
    result = calculate_factorial(number)
    print(f"Factorial of {number} is {result}")
''',
    
    "javascript": '''function calculateFactorial(n) {
    /**
     * Calculate factorial of a number
     * @param {number} n - The number to calculate factorial for
     * @returns {number|null} The factorial or null if invalid
     */
    if (n < 0) {
        return null;
    } else if (n === 0 || n === 1) {
        return 1;
    } else {
        let result = 1;
        for (let i = 2; i <= n; i++) {
            result *= i;
        }
        return result;
    }
}

// Example usage
const number = 5;
const result = calculateFactorial(number);
console.log(`Factorial of ${number} is ${result}`);
''',
    "java": '''public class Factorial {
    public static int calculateFactorial(int n) {
        if (n < 0) {
            return -1; // Or throw an IllegalArgumentException
        } else if (n == 0 || n == 1) {
            return 1;
        } else {
            int result = 1;
            for (int i = 2; i <= n; i++) {
                result *= i;
            }
            return result;
        }
    }

    public static void main(String[] args) {
        int number = 5;
        int result = calculateFactorial(number);
        System.out.println("Factorial of " + number + " is " + result);
    }
}
''',
    "c_cpp": '''#include <iostream>

int calculateFactorial(int n) {
    if (n < 0) {
        return -1; // Indicate error
    } else if (n == 0 || n == 1) {
        return 1;
    } else {
        int result = 1;
        for (int i = 2; i <= n; i++) {
            result *= i;
        }
        return result;
    }
}

int main() {
    int number = 5;
    int result = calculateFactorial(number);
    std::cout << "Factorial of " << number << " is " << result << std::endl;
    return 0;
}
''',
    "typescript": '''function calculateFactorial(n: number): number | null {
    if (n < 0) {
        return null;
    } else if (n === 0 || n === 1) {
        return 1;
    } else {
        let result = 1;
        for (let i = 2; i <= n; i++) {
            result *= i;
        }
        return result;
    }
}

const number: number = 5;
const result = calculateFactorial(number);
console.log(`Factorial of ${number} is ${result}`);
''',
    "go": '''package main

import "fmt"

func calculateFactorial(n int) int {
	if n < 0 {
		return -1 // Indicate error
	} else if n == 0 || n == 1 {
		return 1
	} else {
		result := 1
		for i := 2; i <= n; i++ {
			result *= i
		}
		return result
	}
}

func main() {
	number := 5
	result := calculateFactorial(number)
	fmt.Printf("Factorial of %d is %d\\n", number, result)
}
''',
    "html_css": '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Simple Page</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f4f4f4;
        }
        .container {
            max-width: 800px;
            margin: auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
        }
        p {
            line-height: 1.6;
            color: #666;
        }
        /* Unused CSS rule */
        .unused-class {
            color: blue;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Welcome to My Page</h1>
        <p>This is a simple HTML page demonstrating basic structure and styling.</p>
        <button onclick="alert('Hello!');">Click Me</button>
    </div>
</body>
</html>
'''
}

# Application metadata
APP_METADATA = {
    "name": "AI Code Review Tool",
    "version": "1.0.0",
    "description": "AI-powered code review tool for Python and JavaScript",
    "author": "AI Assistant",
    "supported_languages": list(LANGUAGE_INFO.keys()),
    "features": [
        "Language auto-detection",
        "Linter integration (Pylint, ESLint, Checkstyle, Cppcheck, staticcheck, Stylelint)",
        "AI-powered suggestions",
        "Export functionality",
        "Syntax validation",
        "Code quality metrics"
    ]
}
