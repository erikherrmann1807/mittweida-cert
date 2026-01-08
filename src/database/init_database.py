import psycopg2
from src.database.database_config import *


def postgres():
    return psycopg2.connect(
        database=DB,
        user=DB_USER,
        host=DB_HOST,
        password=DB_PASSWORD,
        port=DB_PORT,
    )


def init_database():
    with postgres() as con:
        with con.cursor() as cur:
            cur.execute("""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM pg_type WHERE typname = 'template_type'
                ) THEN
                    CREATE TYPE template_type AS ENUM ('default', 'custom');
                END IF;
            END $$;
            """)

            cur.execute("""
                create table if not exists public.users (
                    id serial primary key,
                    main_email  varchar(255) unique,
                    alias_email varchar(255) unique,
                    created_at  timestamp default now()
                );
            """)

            cur.execute("""
                create table if not exists public.admins (
                    id serial primary key,
                    name varchar(255),
                    email varchar(255) unique,
                    affiliation varchar(255),
                    created_at timestamp default now()
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
                    template template_type,
                    logo_path varchar(255),

                    user_id  integer,
                    admin_id integer,

                    constraint certificates_users_id_fk
                        foreign key (user_id) references public.users(id),
                    constraint certificates_admins_id_fk
                        foreign key (admin_id) references public.admins(id)
                );
            """)

            cur.execute("""
                CREATE OR REPLACE FUNCTION sync_user_email_from_cert()
                RETURNS trigger AS $$
                BEGIN
                    IF NEW.email IS DISTINCT FROM OLD.email THEN
                        UPDATE public.users
                        SET main_email = NEW.email
                        WHERE id = NEW.user_id;
                    END IF;
                    RETURN NEW;
                END;
                $$ LANGUAGE plpgsql;
            """)

            cur.execute("""
                DROP TRIGGER IF EXISTS trg_sync_user_email_from_cert
                ON public.certificates;
            """)

            cur.execute("""
                CREATE TRIGGER trg_sync_user_email_from_cert
                BEFORE UPDATE OF email ON public.certificates
                FOR EACH ROW
                EXECUTE FUNCTION sync_user_email_from_cert();
            """)

        con.commit()
