
# Booking_unimelb 🪑🎓

This Python script allows you to automatically:

✅ Book your desk for the next two weeks  
✅ Check in to your desk if you’ve already booked it  

---

## ⚙️ Requirements

1. Install **Python 3**
2. Install **Selenium**:

```bash
pip install selenium webdriver-manager
````

---

## ✏️ Configuration

Before running, open the Python file and change these values:

```python
USERNAME = "your_username"
PASSWORD = "your_password"
DESK_NUM = "your desk number e.g. 5.047"
TARGET_WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
```

---

## ⏰ Automate with macOS Launch Agent (run daily at 10:00 AM)

### 🥽 Step 1: Create the `.plist` File

Open Terminal:

```bash
cd ~/Library/LaunchAgents
nano com.unimelb.bot.plist
```

### 📝 Step 2: Paste the Following (update paths!)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
    "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.unimelb.bot</string>

    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/YOURNAME/Documents/booking_unimelb.py</string>
    </array>

    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>10</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>

    <key>StandardOutPath</key>
    <string>/tmp/bookingbot.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/bookingbot.err</string>

    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
```

🔁 Replace:

* `/Users/YOURNAME/...` with the **full path to your `.py` script**
* `/usr/bin/python3` with the output of:

```bash
which python3
```

---

### 💾 Step 3: Save and Exit

In `nano`, press:

* `Ctrl + O` → Enter (to save)
* `Ctrl + X` (to exit)

---

### ▶️ Step 4: Load the Agent

```bash
launchctl load ~/Library/LaunchAgents/com.unimelb.bot.plist
```

🎉 Your script will now run automatically **every day at 10:00 AM**!

---

## 🛠 Maintenance

To **unload or reload** the agent:

```bash
# Unload (disable)
launchctl unload ~/Library/LaunchAgents/com.unimelb.bot.plist

# Edit
nano ~/Library/LaunchAgents/com.unimelb.bot.plist

# Reload after editing
launchctl load ~/Library/LaunchAgents/com.unimelb.bot.plist
```

---
