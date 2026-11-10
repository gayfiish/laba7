
import sqlite3

from database import connect_database, create_tables
from insert_data import insert_sample_data


def create_name_index(connection: sqlite3.Connection) -> None:
    """Create an index for searching employees by name."""
    connection.execute(
        "CREATE INDEX IF NOT EXISTS idx_employees_name "
        "ON employees(name)"
    )
    connection.commit()


def search_employee(
    connection: sqlite3.Connection,
    name: str
) -> list[sqlite3.Row]:
    """Search for employees using a parameterized query."""
    return connection.execute(
        "SELECT id, name, salary FROM employees WHERE name = ?",
        (name,)
    ).fetchall()


def get_query_plan(
    connection: sqlite3.Connection,
    name: str
) -> list[sqlite3.Row]:
    """Return the SQLite query execution plan."""
    return connection.execute(
        """
        EXPLAIN QUERY PLAN
        SELECT id, name, salary
        FROM employees INDEXED BY idx_employees_name
        WHERE name = ?
        """,
        (name,)
    ).fetchall()


def main() -> None:
    """Demonstrate indexing and employee search."""
    connection = connect_database()

    try:
        create_tables(connection)
        insert_sample_data(connection)
        create_name_index(connection)

        name = input("Введите имя сотрудника: ").strip().capitalize()

        if not name:
            print("Ошибка: имя не может быть пустым.")
            return

        employees = search_employee(connection, name)

        print("\nРезультаты поиска:")

        if not employees:
            print("Сотрудники не найдены.")

        for employee in employees:
            print(
                f"{employee['id']}. {employee['name']} | "
                f"Зарплата: {employee['salary']:.0f} руб."
            )

        print("\nПлан выполнения запроса:")

        for row in get_query_plan(connection, name):
            print(row["detail"])
    finally:
        connection.close()


if __name__ == "__main__":
    main()
