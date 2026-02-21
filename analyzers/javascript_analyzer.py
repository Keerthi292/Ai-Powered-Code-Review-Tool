import json
import tempfile
import subprocess
from typing import Dict, List, Any
import os
import sys

def analyze_js_code(code: str, is_typescript: bool = False) -> Dict[str, Any]:
    """
    Analyze JavaScript/TypeScript code using ESLint.
    
    Args:
        code: Source code string
        is_typescript: True if the code is TypeScript, False for JavaScript
        
    Returns:
        Dictionary containing analysis results
    """
    try:
        # Create temporary file for analysis
        suffix = '.ts' if is_typescript else '.js'
        with tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False) as temp_file:
            temp_file.write(code)
            temp_file_path = temp_file.name
        
        # Create a temporary .eslintrc.json for consistent configuration
        eslint_config = {
            "env": {
                "browser": True,
                "node": True,
                "es2021": True
            },
            "extends": [
                "eslint:recommended"
            ],
            "parserOptions": {
                "ecmaVersion": 2021,
                "sourceType": "module"
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
                "arrow-spacing": "warn"
            }
        }

        if is_typescript:
            eslint_config["parser"] = "@typescript-eslint/parser"
            eslint_config["plugins"] = ["@typescript-eslint"]
            eslint_config["extends"].append("plugin:@typescript-eslint/recommended")
            eslint_config["rules"]["@typescript-eslint/no-unused-vars"] = ["warn", { "argsIgnorePattern": "^_" }]
            eslint_config["rules"]["@typescript-eslint/no-explicit-any"] = "warn"
            eslint_config["parserOptions"]["project"] = "./tsconfig.json" # ESLint needs tsconfig for type-aware linting

            # Create a dummy tsconfig.json if it doesn't exist for ESLint
            tsconfig_path = os.path.join(os.path.dirname(temp_file_path), "tsconfig.json")
            if not os.path.exists(tsconfig_path):
                with open(tsconfig_path, 'w') as f:
                    json.dump({
                        "compilerOptions": {
                            "target": "es2021",
                            "module": "commonjs",
                            "strict": True,
                            "esModuleInterop": True,
                            "skipLibCheck": True,
                            "forceConsistentCasingInFileNames": True,
                            "jsx": "react" # For .tsx files
                        },
                        "include": [temp_file_path]
                    }, f, indent=2)

        eslint_config_path = os.path.join(os.path.dirname(temp_file_path), ".eslintrc.json")
        with open(eslint_config_path, 'w') as f:
            json.dump(eslint_config, f, indent=2)

        try:
            # Run ESLint with JSON output
            cmd = [
                "npx", "eslint",
                "--format=json",
                "--no-eslintrc", # Prevent ESLint from looking for other config files
                "--config", eslint_config_path,
                temp_file_path
            ]
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            
            eslint_results = []
            if result.stdout.strip():
                try:
                    # ESLint outputs an array of results, one per file
                    parsed_output = json.loads(result.stdout)
                    if parsed_output and isinstance(parsed_output, list):
                        # We only analyze one file, so take the first result's messages
                        if parsed_output[0] and 'messages' in parsed_output[0]:
                            eslint_results = parsed_output[0]['messages']
                except json.JSONDecodeError:
                    pass # Fallback to empty results if JSON parsing fails
            
            formatted_results = []
            for issue in eslint_results:
                severity_map = {
                    0: 'off', 1: 'warning', 2: 'error' # ESLint severity levels
                }
                formatted_results.append({
                    "type": "linter",
                    "tool": "eslint",
                    "severity": severity_map.get(issue.get("severity", 1), "warning"),
                    "line": issue.get("line", 1),
                    "column": issue.get("column", 0),
                    "message": issue.get("message", ""),
                    "rule_id": issue.get("ruleId", "")
                })
            
            return {
                "success": True,
                "language": "typescript" if is_typescript else "javascript",
                "linter_feedback": formatted_results,
                "raw_output": result.stdout,
                "errors": result.stderr if result.stderr else None,
                "return_code": result.returncode
            }
            
        finally:
            # Clean up temporary files
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
            if os.path.exists(eslint_config_path):
                os.unlink(eslint_config_path)
            tsconfig_path = os.path.join(os.path.dirname(temp_file_path), "tsconfig.json")
            if is_typescript and os.path.exists(tsconfig_path):
                os.unlink(tsconfig_path)
                
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "language": "typescript" if is_typescript else "javascript",
            "error": "ESLint analysis timed out (30s limit). This might happen for very large files or complex code.",
            "linter_feedback": []
        }
    except FileNotFoundError:
        return {
            "success": False,
            "language": "typescript" if is_typescript else "javascript",
            "error": "ESLint or Node.js not found. Please ensure Node.js is installed and ESLint is globally or locally available (`npm install -g eslint @typescript-eslint/parser @typescript-eslint/eslint-plugin`).",
            "linter_feedback": []
        }
    except Exception as e:
        return {
            "success": False,
            "language": "typescript" if is_typescript else "javascript",
            "error": f"ESLint analysis failed: {str(e)}",
            "linter_feedback": []
        }

def validate_js_syntax(code: str) -> Dict[str, Any]:
    """
    Basic JavaScript/TypeScript syntax validation using Node.js.
    """
    try:
        # Use Node.js to attempt parsing the code
        # This is a more robust syntax check than simple regex/brace counting
        cmd = ["node", "-c", "-e", code] # -c checks syntax, -e executes string
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            # Node.js will output syntax errors to stderr
            error_message = result.stderr.strip()
            # Attempt to extract line number from Node.js error output
            match = re.search(r':(\d+)\n', error_message)
            line_num = int(match.group(1)) if match else 1
            return {
                "valid": False,
                "error": f"Syntax Error at line {line_num}: {error_message.splitlines()[0]}"
            }
        return {"valid": True, "error": None}
    except FileNotFoundError:
        return {
            "valid": False,
            "error": "Node.js not found. Cannot perform robust JavaScript/TypeScript syntax validation. Please install Node.js."
        }
    except subprocess.TimeoutExpired:
        return {
            "valid": False,
            "error": "JavaScript/TypeScript syntax validation timed out."
        }
    except Exception as e:
        return {
            "valid": False,
            "error": f"An error occurred during JavaScript/TypeScript syntax validation: {str(e)}"
        }
