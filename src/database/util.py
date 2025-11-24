from src.database.init_database import postgres


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

        con.commit()