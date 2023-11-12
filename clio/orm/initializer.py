from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker


# noinspection PyPep8Naming
def init_database(db_uri, echo=False, **kwargs):
    """Initialize the database."""

    # Create the base class.
    base = declarative_base()

    # Create the engine.
    engine = create_engine(db_uri, echo, **kwargs)

    # Create the session constructor.
    Session_Constructor = scoped_session(sessionmaker(bind=engine))
    return base, Session_Constructor


def create_table(base, check_first=True):
    base.metadata.create_all(checkfirst=check_first)
