#!/usr/bin/env bash
echo "======================================================="
echo "         AI Voice Cloning - Automated Installer (Mac)"
echo "======================================================="
echo ""
echo "This script will automatically check for and install all"
echo "required dependencies to run the Voice Cloning AI on macOS."
echo ""

# 1. Check for Homebrew
echo "[1/4] Checking for Homebrew (Package Manager)..."
if ! command -v brew &> /dev/null; then
    echo "[!] Homebrew is missing. Installing Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    echo "eval \"\$(/opt/homebrew/bin/brew shellenv)\"" >> ~/.zprofile
    eval "$(/opt/homebrew/bin/brew shellenv)"
else
    echo "[OK] Homebrew is installed."
fi

# 2. Check for Python, Node, and FFmpeg
echo ""
echo "[2/4] Checking System Dependencies (Python, Node, FFmpeg)..."
brew install python@3.10 node ffmpeg

# 3. Backend Setup
echo ""
echo "[3/4] Setting up the AI Engine (Backend)..."
cd "$(dirname "$0")/backend" || exit

if [ ! -d "venv" ]; then
    echo "[i] Creating Python Virtual Environment..."
    python3.10 -m venv venv
fi
source venv/bin/activate

echo "[i] Installing AI Libraries..."
pip install --upgrade pip
pip install -r requirements.txt
pip install -r voice_clone_worker/requirements.txt

if [ ! -d "venv_clone" ]; then
    echo "[i] Installing Voice Cloning Sub-Engine..."
    # The sub-engine requires its own venv because of strict torch versions
    python3.10 -m venv venv_clone
    source venv_clone/bin/activate
    pip install torch==2.1.1 torchaudio==2.1.1
    pip install -r voice_clone_worker/requirements.txt
    deactivate
    source venv/bin/activate
fi
cd ..

# 4. Frontend Setup
echo ""
echo "[4/4] Setting up the User Interface (Frontend)..."
cd frontend || exit
echo "[i] Installing UI dependencies (this may take a minute)..."
npm install --no-fund --no-audit
cd ..

echo ""
echo "======================================================="
echo "                INSTALLATION COMPLETE!                 "
echo "======================================================="
echo ""
echo "All requirements have been successfully installed."
echo ""
echo "To start the app, open Terminal in this folder and run:"
echo "sh start_all.sh"
echo ""
