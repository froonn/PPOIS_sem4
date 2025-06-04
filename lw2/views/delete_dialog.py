import tkinter as tk
from tkinter import ttk, messagebox
from utils.constants import COLUMN_HEADERS_MAP


class DeleteDialog(tk.Toplevel):
    """
    Dialog window for deleting records.
    """

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.title("Delete Records")
        self.geometry("600x550")  # Slightly taller to accommodate delete button
        self.transient(parent)
        self.grab_set()

        self.sort_column = "id"  # Default sort column for delete results
        self.sort_order = "asc"  # Default sort order for delete results
        self.records_to_delete = []  # Store raw search results for deletion

        self.create_widgets()

    def create_widgets(self):
        """Creates input elements for deletion conditions and a table for results."""
        delete_frame = tk.LabelFrame(self, text="Deletion Conditions")
        delete_frame.pack(padx=10, pady=10, fill=tk.X)

        tk.Label(delete_frame, text="Teacher Full Name (or part):").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.full_name_entry = tk.Entry(delete_frame)
        self.full_name_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        tk.Label(delete_frame, text="Department Name (or part):").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.department_entry = tk.Entry(delete_frame)  # Changed to Entry
        self.department_entry.grid(row=1, column=1, padx=5, pady=2, sticky="ew")

        tk.Label(delete_frame, text="Academic Rank:").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        self.academic_rank_options = [""] + self.controller.get_unique_values('academic_rank')
        self.academic_rank_var = tk.StringVar(self)
        self.academic_rank_combobox = ttk.Combobox(delete_frame, textvariable=self.academic_rank_var,
                                                   values=self.academic_rank_options, state="readonly")
        self.academic_rank_combobox.grid(row=2, column=1, padx=5, pady=2, sticky="ew")
        self.academic_rank_combobox.set("")

        tk.Label(delete_frame, text="Academic Degree:").grid(row=3, column=0, padx=5, pady=2, sticky="w")  # New field
        self.academic_degree_options = [""] + self.controller.get_unique_values('academic_degree')
        self.academic_degree_var = tk.StringVar(self)
        self.academic_degree_combobox = ttk.Combobox(delete_frame, textvariable=self.academic_degree_var,
                                                     values=self.academic_degree_options, state="readonly")
        self.academic_degree_combobox.grid(row=3, column=1, padx=5, pady=2, sticky="ew")
        self.academic_degree_combobox.set("")

        tk.Label(delete_frame, text="Faculty:").grid(row=4, column=0, padx=5, pady=2, sticky="w")
        self.faculty_options = [""] + self.controller.get_unique_values('faculty')
        self.faculty_var = tk.StringVar(self)
        self.faculty_combobox = ttk.Combobox(delete_frame, textvariable=self.faculty_var,
                                             values=self.faculty_options, state="readonly")
        self.faculty_combobox.grid(row=4, column=1, padx=5, pady=2, sticky="ew")
        self.faculty_combobox.set("")

        tk.Label(delete_frame, text="Experience from:").grid(row=5, column=0, padx=5, pady=2, sticky="w")
        self.experience_min_entry = tk.Entry(delete_frame)
        self.experience_min_entry.grid(row=5, column=1, padx=5, pady=2, sticky="ew")

        tk.Label(delete_frame, text="Experience to:").grid(row=6, column=0, padx=5, pady=2, sticky="w")
        self.experience_max_entry = tk.Entry(delete_frame)
        self.experience_max_entry.grid(row=6, column=1, padx=5, pady=2, sticky="ew")

        delete_frame.grid_columnconfigure(1, weight=1)

        action_button_frame = tk.Frame(self)
        action_button_frame.pack(pady=5)

        search_btn = tk.Button(action_button_frame, text="Search for Deletion",
                               command=self.perform_search_for_deletion)
        search_btn.pack(side=tk.LEFT, padx=5)

        self.delete_btn = tk.Button(action_button_frame, text="Delete Selected Records", command=self.confirm_delete,
                                    state=tk.DISABLED)
        self.delete_btn.pack(side=tk.LEFT, padx=5)

        cancel_btn = tk.Button(action_button_frame, text="Cancel", command=self.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=5)

        results_frame = tk.LabelFrame(self, text="Records to Delete")
        results_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.columns = ("id", "faculty", "department", "full_name", "academic_rank", "academic_degree", "experience")
        self.delete_tree = ttk.Treeview(results_frame, columns=self.columns, show="headings")

        style = ttk.Style()
        style.configure('Treeview.Heading', background='#e0e0e0', font=('TkDefaultFont', 10, 'bold'))

        for col_name, header_text in COLUMN_HEADERS_MAP.items():
            self.delete_tree.heading(col_name, text=header_text, command=lambda c=col_name: self._sort_column(c))
            self.delete_tree.column(col_name, anchor="center", width=80)

        self.delete_tree.pack(fill=tk.BOTH, expand=True)

    def _sort_column(self, col):
        """
        Sorts the delete results Treeview content by the specified column.
        Toggles between ascending and descending order.
        """
        if self.sort_column:
            old_header_text = COLUMN_HEADERS_MAP.get(self.sort_column, self.sort_column)
            self.delete_tree.heading(self.sort_column, text=old_header_text)

        if self.sort_column == col:
            self.sort_order = "desc" if self.sort_order == "asc" else "asc"
        else:
            self.sort_column = col
            self.sort_order = "asc"  # Default to ascending when changing column

        arrow = " ▲" if self.sort_order == "asc" else " ▼"
        new_header_text = COLUMN_HEADERS_MAP.get(self.sort_column, self.sort_column) + arrow
        self.delete_tree.heading(self.sort_column, text=new_header_text)

        self.display_delete_results(self.records_to_delete)  # Re-display sorted data

    def perform_search_for_deletion(self):
        """
        Collects deletion conditions, performs a search, and displays results.
        Enables the delete button if records are found.
        """
        conditions = {}
        if self.full_name_entry.get():
            conditions['full_name'] = self.full_name_entry.get()
        if self.department_entry.get():  # Get value from Entry
            conditions['department'] = self.department_entry.get()
        if self.academic_rank_var.get():
            conditions['academic_rank'] = self.academic_rank_var.get()
        if self.academic_degree_var.get():  # Get value from new combobox
            conditions['academic_degree'] = self.academic_degree_var.get()
        if self.faculty_var.get():
            conditions['faculty'] = self.faculty_var.get()
        try:
            if self.experience_min_entry.get():
                conditions['experience_min'] = int(self.experience_min_entry.get())
            if self.experience_max_entry.get():
                conditions['experience_max'] = int(self.experience_max_entry.get())
        except ValueError:
            messagebox.showerror("Input Error", "Experience must be a number.", parent=self)
            self.delete_btn.config(state=tk.DISABLED)
            return

        if not conditions:
            messagebox.showwarning("Warning", "Please specify at least one condition for deletion.", parent=self)
            self.delete_btn.config(state=tk.DISABLED)
            return

        self.records_to_delete = self.controller.search_records(conditions)  # Get raw results

        if self.records_to_delete:
            messagebox.showinfo("Search Complete",
                                f"Found {len(self.records_to_delete)} records matching the conditions. You can now delete them.",
                                parent=self)
            self.delete_btn.config(state=tk.NORMAL)  # Enable delete button
        else:
            messagebox.showinfo("Search Complete", "No records found matching the conditions.", parent=self)
            self.delete_btn.config(state=tk.DISABLED)  # Disable delete button

        self.current_delete_conditions = conditions

        self.sort_column = "id"
        self.sort_order = "asc"
        self.display_delete_results(self.records_to_delete)

    def display_delete_results(self, records):
        """Displays records found for deletion in the table, applying current sort order."""
        for i in self.delete_tree.get_children():
            self.delete_tree.delete(i)

        column_names = list(COLUMN_HEADERS_MAP.keys())
        try:
            sort_index = column_names.index(self.sort_column)
        except ValueError:
            sort_index = 0  # Fallback to 'id'

        reverse_sort = (self.sort_order == "desc")

        if self.sort_column in ["id", "experience"]:
            sorted_records = sorted(records, key=lambda x: int(x[sort_index]), reverse=reverse_sort)
        else:
            sorted_records = sorted(records, key=lambda x: str(x[sort_index]).lower(), reverse=reverse_sort)

        for record in sorted_records:
            self.delete_tree.insert("", "end", values=record)

        arrow = " ▲" if self.sort_order == "asc" else " ▼"
        current_header_text = COLUMN_HEADERS_MAP.get(self.sort_column, self.sort_column) + arrow
        self.delete_tree.heading(self.sort_column, text=current_header_text)

    def confirm_delete(self):
        """Confirms deletion and calls the controller to delete records."""
        if not hasattr(self, 'current_delete_conditions') or not self.current_delete_conditions:
            messagebox.showwarning("Warning", "No search conditions defined for deletion.", parent=self)
            return

        if not self.records_to_delete:
            messagebox.showinfo("Deletion Complete", "No records to delete based on current search.", parent=self)
            self.delete_btn.config(state=tk.DISABLED)
            return

        response = messagebox.askyesno("Confirm Deletion",
                                       f"Are you sure you want to delete {len(self.records_to_delete)} record(s) matching the criteria?",
                                       parent=self)
        if response:
            deleted_count = self.controller.delete_records(self.current_delete_conditions)
            if deleted_count > 0:
                messagebox.showinfo("Deletion Complete", f"Deleted records: {deleted_count}", parent=self)
                self.records_to_delete = []  # Clear displayed records
                self.display_delete_results([])  # Clear treeview
                self.delete_btn.config(state=tk.DISABLED)
            else:
                messagebox.showinfo("Deletion Complete", "No records were deleted.", parent=self)
            self.destroy()
