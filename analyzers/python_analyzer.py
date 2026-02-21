import json
import tempfile
import subprocess
from typing import Dict, List, Any
import os
import sys

def analyze_python_code(code: str) -> Dict[str, Any]:
    """
    Analyze Python code using Pylint and return structured results.
    
    Args:
        code: Python source code string
        
    Returns:
        Dictionary containing analysis results
    """
    try:
        # Create temporary file for analysis
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
            temp_file.write(code)
            temp_file_path = temp_file.name
        
        try:
            # Run Pylint with JSON output
            cmd = [
                sys.executable, '-m', 'pylint',
                '--output-format=json',
                '--disable=C0114,C0115,C0116,R0903,C0103',  # Disable common warnings
                '--score=no',
                temp_file_path
            ]
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            
            # Parse Pylint JSON output
            pylint_results = []
            if result.stdout.strip():
                try:
                    pylint_results = json.loads(result.stdout)
                except json.JSONDecodeError:
                    # If JSON parsing fails, try to extract from stderr
                    pass
            
            # Transform Pylint results to our format
            formatted_results = []
            for issue in pylint_results:
                severity_map = {
                    'error': 'error',
                    'warning': 'warning', 
                    'refactor': 'refactor',
                    'convention': 'convention',
                    'info': 'info'
                }
                
                formatted_results.append({
                    "type": "linter",
                    "tool": "pylint",
                    "severity": severity_map.get(issue.get("type", "warning"), "warning"),
                    "line": issue.get("line", 1),
                    "column": issue.get("column", 0),
                    "message": issue.get("message", ""),
                    "symbol": issue.get("symbol", ""),
                    "message_id": issue.get("message-id", ""),
                    "category": issue.get("category", "")
                })
            
            return {
                "success": True,
                "language": "python",
                "linter_feedback": formatted_results,
                "raw_output": result.stdout,
                "errors": result.stderr if result.stderr else None,
                "return_code": result.returncode
            }
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "language": "python", 
            "error": "Pylint analysis timed out (30s limit). This might happen for very large files or complex code.",
            "linter_feedback": []
        }
    except FileNotFoundError:
        return {
            "success": False,
            "language": "python",
            "error": "Pylint not found. Please install it: `pip install pylint`",
            "linter_feedback": []
        }
    except Exception as e:
        return {
            "success": False,
            "language": "python",
            "error": f"Python analysis failed: {str(e)}",
            "linter_feedback": []
        }

def validate_python_syntax(code: str) -> Dict[str, Any]:
    """
    Validate Python syntax without running Pylint.
    
    Args:
        code: Python source code string
        
    Returns:
        Dictionary with syntax validation results
    """
    try:
        compile(code, '<string>', 'exec')
        return {"valid": True, "error": None}
    except SyntaxError as e:
        return {
            "valid": False,
            "error": f"Syntax Error at line {e.lineno}: {e.msg}"
        }
    except Exception as e:
        return {
            "valid": False,
            "error": f"Compilation error: {str(e)}"
        }
