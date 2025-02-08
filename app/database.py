import csv
import io
from threading import Lock
from typing import ClassVar

from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Interval, make_url, inspect
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

# Base class for ORM models
Base = declarative_base()


class DatabaseConfig(BaseModel):
    """ Database configuration for connection. """
    host: str = Field(default="localhost", description="The hostname or IP address of the database server.")
    port: int = Field(default=5430, description="The port number for the database connection.")
    user: str = Field(default="user", description="The username for authenticating to the database.")
    password: str = Field(default="root", description="The password for the database user.")
    dbname: str = Field(default="postgres", description="The name of the database to connect to.")

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
    config: DatabaseConfig = Field(..., description="Database configuration", frozen=True)
    session: Session = Field(..., description="Database session", frozen=True)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    # Singleton pattern: only one database connection per configuration
    _instances: ClassVar = {}

    def __new__(cls, config: DatabaseConfig):
        config_hash = hash(config.db_url)  # Use db_url as the unique key for the config
        if config_hash not in cls._instances:
            instance = super(Database, cls).__new__(cls)
            cls._instances[config_hash] = instance
        return cls._instances[config_hash]

    def __init__(self, config: DatabaseConfig):
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
    def connect(cls, config: DatabaseConfig = DatabaseConfig()) -> "Database":
        """Class method to connect to the database and return an instance if successful."""
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
            # Check if the table exists
            inspector = inspect(self.session.bind)
            if CleaningSession.__tablename__ not in inspector.get_table_names():
                raise Exception("Error: Table 'CleaningSessions' does not exist.")

            # Retrieve all rows
            history = self.session.query(CleaningSession).all()
            if not history:
                raise Exception("Error: No data found in the 'CleaningSessions' table.")
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
