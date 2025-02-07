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

        # Retrieve the history (list of CleaningSession objects)
        retrieved_sessions = db_connection.get_history()

        # Check if the retrieved sessions contain the valid_cleaning_session
        assert len(retrieved_sessions) == 1, "No sessions retrieved."

        # Retrieve the first session and compare with the valid_cleaning_session
        retrieved_session = retrieved_sessions[0]

        # Check that the retrieved session matches the inserted one
        assert retrieved_session.id == valid_cleaning_session.id, "ID mismatch."
        assert retrieved_session.session_start_time == valid_cleaning_session.session_start_time, "Start time mismatch."
        assert retrieved_session.session_final_state == valid_cleaning_session.session_final_state, "State mismatch."
        assert retrieved_session.number_of_actions == valid_cleaning_session.number_of_actions, "Actions mismatch."
        assert retrieved_session.number_of_cleaned_tiles == valid_cleaning_session.number_of_cleaned_tiles, "Tiles mismatch."
        assert retrieved_session.duration == valid_cleaning_session.duration, "Duration mismatch."

    def test_cleanup(self, db_connection):
        """Ensure the database session is properly cleaned after the test."""
        inspector = inspect(db_connection.session.bind)
        tables = inspector.get_table_names()
        # Assert that the list of tables is empty (no tables should exist)
        assert len(tables) == 0
