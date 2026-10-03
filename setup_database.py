from pathlib import Path

import mysql.connector

from database import database_config


def main():
    script = Path("Database.sql").read_text(encoding="utf-8-sig")
    connection = mysql.connector.connect(**database_config(include_database=False))
    cursor = connection.cursor()
    try:
        for statement in script.split(";"):
            if statement.strip():
                cursor.execute(statement)
        connection.commit()
        print("StudentHub database is ready.")
    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    main()
