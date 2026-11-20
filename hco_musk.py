#!/usr/bin/env python3
# HCO Musk | Copyright (c) 2026 HCO Team Azhar. All rights reserved.
import os, sys, json, time, shutil, subprocess, urllib.parse, webbrowser
from pathlib import Path
from datetime import datetime

G="\033[92m"; C="\033[96m"; Y="\033[93m"; R="\033[91m"; M="\033[95m"; W="\033[97m"; B="\033[1m"; X="\033[0m"
HOME=Path(__file__).resolve().parent
CFG=HOME/"config.json"
YT="https://youtube.com/@hackers_colony_tech?si=6Uc1vADFNroqTvUP"
DEFAULT={"share_page_url":"","photo_folder":str(Path.home()/"storage/dcim/HCO-Musk"),"youtube_url":YT}
try: config={**DEFAULT,**json.loads(CFG.read_text())}
except Exception: config=DEFAULT.copy()

def save(): CFG.write_text(json.dumps(config,indent=2))
def cmd(args,timeout=30):
    try: return subprocess.run(args,text=True,capture_output=True,timeout=timeout)
    except FileNotFoundError: print(f"{R}Missing command: {args[0]}{X}")
    except Exception as e: print(f"{R}{e}{X}")
    return None
def pause(): input(f"\n{C}Press Enter to continue...{X}")
def openurl(url):
    if shutil.which("termux-open-url"):
        p=cmd(["termux-open-url",url],15)
        if p and p.returncode==0: return
    print(f"{Y}Open manually: {url}{X}")
    try: webbrowser.open(url)
    except Exception: pass

def support():
    os.system("clear")
    print(f"{G}{B}             THIS IS A SUPPORT PAGE{X}\n")
    print("Now Termux will redirect to our YouTube channel.")
    print("Please like, subscribe and click on the bell 🔔")
    print("Then come back to Termux to run the tool.\n")
    for n in range(9,0,-1):
        print(f"\r{C}{B}{n}...{X}",end="",flush=True); time.sleep(1)
    print(f"\r{G}Opening YouTube...{X}       ")
    openurl(config["youtube_url"])
    input(f"\n{Y}Welcome back! Press Enter to run HCO Musk.{X}")

def banner():
    os.system("clear")
    print(G+B+r"""
 _   _  ____ ___  __  __ _   _ ____  _  __
| | | |/ ___/ _ \|  \/  | | | / ___|| |/ /
| |_| | |  | | | | |\/| | | | \___ \| ' /
|  _  | |__| |_| | |  | | |_| |___) | . \
|_| |_|\____\___/|_|  |_|\___/|____/|_|\_\
""" + X)
    print(f"{C}{B}                  by HCO Team Azhar{X}")
    print(f"{Y}        Camera • Location • Media • Surprise Links{X}\n")

def need_api():
    if not shutil.which("termux-location") and not shutil.which("termux-camera-photo"):
        print(f"{R}Termux:API commands missing. Install Termux:API app, then run: pkg install termux-api{X}")
        return False
    return True

def location():
    if not shutil.which("termux-location"):
        print(f"{R}Run: pkg install termux-api and install the Termux:API Android app.{X}"); return
    print(f"{Y}Waiting for Android location permission...{X}")
    p=cmd(["termux-location","-p","gps","-r","once"],60)
    if not p or p.returncode: print(f"{R}Location unavailable. Check GPS and app permission.{X}"); return
    try:
        d=json.loads(p.stdout); lat=float(d["latitude"]); lon=float(d["longitude"])
        print(f"{G}Latitude: {lat}\nLongitude: {lon}{X}")
        print("Accuracy:",d.get("accuracy","not reported"),"m")
        url=f"https://www.google.com/maps?q={lat},{lon}"
        print("Maps:",url)
        return lat,lon
    except Exception: print(f"{R}Could not parse location response.{X}")

def share_base():
    url=config.get("share_page_url","").strip()
    if not url:
        print(f"{Y}Publish web/index.html with GitHub Pages first.{X}")
        url=input("Paste your public GitHub Pages HTTPS URL: ").strip()
        if url: config["share_page_url"]=url.rstrip("/")+"/"; save()
    if not url.startswith("https://"):
        print(f"{R}A public HTTPS webpage URL is required for cross-network links.{X}"); return ""
    return url.rstrip("/")+"/"

def make_link(mode):
    base=share_base()
    if not base: return
    title=input("Surprise title (Enter for default): ").strip() or {"location":"Location Surprise","camera":"Camera Surprise","custom":"A Little Surprise"}[mode]
    msg=input("Optional message: ").strip() if mode=="custom" else ""
    params={"mode":mode,"title":title}
    if msg: params["message"]=msg
    link=base+"?"+urllib.parse.urlencode(params)
    print(f"\n{G}{B}SURPRISE LINK READY!{X}\n{C}{link}{X}")
    print("Recipient must open it and personally approve browser permissions.")
    print("The included page does not upload their location or camera images.")
    if shutil.which("termux-clipboard-set"): cmd(["termux-clipboard-set",link])
    print("1. Preview link\n0. Back")
    if input("Select: ").strip()=="1": openurl(link)

