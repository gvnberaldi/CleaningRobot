import csv
import os
import sys
import tempfile
import time

import pytest
from sqlalchemy import inspect
from sqlalchemy.exc import IntegrityError

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from app.database import CleaningSession


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
        db_connection.get_history()
        # Check if the CSV file was created
        file_path = os.path.join(os.getcwd(), "cleaning_sessions.csv")
        assert os.path.exists(file_path), "CSV file was not created."

        # Read the content of the CSV file and validate the data
        with open(file_path, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            rows = list(reader)
            # Assert that there's at least one row (header + data)
            assert len(rows) > 1, "CSV file is empty or does not contain data."
            # Check the header matches the column names of CleaningSession
            header = rows[0]
            expected_header = [column.name for column in CleaningSession.__table__.columns]
            assert header == expected_header, f"Header mismatch: {header} != {expected_header}"
            # Check that the first row matches the data of the valid_cleaning_session
            row_data = rows[1]  # The first row after the header
            assert len(row_data) == len(expected_header), "Row data does not match column count."

            # Extract the values from the valid_cleaning_session object and compare with the row
            session_values = [
                str(valid_cleaning_session.id),
                valid_cleaning_session.session_start_time.strftime('%Y-%m-%d %H:%M:%S'),
                valid_cleaning_session.session_final_state,
                str(valid_cleaning_session.number_of_actions),
                str(valid_cleaning_session.number_of_cleaned_tiles),
                str(valid_cleaning_session.duration)
            ]

            # Assert that the row matches the values in valid_cleaning_session
            assert row_data == session_values, f"Row data mismatch: {row_data} != {session_values}"

        # Delete the created CSV file after the test is complete
        if os.path.exists(file_path):
            os.remove(file_path)
            assert not os.path.exists(file_path), "CSV file was not deleted."

    def test_cleanup(self, db_connection):
        """Ensure the database session is properly cleaned after the test."""
        inspector = inspect(db_connection.session.bind)
        tables = inspector.get_table_names()
        # Assert that the list of tables is empty (no tables should exist)
        assert len(tables) == 0
