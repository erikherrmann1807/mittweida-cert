from typing import Optional

from src.auth.otp_database.init_database import sqlitedb


def save_otp(email: str, code_hash: str, now_ts: int, exp_ts: int):
    with sqlitedb() as con:
        con.execute("""
        INSERT INTO email_otps(email, code_hash, created_at, expires_at, attempts, last_sent_at)
        VALUES (?, ?, ?, ?, 0, ?)
        ON CONFLICT(email) DO UPDATE SET
            code_hash=excluded.code_hash,
            created_at=excluded.created_at,
            expires_at=excluded.expires_at,
            attempts=0,
            last_sent_at=excluded.last_sent_at
        """, (email, code_hash, now_ts, exp_ts, now_ts))
        con.commit()


def load_otp(email: str) -> Optional[dict]:
    with sqlitedb() as con:
        cur = con.execute(
            "SELECT code_hash, created_at, expires_at, attempts, last_sent_at FROM email_otps WHERE email = ?",
            (email,))
        row = cur.fetchone()
        if not row:
            return None
        return dict(code_hash=row[0], created_at=row[1], expires_at=row[2], attempts=row[3], last_sent_at=row[4])


def inc_attempt(email: str):
    with sqlitedb() as con:
        con.execute("UPDATE email_otps SET attempts = attempts + 1 WHERE email = ?", (email,))
        con.commit()


def delete_otp(email: str):
    with sqlitedb() as con:
        con.execute("DELETE FROM email_otps WHERE email = ?", (email,))
        con.commit()