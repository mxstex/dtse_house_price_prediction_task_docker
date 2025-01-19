import os
import logging


class Config:
    ENV_LOCAL_DOCKER = "0.0.0.0"  # For docker 0.0.0.0, for local localhost

    # MongoDB Configuration
    MONGO_IP = (
        "mongodb"  # localhost for local debuging / mongodb for dockerized solution
    )
    MONGO_DB_NAME = "housing"
    MONGO_COLLECTION = "data"

    # PostgreSQL Configuration
    POSTGRES_DB = "predictions"
    POSTGRES_table = "predictions"
    POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_HOST = os.getenv(
        "POSTGRES_HOST", "postgresdb"
    )  # Default host: localhost / postgresdb
    POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", 5432))

    # File Paths
    DATA_FILE = os.path.join("data", "housing.csv")
    MODEL_FILE = os.path.join("models", "model.joblib")
    PREDICTIONS_FILE = "predictions.csv"

    # Expected Features for Model
    EXPECTED_FEATURES = [
        "longitude",
        "latitude",
        "housing_median_age",
        "total_rooms",
        "total_bedrooms",
        "population",
        "households",
        "median_income",
        "ocean_proximity__LT_1H_OCEAN",
        "ocean_proximity_INLAND",
        "ocean_proximity_ISLAND",
        "ocean_proximity_NEAR_BAY",
        "ocean_proximity_NEAR_OCEAN",
    ]

    # Logging Configuration
    LOG_FILE = os.getenv("LOG_FILE", "app.log")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG").upper()

    @staticmethod
    def setup_logger():
        logger = logging.getLogger(__name__)

        # Check if the logger already has handlers
        if not logger.hasHandlers():
            logger.setLevel(Config.LOG_LEVEL)

            # File Handler
            file_handler = logging.FileHandler(Config.LOG_FILE)
            file_handler.setLevel(Config.LOG_LEVEL)
            file_formatter = logging.Formatter(
                "%(asctime)s - %(levelname)s - %(message)s"
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)

            # Console Handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(Config.LOG_LEVEL)
            console_formatter = logging.Formatter(
                "%(asctime)s - %(levelname)s - %(message)s"
            )
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)

        return logger


# Initialize the logger
logger = Config.setup_logger()
