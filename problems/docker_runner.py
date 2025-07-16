import docker
import tempfile
import os
import json
import time

class DockerCodeRunner:
    def __init__(self):
        try:
            self.client = docker.from_env()
            self.client.ping()
            self.docker_available = True
        except Exception as e:
            print(f"Docker not available: {e}")
            self.docker_available = False
    
    def run_code_in_docker(self, code, input_data, language="python", timeout=10):
        """Run code in a secure Docker container"""
        if not self.docker_available:
            return "Error: Docker is not available"
        
        try:
            # Language configurations
            configs = {
                "python": {
                    "image": "python:3.9-alpine",
                    "file_ext": ".py",
                    "cmd_template": ["python", "/app/solution{ext}"]
                },
                "java": {
                    "image": "openjdk:11-alpine",
                    "file_ext": ".java",
                    "cmd_template": ["sh", "-c", "cd /app && javac Solution.java && java Solution"]
                },
                "cpp": {
                    "image": "gcc:alpine",
                    "file_ext": ".cpp",
                    "cmd_template": ["sh", "-c", "cd /app && g++ -o solution solution.cpp && ./solution"]
                },
                "javascript": {
                    "image": "node:16-alpine",
                    "file_ext": ".js",
                    "cmd_template": ["node", "/app/solution{ext}"]
                },
                "go": {
                    "image": "golang:alpine",
                    "file_ext": ".go",
                    "cmd_template": ["go", "run", "/app/solution{ext}"]
                }
            }
            
            if language not in configs:
                return f"Error: Language {language} not supported in Docker"
            
            config = configs[language]
            
            # Prepare code based on language
            if language == "python":
                wrapped_code = self._wrap_python_code(code, input_data)
            elif language == "java":
                wrapped_code = self._wrap_java_code(code, input_data)
            elif language == "cpp":
                wrapped_code = self._wrap_cpp_code(code, input_data)
            elif language == "javascript":
                wrapped_code = self._wrap_javascript_code(code, input_data)
            elif language == "go":
                wrapped_code = self._wrap_go_code(code, input_data)
            else:
                wrapped_code = code
            
            # Create temporary directory for code
            with tempfile.TemporaryDirectory() as temp_dir:
                file_path = os.path.join(temp_dir, f"solution{config['file_ext']}")
                
                with open(file_path, 'w') as f:
                    f.write(wrapped_code)
                
                # Format command
                cmd = [c.format(ext=config['file_ext']) for c in config['cmd_template']]
                
                # Run container
                try:
                    container = self.client.containers.run(
                        image=config['image'],
                        command=cmd,
                        volumes={temp_dir: {'bind': '/app', 'mode': 'ro'}},
                        working_dir='/app',
                        mem_limit='128m',
                        cpu_quota=50000,  # 50% CPU
                        network_disabled=True,
                        remove=True,
                        detach=True
                    )
                    
                    # Wait for completion with timeout
                    start_time = time.time()
                    while container.status != 'exited' and time.time() - start_time < timeout:
                        time.sleep(0.1)
                        container.reload()
                    
                    if time.time() - start_time >= timeout:
                        container.kill()
                        return "Error: Code execution timed out"
                    
                    # Get output
                    logs = container.logs().decode('utf-8')
                    
                    if container.attrs['State']['ExitCode'] == 0:
                        return logs.strip()
                    else:
                        return f"Runtime Error: {logs.strip()}"
                        
                except docker.errors.ContainerError as e:
                    return f"Container Error: {e.stderr.decode('utf-8') if e.stderr else str(e)}"
                except docker.errors.ImageNotFound:
                    return f"Error: Docker image {config['image']} not found"
                
        except Exception as e:
            return f"Docker Error: {str(e)}"
    
    def _wrap_python_code(self, code, input_data):
        return f"""
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
    
    def _wrap_java_code(self, code, input_data):
        if "public static void main" not in code:
            return f"""
import java.util.Scanner;

public class Solution {{
    private static String[] inputLines = {json.dumps(input_data.split(chr(10)))};
    private static int inputIndex = 0;
    
    public static String nextLine() {{
        if (inputIndex < inputLines.length) {{
            return inputLines[inputIndex++];
        }}
        return "";
    }}
    
    public static void main(String[] args) {{
{chr(10).join('        ' + line for line in code.split(chr(10)))}
    }}
}}
"""
        else:
            # Replace class name with Solution
            import re
            code = re.sub(r'public\s+class\s+\w+', 'public class Solution', code)
            return code
    
    def _wrap_cpp_code(self, code, input_data):
        if "#include" not in code:
            return f"""
#include <iostream>
#include <string>
#include <vector>
#include <sstream>
using namespace std;

vector<string> inputLines;
int inputIndex = 0;

string getline_custom() {{
    if (inputIndex < inputLines.size()) {{
        return inputLines[inputIndex++];
    }}
    return "";
}}

int main() {{
    string input = R"({input_data})";
    stringstream ss(input);
    string line;
    while (getline(ss, line)) {{
        inputLines.push_back(line);
    }}
    
{chr(10).join('    ' + line for line in code.split(chr(10)))}
    return 0;
}}
"""
        else:
            return code
    
    def _wrap_javascript_code(self, code, input_data):
        return f"""
const inputLines = `{input_data}`.trim().split('\\n');
let inputIndex = 0;

function input() {{
    if (inputIndex < inputLines.length) {{
        return inputLines[inputIndex++];
    }}
    return '';
}}

try {{
{chr(10).join('    ' + line for line in code.split(chr(10)))}
}} catch (error) {{
    console.log('Runtime Error:', error.message);
}}
"""
    
    def _wrap_go_code(self, code, input_data):
        if "package main" not in code:
            return f"""
package main

import (
    "fmt"
    "strings"
)

var inputLines []string
var inputIndex int

func init() {{
    input := `{input_data}`
    inputLines = strings.Split(strings.TrimSpace(input), "\\n")
    inputIndex = 0
}}

func Scan() string {{
    if inputIndex < len(inputLines) {{
        result := inputLines[inputIndex]
        inputIndex++
        return result
    }}
    return ""
}}

func main() {{
{chr(10).join('    ' + line for line in code.split(chr(10)))}
}}
"""
        else:
            return code

# Global instance
docker_runner = DockerCodeRunner()
