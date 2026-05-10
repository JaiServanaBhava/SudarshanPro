import os
import sys
import json
import platform
import psutil
import webbrowser
import pyperclip
from waitress import serve
import threading
import socket
import qrcode
import shutil
import subprocess
import time
import tkinter as tk
from PIL import ImageTk, Image
from flask import Flask, render_template, request, jsonify, send_from_directory

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".sudarshan_pro_config.json")

def load_config():
    try:
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    except Exception:
        return {"pin": "1234"}

def save_config(cfg):
    try:
        with open(CONFIG_PATH, "w") as f:
            json.dump(cfg, f)
    except Exception as e:
        print(f"Config save error: {e}")

config = load_config()

app = Flask(__name__,
            template_folder=resource_path("templates"),
            static_folder=resource_path("static"))

IS_WINDOWS = platform.system() == "Windows"
control_lock = threading.Lock()
pyautogui_available = False

try:
    import pyautogui
    pyautogui.FAILSAFE = False
    pyautogui_available = True
except Exception as e:
    print(f"Non-critical: PyAutoGUI unavailable: {e}")

try:
    import screen_brightness_control as sbc
except ImportError:
    sbc = None

_tts_sem = threading.Semaphore(1)  

def _speak_worker(text):
    """Runs in a daemon thread. Creates a fresh pyttsx3 engine every call."""
    with _tts_sem:
        try:
            import pyttsx3
            eng = pyttsx3.init()
            eng.setProperty('rate', 150)
            eng.say(text)
            eng.runAndWait()
            try:
                eng.stop()
            except Exception:
                pass
        except Exception as ex:
            print(f"TTS error: {ex}")

def speak_async(text):
    """Fire-and-forget TTS — works every single time."""
    if text:
        threading.Thread(target=_speak_worker, args=(text,), daemon=True).start()

try:
    DROP_ZONE_PATH = os.path.normpath(os.path.join(os.path.expanduser("~"), "Desktop", "DropZone"))
    os.makedirs(DROP_ZONE_PATH, exist_ok=True)
except Exception:
    DROP_ZONE_PATH = "C:\\"

def kill_port_owner(port):
    current_pid = os.getpid()
    try:
        for conn in psutil.net_connections(kind='inet'):
            try:
                if conn.laddr.port == port and conn.pid and conn.pid != current_pid:
                    psutil.Process(conn.pid).kill()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except Exception:
        pass

def start_mdns(local_ip, port=5000):
    """Advertise sudarshan.local so phones can reach the PC by name."""
    try:
        from zeroconf import Zeroconf, ServiceInfo
        import socket as _socket
        info = ServiceInfo(
            "_http._tcp.local.",
            "sudarshan._http._tcp.local.",
            addresses=[_socket.inet_aton(local_ip)],
            port=port,
            properties={"path": "/"},
            server="sudarshan.local."
        )
        zc = Zeroconf()
        zc.register_service(info)
        print(f"mDNS: sudarshan.local registered → {local_ip}:{port}")
    except ImportError:
        print("zeroconf not installed — hostname feature disabled. Run: pip install zeroconf")
    except Exception as e:
        print(f"mDNS error: {e}")

@app.route('/get_pin_check', methods=['POST'])
def get_pin_check():
    try:
        entered = str(request.json.get('pin', ''))
        correct = config.get('pin', '1234')
        return jsonify({"ok": entered == correct})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/change_pin', methods=['POST'])
