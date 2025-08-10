import sys
import subprocess
import os

def build_docker_image_for_version():
    # Retrieve Python version information from the environment running this script
    major_version = sys.version_info.major
    minor_version = sys.version_info.minor
    patch_version = sys.version_info.micro

    print(f"Detected Python version: {major_version}.{minor_version}.{patch_version}")

    # Determine the Dockerfile and image tag based on the Python version
    dockerfile_name = None
    image_tag = None
    
    if version_majeure == 3 and (version_mineure >= 9 and version_mineure < 10):
        dockerfile_name = "Dockerfile_py309"
        image_tag = "py309"
    elif version_majeure == 3 and (version_mineure >= 10 and version_mineure < 11):
        dockerfile_name = "Dockerfile_py310"
        image_tag = "py310"
    elif version_majeure == 3 and version_mineure >= 11:
        dockerfile_name = "Dockerfile_py311"
        image_tag = "py311"
    else:
        print(f"No specific Dockerfile defined for Python version {major_version}.{minor_version}.")
        print("Please ensure you have a Dockerfile (e.g., Dockerfile_pyX_Y) for this version.")
        return # Exit if no specific Dockerfile is found

    full_image_name = f"your_app_name:{image_tag}" # Customize 'your_app_name'

    if dockerfile_name:
        if not os.path.exists(dockerfile_name):
            print(f"Error: Dockerfile '{dockerfile_name}' not found in the current directory.", file=sys.stderr)
            print("Please ensure your Dockerfiles are correctly named and located.", file=sys.stderr)
            sys.exit(1) # Exit if the specified Dockerfile doesn't exist

        print(f"Attempting to build Docker image '{full_image_name}' using '{dockerfile_name}'...")
        try:
            # Construct the docker build command
            command = [
                "docker", "build",
                "-t", full_image_name,
                "-f", dockerfile_name,
                "."  # The build context (current directory)
            ]
            result = subprocess.run(command, check=True, capture_output=True, text=True)

            # Execute the Docker command
            print(f"Docker image '{full_image_name}' built successfully!")
            print("--- Docker Build Output ---")
            print(result.stdout)
            if result.stderr:
                print("--- Docker Build Warnings/Errors ---")
                print(result.stderr)
            print("---------------------------")

        except FileNotFoundError:
            print("Error: 'docker' command not found. Is Docker Desktop or Docker Engine installed and in your PATH?", file=sys.stderr)
            sys.exit(1)
        except subprocess.CalledProcessError as e:
            print(f"Error building Docker image '{full_image_name}':", file=sys.stderr)
            print(f"Exit Code: {e.returncode}", file=sys.stderr)
            print(f"Standard Output: \n{e.stdout}", file=sys.stderr)
            print(f"Standard Error: \n{e.stderr}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"An unexpected error occurred: {e}", file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    build_docker_image_for_version()