
#!/usr/bin/env python3
# HCO Musk v1.1.0
# Copyright (c) 2026 HCO Team Azhar.

import os, sys, json, time, re, shutil, subprocess, threading
import urllib.parse, urllib.request, socket
from pathlib import Path
from datetime import datetime
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from functools import partial

GREEN="\033[92m"
CYAN="\033[96m"
YELLOW="\033[93m"
RED="\033[91m"
MAGENTA="\033[95m"
WHITE="\033[97m"
BOLD="\033[1m"
RESET="\033[0m"

ROOT=Path(__file__).resolve().parent
WEB=ROOT/"web"
CFG=ROOT/"config.json"
YT="https://youtube.com/@hackers_colony_tech?si=6Uc1vADFNroqTvUP"

DEFAULT={
    "youtube_url":YT,
    "photo_folder":str(Path.home()/"storage/dcim/HCO-Musk"),
    "port":8765
}

try:
    CONFIG={**DEFAULT,**json.loads(CFG.read_text(encoding="utf-8"))}
except Exception:
    CONFIG=DEFAULT.copy()


def save_config():
    CFG.write_text(json.dumps(CONFIG,indent=2),encoding="utf-8")


def clear():
    os.system("clear")


def pause():
    input(f"\n{CYAN}Press Enter to continue...{RESET}")


def banner():
    clear()
    print(GREEN+BOLD+r"""
 _   _  ____ ___  __  __ _   _ ____  _  __
| | | |/ ___/ _ \|  \/  | | | / ___|| |/ /
| |_| | |  | | | | |\/| | | | \___ \| ' /
|  _  | |__| |_| | |  | | |_| |___) | . \
|_| |_|\____\___/|_|  |_|\___/|____/|_|\_\
""" + RESET)

    print(CYAN+BOLD+"                  by HCO Team Azhar"+RESET)
    print(YELLOW+"        Consent-based Surprise Link Toolkit"+RESET+"\n")


def support_page():
    clear()

    print(GREEN+BOLD+"             THIS IS A SUPPORT PAGE"+RESET+"\n")
    print("Now Termux will redirect to our YouTube channel.")
    print("Please like, subscribe and click on the bell 🔔")
    print("Then come back to Termux to run the tool.\n")

    for n in range(9,0,-1):
        print(f"\r{CYAN}{BOLD}{n}...{RESET}",end="",flush=True)
        time.sleep(1)

    print(f"\r{GREEN}Opening YouTube...{RESET}       ")

    if shutil.which("termux-open-url"):
        try:
            subprocess.Popen(["termux-open-url",YT])
        except Exception:
            print(YT)
    else:
        print("Open:",YT)

    input(f"\n{YELLOW}Welcome back! Press Enter to run HCO Musk.{RESET}")


def local_ip():
    s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

    try:
        s.connect(("1.1.1.1",80))
        ip=s.getsockname()[0]
    except Exception:
        ip="127.0.0.1"
    finally:
        s.close()

    return ip


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self,fmt,*args):
        pass


class LinkServer:

    def __init__(self,port):
        handler=partial(QuietHandler,directory=str(WEB))
        self.httpd=ThreadingHTTPServer(("127.0.0.1",port),handler)
        self.thread=threading.Thread(
            target=self.httpd.serve_forever,
            daemon=True
        )

    def start(self):
        self.thread.start()

    def stop(self):
        self.httpd.shutdown()
        self.httpd.server_close()


def url_for(base,mode,title,message=""):
    q={"mode":mode,"title":title}

    if message:
        q["message"]=message

    return base.rstrip("/")+"/?"+urllib.parse.urlencode(q)


def copy_link(url):
    if shutil.which("termux-clipboard-set"):
        try:
            p=subprocess.run(
                ["termux-clipboard-set",url],
                capture_output=True,
                timeout=8
            )

            if p.returncode==0:
                print(GREEN+"Link copied to clipboard."+RESET)

        except Exception:
            pass


def open_link(url):
    if shutil.which("termux-open-url"):
        try:
            subprocess.Popen(["termux-open-url",url])
            return
        except Exception:
            pass

    print("Preview URL:",url)


