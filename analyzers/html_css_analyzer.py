import json
import tempfile
import subprocess
from typing import Dict, List, Any
import os
import sys
import re

def analyze_html_css_code(code: str) -> Dict[str, Any]:
    """
    Analyze HTML/CSS code using Stylelint.
    
    Args:
        code: HTML/CSS source code string
        
    Returns:
        Dictionary containing analysis results
    """
    try:
        # Determine if it's primarily HTML or CSS to set suffix and config
        is_css = re.search(r'{[^}]*}', code) and not re.search(r'<!DOCTYPE html>', code, re.IGNORECASE)
        suffix = '.css' if is_css else '.html' # Stylelint can lint CSS within HTML <style> tags

        with tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False) as temp_file:
            temp_file.write(code)
            temp_file_path = temp_file.name
        
        # Create a temporary .stylelintrc.json for consistent configuration
        stylelint_config = {
            "extends": ["stylelint-config-standard"],
            "rules": {
                "indentation": 2,
                "selector-list-comma-newline-after": "always",
                "block-closing-brace-newline-after": "always",
                "declaration-colon-space-after": "always",
                "declaration-no-important": True,
                "color-no-invalid-hex": True,
                "unit-no-unknown": True,
                "property-no-unknown": True,
                "no-empty-source": True,
                "no-duplicate-selectors": True,
                "no-descending-specificity": True
            }
        }
        # If it's an HTML file, enable HTML processor
        if suffix == '.html':
            stylelint_config["processors"] = ["stylelint-processor-html"]

        stylelint_config_path = os.path.join(os.path.dirname(temp_file_path), ".stylelintrc.json")
        with open(stylelint_config_path, 'w') as f:
            json.dump(stylelint_config, f, indent=2)

        try:
            # Run Stylelint with JSON output
            cmd = [
                "npx", "stylelint",
                "--formatter=json",
                "--config", stylelint_config_path,
                temp_file_path
            ]
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            
            stylelint_results = []
            if result.stdout.strip():
                try:
                    # Stylelint outputs an array of results, one per file
                    parsed_output = json.loads(result.stdout)
                    if parsed_output and isinstance(parsed_output, list):
                        # We only analyze one file, so take the first result's warnings
                        if parsed_output[0] and 'warnings' in parsed_output[0]:
                            stylelint_results = parsed_output[0]['warnings']
                except json.JSONDecodeError:
                    pass # Fallback to empty results if JSON parsing fails
            
            formatted_results = []
            for issue in stylelint_results:
                severity_map = {
                    'warning': 'warning',
                    'error': 'error'
                }
                formatted_results.append({
                    "type": "linter",
                    "tool": "stylelint",
                    "severity": severity_map.get(issue.get("severity", "warning"), "warning"),
                    "line": issue.get("line", 1),
                    "column": issue.get("column", 0),
                    "message": issue.get("text", ""),
                    "rule_id": issue.get("rule", "")
                })
            
            return {
                "success": True,
                "language": "html_css",
                "linter_feedback": formatted_results,
                "raw_output": result.stdout,
                "errors": result.stderr if result.stderr else None,
                "return_code": result.returncode
            }
            
        finally:
            # Clean up temporary files
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
            if os.path.exists(stylelint_config_path):
                os.unlink(stylelint_config_path)
                
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "language": "html_css", 
            "error": "Stylelint analysis timed out (30s limit). This might happen for very large files or complex code.",
            "linter_feedback": []
        }
    except FileNotFoundError:
        return {
            "success": False,
            "language": "html_css",
            "error": "Stylelint or Node.js not found. Please ensure Node.js is installed and Stylelint is globally or locally available (`npm install -g stylelint stylelint-config-standard stylelint-processor-html`).",
            "linter_feedback": []
        }
    except Exception as e:
        return {
            "success": False,
            "language": "html_css",
            "error": f"HTML/CSS analysis failed: {str(e)}",
            "linter_feedback": []
        }

def validate_html_css_syntax(code: str) -> Dict[str, Any]:
    """
    Basic HTML/CSS syntax validation using `html-validate` (for HTML) or `stylelint` (for CSS).
    This is a simplified approach. For full validation, dedicated parsers are needed.
    """
    try:
        # Heuristic to guess if it's primarily HTML or CSS
        is_css = re.search(r'{[^}]*}', code) and not re.search(r'<!DOCTYPE html>', code, re.IGNORECASE)
        
        if is_css:
            # Use Stylelint for CSS syntax validation
            temp_file_path = None
            stylelint_config_path = None
            try:
                with tempfile.NamedTemporaryFile(mode='w', suffix='.css', delete=False) as temp_file:
                    temp_file.write(code)
                    temp_file_path = temp_file.name
                
                stylelint_config = {"rules": {"no-empty-source": True, "block-no-empty": True}}
                stylelint_config_path = os.path.join(os.path.dirname(temp_file_path), ".stylelintrc.json")
                with open(stylelint_config_path, 'w') as f:
                    json.dump(stylelint_config, f, indent=2)

                cmd = ["npx", "stylelint", "--formatter=json", "--config", stylelint_config_path, temp_file_path]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                
                parsed_output = json.loads(result.stdout)
                if parsed_output and parsed_output[0] and parsed_output[0]['warnings']:
                    first_warning = parsed_output[0]['warnings'][0]
                    return {
                        "valid": False,
                        "error": f"CSS Syntax Error at line {first_warning.get('line', 1)}: {first_warning.get('text', 'Invalid CSS syntax')}"
                    }
                return {"valid": True, "error": None}
            finally:
                if temp_file_path and os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                if stylelint_config_path and os.path.exists(stylelint_config_path):
                    os.unlink(stylelint_config_path)

        else:
            # For HTML, a very basic check for root tags
            if '<html' not in code.lower() or '<body' not in code.lower():
                return {"valid": False, "error": "HTML Syntax Error: Missing fundamental <html> or <body> tags."}
            return {"valid": True, "error": None}

    except FileNotFoundError:
        return {
            "valid": False,
            "error": "Node.js or Stylelint not found. Cannot perform robust HTML/CSS syntax validation. Please install Node.js and Stylelint."
        }
    except subprocess.TimeoutExpired:
        return {
            "valid": False,
            "error": "HTML/CSS syntax validation timed out."
        }
    except Exception as e:
        return {
            "valid": False,
            "error": f"An error occurred during HTML/CSS syntax validation: {str(e)}"
        }
