import json
import tempfile
import subprocess
from typing import Dict, List, Any
import os
import sys
import re
import xml.etree.ElementTree as ET

def analyze_c_cpp_code(code: str) -> Dict[str, Any]:
    """
    Analyze C/C++ code using Cppcheck.
    
    Args:
        code: C/C++ source code string
        
    Returns:
        Dictionary containing analysis results
    """
    try:
        # Create temporary file for analysis
        # Cppcheck can auto-detect language from extension, so use .cpp
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cpp', delete=False) as temp_file:
            temp_file.write(code)
            temp_file_path = temp_file.name
        
        try:
            # Run Cppcheck with XML output
            cmd = [
                "cppcheck",
                "--enable=all", # Enable all checks
                "--xml",        # Output format XML
                "--xml-version=2", # Use XML version 2 for more details
                temp_file_path
            ]
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            
            formatted_results = []
            if result.stderr.strip(): # Cppcheck outputs XML to stderr
                try:
                    root = ET.fromstring(result.stderr)
                    for error_elem in root.findall('.//error'):
                        location_elem = error_elem.find('location')
                        if location_elem is not None:
                            severity_map = {
                                'error': 'error',
                                'warning': 'warning',
                                'style': 'info', # Style issues
                                'performance': 'info', # Performance suggestions
                                'portability': 'warning', # Portability issues
                                'information': 'info' # General info
                            }
                            formatted_results.append({
                                "type": "linter",
                                "tool": "cppcheck",
                                "severity": severity_map.get(error_elem.get("severity", "warning"), "warning"),
                                "line": int(location_elem.get("line", 1)),
                                "column": int(location_elem.get("column", 0)),
                                "message": error_elem.get("message", ""),
                                "rule_id": error_elem.get("id", "")
                            })
                except ET.ParseError:
                    pass # Fallback to empty results if XML parsing fails
            
            return {
                "success": True,
                "language": "c_cpp",
                "linter_feedback": formatted_results,
                "raw_output": result.stderr, # Cppcheck outputs XML to stderr
                "errors": result.stdout if result.stdout else None, # stdout might contain other messages
                "return_code": result.returncode
            }
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "language": "c_cpp", 
            "error": "Cppcheck analysis timed out (30s limit). This might happen for very large files or complex code.",
            "linter_feedback": []
        }
    except FileNotFoundError:
        return {
            "success": False,
            "language": "c_cpp",
            "error": "Cppcheck not found. Please install it (e.g., `sudo apt-get install cppcheck` on Linux, or via official installers).",
            "linter_feedback": []
        }
    except Exception as e:
        return {
            "success": False,
            "language": "c_cpp",
            "error": f"C/C++ analysis failed: {str(e)}",
            "linter_feedback": []
        }

def validate_c_cpp_syntax(code: str) -> Dict[str, Any]:
    """
    Basic C/C++ syntax validation by attempting to compile with g++.
    Requires g++ to be installed.
    """
    try:
        # Create temporary file for compilation
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cpp', delete=False) as temp_file:
            temp_file.write(code)
            temp_file_path = temp_file.name
        
        try:
            # Attempt to compile the C++ code (without linking)
            cmd = ["g++", "-fsyntax-only", temp_file_path]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                # g++ outputs errors to stderr
                error_message = result.stderr.strip()
                # Attempt to extract line number from g++ error output
                match = re.search(r'(\w+\.cpp):(\d+):', error_message)
                line_num = int(match.group(2)) if match else 1
                return {
                    "valid": False,
                    "error": f"Syntax Error at line {line_num}: {error_message.splitlines()[0]}"
                }
            return {"valid": True, "error": None}
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
    except FileNotFoundError:
        return {
            "valid": False,
            "error": "g++ (GCC C++ compiler) not found. Cannot perform robust C/C++ syntax validation. Please install g++."
        }
    except subprocess.TimeoutExpired:
        return {
            "valid": False,
            "error": "C/C++ syntax validation timed out."
        }
    except Exception as e:
        return {
            "valid": False,
            "error": f"An error occurred during C/C++ syntax validation: {str(e)}"
        }
