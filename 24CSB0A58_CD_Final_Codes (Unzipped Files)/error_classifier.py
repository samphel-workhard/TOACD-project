import re
import json

def parse_gcc_error(error_message):
    """
    Parses standard GCC error strings.
    Format typically: <file>:<line>:<col>: <severity>: <message>
    """
    pattern = re.compile(r'^(.*?):(\d+):(\d+):\s+(error|warning|note):\s+(.*)$', re.MULTILINE)
    matches = pattern.findall(error_message)
    
    diagnostics = []
    for match in matches:
        diagnostics.append({
            "file": match[0],
            "line": int(match[1]),
            "column": int(match[2]),
            "severity": match[3],
            "message": match[4].strip()
        })
    
    return diagnostics

def classify_error(error_message):
    """
    Analyzes the raw GCC error string and assigns a structured category.
    Returns: dict with extracted details
    """
    diagnostics = parse_gcc_error(error_message)
    msg = error_message.lower()
    
    category = "General Error"
    strategy = "Analyze the provided code and error message. Explain exactly what went wrong and provide the corrected code."
    
    if "expected" in msg or "missing" in msg or "was not declared" in msg:
        category = "Syntax Error"
        strategy = "Focus on C++ syntax rules (semicolons, braces, variable names)."
    elif "undefined reference" in msg or "ld returned 1 exit status" in msg:
        category = "Linker Error"
        strategy = "Explain that a function definition or library is missing."
    elif "conversion" in msg or "cannot convert" in msg or "type" in msg:
        category = "Type Mismatch"
        strategy = "Explain variable types (int vs string, pointers)."
    elif "time limit exceeded" in msg or "infinite loop" in msg:
        category = "Runtime Error (Infinite Loop)"
        strategy = "Explain why the loop never terminates. You MUST provide the corrected code by adding a proper exit condition."
    elif "deprecated" in msg or "warning" in msg or "unsafe" in msg:
        category = "Security Warning"
        strategy = "Explain why this function is dangerous and suggest a modern alternative."

    return {
        "category": category,
        "strategy": strategy,
        "diagnostics": diagnostics,
        "raw_error": error_message
    }

def get_diagnostic_prompt(classification, code):
    """
    Generates a highly-constrained system prompt requesting JSON output for Educational Feedback.
    """
    # Create a summary of structured errors
    diag_summary = ""
    for d in classification['diagnostics']:
        diag_summary += f"- Line {d['line']}, Col {d['column']}: [{d['severity'].upper()}] {d['message']}\n"
    
    if not diag_summary:
        diag_summary = "No structured line information could be parsed. See raw compiler output."

    return f"""Analyze the following C++ code and compiler error, then provide a secure fix.
    CRITICAL DIRECTIVE: You are a strict, automated C++ Compiler Assistant. You MUST NOT make conversation.
    You MUST respond in strict JSON format matching the schema below.

--- BUGGY CODE ---
{code}

--- COMPILER ERROR ---
{classification['raw_error']}

--- PARSED DIAGNOSTICS ---
{diag_summary}

--- INSTRUCTIONS ---
Primary Diagnosis Category: {classification['category']}
Teaching Strategy: {classification['strategy']}

You must identify, fix, and explain EVERY SINGLE ERROR mentioned in the compiler output.
Your JSON response MUST follow this exact format:
{{
    "what_happened": "A short summary of what went wrong",
    "why_it_happened": "The reason the code failed",
    "where_it_happened": "Line number(s) or general location",
    "how_to_fix": "Explanation of the fix",
    "concept": "The C++ concept involved (e.g., Array Indexing)",
    "practice_question": "A small practice question related to the concept",
    "fixed_code": "The complete, securely corrected C++ code as a string (include \\n for newlines)"
}}
"""