def change_pin():
    try:
        data = request.json or {}
        old_pin = str(data.get('old_pin', ''))
        new_pin = str(data.get('new_pin', ''))
        if old_pin != config.get('pin', '1234'):
            return jsonify({"error": "Wrong current PIN"}), 403
        if len(new_pin) < 4 or not new_pin.isdigit():
            return jsonify({"error": "PIN must be at least 4 digits"}), 400
        config['pin'] = new_pin
        save_config(config)
        return jsonify({"status": "PIN changed successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/app_status')
def check_apps():
    try:
        active_apps = []
        media_procs = {"spotify.exe": "Spotify", "vlc.exe": "VLC", "chrome.exe": "Netflix/Web"}
        for proc in psutil.process_iter(['name']):
            try:
                name = proc.info['name'].lower()
                if name in media_procs:
                    active_apps.append(media_procs[name])
            except:
                continue
        return jsonify({"active": list(set(active_apps))})
    except Exception:
        return jsonify({"active": []})

@app.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        return f"HTML Template Error: {e}", 500

@app.route('/mouse', methods=['POST'])
def mouse_control():
    if not pyautogui_available:
        return "GUI Disabled", 503
    try:
        data = request.json
        with control_lock:
            t = data.get('type')
            if t == 'move':
                pyautogui.moveRel(data['dx'], data['dy'], _pause=False)
            elif t == 'click':
                pyautogui.click()
            elif t == 'right_click':
                pyautogui.rightClick()
            elif t == 'middle_click':
                pyautogui.middleClick()
            elif t == 'scroll':
                pyautogui.scroll(data['amount'])
        return jsonify({"status": "OK"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/volume', methods=['POST'])
def volume_control():
    try:
        action = request.json.get('action', '')
        if IS_WINDOWS and pyautogui_available:
            keys = {"up": "volumeup", "down": "volumedown", "mute": "volumemute"}
            key = keys.get(action)
            if key:
                pyautogui.press(key)
        else:
            cmd = {"up": "5%+", "down": "5%-", "mute": "toggle"}.get(action)
            if cmd:
                os.system(f"amixer -q sset Master {cmd}")
        return "OK"
    except Exception:
        return "Volume Error", 500

@app.route('/brightness', methods=['POST'])
def brightness_control():
    try:
        if sbc:
            action = request.json['action']
            current = sbc.get_brightness()
            curr_val = current[0] if isinstance(current, list) else current
            new_val = min(100, curr_val + 10) if action == "up" else max(0, curr_val - 10)
            sbc.set_brightness(new_val)
            return "OK"
    except Exception:
        pass
    return "Brightness Not Supported", 200

@app.route('/system', methods=['POST'])
def system_control():
    try:
        data = request.json
        cmd = data.get('cmd')
        with control_lock:
            if cmd == "minimize":
                if pyautogui_available:
                    pyautogui.hotkey('win', 'd') if IS_WINDOWS else pyautogui.hotkey('super', 'd')
            elif cmd == "taskmgr":
                if pyautogui_available:
                    pyautogui.hotkey('ctrl', 'shift', 'esc')
            elif cmd == "alt_tab":
                if pyautogui_available:
                    pyautogui.hotkey('alt', 'tab')
            elif cmd == "lock":
                os.system("rundll32.exe user32.dll,LockWorkStation") if IS_WINDOWS else os.system("loginctl lock-session")
            elif cmd == "message":
                msg = data.get('text', '')
                if msg:
                    threading.Thread(target=show_alert, args=(msg,), daemon=True).start()
        return "OK"
    except Exception:
        return "System CMD Error", 500

@app.route('/status')
def get_status():
    try:
        battery = psutil.sensors_battery()
        return jsonify({
            "os": platform.system(),
            "battery": f"{battery.percent:.0f}%" if battery else "N/A",
            "charging": battery.power_plugged if battery else False,
            "cpu": psutil.cpu_percent(interval=None),
            "ram": psutil.virtual_memory().percent
        })
    except Exception:
        return jsonify({"os": "Error", "cpu": 0, "ram": 0})

@app.route('/power', methods=['POST'])
def power_control():
    try:
        action = request.json['action']
        if IS_WINDOWS:
            if action == "shutdown":
                os.system("shutdown /s /t 1")
            elif action == "sleep":
                os.system("shutdown /h")
        return "OK"
    except Exception:
        return "Power Error", 500

@app.route('/speak', methods=['POST'])
def handle_speak():
    try:
        data = request.get_json(silent=True) or {}
        text = str(data.get('text', '')).strip()
        if not text:
            return jsonify({"error": "No text provided"}), 400
        speak_async(text)
        return jsonify({"status": "Speaking"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/capture_cam', methods=['POST'])
def capture_cam():
    filename = f"capture_{int(time.time())}.jpg"
    filepath = os.path.join(DROP_ZONE_PATH, filename)

    try:
        import cv2  
        cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not cam.isOpened():
            cam.release()
            raise RuntimeError("Camera busy or not found via OpenCV")
        # Warm-up: discard first few frames (exposure/AWB settle)
        for _ in range(6):
            cam.read()
        ret, frame = cam.read()
        cam.release()
        if not ret or frame is None:
            raise RuntimeError("Frame capture failed")
        cv2.imwrite(filepath, frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
        return jsonify({"status": "success", "file": filename, "method": "opencv"})
    except ImportError:
        pass  # cv2 not installed → try next method
    except Exception as cv_err:
        print(f"[cam] OpenCV attempt failed: {cv_err}")

    # ── Method 2: PowerShell + WIA (no extra install needed) ──────────
    try:
        # Escape backslashes for PowerShell
        ps_path = filepath.replace("\\", "\\\\")
        ps_script = (
            "Add-Type -AssemblyName System.Windows.Forms; "
            "try { "
            "  $wia = New-Object -ComObject WIA.DeviceManager; "
            "  $dev = ($wia.DeviceInfos | Where-Object { $_.Type -eq 64 } | Select-Object -First 1); "
            "  if (-not $dev) { Write-Output 'NO_CAM'; exit }; "
            "  $d = $dev.Connect(); "
            "  $item = $d.Items.Item(1); "
            f"  $img = $item.Transfer(); $img.SaveFile('{ps_path}'); "
            "  Write-Output 'OK' "
            "} catch { Write-Output ('ERR:' + $_.Exception.Message) }"
        )
        result = subprocess.run(
            ['powershell', '-NoProfile', '-NonInteractive', '-Command', ps_script],
            capture_output=True, text=True, timeout=20
        )
        out = result.stdout.strip()
        if 'OK' in out and os.path.exists(filepath):
            return jsonify({"status": "success", "file": filename, "method": "wia"})
        if 'NO_CAM' in out:
            return jsonify({"error": "No camera detected. Plug in a webcam and try again."}), 500
        # Log WIA error detail
        print(f"[cam] WIA output: {out} | stderr: {result.stderr.strip()}")
    except Exception as ps_err:
        print(f"[cam] PowerShell/WIA attempt failed: {ps_err}")

    # ── Method 3: Friendly error ────────────────────────────────────────
    return jsonify({
        "error": (
            "Camera capture failed. "
            "For best results, install opencv-python before building the exe: "
            "pip install opencv-python"
        )
    }), 500

@app.route('/fake_update', methods=['POST'])
def fake_update():
    try:
        url = "https://fakeupdate.net"
        webbrowser.open(url)
        if pyautogui_available:
            threading.Timer(2.0, lambda: pyautogui.press('f11')).start()
        return "Stealth Mode Active"
    except Exception:
        return "Error", 500

def show_alert(msg):
    try:
        import ctypes
        ctypes.windll.user32.MessageBoxW(0, msg, "Sudarshan Pro Alert", 0x40)
    except:
        pass

@app.route('/alert', methods=['POST'])
def alert_control():
    try:
        data = request.json or {}
        msg = data.get('message') or data.get('text') or 'Hello from Sudarshan Pro!'
        threading.Thread(target=show_alert, args=(msg,), daemon=True).start()
        return jsonify({"status": "Alert sent"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/send_type', methods=['POST'])
def send_type():
    try:
        text = request.json.get('text', '')
        if text and pyautogui_available:
            with control_lock:
                pyautogui.typewrite(text, interval=0.02)
        return jsonify({"status": "Typed"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_clipboard', methods=['GET'])
def get_clipboard():
    try:
        content = pyperclip.paste()
        return jsonify({"clipboard": content or ""})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/paste_to_pc', methods=['POST'])
def paste_to_pc():
    try:
        text = request.json.get('text', '')
        if text:
            pyperclip.copy(text)
            if pyautogui_available:
                time.sleep(0.1)
                pyautogui.hotkey('ctrl', 'v')
        return jsonify({"status": "Pasted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_processes', methods=['GET'])
def get_processes():
    try:
        procs = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
            try:
                info = proc.info
                procs.append({
                    "pid": info['pid'],
                    "name": info['name'],
                    "cpu": round(info['cpu_percent'] or 0, 1),
                    "mem": round(info['memory_percent'] or 0, 1),
                    "status": info['status']
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        procs.sort(key=lambda x: x['mem'], reverse=True)
        return jsonify({"processes": procs[:50]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/kill_process', methods=['POST'])
def kill_process():
    try:
        pid = int(request.json.get('pid', 0))
        if pid and pid != os.getpid():
            psutil.Process(pid).kill()
            return jsonify({"status": f"Killed PID {pid}"})
        return jsonify({"error": "Invalid PID"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/open_dropzone', methods=['POST'])
def open_dropzone():
    try:
        os.makedirs(DROP_ZONE_PATH, exist_ok=True)
        subprocess.Popen(f'explorer "{DROP_ZONE_PATH}"')
        return jsonify({"status": "DropZone opened", "path": DROP_ZONE_PATH})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/list_dropzone', methods=['GET'])
def list_dropzone():
    try:
        files = []
        for f in os.listdir(DROP_ZONE_PATH):
            fp = os.path.join(DROP_ZONE_PATH, f)
            files.append({
                "name": f,
                "size": os.path.getsize(fp),
                "modified": int(os.path.getmtime(fp))
            })
        return jsonify({"files": files})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/download_dropzone/<filename>', methods=['GET'])
def download_dropzone(filename):
    try:
        return send_from_directory(DROP_ZONE_PATH, filename, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/keyboard', methods=['POST'])
def keyboard_type():
    try:
        text = request.json.get('text', '')
        if text and pyautogui_available:
            with control_lock:
                pyautogui.typewrite(text, interval=0.02)
        return jsonify({"status": "Typed"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/clipboard', methods=['POST'])
def clipboard_post():
    try:
        text = request.json.get('text', '')
        if text:
            pyperclip.copy(text)
            if pyautogui_available:
                time.sleep(0.1)
                pyautogui.hotkey('ctrl', 'v')
        return jsonify({"status": "Pasted"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/clipboard', methods=['GET'])
def clipboard_get():
    try:
        content = pyperclip.paste()
        return jsonify({"text": content or ""})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/processes', methods=['GET'])
def processes_compat():
    try:
        procs = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                info = proc.info
                procs.append({
                    "pid": info['pid'],
                    "name": info['name'],
                    "cpu": round(info['cpu_percent'] or 0, 1),
                    "mem": round(info['memory_percent'] or 0, 1)
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        procs.sort(key=lambda x: x['mem'], reverse=True)
        return jsonify(procs[:50])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/kill_proc', methods=['POST'])
def kill_proc_compat():
    try:
        pid = int(request.json.get('pid', 0))
        if pid and pid != os.getpid():
            psutil.Process(pid).kill()
            return jsonify({"status": f"Killed PID {pid}"})
        return jsonify({"error": "Invalid PID"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_drops', methods=['GET'])
def get_drops_compat():
    try:
        files = [f for f in os.listdir(DROP_ZONE_PATH) if os.path.isfile(os.path.join(DROP_ZONE_PATH, f))]
        return jsonify({"files": files})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/download_drop/<filename>', methods=['GET'])
def download_drop_compat(filename):
    try:
        return send_from_directory(DROP_ZONE_PATH, filename, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/files', methods=['GET'])
def list_files():
    try:
        home = os.path.expanduser("~")
        items = os.listdir(home)
        return jsonify({"path": home, "items": items})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/download', methods=['GET'])
def download_file():
    try:
        full_path = request.args.get('path', '')
        directory = os.path.dirname(full_path)
        filename = os.path.basename(full_path)
        return send_from_directory(directory, filename, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/terminal', methods=['POST'])
def run_terminal():
    try:
        cmd = request.json.get('cmd', '')
        if cmd:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
            output = result.stdout or result.stderr or "(no output)"
        else:
            output = "No command given"
        return jsonify({"output": output})
    except subprocess.TimeoutExpired:
        return jsonify({"output": "Command timed out"})
    except Exception as e:
        return jsonify({"output": str(e)}), 500

@app.route('/launch', methods=['POST'])
def launch_app():
    try:
        name = request.json.get('name', '')
        if name:
            subprocess.Popen(name, shell=True)
        return jsonify({"status": f"Launched: {name}"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/media', methods=['POST'])
def media_control():
    try:
        action = request.json.get('action', '')
        VK_CODES = {
            "playpause": 0xB3,
            "nexttrack": 0xB0,
            "prevtrack": 0xB1,
        }
        vk = VK_CODES.get(action)
        if vk:
            import ctypes
            KEYEVENTF_KEYUP = 0x0002
            ctypes.windll.user32.keybd_event(vk, 0, 0, 0)
            time.sleep(0.05)
            ctypes.windll.user32.keybd_event(vk, 0, KEYEVENTF_KEYUP, 0)
        return jsonify({"status": "OK"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/record_audio', methods=['POST'])
def record_audio():
    try:
        data = request.get_json(silent=True) or {}
        requested_secs = int(data.get('duration', 30))
        RECORD_SECONDS = max(3, min(120, requested_secs))

        try:
            import pyaudio
            import wave

            CHUNK = 1024
            FORMAT = pyaudio.paInt16
            CHANNELS = 1
            RATE = 44100

            p = pyaudio.PyAudio()
            stream = p.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK
            )
            frames = []
            total_chunks = int(RATE / CHUNK * RECORD_SECONDS)
            for _ in range(total_chunks):
                frames.append(stream.read(CHUNK, exception_on_overflow=False))
            stream.stop_stream()
            stream.close()
            p.terminate()

            filename = f"audio_{int(time.time())}_{RECORD_SECONDS}s.wav"
            filepath = os.path.join(DROP_ZONE_PATH, filename)
            with wave.open(filepath, 'wb') as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(p.get_sample_size(FORMAT))
                wf.setframerate(RATE)
                wf.writeframes(b''.join(frames))

            return jsonify({
                "status": "success",
                "file": filename,
                "duration_seconds": RECORD_SECONDS
            })

        except ImportError:
            return jsonify({
                "error": (
                    "pyaudio is not installed. "
                    "Add 'pip install pyaudio' before building the exe, "
                    "then rebuild with build.bat."
                )
            }), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/screenshot', methods=['POST'])
def take_screenshot():
    try:
        from PIL import ImageGrab
        import io
        img = ImageGrab.grab()
        filename = f"screen_{int(time.time())}.jpg"
        filepath = os.path.join(DROP_ZONE_PATH, filename)
        img.save(filepath, "JPEG", quality=70)
        return jsonify({"status": "success", "file": filename})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/screenshot_view/<filename>', methods=['GET'])
def view_screenshot(filename):
    try:
        return send_from_directory(DROP_ZONE_PATH, filename)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/sticky_note', methods=['POST'])
def sticky_note():
    try:
        text = request.json.get('text', '').strip()
        if text:
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            filename = f"note_{int(time.time())}.txt"
            filepath = os.path.join(desktop, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(text)
            subprocess.Popen(f'notepad "{filepath}"')
            return jsonify({"status": "Note saved", "file": filename})
        return jsonify({"error": "Empty note"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/push_url', methods=['POST'])
def push_url():
    try:
        url = request.json.get('url', '').strip()
        if not url.startswith('http'):
            url = 'https://' + url
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        ]
        chrome = next((p for p in chrome_paths if os.path.exists(p)), None)
        if chrome:
            subprocess.Popen([chrome, url])
        else:
            webbrowser.open(url)
        return jsonify({"status": f"Opened: {url}"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/now_playing', methods=['GET'])
def now_playing():
    try:
        result = subprocess.run(
            ['powershell', '-command',
             "Get-Process | Where-Object {$_.MainWindowTitle -ne ''} | Select-Object -First 5 MainWindowTitle | Format-List"],
            capture_output=True, text=True, timeout=5
        )
        titles = [line.replace('MainWindowTitle :', '').strip()
                  for line in result.stdout.splitlines()
                  if 'MainWindowTitle' in line and line.strip()]
        media_title = next((t for t in titles if any(k in t.lower() for k in ['youtube', 'spotify', 'vlc', 'netflix', 'music'])), None)
        return jsonify({"title": media_title or "Nothing detected", "all_titles": titles})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/monitor', methods=['POST'])
def monitor_control():
    try:
        action = request.json.get('action', 'off')
        import ctypes
        if action == 'off':
            ctypes.windll.user32.SendMessageW(0xFFFF, 0x0112, 0xF170, 2)
        elif action == 'on':
            ctypes.windll.user32.SendMessageW(0xFFFF, 0x0112, 0xF170, -1)
            if pyautogui_available:
                pyautogui.moveRel(1, 0)
        return jsonify({"status": f"Monitor {action}"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/wallpaper', methods=['POST'])
def set_wallpaper():
    try:
        folder = request.json.get('folder', os.path.join(os.path.expanduser("~"), "Pictures"))
        exts = ('.jpg', '.jpeg', '.png', '.bmp')
        images = [os.path.join(folder, f) for f in os.listdir(folder) if f.lower().endswith(exts)]
        if not images:
            return jsonify({"error": "No images found in folder"}), 404
        import random, ctypes
        chosen = random.choice(images)
        ctypes.windll.user32.SystemParametersInfoW(20, 0, chosen, 3)
        return jsonify({"status": "Wallpaper set", "file": os.path.basename(chosen)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/upload_to_dropzone', methods=['POST'])
def upload_to_dropzone():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file"}), 400
        f = request.files['file']
        filename = f.filename.replace('/', '_').replace('\\', '_')
        filepath = os.path.join(DROP_ZONE_PATH, filename)
        f.save(filepath)
        return jsonify({"status": "Uploaded", "file": filename})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

_net_last = {"bytes_sent": 0, "bytes_recv": 0, "time": time.time()}

@app.route('/network_speed', methods=['GET'])
def network_speed():
    try:
        global _net_last
        now_stats = psutil.net_io_counters()
        now_time = time.time()
        elapsed = max(now_time - _net_last["time"], 0.1)
        up_speed = (now_stats.bytes_sent - _net_last["bytes_sent"]) / elapsed
        down_speed = (now_stats.bytes_recv - _net_last["bytes_recv"]) / elapsed
        _net_last = {"bytes_sent": now_stats.bytes_sent, "bytes_recv": now_stats.bytes_recv, "time": now_time}

        def fmt(b):
            if b > 1_000_000: return f"{b/1_000_000:.1f} MB/s"
            if b > 1_000: return f"{b/1_000:.1f} KB/s"
            return f"{b:.0f} B/s"

        return jsonify({"upload": fmt(up_speed), "download": fmt(down_speed)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/installed_apps', methods=['GET'])
def installed_apps():
    try:
        apps = {}
        scan_dirs = [
            os.path.join(os.environ.get('APPDATA', ''), r'Microsoft\Windows\Start Menu\Programs'),
            r'C:\ProgramData\Microsoft\Windows\Start Menu\Programs',
            os.path.join(os.path.expanduser('~'), 'Desktop'),
        ]
        for scan_dir in scan_dirs:
            if not os.path.exists(scan_dir):
                continue
            for root, dirs, files in os.walk(scan_dir):
                for f in files:
                    if f.lower().endswith('.lnk'):
                        name = f[:-4]
                        if name not in apps:
                            apps[name] = os.path.join(root, f)
        result = [{"name": k, "path": v} for k, v in sorted(apps.items(), key=lambda x: x[0].lower())]
        return jsonify({"apps": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/launch_app_path', methods=['POST'])
def launch_app_path():
    try:
        data = request.json or {}
        path = data.get('path', '').strip()
        if path and os.path.exists(path):
            os.startfile(path)
            return jsonify({"status": "Launched"})
        if path:
            try:
                subprocess.Popen(['cmd', '/c', 'start', '', path], shell=False)
                return jsonify({"status": f"Launched via shell: {os.path.basename(path)}"})
            except Exception:
                pass
        name = data.get('name', '').strip()
        if name:
            subprocess.Popen(name, shell=True)
            return jsonify({"status": f"Launched: {name}"})
        return jsonify({"error": "Invalid path or app not found"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/stream_frame', methods=['GET'])
def stream_frame():
    try:
        quality = int(request.args.get('q', 35))
        quality = max(5, min(95, quality))
        from PIL import ImageGrab
        import io
        img = ImageGrab.grab()
        w, h = img.size
        img = img.resize((int(w * 0.4), int(h * 0.4)))
        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=quality)
        buf.seek(0)
        from flask import Response
        return Response(buf.read(), mimetype='image/jpeg')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/browse', methods=['GET'])
def browse_files():
    try:
        path = request.args.get('path', '').strip()
        if not path:
            path = os.path.expanduser('~')
        path = os.path.normpath(path)
        if not os.path.exists(path):
            return jsonify({"error": "Path does not exist"}), 404
        try:
            entries = sorted(os.scandir(path), key=lambda e: (not e.is_dir(), e.name.lower()))
        except PermissionError:
            return jsonify({"error": "Access denied to this folder"}), 403
        items = []
        for entry in entries:
            try:
                size = entry.stat().st_size if entry.is_file() else 0
                items.append({"name": entry.name, "full_path": entry.path, "is_dir": entry.is_dir(), "size": size})
            except Exception:
                continue
        return jsonify({"path": path, "items": items})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/browse_desktop', methods=['GET'])
def browse_desktop():
    try:
        desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
        return jsonify({"path": desktop})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/download_file', methods=['GET'])
def download_file_path():
    try:
        full_path = os.path.normpath(request.args.get('path', ''))
        if not os.path.isfile(full_path):
            return jsonify({"error": "File not found"}), 404
        return send_from_directory(os.path.dirname(full_path), os.path.basename(full_path), as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def show_startup_qr(local_ip, port=5000):
    try:
        url = f"http://{local_ip}:{port}"
        hostname_url = f"http://sudarshan.local:{port}"

        root = tk.Tk()
        root.title("SUDARSHAN PRO")
        root.geometry("420x600")
        root.configure(bg='white')
        root.attributes("-topmost", True)

        # ── App Icon (place icon.ico or icon.png next to the .py / in _MEIPASS) ──
        icon_candidates = [
            resource_path("icon.ico"),
            resource_path("icon.png"),
        ]
        for ic in icon_candidates:
            if os.path.exists(ic):
                try:
                    if ic.endswith(".ico"):
                        root.iconbitmap(ic)
                    else:
                        img_icon = ImageTk.PhotoImage(Image.open(ic))
                        root.iconphoto(True, img_icon)
                except Exception:
                    pass
                break

        tk.Label(root, text="SUDARSHAN PRO", font=("Arial", 22, "bold"),
                 bg="white", fg="#0a4d95").pack(pady=(20, 4))

        # QR for direct IP
        qr = qrcode.QRCode(version=1, box_size=9, border=4)
        qr.add_data(url)
        img_qr = qr.make_image(fill_color="#1a1a2e", back_color="white")
        tk_img = ImageTk.PhotoImage(img_qr)
        qr_label = tk.Label(root, image=tk_img, bg="white")
        qr_label.image = tk_img
        qr_label.pack(expand=True)

        tk.Label(root, text=f"Scan  OR  type in browser:",
                 font=("Arial", 10), bg="white", fg="#666").pack(pady=(6, 0))
        tk.Label(root, text=url,
                 font=("Arial", 11, "bold"), bg="white", fg="#007bff").pack()
        tk.Label(root, text=f"— or —",
                 font=("Arial", 9), bg="white", fg="#aaa").pack(pady=(2, 0))
        tk.Label(root, text=hostname_url,
                 font=("Arial", 11, "bold"), bg="white", fg="#0a4d95").pack()
        tk.Label(root, text="(same Wi-Fi network required)",
                 font=("Arial", 8), bg="white", fg="#bbb").pack(pady=(2, 0))

        tk.Label(root, text="Developed by  Jai Servana Bhava",
                 font=("Arial", 9), bg="white", fg="#aaa").pack(pady=(8, 16))

        root.mainloop()
    except Exception as e:
        print(f"GUI Error: {e}")

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

if __name__ == '__main__':
    try:
        kill_port_owner(5000)
        local_ip = get_local_ip()
        threading.Thread(target=start_mdns, args=(local_ip,), daemon=True).start()

        def run_server():
            try:
                serve(app, host='0.0.0.0', port=5000, threads=16)
            except Exception as e:
                print(f"Server Error: {e}")
        threading.Thread(target=run_server, daemon=True).start()
        show_startup_qr(local_ip)
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        print(f"Startup Panic: {e}")
