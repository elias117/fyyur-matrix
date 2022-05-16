import os

SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database


# TODO IMPLEMENT DATABASE URL
database_user = os.getenv("DATABASE_USER", "postgres")
database_password = os.getenv("DATABASE_PASSWORD", "postgres")
database_address = os.getenv("DATABASE_ADDRESS", "localhost:5432")
database_name = os.getenv("DATABASE_NAME", "fyyur")
SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://{}:{}@{}/{}".format(
    database_user, database_password, database_address, database_name
)
