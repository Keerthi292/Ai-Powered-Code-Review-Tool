import json
import tempfile
import subprocess
from typing import Dict, List, Any
import os
import sys
import re

def analyze_go_code(code: str) -> Dict[str, Any]:
    """
    Analyze Go code using staticcheck.
    
    Args:
        code: Go source code string
        
    Returns:
        Dictionary containing analysis results
    """
    try:
        # Create a temporary directory for the Go module
        temp_dir = tempfile.mkdtemp()
        module_name = "temp_module"
        
        # Create go.mod and main.go inside the temporary directory
        with open(os.path.join(temp_dir, "go.mod"), "w") as f:
            f.write(f"module {module_name}\n\ngo 1.18\n") # Use a recent Go version

        with open(os.path.join(temp_dir, "main.go"), "w") as f:
            f.write(code)
        
        try:
            # Run `go mod tidy` to ensure dependencies are resolved (important for staticcheck)
            go_mod_cmd = ["go", "mod", "tidy"]
            subprocess.run(go_mod_cmd, cwd=temp_dir, capture_output=True, text=True, timeout=10)

            # Run staticcheck with JSON output
            cmd = [
                "staticcheck",
                "-f", "json", # Output format JSON
                f"./{module_name}/..." # Analyze the module
            ]
            
            # staticcheck needs to be run from a directory where it can find the module
            # We run it from the parent directory of temp_dir, and pass the module path
            result = subprocess.run(
                cmd, 
                cwd=os.path.dirname(temp_dir), # Run from parent dir to reference module
                capture_output=True, 
                text=True, 
                timeout=30
            )
            
            staticcheck_results = []
            if result.stdout.strip():
                try:
                    # staticcheck outputs a JSON array of issues
                    staticcheck_results = json.loads(result.stdout)
                except json.JSONDecodeError:
                    pass # Fallback to empty results if JSON parsing fails
            
            formatted_results = []
            for issue in staticcheck_results:
                severity_map = {
                    'error': 'error',
                    'warning': 'warning',
                    'info': 'info'
                }
                formatted_results.append({
                    "type": "linter",
                    "tool": "staticcheck",
                    "severity": severity_map.get(issue.get("severity", "warning"), "warning"),
                    "line": issue.get("line", 1),
                    "column": issue.get("column", 0),
                    "message": issue.get("message", ""),
                    "rule_id": issue.get("code", "")
                })
            
            return {
                "success": True,
                "language": "go",
                "linter_feedback": formatted_results,
                "raw_output": result.stdout,
                "errors": result.stderr if result.stderr else None,
                "return_code": result.returncode
            }
            
        finally:
            # Clean up temporary directory
            import shutil
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
                
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "language": "go", 
            "error": "Staticcheck analysis timed out (30s limit). This might happen for very large files or complex code.",
            "linter_feedback": []
        }
    except FileNotFoundError:
        return {
            "success": False,
            "language": "go",
            "error": "Go or staticcheck not found. Please ensure Go is installed and staticcheck is installed (`go install honnef.co/go/tools/cmd/staticcheck@latest`).",
            "linter_feedback": []
        }
    except Exception as e:
        return {
            "success": False,
            "language": "go",
            "error": f"Go analysis failed: {str(e)}",
            "linter_feedback": []
        }

def validate_go_syntax(code: str) -> Dict[str, Any]:
    """
    Basic Go syntax validation using `go vet`.
    Requires Go to be installed.
    """
    try:
        # Create a temporary directory for the Go module
        temp_dir = tempfile.mkdtemp()
        module_name = "temp_module"
        
        # Create go.mod and main.go inside the temporary directory
        with open(os.path.join(temp_dir, "go.mod"), "w") as f:
            f.write(f"module {module_name}\n\ngo 1.18\n")

        with open(os.path.join(temp_dir, "main.go"), "w") as f:
            f.write(code)
        
        try:
            # Run `go mod tidy` to ensure dependencies are resolved
            go_mod_cmd = ["go", "mod", "tidy"]
            subprocess.run(go_mod_cmd, cwd=temp_dir, capture_output=True, text=True, timeout=10)

            # Run `go vet` for syntax and basic semantic checks
            cmd = ["go", "vet", "./..."]
            result = subprocess.run(
                cmd,
                cwd=temp_dir,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                # go vet outputs errors to stderr
                error_message = result.stderr.strip()
                # Attempt to extract line number from go vet error output
                match = re.search(r'main\.go:(\d+):', error_message)
                line_num = int(match.group(1)) if match else 1
                return {
                    "valid": False,
                    "error": f"Syntax/Semantic Error at line {line_num}: {error_message.splitlines()[0]}"
                }
            return {"valid": True, "error": None}
        finally:
            # Clean up temporary directory
            import shutil
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
    except FileNotFoundError:
        return {
            "valid": False,
            "error": "Go not found. Cannot perform robust Go syntax validation. Please install Go."
        }
    except subprocess.TimeoutExpired:
        return {
            "valid": False,
            "error": "Go syntax validation timed out."
        }
    except Exception as e:
        return {
            "valid": False,
            "error": f"An error occurred during Go syntax validation: {str(e)}"
        }
