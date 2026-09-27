import re

def run_security_guardrail(code_snippet):
    """
    Scans the provided code/text for banned C++ functions using Regex.
    Returns: (is_safe: bool, warning_message: str)
    """
    
    # 'Never-List'(Regex patterns)
    banned_patterns = {
        
        # 1. CRITICAL BUFFER OVERFLOWS (The "Banned" C-String Functions)
         
        r'\bgets\b': "CRITICAL: 'gets()' performs no bounds checking. It is officially removed from C++14. Use 'std::cin' or 'fgets()'.",
        r'\bstrcpy\b': "CRITICAL: 'strcpy' does not check buffer size. Use 'strncpy' or 'std::string'.",
        r'\bstrcat\b': "CRITICAL: 'strcat' can write past the end of a buffer. Use 'strncat' or 'std::string::append'.",
        r'\bsprintf\b': "CRITICAL: 'sprintf' lacks bounds checking. Use 'snprintf' to prevent overflows.",
        r'\bvsprintf\b': "CRITICAL: 'vsprintf' is unsafe. Use 'vsnprintf'.",
        r'\bwcscpy\b': "CRITICAL: Wide-character version of strcpy is equally unsafe. Use 'wcsncpy'.",
        r'\bwcscat\b': "CRITICAL: Wide-character version of strcat is unsafe. Use 'wcsncat'.",
        r'\bstrncpy\b': "WARNING: 'strncpy' can leave strings unterminated if the source is larger than the destination. Prefer 'std::string'.",

        
        # 2. OS COMMAND INJECTION & PROCESS CONTROL
        
        r'\bsystem\s*\(': "CRITICAL: 'system()' allows arbitrary OS command execution. This is a severe injection vulnerability.",
        r'\bpopen\s*\(': "CRITICAL: 'popen()' opens a pipe to a shell command, which is vulnerable to injection attacks.",
        r'\bexecl\s*\(': "CRITICAL: The 'execl' function poses command injection risks. Validate all inputs before execution.",
        r'\bexecle\s*\(': "CRITICAL: The 'execle' function poses command injection risks.",
        r'\bexeclp\s*\(': "CRITICAL: The 'execlp' function poses command injection risks.",
        r'\bexecv\s*\(': "CRITICAL: The 'execv' function poses command injection risks.",
        r'\bexecvp\s*\(': "CRITICAL: The 'execvp' function poses command injection risks.",
        r'\bexecve\s*\(': "CRITICAL: The 'execve' function poses command injection risks.",

        # 3. FORMAT STRING VULNERABILITIES
        # Matches printf or syslog where the user might pass a variable directly instead of a format string
        r'\bprintf\s*\(\s*[a-zA-Z_][a-zA-Z0-9_]*\s*\)': "CRITICAL: Format string vulnerability. Never pass a variable directly to 'printf'. Use 'printf(\"%s\", var)'.",
        r'\bfprintf\s*\(\s*[a-zA-Z_][a-zA-Z0-9_]*\s*,\s*[a-zA-Z_][a-zA-Z0-9_]*\s*\)': "CRITICAL: Format string vulnerability in 'fprintf'. Ensure the format string is hardcoded.",
        r'\bsyslog\s*\(': "WARNING: Ensure you are not passing un-sanitized user input directly to 'syslog()'.",

        # 4. INSECURE TEMPORARY FILE CREATION (Race Conditions)
        r'\bmktemp\s*\(': "CRITICAL: 'mktemp' suffers from race conditions. Use 'mkstemp' instead.",
        r'\btmpnam\s*\(': "CRITICAL: 'tmpnam' is obsolete and insecure. Use 'mkstemp'.",
        r'\btempnam\s*\(': "CRITICAL: 'tempnam' is vulnerable to race conditions. Use 'mkstemp'.",

        # 5. DEPRECATED / UNSAFE C++ MEMORY MANAGEMENT
        r'\bauto_ptr\b': "CRITICAL: 'std::auto_ptr' is deprecated in C++11 and removed in C++17 due to unsafe copy semantics. Use 'std::unique_ptr'.",
        r'\bfree\s*\(': "WARNING: Mixing 'malloc/free' with 'new/delete' causes undefined behavior. Stick to C++ paradigms (new/delete or smart pointers).",
        r'\bdelete\s+': "WARNING: Manual 'delete' can lead to dangling pointers. Modern C++ heavily favors 'std::unique_ptr' or 'std::shared_ptr'.",
        r'\bscanf\s*\(\s*\"%s\"': "RISK: 'scanf' with '%s' has no bounds checking. Specify a width (e.g., '%49s') or use 'std::cin'.",

        # 6. WEAK CRYPTOGRAPHY & RANDOMNESS
        r'\brand\s*\(\s*\)': "WARNING: 'rand()' is not cryptographically secure. For security-sensitive randomness, use the '<random>' library (e.g., std::mt19937).",
        r'\bsrand\s*\(': "WARNING: Seeding with 'srand(time(NULL))' is predictable. Use a true hardware entropy source like 'std::random_device'.",

        # 7. PLATFORM & STANDARD ISSUES
        r'system\s*\(\s*\"pause\"\s*\)': "WARNING: 'system(\"pause\")' is platform-dependent (Windows only). Use 'std::cin.get()' for cross-platform compatibility.",
        r'\bvoid\s+main\b': "STANDARD: 'void main()' is non-standard C++. The standard dictates using 'int main()' and returning 0.",
        r'#include\s+<bits/stdc\+\+\.h>': "PERFORMANCE: Including '<bits/stdc++.h>' drastically increases compilation time and makes code non-portable. Include specific headers."
    }

    # Check the code against patterns
    for pattern, warning in banned_patterns.items():
        if re.search(pattern, code_snippet):
            return False, warning 

    return True, "Code looks safe."