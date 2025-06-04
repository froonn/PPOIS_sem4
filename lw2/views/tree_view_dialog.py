import tkinter as tk
from tkinter import ttk
from utils.constants import COLUMN_HEADERS_MAP

class TreeViewDialog(tk.Toplevel):
    """
    Dialog for displaying records as a hierarchical tree.
    """
    def __init__(self, parent, records):
        super().__init__(parent)
        self.title("Tree View of Records")
        self.geometry("600x450")
        self.resizable(True, True)
        self.records = records
        self.column_keys = list(COLUMN_HEADERS_MAP.keys())

        self.tree = ttk.Treeview(self)
        self.init_widgets()
        self.populate_tree()
        self.grab_set()  # Modal behavior

    def init_widgets(self):
        # Scrollbars
        vsb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(self, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        hsb.pack(side="bottom", fill="x")
        # No Close button

    def populate_tree(self):
        """
        Populate the Treeview with record data.
        """
        for idx, record in enumerate(self.records):
            try:
                # Use the key for 'full_name' field from column_keys
                full_name_index = self.column_keys.index('full_name')
                record_label = f"{record[full_name_index]}"
            except Exception:
                record_label = f"Record {idx + 1}"

            parent_id = self.tree.insert('', 'end', text=record_label, open=False)
            for col_idx, col_key in enumerate(self.column_keys):
                if col_key == "full_name":
                    continue
                field_val = record[col_idx]
                header = COLUMN_HEADERS_MAP.get(col_key, col_key)
                leaf_label = f"{header}: {field_val}"
                self.tree.insert(parent_id, 'end', text=leaf_label)
        # Expand all top-level nodes
        for item in self.tree.get_children():
            self.tree.item(item, open=True)