import tkinter as tk
from tkinter import messagebox
import imaplib
import email
import re
import time
import webbrowser
import pyautogui
import psutil
from datetime import datetime
import cv2
import numpy as np
from PIL import ImageGrab

# Your email credentials and join button image path
EMAIL = "ajaybabupadamatiaj@gmail.com"
PASSWORD = "vxrnbehdxwevygbs"
JOIN_NOW_IMAGE_PATH = "C:/Ajay personal/pyauto/join_now_button.png"

def fetch_zoho_webinar_link():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔍 Checking email...")
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    try:
        imap.login(EMAIL, PASSWORD)
    except imaplib.IMAP4.error as e:
        print("❌ Login failed:", e)
        return None

    imap.select("inbox")
    status, messages = imap.search(None, 'FROM "noreply@mailer.zohowebinar.in" SUBJECT "Reminder to join - APSCHE"')
    mail_ids = messages[0].split()

    if not mail_ids:
        print("❌ No Zoho emails found.")
        imap.logout()
        return None

    latest_id = mail_ids[-1]
    res, msg = imap.fetch(latest_id, "(RFC822)")
    for response in msg:
        if isinstance(response, tuple):
            msg = email.message_from_bytes(response[1])
            html = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/html":
                        html = part.get_payload(decode=True).decode()
                        break
            else:
                html = msg.get_payload(decode=True).decode()

            match = re.search(r'https://[^\s"]*zoho[^\s"]*', html)
            if match:
                imap.logout()
                print("✅ Webinar link found:", match.group(0))
                return match.group(0)

    imap.logout()
    return None

def scan_and_open_qr_code(timeout=30):
    print("🔍 Scanning for QR code...")
    cap_time = time.time()
    detector = cv2.QRCodeDetector()

    while time.time() - cap_time < timeout:
        screen = ImageGrab.grab()
        frame = np.array(screen)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        data, bbox, _ = detector.detectAndDecode(frame)
        if data:
            print(f"✅ QR Code Detected: {data}")
            webbrowser.open(data)
            return

        time.sleep(1)

    print("❌ No QR code detected in allotted time.")

def open_webinar():
    webinar_url = fetch_zoho_webinar_link()
    if not webinar_url:
        messagebox.showerror("Error", "Webinar link not found.")
        return

    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🚀 Opening webinar...")
    webbrowser.open(webinar_url)
    time.sleep(12)

    try:
        print("🔍 Looking for 'Join Now' button...")
        location = pyautogui.locateOnScreen(JOIN_NOW_IMAGE_PATH, confidence=0.8)
        if location:
            pyautogui.click(pyautogui.center(location))
            print("✅ Clicked 'Join Now'")
            time.sleep(10)
            scan_and_open_qr_code()
        else:
            print("❌ 'Join Now' button not found.")
            pyautogui.screenshot("screen_debug.png")
            print("📸 Screenshot saved.")
    except Exception as e:
        print("⚠️ Error:", e)

    messagebox.showinfo("Done", "Webinar operation completed.")

# -------------------------------
# GUI Code
# -------------------------------
def launch_gui():
    root = tk.Tk()
    root.title("Webinar App")
    root.geometry("300x200")
    root.resizable(False, False)

    title = tk.Label(root, text="📡 Webinar App", font=("Helvetica", 16))
    title.pack(pady=20)

    activate_btn = tk.Button(root, text="Activate", font=("Helvetica", 14), command=open_webinar)
    activate_btn.pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    launch_gui()
