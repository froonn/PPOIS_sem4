import math

class PaginationModel:
    """
    Model for managing pagination and sorting state of data.
    """
    def __init__(self, records_per_page_options=None, default_records_per_page=10):
        """
        Initializes the pagination model.
        """
        self.records_per_page_options = records_per_page_options if records_per_page_options is not None else [10, 20, 50]
        self._records_per_page = default_records_per_page
        self._current_page = 1
        self._total_pages = 1
        self._total_records = 0
        self._sort_column = "id"  # Default sort column
        self._sort_order = "asc"  # Default sort order (ascending)

    @property
    def records_per_page(self):
        """Returns the current number of records per page."""
        return self._records_per_page

    @records_per_page.setter
    def records_per_page(self, value):
        """Sets the number of records per page and resets the current page to 1."""
        if value in self.records_per_page_options:
            self._records_per_page = value
            self._current_page = 1
            self._update_total_pages()

    @property
    def current_page(self):
        """Returns the current page."""
        return self._current_page

    @current_page.setter
    def current_page(self, value):
        """Sets the current page, ensuring it's within the valid range."""
        if 1 <= value <= self._total_pages:
            self._current_page = value
        elif value < 1:
            self._current_page = 1
        else:
            self._current_page = self._total_pages

    @property
    def total_pages(self):
        """Returns the total number of pages."""
        return self._total_pages

    @property
    def total_records(self):
        """Returns the total number of records."""
        return self._total_records

    @property
    def sort_column(self):
        """Returns the current sort column."""
        return self._sort_column

    @sort_column.setter
    def sort_column(self, value):
        """Sets the sort column."""
        self._sort_column = value

    @property
    def sort_order(self):
        """Returns the current sort order."""
        return self._sort_order

    @sort_order.setter
    def sort_order(self, value):
        """Sets the sort order."""
        self._sort_order = value

    def _update_total_pages(self):
        """Updates the total number of pages based on total records and records per page."""
        if self._records_per_page > 0:
            self._total_pages = math.ceil(self._total_records / self._records_per_page)
        else:
            self._total_pages = 1 # Avoid division by zero
        if self._total_pages == 0:
            self._total_pages = 1
        # Ensure current page does not exceed total pages
        if self._current_page > self._total_pages:
            self._current_page = self._total_pages

    def set_total_records(self, count):
        """
        Sets the total number of records and updates the total number of pages.
        """
        self._total_records = count
        self._update_total_pages()

    def go_to_first_page(self):
        """Goes to the first page."""
        self.current_page = 1

    def go_to_prev_page(self):
        """Goes to the previous page."""
        if self.current_page > 1:
            self.current_page -= 1

    def go_to_next_page(self):
        """Goes to the next page."""
        if self.current_page < self.total_pages:
            self.current_page += 1

    def go_to_last_page(self):
        """Goes to the last page."""
        self.current_page = self.total_pages

    def jump_to_page(self, page_num):
        """
        Jumps to the specified page number.
        """
        self.current_page = page_num

    def toggle_sort_order(self, col):
        """
        Toggles the sort order for the specified column.
        """
        if self.sort_column == col:
            self.sort_order = "desc" if self.sort_order == "asc" else "asc"
        else:
            self.sort_column = col
            self.sort_order = "asc"  # Default to ascending when changing column
        self.current_page = 1 # Reset to first page after sorting

    def get_paginated_and_sorted_data(self, data, column_headers_map):
        """
        Applies sorting and pagination to the provided data.
        """
        # Apply sorting to the entire dataset
        column_names = list(column_headers_map.keys())
        try:
            sort_index = column_names.index(self.sort_column)
        except ValueError:
            sort_index = 0  # Fallback to 'id' if column not found

        reverse_sort = (self.sort_order == "desc")

        # Handle sorting for numeric and string fields
        if self.sort_column in ["id", "experience"]:
            # For numeric fields, treat empty values as 0
            sorted_data = sorted(data, key=lambda x: int(x[sort_index]) if x[sort_index] else 0, reverse=reverse_sort)
        else:
            # For string fields, treat empty values as empty string for comparison
            sorted_data = sorted(data, key=lambda x: str(x[sort_index]).lower() if x[sort_index] else '', reverse=reverse_sort)

        self.set_total_records(len(sorted_data))

        offset = (self.current_page - 1) * self.records_per_page
        paginated_data = sorted_data[offset : offset + self.records_per_page]
        return paginated_data
