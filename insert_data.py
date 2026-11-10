
import sqlite3

from database import connect_database, create_tables


def insert_sample_data(connection: sqlite3.Connection) -> None:
    """Insert sample departments and employees."""
    departments = ["Бухгалтерия", "Разработка"]

    for name in departments:
        connection.execute(
            "INSERT OR IGNORE INTO departments (name) VALUES (?)",
            (name,)
        )

    employees = [
        ("Анна", "Бухгалтерия", 50000),
        ("Иван", "Разработка", 65000),
        ("Мария", "Бухгалтерия", 55000),
    ]

    for name, department, salary in employees:
        row = connection.execute(
            "SELECT id FROM departments WHERE name = ?",
            (department,)
        ).fetchone()

        if row is None:
            raise ValueError(f"Отдел не найден: {department}")

        department_id = row["id"]

        connection.execute(
            """
            INSERT INTO employees (name, department_id, salary)
            SELECT ?, ?, ?
            WHERE NOT EXISTS (
                SELECT 1 FROM employees
                WHERE name = ? AND department_id = ?
            )
            """,
            (name, department_id, salary, name, department_id)
        )

    connection.commit()


def main() -> None:
    """Insert sample data and display employees."""
    connection = connect_database()

    try:
        create_tables(connection)
        insert_sample_data(connection)

        employees = connection.execute(
            "SELECT id, name, department_id, salary "
            "FROM employees ORDER BY id"
        ).fetchall()

        for employee in employees:
            print(
                f"{employee['id']}. {employee['name']} | "
                f"Отдел: {employee['department_id']} | "
                f"Зарплата: {employee['salary']:.0f}"
            )
    finally:
        connection.close()


if __name__ == "__main__":
    main()
