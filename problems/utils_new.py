import subprocess
import tempfile
import os
import sys
from io import StringIO

def run_code(code, input_data, language="python"):
    """
    Run code in different programming languages locally
    """
    try:
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
from io import StringIO

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
        # Create temporary directory for Java files
        with tempfile.TemporaryDirectory() as temp_dir:
            java_file = os.path.join(temp_dir, "Solution.java")
            
            # Wrap the code in a proper Java class
            java_code = f"""
import java.util.*;
import java.io.*;

public class Solution {{
    public static void main(String[] args) {{
        try {{
{chr(10).join('            ' + line for line in code.split(chr(10)))}
        }} catch (Exception e) {{
            System.err.println("Runtime Error: " + e.getMessage());
        }}
    }}
}}
"""
            
            # Write file
            with open(java_file, 'w') as f:
                f.write(java_code)
            
            # Compile
            compile_result = subprocess.run(
                ["javac", java_file],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if compile_result.returncode != 0:
                return f"Compilation Error: {compile_result.stderr.strip()}"
            
            # Run
            run_result = subprocess.run(
                ["java", "-cp", temp_dir, "Solution"],
                input=input_data,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if run_result.returncode == 0:
                return run_result.stdout.strip()
            else:
                error_msg = run_result.stderr.strip()
                if "Runtime Error:" in error_msg:
                    return error_msg
                else:
                    return f"Runtime Error: {error_msg}"
                
    except subprocess.TimeoutExpired:
        return "Error: Code execution timed out"
    except FileNotFoundError:
        return "Error: Java compiler not found. Please install Java JDK."
    except Exception as e:
        return f"Error: {str(e)}"

def run_cpp_code(code, input_data):
    """Run C++ code locally"""
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            cpp_file = os.path.join(temp_dir, "solution.cpp")
            exe_file = os.path.join(temp_dir, "solution")
            
            # Wrap the code with necessary includes
            cpp_code = f"""
#include <iostream>
#include <vector>
#include <string>
#include <algorithm>
#include <map>
#include <set>
#include <queue>
#include <stack>
#include <sstream>
using namespace std;

int main() {{
    try {{
{chr(10).join('        ' + line for line in code.split(chr(10)))}
    }} catch (const exception& e) {{
        cerr << "Runtime Error: " << e.what() << endl;
    }}
    return 0;
}}
"""
            
            # Write file
            with open(cpp_file, 'w') as f:
                f.write(cpp_code)
            
            # Compile
            compile_result = subprocess.run(
                ["g++", "-o", exe_file, cpp_file, "-std=c++17"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if compile_result.returncode != 0:
                return f"Compilation Error: {compile_result.stderr.strip()}"
            
            # Run
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
                error_msg = run_result.stderr.strip()
                if "Runtime Error:" in error_msg:
                    return error_msg
                else:
                    return f"Runtime Error: {error_msg}"
                
    except subprocess.TimeoutExpired:
        return "Error: Code execution timed out"
    except FileNotFoundError:
        return "Error: C++ compiler not found. Please install g++."
    except Exception as e:
        return f"Error: {str(e)}"

def run_javascript_code(code, input_data):
    """Run JavaScript code locally"""
    try:
        # Create a Node.js wrapper
        js_code = f"""
const inputLines = `{input_data}`.trim().split('\\n');
let inputIndex = 0;

// Override console.log to capture output
const originalLog = console.log;
let output = [];
console.log = function(...args) {{
    output.push(args.join(' '));
}};

// Mock readline function
function readline() {{
    if (inputIndex < inputLines.length) {{
        return inputLines[inputIndex++];
    }}
    return '';
}}

try {{
{chr(10).join('    ' + line for line in code.split(chr(10)))}
}} catch (error) {{
    console.error('Runtime Error:', error.message);
}}

// Print captured output
output.forEach(line => originalLog(line));
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as temp_file:
            temp_file.write(js_code)
            temp_file_path = temp_file.name
        
        try:
            result = subprocess.run(
                ["node", temp_file_path],
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
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except subprocess.TimeoutExpired:
        return "Error: Code execution timed out"
    except FileNotFoundError:
        return "Error: Node.js not found. Please install Node.js."
    except Exception as e:
        return f"Error: {str(e)}"

def run_go_code(code, input_data):
    """Run Go code locally"""
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            go_file = os.path.join(temp_dir, "main.go")
            
            # Wrap the code with necessary package and imports
            go_code = f"""
package main

import (
    "fmt"
    "bufio"
    "strings"
    "strconv"
    "os"
)

func main() {{
    inputLines := strings.Split(`{input_data}`, "\\n")
    scanner := bufio.NewScanner(strings.NewReader(`{input_data}`))
    
    defer func() {{
        if r := recover(); r != nil {{
            fmt.Println("Runtime Error:", r)
        }}
    }}()
    
{chr(10).join('    ' + line for line in code.split(chr(10)))}
}}
"""
            
            # Write file
            with open(go_file, 'w') as f:
                f.write(go_code)
            
            # Run
            result = subprocess.run(
                ["go", "run", go_file],
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
                
    except subprocess.TimeoutExpired:
        return "Error: Code execution timed out"
    except FileNotFoundError:
        return "Error: Go compiler not found. Please install Go."
    except Exception as e:
        return f"Error: {str(e)}"

def run_rust_code(code, input_data):
    """Run Rust code locally"""
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            rust_file = os.path.join(temp_dir, "main.rs")
            
            # Wrap the code with necessary use statements
            rust_code = f"""
use std::io;
use std::collections::{{HashMap, HashSet}};

fn main() {{
    let input_data = r#"{input_data}"#;
    let mut lines = input_data.lines();
    
    std::panic::set_hook(Box::new(|panic_info| {{
        println!("Runtime Error: {{:?}}", panic_info);
    }}));
    
{chr(10).join('    ' + line for line in code.split(chr(10)))}
}}
"""
            
            # Write file
            with open(rust_file, 'w') as f:
                f.write(rust_code)
            
            # Run
            result = subprocess.run(
                ["rustc", "--edition", "2021", "-o", os.path.join(temp_dir, "main"), rust_file],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return f"Compilation Error: {result.stderr.strip()}"
            
            # Execute
            exe_result = subprocess.run(
                [os.path.join(temp_dir, "main")],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if exe_result.returncode == 0:
                return exe_result.stdout.strip()
            else:
                error_msg = exe_result.stderr.strip()
                if "Runtime Error:" in error_msg:
                    return error_msg
                else:
                    return f"Runtime Error: {error_msg}"
                
    except subprocess.TimeoutExpired:
        return "Error: Code execution timed out"
    except FileNotFoundError:
        return "Error: Rust compiler not found. Please install Rust."
    except Exception as e:
        return f"Error: {str(e)}"
