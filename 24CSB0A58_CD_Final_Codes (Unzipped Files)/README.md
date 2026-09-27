# Chatbot-Driven C++ Compiler Debugger
An Automated Program Repair (APR) teaching assistant designed to help college students securely diagnose and fix C++ compilation errors using localized AI.

## Proposed Architecture
Our architecture functions as a secure wrapper around the standard GCC compiler.
* **Frontend:** Streamlit-based web UI.
* **Execution Sandbox:** Python subprocess layer with strict timeout constraints.
* **Diagnostic Engine:** Heuristic classification module for raw GCC errors.
* **AI Core:** Localized Llama 3 Large Language Model (LLM).
* **Security Pipeline:** Bi-directional validation system (Pre-scan and Post-scan).

## Methodology / Pipeline
1. **Ingestion & Pre-Scan:** Scans user input for malicious system calls.
2. **Compilation:** Passes code to GCC within a sandboxed timeout.
3. **Classification:** Intercepts compiler errors and classifies them using a rule-based engine.
4. **AI Generation:** LLM receives a constrained prompt to generate a pedagogical fix.
5. **Post-Scan Audit:** Validates the LLM's suggested code before presenting it to the user.
