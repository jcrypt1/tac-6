"""
Tests for CSV export endpoints
"""

import pytest
import sqlite3
import tempfile
import os
import shutil
from fastapi.testclient import TestClient


@pytest.fixture
def test_db_setup():
    """Create a test database with sample data in the expected location"""
    # Create db directory
    os.makedirs("db", exist_ok=True)

    # Backup existing database if it exists
    db_path = "db/database.db"
    backup_path = None
    if os.path.exists(db_path):
        backup_path = "db/database.db.bak"
        shutil.copy(db_path, backup_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create test tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS test_users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT,
            age INTEGER
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS test_empty_table (
            id INTEGER PRIMARY KEY,
            name TEXT
        )
    ''')

    # Clear and insert test data
    cursor.execute("DELETE FROM test_users")
    cursor.execute("INSERT INTO test_users (name, email, age) VALUES (?, ?, ?)",
                   ('Alice', 'alice@example.com', 30))
    cursor.execute("INSERT INTO test_users (name, email, age) VALUES (?, ?, ?)",
                   ('Bob', 'bob@example.com', 25))
    cursor.execute("INSERT INTO test_users (name, email, age) VALUES (?, ?, ?)",
                   ('Charlie, Jr.', 'charlie@example.com', 35))  # Name with comma

    conn.commit()
    conn.close()

    yield db_path

    # Cleanup - restore original database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS test_users")
    cursor.execute("DROP TABLE IF EXISTS test_empty_table")
    conn.commit()
    conn.close()

    if backup_path and os.path.exists(backup_path):
        shutil.move(backup_path, db_path)


@pytest.fixture
def client():
    """Create a test client"""
    from server import app
    return TestClient(app)


class TestTableExport:
    """Test table export endpoint"""

    def test_export_table_valid(self, test_db_setup, client):
        """Test exporting a valid table"""
        response = client.get("/api/export/table/test_users")

        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"
        assert 'attachment; filename="test_users.csv"' in response.headers["content-disposition"]

        # Parse CSV content (strip \r for cross-platform compatibility)
        content = response.text.replace('\r', '')
        lines = content.strip().split('\n')

        # Check header
        assert lines[0] == "id,name,email,age"

        # Check we have data rows
        assert len(lines) == 4  # header + 3 data rows

    def test_export_table_not_found(self, client):
        """Test exporting a non-existent table"""
        response = client.get("/api/export/table/nonexistent_table_xyz")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_export_table_invalid_name(self, client):
        """Test exporting with invalid table name"""
        response = client.get("/api/export/table/users'; DROP TABLE users; --")

        assert response.status_code == 400

    def test_export_empty_table(self, test_db_setup, client):
        """Test exporting an empty table"""
        response = client.get("/api/export/table/test_empty_table")

        assert response.status_code == 200

        # Parse CSV content (strip \r for cross-platform compatibility)
        content = response.text.replace('\r', '')
        lines = content.strip().split('\n')

        # Should have header row only
        assert len(lines) == 1
        assert lines[0] == "id,name"

    def test_export_table_csv_escaping(self, test_db_setup, client):
        """Test that CSV properly escapes special characters"""
        response = client.get("/api/export/table/test_users")

        assert response.status_code == 200
        content = response.text

        # The name "Charlie, Jr." contains a comma, so it should be quoted
        assert '"Charlie, Jr."' in content


class TestResultsExport:
    """Test results export endpoint"""

    def test_export_results_valid(self, client):
        """Test exporting valid results"""
        request_data = {
            "columns": ["id", "name", "email"],
            "results": [
                {"id": 1, "name": "Alice", "email": "alice@example.com"},
                {"id": 2, "name": "Bob", "email": "bob@example.com"}
            ]
        }

        response = client.post("/api/export/results", json=request_data)

        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"
        assert 'attachment; filename="query_results.csv"' in response.headers["content-disposition"]

        # Parse CSV content (strip \r for cross-platform compatibility)
        content = response.text.replace('\r', '')
        lines = content.strip().split('\n')

        # Check header
        assert lines[0] == "id,name,email"

        # Check data rows
        assert len(lines) == 3  # header + 2 data rows

    def test_export_results_empty(self, client):
        """Test exporting empty results"""
        request_data = {
            "columns": ["id", "name"],
            "results": []
        }

        response = client.post("/api/export/results", json=request_data)

        assert response.status_code == 200

        # Parse CSV content (strip \r for cross-platform compatibility)
        content = response.text.replace('\r', '')
        lines = content.strip().split('\n')

        # Should have header row only
        assert len(lines) == 1
        assert lines[0] == "id,name"

    def test_export_results_special_characters(self, client):
        """Test CSV escaping with special characters"""
        request_data = {
            "columns": ["id", "name", "notes"],
            "results": [
                {"id": 1, "name": "Alice, Bob", "notes": 'Has "quotes"'},
                {"id": 2, "name": "Charlie\nNewline", "notes": "Normal"}
            ]
        }

        response = client.post("/api/export/results", json=request_data)

        assert response.status_code == 200
        content = response.text

        # Check that commas are properly escaped (field should be quoted)
        assert '"Alice, Bob"' in content
        # Check that quotes are properly escaped (doubled)
        assert '"Has ""quotes"""' in content

    def test_export_results_missing_column(self, client):
        """Test exporting results where a row is missing a column value"""
        request_data = {
            "columns": ["id", "name", "email"],
            "results": [
                {"id": 1, "name": "Alice"},  # Missing email
                {"id": 2, "name": "Bob", "email": "bob@example.com"}
            ]
        }

        response = client.post("/api/export/results", json=request_data)

        assert response.status_code == 200
        content = response.text.replace('\r', '')
        lines = content.strip().split('\n')

        # First data row should have empty email
        assert lines[1] == "1,Alice,"
