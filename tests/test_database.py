import sqlite3
from pathlib import Path

import pytest

SCHEMA = Path("database/schema.sql")


@pytest.fixture
def db(tmp_path):
    conn = sqlite3.connect(tmp_path / "test.db")
    conn.execute("PRAGMA foreign_keys = ON")

    conn.executescript(
        SCHEMA.read_text(encoding="utf-8")
    )

    yield conn

    conn.close()


def test_tables_created(db):
    tables = db.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()

    table_names = [row[0] for row in tables]

    assert "users" in table_names
    assert "items" in table_names
    assert "claims" in table_names
    assert "notifications" in table_names
    assert "recovery_history" in table_names


def test_user_insertion(db):
    db.execute(
        "INSERT INTO users(name,email,password_hash) VALUES(?,?,?)",
        ("Test User", "test@example.com", "dummy_hash")
    )

    user = db.execute(
        "SELECT * FROM users WHERE email=?",
        ("test@example.com",)
    ).fetchone()

    assert user is not None
    assert user[1] == "Test User"


def test_item_insertion(db):
    db.execute(
        "INSERT INTO users(name,email,password_hash) VALUES(?,?,?)",
        ("Test User", "user@example.com", "dummy_hash")
    )

    db.execute(
        """INSERT INTO items
        (user_id,item_name,item_type)
        VALUES(?,?,?)""",
        (1, "Black Wallet", "lost")
    )

    item = db.execute(
        "SELECT item_name FROM items"
    ).fetchone()

    assert item[0] == "Black Wallet"


def test_duplicate_email_rejected(db):
    db.execute(
        "INSERT INTO users(name,email,password_hash) VALUES(?,?,?)",
        ("User One", "same@example.com", "hash")
    )

    with pytest.raises(sqlite3.IntegrityError):
        db.execute(
            "INSERT INTO users(name,email,password_hash) VALUES(?,?,?)",
            ("User Two", "same@example.com", "hash")
        )


def test_invalid_user_reference_rejected(db):
    with pytest.raises(sqlite3.IntegrityError):
        db.execute(
            """INSERT INTO items(user_id,item_name,item_type)
            VALUES(?,?,?)""",
            (999, "Phone", "lost")
        )
