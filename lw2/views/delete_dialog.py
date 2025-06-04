import tkinter as tk
from tkinter import ttk, messagebox
from utils.constants import COLUMN_HEADERS_MAP
from .pagination_model import PaginationModel # Import the new model


class DeleteDialog(tk.Toplevel):
    """
    Dialog window for deleting records with pagination.
    Uses PaginationModel to manage pagination and sorting.
    """

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.title("Delete Records")
        self.geometry("900x650")  # Increased size to accommodate pagination elements
        self.transient(parent)
        self.grab_set()

        self.pagination_model = PaginationModel() # Create an instance of the pagination model
        self.records_to_delete = []  # Store all found results for deletion
        self.current_delete_conditions = {} # Store conditions for actual deletion

        self.create_widgets()

    def create_widgets(self):
        """Creates input elements for deletion conditions, a table for results, and pagination controls."""
        delete_frame = tk.LabelFrame(self, text="Deletion Conditions")
        delete_frame.pack(padx=10, pady=10, fill=tk.X)

        tk.Label(delete_frame, text="Teacher Full Name (or part):").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.full_name_entry = tk.Entry(delete_frame)
        self.full_name_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        tk.Label(delete_frame, text="Department Name (or part):").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.department_entry = tk.Entry(delete_frame)
        self.department_entry.grid(row=1, column=1, padx=5, pady=2, sticky="ew")

        tk.Label(delete_frame, text="Academic Rank:").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        self.academic_rank_options = [""] + self.controller.get_unique_values('academic_rank')
        self.academic_rank_var = tk.StringVar(self)
        self.academic_rank_combobox = ttk.Combobox(delete_frame, textvariable=self.academic_rank_var,
                                                   values=self.academic_rank_options, state="readonly")
        self.academic_rank_combobox.grid(row=2, column=1, padx=5, pady=2, sticky="ew")
        self.academic_rank_combobox.set("")

        tk.Label(delete_frame, text="Academic Degree:").grid(row=3, column=0, padx=5, pady=2, sticky="w")
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

        self.delete_btn = tk.Button(action_button_frame, text="Delete All Found Records", command=self.confirm_delete,
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

        # Pagination controls for deletion results
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
        Sorts the deletion results Treeview content by the specified column.
        Toggles between ascending and descending order.
        """
        # Reset header text for the previously sorted column
        if self.pagination_model.sort_column:
            old_header_text = COLUMN_HEADERS_MAP.get(self.pagination_model.sort_column, self.pagination_model.sort_column)
            self.delete_tree.heading(self.pagination_model.sort_column, text=old_header_text)

        self.pagination_model.toggle_sort_order(col) # Use the model's method to toggle sort

        arrow = " ▲" if self.pagination_model.sort_order == "asc" else " ▼"
        new_header_text = COLUMN_HEADERS_MAP.get(self.pagination_model.sort_column, self.pagination_model.sort_column) + arrow
        self.delete_tree.heading(self.pagination_model.sort_column, text=new_header_text)

        self.display_paginated_results()

    def perform_search_for_deletion(self):
        """
        Collects deletion conditions, performs a search, and displays paginated results.
        Enables the delete button if records are found.
        """
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
            self.delete_btn.config(state=tk.DISABLED)
            return

        if not conditions:
            messagebox.showwarning("Warning", "Please specify at least one condition for deletion.", parent=self)
            self.delete_btn.config(state=tk.DISABLED)
            return

        self.records_to_delete = self.controller.search_records(conditions)  # Get all raw results
        self.current_delete_conditions = conditions # Store conditions for actual deletion

        if self.records_to_delete:
            messagebox.showinfo("Search Complete",
                                f"Found {len(self.records_to_delete)} records matching the conditions. You can now delete them.",
                                parent=self)
            self.delete_btn.config(state=tk.NORMAL)  # Enable delete button
        else:
            messagebox.showinfo("Search Complete", "No records found matching the conditions.", parent=self)
            self.delete_btn.config(state=tk.DISABLED)  # Disable delete button

        self.pagination_model.set_total_records(len(self.records_to_delete))
        self.pagination_model.current_page = 1 # Reset to first page for new search results
        self.pagination_model.sort_column = "id" # Reset sort column
        self.pagination_model.sort_order = "asc" # Reset sort order
        self.display_paginated_results()

    def display_paginated_results(self):
        """Displays records found for deletion in the table, applying current sort order and pagination."""
        for i in self.delete_tree.get_children():
            self.delete_tree.delete(i)

        paginated_records = self.pagination_model.get_paginated_and_sorted_data(
            self.records_to_delete, COLUMN_HEADERS_MAP
        )

        for record in paginated_records:
            self.delete_tree.insert("", "end", values=record)

        self.page_info_label.config(text=f"Page {self.pagination_model.current_page} of {self.pagination_model.total_pages} ({self.pagination_model.total_records} records)")
        self.update_pagination_buttons()

        arrow = " ▲" if self.pagination_model.sort_order == "asc" else " ▼"
        current_header_text = COLUMN_HEADERS_MAP.get(self.pagination_model.sort_column, self.pagination_model.sort_column) + arrow
        self.delete_tree.heading(self.pagination_model.sort_column, text=current_header_text)

    def confirm_delete(self):
        """Confirms deletion and calls the controller to delete records."""
        if not self.current_delete_conditions:
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
                self.records_to_delete = []  # Clear stored records
                self.current_delete_conditions = {} # Clear conditions
                self.pagination_model.set_total_records(0) # Reset total records in pagination model
                self.display_paginated_results()  # Refresh the display (will show empty if no records)
                self.delete_btn.config(state=tk.DISABLED)
            else:
                messagebox.showinfo("Deletion Complete", "No records were deleted.", parent=self)
            self.destroy() # Close the dialog after deletion attempt

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
