# Intrusion Protection System 🔐 

This project is a standalone, full-screen desktop security interface designed to simulate a **device lockdown system**. When unauthorized users attempt to unlock the device, the system triggers alerts, captures photos using the webcam, and sends them to the device owner via Telegram.

---

## Key Features ⭐

### **1. Full-Screen Lockdown UI (Tkinter) 🖥️ (Tkinter)**

* Unclosable full-screen interface
* Disables Alt+F4
* Central password input card with attempts tracking
* System status updates and flashing alert system

### **2. Password Authentication 🔑**

* Default password: `1234`
* Maximum attempts: 3
* After 3 failed attempts → "Intrusion Lockdown" mode

### **3. Telegram Integration 📩**

* Sends alert messages to the owner
* Sends intruder photo captured from webcam
* Supports **remote commands**:

  * `deactivate protection`
  * `disable password`
  * `start siren`
  * `stop siren`
  * `enhance protection`
  * `stop enhance protection`

### **4. Intruder Detection 🚨**

* Captures photo using OpenCV
* Sends snapshot to Telegram
* Plays looping alarm siren (if siren file exists)

### **5. Visual Matrix “Enhanced Protection ⚡” Mode**

* Animates a matrix-code rain overlay
* Activates only in lockdown
* Can be started or stopped remotely

### **6. Remote-Assisted Recovery 🔄**

* Owner can restore 1-time password entry
* Owner can instantly unlock and close program remotely

---

## Requirements 📦

### **Python Packages**

```
pip install -r requirements.txt
```

### **Other Files Needed**

* `siren.mp3` — alarm sound file

---

## How to Use ▶️

### **1. Configure Credentials**

Edit these values in the script:

```python
CORRECT_PASSWORD = "1234"
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN"
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID"
```

### **2. Run the App**

```
python main.py
```

The window locks the screen immediately.

### **3. Failed Attempts → Lockdown Mode**

After 3 wrong password entries:

* Siren plays
* Photo captured
* Messages sent to Telegram
* Input disabled

### **4. Use Remote Commands (Telegram)**

Send commands from your authorized Telegram account:

* `deactivate protection` – restore 1 password attempt
* `disable password` – instantly unlock and close app
* `start siren` – manually trigger alarm
* `stop siren` – stop alarm
* `enhance protection` – matrix animation
* `stop enhance protection` – stop animation

---

## File Structure 📁

```
project/
│-- main.py
│-- siren.mp3
│-- intruder.jpg (created automatically)
│-- README.md
```

---

## Notes 📝

* For real security, replace the hardcoded password
* Tkinter full-screen lock is **not OS-level secure**
* Ensure webcam permissions are allowed

---

## License 📄

This project is for educational and demonstration purposes only.
