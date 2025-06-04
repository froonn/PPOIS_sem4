import tkinter as tk
from tkinter import ttk, messagebox
from utils.constants import COLUMN_HEADERS_MAP


class SearchDialog(tk.Toplevel):
    """
    Dialog window for searching records.
    """

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.title("Search Records")
        self.geometry("600x500")
        self.transient(parent)
        self.grab_set()

        self.sort_column = "id"  # Default sort column for search results
        self.sort_order = "asc"  # Default sort order for search results
        self.search_results_data = []  # Store raw search results for sorting

        self.create_widgets()

    def create_widgets(self):
        """Creates input elements for search conditions and a table for results."""
        search_frame = tk.LabelFrame(self, text="Search Conditions")
        search_frame.pack(padx=10, pady=10, fill=tk.X)

        tk.Label(search_frame, text="Teacher Full Name (or part):").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.full_name_entry = tk.Entry(search_frame)
        self.full_name_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        tk.Label(search_frame, text="Department Name (or part):").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.department_entry = tk.Entry(search_frame)  # Changed to Entry
        self.department_entry.grid(row=1, column=1, padx=5, pady=2, sticky="ew")

        tk.Label(search_frame, text="Academic Rank:").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        self.academic_rank_options = [""] + self.controller.get_unique_values('academic_rank')
        self.academic_rank_var = tk.StringVar(self)
        self.academic_rank_combobox = ttk.Combobox(search_frame, textvariable=self.academic_rank_var,
                                                   values=self.academic_rank_options, state="readonly")
        self.academic_rank_combobox.grid(row=2, column=1, padx=5, pady=2, sticky="ew")
        self.academic_rank_combobox.set("")  # Option "any"

        tk.Label(search_frame, text="Academic Degree:").grid(row=3, column=0, padx=5, pady=2, sticky="w")  # New field
        self.academic_degree_options = [""] + self.controller.get_unique_values('academic_degree')
        self.academic_degree_var = tk.StringVar(self)
        self.academic_degree_combobox = ttk.Combobox(search_frame, textvariable=self.academic_degree_var,
                                                     values=self.academic_degree_options, state="readonly")
        self.academic_degree_combobox.grid(row=3, column=1, padx=5, pady=2, sticky="ew")
        self.academic_degree_combobox.set("")  # Option "any"

        tk.Label(search_frame, text="Faculty:").grid(row=4, column=0, padx=5, pady=2, sticky="w")
        self.faculty_options = [""] + self.controller.get_unique_values('faculty')
        self.faculty_var = tk.StringVar(self)
        self.faculty_combobox = ttk.Combobox(search_frame, textvariable=self.faculty_var,
                                             values=self.faculty_options, state="readonly")
        self.faculty_combobox.grid(row=4, column=1, padx=5, pady=2, sticky="ew")
        self.faculty_combobox.set("")  # Option "any"

        tk.Label(search_frame, text="Experience from:").grid(row=5, column=0, padx=5, pady=2, sticky="w")
        self.experience_min_entry = tk.Entry(search_frame)
        self.experience_min_entry.grid(row=5, column=1, padx=5, pady=2, sticky="ew")

        tk.Label(search_frame, text="Experience to:").grid(row=6, column=0, padx=5, pady=2, sticky="w")
        self.experience_max_entry = tk.Entry(search_frame)
        self.experience_max_entry.grid(row=6, column=1, padx=5, pady=2, sticky="ew")

        search_frame.grid_columnconfigure(1, weight=1)

        button_frame = tk.Frame(self)
        button_frame.pack(pady=5)

        search_btn = tk.Button(button_frame, text="Search", command=self.perform_search)
        search_btn.pack(side=tk.LEFT, padx=5)

        cancel_btn = tk.Button(button_frame, text="Cancel", command=self.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=5)

        results_frame = tk.LabelFrame(self, text="Search Results")
        results_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.columns = ("id", "faculty", "department", "full_name", "academic_rank", "academic_degree", "experience")
        self.results_tree = ttk.Treeview(results_frame, columns=self.columns, show="headings")

        style = ttk.Style()
        style.configure('Treeview.Heading', background='#e0e0e0', font=('TkDefaultFont', 10, 'bold'))

        for col_name, header_text in COLUMN_HEADERS_MAP.items():
            self.results_tree.heading(col_name, text=header_text, command=lambda c=col_name: self._sort_column(c))
            self.results_tree.column(col_name, anchor="center", width=80)

        self.results_tree.pack(fill=tk.BOTH, expand=True)

    def _sort_column(self, col):
        """
        Sorts the search results Treeview content by the specified column.
        Toggles between ascending and descending order.
        """
        if self.sort_column:
            old_header_text = COLUMN_HEADERS_MAP.get(self.sort_column, self.sort_column)
            self.results_tree.heading(self.sort_column, text=old_header_text)

        if self.sort_column == col:
            self.sort_order = "desc" if self.sort_order == "asc" else "asc"
        else:
            self.sort_column = col
            self.sort_order = "asc"  # Default to ascending when changing column

        arrow = " ▲" if self.sort_order == "asc" else " ▼"
        new_header_text = COLUMN_HEADERS_MAP.get(self.sort_column, self.sort_column) + arrow
        self.results_tree.heading(self.sort_column, text=new_header_text)

        self.display_search_results(self.search_results_data)  # Re-display sorted data

    def perform_search(self):
        """Collects search conditions and passes them to the controller."""
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
            return

        self.search_results_data = self.controller.search_records(conditions)  # Get raw results
        if not self.search_results_data:
            messagebox.showinfo("Search", "No records found matching the specified conditions.", parent=self)

        self.sort_column = "id"
        self.sort_order = "asc"
        self.display_search_results(self.search_results_data)

    def display_search_results(self, records):
        """Displays search results in the table, applying current sort order."""
        for i in self.results_tree.get_children():
            self.results_tree.delete(i)

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
            self.results_tree.insert("", "end", values=record)

        arrow = " ▲" if self.sort_order == "asc" else " ▼"
        current_header_text = COLUMN_HEADERS_MAP.get(self.sort_column, self.sort_column) + arrow
        self.results_tree.heading(self.sort_column, text=current_header_text)
