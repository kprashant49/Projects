import subprocess

# Example: list files
result = subprocess.run(["cmd", "/c", "dir"], capture_output=True, text=True)

print("Output:\n", result.stdout)
print("Errors:\n", result.stderr)
