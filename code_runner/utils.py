import docker

def run_code_in_docker(code: str, input_data: str) -> str:
    client = docker.from_env()

    wrapped_code = f"""
input_data = \"\"\"{input_data}\"\"\".split("\\n")
input = lambda: input_data.pop(0)
{code}
"""

    try:
        container = client.containers.run(
            image="python:3.9",
            command=["python", "-c", wrapped_code],
            stdout=True,
            stderr=True,
            remove=True,
        )
        return container.decode()
    except docker.errors.ContainerError as e:
        return f"Runtime Error:\n{e.stderr.decode() if e.stderr else str(e)}"
    except Exception as e:
        return f"Unexpected Error:\n{str(e)}"
