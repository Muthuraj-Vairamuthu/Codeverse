import subprocess
import tempfile
import os
import sys

def run_code(code, input_data, language="python"):
    """
    Run code in different programming languages with fallback to local execution
    """
    try:
        # Try Docker first, fallback to local execution
        try:
            import docker
            client = docker.from_env()
            return run_code_docker(client, code, input_data, language)
        except Exception as docker_error:
            print(f"Docker not available: {docker_error}")
            # Fallback to local execution
            return run_code_local(code, input_data, language)
            
    except Exception as e:
        return f"Error: {str(e)}"

def run_code_local(code, input_data, language="python"):
    """
    Run code locally without Docker (fallback method)
    """
    if language == "python":
        return run_python_local(code, input_data)
    elif language == "java":
        return run_java_local(code, input_data)
    elif language == "cpp":
        return run_cpp_local(code, input_data)
    elif language == "javascript":
        return run_javascript_local(code, input_data)
    else:
        return f"Error: Language {language} not supported in local mode"

def run_python_local(code, input_data):
    """Run Python code locally"""
    try:
        # Create a safe wrapper for the code
        wrapped_code = f"""
import sys
from io import StringIO

# Redirect input
input_lines = '''{input_data}'''.strip().split('\\n')
input_index = 0

def input():
    global input_index
    if input_index < len(input_lines):
        result = input_lines[input_index]
        input_index += 1
        return result
    return ''

# Capture output
output_buffer = StringIO()
sys.stdout = output_buffer

try:
{chr(10).join('    ' + line for line in code.split(chr(10)))}
except Exception as e:
    print(f"Runtime Error: {{e}}")

# Get the output
sys.stdout = sys.__stdout__
result = output_buffer.getvalue()
print(result.strip())
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
                return f"Error: {result.stderr.strip()}"
                
        finally:
            # Clean up
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except subprocess.TimeoutExpired:
        return "Error: Code execution timed out"
    except Exception as e:
        return f"Error: {str(e)}"

def run_java_local(code, input_data):
    """Run Java code locally"""
    try:
        # Create temporary directory for Java files
        with tempfile.TemporaryDirectory() as temp_dir:
            java_file = os.path.join(temp_dir, "Solution.java")
            input_file = os.path.join(temp_dir, "input.txt")
            
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
            
            # Write files
            with open(java_file, 'w') as f:
                f.write(java_code)
            with open(input_file, 'w') as f:
                f.write(input_data)
            
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
                return f"Runtime Error: {run_result.stderr.strip()}"
                
    except subprocess.TimeoutExpired:
        return "Error: Code execution timed out"
    except FileNotFoundError:
        return "Error: Java compiler not found. Please install Java JDK."
    except Exception as e:
        return f"Error: {str(e)}"

def run_cpp_local(code, input_data):
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
                return f"Runtime Error: {run_result.stderr.strip()}"
                
    except subprocess.TimeoutExpired:
        return "Error: Code execution timed out"
    except FileNotFoundError:
        return "Error: C++ compiler not found. Please install g++."
    except Exception as e:
        return f"Error: {str(e)}"

def run_javascript_local(code, input_data):
    """Run JavaScript code locally"""
    try:
        # Create a Node.js wrapper
        js_code = f"""
const readline = require('readline');
const rl = readline.createInterface({{
    input: process.stdin,
    output: process.stdout
}});

const inputLines = `{input_data}`.trim().split('\\n');
let inputIndex = 0;

// Override readline function for compatibility
global.readline = function() {{
    if (inputIndex < inputLines.length) {{
        return inputLines[inputIndex++];
    }}
    return '';
}};

try {{
{chr(10).join('    ' + line for line in code.split(chr(10)))}
}} catch (error) {{
    console.error('Runtime Error:', error.message);
}}

rl.close();
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
                return f"Error: {result.stderr.strip()}"
                
        finally:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except subprocess.TimeoutExpired:
        return "Error: Code execution timed out"
    except FileNotFoundError:
        return "Error: Node.js not found. Please install Node.js."
    except Exception as e:
        return f"Error: {str(e)}"

def run_code_docker(client, code, input_data, language):
    """
    Run code using Docker containers (original method)
    """
    if language == "python":
        return run_python_docker(client, code, input_data)
    elif language == "java":
        return run_java_docker(client, code, input_data)
    elif language == "cpp":
        return run_cpp_docker(client, code, input_data)
    elif language == "javascript":
        return run_javascript_docker(client, code, input_data)
    elif language == "go":
        return run_go_docker(client, code, input_data)
    elif language == "rust":
        return run_rust_docker(client, code, input_data)
    else:
        return "Error: Unsupported language"

def run_python_docker(client, code, input_data):
    """Run Python code using Docker"""
    wrapped_code = f"""
import sys
input_lines = '''{input_data}'''.strip().split('\\n')
input_index = 0

def input():
    global input_index
    if input_index < len(input_lines):
        result = input_lines[input_index]
        input_index += 1
        return result
    return ''

{code}
"""
    
    container = client.containers.run(
        image="python:3.9-slim",
        command=["python", "-c", wrapped_code],
        stdout=True,
        stderr=True,
        remove=True,
        detach=False,
        mem_limit="128m",
        network_disabled=True
    )
    return container.decode('utf-8')

