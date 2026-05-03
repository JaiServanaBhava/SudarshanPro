<div align="center">
  <img src="https://github.com/JaiServanaBhava/SudarshanPro/blob/main/icon.png?raw=true" alt="Sudarshan Pro Logo" width="160">
  <h1>Sudarshan Pro</h1>
  <p align="center">
    <b>The Ultimate Zero-Config Remote PC Control & Surveillance Suite</b>
    <br />
    <i>Control your world from your pocket. Fast. Secure. Professional.</i>
  </p>

  <p align="center">
    <img src="https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python">
    <img src="https://img.shields.io/badge/Framework-Flask-black?style=for-the-badge&logo=flask" alt="Flask">
    <img src="https://img.shields.io/badge/Architecture-Async_Threaded-orange?style=for-the-badge" alt="Async">
    <img src="https://img.shields.io/badge/UI-Glassmorphism-brightgreen?style=for-the-badge" alt="UI">
  </p>

  <a href="https://drive.google.com/file/d/1PtmbLT0mRky7qzX1UMUDUjovTk7V5yRV/view?usp=sharing">
    <img src="https://img.shields.io/badge/DOWNLOAD-SUDARSHAN_PRO_EXE-blueviolet?style=for-the-badge&logo=google-drive&logoColor=white" alt="Download EXE">
  </a>

  <h4>
    <a href="#-key-advantages">Advantages</a> •
    <a href="#-feature-suite">Features</a> •
    <a href="#-screenshots">Screenshots</a> •
    <a href="#-installation">Installation</a> •
    <a href="#-tech-stack">Tech Stack</a>
  </h4>
</div>

---

## 🌟 Why Sudarshan Pro?

Traditional remote desktop tools are often heavy, laggy, or require complex port forwarding. **Sudarshan Pro** is built for speed and absolute simplicity. Whether you need to monitor your system, transfer files instantly, or control your media from across the room, it offers a professional-grade experience in a lightweight package.

### 💎 Key Advantages
*   **Zero Setup:** No mobile app installation required. Simply scan the auto-generated QR code to begin.
*   **Ultra Lightweight:** Consumes minimal RAM and CPU while maintaining a high-performance background connection.
*   **Privacy First:** All data remains on your local network. No third-party servers or external cloud dependencies.
*   **Bi-Directional Utility:** Beyond simple mouse control, it acts as a full-system bridge for file management and surveillance.
*   **100% Portable:** Run it anywhere as a single `.exe` file without needing Python installed on the host machine.[cite: 1, 2]

---

## 🛠 Feature Suite

### 📱 HID & System Control
*   **Smart Input:** Precision mouse movement, scrolling, and remote keyboard typing via your mobile browser.[cite: 1, 2]
*   **Instant Shortcuts:** One-tap Alt-Tab, Task Manager access, and desktop window toggling.[cite: 1, 2]
*   **Media Center:** Full control over playback and volume for Spotify, YouTube, VLC, and Netflix.[cite: 1, 2]

### 📸 Pro Surveillance
*   **Live Stream:** View your PC screen frame-by-frame directly on your smartphone.[cite: 1, 2]
*   **Webcam Capture:** Snap high-quality remote photos using OpenCV or native Windows drivers.[cite: 1, 2]
*   **Stealth Screenshots:** Capture and save full-resolution PC screenshots directly to your device.[cite: 1, 2]

### 📁 Data & Automation
*   **DropZone:** A dedicated desktop folder for instant, drag-and-drop file transfers between PC and Mobile.[cite: 1, 2]
*   **Clipboard Bridge:** Sync your clipboard to copy text on your phone and paste it directly on your PC.[cite: 1, 2]
*   **Process Switcher:** Real-time process monitoring with a remote "Kill" switch for frozen applications.[cite: 1, 2]
*   **Voice & TTS:** Make your PC speak any text or record remote environment audio as `.wav` files.[cite: 1, 2]

---

## 📸 Screenshots
*Insert your project screenshots here to showcase the sleek UI.*

<div align="center">
  <table style="border: none;">
    <tr>
  <td><img src="https://github.com/JaiServanaBhava/SudarshanPro/blob/main/screenshots/3.jpeg" alt="Dashboard" width="250"></td>
  <td><img src="https://github.com/JaiServanaBhava/SudarshanPro/blob/main/screenshots/2.jpeg" alt="Remote View" width="250"></td>
    </tr>
    <tr>
  <td><img src="https://github.com/JaiServanaBhava/SudarshanPro/blob/main/screenshots/1.jpeg" alt="Dashboard" width="250"></td>
  <td><img src="https://github.com/JaiServanaBhava/SudarshanPro/blob/main/screenshots/4.jpeg" alt="Dashboard" width="250"></td>
      
    </tr>
     <tr>
  <td><img src="https://github.com/JaiServanaBhava/SudarshanPro/blob/main/screenshots/5.jpeg" alt="Dashboard" width="250"></td>
  <td><img src="https://github.com/JaiServanaBhava/SudarshanPro/blob/main/screenshots/6.jpeg" alt="Dashboard" width="250"></td>
      
    </tr>
  </table>
</div>

---

## 🚀 Installation & Setup

### 📦 Portable Execution (Fastest)
1.  **Download:** Get the `SudarshanPro.exe` using the badge at the top or this [Direct Link](https://drive.google.com/file/d/1PtmbLT0mRky7qzX1UMUDUjovTk7V5yRV/view?usp=sharing).
2.  **Launch:** Open the executable file.[cite: 1, 2]
3.  **Firewall Configuration:** When prompted by Windows, you **MUST** check both 🔳 **Private** and 🔳 **Public** networks to allow your phone to talk to your PC.
4.  **Connect:** Scan the QR code on your PC screen with your phone.[cite: 1, 2]
5.  **Authentication:** 
    *   The **default security PIN** is `1234`.[cite: 1, 2]
    *   *Note: You can update this PIN to a custom value later in the settings menu for enhanced security.*[cite: 1, 2]

### 💻 Developer Mode
```bash
# Clone the repository
git clone [https://github.com/JaiServanaBhava/SudarshanPro.git](https://github.com/JaiServanaBhava/SudarshanPro.git)
cd SudarshanPro

# Install dependencies
pip install flask waitress psutil pyautogui pyperclip qrcode zeroconf pillow opencv-python pyaudio pyttsx3

# Run the controller
python remotepc.py
