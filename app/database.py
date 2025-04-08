import os
import time
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import logging
from typing import Optional

load_dotenv()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class DatabaseConnectionError(Exception):
    """Custom exception for database connection failures."""
    pass


def get_db_connection(
    max_retries: int = 12,  # 12 retries
    retry_delay: int = 5,  # 5 seconds between retries
) -> mysql.connector.MySQLConnection:
    """Create database connection with retry mechanism."""
    connection: Optional[mysql.connector.MySQLConnection] = None
    attempt = 1
    last_error = None

    while attempt <= max_retries:
        try:
            connection = mysql.connector.connect(
                host=os.getenv("MYSQL_HOST"),
                # port=os.getenv('MYSQL_PORT'),
                user=os.getenv("MYSQL_USER"),
                password=os.getenv("MYSQL_PASSWORD"),
                database=os.getenv("MYSQL_DATABASE"),
            #    ssl_ca=os.getenv('MYSQL_SSL_CA')  # Path to CA certificate file
            )

            # Test the connection
            connection.ping(reconnect=True, attempts=1, delay=0)
            logger.info("Database connection established successfully")
            return connection

        except Error as err:
            last_error = err
            logger.warning(
                f"Connection attempt {attempt}/{max_retries} failed: {err}. "
                f"Retrying in {retry_delay} seconds..."
            )

            if connection is not None:
                try:
                    connection.close()
                except Exception:
                    pass

            if attempt == max_retries:
                break

            time.sleep(retry_delay)
            attempt += 1

    raise DatabaseConnectionError(
        f"Failed to connect to database after {max_retries} attempts. "
        f"Last error: {last_error}"
    )
    

async def setup_database():
    """Creates users, devices, wardrobe, and sessions tables."""

    # Define table schemas
    table_schemas = {
        "students": """
            CREATE TABLE IF NOT EXISTS users (
                user_id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                depth VARCHAR(100) NOT NULL UNIQUE,
                grad_year VARCHAR(100) NOT NULL,
                quote VARCHAR(100) DEFAULT NULL,
                linkedin VARCHAR(100) DEFAULT NULL,
                github VARCHAR(100) DEFAULT NULL,
                insta VARCHAR(100) DEFAULT NULL,
                discord VARCHAR(100) DEFAULT NULL
            )
        """,
    }

    # Connect to the database
    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        if not connection:
            raise Exception("Database connection failed")

        cursor = connection.cursor()

        # Create tables
        for table_name, table_query in table_schemas.items():
            cursor.execute(table_query)
            logger.info(f"Table '{table_name}' checked/created successfully.")

        connection.commit()  # Commit all changes

    except Exception as e:
        logger.error(f"Database setup failed: {e}")
        raise  # Rethrow exception to avoid silent failure

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
            logger.info("Database connection closed")