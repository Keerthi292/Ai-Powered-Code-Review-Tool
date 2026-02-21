from typing import Dict, Any, Optional
from utils.language_detector import get_language_info, get_supported_languages, is_language_supported

class CodeAnalyzer:
    """Main code analysis coordinator."""
    
    def __init__(self):
        self.supported_languages = get_supported_languages()
    
    def analyze_code(self, code: str, language: Optional[str] = None, filename: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze code using both linters and AI suggestions.
        
        Args:
            code: Source code string
            language: Programming language (if None, will auto-detect)
            filename: Optional filename for language detection
            
        Returns:
            Unified analysis results
        """
        try:
            if not code.strip():
                return {
                    "success": False,
                    "error": "No code provided for analysis",
                    "language": None,
                    "linter_feedback": [],
                    "ai_suggestions": [],
                    "language_info": {}
                }
            
            # Import here to avoid circular imports and only load necessary analyzers
            from utils.language_detector import detect_language, analyze_code_characteristics, detect_code_complexity
            from analyzers.python_analyzer import analyze_python_code, validate_python_syntax
            from analyzers.javascript_analyzer import analyze_js_code, validate_js_syntax
            from analyzers.ai_analyzer import get_ai_suggestions_sync
            
            # Import new analyzers
            from analyzers.java_analyzer import analyze_java_code, validate_java_syntax
            from analyzers.c_cpp_analyzer import analyze_c_cpp_code, validate_c_cpp_syntax
            from analyzers.typescript_analyzer import analyze_typescript_code, validate_typescript_syntax # Deprecated
            from analyzers.html_css_analyzer import analyze_html_css_code, validate_html_css_syntax
            
            # Detect or validate language
            detected_language = language or detect_language(code, filename)
            
            if not is_language_supported(detected_language):
                return {
                    "success": False,
                    "error": f"Unsupported language: '{detected_language}'. Please select a supported language or provide a file with a known extension.",
                    "language": detected_language,
                    "linter_feedback": [],
                    "ai_suggestions": [],
                    "language_info": get_language_info(detected_language)
                }
            
            # Get language information
            lang_info = get_language_info(detected_language)
            
            # Validate syntax
            syntax_valid = True
            syntax_error = None
            
            try:
                syntax_check_func = {
                    'python': validate_python_syntax,
                    'javascript': validate_js_syntax,
                    'java': validate_java_syntax,
                    'c_cpp': validate_c_cpp_syntax,
                    'typescript': validate_js_syntax, # Use JS validator for TS
                    # 'go': validate_go_syntax,
                    'html_css': validate_html_css_syntax,
                }.get(detected_language)
                
                if syntax_check_func:
                    syntax_check = syntax_check_func(code)
                    syntax_valid = syntax_check.get("valid", True)
                    syntax_error = syntax_check.get("error")
                else:
                    syntax_valid = True # Assume valid if no specific validator
            except Exception as e:
                syntax_valid = False
                syntax_error = f"Internal syntax check error: {str(e)}"
            
            # Run linter analysis
            linter_results = {"success": True, "linter_feedback": [], "errors": None, "raw_output": None}
            
            if not syntax_valid:
                linter_results["success"] = False
                linter_results["error"] = syntax_error
                linter_results["linter_feedback"].append({
                    "type": "linter",
                    "tool": "syntax_checker",
                    "severity": "error",
                    "line": 1, # Default to line 1 if not specific
                    "column": 0,
                    "message": f"Syntax Error: {syntax_error}",
                    "rule_id": "syntax-error"
                })
            else:
                try:
                    linter_analysis_func = {
                        'python': analyze_python_code,
                        'javascript': lambda c: analyze_js_code(c, is_typescript=False), # Pass is_typescript=False
                        'java': analyze_java_code,
                        'c_cpp': analyze_c_cpp_code,
                        'typescript': lambda c: analyze_js_code(c, is_typescript=True), # Pass is_typescript=True
                        # 'go': analyze_go_code,
                        'html_css': analyze_html_css_code,
                    }.get(detected_language)
                    
                    if linter_analysis_func:
                        linter_results = linter_analysis_func(code)
                    else:
                        linter_results["success"] = True
                        linter_results["linter_feedback"] = []
                        linter_results["raw_output"] = "No specific linter for this language."
                except Exception as e:
                    linter_results = {
                        "success": False,
                        "error": f"Linter analysis failed: {str(e)}",
                        "linter_feedback": [],
                        "raw_output": None,
                        "errors": str(e)
                    }
            
            # Get AI suggestions
            ai_suggestions = []
            try:
                ai_suggestions = get_ai_suggestions_sync(code, detected_language)
            except Exception as e:
                ai_suggestions = [{
                    "type": "info",
                    "severity": "low",
                    "line": None,
                    "message": f"AI analysis unavailable due to an internal error: {str(e)}",
                    "example": None,
                    "category": "internal_error"
                }]
            
            # Calculate summary
            linter_issues = linter_results.get("linter_feedback", [])
            total_issues = len(linter_issues) + len(ai_suggestions)
            
            # Count by severity
            severity_counts = {"error": 0, "high": 0, "warning": 0, "medium": 0, "info": 0, "low": 0, "suggestion": 0}
            for issue in linter_issues + ai_suggestions:
                severity = issue.get("severity", "info")
                if severity in severity_counts:
                    severity_counts[severity] += 1
            
            # Get code characteristics and complexity
            code_characteristics = analyze_code_characteristics(code)
            code_complexity = detect_code_complexity(code)

            return {
                "success": True,
                "language": detected_language,
                "language_info": lang_info,
                "linter_feedback": linter_issues,
                "ai_suggestions": ai_suggestions,
                "summary": {
                    "total_issues": total_issues,
                    "linter_issues": len(linter_issues),
                    "ai_suggestions": len(ai_suggestions),
                    "severity_counts": severity_counts
                },
                "errors": linter_results.get("errors"),
                "linter_raw_output": linter_results.get("raw_output"),
                "metadata": {
                    "code_length": len(code),
                    "lines_of_code": len(code.splitlines()),
                    "characteristics": code_characteristics,
                    "complexity": code_complexity
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"An unexpected error occurred during analysis: {str(e)}",
                "language": "unknown",
                "language_info": {},
                "linter_feedback": [],
                "ai_suggestions": [],
                "summary": {"total_issues": 0, "linter_issues": 0, "ai_suggestions": 0},
                "debug_info": {
                    "error_type": type(e).__name__,
                    "message": str(e),
                    "code_length": len(code),
                    "lines_of_code": len(code.splitlines())
                }
            }
    
    def get_supported_languages(self) -> list:
        """Get list of supported programming languages."""
        return self.supported_languages.copy()
    
    def is_language_supported(self, language: str) -> bool:
        """Check if a programming language is supported."""
        return language.lower() in self.supported_languages
