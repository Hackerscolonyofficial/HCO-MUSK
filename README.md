
# HCO Musk

**HCO Musk** is a consent-first Python + Termux surprise-link toolkit by **Azhar Team HCO**.

YouTube: https://youtube.com/@hackers_colony_tech?si=6Uc1vADFNroqTvUP

## Features

- Custom surprise message links.
- Location-sharing links that clearly explain the browser permission request.
- Front/rear camera preview links with explicit user action and browser permission.
- Photo surprise landing page (does not read a recipient's private gallery).
- Local web server with public tunnel options: Cloudflare Quick Tunnel, ngrok, and LocalTunnel.
- Colourful Termux menu and YouTube support-page countdown.

## Privacy and safe use

The link does not secretly activate a camera or obtain a location. A recipient sees what permission is requested and must press the relevant button and approve the browser prompt.

Location is displayed in their browser and is not sent to HCO Musk.

Camera preview is local to their browser; optional capture downloads the image to their device. This webpage has no upload endpoint.

Do not disguise permission prompts or send surprise links to people who have not agreed to receive them. Only share with people who understand what the page does.

## Requirements

- Android + Termux + Python 3.
- Internet connection.
- For tunnel options: `cloudflared`, `ngrok`, or Node.js + LocalTunnel, depending on provider.
- Browser on recipient's device. Camera and geolocation browser APIs require HTTPS (or localhost).

## Install

```bash
pkg update -y && pkg upgrade -y

pkg install python git cloudflared nodejs -y

npm install -g localtunnel

git clone https://github.com/Hackerscolonyofficial/HCO-MUSK.git

cd HCO-MUSK

chmod +x install.sh

bash install.sh

python hco_musk.py
```

### ngrok setup (optional)

Create an ngrok account, install the official ngrok agent for your Termux architecture, then configure your token once:

```bash
ngrok config add-authtoken YOUR_NGROK_AUTHTOKEN
```

Do not paste your token into public GitHub files or share it with anyone.

## How links work

1. HCO Musk starts a local web server on port 8765.
2. Choose a tunnel provider.
3. The selected provider creates a temporary public HTTPS URL.
4. HCO Musk appends the selected surprise mode and copies the link if Termux clipboard support is available.
5. Keep Termux open while the tunnel is running. Press Ctrl+C or choose stop to end it.

### Tunnel provider notes

- **Cloudflare Quick Tunnel:** no account or domain required; generates a temporary `trycloudflare.com` URL. The link stops when the process stops. Intended for development/testing, not production.
- **ngrok:** account and authtoken required. The URL is active while the ngrok process runs.
- **LocalTunnel:** free basic service, requires Node.js/npm. Availability and rate limits may vary.
- **Auto Select:** tries Cloudflare, then LocalTunnel, then ngrok if installed/configured.

No tunnel provider guarantees availability on every network. Some mobile carriers, firewalls, or restricted networks may block tunnels.

## YouTube redirect

At launch the tool displays the support message, counts down 9 to 1, and asks Android to open the HCO YouTube channel.

Android may open the YouTube app or browser depending on app-link settings. Return to Termux and press Enter.

## License

See `LICENSE`. All Rights Reserved. This notice does not technically prevent copying; legal protection and enforcement depend on applicable law.

## Disclaimer

For education and consent-based demonstrations only. Do not use links to deceive, monitor, or collect information from anyone without informed consent.
