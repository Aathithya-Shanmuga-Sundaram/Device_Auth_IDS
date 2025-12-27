import tkinter as tk
import threading
import time
import requests
import pygame
import cv2
import os
import random

# --- CONFIGURATION ---
CORRECT_PASSWORD = "1234" 
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN_HERE" 
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID_HERE"  
SIREN_FILE = "siren.mp3" 
SNAPSHOT_FILE = "intruder.jpg"
MAX_ATTEMPTS = 3
POLL_INTERVAL = 1

def send_telegram_message(text: str):
    url = (
        f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
        f"/sendMessage?chat_id={TELEGRAM_CHAT_ID}&text={text}"
    )
    try:
        requests.get(url, timeout=5)
    except Exception as e:
        print("Error sending Telegram message:", e)


def send_telegram_photo(path: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    try:
        with open(path, "rb") as f:
            files = {"photo": f}
            data = {"chat_id": TELEGRAM_CHAT_ID}
            requests.post(url, files=files, data=data, timeout=10)
    except Exception as e:
        print("Error sending Telegram photo:", e)


def capture_intruder_photo(path: str = SNAPSHOT_FILE):
    try:
        cam = cv2.VideoCapture(0)
        if not cam.isOpened():
            print("Webcam not available. Skipping photo capture.")
            return None
        
        # Warm up camera
        for _ in range(30):
            cam.read() 
        
        ret, frame = cam.read()
        cam.release()
        
        if not ret:
            print("Failed to capture frame")
            return None
            
        cv2.imwrite(path, frame)
        return path
    except Exception as e:
        print("Error capturing intruder photo:", e)
        return None


class AuthApp:
    CHAR_SET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
    FONT_SIZE = 14
    RAIN_SPEED = 25
    DROP_COUNT = 80 

    def __init__(self, root: tk.Tk):
        self.root = root
        
        # --- TIMESTAMP FIX: Record exactly when the app started ---
        self.app_start_time = time.time()
        # ----------------------------------------------------------

        self.root.title("Device Protection Protocol")
        self.root.attributes("-fullscreen", True)
        self.root.attributes("-topmost", True)
        self.root.configure(bg="#111624") 

        self.root.protocol("WM_DELETE_WINDOW", self.safe_exit)
        self.root.bind('<Alt-F4>', self.disallow_alt_f4)
        self.root.bind('<Escape>', self.safe_exit)
        
        self.attempts_left = MAX_ATTEMPTS
        self.locked = False
        self.deactivate_mode = False
        self.siren_playing = False
        self.enhance_protection_active = False

        # --- OTP Variables ---
        self.otp_mode = False
        self.current_otp = None
        # ---------------------

        self.matrix_drops = []
        
        pygame.mixer.init()

        self.build_ui()
        self.setup_matrix_rain()
    
    def disallow_alt_f4(self, event=None):
        self.status_label.configure(text="ACCESS DENIED: Force close is disabled (Alt+F4).", fg="#FF5C5C")
        self.flash_red()
        return "break"
        
    def safe_exit(self, event=None):
        self.root.attributes("-topmost", False)
        self.stop_siren()
        self.stop_fake_popups() 
        self.root.destroy()
            
    def build_ui(self):
        self.bg_frame_top = tk.Frame(self.root, bg="#111624")
        self.bg_frame_top.pack(fill="both", expand=True)

        self.main_card = tk.Frame(
            self.bg_frame_top, bg="#1C2331", padx=40, pady=40,
            highlightbackground="#00F0B8", highlightcolor="#00F0B8", highlightthickness=2, bd=0
        )
        self.main_card.place(
            relx=0.5, rely=0.5, anchor="center", relwidth=0.4, relheight=0.6
        )

        self.title_label = tk.Label(
            self.main_card,
            text="SYSTEM LOCKED",
            font=("Consolas", 36, "bold"),
            bg="#1C2331",
            fg="#00F0B8", 
        )
        self.title_label.pack(pady=(10, 5))

        self.subtitle_label = tk.Label(
            self.main_card,
            text="PROTOCOL ACTIVATED: UNAUTHORIZED ACCESS DETECTED.\nEnter credentials to terminate lockdown.",
            font=("Consolas", 12),
            bg="#1C2331",
            fg="#B0B9C6",
            justify="center",
            wraplength=450
        )
        self.subtitle_label.pack(pady=(0, 25))

        self.attempts_label = tk.Label(
            self.main_card,
            text=f"// ATTEMPTS LEFT: {self.attempts_left} //",
            font=("Consolas", 14),
            bg="#1C2331",
            fg="#708090",
        )
        self.attempts_label.pack(pady=(0, 15))

        self.entry = tk.Entry(
            self.main_card,
            font=("Consolas", 18),
            show="*",
            bd=0,
            bg="#0E1218", 
            fg="#FFFFFF",
            insertbackground="#00F0B8",
            justify="center",
        )
        self.entry.pack(ipady=15, fill="x", padx=10)
        self.entry.focus_set()
        self.entry.bind("<Return>", lambda e: self.check_password())

        self.status_label = tk.Label(
            self.main_card,
            text="",
            font=("Consolas", 12),
            bg="#1C2331",
            fg="#FF5C5C", 
            wraplength=400,
            justify="center",
        )
        self.status_label.pack(pady=(15, 10))

        self.submit_btn = tk.Button(
            self.main_card,
            text="AUTHORIZE",
            font=("Consolas", 14, "bold"),
            width=20,
            command=self.check_password,
            bg="#00A87C", 
            fg="white",
            activebackground="#00805C",
            activeforeground="white",
            relief="flat",
            bd=0,
            cursor="hand2",
        )
        self.submit_btn.pack(pady=(5, 15))
        
        # Custom temporary notification banner
        self.temp_status_label = tk.Label(
            self.root,
            text="",
            font=("Consolas", 16, "bold"),
            bg="#111624",
            fg="#00F0B8",
            height=2,
            relief="flat"
        )
        self.temp_status_label.place(relx=0.5, rely=0.9, anchor="center", relwidth=0.9)
        
        # Global Watermark Label
        self.watermark_label_global = tk.Label(
            self.root,
            text="// Developed by Aathithya Shanmuga Sundaram #MakeEveryoneCyberSafe //",
            font=("Consolas", 8),
            bg="#111624",
            fg="#3A4A5D",
            justify="center",
        )
        self.watermark_label_global.place(relx=0.5, rely=0.97, anchor="center") 


    def setup_matrix_rain(self):
        self.matrix_canvas = tk.Canvas(
            self.root, bg="#111624", highlightthickness=0
        )
        
        for _ in range(self.DROP_COUNT):
            x = random.randrange(0, self.root.winfo_screenwidth(), self.FONT_SIZE)
            y = random.randrange(-300, 0, self.FONT_SIZE)
            speed = random.randint(5, 15)
            self.matrix_drops.append([x, y, speed])

    def flash_red(self):
        self.main_card.configure(highlightbackground="#FF5C5C", highlightcolor="#FF5C5C")
        self.title_label.configure(fg="#FF5C5C")
        self.status_label.configure(fg="#FF5C5C")
        self.root.after(600, self.reset_colors)

    def reset_colors(self):
        if not self.locked:
            self.main_card.configure(highlightbackground="#00F0B8", highlightcolor="#00F0B8")
            self.title_label.configure(fg="#00F0B8")
            self.status_label.configure(fg="#FF5C5C")

    def start_siren(self):
        if self.siren_playing:
            return
        self.siren_playing = True

        def loop_siren():
            try:
                if os.path.exists(SIREN_FILE):
                    pygame.mixer.music.load(SIREN_FILE)
                    pygame.mixer.music.play(-1)
                else:
                    print(f"Siren file not found: {SIREN_FILE}. Skipping alarm.")
            except Exception as e:
                print("Error playing siren:", e)

        threading.Thread(target=loop_siren, daemon=True).start()

    def stop_siren(self):
        if self.siren_playing:
            pygame.mixer.music.stop()
            self.siren_playing = False

    def success_exit(self, message):
        self.temp_status_label.configure(
            text=message, 
            fg="#00F0B8", 
            bg="#0E1218"
        )
        self.root.attributes("-topmost", False)
        # Delay exit to allow message to be seen
        self.root.after(1500, self.safe_exit)

    def remote_immediate_unlock(self):
        self.locked = False
        self.success_exit("OWNER AUTHORIZED: Remote command initiated. Shutting down system...")
        
    def check_password(self):
        entered = self.entry.get()
        self.entry.delete(0, tk.END)

        # --- OTP / PASSWORD LOGIC START ---
        is_correct = False
        if self.otp_mode:
            if entered == self.current_otp:
                is_correct = True
        else:
            if entered == CORRECT_PASSWORD:
                is_correct = True
        # ----------------------------------

        if is_correct:
            self.locked = False
            self.otp_mode = False
            self.success_exit("ACCESS GRANTED: Verified. Protocol terminating...")
            return

        if self.locked:
            self.status_label.configure(text="ACCESS DENIED. SYSTEM IN HARD LOCKDOWN MODE.")
            return

        self.attempts_left -= 1
        self.attempts_label.configure(text=f"// ATTEMPTS LEFT: {self.attempts_left} //")
        
        # Display specific error message
        msg = "INCORRECT OTP." if self.otp_mode else "INCORRECT PASSWORD."
        self.status_label.configure(text=f"{msg} ALERT LEVEL RAISED.", fg="#FF5C5C")
        
        self.flash_red()

        if self.attempts_left <= 0:
            self.trigger_lockdown()

    def trigger_lockdown(self):
        self.locked = True
        self.otp_mode = False # Reset OTP mode on full lockdown
        self.current_otp = None
        self.remove_input()
        
        self.title_label.configure(text="!! INTRUSION ALERT !!", fg="#FF5C5C")
        self.subtitle_label.configure(
            text="LOCKDOWN ACTIVE. INTRUDER PHOTO SENT. OWNER NOTIFIED.",
            fg="#FF5C5C",
        )
        self.status_label.configure(
            text="EMERGENCY PROTOCOL ENGAGED. AWAITING REMOTE INSTRUCTIONS.",
            fg="#FFD700",
        )

        def capture_and_send():
            path = capture_intruder_photo()
            send_telegram_message(f"🚨 INTRUDER ALERT: Max attempts ({MAX_ATTEMPTS}) failed on protected device.")
            
            if path and os.path.exists(path):
                send_telegram_photo(path)
            
            send_telegram_message(
                "Owner Actions:\n"
                "1. 'Deactivate protection' (Generates OTP for unlocking).\n"
                "2. 'Disable password' (Unlocks device IMMEDIATELY).\n"
                "3. 'Start siren' / 'Stop siren'.\n"
                "4. 'Enhance protection' (Matrix visual alert)."
            )

        threading.Thread(target=capture_and_send, daemon=True).start()
        self.start_siren()

    def remove_input(self):
        self.entry.configure(state="disabled")
        self.submit_btn.configure(state="disabled", cursor="arrow", bg="#3A4A5D")

    def restore_input(self):
        self.entry.configure(state="normal")
        self.submit_btn.configure(state="normal", cursor="hand2", bg="#00A87C")
        self.entry.focus_set()
        
        # Adjust message based on mode
        if self.otp_mode:
             self.status_label.configure(text="ENTER TELEGRAM OTP TO UNLOCK.", fg="#00F0B8")
        else:
             self.status_label.configure(text="ONE-TIME ENTRY ACTIVE.", fg="#00F0B8")
             
        self.attempts_left = 1 
        self.attempts_label.configure(text=f"// ATTEMPTS LEFT: {self.attempts_left} //")

    def request_deactivation(self):
        # Generate OTP
        self.current_otp = str(random.randint(100000, 999999))
        self.otp_mode = True
        self.locked = False
        
        self.stop_siren()
        self.stop_fake_popups()
        
        self.title_label.configure(text="OTP VERIFICATION", fg="#00F0B8")
        self.subtitle_label.configure(
            text="SECURITY OVERRIDE INITIATED.\nEnter the 6-digit OTP sent to the owner's Telegram.", 
            fg="#B0B9C6"
        )
        
        self.restore_input()
        
        send_telegram_message(f"⚠️ DEACTIVATION REQUESTED.\n\nYour One-Time Password (OTP) is: {self.current_otp}")
    
    def start_fake_popups(self):
        if not self.locked: 
            send_telegram_message("Cannot start Enhanced Protection: Device is not in lockdown.")
            return
            
        self.enhance_protection_active = True
        
        self.matrix_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        self.main_card.lift()
        
        self.animate_matrix()

    def stop_fake_popups(self):
        self.enhance_protection_active = False
        self.matrix_canvas.place_forget()

    def animate_matrix(self):
        if not self.enhance_protection_active:
            return

        self.matrix_canvas.create_rectangle(0, 0, 
            self.root.winfo_screenwidth(), self.root.winfo_screenheight(), 
            fill="#111624", tags="fade")

        for i, drop in enumerate(self.matrix_drops):
            x = drop[0]
            y = drop[1]
            speed = drop[2]
            
            char = random.choice(self.CHAR_SET)
            self.matrix_canvas.create_text(x, y, text=char, fill="#00FF41", 
                                           font=("Consolas", self.FONT_SIZE, "bold"), anchor="n")
            
            for j in range(1, 10):
                tail_y = y - j * self.FONT_SIZE
                if tail_y > -self.FONT_SIZE:
                    tail_char = random.choice(self.CHAR_SET)
                    intensity = max(0, 255 - j * 25) 
                    color = f'#00{intensity:02x}00'
                    
                    if j > 1:
                         self.matrix_canvas.create_text(x, tail_y, text=tail_char, fill=color, 
                                                        font=("Consolas", self.FONT_SIZE), anchor="n")

            y += speed * 2 
            if y > self.root.winfo_screenheight():
                y = random.randrange(-300, 0, self.FONT_SIZE)
                
            self.matrix_drops[i] = [x, y, speed]

        self.root.after(self.RAIN_SPEED, self.animate_matrix)


def poll_telegram(app: AuthApp, root: tk.Tk):
    last_update_id = None
    base_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getUpdates"

    try:
        target_chat_id = int(TELEGRAM_CHAT_ID) if TELEGRAM_CHAT_ID.isdigit() else TELEGRAM_CHAT_ID
    except ValueError:
        target_chat_id = TELEGRAM_CHAT_ID

    while True:
        try:
            params = {"timeout": 20}
            if last_update_id is not None:
                params["offset"] = last_update_id + 1

            resp = requests.get(base_url, params=params, timeout=25).json()
            
            for update in resp.get("result", []):
                last_update_id = update["update_id"]
                msg = update.get("message") or update.get("edited_message")
                if not msg:
                    continue

                # 1. Ignore Old Messages
                msg_date = msg.get("date", 0)
                if msg_date < app.app_start_time:
                    continue 

                chat_id = msg["chat"]["id"]
                text = msg.get("text", "").strip().lower()

                # 2. Authorization Check
                is_authorized = False
                if isinstance(target_chat_id, int):
                    is_authorized = (chat_id == target_chat_id)
                elif isinstance(target_chat_id, str):
                    is_authorized = (str(chat_id) == target_chat_id)
                
                if not is_authorized:
                    continue

                # --- 3. SECURITY GATEKEEPER: IGNORE IF NOT LOCKED ---
                # This ensures commands only work if there is an active intrusion
                valid_commands = [
                    "deactivate protection", "enhance protection", 
                    "stop enhance protection", "disable password", 
                    "start siren", "stop siren"
                ]
                
                if text in valid_commands and not app.locked:
                    # Optional: Uncomment the next line if you want the bot to reply "Not Locked"
                    # send_telegram_message("⛔ Command Ignored: System is not in lockdown mode.")
                    continue
                # ----------------------------------------------------

                if text == "deactivate protection":
                    root.after(0, app.request_deactivation)

                elif text == "enhance protection":
                    root.after(0, app.start_fake_popups)
                    send_telegram_message("Enhanced Protection: Matrix Code Rain initiated.")

                elif text == "stop enhance protection":
                    root.after(0, app.stop_fake_popups)
                    send_telegram_message("Enhanced Protection stopped.")
                
                elif text == "disable password":
                    root.after(0, app.remote_immediate_unlock)
                    send_telegram_message("Immediate Remote Unlock initiated.")
                    
                elif text == "start siren":
                    root.after(0, app.start_siren)
                    send_telegram_message("Siren activated remotely.")

                elif text == "stop siren":
                    root.after(0, app.stop_siren)
                    send_telegram_message("Siren deactivated remotely.")
                
        except requests.exceptions.Timeout:
            pass
        except Exception as e:
            print("Error in poll_telegram:", e)

        time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    if not os.path.exists(SIREN_FILE):
        print(f"WARNING: The siren sound file '{SIREN_FILE}' was not found.")
        print("Please place a sound file (e.g., siren.mp3) in the same directory.")
        
    root = tk.Tk()
    app = AuthApp(root)

    t = threading.Thread(target=poll_telegram, args=(app, root), daemon=True)
    t.start()
    
    root.mainloop()
