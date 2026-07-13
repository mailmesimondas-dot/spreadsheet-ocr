#!/bin/bash
# ==============================================================================
# SPREADSHEET OCR - WSL2 ONE-CLICK APK BUILDER
# ==============================================================================
# Run this script inside your Ubuntu terminal using:
#   cd "/mnt/d/SOFTWEAR/All project/image to ocr and excel antigravity"
#   bash setup_wsl_build.sh
# ==============================================================================

set -e # Exit immediately on error

echo "=========================================================="
echo "    SETTING UP WSL BUILDOZER & COMPILING APK"
echo "=========================================================="
echo ""

# 1. Update and upgrade apt packages
echo "[1/4] Updating package lists..."
sudo apt-get update

# 2. Install compiler and Android building dependencies
echo "[2/4] Installing build tools and JDK 17..."
sudo apt-get install -y git zip unzip openjdk-17-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libgdbm-dev libssl-dev libffi-dev cmake gettext build-essential python3-dev libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev libportmidi-dev

# Set Java 17 as the active JDK version
export JAVA_HOME="/usr/lib/jvm/java-17-openjdk-amd64"
sudo update-alternatives --set java /usr/lib/jvm/java-17-openjdk-amd64/bin/java || true
sudo update-alternatives --set javac /usr/lib/jvm/java-17-openjdk-amd64/bin/javac || true

# 3. Install Cython and Buildozer
echo "[3/4] Installing Cython and Buildozer..."
pip3 install --user --upgrade Cython==0.29.33 buildozer

# Ensure local bin is in PATH
export PATH="$HOME/.local/bin:$PATH"
if ! grep -q "export PATH=\"\$HOME/.local/bin:\$PATH\"" ~/.bashrc; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
    echo 'export JAVA_HOME="/usr/lib/jvm/java-17-openjdk-amd64"' >> ~/.bashrc
fi

echo "[SUCCESS] All build dependencies successfully installed."
echo ""

# 4. Clean and run Buildozer compilation
echo "[4/4] Starting Buildozer Android APK compilation..."
echo "This will take ~8-12 minutes on the first build, but subsequent builds will be <1 minute."
echo ""

buildozer android clean
buildozer android debug

echo ""
echo "=========================================================="
echo "🎉 BUILD FINISHED SUCCESSFULLY!"
echo "Your APK has been generated in the 'bin/' folder."
echo "=========================================================="
