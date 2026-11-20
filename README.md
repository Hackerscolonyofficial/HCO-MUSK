# HCO Musk

**HCO Musk** is a Python + Termux toolkit for Android camera utilities, location utilities, photo organization, and consent-based surprise links.

**Code by Azhar Team HCO**  
**YouTube:** https://youtube.com/@hackers_colony_tech?si=6Uc1vADFNroqTvUP

## Features
- Get the current phone location with Android permission and open it in Google Maps.
- List camera information and capture photos using a selected Termux:API camera ID.
- View and organize JPG/PNG images into date folders.
- Generate shareable location, camera, and custom surprise links.
- Colourful terminal interface, 9-to-1 support countdown, and YouTube redirect.

## Important: links and privacy
The surprise links work across different Wi-Fi/mobile networks **after** the included `web/index.html` is published on a public HTTPS host such as GitHub Pages. A local Termux script alone cannot create a public cross-network link.

The recipient must open the page, press the action button, and grant browser permission. The page cannot secretly activate a camera or read location. It does not upload the recipient's location or camera images; location is displayed in their browser and camera photos are downloaded locally.

Camera/location commands on your own Android phone require the Termux:API Android app, `termux-api` package, and Android permissions. Camera IDs vary by device; check the camera list before choosing front/back IDs.

## Requirements
- Android + Termux + Python 3
- Termux:API Android app installed from the same trusted source as Termux
- `termux-api` package
- Internet for YouTube and hosted share links

## Install in Termux
```bash
pkg update -y && pkg upgrade -y
pkg install python git termux-api -y
```
Install/open the Termux:API Android app separately and grant permissions. Then clone your GitHub repository:
```bash
git clone https://github.com/YOUR-USERNAME/HCO-Musk.git
cd HCO-Musk
chmod +x install.sh
bash install.sh
python hco_musk.py
```
Optional shared storage access:
```bash
termux-setup-storage
```

## Publish surprise links (required)
1. Upload this repository to GitHub with the `main` branch.
2. Open **Settings → Pages** and set **Source** to **GitHub Actions**.
3. The included `.github/workflows/pages.yml` publishes the `web/` folder automatically after a push.
4. Wait for the Pages deployment to finish, then copy the public HTTPS Pages URL shown by GitHub.
5. In HCO Musk choose **Surprise Link Generator → Set/change webpage URL** and paste that URL.
6. Generate a location, camera, or custom link. Anyone with internet can open it on another network.

## Menu
1. Location Tools — current location, Maps, location-request link.
2. Camera Tools — camera info, front/back capture using device camera ID, camera-request link.
3. Media Tools — photo folder and date-based organization.
4. Surprise Link Generator — location, camera, custom link.
5. System Check — check Termux command availability.
6. About HCO Musk.

On each launch, the support message is shown, countdown runs from 9 to 1, and Android is asked to open the HCO YouTube channel. Depending on Android app-link settings, it may open the YouTube app or browser. Return to Termux and press Enter.

## Troubleshooting
- Missing `termux-*` commands: install Termux:API app and run `pkg install termux-api`.
- Permission issue: grant Camera/Location permissions in Android Settings for Termux:API.
- Camera ID error: use Camera Tools → List camera information.
- Link unavailable: check GitHub Pages deployment and ensure the configured URL is public HTTPS.

## License
See `LICENSE` for the HCO Musk All Rights Reserved terms. Public availability does not technically prevent copying; the license states the permissions granted by the copyright holder.

## Disclaimer
For personal device utilities and education. Use camera/location features only on your own device or with informed consent. Do not use links to trick people or collect information without their knowledge.
