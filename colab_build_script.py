# ==============================================================================
# SPREADSHEET OCR - GOOGLE COLAB ONE-CLICK APK BUILDER
# ==============================================================================
# Instructions:
# 1. Go to https://colab.research.google.com/
# 2. Click "New notebook" (sign in with your Google/Gmail account if needed).
# 3. Copy this entire script, paste it into the first code cell, and click RUN (Play button).
# 4. Wait ~10 minutes. The script will write files, compile, and automatically download the APK.
# ==============================================================================

import os

# --- STEP 1: Write mobile_client.py ---
print("[1/5] Creating mobile_client.py...")
mobile_client_code = """import os
import threading
import requests
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.uix.filechooser import FileChooserIconView
from kivy.core.window import Window
from kivy.utils import platform

if platform not in ['android', 'ios']:
    Window.size = (360, 640)

class MobileScannerApp(App):
    def build(self):
        self.title = "Spreadsheet OCR Scanner"
        self.main_layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        title_label = Label(
            text="📊 Spreadsheet OCR",
            font_size='24sp',
            bold=True,
            size_hint_y=None,
            height=40,
            color=(0.54, 0.36, 0.96, 1)
        )
        self.main_layout.add_widget(title_label)
        
        subtitle_label = Label(
            text="Mobile Client (Android)",
            font_size='14sp',
            size_hint_y=None,
            height=20,
            color=(0.6, 0.6, 0.6, 1)
        )
        self.main_layout.add_widget(subtitle_label)
        
        server_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, spacing=5)
        server_layout.add_widget(Label(text="API URL:", size_hint_x=0.25, font_size='14sp'))
        
        self.server_input = TextInput(
            text="http://192.168.1.13:8000",
            multiline=False,
            font_size='14sp',
            size_hint_x=0.75
        )
        server_layout.add_widget(self.server_input)
        self.main_layout.add_widget(server_layout)
        
        self.preview_image = Image(
            source="",
            size_hint_y=0.3,
            allow_stretch=True
        )
        self.main_layout.add_widget(self.preview_image)
        
        self.status_label = Label(
            text="Status: Please select a spreadsheet image to scan",
            font_size='13sp',
            size_hint_y=None,
            height=30,
            color=(0.8, 0.8, 0.8, 1)
        )
        self.main_layout.add_widget(self.status_label)
        
        self.file_chooser = FileChooserIconView(
            size_hint_y=0.4,
            filters=['*.png', '*.jpg', '*.jpeg']
        )
        self.file_chooser.bind(on_submit=self.file_selected)
        self.main_layout.add_widget(self.file_chooser)
        
        btn_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        self.scan_btn = Button(
            text="🚀 Scan & Export",
            background_color=(0.92, 0.28, 0.6, 1),
            font_size='16sp',
            bold=True,
            disabled=True
        )
        self.scan_btn.bind(on_press=self.start_scan_thread)
        btn_layout.add_widget(self.scan_btn)
        self.main_layout.add_widget(btn_layout)
        
        self.selected_file_path = None
        return self.main_layout

    def file_selected(self, chooser, selection, touch=None):
        if selection:
            self.selected_file_path = selection[0]
            self.preview_image.source = self.selected_file_path
            self.status_label.text = f"Selected: {os.path.basename(self.selected_file_path)}"
            self.scan_btn.disabled = False

    def start_scan_thread(self, instance):
        if not self.selected_file_path:
            return
        self.status_label.text = "Uploading image and processing OCR (please wait)..."
        self.scan_btn.disabled = True
        threading.Thread(target=self.run_ocr_scan, daemon=True).start()

    def run_ocr_scan(self):
        api_url = f"{self.server_input.text.strip().rstrip('/')}/scan"
        filename = os.path.basename(self.selected_file_path)
        
        try:
            with open(self.selected_file_path, 'rb') as f:
                files = {'file': (filename, f, 'image/png')}
                response = requests.post(api_url, files=files, timeout=60)
                
            if response.status_code == 200:
                download_path = self.get_download_path(filename)
                with open(download_path, 'wb') as out_f:
                    out_f.write(response.content)
                self.update_status(f"🎉 Success! Excel saved to:\\n{download_path}", success=True)
            else:
                error_msg = response.json().get('detail', 'Unknown error occurred.')
                self.update_status(f"❌ Scan failed: {error_msg}")
                
        except requests.exceptions.RequestException as e:
            self.update_status(f"❌ Network connection error:\\nVerify your API URL and server status.")
        except Exception as e:
            self.update_status(f"❌ Error: {str(e)}")
        finally:
            self.enable_scan_button()

    def get_download_path(self, original_filename):
        base_name = f"extracted_{os.path.splitext(original_filename)[0]}.xlsx"
        if platform == 'android':
            from android.storage import primary_external_storage_path
            downloads_dir = os.path.join(primary_external_storage_path(), 'Download')
            if not os.path.exists(downloads_dir):
                os.makedirs(downloads_dir)
            return os.path.join(downloads_dir, base_name)
        else:
            return os.path.join(os.getcwd(), base_name)

    def update_status(self, text, success=False):
        def set_label(dt):
            self.status_label.text = text
            if success:
                self.status_label.color = (0.2, 0.8, 0.2, 1)
            else:
                self.status_label.color = (1, 0.3, 0.3, 1)
        from kivy.clock import Clock
        Clock.schedule_once(set_label)

    def enable_scan_button(self):
        def enable(dt):
            self.scan_btn.disabled = False
        from kivy.clock import Clock
        Clock.schedule_once(enable)

if __name__ == '__main__':
    MobileScannerApp().run()
"""

