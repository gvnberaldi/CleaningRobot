import os
import sys
import pytest
from sqlalchemy.exc import IntegrityError

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from app.database import CleaningSession


class TestDatabaseMethods:
    def test_create_table(self, db_connection):
        """Test that the CleaningSessions table is created successfully."""
        assert db_connection.query(CleaningSession).count() == 0  # Table exists but is empty

    def test_save_valid_session(self, db_connection, valid_cleaning_session):
        """Test inserting a valid CleaningSession into the database."""
        db_connection.add(valid_cleaning_session)
        db_connection.commit()
        session_count = db_connection.query(CleaningSession).count()
        assert session_count == 1  # Ensure the session is stored

    def test_save_invalid_session(self, db_connection, invalid_cleaning_session):
        """Test inserting an invalid CleaningSession and expect failure."""
        db_connection.add(invalid_cleaning_session)
        with pytest.raises(IntegrityError):  # Expect failure due to constraints
            db_connection.commit()
        db_connection.rollback()  # Ensure the database state remains clean

    def test_get_history(self, db_connection, valid_cleaning_session):
        """Test retrieving all cleaning sessions from the database."""
        db_connection.add(valid_cleaning_session)
        db_connection.commit()

        # Retrieve sessions
        sessions = db_connection.query(CleaningSession).all()
        assert len(sessions) == 1
        assert sessions[0].session_final_state == "Completed"

    def test_cleanup(self, db_connection):
        """Ensure the database session is properly cleaned after the test."""
        assert db_connection.query(CleaningSession).count() == 0  # New test session should be clean
