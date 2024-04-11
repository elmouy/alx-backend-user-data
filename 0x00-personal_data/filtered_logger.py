#!/usr/bin/env python3
"""
Main file
"""

import os
import logging
import mysql.connector

PII_FIELDS = ("name", "email", "phone", "ssn", "password")


class RedactingFormatter(logging.Formatter):
    """ Redacting Formatter class """

    REDACTION = "***"
    FORMAT = "[HOLBERTON] %(name)s %(levelname)s %(asctime)-15s: %(message)s"
    SEPARATOR = ";"

    def __init__(self, fields):
        """ Initialize """
        super().__init__(self.FORMAT)
        self.fields = fields

    def format(self, record):
        """ Format record """
        return filter_datum(self.fields, self.REDACTION,
                            super().format(record), self.SEPARATOR)


def filter_datum(fields, redaction, message, separator):
    """ Obfuscate sensitive data """
    return re.sub(
        r"(\w+)=([a-zA-Z0-9@\.\-\(\)\ \:\^\<\>\~\$\%\@\?\!\/]*)",
        lambda match: match.group(1) + "=" + redaction
        if match.group(1) in fields else match.group(0), message)


def get_logger():
    """ Return a logger object """
    logger = logging.getLogger("user_data")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    sh = logging.StreamHandler()
    sh.setFormatter(RedactingFormatter(PII_FIELDS))
    logger.addHandler(sh)
    return logger


def get_db():
    """ Connect to MySQL database """
    return mysql.connector.connect(
        host=os.getenv("PERSONAL_DATA_DB_HOST", "localhost"),
        database=os.getenv("PERSONAL_DATA_DB_NAME"),
        user=os.getenv("PERSONAL_DATA_DB_USERNAME", "root"),
        password=os.getenv("PERSONAL_DATA_DB_PASSWORD", ""),
    )


def main():
    """ Main function """
    logger = get_logger()
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT COUNT(*) FROM users;")
        result = cursor.fetchone()[0]
        logger.info("Total users in the database: %d", result)
    except mysql.connector.Error as err:
        logger.error("Error accessing database: %s", err)
    finally:
        if 'db' in locals() and db.is_connected():
            cursor.close()
            db.close()


if __name__ == "__main__":
    main()