def start_tunnel(provider,port):

    if provider=="cloudflare":

        if not shutil.which("cloudflared"):
            print(RED+"cloudflared not installed. Try: pkg install cloudflared -y"+RESET)
            return None

        command=[
            "cloudflared",
            "tunnel",
            "--url",
            f"http://127.0.0.1:{port}",
            "--no-autoupdate"
        ]

    elif provider=="ngrok":

        if not shutil.which("ngrok"):
            print(RED+"ngrok not installed. Install the official ngrok agent first."+RESET)
            return None

        command=["ngrok","http",str(port),"--log","stdout"]

    elif provider=="localtunnel":

        if not shutil.which("lt"):
            print(RED+"LocalTunnel CLI not installed. Run: npm install -g localtunnel"+RESET)
            return None

        command=["lt","--port",str(port)]

    else:
        return None

    print(YELLOW+f"Starting {provider} tunnel..."+RESET)

    try:
        proc=subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
    except Exception as e:
        print(RED+f"Could not start tunnel: {e}"+RESET)
        return None

    lines=[]

    def reader():
        try:
            for line in proc.stdout:
                lines.append(line.rstrip())

                if len(lines)>100:
                    del lines[:30]

        except Exception:
            pass

    threading.Thread(target=reader,daemon=True).start()

    found=None
    deadline=time.time()+35

    while time.time()<deadline and proc.poll() is None:

        text="\n".join(lines)

        if provider=="cloudflare":

            m=re.search(
                r"https://[a-zA-Z0-9-]+\.trycloudflare\.com",
                text
            )

            if m:
                found=m.group(0)

        elif provider=="localtunnel":

            m=re.search(
                r"https://[a-zA-Z0-9.-]+\.loca\.lt",
                text
            )

            if m:
                found=m.group(0)

            if not found:
                m=re.search(
                    r"https://[a-zA-Z0-9.-]+\.localtunnel\.me",
                    text
                )

                if m:
                    found=m.group(0)

        elif provider=="ngrok":

            try:
                with urllib.request.urlopen(
                    "http://127.0.0.1:4040/api/tunnels",
                    timeout=1
                ) as r:

                    data=json.loads(r.read().decode())

                for tunnel in data.get("tunnels",[]):

                    if tunnel.get("public_url","").startswith("https://"):
                        found=tunnel["public_url"]
                        break

            except Exception:
                pass

        if found:
            return proc,found

        time.sleep(.5)

    print(RED+"Could not detect a public URL. Provider output:"+RESET)
    print("\n".join(lines[-12:]) or "No output received.")

    try:
        proc.terminate()
    except Exception:
        pass

    return None


def tunnel_menu():

    print(f"\n{MAGENTA}{BOLD}LINK SERVER MANAGER{RESET}")
    print("1. Cloudflare Quick Tunnel (no account; temporary)")
    print("2. ngrok (account + authtoken required)")
    print("3. LocalTunnel (Node.js/npm required)")
    print("4. Auto Select (Cloudflare → LocalTunnel → ngrok)")
    print("0. Back")

    c=input(f"\n{GREEN}HCO Musk > {RESET}").strip()

    return {
        "1":"cloudflare",
        "2":"ngrok",
        "3":"localtunnel",
        "4":"auto"
    }.get(c)


def generate_link(mode):

    if not WEB.joinpath("index.html").exists():
        print(RED+"Missing web/index.html. Restore the web folder from the repository."+RESET)
        return

    title=input(
        "Surprise title [A Surprise for You]: "
    ).strip() or "A Surprise for You"

    message=""

    if mode=="custom":
        message=input("Your surprise message: ").strip() or "There is a surprise waiting for you!"

    try:
        port=int(CONFIG.get("port",8765))
    except Exception:
        port=8765

    server=None
    tunnel_proc=None
    public=None

    try:
        server=LinkServer(port)
        server.start()

    except OSError:
        print(RED+f"Could not start local web server on port {port}. Is another HCO Musk session running?"+RESET)
        return

    print(f"{GREEN}Local page started at http://127.0.0.1:{port}{RESET}")
    print("\nChoose a public link provider:")

    provider=tunnel_menu()

    if provider is None:
        server.stop()
        return

    providers=(
        ["cloudflare","localtunnel","ngrok"]
        if provider=="auto"
        else [provider]
    )

    for p in providers:

        result=start_tunnel(p,port)

        if result:
            tunnel_proc,public=result
            break

    if not public:
        server.stop()
        print(YELLOW+"No tunnel started. Install/configure a provider and try again."+RESET)
        return

    share=url_for(public,mode,title,message)

    print(f"\n{GREEN}{BOLD}YOUR SURPRISE LINK IS READY!{RESET}")
    print(CYAN+share+RESET)

    print(
        YELLOW+
        "Share only with people who expect this link. The tunnel is public while running."
        +RESET
    )

    copy_link(share)

    print("\n1. Preview in browser")
    print("2. Keep link server running (press Ctrl+C to stop)")
    print("0. Stop and return")

    action=input(f"{GREEN}Choose: {RESET}").strip()

    if action=="1":
        open_link(share)

    if action=="2":

        print(
            YELLOW+
            "Server/tunnel running. Keep Termux open; press Ctrl+C to stop."
            +RESET
        )

        try:
            while tunnel_proc.poll() is None:
                time.sleep(1)
        except KeyboardInterrupt:
            pass

    try:
        if tunnel_proc and tunnel_proc.poll() is None:
            tunnel_proc.terminate()
    except Exception:
        pass

    server.stop()

    print(GREEN+"Local server and tunnel stopped."+RESET)


