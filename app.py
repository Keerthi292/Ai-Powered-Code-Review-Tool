import streamlit as st
import json
from typing import Dict, Any
from datetime import datetime
from core.analyzer import CodeAnalyzer
from config import SEVERITY_COLORS, OPENAI_API_KEY, DEFAULT_CODE_EXAMPLES, LANGUAGE_INFO

# Page configuration
st.set_page_config(
    page_title="AI Code Review Tool",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced Custom CSS with better readability
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .main-header h1 {
        font-size: 2.2em;
        margin-bottom: 0.5rem;
        font-weight: 600;
    }
    
    .main-header p {
        font-size: 1.1em;
        opacity: 0.9;
        margin: 0;
    }
    
    .feedback-card {
        background: white;
        border-radius: 12px;
        padding: 1.2rem;
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        border-left: 4px solid #e0e0e0;
        transition: all 0.2s ease;
    }
    
    .feedback-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 20px rgba(0,0,0,0.12);
    }
    
    .severity-critical { border-left-color: #dc3545 !important; }
    .severity-warning { border-left-color: #ffc107 !important; }
    .severity-info { border-left-color: #17a2b8 !important; }
    
    .issue-header {
        display: flex;
        align-items: center;
        gap: 0.8rem;
        margin-bottom: 0.8rem;
        font-size: 1.1em;
        font-weight: 600;
    }
    
    .severity-badge {
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8em;
        font-weight: 600;
        text-transform: uppercase;
    }
    
    .badge-critical { background: #dc3545; color: white; }
    .badge-warning { background: #ffc107; color: #212529; }
    .badge-info { background: #17a2b8; color: white; }
    
    .issue-content {
        font-size: 1rem;
        line-height: 1.6;
        color: #333;
        margin-bottom: 0.8rem;
    }
    
    .issue-explanation {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 3px solid #007bff;
        margin-top: 0.8rem;
        font-size: 0.95em;
        color: #495057;
    }
    
    .line-link {
        background: #e9ecef;
        padding: 0.2rem 0.6rem;
        border-radius: 15px;
        font-size: 0.85em;
        color: #495057;
        text-decoration: none;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .line-link:hover {
        background: #007bff;
        color: white;
    }
    
    .quality-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        text-align: center;
    }
    
    .quality-excellent { border-top: 4px solid #28a745; }
    .quality-good { border-top: 4px solid #17a2b8; }
    .quality-fair { border-top: 4px solid #ffc107; }
    .quality-poor { border-top: 4px solid #dc3545; }
    
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }
    
    .metric-item {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
    }
    
    .metric-value {
        font-size: 1.8em;
        font-weight: bold;
        color: #495057;
    }
    
    .metric-label {
        font-size: 0.9em;
        color: #6c757d;
        margin-top: 0.3rem;
    }
    
    .section-header {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 1.3em;
        font-weight: 600;
        margin: 1.5rem 0 1rem 0;
        color: #495057;
    }
    
    .no-issues {
        text-align: center;
        padding: 2rem;
        background: #d4edda;
        border-radius: 12px;
        color: #155724;
        font-size: 1.1em;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
    }
    
    .stTabs [data-baseweb="tab-list"] button {
        font-weight: 600;
        border-radius: 8px 8px 0 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize analyzer
@st.cache_resource
def get_analyzer():
    return CodeAnalyzer()

def set_code_input_and_highlight(code: str, line_to_highlight: int = None):
    """Sets the code input and marks a line for highlighting."""
    st.session_state.code_input = code
    st.session_state.highlight_line = line_to_highlight
    st.rerun()

def get_severity_info(severity: str):
    """Get severity display information"""
    severity_map = {
        'error': {'emoji': '🚨', 'text': 'Critical', 'class': 'critical'},
        'high': {'emoji': '🚨', 'text': 'Critical', 'class': 'critical'},
        'warning': {'emoji': '⚠️', 'text': 'Warning', 'class': 'warning'},
        'medium': {'emoji': '⚠️', 'text': 'Warning', 'class': 'warning'},
        'info': {'emoji': '💡', 'text': 'Info', 'class': 'info'},
        'low': {'emoji': '💡', 'text': 'Info', 'class': 'info'},
        'suggestion': {'emoji': '💡', 'text': 'Suggestion', 'class': 'info'},
    }
    return severity_map.get(severity, {'emoji': '💡', 'text': 'Info', 'class': 'info'})

def display_feedback_item(item: Dict[str, Any], item_type: str):
    """Enhanced feedback item display with better readability"""
    severity = item.get('severity', 'info')
    sev_info = get_severity_info(severity)
    
    # Create the feedback card
    card_class = f"feedback-card severity-{sev_info['class']}"
    
    with st.container():
        st.markdown(f'<div class="{card_class}">', unsafe_allow_html=True)
        
        # Header with emoji, severity, and line number
        header_parts = [
            f"{sev_info['emoji']}",
            f'<span class="severity-badge badge-{sev_info["class"]}">{sev_info["text"]}</span>'
        ]
        
        if item.get('tool'):
            header_parts.append(f"**{item.get('tool').title()}**")
        
        if item.get('line'):
            header_parts.append(f'<span class="line-link">📍 Line {item.get("line")}</span>')
        
        st.markdown(f'<div class="issue-header">{" ".join(header_parts)}</div>', unsafe_allow_html=True)
        
        # Main message
        message = item.get('message', 'No message provided')
        st.markdown(f'<div class="issue-content">{message}</div>', unsafe_allow_html=True)
        
        # Rule information for linter issues
        if item_type == "linter" and (item.get('rule_id') or item.get('symbol')):
            rule_name = item.get('rule_id') or item.get('symbol')
            st.markdown(f"**Rule:** `{rule_name}`")
            
            # Rule explanations
            rule_explanations = {
                "semi": "Semicolons prevent automatic semicolon insertion issues and make code more predictable.",
                "no-var": "`let` and `const` have block scope, preventing common variable hoisting bugs.",
                "no-console": "Console statements should be removed in production code for performance and security.",
                "eqeqeq": "`===` prevents type coercion bugs by checking both value and type.",
                "no-unused-vars": "Unused variables clutter code and may indicate logic errors.",
                "undefined-variable": "Using undefined variables will cause runtime errors.",
                "html-doctype": "The doctype ensures browsers render your page in standards mode.",
                "html-html-tag": "The `<html>` tag is the root element of an HTML page.",
                "html-head-tag": "The `<head>` contains metadata crucial for browser rendering and SEO.",
                "html-body-tag": "The `<body>` contains all the visible content of a web page.",
                "html-title-tag": "The `<title>` appears in the browser tab and is important for user experience and SEO.",
                "html-unclosed-tag": "Unclosed tags can lead to unexpected rendering issues and broken layouts.",
                "css-inline-style": "Separating styles from HTML improves maintainability and reusability.",
                "css-missing-semi": "Missing semicolons can cause CSS properties to be ignored or lead to parsing errors.",
                "css-unused-class": "Unused CSS rules increase file size and make stylesheets harder to manage.",
            }
            
            if rule_name in rule_explanations:
                st.markdown(f'<div class="issue-explanation">💡 <strong>Why this matters:</strong> {rule_explanations[rule_name]}</div>', unsafe_allow_html=True)
        
        # AI suggestion details
        elif item_type == "ai":
            if item.get('category'):
                category = item.get('category').replace('_', ' ').title()
                st.markdown(f"**Category:** {category}")
            
            st.markdown('<div class="issue-explanation">🤖 <strong>AI Insight:</strong> This suggestion is based on modern coding best practices and industry standards.</div>', unsafe_allow_html=True)
            
            if item.get('example'):
                with st.expander("💻 View Code Example & Solution", expanded=False):
                    st.markdown("**Here's how you could improve it:**")
                    st.code(item['example'], language=item.get('language', 'python'))
        
        st.markdown('</div>', unsafe_allow_html=True)

def display_quality_overview(summary: Dict[str, Any], metadata: Dict[str, Any]):
    """Enhanced quality overview with better visual presentation"""
    
    total_issues = summary.get("total_issues", 0)
    severity_counts = summary.get("severity_counts", {})
    high_severity = severity_counts.get("error", 0) + severity_counts.get("high", 0)
    
    # Determine quality rating
    if total_issues == 0:
        quality_rating = "Excellent"
        quality_class = "quality-excellent"
        quality_emoji = "🌟"
        quality_message = "Your code is pristine! No issues found."
    elif high_severity == 0 and total_issues <= 3:
        quality_rating = "Good"
        quality_class = "quality-good"
        quality_emoji = "✅"
        quality_message = "Your code looks great with only minor suggestions."
    elif high_severity <= 2 and total_issues <= 10:
        quality_rating = "Fair"
        quality_class = "quality-fair"
        quality_emoji = "⚠️"
        quality_message = "Several issues found that should be addressed."
    else:
        quality_rating = "Needs Work"
        quality_class = "quality-poor"
        quality_emoji = "🔧"
        quality_message = "Multiple critical issues require immediate attention."
    
    # Quality rating card
    st.markdown(f"""
    <div class="quality-card {quality_class}">
        <div style="font-size: 3em; margin-bottom: 0.5rem;">{quality_emoji}</div>
        <div style="font-size: 1.5em; font-weight: bold; margin-bottom: 0.5rem;">Quality Rating: {quality_rating}</div>
        <div style="font-size: 1.1em; color: #6c757d;">{quality_message}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Metrics grid
    st.markdown('<div class="section-header">📊 Code Analysis Metrics</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-item">
            <div class="metric-value">{total_issues}</div>
            <div class="metric-label">Total Issues</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-item">
            <div class="metric-value">{summary.get("linter_issues", 0)}</div>
            <div class="metric-label">Linter Issues</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-item">
            <div class="metric-value">{summary.get("ai_suggestions", 0)}</div>
            <div class="metric-label">AI Suggestions</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-item">
            <div class="metric-value">{high_severity}</div>
            <div class="metric-label">Critical Issues</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Code characteristics
    st.markdown('<div class="section-header">📈 Code Characteristics</div>', unsafe_allow_html=True)
    
    char_col1, char_col2 = st.columns(2)
    
    with char_col1:
        st.markdown("**📏 Size & Structure**")
        st.write(f"• **Lines of Code:** {metadata.get('lines_of_code', 'N/A')}")
        st.write(f"• **Characters:** {metadata.get('code_length', 'N/A'):,}")
        st.write(f"• **Language:** {metadata.get('language_info', {}).get('name', 'Unknown')}")
        st.write(f"• **Functions:** {metadata.get('complexity', {}).get('function_count', 'N/A')}")
    
    with char_col2:
        st.markdown("**🔍 Complexity Analysis**")
        st.write(f"• **Classes:** {metadata.get('complexity', {}).get('class_count', 'N/A')}")
        st.write(f"• **Max Nesting:** {metadata.get('complexity', {}).get('nesting_depth', 'N/A')}")
        st.write(f"• **Cyclomatic Complexity:** {metadata.get('complexity', {}).get('cyclomatic_complexity', 'N/A')}")
        
        complexity_score = metadata.get('complexity', {}).get('cyclomatic_complexity', 0)
        if complexity_score <= 10:
            st.success("🟢 Low Complexity")
        elif complexity_score <= 20:
            st.info("🟡 Moderate Complexity")
        else:
            st.warning("🔴 High Complexity")

def main():
    # Clear the code input *before* the widget is rendered
    if "clear_requested" in st.session_state and st.session_state.clear_requested:
      st.session_state.code_input = ""
      st.session_state.clear_requested = False
      st.rerun() 
    
    # Initialize session state
    if "code_input" not in st.session_state:
        st.session_state.code_input = ""
    if "highlight_line" not in st.session_state:
        st.session_state.highlight_line = None
    
    # Main header
    st.markdown("""
    <div class="main-header">
        <h1>🔍 AI-Powered Code Review Tool</h1>
        <p>Get instant, intelligent feedback on your code quality using advanced linters and AI analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        supported_langs = list(LANGUAGE_INFO.keys())
        language_options = ["Auto-detect"] + [LANGUAGE_INFO[lang]["name"] for lang in supported_langs]
        selected_language_name = st.selectbox("🔤 Language", language_options)
        
        # Map selected language name back to internal key
        selected_language_key = None
        if selected_language_name != "Auto-detect":
            for key, info in LANGUAGE_INFO.items():
                if info["name"] == selected_language_name:
                    selected_language_key = key
                    break
        
        uploaded_file = st.file_uploader(
            "📁 Upload Code File", 
            type=[ext.replace('.', '') for ext in sum([info["extensions"] for info in LANGUAGE_INFO.values()], [])]
        )
        
        if uploaded_file is not None:
            st.session_state.code_input = uploaded_file.read().decode("utf-8")
            st.session_state.highlight_line = None
            st.success(f"✅ Loaded {uploaded_file.name}")
        
        st.markdown("### 🛠️ Analysis Tools")
        for lang_key, lang_info in LANGUAGE_INFO.items():
            st.markdown(f"• **{lang_info['name']}:** {lang_info['linter']} + AI")
        st.markdown("• **AI Model:** OpenAI GPT-4o-mini")
        
        analyzer = get_analyzer()
        if OPENAI_API_KEY:
            st.success("🔑 OpenAI API Key configured")
        else:
            st.warning("⚠️ OpenAI API Key not set")
            st.markdown("Set `OPENAI_API_KEY` environment variable for AI suggestions.")
        
        st.markdown("### 📝 Try Examples")
        
        example_cols = st.columns(2)
        
        with example_cols[0]:
            if st.button("🐍 Python", use_container_width=True):
                set_code_input_and_highlight(DEFAULT_CODE_EXAMPLES["python"])
            if st.button("☕ Java", use_container_width=True):
                set_code_input_and_highlight(DEFAULT_CODE_EXAMPLES["java"])
            if st.button("📘 TypeScript", use_container_width=True):
                set_code_input_and_highlight(DEFAULT_CODE_EXAMPLES["typescript"])
           
        
        with example_cols[1]:
            if st.button("📜 JavaScript", use_container_width=True):
                set_code_input_and_highlight(DEFAULT_CODE_EXAMPLES["javascript"])
            if st.button("⚡ C/C++", use_container_width=True):
                set_code_input_and_highlight(DEFAULT_CODE_EXAMPLES["c_cpp"])
            if st.button("🌐 HTML/CSS", use_container_width=True):
                set_code_input_and_highlight(DEFAULT_CODE_EXAMPLES["html_css"])
            
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<div class="section-header">📝 Code Input</div>', unsafe_allow_html=True)
        
        code_input = st.text_area(
            "Paste your code here:",
            value=st.session_state.code_input,
            height=400,
            placeholder="Paste your code here (Python, JavaScript, Java, C/C++, TypeScript, HTML/CSS)...",
            key="code_input",
            help="Paste your code for analysis. Click on line numbers in results to highlight code."
        )
        
        # Update session state if text area is directly edited
        if code_input != st.session_state.code_input:
            st.session_state.code_input = code_input
            st.session_state.highlight_line = None
        
        col_btn1, col_btn2 = st.columns([2, 1])
        
        with col_btn1:
            analyze_button = st.button(
                "🔍 Analyze Code",
                type="primary",
                use_container_width=True,
                disabled=not st.session_state.code_input.strip()
            )
        
        with col_btn2:
          if st.button("🗑️ Clear", use_container_width=True):
           st.session_state.clear_requested = True
           st.rerun()
        
        if st.session_state.code_input.strip():
            st.caption(f"📊 {len(st.session_state.code_input.splitlines())} lines, {len(st.session_state.code_input):,} characters")
    
    with col2:
        st.markdown('<div class="section-header">📋 Analysis Results</div>', unsafe_allow_html=True)
        
        if analyze_button and st.session_state.code_input.strip():
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            with st.spinner("🔄 Analyzing code..."):
                status_text.text("🔍 Detecting language...")
                progress_bar.progress(20)
                
                analyzer = get_analyzer()
                
                lang_to_analyze = selected_language_key if selected_language_key else None
                filename = uploaded_file.name if uploaded_file else None
                
                status_text.text("🛠️ Running linter analysis...")
                progress_bar.progress(50)
                
                results = analyzer.analyze_code(st.session_state.code_input, lang_to_analyze, filename)
                
                status_text.text("🤖 Getting AI suggestions...")
                progress_bar.progress(80)
                
                progress_bar.progress(100)
                status_text.text("✅ Analysis complete!")
            
            progress_bar.empty()
            status_text.empty()
            
            if results["success"]:
                st.success(f"🎉 Analysis complete for **{results.get('language_info', {}).get('name', results['language'].title())}** code")
                
                # Display quality overview
                display_quality_overview(results.get("summary", {}), results.get("metadata", {}))
                
                # Results tabs
                tab1, tab2, tab3, tab4 = st.tabs(["🛠️ Linter Issues", "🤖 AI Suggestions", "📊 Detailed Summary", "📄 Export & Data"])
                
                with tab1:
                    linter_feedback = results.get("linter_feedback", [])
                    linter_error = results.get("errors")
                    
                    if linter_error and "not found" in linter_error.lower():
                        st.error(f"🚫 Linter Error: {linter_error}")
                        st.info("💡 Please ensure the required linter for this language is installed on your system and accessible in your PATH.")
                    elif linter_feedback:
                        st.markdown(f'<div class="section-header">🔍 Found {len(linter_feedback)} Code Issues</div>', unsafe_allow_html=True)
                        st.markdown("*Issues detected by static code analysis tools*")
                        
                        # Group by severity
                        high_priority = [item for item in linter_feedback if item.get('severity') in ['error', 'high']]
                        medium_priority = [item for item in linter_feedback if item.get('severity') in ['warning', 'medium']]
                        low_priority = [item for item in linter_feedback if item.get('severity') in ['info', 'low', 'convention', 'refactor']]
                        
                        if high_priority:
                            st.markdown('<div class="section-header">🚨 Critical Issues (Fix These First!)</div>', unsafe_allow_html=True)
                            for item in high_priority:
                                display_feedback_item(item, "linter")
                        
                        if medium_priority:
                            st.markdown('<div class="section-header">⚠️ Important Issues</div>', unsafe_allow_html=True)
                            for item in medium_priority:
                                display_feedback_item(item, "linter")
                        
                        if low_priority:
                            st.markdown('<div class="section-header">💡 Minor Issues & Suggestions</div>', unsafe_allow_html=True)
                            for item in low_priority:
                                display_feedback_item(item, "linter")
                    else:
                        st.markdown("""
                        <div class="no-issues">
                            <div style="font-size: 3em; margin-bottom: 1rem;">🎉</div>
                            <div style="font-size: 1.3em; font-weight: bold; margin-bottom: 0.5rem;">Perfect! No linter issues found!</div>
                            <div>Your code follows excellent practices:</div>
                            <div style="margin-top: 1rem; text-align: left; display: inline-block;">
                                ✅ No syntax errors detected<br>
                                ✅ No style violations found<br>
                                ✅ No potential bugs identified<br>
                                ✅ Code structure looks great
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                
                with tab2:
                    ai_suggestions = results.get("ai_suggestions", [])
                    if ai_suggestions:
                        actual_suggestions = [s for s in ai_suggestions if s.get("type") != "error"]
                        error_messages = [s for s in ai_suggestions if s.get("type") == "error"]
                        
                        if actual_suggestions:
                            st.markdown(f'<div class="section-header">🤖 AI Found {len(actual_suggestions)} Improvement Opportunities</div>', unsafe_allow_html=True)
                            st.markdown("*Smart suggestions to make your code even better*")
                            
                            # Group AI suggestions by category
                            categories = {}
                            for suggestion in actual_suggestions:
                                category = suggestion.get('category', 'General').replace('_', ' ').title()
                                if category not in categories:
                                    categories[category] = []
                                categories[category].append(suggestion)
                            
                            for category, suggestions_in_category in categories.items():
                                st.markdown(f'<div class="section-header">💡 {category}</div>', unsafe_allow_html=True)
                                for item in suggestions_in_category:
                                    display_feedback_item(item, "ai")
                        
                        if error_messages:
                            st.error("🚫 AI Analysis Issues:")
                            for error in error_messages:
                                st.error(f"• {error.get('message', 'Unknown error')}")
                    else:
                        st.markdown("""
                        <div class="no-issues">
                            <div style="font-size: 3em; margin-bottom: 1rem;">🤖</div>
                            <div style="font-size: 1.3em; font-weight: bold; margin-bottom: 0.5rem;">No AI suggestions available</div>
                            <div>Your code looks good to our AI analysis!</div>
                        </div>
                        """, unsafe_allow_html=True)
                
                with tab3:
                    summary = results.get("summary", {})
                    metadata = results.get("metadata", {})
                    
                    st.markdown('<div class="section-header">📊 Comprehensive Analysis Summary</div>', unsafe_allow_html=True)
                    
                    # Detailed metrics in a more organized way
                    detail_col1, detail_col2 = st.columns(2)
                    
                    with detail_col1:
                        st.markdown("#### 📈 Issue Statistics")
                        total = summary.get('total_issues', 0)
                        linter = summary.get('linter_issues', 0)
                        ai = summary.get('ai_suggestions', 0)
                        
                        st.write(f"**Total Issues:** {total}")
                        st.write(f"**Linter Issues:** {linter}")
                        st.write(f"**AI Suggestions:** {ai}")
                        
                        severity_counts = summary.get("severity_counts", {})
                        if any(severity_counts.values()):
                            st.markdown("#### 🎯 Severity Breakdown")
                            
                            high_count = severity_counts.get("error", 0) + severity_counts.get("high", 0)
                            med_count = severity_counts.get("warning", 0) + severity_counts.get("medium", 0)
                            low_count = severity_counts.get("info", 0) + severity_counts.get("low", 0) + severity_counts.get("suggestion", 0)
                            
                            if high_count > 0:
                                st.error(f"🚨 Critical/High: {high_count}")
                            else:
                                st.success("🚨 Critical/High: 0")
                            
                            if med_count > 0:
                                st.warning(f"⚠️ Medium/Warning: {med_count}")
                            else:
                                st.success("⚠️ Medium/Warning: 0")
                            
                            if low_count > 0:
                                st.info(f"💡 Low/Info/Suggestions: {low_count}")
                            else:
                                st.success("💡 Low/Info/Suggestions: 0")
                    
                    with detail_col2:
                        st.markdown("#### 📏 Code Metrics")
                        st.write(f"**Lines of Code:** {metadata.get('lines_of_code', 'N/A')}")
                        st.write(f"**Characters:** {metadata.get('code_length', 'N/A'):,}")
                        st.write(f"**Language:** {results.get('language_info', {}).get('name', 'Unknown')}")
                        
                        complexity_score = metadata.get('complexity', {}).get('cyclomatic_complexity', 0)
                        if complexity_score <= 10:
                            st.success(f"**Complexity:** {complexity_score} (Low) 🟢")
                        elif complexity_score <= 20:
                            st.info(f"**Complexity:** {complexity_score} (Moderate) 🟡")
                        else:
                            st.warning(f"**Complexity:** {complexity_score} (High) 🔴")
                        
                        st.markdown("#### 🏗️ Structure Analysis")
                        st.write(f"**Functions:** {metadata.get('complexity', {}).get('function_count', 'N/A')}")
                        st.write(f"**Classes:** {metadata.get('complexity', {}).get('class_count', 'N/A')}")
                        st.write(f"**Max Nesting Depth:** {metadata.get('complexity', {}).get('nesting_depth', 'N/A')}")
                
                with tab4:
                    st.markdown('<div class="section-header">📄 Export & Technical Data</div>', unsafe_allow_html=True)
                    
                    export_col1, export_col2 = st.columns(2)
                    
                    with export_col1:
                        export_data = {
                            "timestamp": datetime.now().isoformat(),
                            "analysis_results": results
                        }
                        
                        st.download_button(
                            label="📥 Download Complete Report (JSON)",
                            data=json.dumps(export_data, indent=2),
                            file_name=f"code_review_{results['language']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                            mime="application/json",
                            use_container_width=True,
                            help="Download full analysis results in JSON format"
                        )
                    
                    with export_col2:
                        # Determine quality rating for summary
                        total_issues = summary.get("total_issues", 0)
                        high_severity = summary.get("severity_counts", {}).get("error", 0) + summary.get("severity_counts", {}).get("high", 0)
                        
                        if total_issues == 0:
                            quality_rating = "Excellent"
                        elif high_severity == 0 and total_issues <= 3:
                            quality_rating = "Good"
                        elif high_severity <= 2 and total_issues <= 10:
                            quality_rating = "Fair"
                        else:
                            quality_rating = "Needs Work"
                        
                        summary_report = f"""CODE REVIEW SUMMARY
===================
Language: {results.get('language_info', {}).get('name', 'Unknown')}
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

OVERVIEW:
- Total Issues: {summary.get('total_issues', 0)}
- Linter Issues: {summary.get('linter_issues', 0)}
- AI Suggestions: {summary.get('ai_suggestions', 0)}
- Quality Rating: {quality_rating}

CODE METRICS:
- Lines: {metadata.get('lines_of_code', 'N/A')}
- Characters: {metadata.get('code_length', 'N/A')}
- Functions: {metadata.get('complexity', {}).get('function_count', 'N/A')}
- Classes: {metadata.get('complexity', {}).get('class_count', 'N/A')}
- Max Nesting Depth: {metadata.get('complexity', {}).get('nesting_depth', 'N/A')}
- Cyclomatic Complexity (Est.): {metadata.get('complexity', {}).get('cyclomatic_complexity', 'N/A')}

SEVERITY BREAKDOWN:
- Critical/High: {summary.get('severity_counts', {}).get('error', 0) + summary.get('severity_counts', {}).get('high', 0)}
- Medium/Warning: {summary.get('severity_counts', {}).get('warning', 0) + summary.get('severity_counts', {}).get('medium', 0)}
- Low/Info/Suggestions: {summary.get('severity_counts', {}).get('info', 0) + summary.get('severity_counts', {}).get('low', 0) + summary.get('severity_counts', {}).get('suggestion', 0)}

---
Generated by AI Code Review Tool"""
                        
                        st.download_button(
                            label="📄 Download Summary (TXT)",
                            data=summary_report,
                            file_name=f"summary_{results['language']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                            mime="text/plain",
                            use_container_width=True,
                            help="Download a human-readable summary report"
                        )
                    
                    if results.get("linter_raw_output"):
                        with st.expander("🔧 Raw Linter Output"):
                            st.code(results["linter_raw_output"], language="text")
                    
                    with st.expander("📋 Complete Analysis Results (JSON)"):
                        st.json(results)
            
            else:
                st.error(f"❌ Analysis failed: {results.get('error', 'Unknown error')}")
                
                if results.get("errors"):
                    with st.expander("🔍 Error Details"):
                        st.code(results["errors"])
                
                if results.get("linter_feedback") or results.get("ai_suggestions"):
                    st.warning("⚠️ Partial results available despite errors:")
                    if results.get("linter_feedback"):
                        st.markdown("### 🛠️ Linter Feedback (Partial)")
                        for item in results["linter_feedback"]:
                            display_feedback_item(item, "linter")
                    if results.get("ai_suggestions"):
                        st.markdown("### 🤖 AI Suggestions (Partial)")
                        for item in results["ai_suggestions"]:
                            display_feedback_item(item, "ai")
        
        elif analyze_button:
            st.warning("⚠️ Please enter some code to analyze")
        else:
            st.info("👋 Enter your code or select an example and click 'Analyze Code' to get started!")
            st.markdown("### 🚀 What this tool does:")
            st.markdown("""
            - **🔍 Language Detection:** Automatically identifies Python, JavaScript, Java, C/C++, TypeScript, HTML/CSS
            - **🛠️ Linter Analysis:** Uses dedicated linters for each language (Pylint, ESLint, Checkstyle, Cppcheck, Stylelint)
            - **🤖 AI Suggestions:** Offers intelligent, human-friendly code improvement recommendations using OpenAI's GPT-4o-mini
            - **📊 Quality Assessment:** Gives an overall code quality rating and detailed metrics
            - **📥 Export Reports:** Allows downloading comprehensive JSON or human-readable TXT reports
            """)
    
    # Footer
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.9em; margin-top: 3rem; padding: 2rem; background: #f8f9fa; border-radius: 12px;'>
        <p><strong>🛠️ Built with Streamlit, OpenAI, and various open-source linters</strong></p>
        <p>Ensure all required linters and their runtimes are installed on your system for full functionality.</p>
          </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
