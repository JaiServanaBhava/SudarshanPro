---

## 🏗 Tech Stack

| Layer | Technologies |
| :--- | :--- |
| **Engine** | Python 3, Waitress WSGI |
| **Automation** | PyAutoGUI, Psutil, Subprocess |
| **Interface** | HTML5, CSS3 (Glassmorphism), Jinja2 |
| **Connectivity** | mDNS (Zeroconf), Socket, QR Code |
| **Multimedia** | OpenCV, PIL (Pillow), PyAudio, PyTTSx3 |

---

<div align="center">
  <p><b>Developed by <a href="https://github.com/JaiServanaBhava">Jai Servana Bhava</a></b></p>
  <p><i>Empowering remote management through elegant code.</i></p>
Here is the updated, high-impact `README.md` code. I've restructured it to look like a top-tier professional software project, emphasizing the "Why Sudarshan Pro" factor and making the features look more compelling to potential users.
```html
<div align="center">
  <img src="[https://github.com/JaiServanaBhava/SudarshanPro/blob/main/icon.png](https://github.com/JaiServanaBhava/SudarshanPro/blob/main/icon.png)" alt="Sudarshan Pro Logo" width="160">
  <h1>Sudarshan Pro</h1>
  <p align="center">
    <b>The Ultimate Zero-Config Remote PC Control & Surveillance Suite</b>
    <br />
    <i>Control your world from your pocket. Fast. Secure. Professional.</i>
  </p>

  <p align="center">
    <img src="[https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python&logoColor=white](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python&logoColor=white)" alt="Python">
    <img src="[https://img.shields.io/badge/Framework-Flask-black?style=for-the-badge&logo=flask](https://img.shields.io/badge/Framework-Flask-black?style=for-the-badge&logo=flask)" alt="Flask">
    <img src="[https://img.shields.io/badge/Architecture-Async_Threaded-orange?style=for-the-badge](https://img.shields.io/badge/Architecture-Async_Threaded-orange?style=for-the-badge)" alt="Async">
    <img src="[https://img.shields.io/badge/UI-Glassmorphism-brightgreen?style=for-the-badge](https://img.shields.io/badge/UI-Glassmorphism-brightgreen?style=for-the-badge)" alt="UI">
  </p>

  <h4>
    <a href="#-key-advantages">Advantages</a> •
    <a href="#-feature-suite">Features</a> •
    <a href="#-installation">Installation</a> •
    <a href="#-tech-stack">Tech Stack</a>
  </h4>
</div>

---

## 🌟 Why Sudarshan Pro?

Most remote desktop tools are heavy, laggy, or require complex port forwarding. **Sudarshan Pro** is built for speed and simplicity. Whether you need to monitor your system, transfer files instantly, or control your media from across the room, it offers a professional-grade experience in a lightweight package.

### 💎 Key Advantages
*   **Zero Setup:** No mobile app required. Just scan the auto-generated QR code.
*   **Ultra Lightweight:** Consumes minimal RAM and CPU while running in the background.[cite: 2]
*   **Privacy First:** All data stays on your local network. No third-party servers.
*   **Bi-Directional Control:** Not just a remote mouse—it's a full-system bridge.[cite: 2]
*   **Portable:** Run it anywhere as a single `.exe` without installing Python.[cite: 2]

---

## 🛠 Feature Suite

### 📱 HID & System Control
*   **Smart Mouse & Keyboard:** Precision movement, scrolling, and remote typing.[cite: 2]
*   **Instant Shortcuts:** One-tap Alt-Tab, Task Manager, and Window Minimizing.[cite: 2]
*   **Media Center:** Control Spotify, YouTube, and VLC volume or playback.[cite: 2]

### 📸 Pro Surveillance
*   **Live View:** Stream your desktop frame-by-frame directly to your phone.[cite: 2]
*   **Webcam Capture:** Snap high-quality photos using OpenCV or native Windows drivers.[cite: 2]
*   **Screen Snaps:** Save full-resolution screenshots directly to the DropZone.[cite: 2]

### 📁 Advanced Data Management
*   **DropZone:** A professional file-sharing hub on your Desktop for instant drag-and-drop transfers.[cite: 2]
*   **Clipboard Bridge:** Copy text on your phone and paste it instantly on your PC (and vice versa).[cite: 2]
*   **Process Manager:** Real-time CPU/RAM monitoring and a remote "Kill" switch for frozen apps.[cite: 2]

### 🎙️ Voice & Automation
*   **Remote TTS:** Make your PC talk using a dedicated text-to-speech engine.[cite: 2]
*   **Audio Recording:** Record environmental audio and download the `.wav` file remotely.[cite: 2]
*   **Terminal Access:** Execute CMD/PowerShell commands directly from the web UI.[cite: 2]

---

## 📸 Screenshots

<div align="center">
  <img src="https://via.placeholder.com/600x350?text=Sudarshan+Pro+Mobile+Dashboard+UI" alt="Dashboard" width="600">
  <br>
  <i>Experience a sleek, modern Glassmorphic interface designed for productivity.</i>
</div>

---

## 🚀 Installation & Setup

### 📦 The 10-Second QuickStart (Recommended)
1.  **Download** the latest `SudarshanPro.exe` from the [Releases](https://github.com/JaiServanaBhava/SudarshanPro/releases) page.
2.  **Launch** the application.[cite: 2]
3.  **Firewall:** When Windows asks, check **both** 🔳 **Private** and 🔳 **Public** networks.
4.  **Connect:** Scan the QR code on your PC screen and enter your secure PIN.[cite: 2]

### 💻 Developer Mode (Running from Source)
```bash
# Clone the repository
git clone https://github.com/JaiServanaBhava/SudarshanPro.git
cd SudarshanPro

# Install dependencies
pip install flask waitress psutil pyautogui pyperclip qrcode zeroconf pillow opencv-python pyaudio pyttsx3

# Run the master script
python remotepc.py
