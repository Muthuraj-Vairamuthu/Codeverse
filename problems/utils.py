import subprocess
import tempfile
import os
import sys

def run_code(code, input_data, language="python", use_docker=False):
    """
    Run code in different programming languages locally or in Docker
    """
    try:
        # Try Docker first if available and requested
        if use_docker:
            try:
                from .docker_runner import docker_runner
                result = docker_runner.run_code_in_docker(code, input_data, language)
                if not result.startswith("Error: Docker"):
                    return result
                # Fall back to local execution if Docker fails
            except ImportError:
                pass  # Fall back to local execution
        
        # Local execution
        if language == "python":
            return run_python_code(code, input_data)
        elif language == "java":
            return run_java_code(code, input_data)
        elif language == "cpp":
            return run_cpp_code(code, input_data)
        elif language == "javascript":
            return run_javascript_code(code, input_data)
        elif language == "go":
            return run_go_code(code, input_data)
        elif language == "rust":
            return run_rust_code(code, input_data)
        else:
            return f"Error: Language {language} not supported"
            
    except Exception as e:
        return f"Error: {str(e)}"

def run_python_code(code, input_data):
    """Run Python code locally"""
    try:
        # Create a safe wrapper for the code
        wrapped_code = f"""
import sys

# Prepare input
input_lines = '''{input_data}'''.strip().split('\\n')
input_index = 0

def input():
    global input_index
    if input_index < len(input_lines):
        result = input_lines[input_index]
        input_index += 1
        return result
    return ''

# Execute user code
try:
{chr(10).join('    ' + line for line in code.split(chr(10)))}
except Exception as e:
    print(f"Runtime Error: {{e}}")
"""
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
            temp_file.write(wrapped_code)
            temp_file_path = temp_file.name
        
        try:
            # Run the code with timeout
            result = subprocess.run(
                [sys.executable, temp_file_path],
                capture_output=True,
                text=True,
                timeout=5  # 5 second timeout
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                error_msg = result.stderr.strip()
                if "Runtime Error:" in error_msg:
                    return error_msg
                else:
                    return f"Error: {error_msg}"
                
        finally:
            # Clean up
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except subprocess.TimeoutExpired:
        return "Error: Code execution timed out"
    except Exception as e:
        return f"Error: {str(e)}"

def run_java_code(code, input_data):
    """Run Java code locally"""
    try:
        # Create temporary directory
        import uuid
        temp_dir = tempfile.mkdtemp()
        class_name = "Solution"
        
        # Wrap the code with proper main method if needed
        if "public static void main" not in code:
            wrapped_code = f"""
import java.util.Scanner;

public class {class_name} {{
    public static void main(String[] args) {{
        Scanner scanner = new Scanner(System.in);
{chr(10).join('        ' + line for line in code.split(chr(10)))}
        scanner.close();
    }}
}}
"""
        else:
            # Extract class name from code if present
            import re
            class_match = re.search(r'public\s+class\s+(\w+)', code)
            if class_match:
                class_name = class_match.group(1)
            wrapped_code = code
        
        java_file_path = os.path.join(temp_dir, f"{class_name}.java")
        class_file_path = os.path.join(temp_dir, f"{class_name}.class")
        
        # Write Java code to file
        with open(java_file_path, 'w') as f:
            f.write(wrapped_code)
        
        try:
            # Compile Java code
            compile_result = subprocess.run(
                ['javac', java_file_path],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if compile_result.returncode != 0:
                return f"Compilation Error: {compile_result.stderr}"
            
            # Run Java code
            run_result = subprocess.run(
                ['java', '-cp', temp_dir, class_name],
                input=input_data,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if run_result.returncode == 0:
                return run_result.stdout.strip()
            else:
                return f"Runtime Error: {run_result.stderr}"
                
        finally:
            # Clean up
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
            
    except subprocess.TimeoutExpired:
        return "Error: Code execution timed out"
    except FileNotFoundError:
        return "Error: Java compiler not found. Please install Java JDK"
    except Exception as e:
        return f"Error: {str(e)}"

def run_cpp_code(code, input_data):
    """Run C++ code locally"""
    try:
        # Create temporary files
        cpp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.cpp', delete=False)
        exe_file = cpp_file.name.replace('.cpp', '.exe')
        
        # Add necessary headers if not present
        if "#include" not in code:
            wrapped_code = f"""
#include <iostream>
#include <string>
#include <vector>
#include <algorithm>
using namespace std;

{code}
"""
        else:
            wrapped_code = code
        
        cpp_file.write(wrapped_code)
        cpp_file.close()
        
        try:
            # Compile C++ code
            compile_result = subprocess.run(
                ['g++', '-o', exe_file, cpp_file.name, '-std=c++17'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if compile_result.returncode != 0:
                return f"Compilation Error: {compile_result.stderr}"
            
            # Run C++ executable
            run_result = subprocess.run(
                [exe_file],
                input=input_data,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if run_result.returncode == 0:
                return run_result.stdout.strip()
            else:
                return f"Runtime Error: {run_result.stderr}"
                
        finally:
            # Clean up
            if os.path.exists(cpp_file.name):
                os.unlink(cpp_file.name)
            if os.path.exists(exe_file):
                os.unlink(exe_file)
                
    except subprocess.TimeoutExpired:
        return "Error: Code execution timed out"
    except FileNotFoundError:
        return "Error: GCC compiler not found. Please install GCC"
    except Exception as e:
        return f"Error: {str(e)}"

def run_javascript_code(code, input_data):
    """Run JavaScript code using Node.js"""
    try:
        # Create a wrapper for JavaScript code
        wrapped_code = f"""
const inputLines = `{input_data}`.trim().split('\\n');
let inputIndex = 0;

// Mock readline for input
const readline = {{
    question: (query, callback) => {{
        if (inputIndex < inputLines.length) {{
            callback(inputLines[inputIndex++]);
        }} else {{
            callback('');
        }}
    }}
}};

// Simple input function
function input() {{
    if (inputIndex < inputLines.length) {{
        return inputLines[inputIndex++];
    }}
    return '';
}}

// Execute user code
try {{
{chr(10).join('    ' + line for line in code.split(chr(10)))}
}} catch (error) {{
    console.log('Runtime Error:', error.message);
}}
"""
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as temp_file:
            temp_file.write(wrapped_code)
            temp_file_path = temp_file.name
        
        try:
            # Run JavaScript code with Node.js
            result = subprocess.run(
                ['node', temp_file_path],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                error_msg = result.stderr.strip()
                if "Runtime Error:" in error_msg:
                    return error_msg
                else:
                    return f"Error: {error_msg}"
                
        finally:
            # Clean up
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except subprocess.TimeoutExpired:
        return "Error: Code execution timed out"
    except FileNotFoundError:
        return "Error: Node.js not found. Please install Node.js"
    except Exception as e:
        return f"Error: {str(e)}"

def run_go_code(code, input_data):
    """Run Go code locally"""
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.go', delete=False) as temp_file:
            # Add package main if not present
            if "package main" not in code:
                wrapped_code = f"""
package main

import (
    "fmt"
    "bufio"
    "os"
    "strings"
)

var scanner *bufio.Scanner

func init() {{
    input := `{input_data}`
    scanner = bufio.NewScanner(strings.NewReader(input))
}}

func Scan() string {{
    if scanner.Scan() {{
        return scanner.Text()
    }}
    return ""
}}

{code}
"""
            else:
                wrapped_code = code
            
            temp_file.write(wrapped_code)
            temp_file_path = temp_file.name
        
        try:
            # Run Go code
            result = subprocess.run(
                ['go', 'run', temp_file_path],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                error_msg = result.stderr.strip()
                return f"Error: {error_msg}"
                
        finally:
            # Clean up
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except subprocess.TimeoutExpired:
        return "Error: Code execution timed out"
    except FileNotFoundError:
        return "Error: Go compiler not found. Please install Go"
    except Exception as e:
        return f"Error: {str(e)}"

def run_rust_code(code, input_data):
    """Run Rust code locally"""
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.rs', delete=False) as temp_file:
            # Add main function if not present
            if "fn main()" not in code:
                wrapped_code = f"""
use std::io;

fn input() -> String {{
    static mut INPUT_LINES: Vec<String> = Vec::new();
    static mut INPUT_INDEX: usize = 0;
    
    unsafe {{
        if INPUT_LINES.is_empty() {{
            INPUT_LINES = r#"{input_data}"#.lines().map(|s| s.to_string()).collect();
        }}
        
        if INPUT_INDEX < INPUT_LINES.len() {{
            let result = INPUT_LINES[INPUT_INDEX].clone();
            INPUT_INDEX += 1;
            result
        }} else {{
            String::new()
        }}
    }}
}}

fn main() {{
{chr(10).join('    ' + line for line in code.split(chr(10)))}
}}
"""
            else:
                wrapped_code = code
            
            temp_file.write(wrapped_code)
            temp_file_path = temp_file.name
        
        try:
            # Compile Rust code
            exe_file = temp_file_path.replace('.rs', '')
            compile_result = subprocess.run(
                ['rustc', temp_file_path, '-o', exe_file],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if compile_result.returncode != 0:
                return f"Compilation Error: {compile_result.stderr}"
            
            # Run Rust executable
            run_result = subprocess.run(
                [exe_file],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if run_result.returncode == 0:
                return run_result.stdout.strip()
            else:
                return f"Runtime Error: {run_result.stderr}"
                
        finally:
            # Clean up
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
            if os.path.exists(exe_file):
                os.unlink(exe_file)
                
    except subprocess.TimeoutExpired:
        return "Error: Code execution timed out"
    except FileNotFoundError:
        return "Error: Rust compiler not found. Please install Rust"
    except Exception as e:
        return f"Error: {str(e)}"