def run_java_docker(client, code, input_data):
        stdout=True,
        stderr=True,
        remove=True,
        detach=False,
        mem_limit="128m",
        network_disabled=True
    )
    return container.decode('utf-8')

def run_java_code(client, code, input_data):
    """Run Java code"""
    # Create temporary files
    java_code = f"""
import java.util.*;
import java.io.*;

public class Solution {{
    public static void main(String[] args) {{
        Scanner scanner = new Scanner(System.in);
        {code}
    }}
}}
"""
    
    # Create a temporary directory for compilation
    with tempfile.TemporaryDirectory() as temp_dir:
        java_file = os.path.join(temp_dir, "Solution.java")
        input_file = os.path.join(temp_dir, "input.txt")
        
        with open(java_file, 'w') as f:
            f.write(java_code)
        with open(input_file, 'w') as f:
            f.write(input_data)
        
        # Mount the temporary directory
        volumes = {temp_dir: {'bind': '/workspace', 'mode': 'rw'}}
        
        # Compile and run
        result = client.containers.run(
            image="openjdk:11-slim",
            command=["sh", "-c", "cd /workspace && javac Solution.java && java Solution < input.txt"],
            volumes=volumes,
            stdout=True,
            stderr=True,
            remove=True,
            detach=False,
            mem_limit="256m",
            network_disabled=True
        )
        return result.decode('utf-8')

def run_cpp_code(client, code, input_data):
    """Run C++ code"""
    cpp_code = f"""
#include <iostream>
#include <vector>
#include <string>
#include <algorithm>
#include <map>
#include <set>
#include <queue>
#include <stack>
using namespace std;

int main() {{
    {code}
    return 0;
}}
"""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        cpp_file = os.path.join(temp_dir, "solution.cpp")
        input_file = os.path.join(temp_dir, "input.txt")
        
        with open(cpp_file, 'w') as f:
            f.write(cpp_code)
        with open(input_file, 'w') as f:
            f.write(input_data)
        
        volumes = {temp_dir: {'bind': '/workspace', 'mode': 'rw'}}
        
        result = client.containers.run(
            image="gcc:9",
            command=["sh", "-c", "cd /workspace && g++ -o solution solution.cpp && ./solution < input.txt"],
            volumes=volumes,
            stdout=True,
            stderr=True,
            remove=True,
            detach=False,
            mem_limit="256m",
            network_disabled=True
        )
        return result.decode('utf-8')

def run_javascript_code(client, code, input_data):
    """Run JavaScript code"""
    js_code = f"""
const fs = require('fs');
const input = `{input_data}`;
const lines = input.trim().split('\\n');
let lineIndex = 0;

function readline() {{
    if (lineIndex < lines.length) {{
        return lines[lineIndex++];
    }}
    return '';
}}

{code}
"""
    
    container = client.containers.run(
        image="node:16-slim",
        command=["node", "-e", js_code],
        stdout=True,
        stderr=True,
        remove=True,
        detach=False,
        mem_limit="128m",
        network_disabled=True
    )
    return container.decode('utf-8')

def run_go_code(client, code, input_data):
    """Run Go code"""
    go_code = f"""
package main

import (
    "fmt"
    "strings"
    "strconv"
    "bufio"
    "os"
)

func main() {{
    input := `{input_data}`
    scanner := bufio.NewScanner(strings.NewReader(input))
    
    {code}
}}
"""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        go_file = os.path.join(temp_dir, "main.go")
        
        with open(go_file, 'w') as f:
            f.write(go_code)
        
        volumes = {temp_dir: {'bind': '/workspace', 'mode': 'rw'}}
        
        result = client.containers.run(
            image="golang:1.19-alpine",
            command=["sh", "-c", "cd /workspace && go run main.go"],
            volumes=volumes,
            stdout=True,
            stderr=True,
            remove=True,
            detach=False,
            mem_limit="256m",
            network_disabled=True
        )
        return result.decode('utf-8')

def run_rust_code(client, code, input_data):
    """Run Rust code"""
    rust_code = f"""
use std::io;

fn main() {{
    let input = r#"{input_data}"#;
    let mut lines = input.trim().lines();
    
    {code}
}}
"""
    
    with tempfile.TemporaryDirectory() as temp_dir:
        rust_file = os.path.join(temp_dir, "main.rs")
        
        with open(rust_file, 'w') as f:
            f.write(rust_code)
        
        volumes = {temp_dir: {'bind': '/workspace', 'mode': 'rw'}}
        
        result = client.containers.run(
            image="rust:1.70-slim",
            command=["sh", "-c", "cd /workspace && rustc main.rs && ./main"],
            volumes=volumes,
            stdout=True,
            stderr=True,
            remove=True,
            detach=False,
            mem_limit="256m",
            network_disabled=True
        )
        return result.decode('utf-8')
