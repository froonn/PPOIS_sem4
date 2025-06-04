import sqlite3
from tkinter import messagebox


class DatabaseModel:
    """
    Data model responsible for interacting with the SQLite database.
    """

    def __init__(self, db_name):
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_table()

    def connect(self):
        """Establishes a connection to the database."""
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            raise ConnectionError(f"Could not connect to the database: {e}")  # Re-raise for controller to catch

    def create_table(self):
        """Creates the 'teachers' table if it doesn't exist."""
        if self.conn:
            try:
                self.cursor.execute("""
                                    CREATE TABLE IF NOT EXISTS teachers
                                    (
                                        id              INTEGER PRIMARY KEY AUTOINCREMENT,
                                        faculty         TEXT    NOT NULL,
                                        department      TEXT    NOT NULL,
                                        full_name       TEXT    NOT NULL,
                                        academic_rank   TEXT    NOT NULL,
                                        academic_degree TEXT    NOT NULL,
                                        experience      INTEGER NOT NULL
                                    )
                                    """)
                self.conn.commit()
            except sqlite3.Error as e:
                print(f"Table creation error: {e}")
                raise RuntimeError(f"Could not create table: {e}")  # Re-raise for controller to catch

    def add_record(self, record):
        """
        Adds a new record to the teachers table.
        :param record: Dictionary with teacher data.
        """
        if self.conn:
            try:
                self.cursor.execute("""
                                    INSERT INTO teachers (faculty, department, full_name, academic_rank,
                                                          academic_degree, experience)
                                    VALUES (?, ?, ?, ?, ?, ?)
                                    """, (record['faculty'], record['department'], record['full_name'],
                                          record['academic_rank'], record['academic_degree'], record['experience']))
                self.conn.commit()
                return True
            except sqlite3.Error as e:
                print(f"Error adding record: {e}")
                return False
        return False

    def add_records_batch(self, records):
        """
        Adds multiple records to the teachers table in a batch.
        :param records: List of dictionaries with teacher data.
        """
        if self.conn:
            try:
                records_to_insert = []
                for r in records:
                    records_to_insert.append((r.get('faculty'), r.get('department'), r.get('full_name'),
                                              r.get('academic_rank'), r.get('academic_degree'), r.get('experience')))

                self.cursor.executemany("""
                                        INSERT INTO teachers (faculty, department, full_name, academic_rank,
                                                              academic_degree, experience)
                                        VALUES (?, ?, ?, ?, ?, ?)
                                        """, records_to_insert)
                self.conn.commit()
                return True
            except sqlite3.Error as e:
                print(f"Error adding records batch: {e}")
                return False
        return False

    def get_all_records(self):
        """
        Retrieves all records from the table.
        :return: List of tuples with all records.
        """
        if self.conn:
            try:
                self.cursor.execute("SELECT * FROM teachers")
                return self.cursor.fetchall()
            except sqlite3.Error as e:
                print(f"Error getting all records: {e}")
                messagebox.showerror("Error", f"Could not retrieve all records: {e}")
        return []

    def count_records(self):
        """
        Returns the total number of records in the table.
        :return: Number of records.
        """
        if self.conn:
            try:
                self.cursor.execute("SELECT COUNT(*) FROM teachers")
                return self.cursor.fetchone()[0]
            except sqlite3.Error as e:
                print(f"Error counting records: {e}")
                messagebox.showerror("Error", f"Could not count records: {e}")
        return 0

    def search_records(self, conditions):
        """
        Searches for records based on specified conditions.
        :param conditions: Dictionary with search conditions.
        :return: List of tuples with found records.
        """
        if self.conn:
            query = "SELECT * FROM teachers WHERE 1=1"
            params = []

            if conditions.get('full_name'):
                query += " AND full_name LIKE ?"
                params.append(f"%{conditions['full_name']}%")
            if conditions.get('department'):
                query += " AND department LIKE ?"
                params.append(f"%{conditions['department']}%")
            if conditions.get('academic_rank'):
                query += " AND academic_rank = ?"
                params.append(conditions['academic_rank'])
            if conditions.get('academic_degree'):
                query += " AND academic_degree = ?"
                params.append(conditions['academic_degree'])
            if conditions.get('faculty'):
                query += " AND faculty = ?"
                params.append(conditions['faculty'])
            if conditions.get('experience_min') is not None:
                query += " AND experience >= ?"
                params.append(conditions['experience_min'])
            if conditions.get('experience_max') is not None:
                query += " AND experience <= ?"
                params.append(conditions['experience_max'])

            try:
                self.cursor.execute(query, params)
                return self.cursor.fetchall()
            except sqlite3.Error as e:
                print(f"Error searching records: {e}")
                messagebox.showerror("Error", f"Could not search records: {e}")
        return []

    def delete_records(self, conditions):
        """
        Deletes records based on specified conditions.
        :param conditions: Dictionary with deletion conditions.
        :return: Number of deleted records.
        """
        if self.conn:
            query = "DELETE FROM teachers WHERE 1=1"
            params = []

            if conditions.get('full_name'):
                query += " AND full_name LIKE ?"
                params.append(f"%{conditions['full_name']}%")
            if conditions.get('department'):
                query += " AND department LIKE ?"
                params.append(f"%{conditions['department']}%")
            if conditions.get('academic_rank'):
                query += " AND academic_rank = ?"
                params.append(conditions['academic_rank'])
            if conditions.get('academic_degree'):
                query += " AND academic_degree = ?"
                params.append(conditions['academic_degree'])
            if conditions.get('faculty'):
                query += " AND faculty = ?"
                params.append(conditions['faculty'])
            if conditions.get('experience_min') is not None:
                query += " AND experience >= ?"
                params.append(conditions['experience_min'])
            if conditions.get('experience_max') is not None:
                query += " AND experience <= ?"
                params.append(conditions['experience_max'])

            try:
                self.cursor.execute(query, params)
                deleted_count = self.cursor.rowcount
                self.conn.commit()
                return deleted_count
            except sqlite3.Error as e:
                print(f"Error deleting records: {e}")
                return 0
        return 0

    def get_unique_values(self, column_name):
        """
        Retrieves unique values from the specified column.
        :param column_name: Name of the column.
        :return: List of unique values.
        """
        if self.conn:
            try:
                self.cursor.execute(f"SELECT DISTINCT {column_name} FROM teachers")
                return [row[0] for row in self.cursor.fetchall()]
            except sqlite3.Error as e:
                print(f"Error getting unique values: {e}")
                return []
        return []

    def close(self):
        """Closes the database connection."""
        if self.conn:
            self.conn.close()
