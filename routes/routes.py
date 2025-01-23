from fastapi import HTTPException, APIRouter, UploadFile, File
from pymongo import MongoClient
import pandas as pd
from analytics.preprocessor import preprocess_housing_data
from database_handler.db_connector import get_postgres_connection, get_mongo_client
from database_handler.db_queries import (
    insert_data_to_mongo,
    delete_all_from_mongo,
    save_to_postgres,
    fetch_predictions,
)
from config import Config
import joblib
from datetime import datetime
from fastapi.encoders import jsonable_encoder

logger = Config.setup_logger()
router = APIRouter()


@router.post("/upload")
async def upload_data(
    file: UploadFile = File(...),
    db_name: str = Config.MONGO_DB_NAME,
    collection_name: str = Config.MONGO_COLLECTION,
):
    logger.info(f"Received upload request for file: {file.filename}")
    logger.info(f"Target database: {db_name}, collection: {collection_name}")

    try:
        # Load the file content
        content = await file.read()
        logger.info(
            f"File '{file.filename}' read successfully. Size: {len(content)} bytes"
        )

        # Save the file temporarily
        temp_file_path = f"temp_{file.filename}"
        with open(temp_file_path, "wb") as f:
            f.write(content)

        # Preprocess data
        logger.info(f"Starting data preprocessing for file: {temp_file_path}")
        X, y = preprocess_housing_data(temp_file_path)
        logger.info(
            f"Data preprocessing completed. Features shape: {X.shape}, Target shape: {y.shape}"
        )

        # Combine features and target into a list of dictionaries
        processed_data = X.assign(target=y).to_dict(orient="records")
        logger.info(
            f"Processed data formatted for MongoDB. Total records: {len(processed_data)}"
        )

        # Insert into MongoDB
        logger.info(
            f"Inserting processed data into MongoDB: {db_name}.{collection_name}"
        )
        insert_data_to_mongo(processed_data, db_name, collection_name)
        logger.info(f"Data successfully inserted into {db_name}.{collection_name}")

        # Clean up the temporary file
        import os

        os.remove(temp_file_path)
        logger.info(f"Temporary file '{temp_file_path}' deleted.")

        return {"message": "Data uploaded and stored successfully."}

    except HTTPException as http_err:
        logger.error(f"HTTP Exception: {http_err.detail}")
        raise http_err
    except Exception as e:
        logger.error(f"Unexpected error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal server error.")


@router.delete("/delete_mongodb/")
async def delete_mongodb(
    db_name: str = Config.MONGO_DB_NAME, collection_name: str = Config.MONGO_COLLECTION
):
    logger.info(
        f"Received request to delete all documents from {db_name}.{collection_name}"
    )
    try:
        delete_all_from_mongo(db_name, collection_name)
        logger.info(f"All documents deleted from {db_name}.{collection_name}")
        return {
            "message": f"All documents in {db_name}.{collection_name} have been deleted successfully."
        }
    except Exception as e:
        logger.error(f"Error deleting documents from {db_name}.{collection_name}: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to delete documents from MongoDB."
        )


@router.get("/raw_data")
async def get_data(
    db_name: str = Config.MONGO_DB_NAME,
    collection_name: str = Config.MONGO_COLLECTION,
    skip: int = 0,
    limit: int = 10,
):
    try:
        client = get_mongo_client()
        # client = MongoClient(f"mongodb://{Config.MONGO_IP}:27017")
        db = client[db_name]
        collection = db[collection_name]

        data = list(collection.find().skip(skip).limit(limit))
        for document in data:
            if "_id" in document:
                document["_id"] = str(document["_id"])

        total = collection.count_documents({})
        client.close()
        return {"data": data, "skip": skip, "limit": limit, "total": total}
    except Exception as e:
        logger.error(f"Error in /raw_data endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    logger.info("Performing health check")
    try:
        client = get_mongo_client()
        # client = MongoClient(f"mongodb://{Config.MONGO_IP}:27017")
        client.admin.command("ping")
        client.close()
        return {"status": "healthy"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Service unhealthy.")


@router.get("/process")
async def process_data(
    db_name: str = Config.MONGO_DB_NAME,
    collection_name: str = Config.MONGO_COLLECTION,
):
    logger.info(f"Starting data processing for {db_name}.{collection_name}")
    try:
        client = get_mongo_client()
        # client = MongoClient(f"mongodb://{Config.MONGO_IP}:27017")
        db = client[db_name]
        collection = db[collection_name]

        data = list(collection.find())
        client.close()

        if not data:
            logger.error("No data found in the collection.")
            raise HTTPException(
                status_code=404, detail="No data found in the collection."
            )

        df = pd.DataFrame(data)
        if "_id" in df.columns:
            df.drop(columns=["_id"], inplace=True)

        missing_cols = [
            col for col in Config.EXPECTED_FEATURES if col not in df.columns
        ]
        for col in missing_cols:
            df[col] = 0
        df = df[Config.EXPECTED_FEATURES]

        logger.info(f"Loading model from {Config.MODEL_FILE}")
        model = joblib.load(Config.MODEL_FILE)

        logger.info("Generating predictions...")
        predictions = model.predict(df)

        df["predictions"] = predictions
        df["prediction_timestamp"] = datetime.now()

        logger.info("Saving predictions to PostgreSQL...")
        save_to_postgres(df, Config.POSTGRES_DB, Config.POSTGRES_table)
        logger.info("Predictions saved to PostgreSQL successfully.")

        return {"message": "Data processed and stored successfully in PostgreSQL."}

    except FileNotFoundError:
        logger.error("Model file not found.")
        raise HTTPException(status_code=500, detail="Model file not found.")
    except Exception as e:
        logger.error(f"Error during data processing: {e}")
        raise HTTPException(status_code=500, detail="Failed to process data.")


@router.get("/predicted_data/")
async def get_predicted_data(
    skip: int = 0,
    limit: int = 10,
    db_name: str = Config.POSTGRES_DB,
    table_name: str = Config.POSTGRES_table,
):
    """
    Fetch predicted data from PostgreSQL.
    """
    logger.info(f"Fetching predicted data from PostgreSQL table: {table_name}")
    try:
        with get_postgres_connection(db_name=db_name) as conn:
            predicted_data = fetch_predictions(conn, table_name, limit, skip)

        if not predicted_data:
            logger.warning("No predicted data found in the database.")
            raise HTTPException(status_code=404, detail="No predicted data found.")

        # Encode the data to ensure compatibility
        encoded_data = jsonable_encoder(predicted_data)
        logger.info(f"Encoded data: {encoded_data}")

        return {"predicted_data": encoded_data, "skip": skip, "limit": limit}

    except Exception as e:
        logger.error(f"Error fetching predicted data: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch predicted data.")
