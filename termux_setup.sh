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

# Install the Python project
echo "Starting Python project installation (this may take a while)..."
pip install . --verbose || { echo "Error: Python project installation failed."; exit 1; }

echo "--- Project installation complete ---"

# Final move
echo "Changing to the ~/storage/downloads directory."
cd ~/storage/downloads || { echo "Error: Failed to change to ~/storage/downloads at the end of the script."; } # Not a fatal failure

echo "You can now start the crawler by typing 'lncrawl' (if installed in the PATH) or by navigating to ~/lightnovel-crawler."
