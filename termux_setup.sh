#!/data/data/com.termux/files/usr/bin/bash

echo "--- Starting Termux setup and system dependency installation ---"

# 1. Updating Termux repositories and base packages
echo "Updating Termux repositories and base packages..."
termux-change-repo || { echo "Error: termux-change-repo failed. Make sure termux-tools is installed and storage is configured."; exit 1; }
pkg update && pkg upgrade -y || { echo "Error: pkg update/upgrade failed."; exit 1; }

# 2. Installing essential build dependencies via pkg
echo "Installing required build tools and libraries via pkg..."
pkg install python git rust clang make autoconf automake libtool pkg-config patch binutils libuv postgresql libxml2 libxslt libjpeg-turbo zlib libtiff freetype libwebp openjpeg -y || { echo "Error: System package installation failed."; exit 1; }

# 3. Installing maturin via pip
echo "Installing maturin via pip..."
pip install maturin==1.8.6 || { echo "Error: Maturin installation failed."; exit 1; }

# 4. Updating Python build tools
echo "Updating Python build tools (pip, setuptools, wheel)..."
pip install --upgrade pip setuptools wheel || { echo "Error: Python tools update failed."; exit 1; }

echo "--- Termux setup complete ---"
echo "--- Cloning and installing the lightnovel-crawler project ---"

export CFLAGS="-Wno-error=incompatible-function-pointer-types"

# Check if the repository is already cloned
if [ -d "$HOME/lightnovel-crawler" ]; then
    echo "The lightnovel-crawler directory already exists. Skipping clone."
else
    echo "Cloning the repository into directory: $(pwd)"
    git clone https://github.com/thibaud200/lightnovel-crawler.git || { echo "Error: Repository cloning failed. Check the URL or your connection."; exit 1; }
fi

# Enter the project directory
cd "$HOME/lightnovel-crawler" || { echo "Error: Failed to enter the lightnovel-crawler directory."; exit 1; }

# --- START OF SPECIFIC CONFIGURATION FILE MANAGEMENT LOGIC ---

# Detect Python version
PYTHON_MAJOR=$(python -c 'import sys; print(sys.version_info.major)')
PYTHON_MINOR=$(python -c 'import sys; print(sys.version_info.minor)')
PYTHON_VERSION_TAG="${PYTHON_MAJOR}0${PYTHON_MINOR}" # E.g.: 309, 310, 311 (for file names)

echo "Detected Python version: ${PYTHON_MAJOR}.${PYTHON_MINOR}. Using config tag: ${PYTHON_VERSION_TAG}"

# Define specific configuration file names
# Ensure the path "./install_Specific/" is correct relative to the repository root.
SPECIFIC_PYPROJECT="./install_Specific/pyproject${PYTHON_VERSION_TAG}.toml"
SPECIFIC_REQUIREMENTS="./install_Specific/requirements_${PYTHON_VERSION_TAG}.txt"

# Check if specific files exist
if [ ! -f "$SPECIFIC_PYPROJECT" ]; then
    echo "Error: Specific pyproject.toml not found: $SPECIFIC_PYPROJECT"
    echo "Please ensure 'install_Specific/pyproject${PYTHON_VERSION_TAG}.toml' exists for your Python version."
    exit 1
fi
if [ ! -f "$SPECIFIC_REQUIREMENTS" ]; then
    echo "Error: Specific requirements.txt not found: $SPECIFIC_REQUIREMENTS"
    echo "Please ensure 'install_Specific/requirements_${PYTHON_VERSION_TAG}.txt' exists for your Python version."
    exit 1
fi

echo "Backing up original pyproject.toml and requirements.txt..."
# Save original files (if they exist)
if [ -f "pyproject.toml" ]; then
    mv pyproject.toml pyproject.toml.bak
else
    echo "No original pyproject.toml found to backup."
fi

if [ -f "requirements.txt" ]; then
    mv requirements.txt requirements.txt.bak
else
    echo "No original requirements.txt found to backup."
fi

echo "Copying Termux-specific configuration files..."
# Copy the specific pyproject.toml and rename it to pyproject.toml
cp "$SPECIFIC_PYPROJECT" pyproject.toml || { echo "Error: Failed to copy $SPECIFIC_PYPROJECT."; exit 1; }

# Copy the specific requirements.txt (without renaming, as the pyproject.toml will point to it)
cp "$SPECIFIC_REQUIREMENTS" "requirements_${PYTHON_VERSION_TAG}.txt" || { echo "Error: Failed to copy $SPECIFIC_REQUIREMENTS."; exit 1; }

# --- END OF SPECIFIC CONFIGURATION FILE MANAGEMENT LOGIC ---

# Install the Python project
echo "Starting Python project installation (this may take a while)..."
pip install . --verbose || { echo "Error: Python project installation failed."; exit 1; }

echo "--- Project installation complete ---"

# --- RESTORING ORIGINAL FILES ---
echo "Restoring original pyproject.toml and requirements.txt..."
if [ -f "pyproject.toml.bak" ]; then
    mv pyproject.toml.bak pyproject.toml
else
    echo "No pyproject.toml.bak found to restore."
fi

if [ -f "requirements.txt.bak" ]; then
    mv requirements.txt.bak requirements.txt
else
    echo "No requirements.txt.bak found to restore."
fi
# --- END RESTORATION ---

# Final move
echo "Changing to the ~/storage/downloads directory."
cd ~/storage/downloads || { echo "Error: Failed to change to ~/storage/downloads at the end of the script."; } # Not a fatal failure

echo "You can now start the crawler by typing 'lncrawl' (if installed in the PATH) or by navigating to ~/lightnovel-crawler."
