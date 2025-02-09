import csv
import io
import os
import sys
import tempfile
import time

import pytest
from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from app.database import CleaningSession, Base


class TestDatabaseMethods:
    def test_create_table(self, db_connection):
        """Test that the CleaningSessions table is created successfully."""
        db_connection.create_table()
        assert db_connection.session.query(CleaningSession).count() == 0  # Table exists but is empty

    def test_save_valid_session(self, db_connection, valid_cleaning_session):
        """Test inserting a valid CleaningSession into the database."""
        db_connection.create_table()
        db_connection.save_session(valid_cleaning_session)
        assert db_connection.session.query(CleaningSession).count() == 1  # Ensure the session is stored

    def test_save_invalid_session(self, db_connection, invalid_cleaning_session):
        """Test inserting an invalid CleaningSession and expect failure."""
        db_connection.create_table()
        with pytest.raises(Exception):  # Expect failure due to constraints
            db_connection.save_session(invalid_cleaning_session)

    def test_get_history(self, db_connection, valid_cleaning_session):
        """Test retrieving all cleaning sessions from the database."""
        db_connection.create_table()
        db_connection.save_session(valid_cleaning_session)

        # Retrieve the history (list of CleaningSession objects)
        csv_dump = db_connection.get_history()

        csv_dump = io.StringIO(csv_dump)
        reader = csv.reader(csv_dump)
        rows = list(reader)

        # Assert that there's at least one row (header + data)
        assert len(rows) > 1, "CSV data is empty or does not contain data."

        # Check the header matches the column names of CleaningSession
        header = rows[0]
        expected_header = [column.name for column in CleaningSession.__table__.columns]
        assert header == expected_header, f"Header mismatch: {header} != {expected_header}"

        # Extract the expected values from valid_cleaning_session
        expected_values = [
            str(getattr(valid_cleaning_session, column.name)) for column in CleaningSession.__table__.columns
        ]

        # Compare the retrieved data row with the expected values
        data_row = rows[1]
        assert data_row == expected_values, f"Data mismatch: {data_row} != {expected_values}"

    def test_cleanup(self, db_connection):
        """Ensure the database session is properly cleaned after the test."""
        inspector = inspect(db_connection.session.bind)
        tables = inspector.get_table_names()
        # Assert that the list of tables is empty (no tables should exist)
        assert len(tables) == 0
