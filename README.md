# AI-Code-Review-Tool
# Overview
This is a simple AI-based code review tool that checks your code for errors, style problems, and best-practice issues.
It works using two methods:
 * Linters → Find basic mistakes like formatting issues, unused variables, etc.
 * AI (GPT-4o Mini) → Gives deeper, human-like suggestions to improve readability, structure, and quality.
The final output is a combined report that is easy to understand.

# Features

 - Supports multiple languages (Python, JavaScript, Java, C/C++, HTML/CSS).
 - Uses linters for fast, rule-based analysis.
 - Uses AI for deeper and smarter suggestions.
 - Clean and simple web interface made with Streamlit.
 - Gives instant feedback to help students, developers, and teams.

# How It Works

1) User pastes or uploads code.
2) Tool automatically detects the language.
3) Performs Linter Analysis (syntax/style errors).
4) Performs AI Analysis (best practices, readability).
5) Combines both results into a single report.

# Technologies Used

 * Python (backend logic)
 * Streamlit (web interface)
 * Linters (Pylint, ESLint, Checkstyle, Cppcheck, Stylelint)
 * OpenAI GPT-4o Mini (AI suggestions)

# Use Cases

 - Students → Learn coding and fix mistakes quickly.
 - Developers → Save time in debugging and code review.
 - Companies → Maintain clean, consistent code across teams.

# Limitations

 * May miss very complex or logical errors.
 * Dependent on linter rules and AI model quality.
 * Limited support for rare programming languages.

# Future Improvements

 * More language support
 * Real-time suggestions
 * IDE plugins (VS Code, PyCharm)
 * AI-powered auto-fixes

# How to Run the Project

1) Install dependencies:
   pip install -r requirements.txt

2) Run Streamlit:
   streamlit run app.py

3) Paste your code and view the results.