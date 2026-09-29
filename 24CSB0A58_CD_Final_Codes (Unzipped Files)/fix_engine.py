import json
from secure_scan import run_security_guardrail

def validate_ai_fix(llm_response):
    """
    Extracts the C++ code block from the LLM's JSON response and scans it for vulnerabilities.
    Returns: (is_safe, extracted_code, security_warning, parsed_json)
    """
    try:
        # LLM might wrap the JSON in markdown blocks, so we clean it up
        cleaned_response = llm_response.strip()
        if cleaned_response.startswith('```json'):
            cleaned_response = cleaned_response[7:]
        if cleaned_response.startswith('```'):
            cleaned_response = cleaned_response[3:]
        if cleaned_response.endswith('```'):
            cleaned_response = cleaned_response[:-3]
            
        parsed_json = json.loads(cleaned_response)
        extracted_code = parsed_json.get("fixed_code", "")
        
        if not extracted_code:
            return False, None, "No fixed_code found in the AI suggestion.", parsed_json
            
        # 2. Validate the AI-generated code for secure coding practices
        is_safe, findings = run_security_guardrail(extracted_code)
        
        if not is_safe:
            warning_msg = "\n".join([f"- Line {f['line']}: `{f['pattern']}` ({f['severity']}). {f['reason']}" for f in findings if f['severity'] == 'CRITICAL'])
            return False, extracted_code, f"The AI suggested an insecure function:\n{warning_msg}", parsed_json
            
        return True, extracted_code, "The suggested fix is secure.", parsed_json
        
    except json.JSONDecodeError as e:
        return False, None, f"Failed to parse AI response as JSON: {str(e)}", None