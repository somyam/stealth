import psycopg2
from psycopg2 import sql

def create_database_and_user(dbname, user, password):
    # Connect to the default database (postgres)
    conn = psycopg2.connect(
    database="postgres",
        user='postgres',
        password='password',
        host='localhost',
        port= '5432'
    )
    conn.autocommit = True  # Ensure that the commands are committed without having to call conn.commit()

    try:
        cur = conn.cursor()
        # cur.execute(sql.SQL("CREATE USER {} WITH PASSWORD %s").format(sql.Identifier(user)), [password])
        cur.execute(sql.SQL("CREATE DATABASE {} OWNER {}").format(
            sql.Identifier(dbname),
            sql.Identifier(user)
        ))

        print("Database and user created successfully")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        cur.close()
        conn.close()

create_database_and_user("discord", "somyam", "ilovediscord")