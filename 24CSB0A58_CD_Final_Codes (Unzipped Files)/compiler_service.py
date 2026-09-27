import subprocess
import os

def compile_and_run(cpp_code):
    """
    Compiles with '-g' for LLDB support and runs the code.
    Returns: (status_code, stdout, stderr)
      0 = Success
      1 = Compile Error
      2 = Runtime Error (Segfault/Crash)
     -1 = Timeout/System Error
    """
    source_file = "temp_source.cpp"
    executable = "./temp_program"

    with open(source_file, "w") as f:
        f.write(cpp_code)

    try:
        # 1. COMPILE (Now with -g for debug symbols!)
        compile_process = subprocess.run(
            ["g++", "-g", source_file, "-o", executable.strip("./")], 
            capture_output=True, 
            text=True, 
            timeout=10
        )

        if compile_process.returncode != 0:
            return 1, "", compile_process.stderr

        # 2. RUN BINARY
        run_process = subprocess.run(
            [executable], 
            capture_output=True, 
            text=True, 
            timeout=5
        )
        # 3. CATCH RUNTIME CRASHES (Like SegFaults)
        if run_process.returncode < 0:
            # On Mac, SegFaults sometimes just return a negative exit code
            crash_reason = run_process.stderr if run_process.stderr else f"Process crashed with exit code {run_process.returncode} (Likely Segmentation Fault)"
            return 2, run_process.stdout, crash_reason
        # 4. GRACEFUL EXITS (e.g., return 0, or user-defined return 1)
        # We combine stdout and stderr so the user can see their custom std::cerr messages!
        full_output = run_process.stdout
        if run_process.stderr:
            full_output += "\n" + run_process.stderr
            
        return 0, full_output.strip(), ""
    except subprocess.TimeoutExpired:
        return -1, "", "❌ Time Limit Exceeded! Possible infinite loop."
    except Exception as e:
        return -1, "", f"❌ System Error: {str(e)}"