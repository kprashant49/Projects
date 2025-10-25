import subprocess

# Set your base folder
base_dir = r"D:\Projects\misc_projects"

# Run first command inside that folder
result = subprocess.run(
    ["cmd", "/c", "dir"],
    capture_output=True,
    text=True,
    cwd=base_dir
)

print("Output:\n", result.stdout)

# Run another command in the same folder
if result.returncode == 0:
    next_result = subprocess.run(
        ["cmd", "/c", "cd .. && dir"],
        capture_output=True,
        text=True,
        cwd=base_dir
    )
    print("\n After moving up a directory:")
    print(next_result.stdout)
