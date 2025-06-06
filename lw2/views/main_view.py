import tkinter as tk
from tkinter import ttk, messagebox
from utils.constants import COLUMN_HEADERS_MAP
from .pagination_model import PaginationModel # Import the new model


class MainView(tk.Tk):
    """
    Main application window, displaying a list of teachers and controls.
    """

    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.title("Teacher Data Management")
        self.geometry("900x600")

        self.pagination_model = PaginationModel() # Create an instance of the pagination model

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
        file_menu.add_command(label="Tree View", command=self.controller.open_tree_view)
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

    def _sort_column(self, col):
        """
        Sorts the Treeview content by the specified column.
        """
        # Reset header text for the previously sorted column
        if self.pagination_model.sort_column:
            old_header_text = COLUMN_HEADERS_MAP.get(self.pagination_model.sort_column, self.pagination_model.sort_column)
            self.tree.heading(self.pagination_model.sort_column, text=old_header_text)

        self.pagination_model.toggle_sort_order(col) # Use the model's method to toggle sort

        arrow = " ▲" if self.pagination_model.sort_order == "asc" else " ▼"
        new_header_text = COLUMN_HEADERS_MAP.get(self.pagination_model.sort_column, self.pagination_model.sort_column) + arrow
        self.tree.heading(self.pagination_model.sort_column, text=new_header_text)

        self.update_record_display()

    def update_record_display(self, records=None):
        """
        Updates the display of records in the table.
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
            self.pagination_model.set_total_records(total_records)

            offset = (self.pagination_model.current_page - 1) * self.pagination_model.records_per_page
            records = self.controller.get_paginated_and_sorted_records(
                offset, self.pagination_model.records_per_page, self.pagination_model.sort_column, self.pagination_model.sort_order
            )
        else:
            # If records are passed directly (e.g., from search), pagination is not applied
            self.pagination_model.set_total_records(len(records))
            self.pagination_model.current_page = 1 # Reset page as this is not a paginated set
            self.pagination_model.sort_column = "id" # Reset sort
            self.pagination_model.sort_order = "asc"

        for record in records:
            self.tree.insert("", "end", values=record)

        self.page_info_label.config(text=f"Page {self.pagination_model.current_page} of {self.pagination_model.total_pages} ({self.pagination_model.total_records} records)")
        self.update_pagination_buttons()

        arrow = " ▲" if self.pagination_model.sort_order == "asc" else " ▼"
        current_header_text = COLUMN_HEADERS_MAP.get(self.pagination_model.sort_column, self.pagination_model.sort_column) + arrow
        self.tree.heading(self.pagination_model.sort_column, text=current_header_text)


    def update_pagination_buttons(self):
        """Updates the state of pagination buttons."""
        self.first_page_btn.config(state=tk.NORMAL if self.pagination_model.current_page > 1 else tk.DISABLED)
        self.prev_page_btn.config(state=tk.NORMAL if self.pagination_model.current_page > 1 else tk.DISABLED)
        self.next_page_btn.config(state=tk.NORMAL if self.pagination_model.current_page < self.pagination_model.total_pages else tk.DISABLED)
        self.last_page_btn.config(state=tk.NORMAL if self.pagination_model.current_page < self.pagination_model.total_pages else tk.DISABLED)

    def go_to_first_page(self):
        """Goes to the first page."""
        self.pagination_model.go_to_first_page()
        self.update_record_display()

    def go_to_prev_page(self):
        """Goes to the previous page."""
        self.pagination_model.go_to_prev_page()
        self.update_record_display()

    def go_to_next_page(self):
        """Goes to the next page."""
        self.pagination_model.go_to_next_page()
        self.update_record_display()

    def go_to_last_page(self):
        """Goes to the last page."""
        self.pagination_model.go_to_last_page()
        self.update_record_display()

    def on_records_per_page_change(self, value):
        """Handles changing the number of records per page."""
        self.pagination_model.records_per_page = int(value)
        self.update_record_display()

    def jump_to_page(self, event=None):
        """Jumps to a specific page number entered by the user."""
        try:
            page_num = int(self.page_jump_entry.get())
            if 1 <= page_num <= self.pagination_model.total_pages:
                self.pagination_model.jump_to_page(page_num)
                self.update_record_display()
            else:
                messagebox.showwarning("Invalid Page", f"Please enter a page number between 1 and {self.pagination_model.total_pages}.",
                                       parent=self)
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number for the page.", parent=self)
        self.page_jump_entry.delete(0, tk.END)  # Clear the entry after attempt
