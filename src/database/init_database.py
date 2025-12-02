import psycopg2

from src.database.database_config import *


def postgres():
    return psycopg2.connect(database=DB,
                            user=DB_USER,
                            host=DB_HOST,
                            password=DB_PASSWORD,
                            port=DB_PORT)


def init_database():
    with postgres() as con:
        with con.cursor() as cur:
            cur.execute("""
                create table if not exists public.users (
                    id serial primary key,
                    main_email  varchar(255) constraint users_pk unique,
                    alias_email varchar(255) constraint users_pk_2 unique,
                    created_at  timestamp default now()
                );
            """)
            cur.execute("""
                create table if not exists public.certificates (
                    id serial primary key,
                    name varchar(255),
                    email varchar(255),
                    course_name varchar(255),
                    platform varchar(255),
                    created_at timestamp default now(),
                    cert_number varchar(255),
                    institution varchar(255),
                    logo bytea,
                    user_id serial constraint certificates_users_id_fk references public.users
                );
            """)

            cur.execute(
                """
                INSERT INTO users (main_email, alias_email, created_at)
                VALUES (%s, %s, NOW())
                ON CONFLICT (main_email) DO NOTHING;
                """,
                ('admin@example.com', None)
            )