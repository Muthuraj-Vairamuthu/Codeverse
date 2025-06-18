import docker

def run_code(code, input_data):
    client = docker.from_env()

    wrapped_code = f"""
input_data = \"\"\"{input_data}\"\"\".split("\\n")
input = lambda: input_data.pop(0)
{code}
"""

    container = client.containers.run(
        image="python:3.9",
        command=["python", "-c", wrapped_code],
        stdout=True,
        stderr=True,
        remove=True,
    )

    return container.decode()

if __name__ == "__main__":
    code = "a = int(input())\nb = int(input())\nprint(a + b)"
    input_data = "2\n3"
    output = run_code(code, input_data)
    print("Output:\n", output)
