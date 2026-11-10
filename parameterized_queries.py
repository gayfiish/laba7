
import sqlite3

from database import connect_database, create_tables
from insert_data import insert_sample_data


def find_by_name(
    connection: sqlite3.Connection,
    name: str
) -> list[sqlite3.Row]:
    """Find employees by name using a parameterized query."""
    return connection.execute(
        "SELECT id, name, salary FROM employees WHERE name = ?",
        (name,)
    ).fetchall()


def find_by_min_salary(
    connection: sqlite3.Connection,
    min_salary: float
) -> list[sqlite3.Row]:
    """Find employees earning at least the specified salary."""
    return connection.execute(
        "SELECT id, name, salary FROM employees "
        "WHERE salary >= ? ORDER BY salary",
        (min_salary,)
    ).fetchall()


def main() -> None:
    """Demonstrate parameterized SQLite queries."""
    connection = connect_database()

    try:
        create_tables(connection)
        insert_sample_data(connection)

        name = input("Введите имя сотрудника: ").strip()
        employees = find_by_name(connection, name)

        print("\nПоиск по имени:")
        if not employees:
            print("Сотрудники не найдены.")

        for employee in employees:
            print(
                f"{employee['name']} — "
                f"{employee['salary']:.0f} руб."
            )

        try:
            min_salary = float(
                input("\nВведите минимальную зарплату: ")
            )
        except ValueError:
            print("Ошибка: зарплата должна быть числом.")
            return

        if min_salary < 0:
            print("Ошибка: зарплата не может быть отрицательной.")
            return

        employees = find_by_min_salary(connection, min_salary)

        print("\nПоиск по зарплате:")
        if not employees:
            print("Сотрудники не найдены.")

        for employee in employees:
            print(
                f"{employee['name']} — "
                f"{employee['salary']:.0f} руб."
            )
    finally:
        connection.close()


if __name__ == "__main__":
    main()
