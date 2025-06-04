import tkinter as tk
from tkinter import ttk, messagebox
from utils.constants import ACADEMIC_RANKS, ACADEMIC_DEGREES, FACULTIES


class AddRecordDialog(tk.Toplevel):
    """
    Dialog window for adding a new record.
    """

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.title("Add Record")
        self.geometry("400x275")
        self.transient(parent)  # Makes the dialog modal relative to its parent
        self.grab_set()  # Captures all input events

        self.create_widgets()

    def create_widgets(self):
        """Creates input elements for adding a record."""
        labels = ["Faculty:", "Department Name:", "Teacher Full Name:",
                  "Academic Rank:", "Academic Degree:", "Experience (years):"]
        self.entries = {}

        for i, text in enumerate(labels):
            tk.Label(self, text=text).grid(row=i, column=0, padx=10, pady=5, sticky="w")
            entry = tk.Entry(self)
            entry.grid(row=i, column=1, padx=10, pady=5, sticky="ew")
            self.entries[text.replace(":", "").strip()] = entry

        # Use imported constants for predefined lists
        self.entries["Academic Rank"] = ttk.Combobox(self, values=ACADEMIC_RANKS, state="readonly")
        self.entries["Academic Rank"].grid(row=3, column=1, padx=10, pady=5, sticky="ew")
        self.entries["Academic Rank"].set(ACADEMIC_RANKS[0])

        self.entries["Academic Degree"] = ttk.Combobox(self, values=ACADEMIC_DEGREES, state="readonly")
        self.entries["Academic Degree"].grid(row=4, column=1, padx=10, pady=5, sticky="ew")
        self.entries["Academic Degree"].set(ACADEMIC_DEGREES[0])

        self.entries["Faculty"] = ttk.Combobox(self, values=FACULTIES, state="readonly")
        self.entries["Faculty"].grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        self.entries["Faculty"].set(FACULTIES[0])

        button_frame = tk.Frame(self)
        button_frame.grid(row=len(labels), column=0, columnspan=2, pady=10)

        add_btn = tk.Button(button_frame, text="Add", command=self.add_record)
        add_btn.pack(side=tk.LEFT, padx=5)

        cancel_btn = tk.Button(button_frame, text="Cancel", command=self.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=5)

        self.grid_columnconfigure(1, weight=1)

    def add_record(self):
        """Collects data from fields and passes it to the controller for adding."""
        record_data = {
            'faculty': self.entries["Faculty"].get(),
            'department': self.entries["Department Name"].get(),
            'full_name': self.entries["Teacher Full Name"].get(),
            'academic_rank': self.entries["Academic Rank"].get(),
            'academic_degree': self.entries["Academic Degree"].get(),
            'experience': self.entries["Experience (years)"].get()
        }

        try:
            record_data['experience'] = int(record_data['experience'])
            if record_data['experience'] < 0:
                messagebox.showerror("Input Error", "Experience cannot be negative.", parent=self)
                return
        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid experience: {e}", parent=self)
            return
        if not all(record_data.values()):
            messagebox.showwarning("Warning", "All fields must be filled.", parent=self)
            return

        if self.controller.add_record(record_data):
            messagebox.showinfo("Success", "Record successfully added.", parent=self)
        else:
            messagebox.showerror("Error", "Could not add record.", parent=self)

        self.destroy()  # Close the dialog after showing the message
