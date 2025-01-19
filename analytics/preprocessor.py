import pandas as pd
from typing import Tuple
from config import logger, Config


def preprocess_housing_data(input_data_path: str) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Preprocess the housing data to prepare it for model training or inference.

    Args:
        input_data_path (str): Path to the input CSV file.

    Returns:
        Tuple[pd.DataFrame, pd.Series]: Processed features (X) and target (y).

    Raises:
        FileNotFoundError: If the input file is not found.
        ValueError: If the target column is missing or the file format is invalid.
    """
    logger.info(f"Starting preprocessing for file: {input_data_path}")

    # Step 1: Load the data
    try:
        df = pd.read_csv(input_data_path)
        logger.info(
            f"File '{input_data_path}' loaded successfully. Data shape: {df.shape}"
        )
    except FileNotFoundError:
        logger.error(f"Input file not found at path: {input_data_path}")
        raise
    except pd.errors.ParserError:
        logger.error(f"Invalid file format for file: {input_data_path}")
        raise ValueError(f"Invalid file format for file: {input_data_path}")
    except Exception as e:
        logger.error(f"Error loading file '{input_data_path}': {e}")
        raise

    # Step 2: Validate minimum columns
    if df.shape[1] < 2:
        logger.error(f"Insufficient columns in file: {input_data_path}")
        raise ValueError(f"Insufficient columns in file: {input_data_path}")

    # Step 3: Normalize column names
    df.columns = df.columns.str.lower()
    logger.debug(f"Normalized column names: {list(df.columns)}")

    # Step 4: Rename columns for consistency
    column_renames = {
        "lat": "latitude",
        "bedrooms": "total_bedrooms",
        "median_age": "housing_median_age",
        "pop": "population",
        "rooms": "total_rooms",
    }
    df.rename(columns=column_renames, inplace=True)
    logger.debug(f"Renamed columns: {list(df.columns)}")

    # Step 5: Encode categorical variables
    if "ocean_proximity" in df.columns:
        df = pd.get_dummies(df, columns=["ocean_proximity"], drop_first=False)
        logger.debug(
            f"Encoded 'ocean_proximity' column. Current columns: {list(df.columns)}"
        )
    else:
        logger.warning("'ocean_proximity' column not found. Skipping encoding.")

    # Step 6: Handle missing or unexpected values
    df.replace("Null", 0, inplace=True)
    df.fillna(0, inplace=True)
    logger.debug(
        "Handled missing and unexpected values (replaced 'Null', filled NaNs)."
    )

    # Step 7: Validate target column
    target = "median_house_value"
    if target not in df.columns:
        logger.error(f"Target column '{target}' not found in the dataset.")
        raise ValueError(f"Target column '{target}' not found in the dataset.")

    # Step 8: Separate features and target
    y = df[target]
    X = df.drop(columns=[target])
    logger.info(
        f"Separated target column '{target}'. Features shape: {X.shape}, Target shape: {y.shape}"
    )

    # Step 9: Align features with the expected schema
    for col in Config.EXPECTED_FEATURES:
        if col not in X.columns:
            X[col] = 0  # Add missing columns as 0
            logger.debug(f"Added missing column '{col}' with default value 0.")
    X = X[Config.EXPECTED_FEATURES]
    logger.info(f"Aligned features with the expected schema. Final shape: {X.shape}")

    logger.info("Data preprocessing completed successfully.")
    return X, y
