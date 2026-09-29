import re

def run_security_guardrail(code_snippet):
    """
    Scans the provided code/text for banned C++ functions using Regex.
    Returns: (is_safe: bool, findings: list)
    """
    
    # 'Never-List'(Regex patterns) -> Tuple: (Severity, Reason, Recommendation)
    banned_patterns = {
        # 1. CRITICAL BUFFER OVERFLOWS
        r'\bgets\b': ("CRITICAL", "performs no bounds checking. It is officially removed from C++14.", "Use 'std::cin' or 'fgets()'."),
        r'\bstrcpy\b': ("CRITICAL", "does not check buffer size.", "Use 'strncpy' or 'std::string'."),
        r'\bstrcat\b': ("CRITICAL", "can write past the end of a buffer.", "Use 'strncat' or 'std::string::append'."),
        r'\bsprintf\b': ("CRITICAL", "lacks bounds checking.", "Use 'snprintf' to prevent overflows."),
        r'\bvsprintf\b': ("CRITICAL", "is unsafe.", "Use 'vsnprintf'."),
        r'\bwcscpy\b': ("CRITICAL", "Wide-character version of strcpy is equally unsafe.", "Use 'wcsncpy'."),
        r'\bwcscat\b': ("CRITICAL", "Wide-character version of strcat is unsafe.", "Use 'wcsncat'."),
        r'\bstrncpy\b': ("WARNING", "can leave strings unterminated if the source is larger than the destination.", "Prefer 'std::string'."),

        # 2. OS COMMAND INJECTION & PROCESS CONTROL
        r'\bsystem\s*\(': ("CRITICAL", "allows arbitrary OS command execution. Severe injection vulnerability.", "Avoid system() where possible and use safer APIs."),
        r'\bpopen\s*\(': ("CRITICAL", "opens a pipe to a shell command, which is vulnerable to injection attacks.", "Avoid popen() or sanitize input aggressively."),
        r'\bexecl\s*\(': ("CRITICAL", "poses command injection risks.", "Validate all inputs before execution."),
        r'\bexecle\s*\(': ("CRITICAL", "poses command injection risks.", "Validate all inputs before execution."),
        r'\bexeclp\s*\(': ("CRITICAL", "poses command injection risks.", "Validate all inputs before execution."),
        r'\bexecv\s*\(': ("CRITICAL", "poses command injection risks.", "Validate all inputs before execution."),
        r'\bexecvp\s*\(': ("CRITICAL", "poses command injection risks.", "Validate all inputs before execution."),
        r'\bexecve\s*\(': ("CRITICAL", "poses command injection risks.", "Validate all inputs before execution."),

        # 3. FORMAT STRING VULNERABILITIES
        r'\bprintf\s*\(\s*[a-zA-Z_][a-zA-Z0-9_]*\s*\)': ("CRITICAL", "Format string vulnerability. Never pass a variable directly to 'printf'.", "Use 'printf(\"%s\", var)'."),
        r'\bfprintf\s*\(\s*[a-zA-Z_][a-zA-Z0-9_]*\s*,\s*[a-zA-Z_][a-zA-Z0-9_]*\s*\)': ("CRITICAL", "Format string vulnerability in 'fprintf'.", "Ensure the format string is hardcoded."),
        r'\bsyslog\s*\(': ("WARNING", "Ensure you are not passing un-sanitized user input directly to 'syslog()'.", "Sanitize all input."),

        # 4. INSECURE TEMPORARY FILE CREATION
        r'\bmktemp\s*\(': ("CRITICAL", "suffers from race conditions.", "Use 'mkstemp' instead."),
        r'\btmpnam\s*\(': ("CRITICAL", "is obsolete and insecure.", "Use 'mkstemp'."),
        r'\btempnam\s*\(': ("CRITICAL", "is vulnerable to race conditions.", "Use 'mkstemp'."),

        # 5. DEPRECATED / UNSAFE C++ MEMORY MANAGEMENT
        r'\bauto_ptr\b': ("CRITICAL", "is deprecated in C++11 and removed in C++17 due to unsafe copy semantics.", "Use 'std::unique_ptr'."),
        r'\bfree\s*\(': ("WARNING", "Mixing 'malloc/free' with 'new/delete' causes undefined behavior.", "Stick to C++ paradigms (new/delete or smart pointers)."),
        r'\bdelete\s+': ("WARNING", "Manual 'delete' can lead to dangling pointers.", "Modern C++ heavily favors 'std::unique_ptr' or 'std::shared_ptr'."),
        r'\bscanf\s*\(\s*\"%s\"': ("RISK", "'scanf' with '%s' has no bounds checking.", "Specify a width (e.g., '%49s') or use 'std::cin'."),

        # 6. WEAK CRYPTOGRAPHY & RANDOMNESS
        r'\brand\s*\(\s*\)': ("WARNING", "is not cryptographically secure.", "For security-sensitive randomness, use the '<random>' library (e.g., std::mt19937)."),
        r'\bsrand\s*\(': ("WARNING", "Seeding with 'srand(time(NULL))' is predictable.", "Use a true hardware entropy source like 'std::random_device'."),

        # 7. PLATFORM & STANDARD ISSUES
        r'system\s*\(\s*\"pause\"\s*\)': ("WARNING", "is platform-dependent (Windows only).", "Use 'std::cin.get()' for cross-platform compatibility."),
        r'\bvoid\s+main\b': ("STANDARD", "is non-standard C++.", "The standard dictates using 'int main()' and returning 0."),
        r'#include\s+<bits/stdc\+\+\.h>': ("PERFORMANCE", "drastically increases compilation time and makes code non-portable.", "Include specific headers.")
    }

    findings = []
    lines = code_snippet.split('\n')
    
    for i, line in enumerate(lines):
        line_num = i + 1
        for pattern, info in banned_patterns.items():
            match = re.search(pattern, line)
            if match:
                severity, reason, recommendation = info
                findings.append({
                    "severity": severity,
                    "line": line_num,
                    "pattern": match.group(0),
                    "reason": reason,
                    "recommendation": recommendation
                })
                
    is_safe = len([f for f in findings if f['severity'] == "CRITICAL"]) == 0
    return is_safe, findings