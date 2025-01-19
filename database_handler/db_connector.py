import logging
import psycopg2

from pymongo import MongoClient
from config import Config

logger = logging.getLogger(__name__)


def get_mongo_client(mongo_uri=f"mongodb://{Config.MONGO_IP}:27017"):
    """
    Get a MongoDB client.

    Args:
        mongo_uri (str): MongoDB connection string.

    Returns:
        MongoClient: MongoDB client instance.
    """
    try:
        client = MongoClient(mongo_uri)
        logger.info("Connected to MongoDB.")
        return client
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise


def get_postgres_connection(db_name: str):
    """
    Get a PostgreSQL connection.

    Args:
        db_name (str): PostgreSQL database name.
        user (str): Database username.
        password (str): Database password.
        host (str): Database host.
        port (int): Database port.

    Returns:
        connection: PostgreSQL connection instance.
    """
    try:
        conn = psycopg2.connect(
            dbname=Config.POSTGRES_DB,
            user=Config.POSTGRES_USER,
            password=Config.POSTGRES_PASSWORD,
            host=Config.POSTGRES_HOST,
            port=Config.POSTGRES_PORT,
        )
        logger.info(f"Connecting to database: {db_name}")
        logger.info("Connected to PostgreSQL.")
        return conn
    except Exception as e:
        logger.error(f"Failed to connect to PostgreSQL: {e}")
        raise
