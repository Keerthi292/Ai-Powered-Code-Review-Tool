import json
import tempfile
import subprocess
from typing import Dict, List, Any
import os
import sys
import re

def analyze_java_code(code: str) -> Dict[str, Any]:
    """
    Analyze Java code using Checkstyle.
    
    Args:
        code: Java source code string
        
    Returns:
        Dictionary containing analysis results
    """
    try:
        # Create temporary file for analysis
        with tempfile.NamedTemporaryFile(mode='w', suffix='.java', delete=False) as temp_file:
            temp_file.write(code)
            temp_file_path = temp_file.name
        
        # Define paths for Checkstyle JAR and config file
        # User needs to download checkstyle-X.Y-all.jar and a config file (e.g., google_checks.xml)
        # and place them in a known location, or specify full paths.
        # For simplicity, we assume they are in the same directory or accessible via PATH.
        checkstyle_jar = os.getenv("CHECKSTYLE_JAR", "checkstyle-11.0.0-all.jar") # Example version
        checkstyle_config = os.getenv("CHECKSTYLE_CONFIG", "google_checks.xml") # Example config

        # Check if Checkstyle JAR and config exist
        if not os.path.exists(checkstyle_jar):
            return {
                "success": False,
                "language": "java",
                "error": f"Checkstyle JAR not found at '{checkstyle_jar}'. Please download it (e.g., from Maven Central) and set CHECKSTYLE_JAR environment variable or place it in the working directory.",
                "linter_feedback": []
            }
        if not os.path.exists(checkstyle_config):
            return {
                "success": False,
                "language": "java",
                "error": f"Checkstyle config file not found at '{checkstyle_config}'. Please download a config (e.g., google_checks.xml) and set CHECKSTYLE_CONFIG environment variable or place it in the working directory.",
                "linter_feedback": []
            }

        try:
            # Run Checkstyle with XML output
            cmd = [
                "java", "-jar", checkstyle_jar,
                "-c", checkstyle_config,
                "-f", "xml", # Output format XML
                temp_file_path
            ]
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            
            # Parse Checkstyle XML output
            # Checkstyle outputs XML to stdout, even if there are errors.
            # We need to parse the XML to extract issues.
            import xml.etree.ElementTree as ET
            
            formatted_results = []
            if result.stdout.strip():
                try:
                    root = ET.fromstring(result.stdout)
                    for file_elem in root.findall('file'):
                        if file_elem.get('name') == temp_file_path:
                            for error_elem in file_elem.findall('error'):
                                severity_map = {
                                    'error': 'error',
                                    'warning': 'warning',
                                    'info': 'info'
                                }
                                formatted_results.append({
                                    "type": "linter",
                                    "tool": "checkstyle",
                                    "severity": severity_map.get(error_elem.get("severity", "warning"), "warning"),
                                    "line": int(error_elem.get("line", 1)),
                                    "column": int(error_elem.get("column", 0)),
                                    "message": error_elem.get("message", ""),
                                    "rule_id": error_elem.get("source", "").split('.')[-1] # Extract rule name
                                })
                except ET.ParseError:
                    pass # Fallback to empty results if XML parsing fails
            
            return {
                "success": True,
                "language": "java",
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
            "language": "java", 
            "error": "Checkstyle analysis timed out (30s limit). This might happen for very large files or complex code.",
            "linter_feedback": []
        }
    except FileNotFoundError:
        return {
            "success": False,
            "language": "java",
            "error": "Java Runtime Environment (JRE) not found. Please ensure Java is installed and in your PATH.",
            "linter_feedback": []
        }
    except Exception as e:
        return {
            "success": False,
            "language": "java",
            "error": f"Java analysis failed: {str(e)}",
            "linter_feedback": []
        }

def validate_java_syntax(code: str) -> Dict[str, Any]:
    """
    Basic Java syntax validation by attempting to compile (without running).
    Requires a Java Development Kit (JDK) for `javac`.
    """
    try:
        # Create temporary file for compilation
        with tempfile.NamedTemporaryFile(mode='w', suffix='.java', delete=False) as temp_file:
            temp_file.write(code)
            temp_file_path = temp_file.name
        
        try:
            # Attempt to compile the Java code
            cmd = ["javac", "-Xlint:none", "-d", os.path.dirname(temp_file_path), temp_file_path]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                # javac outputs errors to stderr
                error_message = result.stderr.strip()
                # Attempt to extract line number from javac error output
                match = re.search(r'(\w+\.java):(\d+):', error_message)
                line_num = int(match.group(2)) if match else 1
                return {
                    "valid": False,
                    "error": f"Syntax Error at line {line_num}: {error_message.splitlines()[0]}"
                }
            return {"valid": True, "error": None}
        finally:
            # Clean up temporary files
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
            # Clean up .class files if compilation was successful
            class_file = temp_file_path.replace('.java', '.class')
            if os.path.exists(class_file):
                os.unlink(class_file)
    except FileNotFoundError:
        return {
            "valid": False,
            "error": "Java Development Kit (JDK) not found. Cannot perform robust Java syntax validation. Please install a JDK."
        }
    except subprocess.TimeoutExpired:
        return {
            "valid": False,
            "error": "Java syntax validation timed out."
        }
    except Exception as e:
        return {
            "valid": False,
            "error": f"An error occurred during Java syntax validation: {str(e)}"
        }
