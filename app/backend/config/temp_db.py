
import tempfile
import uuid
import os

def generate_temp_db_url() -> str:
    """
    Generates a temporary SQLite database URL with a random filename.

    Returns:
        str: SQLAlchemy-compatible database URL.
    """
    temp_dir = tempfile.gettempdir()
    random_filename = f"testdb_{uuid.uuid4().hex}.db"
    db_path = os.path.join(temp_dir, random_filename)
    return f"sqlite:///{db_path}"
