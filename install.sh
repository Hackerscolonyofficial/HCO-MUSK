#!/data/data/com.termux/files/usr/bin/bash
set -e
cd "$(dirname "$0")"
echo "[HCO Musk] Installing packages..."
pkg update -y
pkg install python termux-api -y
mkdir -p "$HOME/storage/dcim/HCO-Musk"
echo "Installation complete."
echo "Run: python hco_musk.py"
echo "Install the Termux:API Android app separately from the same trusted source as Termux."