def surprise_menu():

    while True:

        print(f"\n{MAGENTA}{BOLD}SURPRISE LINK GENERATOR{RESET}")
        print("1. Custom Surprise Message")
        print("2. Location Sharing Link")
        print("3. Camera Preview Link")
        print("4. Photo Surprise Page")
        print("5. Create My Own Surprise")
        print("0. Back")

        c=input(f"\n{GREEN}HCO Musk > {RESET}").strip()

        modes={
            "1":"custom",
            "2":"location",
            "3":"camera",
            "4":"photo",
            "5":"custom"
        }

        if c=="0":
            return

        if c in modes:
            generate_link(modes[c])
        else:
            print(RED+"Invalid option."+RESET)

        pause()


def camera_menu():

    while True:

        print(f"\n{MAGENTA}{BOLD}CAMERA TOOLS{RESET}")
        print("1. Generate Front Camera Preview Link")
        print("2. Generate Rear Camera Preview Link")
        print("3. Camera Permission & Compatibility Guide")
        print("0. Back")

        c=input(f"\n{GREEN}HCO Musk > {RESET}").strip()

        if c=="0":
            return

        if c=="1":
            generate_link("camera-front")

        elif c=="2":
            generate_link("camera-rear")

        elif c=="3":
            print("The recipient's browser asks for camera permission after they press Start Camera.")
            print("Camera preview stays in their browser; HCO Musk does not upload or record it.")

        else:
            print(RED+"Invalid option."+RESET)

        pause()


def location_menu():

    while True:

        print(f"\n{MAGENTA}{BOLD}LOCATION TOOLS{RESET}")
        print("1. Generate Location Sharing Link")
        print("2. Generate Map Surprise Link")
        print("3. Location Permission Information")
        print("0. Back")

        c=input(f"\n{GREEN}HCO Musk > {RESET}").strip()

        if c=="0":
            return

        if c=="1":
            generate_link("location")

        elif c=="2":
            generate_link("location-map")

        elif c=="3":
            print("The recipient sees a clear location-sharing explanation.")
            print("Their browser requests location only after they press Share My Location.")
            print("The coordinates are shown to them in their browser; HCO Musk does not receive them.")

        else:
            print(RED+"Invalid option."+RESET)

        pause()


def media_menu():

    while True:

        print(f"\n{MAGENTA}{BOLD}MEDIA TOOLS{RESET}")
        print("1. Generate Photo Surprise Page")
        print("2. Open local HCO photo folder")
        print("0. Back")

        c=input(f"\n{GREEN}HCO Musk > {RESET}").strip()

        if c=="0":
            return

        if c=="1":
            generate_link("photo")

        elif c=="2":

            folder=Path(CONFIG["photo_folder"]).expanduser()
            folder.mkdir(parents=True,exist_ok=True)

            print("Photo folder:",folder)

            for p in sorted(folder.iterdir()):
                print(p.name)

        else:
            print(RED+"Invalid option."+RESET)

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

        status=(
            GREEN+"AVAILABLE"+RESET
            if shutil.which(name)
            else YELLOW+"NOT INSTALLED"+RESET
        )

        print(f"{name:<22}{status}")

    print("\nCloudflare Quick Tunnel is temporary and stops when its process exits.")
    print("ngrok requires an account and configured authtoken.")
    print("LocalTunnel requires Node.js/npm.")

    pause()


def main():

    support_page()

    while True:

        banner()

        print(WHITE+BOLD+"MAIN MENU"+RESET)

        print(GREEN+"01."+RESET+" Surprise Link Generator")
        print(GREEN+"02."+RESET+" Camera Tools")
        print(GREEN+"03."+RESET+" Location Tools")
        print(GREEN+"04."+RESET+" Media Tools")
        print(GREEN+"05."+RESET+" Link Server Manager")
        print(GREEN+"06."+RESET+" System Check")
        print(GREEN+"07."+RESET+" About HCO Musk")
        print(RED+"00."+RESET+" Exit")

        c=input(
            f"\n{CYAN}{BOLD}HCO Musk @ Termux > {RESET}"
        ).strip().lower()

        if c in ("1","01"):
            surprise_menu()

        elif c in ("2","02"):
            camera_menu()

        elif c in ("3","03"):
            location_menu()

        elif c in ("4","04"):
            media_menu()

        elif c in ("5","05"):
            print("Select a tunnel provider when generating a surprise link.")
            system_check()

        elif c in ("6","06"):
            system_check()

        elif c in ("7","07"):
            print(GREEN+"HCO Musk v1.1.0 — Code by Azhar Team HCO"+RESET)
            print(YT)
            pause()

        elif c in ("0","00","q","exit"):
            print(GREEN+"Thanks for using HCO Musk!"+RESET)
            break

        else:
            print(RED+"Invalid option."+RESET)
            time.sleep(.7)


if __name__=="__main__":

    try:
        main()

    except KeyboardInterrupt:
        print("\nStopped by user.")
        sys.exit(0)
