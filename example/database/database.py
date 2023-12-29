import os

from clio import SQLAlchemy

database_uri = os.environ.get("DATABASE_URI")

db = SQLAlchemy(database_uri or "")
