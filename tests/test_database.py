
import sqlite3
from typing import Iterator

import pytest

from database import connect_database, create_tables
from indexing_search import (
    create_name_index,
    get_query_plan,
    search_employee,
)
from insert_data import insert_sample_data
from join_queries import get_employees_with_departments
from parameterized_queries import find_by_min_salary, find_by_name


@pytest.fixture
def connection() -> Iterator[sqlite3.Connection]:
    """Create an isolated in-memory database for each test."""
    db = connect_database(":memory:")

    try:
        create_tables(db)
        insert_sample_data(db)
        yield db
    finally:
        db.close()


def test_tables_created(connection: sqlite3.Connection) -> None:
    """Check that both database tables exist."""
    rows = connection.execute(
        "SELECT name FROM sqlite_master "
        "WHERE type = 'table' "
        "AND name IN ('departments', 'employees')"
    ).fetchall()

    names = {row["name"] for row in rows}
    assert names == {"departments", "employees"}


def test_data_insertion(connection: sqlite3.Connection) -> None:
    """Check that sample records are inserted."""
    employees = connection.execute(
        "SELECT name FROM employees ORDER BY id"
    ).fetchall()

    assert [row["name"] for row in employees] == [
        "Анна", "Иван", "Мария"
    ]


def test_no_duplicate_insertion(
    connection: sqlite3.Connection
) -> None:
    """Check that repeated sample insertion creates no duplicates."""
    insert_sample_data(connection)

    count = connection.execute(
        "SELECT COUNT(*) FROM employees"
    ).fetchone()[0]

    assert count == 3


def test_parameterized_name_search(
    connection: sqlite3.Connection
) -> None:
    """Check searching employees by name."""
    employees = find_by_name(connection, "Анна")

    assert len(employees) == 1
    assert employees[0]["name"] == "Анна"
    assert employees[0]["salary"] == 50000


def test_unknown_employee(
    connection: sqlite3.Connection
) -> None:
    """Check searching for a missing employee."""
    assert find_by_name(connection, "Пётр") == []


def test_sql_injection_protection(
    connection: sqlite3.Connection
) -> None:
    """Check that SQL input is treated as data."""
    malicious_name = "' OR 1=1 --"

    employees = find_by_name(connection, malicious_name)

    assert employees == []


def test_minimum_salary_search(
    connection: sqlite3.Connection
) -> None:
    """Check the minimum salary filter."""
    employees = find_by_min_salary(connection, 55000)

    assert [row["name"] for row in employees] == [
        "Мария", "Иван"
    ]


def test_join_query(connection: sqlite3.Connection) -> None:
    """Check employees joined with their departments."""
    employees = get_employees_with_departments(connection)

    result = [
        (row["name"], row["department"])
        for row in employees
    ]

    assert result == [
        ("Анна", "Бухгалтерия"),
        ("Иван", "Разработка"),
        ("Мария", "Бухгалтерия"),
    ]


def test_index_creation(connection: sqlite3.Connection) -> None:
    """Check that the employee name index is created."""
    create_name_index(connection)

    index = connection.execute(
        "SELECT name FROM sqlite_master "
        "WHERE type = 'index' AND name = ?",
        ("idx_employees_name",)
    ).fetchone()

    assert index is not None


def test_indexed_search(connection: sqlite3.Connection) -> None:
    """Check employee search after creating the index."""
    create_name_index(connection)

    employees = search_employee(connection, "Анна")

    assert len(employees) == 1
    assert employees[0]["name"] == "Анна"


def test_index_query_plan(
    connection: sqlite3.Connection
) -> None:
    """Check index usage in the explicit query plan."""
    create_name_index(connection)

    plan = get_query_plan(connection, "Анна")
    details = " ".join(row["detail"] for row in plan)

    assert "USING INDEX idx_employees_name" in details


def test_foreign_key_constraint(
    connection: sqlite3.Connection
) -> None:
    """Check rejection of an unknown department."""
    with pytest.raises(sqlite3.IntegrityError):
        connection.execute(
            "INSERT INTO employees "
            "(name, department_id, salary) "
            "VALUES (?, ?, ?)",
            ("Тест", 999999, 30000)
        )


def test_negative_salary_constraint(
    connection: sqlite3.Connection
) -> None:
    """Check rejection of negative salaries."""
    with pytest.raises(sqlite3.IntegrityError):
        connection.execute(
            "INSERT INTO employees "
            "(name, department_id, salary) "
            "VALUES (?, ?, ?)",
            ("Тест", 1, -1000)
        )
