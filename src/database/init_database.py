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
                    main_email  varchar(255) unique,
                    alias_email varchar(255) unique,
                    created_at  timestamp default now()
                );
            """)

            cur.execute("""
                create table if not exists public.admins (
                    id serial primary key,
                    name varchar(255),
                    email  varchar(255) unique,
                    affiliation varchar(255),
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
                    logo_path varchar(255),

                    user_id  integer,
                    admin_id integer,

                    constraint certificates_users_id_fk
                        foreign key (user_id) references public.users(id),

                    constraint certificates_admins_id_fk
                        foreign key (admin_id) references public.admins(id)
                );
            """)

        con.commit()