def loc_menu():
    while True:
        print(f"\n{M}{B}LOCATION TOOLS{X}\n1. Get my location\n2. Open my location in Maps\n3. Create location surprise link\n0. Back")
        c=input(f"{G}HCO Musk > {X}").strip()
        if c=="0": return
        if c=="1": location()
        elif c=="2":
            got=location()
            if got: openurl(f"https://www.google.com/maps?q={got[0]},{got[1]}")
        elif c=="3": make_link("location")
        else: print(f"{R}Invalid option{X}")
        pause()

def camera_menu():
    while True:
        print(f"\n{M}{B}CAMERA TOOLS{X}\n1. List camera information\n2. Capture front camera\n3. Capture back camera\n4. Create camera surprise link\n0. Back")
        c=input(f"{G}HCO Musk > {X}").strip()
        if c=="0": return
        if c=="1":
            p=cmd(["termux-camera-info"])
            if p: print(p.stdout or p.stderr)
        elif c in ("2","3"):
            if not shutil.which("termux-camera-photo"):
                print(f"{R}Install Termux:API app and run pkg install termux-api{X}")
            else:
                print("Camera IDs vary by device. Check option 1. Common defaults: front=1, back=0.")
                cam=input("Enter camera ID: ").strip()
                if not cam: cam="1" if c=="2" else "0"
                if not cam.isdigit(): print(f"{R}Camera ID must be numeric.{X}")
                else:
                    folder=Path(config["photo_folder"]).expanduser(); folder.mkdir(parents=True,exist_ok=True)
                    kind="front" if c=="2" else "back"
                    target=folder/f"HCO_Musk_{kind}_{datetime.now():%Y%m%d_%H%M%S}.jpg"
                    print("Android may ask for camera permission.")
                    p=cmd(["termux-camera-photo","-c",cam,str(target)],60)
                    if p and p.returncode==0 and target.exists(): print(f"{G}Saved: {target}{X}")
                    else: print(f"{R}Capture failed. Check ID and permissions.{X}")
        elif c=="4": make_link("camera")
        else: print(f"{R}Invalid option{X}")
        pause()

def media_menu():
    while True:
        folder=Path(config["photo_folder"]).expanduser()
        print(f"\n{M}{B}MEDIA TOOLS{X}\n1. Show photo folder\n2. Organize loose JPG/PNG into date folders\n3. Change photo folder\n0. Back")
        c=input(f"{G}HCO Musk > {X}").strip()
        if c=="0": return
        folder.mkdir(parents=True,exist_ok=True)
        if c=="1":
            print(folder)
            for f in sorted(folder.iterdir()): print(("DIR " if f.is_dir() else "FILE")+f" {f.name}")
        elif c=="2":
            files=[f for f in folder.iterdir() if f.is_file() and f.suffix.lower() in (".jpg",".jpeg",".png")]
            for f in files:
                dest=folder/datetime.fromtimestamp(f.stat().st_mtime).strftime("%Y-%m-%d"); dest.mkdir(exist_ok=True)
                target=dest/f.name
                if target.exists(): target=dest/f"{f.stem}_{int(time.time())}{f.suffix}"
                shutil.move(str(f),str(target))
            print(f"{G}Organized {len(files)} image(s).{X}")
        elif c=="3":
            p=input("New full folder path: ").strip()
            if p: config["photo_folder"]=str(Path(p).expanduser()); save()
        else: print(f"{R}Invalid option{X}")
        pause()

def link_menu():
    while True:
        print(f"\n{M}{B}SURPRISE LINK GENERATOR{X}\n1. Location surprise link\n2. Camera surprise link\n3. Custom surprise link\n4. Set/change published webpage URL\n0. Back")
        c=input(f"{G}HCO Musk > {X}").strip()
        if c=="0": return
        if c=="1": make_link("location")
        elif c=="2": make_link("camera")
        elif c=="3": make_link("custom")
        elif c=="4": config["share_page_url"]=""; share_base()
        else: print(f"{R}Invalid option{X}")
        pause()

def main():
    support()
    while True:
        banner()
        print(f"{W}{B}MAIN MENU{X}")
        print(f"{G}01.{X} Location Tools\n{G}02.{X} Camera Tools\n{G}03.{X} Media Tools\n{G}04.{X} Surprise Link Generator\n{G}05.{X} System Check\n{G}06.{X} About HCO Musk\n{R}00.{X} Exit")
        c=input(f"\n{C}{B}HCO Musk @ Termux > {X}").strip().lower()
        if c in ("1","01"): loc_menu()
        elif c in ("2","02"): camera_menu()
        elif c in ("3","03"): media_menu()
        elif c in ("4","04"): link_menu()
        elif c in ("5","05"):
            for x in ("termux-location","termux-camera-info","termux-camera-photo","termux-open-url","termux-clipboard-set"):
                print(f"{x:<25}{G+'AVAILABLE'+X if shutil.which(x) else Y+'NOT FOUND'+X}")
            print("Share page:",config["share_page_url"] or "not configured"); pause()
        elif c in ("6","06"):
            print(f"{G}HCO Musk v1.0.0 — Code by Azhar Team HCO{X}\n{YT}"); pause()
        elif c in ("0","00","q","exit"): print(f"{G}Thanks for using HCO Musk!{X}"); break
        else: print(f"{R}Invalid option.{X}"); time.sleep(.7)

if __name__=="__main__":
    try: main()
    except KeyboardInterrupt: print(f"\n{Y}Stopped by user.{X}"); sys.exit(0)
