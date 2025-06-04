from controllers.controller import Controller
from utils.config_manager import load_config
from tkinter import messagebox

if __name__ == "__main__":
    try:
        load_config()
    except Exception as e:
        messagebox.showerror("Configuration Error", f"Failed to load configuration: {e}\nUsing default settings.")

    app = Controller()
    app.run()
