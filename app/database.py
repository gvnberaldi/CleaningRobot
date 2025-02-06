import csv
import os
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Interval
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session

# Base class for ORM models
Base = declarative_base()


class _DatabaseConfig(BaseModel):
    """ Database configuration for connection. """
    host: str = Field(..., env="DB_HOST", frozen=True)
    port: int = Field(..., env="DB_PORT", frozen=True)
    user: str = Field(..., env="DB_USER", frozen=True)
    password: str = Field(..., env="DB_PASSWORD", frozen=True)
    dbname: str = Field(..., env="DB_NAME", frozen=True)

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

    @classmethod
    def connect(cls) -> "Database":
        """Class method to connect to the database and return an instance if successful."""
        # Load configuration directly from environment variables
        config = _DatabaseConfig()

        try:
            # Use the db_url property of DatabaseConfig to construct the engine
            engine = create_engine(config.db_url, echo=True)

            # Create session factory
            session_factory = sessionmaker(bind=engine)

            # Create a session
            session = session_factory()

            # Return a new instance with the session
            db_instance = cls(config=config, session=session)
            return db_instance
        except Exception as e:
            raise Exception(f"Error connecting to database: {e}")

    def create_table(self):
        """Create the Cleaning Sessions table if it does not exist."""
        try:
            # Create all tables (if not already created)
            Base.metadata.create_all(self.session.bind)
        except Exception as e:
            raise Exception(f"Error creating table: {e}")

    def get_history(self) -> None:
        """
        Retrieve all the rows from the Cleaning Sessions table and
        write to a CSV file in the current directory.
        """
        try:
            history = self.session.query(CleaningSession).all()

            # Get the current working directory
            current_directory = os.getcwd()
            file_path = os.path.join(current_directory, "cleaning_sessions.csv")

            # Write the data to a CSV file in the current directory
            with open(file_path, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                # Write the header (column names)
                writer.writerow([column.name for column in CleaningSession.__table__.columns])
                # Write the rows of the history
                for session in history:
                    writer.writerow([getattr(session, column.name) for column in CleaningSession.__table__.columns])

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
        except Exception as e:
            raise Exception(f"Error closing session: {e}")

    def __del__(self):
        """Ensure the session is closed when the object is deleted."""
        self.close()
