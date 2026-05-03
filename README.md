<div align="center">
  <!-- Use the logo link you mentioned here -->
  <img src="https://github.com/JaiServanaBhava/SudarshanPro/blob/main/icon.png" alt="Sudarshan Pro Logo" width="200">

  <h1>Sudarshan Pro</h1>

  <p><b>A powerful, lightweight Python-based Remote PC Controller & Surveillance System.</b></p>

  <p>
    <img src="https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python" alt="Python">
    <img src="https://img.shields.io/badge/Framework-Flask-lightgrey?style=for-the-badge&logo=flask" alt="Flask">
    <img src="https://img.shields.io/badge/UI-Modern_Glassmorphism-brightgreen?style=for-the-badge" alt="UI">
    <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" alt="License">
  </p>
</div>

---

## 🚀 Overview

**Sudarshan Pro** is an all-in-one remote management tool that transforms your smartphone into a sophisticated remote control for your PC. It features a modern web interface accessible via a QR code, allowing for seamless system control, file management, and real-time monitoring over the same Wi-Fi network.

## ✨ Features

*   **📱 Remote Input:** Full mouse and keyboard control (click, scroll, type) via smartphone.
*   **📸 Surveillance:** Capture real-time screenshots and webcam photos remotely.
*   **📁 DropZone:** Dedicated file transfer hub to upload/download files between PC and Mobile.
*   **🎙️ Voice & TTS:** Send text to be spoken by the PC or record remote audio clips.
*   **⚡ System Actions:** Control volume, brightness, power (shutdown/sleep), and monitor status.
*   **📊 Task Manager:** View running processes and kill them remotely if needed.
*   **🌐 mDNS Support:** Connect easily via `sudarshan.local` without typing IP addresses.
*   **🛡️ Secure Access:** Persistent PIN-based authentication for all remote actions.

## 📸 Screenshots

<div align="center">
  <img src="https://via.placeholder.com/400x250?text=Web+Dashboard+UI" alt="Dashboard" width="400">
  <img src="https://via.placeholder.com/400x250?text=QR+Code+Startup" alt="QR Interface" width="400">
  <p><i>Sudarshan Pro uses a sleek, glassmorphic UI for a professional SaaS feel.</i></p>
</div>

## 🛠️ Technologies Used

*   **Backend:** Python 3 with Flask & Waitress (Production-grade WSGI).
*   **Automation:** `PyAutoGUI` for HID control and `psutil` for system monitoring.
*   **Connectivity:** `Zeroconf` (mDNS) and `qrcode` for easy pairing.
*   **GUI:** `Tkinter` and `Pillow` for the local PC dashboard.

## 🚀 Getting Started

### Installation (Portable EXE)
1.  **Download** the latest `SudarshanPro.exe` from the [Releases](https://github.com/JaiServanaBhava/SudarshanPro/releases) page.
2.  **Run** the file. 
3.  **Firewall Setup:** 
    *   When the Windows Firewall prompt appears, ensure **both** "Private" and "Public" networks are checked to allow the phone to communicate with the PC.
4.  **Scan the QR code** that appears on your PC screen with your phone.

### Run from Source
```bash
pip install flask waitress psutil pyautogui pyperclip qrcode zeroconf pillow opencv-python
python main.py
