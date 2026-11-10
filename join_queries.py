
import sqlite3

from database import connect_database, create_tables
from insert_data import insert_sample_data


def get_employees_with_departments(
    connection: sqlite3.Connection
) -> list[sqlite3.Row]:
    """Get employees with their department names using JOIN."""
    return connection.execute(
        """
        SELECT
            e.id,
            e.name,
            d.name AS department,
            e.salary
        FROM employees AS e
        INNER JOIN departments AS d
            ON e.department_id = d.id
        ORDER BY e.id
        """
    ).fetchall()


def main() -> None:
    """Display employees and their departments."""
    connection = connect_database()

    try:
        create_tables(connection)
        insert_sample_data(connection)

        employees = get_employees_with_departments(connection)

        if not employees:
            print("Сотрудники не найдены.")
            return

        for employee in employees:
            print(
                f"{employee['id']}. {employee['name']} | "
                f"Отдел: {employee['department']} | "
                f"Зарплата: {employee['salary']:.0f} руб."
            )
    finally:
        connection.close()


if __name__ == "__main__":
    main()
