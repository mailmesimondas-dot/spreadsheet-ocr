import os
import sys

def main():
    # Resolve the path to gui.py when compiled via PyInstaller
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    # Inject path to import local modules
    sys.path.insert(0, base_path)

    try:
        import gui
        gui.main()
    except Exception as e:
        import tkinter.messagebox as messagebox
        messagebox.showerror("Error", f"Failed to launch native GUI:\n{str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
