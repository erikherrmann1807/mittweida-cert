import pandas as pd

from src.database.init_database import postgres


def set_alias_email(main_email: str, alias_email: str):
    with postgres() as con:
        with con.cursor() as cur:
            cur.execute(
                """
                UPDATE users SET alias_email = %s WHERE main_email = %s
                """,
                (alias_email, main_email)
            )


def check_existing_user(email: str):
    with postgres() as con:
        with con.cursor() as cur:
            cur.execute(
                """
                SELECT 1 FROM users WHERE main_email = %s OR alias_email = %s
                """,
                (email, email)
            )
            user = cur.fetchone()
            if user:
                return True
        return False

def get_or_create_user_id(cur, main_email, alias_email):
    cur.execute(
        "SELECT id FROM users WHERE main_email = %s",
        (main_email,)
    )
    row = cur.fetchone()

    if row:
        return row[0]

    cur.execute(
        """
        INSERT INTO users (main_email, alias_email, created_at)
        VALUES (%s, %s, NOW())
        RETURNING id;
        """,
        (main_email, alias_email)
    )
    return cur.fetchone()[0]


def get_user(cur, email: str):
    cur.execute(
        "SELECT id FROM users WHERE main_email = %s OR alias_email = %s",
        (email, email)
    )
    return cur.fetchone()[0]


def insert_csv(csv_file, institution, logo):
    with postgres() as con:
        with con.cursor() as cur:
            df = pd.read_csv(csv_file[0], sep=';')
            for _, row in df.iterrows():
                name = row['name']
                email = row['email']
                course_name = row['course_name']
                platform = row['platform']
                cert_number = row['cert_number']
                user_id = get_or_create_user_id(cur, email, None)
                cur.execute(
                    """
                    INSERT INTO certificates (name, email, course_name, platform, created_at, cert_number, institution, user_id, logo) 
                    VALUES (%s, %s, %s, %s, NOW(), %s, %s, %s, %s)
                    """,
                    (name, email, course_name, platform, cert_number, institution, user_id, logo)
                )


def get_data_per_user(email: str):
    with postgres() as con:
        with con.cursor() as cur:

            user_id = get_user(cur, email)

            cur.execute("""
            SELECT * FROM certificates WHERE user_id = %s
            """,
            (user_id,)
            )
            return cur.fetchall()