with open("main.py", "w") as f:
    f.write(mobile_client_code)
print("[SUCCESS] main.py created.")

# --- STEP 2: Write buildozer.spec ---
print("[2/5] Creating buildozer.spec...")
buildozer_spec_content = """[app]
title = Spreadsheet OCR
package.name = spreadsheet_ocr
package.domain = org.antigravity
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas
version = 1.0.0
requirements = python3,kivy,requests,urllib3,idna,certifi,charset_normalizer
orientation = portrait
fullscreen = 0
android.permissions = INTERNET, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.sdk = 33
android.bootstrap = sdl2
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 0
"""

with open("buildozer.spec", "w") as f:
    f.write(buildozer_spec_content)
print("[SUCCESS] buildozer.spec created.")

# --- STEP 3: Install Linux dependencies ---
print("[3/5] Installing Ubuntu compiler dependencies (this will take 1-2 minutes)...")
os.system("apt-get update -qq")
os.system("apt-get install -y -qq git zip unzip openjdk-17-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses5-dev libgdbm-dev libssl-dev libffi-dev cmake gettext build-essential python3-dev libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev libportmidi-dev")
os.system("pip uninstall -y cython")
os.system("pip install --upgrade -q buildozer")
os.system("pip install -q Cython==0.29.33")  # Pinned stable compiler version for Kivy

# Explicitly set Java 17 as active JDK
os.environ["JAVA_HOME"] = "/usr/lib/jvm/java-17-openjdk-amd64"
os.system("update-alternatives --set java /usr/lib/jvm/java-17-openjdk-amd64/bin/java")
os.system("update-alternatives --set javac /usr/lib/jvm/java-17-openjdk-amd64/bin/javac")

print("[SUCCESS] Dependencies installed.")

# --- STEP 4: Run Buildozer ---
print("[4/5] Running Buildozer Android Compiler (this takes ~8-12 minutes)...")
print("Compiling APK (streaming logs in real-time)...")
os.system("buildozer android clean")  # Clear caches from any previous failed builds

import subprocess
import sys

with open("buildozer.log", "w") as log_f:
    process = subprocess.Popen(
        ["buildozer", "android", "debug"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    # Stream logs to console in real-time and save to file
    for line in process.stdout:
        sys.stdout.write(line)
        sys.stdout.flush()
        log_f.write(line)
        log_f.flush()
        
    process.wait()
    returncode = process.returncode

# --- STEP 5: Check compile output ---
print("[5/5] Checking compile output...")
if returncode != 0:
    print(f"\n[ERROR] Buildozer failed with exit code {returncode}")
    print("Please copy the log output above and paste it in the chat so I can resolve the error.")
else:
    apk_dir = "bin/"
    if os.path.exists(apk_dir):
        apks = [f for f in os.listdir(apk_dir) if f.endswith(".apk")]
        if apks:
            apk_path = os.path.join(apk_dir, apks[0])
            print(f"[SUCCESS] APK compiled successfully: {apk_path}")
            print("Downloading APK to your computer...")
            from google.colab import files
            files.download(apk_path)
        else:
            print("[ERROR] No APK file was found in the bin/ directory.")
    else:
        print("[ERROR] Build failed. The bin/ output directory was not created.")
