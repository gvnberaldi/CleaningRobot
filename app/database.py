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
    host: str = Field("localhost", frozen=True, description="The hostname or IP address of the database server.")
    port: int = Field(5431, frozen=True, description="The port number for the database connection.")
    user: str = Field("test", frozen=True, description="The username for authenticating to the database.")
    password: str = Field("test", frozen=True, description="The password for the database user.")
    dbname: str = Field("test", frozen=True, description="The name of the database to connect to.")

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
    session: Session = Field(..., description="SQLAlchemy session", frozen=True)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    # Singleton instance and lock for thread safety
    _instance: ClassVar['Database'] = None
    _lock: ClassVar[Lock] = Lock()

    def __init__(self, config: _DatabaseConfig, session: Session):
        super().__init__(config=config, session=session)

        # Validates if the session's database connection matches the configuration.
        engine_url = make_url(str(self.session.bind.url))
        expected_url = make_url(self.config.db_url)
        if (engine_url.drivername != expected_url.drivername or
            engine_url.username != expected_url.username or
            engine_url.host != expected_url.host or
            engine_url.port != expected_url.port or
            engine_url.database != expected_url.database
        ):
            raise ValueError(f"Incompatible session: expected {expected_url}, but got {engine_url}")

    @classmethod
    def connect(cls) -> "Database":
        """Singleton class method to connect to the database and return an instance if successful."""
        if cls._instance is None:
            with cls._lock:  # Ensure thread safety
                if cls._instance is None:
                    # Load configuration directly from environment variables
                    config = _DatabaseConfig()
                    try:
                        # Use the db_url property of DatabaseConfig to construct the engine
                        engine = create_engine(config.db_url)
                        # Create session factory
                        session_factory = sessionmaker(bind=engine)
                        # Create a session
                        session = session_factory()
                        # Return a new instance with the session
                        cls._instance = cls(config=config, session=session)
                    except Exception as e:
                        raise Exception(f"Error connecting to database: {e}")
        return cls._instance

    def create_table(self):
        """Create the Cleaning Sessions table if it does not exist."""
        try:
            # Create all tables (if not already created)
            Base.metadata.create_all(self.session.bind)
        except Exception as e:
            raise Exception(f"Error creating table: {e}")

    def get_history(self) -> list:
        """
        Retrieve all the rows from the Cleaning Sessions table and
        write to a CSV file in the current directory.
        """
        try:
            history = self.session.query(CleaningSession).all()
            return history

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
