
#!/data/data/com.termux/files/usr/bin/bash

set -e

cd "$(dirname "$0")"

echo "[HCO Musk] Installing core packages..."

pkg update -y

pkg install -y python git cloudflared nodejs

if command -v npm >/dev/null 2>&1; then

    npm install -g localtunnel || echo "LocalTunnel install skipped; you can install it later with: npm install -g localtunnel"

fi

mkdir -p "$HOME/storage/dcim/HCO-Musk"

echo
echo "Core installation complete."
echo "Optional: install ngrok agent and configure:"
echo "ngrok config add-authtoken YOUR_TOKEN"
echo
echo "Run: python hco_musk.py"
