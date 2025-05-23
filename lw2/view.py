import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from constants import ACADEMIC_RANKS, ACADEMIC_DEGREES, FACULTIES, COLUMN_HEADERS_MAP


class MainView(tk.Tk):
    """
    Main application window, displaying a list of teachers and controls.
    """

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.title("Teacher Data Management")
        self.geometry("900x600")

        self.records_per_page_options = [10, 20, 50]
        self.records_per_page = tk.IntVar(value=self.records_per_page_options[0])
        self.current_page = 1
        self.total_pages = 1

        self.sort_column = "id"  # Default sort column
        self.sort_order = "asc"  # Default sort order

        self.create_menu()
        self.create_toolbar()
        self.create_widgets()
        self.update_record_display()

    def create_menu(self):
        """Creates the main application menu."""
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        edit_menu = tk.Menu(menubar, tearoff=0)

        menubar.add_cascade(label="File", menu=file_menu)
        menubar.add_cascade(label="Edit", menu=edit_menu)

        file_menu.add_command(label="Select Database...", command=self.controller.select_db_file)
        file_menu.add_command(label="Export to XML...", command=self.controller.export_data_to_xml)
        file_menu.add_command(label="Import from XML...", command=self.controller.import_data_from_xml)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)

        edit_menu.add_command(label="Add Record", command=self.controller.open_add_dialog)
        edit_menu.add_command(label="Search Records", command=self.controller.open_search_dialog)
        edit_menu.add_command(label="Delete Records", command=self.controller.open_delete_dialog)

    def create_toolbar(self):
        """Creates the toolbar."""
        toolbar = tk.Frame(self, bd=1, relief=tk.RAISED)

        add_btn = tk.Button(toolbar, text="Add", command=self.controller.open_add_dialog)
        add_btn.pack(side=tk.LEFT, padx=2, pady=2)

        search_btn = tk.Button(toolbar, text="Search", command=self.controller.open_search_dialog)
        search_btn.pack(side=tk.LEFT, padx=2, pady=2)

        delete_btn = tk.Button(toolbar, text="Delete", command=self.controller.open_delete_dialog)
        delete_btn.pack(side=tk.LEFT, padx=2, pady=2)

        toolbar.pack(side=tk.TOP, fill=tk.X)

    def create_widgets(self):
        """Creates widgets for displaying records and pagination."""
        self.columns = ("id", "faculty", "department", "full_name", "academic_rank", "academic_degree", "experience")
        self.tree = ttk.Treeview(self, columns=self.columns, show="headings")

        style = ttk.Style()
        style.configure('Treeview.Heading', background='#e0e0e0', font=('TkDefaultFont', 10, 'bold'))

        for col_name, header_text in COLUMN_HEADERS_MAP.items():
            self.tree.heading(col_name, text=header_text, command=lambda c=col_name: self._sort_column(c))
            self.tree.column(col_name, anchor="center", width=100)

        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

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
        self.records_per_page_menu = ttk.OptionMenu(pagination_frame, self.records_per_page,
                                                    self.records_per_page.get(),
                                                    *self.records_per_page_options,
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

    def _sort_column(self, col):
        """
        Sorts the Treeview content by the specified column.
        Toggles between ascending and descending order.
        """
        if self.sort_column:
            old_header_text = COLUMN_HEADERS_MAP.get(self.sort_column, self.sort_column)
            self.tree.heading(self.sort_column, text=old_header_text)

        if self.sort_column == col:
            self.sort_order = "desc" if self.sort_order == "asc" else "asc"
        else:
            self.sort_column = col
            self.sort_order = "asc"  # Default to ascending when changing column

        arrow = " ▲" if self.sort_order == "asc" else " ▼"
        new_header_text = COLUMN_HEADERS_MAP.get(self.sort_column, self.sort_column) + arrow
        self.tree.heading(self.sort_column, text=new_header_text)

        self.current_page = 1  # Reset to first page after sorting
        self.update_record_display()

    def update_record_display(self, records=None):
        """
        Updates the display of records in the table.
        :param records: List of records to display. If None, records will be retrieved from the controller.
        """
        current_selection_ids = self.tree.selection()
        if current_selection_ids:
            self.selected_record_id = self.tree.item(current_selection_ids[0], 'values')[0]
        else:
            self.selected_record_id = None

        for i in self.tree.get_children():
            self.tree.delete(i)

        if records is None:
            total_records = self.controller.get_total_records()
            self.total_pages = (total_records + self.records_per_page.get() - 1) // self.records_per_page.get()
            if self.total_pages == 0:
                self.total_pages = 1

            if self.current_page > self.total_pages:
                self.current_page = self.total_pages
            if self.current_page < 1:
                self.current_page = 1

            offset = (self.current_page - 1) * self.records_per_page.get()
            records = self.controller.get_paginated_and_sorted_records(
                offset, self.records_per_page.get(), self.sort_column, self.sort_order
            )
        else:
            total_records = len(records)
            self.total_pages = 1
            self.current_page = 1

        for record in records:
            self.tree.insert("", "end", values=record)

        self.page_info_label.config(text=f"Page {self.current_page} of {self.total_pages} ({total_records} records)")
        self.update_pagination_buttons()

        arrow = " ▲" if self.sort_order == "asc" else " ▼"
        current_header_text = COLUMN_HEADERS_MAP.get(self.sort_column, self.sort_column) + arrow
        self.tree.heading(self.sort_column, text=current_header_text)

    def update_pagination_buttons(self):
        """Updates the state of pagination buttons."""
        self.first_page_btn.config(state=tk.NORMAL if self.current_page > 1 else tk.DISABLED)
        self.prev_page_btn.config(state=tk.NORMAL if self.current_page > 1 else tk.DISABLED)
        self.next_page_btn.config(state=tk.NORMAL if self.current_page < self.total_pages else tk.DISABLED)
        self.last_page_btn.config(state=tk.NORMAL if self.current_page < self.total_pages else tk.DISABLED)

    def go_to_first_page(self):
        """Goes to the first page."""
        self.current_page = 1
        self.update_record_display()

    def go_to_prev_page(self):
        """Goes to the previous page."""
        if self.current_page > 1:
            self.current_page -= 1
            self.update_record_display()

    def go_to_next_page(self):
        """Goes to the next page."""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.update_record_display()

    def go_to_last_page(self):
        """Goes to the last page."""
        self.current_page = self.total_pages
        self.update_record_display()

    def on_records_per_page_change(self, value):
        """Handles changing the number of records per page."""
        self.records_per_page.set(int(value))
        self.current_page = 1  # Reset to the first page when changing records per page
        self.update_record_display()

    def jump_to_page(self, event=None):
        """Jumps to a specific page number entered by the user."""
        try:
            page_num = int(self.page_jump_entry.get())
            if 1 <= page_num <= self.total_pages:
                self.current_page = page_num
                self.update_record_display()
            else:
                messagebox.showwarning("Invalid Page", f"Please enter a page number between 1 and {self.total_pages}.",
                                       parent=self)
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number for the page.", parent=self)
        self.page_jump_entry.delete(0, tk.END)  # Clear the entry after attempt


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
        self.grab_set()         # Captures all input events

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
