import sqlmodel
from sqlmodel import SQLModel, Session
from .db_config import DATABASE_URL, DB_TIMEZONE
import timescaledb

if DATABASE_URL == "":
    raise NotImplementedError('DATABASE_URL needs to be set')

print('DATABASE_URL', DATABASE_URL)
# Fix SQLAlchemy dialect mismatch
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
engine = timescaledb.create_engine(DATABASE_URL, timezone=DB_TIMEZONE)

def init_db():
    print('Creating Database....')
    SQLModel.metadata.create_all(engine)
    # print('Creating Hypertable...')
    # timescaledb.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
