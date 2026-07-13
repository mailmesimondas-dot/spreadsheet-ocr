import os
import sys
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess

# Import the core scanner backend
from scanner import TableScanner

class SpreadsheetOCRApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Spreadsheet OCR Scanner")
        self.root.geometry("620x720")
        self.root.resizable(False, False)

        # Set Colors (Premium Dark Theme)
        self.bg_color = "#0f172a"        # Deep slate/blue
        self.card_bg = "#1e293b"         # Lighter slate
        self.text_color = "#f8fafc"      # White
        self.accent_color = "#a855f7"    # Purple
        self.accent_hover = "#c084fc"    # Light purple
        self.success_color = "#10b981"   # Emerald green
        self.error_color = "#ef4444"     # Red

        self.root.configure(bg=self.bg_color)
        
        # Configure styles for ttk widgets
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        self.style.configure(".", background=self.bg_color, foreground=self.text_color)
        self.style.configure("TFrame", background=self.bg_color)
        self.style.configure("Card.TFrame", background=self.card_bg, borderwidth=1, relief="solid")
        self.style.configure("TLabel", background=self.bg_color, foreground=self.text_color, font=("Outfit", 10))
        self.style.configure("Card.TLabel", background=self.card_bg, foreground=self.text_color, font=("Outfit", 10))
        self.style.configure("Header.TLabel", background=self.bg_color, foreground=self.accent_color, font=("Outfit", 20, "bold"))
        self.style.configure("TCheckbutton", background=self.card_bg, foreground=self.text_color, font=("Outfit", 10))
        
        # Initialize Scanner Variable
        self.scanner = None
        self.input_file = None
        self.output_file = None
        
        # Build UI
        self.build_ui()

    def build_ui(self):
        # 1. Header Frame
        header_frame = ttk.Frame(self.root, padding=20)
        header_frame.pack(fill="x")
        
        title_lbl = ttk.Label(header_frame, text="📊 Spreadsheet OCR Scanner", style="Header.TLabel")
        title_lbl.pack(anchor="center")
        
        sub_lbl = ttk.Label(header_frame, text="Extract printed tables from images directly to Excel files", font=("Outfit", 9, "italic"), foreground="#94a3b8")
        sub_lbl.pack(anchor="center", pady=2)

        # 2. Main File Selection Frame (Card style)
        files_card = ttk.Frame(self.root, style="Card.TFrame", padding=15)
        files_card.pack(fill="x", padx=20, pady=10)

        # Input Row
        ttk.Label(files_card, text="Spreadsheet Image:", style="Card.TLabel", font=("Outfit", 10, "bold")).grid(row=0, column=0, sticky="w", pady=5)
        self.input_entry = tk.Entry(files_card, width=45, bg="#334155", fg=self.text_color, insertbackground="white", relief="flat", font=("Outfit", 9))
        self.input_entry.grid(row=0, column=1, padx=10, pady=5)
        
        input_btn = tk.Button(
            files_card, text="Browse...", command=self.browse_input,
            bg=self.accent_color, fg=self.text_color, activebackground=self.accent_hover, activeforeground=self.text_color,
            relief="flat", font=("Outfit", 9, "bold"), padx=10, cursor="hand2"
        )
        input_btn.grid(row=0, column=2, pady=5)

        # Output Row
        ttk.Label(files_card, text="Save Excel As:", style="Card.TLabel", font=("Outfit", 10, "bold")).grid(row=1, column=0, sticky="w", pady=10)
        self.output_entry = tk.Entry(files_card, width=45, bg="#334155", fg=self.text_color, insertbackground="white", relief="flat", font=("Outfit", 9))
        self.output_entry.grid(row=1, column=1, padx=10, pady=10)
        
        output_btn = tk.Button(
            files_card, text="Browse...", command=self.browse_output,
            bg=self.accent_color, fg=self.text_color, activebackground=self.accent_hover, activeforeground=self.text_color,
            relief="flat", font=("Outfit", 9, "bold"), padx=10, cursor="hand2"
        )
        output_btn.grid(row=1, column=2, pady=10)

        # 3. Settings Frame (Card style)
        settings_card = ttk.Frame(self.root, style="Card.TFrame", padding=15)
        settings_card.pack(fill="x", padx=20, pady=5)

        ttk.Label(settings_card, text="Layout & Extraction Settings", style="Card.TLabel", font=("Outfit", 11, "bold"), foreground=self.accent_color).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))

        # Checkbox Settings
        self.rot_var = tk.BooleanVar(value=True)
        self.borderless_var = tk.BooleanVar(value=True)
        self.rows_var = tk.BooleanVar(value=True)
        self.cols_var = tk.BooleanVar(value=True)

        ttk.Checkbutton(settings_card, text="Detect Image Rotation / Skew", variable=self.rot_var).grid(row=1, column=0, sticky="w", pady=3)
        ttk.Checkbutton(settings_card, text="Detect Borderless Tables", variable=self.borderless_var).grid(row=1, column=1, sticky="w", pady=3)
        ttk.Checkbutton(settings_card, text="Detect Implicit Rows", variable=self.rows_var).grid(row=2, column=0, sticky="w", pady=3)
        ttk.Checkbutton(settings_card, text="Detect Implicit Columns", variable=self.cols_var).grid(row=2, column=1, sticky="w", pady=3)

        # Confidence Threshold Slider
        ttk.Label(settings_card, text="OCR Confidence Threshold (%):", style="Card.TLabel").grid(row=3, column=0, sticky="w", pady=(15, 0))
        self.conf_slider = tk.Scale(
            settings_card, from_=10, to=100, orient="horizontal",
            bg=self.card_bg, fg=self.text_color, highlightbackground=self.card_bg,
            troughcolor="#334155", activebackground=self.accent_color,
            resolution=5, length=200, cursor="hand2"
        )
        self.conf_slider.set(50)
        self.conf_slider.grid(row=3, column=1, sticky="w", pady=(5, 0))

        # 4. Action Frame
        action_frame = ttk.Frame(self.root, padding=10)
        action_frame.pack(fill="x", padx=20, pady=10)

        self.scan_btn = tk.Button(
            action_frame, text="🚀 Scan & Export to Excel", command=self.start_scan_thread,
            bg="#ec4899", fg=self.text_color, activebackground="#f472b6", activeforeground=self.text_color,
            relief="flat", font=("Outfit", 12, "bold"), pady=8, cursor="hand2"
        )
        self.scan_btn.pack(fill="x")

        # 5. Output Console/Logs Frame
        console_frame = ttk.Frame(self.root, padding=5)
        console_frame.pack(fill="both", expand=True, padx=20, pady=5)

        ttk.Label(console_frame, text="Execution Logs:", font=("Outfit", 10, "bold"), foreground="#94a3b8").pack(anchor="w", pady=3)

        self.console_text = tk.Text(
            console_frame, bg="#020617", fg="#cbd5e1", insertbackground="white",
            relief="flat", font=("Consolas", 9), height=10, state="disabled"
        )
        self.console_text.pack(fill="both", expand=True, side="left")

        scrollbar = ttk.Scrollbar(console_frame, orient="vertical", command=self.console_text.yview)
        scrollbar.pack(fill="y", side="right")
        self.console_text.configure(yscrollcommand=scrollbar.set)

        # 6. Bottom Open File Action Button
        self.open_excel_btn = tk.Button(
            self.root, text="📥 Open Extracted Excel File", command=self.open_excel_file,
            bg=self.success_color, fg=self.text_color, activebackground="#34d399", activeforeground=self.text_color,
            relief="flat", font=("Outfit", 10, "bold"), state="disabled", pady=6, cursor="hand2"
        )
        self.open_excel_btn.pack(fill="x", padx=20, pady=(5, 20))

    def log(self, message):
        """
        Thread-safely appends a message to the status console.
        """
        self.console_text.configure(state="normal")
        self.console_text.insert(tk.END, f"{message}\n")
        self.console_text.see(tk.END)
        self.console_text.configure(state="disabled")

    def browse_input(self):
        file_path = filedialog.askopenfilename(
            title="Select Spreadsheet Image",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg"), ("All Files", "*.*")]
        )
        if file_path:
            self.input_file = file_path
            self.input_entry.delete(0, tk.END)
            self.input_entry.insert(0, os.path.abspath(file_path))
            
            # Suggest a default output path
            dir_name = os.path.dirname(file_path)
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            default_out = os.path.join(dir_name, f"extracted_{base_name}.xlsx")
            
            self.output_file = default_out
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, os.path.abspath(default_out))

    def browse_output(self):
        file_path = filedialog.asksaveasfilename(
            title="Save Excel File As",
            defaultextension=".xlsx",
            filetypes=[("Excel Files", "*.xlsx")]
        )
        if file_path:
            self.output_file = file_path
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, os.path.abspath(file_path))

    def start_scan_thread(self):
        # Validate inputs
        in_path = self.input_entry.get().strip()
        out_path = self.output_entry.get().strip()

        if not in_path or not os.path.exists(in_path):
            messagebox.showerror("Error", "Please select a valid input spreadsheet image.")
            return
        if not out_path:
            messagebox.showerror("Error", "Please select an output Excel file location.")
            return

        self.input_file = in_path
        self.output_file = out_path

        # Disable buttons during execution to avoid race conditions
        self.scan_btn.configure(state="disabled", text="Scanning...")
        self.open_excel_btn.configure(state="disabled")
        
        # Clear console log
        self.console_text.configure(state="normal")
        self.console_text.delete(1.0, tk.END)
        self.console_text.configure(state="disabled")

        # Run process in a background thread so UI remains responsive
        threading.Thread(target=self.run_ocr_scan, daemon=True).start()

    def run_ocr_scan(self):
        self.log("[OCR START] Starting spreadsheet scanning workflow...")
        try:
            # 1. Initialize Engine
            if self.scanner is None:
                self.log("[STATUS] Initializing EasyOCR Engine (first boot downloads models)...")
                # Run on CPU for packaging/compatibility by default
                self.scanner = TableScanner(gpu=False, lang=["en"])
                self.log("[SUCCESS] EasyOCR Engine successfully initialized.")
            
            # 2. Extract layout
            self.log(f"[STATUS] Parsing table structure from: {os.path.basename(self.input_file)}")
            self.log(f"[INFO] Rotation Correction={self.rot_var.get()}, Borderless={self.borderless_var.get()}")
            
            extracted_tables, doc = self.scanner.scan_image(
                image_path=self.input_file,
                detect_rotation=self.rot_var.get(),
                implicit_rows=self.rows_var.get(),
                implicit_columns=self.cols_var.get(),
                borderless_tables=self.borderless_var.get(),
                min_confidence=self.conf_slider.get()
            )

            # 3. Handle results
            if not extracted_tables:
                self.log("[WARNING] No tabular structures could be identified in the image.")
                self.log("[STATUS] Try adjusting the settings (enable rotation/skew correction).")
                messagebox.showwarning("No Tables Found", "No spreadsheet structures were detected in the image.")
                self.scan_btn.configure(state="normal", text="🚀 Scan & Export to Excel")
                return

            self.log(f"[SUCCESS] Detected {len(extracted_tables)} tables in image layout.")
            
            # 4. Exporting to excel
            self.log(f"[STATUS] Exporting cell text values to Excel sheets: {os.path.basename(self.output_file)}")
            self.scanner.export_to_excel(doc, self.output_file)
            
            self.log("[SUCCESS] Excel file generated successfully.")
            self.log(f"[OUTPUT] File saved at: {os.path.abspath(self.output_file)}")
            
            # Enable Open Button thread-safely
            self.open_excel_btn.configure(state="normal")
            
            # Pop success dialog
            messagebox.showinfo(
                "Scanning Completed", 
                f"Successfully extracted {len(extracted_tables)} tables!\n\nSaved to: {os.path.basename(self.output_file)}"
            )

        except Exception as e:
            self.log(f"[ERROR] Process failed: {str(e)}")
            messagebox.showerror("Execution Failed", f"An error occurred:\n{str(e)}")
            
        finally:
            # Enable scan button thread-safely
            self.scan_btn.configure(state="normal", text="🚀 Scan & Export to Excel")

    def open_excel_file(self):
        """
        Launches the generated Excel file in Microsoft Excel or default system viewer.
        """
        if self.output_file and os.path.exists(self.output_file):
            try:
                if sys.platform == "win32":
                    os.startfile(self.output_file)
                elif sys.platform == "darwin":
                    subprocess.call(["open", self.output_file])
                else:
                    subprocess.call(["xdg-open", self.output_file])
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open Excel file:\n{str(e)}")

def main():
    root = tk.Tk()
    app = SpreadsheetOCRApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
