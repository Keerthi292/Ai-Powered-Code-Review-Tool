import json
from typing import List, Dict, Any
from config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_TEMPERATURE, OPENAI_MAX_TOKENS, AI_PROMPT_TEMPLATES, SYSTEM_PROMPTS

def get_ai_suggestions_sync(code: str, language: str) -> List[Dict[str, Any]]:
    """
    Get AI-powered code improvement suggestions.
    
    Args:
        code: Source code string
        language: Programming language
        
    Returns:
        List of AI suggestions
    """
    try:
        if not OPENAI_API_KEY:
            return [{
                "type": "info",
                "severity": "low",
                "line": None,
                "message": "AI suggestions unavailable: OpenAI API key not configured. Please set the OPENAI_API_KEY environment variable.",
                "example": None,
                "category": "configuration"
            }]
        
        try:
            import openai
        except ImportError:
            return [{
                "type": "info",
                "severity": "low",
                "line": None,
                "message": "AI suggestions unavailable: OpenAI package not installed. Please run `pip install openai`.",
                "example": None,
                "category": "configuration"
            }]
        
        if len(code.strip()) > 8000: # Limit for GPT-4o-mini context window
            return [{
                "type": "warning",
                "severity": "medium",
                "line": None,
                "message": "Code is too long for AI analysis (exceeds 8000 characters). AI suggestions might be incomplete or unavailable for very large files.",
                "example": None,
                "category": "limitations"
            }]
        
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        
        # Get the appropriate prompt template and system message
        prompt_template = AI_PROMPT_TEMPLATES.get(language, AI_PROMPT_TEMPLATES["python"]) # Default to python if language not found
        system_prompt = SYSTEM_PROMPTS.get(f"{language}_expert", SYSTEM_PROMPTS["code_reviewer"])
        
        prompt = prompt_template.format(code=code)
        
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=OPENAI_TEMPERATURE,
            max_tokens=OPENAI_MAX_TOKENS
        )
        
        content = response.choices[0].message.content.strip()
        
        # Clean up response (remove markdown code blocks)
        if content.startswith('```json'):
            content = content[7:]
        if content.startswith('```'):
            content = content[3:]
        if content.endswith('```'):
            content = content[:-3]
        
        content = content.strip()
        
        suggestions = []
        try:
            suggestions = json.loads(content)
            if not isinstance(suggestions, list):
                suggestions = [suggestions] if isinstance(suggestions, dict) else []
        except json.JSONDecodeError:
            return [{
                "type": "error",
                "severity": "high",
                "line": None,
                "message": f"AI response was not valid JSON. Raw response: {content[:200]}...",
                "example": None,
                "category": "api_error"
            }]
        
        formatted_suggestions = []
        for suggestion in suggestions:
            if isinstance(suggestion, dict):
                formatted_suggestions.append({
                    "type": suggestion.get("type", "suggestion"),
                    "severity": suggestion.get("severity", "medium"),
                    "line": suggestion.get("line"),
                    "message": suggestion.get("message", "No message provided"),
                    "example": suggestion.get("example"),
                    "category": suggestion.get("category", "general")
                })
        
        return formatted_suggestions if formatted_suggestions else [{
            "type": "info",
            "severity": "low",
            "line": None,
            "message": "AI analysis completed - no specific suggestions found for this code. Great job!",
            "example": None,
            "category": "no_suggestions"
        }]
        
    except openai.APIError as e:
        return [{
            "type": "error",
            "severity": "high",
            "line": None,
            "message": f"OpenAI API Error: {e.status_code} - {e.response.json().get('error', {}).get('message', str(e))}",
            "example": None,
            "category": "api_error"
        }]
    except openai.APITimeoutError:
        return [{
            "type": "error",
            "severity": "high",
            "line": None,
            "message": "OpenAI API request timed out. The model took too long to respond.",
            "example": None,
            "category": "api_error"
        }]
    except Exception as e:
        return [{
            "type": "error",
            "severity": "high",
            "line": None,
            "message": f"An unexpected error occurred during AI analysis: {str(e)}",
            "example": None,
            "category": "internal_error"
        }]
