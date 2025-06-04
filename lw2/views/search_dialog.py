import tkinter as tk
from tkinter import ttk, messagebox
from utils.constants import COLUMN_HEADERS_MAP
from .pagination_model import PaginationModel # Import the new model


class SearchDialog(tk.Toplevel):
    """
    Dialog window for searching records with pagination.
    """

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.title("Search Records")
        self.geometry("900x650")  # Increased size to accommodate pagination elements
        self.transient(parent)
        self.grab_set()

        self.pagination_model = PaginationModel() # Create an instance of the pagination model
        self.search_results_data = []  # Store all found search results

        self.create_widgets()

    def create_widgets(self):
        """Creates input elements for search conditions, a table for results, and pagination controls."""
        search_frame = tk.LabelFrame(self, text="Search Conditions")
        search_frame.pack(padx=10, pady=10, fill=tk.X)

        tk.Label(search_frame, text="Teacher Full Name (or part):").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.full_name_entry = tk.Entry(search_frame)
        self.full_name_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        tk.Label(search_frame, text="Department Name (or part):").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.department_entry = tk.Entry(search_frame)
        self.department_entry.grid(row=1, column=1, padx=5, pady=2, sticky="ew")

        tk.Label(search_frame, text="Academic Rank:").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        self.academic_rank_options = [""] + self.controller.get_unique_values('academic_rank')
        self.academic_rank_var = tk.StringVar(self)
        self.academic_rank_combobox = ttk.Combobox(search_frame, textvariable=self.academic_rank_var,
                                                   values=self.academic_rank_options, state="readonly")
        self.academic_rank_combobox.grid(row=2, column=1, padx=5, pady=2, sticky="ew")
        self.academic_rank_combobox.set("")  # Option "any"

        tk.Label(search_frame, text="Academic Degree:").grid(row=3, column=0, padx=5, pady=2, sticky="w")
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

        # Pagination controls for search results
        pagination_frame = tk.Frame(self)
        pagination_frame.pack(pady=5)

        self.first_page_btn = tk.Button(pagination_frame, text="<<", command=self.go_to_first_page)
        self.first_page_btn.pack(side=tk.LEFT, padx=2)

        self.prev_page_btn = tk.Button(pagination_frame, text="<", command=self.go_to_prev_page)
        self.prev_page_btn.pack(side=tk.LEFT, padx=2)

        self.page_info_label = tk.Label(pagination_frame, text="Page X of Y (Z records)")
        self.page_info_label.pack(side=tk.LEFT, padx=5)

        self.next_page_btn = tk.Button(pagination_frame, text=">", command=self.go_to_next_page)
        self.next_page_btn.pack(side=tk.LEFT, padx=2)

        self.last_page_btn = tk.Button(pagination_frame, text=">>", command=self.go_to_last_page)
        self.last_page_btn.pack(side=tk.LEFT, padx=2)

        tk.Label(pagination_frame, text="Records per page:").pack(side=tk.LEFT, padx=5)
        self.records_per_page_var = tk.StringVar(self)
        self.records_per_page_var.set(str(self.pagination_model.records_per_page))
        self.records_per_page_menu = ttk.OptionMenu(pagination_frame, self.records_per_page_var,
                                                    self.records_per_page_var.get(),
                                                    *map(str, self.pagination_model.records_per_page_options),
                                                    command=self.on_records_per_page_change)
        self.records_per_page_menu.pack(side=tk.LEFT, padx=2)

        jump_page_frame = tk.Frame(self)
        jump_page_frame.pack(pady=5)
        tk.Label(jump_page_frame, text="Go to page:").pack(side=tk.LEFT, padx=5)
        self.page_jump_entry = tk.Entry(jump_page_frame, width=5)
        self.page_jump_entry.pack(side=tk.LEFT, padx=2)
        self.page_jump_entry.bind("<Return>", self.jump_to_page)  # Bind Enter key
        self.page_jump_button = tk.Button(jump_page_frame, text="Go", command=self.jump_to_page)
        self.page_jump_button.pack(side=tk.LEFT, padx=2)

        # Initially disable pagination buttons
        self.update_pagination_buttons()

    def _sort_column(self, col):
        """
        Sorts the search results Treeview content by the specified column.
        Toggles between ascending and descending order.
        """
        # Reset header text for the previously sorted column
        if self.pagination_model.sort_column:
            old_header_text = COLUMN_HEADERS_MAP.get(self.pagination_model.sort_column, self.pagination_model.sort_column)
            self.results_tree.heading(self.pagination_model.sort_column, text=old_header_text)

        self.pagination_model.toggle_sort_order(col) # Use the model's method to toggle sort

        arrow = " ▲" if self.pagination_model.sort_order == "asc" else " ▼"
        new_header_text = COLUMN_HEADERS_MAP.get(self.pagination_model.sort_column, self.pagination_model.sort_column) + arrow
        self.results_tree.heading(self.pagination_model.sort_column, text=new_header_text)

        self.display_paginated_results()

    def perform_search(self):
        """Collects search conditions and passes them to the controller, then displays paginated results."""
        conditions = {}
        if self.full_name_entry.get():
            conditions['full_name'] = self.full_name_entry.get()
        if self.department_entry.get():
            conditions['department'] = self.department_entry.get()
        if self.academic_rank_var.get():
            conditions['academic_rank'] = self.academic_rank_var.get()
        if self.academic_degree_var.get():
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

        self.search_results_data = self.controller.search_records(conditions)  # Get all raw results
        if not self.search_results_data:
            messagebox.showinfo("Search", "No records found matching the specified conditions.", parent=self)

        self.pagination_model.set_total_records(len(self.search_results_data))
        self.pagination_model.current_page = 1  # Reset to the first page for new search results
        self.pagination_model.sort_column = "id" # Reset sort column
        self.pagination_model.sort_order = "asc" # Reset sort order
        self.display_paginated_results()

    def display_paginated_results(self):
        """Displays search results in the table, applying current sort order and pagination."""
        for i in self.results_tree.get_children():
            self.results_tree.delete(i)

        paginated_records = self.pagination_model.get_paginated_and_sorted_data(
            self.search_results_data, COLUMN_HEADERS_MAP
        )

        for record in paginated_records:
            self.results_tree.insert("", "end", values=record)

        self.page_info_label.config(text=f"Page {self.pagination_model.current_page} of {self.pagination_model.total_pages} ({self.pagination_model.total_records} records)")
        self.update_pagination_buttons()

        arrow = " ▲" if self.pagination_model.sort_order == "asc" else " ▼"
        current_header_text = COLUMN_HEADERS_MAP.get(self.pagination_model.sort_column, self.pagination_model.sort_column) + arrow
        self.results_tree.heading(self.pagination_model.sort_column, text=current_header_text)

    def update_pagination_buttons(self):
        """Updates the state of pagination buttons."""
        self.first_page_btn.config(state=tk.NORMAL if self.pagination_model.current_page > 1 else tk.DISABLED)
        self.prev_page_btn.config(state=tk.NORMAL if self.pagination_model.current_page > 1 else tk.DISABLED)
        self.next_page_btn.config(state=tk.NORMAL if self.pagination_model.current_page < self.pagination_model.total_pages else tk.DISABLED)
        self.last_page_btn.config(state=tk.NORMAL if self.pagination_model.current_page < self.pagination_model.total_pages else tk.DISABLED)

    def go_to_first_page(self):
        """Goes to the first page."""
        self.pagination_model.go_to_first_page()
        self.display_paginated_results()

    def go_to_prev_page(self):
        """Goes to the previous page."""
        self.pagination_model.go_to_prev_page()
        self.display_paginated_results()

    def go_to_next_page(self):
        """Goes to the next page."""
        self.pagination_model.go_to_next_page()
        self.display_paginated_results()

    def go_to_last_page(self):
        """Goes to the last page."""
        self.pagination_model.go_to_last_page()
        self.display_paginated_results()

    def on_records_per_page_change(self, value):
        """Handles changing the number of records per page."""
        self.pagination_model.records_per_page = int(value)
        self.display_paginated_results()

    def jump_to_page(self, event=None):
        """Jumps to a specific page number entered by the user."""
        try:
            page_num = int(self.page_jump_entry.get())
            if 1 <= page_num <= self.pagination_model.total_pages:
                self.pagination_model.jump_to_page(page_num)
                self.display_paginated_results()
            else:
                messagebox.showwarning("Invalid Page", f"Please enter a page number between 1 and {self.pagination_model.total_pages}.",
                                       parent=self)
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number for the page.", parent=self)
        self.page_jump_entry.delete(0, tk.END)  # Clear the entry after attempt
