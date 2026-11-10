
import sqlite3

DATABASE_FILE = "company.db"


def connect_database(
    database_path: str = DATABASE_FILE
) -> sqlite3.Connection:
    """Connect to the SQLite database."""
    connection = sqlite3.connect(database_path)
    connection.execute("PRAGMA foreign_keys = ON")
    connection.row_factory = sqlite3.Row
    return connection


def create_tables(connection: sqlite3.Connection) -> None:
    """Create departments and employees tables."""
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS departments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
        """
    )

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            department_id INTEGER NOT NULL,
            salary REAL NOT NULL CHECK (salary >= 0),
            FOREIGN KEY (department_id) REFERENCES departments(id)
        )
        """
    )

    connection.commit()


if __name__ == "__main__":
    connection = connect_database()

    try:
        create_tables(connection)

        tables = connection.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type = 'table' "
            "AND name IN ('departments', 'employees') "
            "ORDER BY name"
        ).fetchall()

        for table in tables:
            print("Таблица:", table["name"])
    finally:
        connection.close()
