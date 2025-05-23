import os
from model import DatabaseModel
from view import MainView, AddRecordDialog, SearchDialog, DeleteDialog
from tkinter import messagebox, filedialog
from constants import COLUMN_HEADERS_MAP
from config_manager import get_db_name, set_db_name
from xml_handler import XMLWriter, XMLReader


class Controller:
    """
    Controller managing the interaction between the model and the view.
    """

    def __init__(self):
        self.db_name = get_db_name()
        self.model = None
        self._initialize_model()

        self.all_records = []  # To store all records for in-memory sorting
        self.refresh_all_records()  # Initial load of all records

        self.view = MainView(self)

    def _initialize_model(self):
        """Initializes or re-initializes the DatabaseModel."""
        if self.model:
            self.model.close()  # Close existing connection if any
        try:
            self.model = DatabaseModel(db_name=self.db_name)
        except (ConnectionError, RuntimeError) as e:
            messagebox.showerror("Database Error", f"Failed to connect or initialize database '{self.db_name}': {e}\n"
                                                   "Please select a valid database file or create a new one.")
            self.model = None  # Set model to None if initialization fails

    def run(self):
        """Runs the main application window."""
        self.view.mainloop()
        if self.model:
            self.model.close()

    def refresh_all_records(self):
        """Refreshes the in-memory list of all records from the database."""
        if self.model:
            self.all_records = self.model.get_all_records()
        else:
            self.all_records = []

    def open_add_dialog(self):
        """Opens the add record dialog."""
        if self.model:
            AddRecordDialog(self.view, self)
        else:
            messagebox.showwarning("Database Not Ready", "Please select or create a database file first.",
                                   parent=self.view)

    def open_search_dialog(self):
        """Opens the search records dialog."""
        if self.model:
            SearchDialog(self.view, self)
        else:
            messagebox.showwarning("Database Not Ready", "Please select or create a database file first.",
                                   parent=self.view)

    def open_delete_dialog(self):
        """Opens the delete records dialog."""
        if self.model:
            DeleteDialog(self.view, self)
        else:
            messagebox.showwarning("Database Not Ready", "Please select or create a database file first.",
                                   parent=self.view)

    def add_record(self, record_data):
        """
        Adds a record to the database.
        :param record_data: Dictionary with record data.
        :return: True if record was added successfully, False otherwise.
        """
        if self.model:
            success = self.model.add_record(record_data)
            if success:
                self.refresh_all_records()
                self.view.update_record_display()
            return success
        return False

    def get_paginated_and_sorted_records(self, offset, limit, sort_column, sort_order):
        """
        Retrieves records for display on the current page, sorted.
        :param offset: Offset.
        :param limit: Number of records per page.
        :param sort_column: Column name to sort by.
        :param sort_order: 'asc' for ascending, 'desc' for descending.
        :return: List of sorted and paginated records.
        """
        if not self.all_records:
            return []

        column_names = list(COLUMN_HEADERS_MAP.keys())
        try:
            sort_index = column_names.index(sort_column)
        except ValueError:
            sort_index = 0  # Default to 'id' if column not found

        reverse_sort = (sort_order == "desc")

        if sort_column in ["id", "experience"]:
            sorted_records = sorted(self.all_records, key=lambda x: int(x[sort_index]), reverse=reverse_sort)
        else:
            sorted_records = sorted(self.all_records, key=lambda x: str(x[sort_index]).lower(), reverse=reverse_sort)

        return sorted_records[offset:offset + limit]

    def get_total_records(self):
        """
        Retrieves the total number of records.
        :return: Total number of records.
        """
        return len(self.all_records)

    def search_records(self, conditions):
        """
        Performs a search for records based on conditions.
        :param conditions: Dictionary with search conditions.
        :return: List of found records.
        """
        if self.model:
            results = self.model.search_records(conditions)
            return results
        return []

    def delete_records(self, conditions):
        """
        Deletes records based on conditions.
        :param conditions: Dictionary with deletion conditions.
        :return: Number of deleted records.
        """
        if self.model:
            deleted_count = self.model.delete_records(conditions)
            if deleted_count > 0:
                self.refresh_all_records()
            self.view.update_record_display()
            return deleted_count
        return 0

    def get_unique_values(self, column_name):
        """
        Retrieves unique values for dropdown lists.
        :param column_name: Column name.
        :return: List of unique values.
        """
        if self.model:
            return self.model.get_unique_values(column_name)
        return []

    def select_db_file(self):
        """Allows the user to select a new SQLite database file."""
        file_path = filedialog.askopenfilename(
            parent=self.view,
            title="Select Database File",
            filetypes=[("SQLite Database", "*.db"), ("All Files", "*.*")]
        )
        if file_path:
            try:
                set_db_name(file_path)
                self.db_name = file_path
                self._initialize_model()
                self.refresh_all_records()
                self.view.update_record_display()
                messagebox.showinfo("Database Changed",
                                    f"Successfully switched to database: {os.path.basename(file_path)}",
                                    parent=self.view)
            except Exception as e:
                messagebox.showerror("Error", f"Could not open or switch database: {e}", parent=self.view)
                self.db_name = get_db_name()
                self._initialize_model()
                self.refresh_all_records()
                self.view.update_record_display()

    def export_data_to_xml(self):
        """Exports all current records to an XML file using DOM parser."""
        if not self.model or not self.all_records:
            messagebox.showwarning("Export Warning", "No records to export or database not connected.",
                                   parent=self.view)
            return

        file_path = filedialog.asksaveasfilename(
            parent=self.view,
            title="Export Records to XML",
            defaultextension=".xml",
            filetypes=[("XML files", "*.xml"), ("All files", "*.*")]
        )
        if file_path:
            try:
                records_dicts = []
                column_names = list(COLUMN_HEADERS_MAP.keys())
                for record_tuple in self.all_records:
                    record_dict = {column_names[i]: record_tuple[i] for i in range(len(column_names))}
                    records_dicts.append(record_dict)

                XMLWriter.write_records_to_xml(records_dicts, file_path)
                messagebox.showinfo("Export Complete",
                                    f"Records successfully exported to:\n{os.path.basename(file_path)}",
                                    parent=self.view)
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export records to XML: {e}", parent=self.view)

    def import_data_from_xml(self):
        """Imports records from an XML file into the database using SAX parser."""
        if not self.model:
            messagebox.showwarning("Import Warning",
                                   "Database not connected. Please select or create a database file first.",
                                   parent=self.view)
            return

        file_path = filedialog.askopenfilename(
            parent=self.view,
            title="Import Records from XML",
            filetypes=[("XML files", "*.xml"), ("All files", "*.*")]
        )
        if file_path:
            try:
                imported_records = XMLReader.read_records_from_xml(file_path)
                if imported_records:
                    if self.model.add_records_batch(imported_records):
                        self.refresh_all_records()
                        self.view.update_record_display()
                        messagebox.showinfo("Import Complete",
                                            f"Successfully imported {len(imported_records)} records from:\n{os.path.basename(file_path)}",
                                            parent=self.view)
                    else:
                        messagebox.showerror("Import Error", "Failed to add imported records to the database.",
                                             parent=self.view)
                else:
                    messagebox.showinfo("Import Complete", "No records found in the selected XML file.",
                                        parent=self.view)
            except Exception as e:
                messagebox.showerror("Import Error", f"Failed to import records from XML: {e}", parent=self.view)
