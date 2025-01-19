import logging
import pandas as pd
from datetime import datetime

from psycopg2.extras import execute_values
from database_handler.db_connector import get_mongo_client, get_postgres_connection

logger = logging.getLogger(__name__)


# MongoDB Queries
def insert_data_to_mongo(data, db_name, collection_name):
    """
    Inserts preprocessed data into a MongoDB collection.

    Args:
        data (list): List of dictionaries to insert.
        db_name (str): MongoDB database name.
        collection_name (str): MongoDB collection name.
        mongo_uri (str): MongoDB connection string.
    """
    client = get_mongo_client()
    db = client[db_name]
    collection = db[collection_name]

    if data:
        collection.insert_many(data)
        logger.info(f"Inserted {len(data)} records into {db_name}.{collection_name}")

    client.close()


def delete_all_from_mongo(db_name: str, collection_name: str):
    """
    Deletes all documents from the specified MongoDB collection.

    Args:
        db_name (str): MongoDB database name.
        collection_name (str): MongoDB collection name.
    """
    try:
        client = get_mongo_client()
        db = client[db_name]
        collection = db[collection_name]

        # Delete all documents
        result = collection.delete_many({})
        logger.info(
            f"Deleted {result.deleted_count} documents from {db_name}.{collection_name}"
        )
    except Exception as e:
        logger.error(f"Error deleting documents from {db_name}.{collection_name}: {e}")
        raise
    finally:
        client.close()


# PostgreSQL Queries
def save_to_postgres(df: pd.DataFrame, db_name: str, table_name: str):
    """
    Save a DataFrame to a PostgreSQL table with versioning.

    Args:
        df (pd.DataFrame): DataFrame to save.
        db_name (str): PostgreSQL database name.
        table_name (str): Table name.
    """
    try:
        conn = get_postgres_connection(db_name)
        cursor = conn.cursor()

        # Create table if it doesn't exist
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id SERIAL PRIMARY KEY,
            longitude REAL,
            latitude REAL,
            housing_median_age REAL,
            total_rooms REAL,
            total_bedrooms REAL,
            population REAL,
            households REAL,
            median_income REAL,
            ocean_proximity__LT_1H_OCEAN REAL,
            ocean_proximity_INLAND REAL,
            ocean_proximity_ISLAND REAL,
            ocean_proximity_NEAR_BAY REAL,
            ocean_proximity_NEAR_OCEAN REAL,
            predictions REAL,
            prediction_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        cursor.execute(create_table_query)
        conn.commit()
        logger.info(f"Table {table_name} created (if not exists).")

        # Prepare data for insertion
        columns = list(df.columns)
        values = [tuple(x) for x in df.to_numpy()]
        insert_query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES %s"

        # Insert data
        execute_values(cursor, insert_query, values)
        conn.commit()
        logger.info(f"Inserted {len(values)} records into {table_name}.")

        # Close the connection
        cursor.close()
        conn.close()

    except Exception as e:
        logger.error(f"Failed to save data to PostgreSQL: {e}")
        raise


def fetch_predictions(conn, table_name: str, limit: int = 10, skip: int = 0):
    """
    Fetch predictions from the PostgreSQL table.
    """
    try:
        cursor = conn.cursor()

        query = f"""
            SELECT * FROM public.{table_name}
            ORDER BY id DESC
            LIMIT {limit} OFFSET {skip};
        """
        logger.debug(f"Executing SQL query:\n{query}")

        cursor.execute(query)
        results = cursor.fetchall()

        if not results:
            logger.warning("No rows fetched from the database.")
        else:
            logger.info(f"Fetched {len(results)} rows from the database {table_name}.")

        # Fetch column names for constructing the result as a dictionary
        columns = [desc[0] for desc in cursor.description]
        predictions = []
        for row in results:
            row_dict = dict(zip(columns, row))
            # Ensure datetime fields are serialized
            for key, value in row_dict.items():
                if isinstance(value, datetime):
                    row_dict[key] = value.isoformat()
            predictions.append(row_dict)

        cursor.close()
        return predictions
    except Exception as e:
        logger.error(f"Error fetching predictions: {e}")
        raise
