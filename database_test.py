import csv

import psycopg2


def postgres():
    return psycopg2.connect(database="mwcertlocal",
                            user="postgres",
                            host="localhost",
                            password="mwcertlocal",
                            port="5430")


def show_data():
    with postgres() as con:
        with con.cursor() as cur:
            cur.execute("SELECT id FROM users WHERE main_email = 'erik@example.de'")
            row = cur.fetchone()
            print("User Id:")
            for user in row:
                print(user)

            user_id = row[0]
            cur.execute("SELECT * FROM certificates WHERE user_id = %s", (user_id,))
            certificates = cur.fetchall()
            print("\nCertificates:")
            for cert in certificates:
                print(cert)


def delete_data():
    with postgres() as con:
        with con.cursor() as cur:
            cur.execute("DELETE FROM certificates")
            cur.execute("DELETE FROM users")
            print("Data deleted successfully")
        con.commit()


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


def insert_csv(path_to_csv: str):
    with postgres() as con:
        with con.cursor() as cur:
            with open(path_to_csv, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f, delimiter=';')

                for row in reader:
                    name = row['name']
                    email = row['email']
                    course_name = row['course_name']
                    user_id = get_or_create_user_id(cur, email, None)

                    cur.execute(
                        """
                        INSERT INTO certificates (name, email, course_name, created_at, user_id) 
                        VALUES (%s, %s, %s, NOW(), %s)
                        """,
                        (name, email, course_name, user_id)
                    )

if __name__ == "__main__":
    delete_data()
    #insert_csv('data.csv')
    #show_data()
