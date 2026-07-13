import os
import threading
import requests
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.image import Image
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.utils import platform

# Set a standard mobile portrait ratio for testing on desktop
if platform not in ['android', 'ios']:
    Window.size = (360, 640)

class MobileScannerApp(App):
    def build(self):
        self.title = "Spreadsheet OCR Scanner"
        
        # Main layout
        self.main_layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        # Title Header
        title_label = Label(
            text="📊 Spreadsheet OCR",
            font_size='24sp',
            bold=True,
            size_hint_y=None,
            height=40,
            color=(0.54, 0.36, 0.96, 1)  # Purple Accent
        )
        self.main_layout.add_widget(title_label)
        
        # Sub-header
        subtitle_label = Label(
            text="Mobile Client (Android)",
            font_size='14sp',
            size_hint_y=None,
            height=20,
            color=(0.6, 0.6, 0.6, 1)
        )
        self.main_layout.add_widget(subtitle_label)
        
        # Server URL configuration
        server_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, spacing=5)
        server_layout.add_widget(Label(text="API URL:", size_hint_x=0.25, font_size='14sp'))
        
        # Retrieve default local host address
        self.server_input = TextInput(
            text="http://192.168.1.13:8000",  # Replace with backend host IP
            multiline=False,
            font_size='14sp',
            size_hint_x=0.75
        )
        server_layout.add_widget(self.server_input)
        self.main_layout.add_widget(server_layout)
        
        # Image Preview placeholder
        self.preview_image = Image(
            source="",
            size_hint_y=0.3,
            allow_stretch=True
        )
        self.main_layout.add_widget(self.preview_image)
        
        # Current status label
        self.status_label = Label(
            text="Status: Please select a spreadsheet image to scan",
            font_size='13sp',
            size_hint_y=None,
            height=30,
            color=(0.8, 0.8, 0.8, 1)
        )
        self.main_layout.add_widget(self.status_label)
        
        # File selector component
        self.file_chooser = FileChooserIconView(
            size_hint_y=0.4,
            filters=['*.png', '*.jpg', '*.jpeg']
        )
        self.file_chooser.bind(on_submit=self.file_selected)
        self.main_layout.add_widget(self.file_chooser)
        
        # Control Buttons
        btn_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)
        
        self.scan_btn = Button(
            text="🚀 Scan & Export",
            background_color=(0.92, 0.28, 0.6, 1), # Pinkish-red
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
        
        # Run scanning inside a background thread so Kivy UI stays responsive
        threading.Thread(target=self.run_ocr_scan, daemon=True).start()

    def run_ocr_scan(self):
        api_url = f"{self.server_input.text.strip().rstrip('/')}/scan"
        filename = os.path.basename(self.selected_file_path)
        
        try:
            # Prepare files for multipart/form-data upload
            with open(self.selected_file_path, 'rb') as f:
                files = {'file': (filename, f, 'image/png')}
                # Call REST API
                response = requests.post(api_url, files=files, timeout=60)
                
            if response.status_code == 200:
                # Save output Excel file
                download_path = self.get_download_path(filename)
                with open(download_path, 'wb') as out_f:
                    out_f.write(response.content)
                
                self.update_status(f"🎉 Success! Excel saved to:\n{download_path}", success=True)
            else:
                error_msg = response.json().get('detail', 'Unknown error occurred.')
                self.update_status(f"❌ Scan failed: {error_msg}")
                
        except requests.exceptions.RequestException as e:
            self.update_status(f"❌ Network connection error:\nVerify your API URL and server status.")
        except Exception as e:
            self.update_status(f"❌ Error: {str(e)}")
        finally:
            self.enable_scan_button()

    def get_download_path(self, original_filename):
        """
        Determines the appropriate user download directory based on the platform.
        """
        base_name = f"extracted_{os.path.splitext(original_filename)[0]}.xlsx"
        if platform == 'android':
            # Save directly to Android primary storage Downloads directory
            from android.storage import primary_external_storage_path
            downloads_dir = os.path.join(primary_external_storage_path(), 'Download')
            if not os.path.exists(downloads_dir):
                os.makedirs(downloads_dir)
            return os.path.join(downloads_dir, base_name)
        else:
            # Desktop fallback (saves in local directory)
            return os.path.join(os.getcwd(), base_name)

    def update_status(self, text, success=False):
        # Update Kivy labels thread-safely
        def set_label(dt):
            self.status_label.text = text
            if success:
                self.status_label.color = (0.2, 0.8, 0.2, 1) # Green success text
            else:
                self.status_label.color = (1, 0.3, 0.3, 1) # Red error text
        from kivy.clock import Clock
        Clock.schedule_once(set_label)

    def enable_scan_button(self):
        def enable(dt):
            self.scan_btn.disabled = False
        from kivy.clock import Clock
        Clock.schedule_once(enable)

if __name__ == '__main__':
    MobileScannerApp().run()
