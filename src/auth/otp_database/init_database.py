import sqlite3

from src.auth.otp_mail.config import DB_PATH


def sqlitedb():
    return sqlite3.connect(DB_PATH)


def init_sqlitedb():
    with sqlitedb() as con:
        con.execute("""
        CREATE TABLE IF NOT EXISTS email_otps (
            email TEXT PRIMARY KEY,
            code_hash TEXT NOT NULL,
            created_at INTEGER NOT NULL,
            expires_at INTEGER NOT NULL,
            attempts INTEGER NOT NULL DEFAULT 0,
            last_sent_at INTEGER NOT NULL
        )
        """)
        con.commit()