import pytest
from secure_scan import run_security_guardrail
from error_classifier import classify_error
from fix_engine import validate_ai_fix
import json

def test_security_guardrail():
    # Test safe code
    safe_code = "int main() { std::cout << \"Hello World\"; return 0; }"
    is_safe, findings = run_security_guardrail(safe_code)
    assert is_safe is True
    assert len(findings) == 0

    # Test unsafe code (strcpy)
    unsafe_code = "void func() { char buf[10]; strcpy(buf, \"too long string\"); }"
    is_safe, findings = run_security_guardrail(unsafe_code)
    assert is_safe is False
    assert len(findings) == 1
    assert findings[0]["severity"] == "CRITICAL"
    assert "strcpy" in findings[0]["pattern"]

    # Test system call
    unsafe_system = "system(\"rm -rf /\");"
    is_safe, findings = run_security_guardrail(unsafe_system)
    assert is_safe is False

def test_error_classifier():
    # Simulate a GCC error
    raw_error = "temp_code.cpp:4:5: error: expected ';' before 'return'"
    result = classify_error(raw_error)
    assert result["category"] == "Syntax Error"
    assert len(result["diagnostics"]) == 1
    assert result["diagnostics"][0]["line"] == 4
    assert result["diagnostics"][0]["column"] == 5
    assert result["diagnostics"][0]["severity"] == "error"

def test_validate_ai_fix_valid_json():
    # Test valid JSON with safe code
    valid_json = json.dumps({
        "what_happened": "Missing semicolon",
        "why_it_happened": "Forgot to close the statement",
        "where_it_happened": "Line 5",
        "how_to_fix": "Add semicolon",
        "concept": "Syntax",
        "practice_question": "What is the end of line character?",
        "fixed_code": "int main() { return 0; }"
    })
    
    is_safe, code, msg, parsed = validate_ai_fix(valid_json)
    assert is_safe is True
    assert code == "int main() { return 0; }"
    assert parsed["what_happened"] == "Missing semicolon"

def test_validate_ai_fix_insecure_code():
    # Test valid JSON but insecure code
    insecure_json = json.dumps({
        "what_happened": "...",
        "fixed_code": "system(\"rm -rf /\");"
    })
    
    is_safe, code, msg, parsed = validate_ai_fix(insecure_json)
    assert is_safe is False
    assert "insecure function" in msg

def test_validate_ai_fix_invalid_json():
    # Test invalid JSON format
    invalid_json = "This is not json!"
    is_safe, code, msg, parsed = validate_ai_fix(invalid_json)
    assert is_safe is False
    assert parsed is None
    assert "Failed to parse AI response as JSON" in msg
