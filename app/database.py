import csv
import io
from threading import Lock
from typing import ClassVar

from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Interval, make_url
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

# Base class for ORM models
Base = declarative_base()


class _DatabaseConfig(BaseModel):
    """ Database configuration for connection. """
    host: str = Field(default="localhost", description="The hostname or IP address of the database server.")
    port: int = Field(default=5431, description="The port number for the database connection.")
    user: str = Field(default="test", description="The username for authenticating to the database.")
    password: str = Field(default="test", description="The password for the database user.")
    dbname: str = Field(default="test", description="The name of the database to connect to.")

    @property
    def db_url(self) -> str:
        """Constructs and returns the database URL for SQLAlchemy."""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.dbname}"


class CleaningSession(Base):
    """ ORM model for the CleaningSessions table. """
    __tablename__ = 'CleaningSessions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_start_time = Column(DateTime, nullable=False)
    session_final_state = Column(String(255), nullable=False)
    number_of_actions = Column(Integer, nullable=False)
    number_of_cleaned_tiles = Column(Integer, nullable=False)
    duration = Column(Interval, nullable=False)


class Database(BaseModel):
    """ Database class for managing the database connection. """
    config: _DatabaseConfig = Field(..., description="Database configuration", frozen=True)
    session: Session = Field(..., description="Database session", frozen=True)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    # Singleton pattern: only one database connection
    def __new__(cls, config: _DatabaseConfig):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Database, cls).__new__(cls)
        return cls.instance

    def __init__(self, config: _DatabaseConfig):
        try:
            # Use the db_url property of DatabaseConfig to construct the engine
            engine = create_engine(config.db_url)
            # Create session factory
            session_factory = sessionmaker(bind=engine)
            # Create a session
            session = session_factory()
            # Return a new instance with the session
            super().__init__(config=config, session=session)
        except Exception as e:
            raise Exception(f"Error connecting to database: {e}")

    @classmethod
    def connect(cls) -> "Database":
        """Class method to connect to the database and return an instance if successful."""
        config = _DatabaseConfig()  # Load configuration
        try:
            return cls(config=config)
        except Exception as e:
            raise Exception(f"Error connecting to database: {e}")

    def create_table(self):
        """Create the Cleaning Sessions table if it does not exist."""
        try:
            # Create all tables (if not already created)
            Base.metadata.create_all(self.session.bind)
        except Exception as e:
            raise Exception(f"Error creating table: {e}")

    def get_history(self):
        """
        Retrieve all the rows from the Cleaning Sessions table and
        write to a CSV file in the current directory.
        """
        try:
            history = self.session.query(CleaningSession).all()
            csv_buffer = io.StringIO()
            writer = csv.writer(csv_buffer)
            # Write the header (column names)
            writer.writerow([column.name for column in CleaningSession.__table__.columns])
            # Write the rows of the history
            for session in history:
                writer.writerow([
                    int(getattr(session, column.name)) if isinstance(getattr(session, column.name), (int, float))
                    else getattr(session, column.name) for column in CleaningSession.__table__.columns
                ])
            csv_content = csv_buffer.getvalue()
            csv_buffer.close()
            return csv_content

        except Exception as e:
            raise Exception(f"Error fetching history: {e}")

    def save_session(self, session: CleaningSession):
        """Insert a cleaning session into the Cleaning Sessions table."""
        try:
            # Add and commit to the database
            self.session.add(session)
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise Exception(f"Error saving session: {e}")

    def clean(self):
        """Clean the entire Cleaning Sessions table."""
        try:
            # Create all tables (if not already created)
            Base.metadata.drop_all(self.session.bind)
        except Exception as e:
            raise Exception(f"Error creating table: {e}")

    def close(self):
        """Close the database session."""
        try:
            if self.session:
                self.session.close()
                Database._instance = None  # Reset instance after closing
        except Exception as e:
            raise Exception(f"Error closing session: {e}")

    def __del__(self):
        """Ensure the session is closed when the object is deleted."""
        self.close()
