import pytest
import pandas as pd
import os
from unittest.mock import patch
from analytics.preprocessor import preprocess_housing_data
from config import Config


@patch("analytics.preprocessor.logger")
def test_preprocess_housing_data_valid(mock_logger):
    # Define the path to the housing.csv file in your project
    csv_path = "tests/data/housing.csv"

    # Read the file and standardize column names to lowercase
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.lower()  # Convert all column names to lowercase

    # Verify unique values in 'ocean_proximity'
    if "ocean_proximity" in df.columns:
        print("Unique values in 'ocean_proximity':", df["ocean_proximity"].unique())
    else:
        raise KeyError("Column 'ocean_proximity' not found in the CSV file")

    # Run the preprocessor
    X, y = preprocess_housing_data(csv_path)

    # Debug logs for verification
    print("Processed Columns:", list(X.columns))
    print("Processed DataFrame:\n", X.head())
    print("Target Series:\n", y.head())

    # Validate the output shapes
    assert X.shape[0] == y.shape[0], "Mismatch between features and target rows"
    assert len(Config.EXPECTED_FEATURES) == len(X.columns), "Feature count mismatch"

    # Validate that all expected features are present
    missing_features = set(Config.EXPECTED_FEATURES) - set(X.columns)
    assert not missing_features, f"Missing features: {missing_features}"

    # Validate that extra columns were not added
    extra_features = set(X.columns) - set(Config.EXPECTED_FEATURES)
    assert not extra_features, f"Unexpected features: {extra_features}"

    # Verify categorical encoding for 'ocean_proximity' (example NEAR BAY)
    if "ocean_proximity_near_bay" in X.columns:
        assert (
            X["ocean_proximity_near_bay"].sum() > 0
        ), "Expected at least one 'NEAR BAY' entry to be encoded as 1"


@patch("analytics.preprocessor.logger")
def test_preprocess_housing_data_missing_file(mock_logger):
    # Test for missing file
    with pytest.raises(FileNotFoundError):
        preprocess_housing_data("non_existent_file.csv")


@patch("analytics.preprocessor.logger")
def test_preprocess_housing_data_invalid_format(mock_logger, tmpdir):
    # Create a temporary invalid CSV file
    invalid_path = os.path.join(tmpdir, "invalid.csv")
    with open(invalid_path, "w") as f:
        f.write("INVALID FILE CONTENT")

    # Test for invalid format
    with pytest.raises(ValueError):
        preprocess_housing_data(invalid_path)


@patch("analytics.preprocessor.logger")
def test_preprocess_housing_data_missing_target(mock_logger, tmpdir):
    # Create a CSV file without the target column
    csv_path = os.path.join(tmpdir, "missing_target.csv")
    data = {
        "longitude": [-122.23],
        "latitude": [37.88],
        "housing_median_age": [41.0],
        "total_rooms": [880.0],
    }
    pd.DataFrame(data).to_csv(csv_path, index=False)

    # Test for missing target column
    with pytest.raises(
        ValueError, match="Target column 'median_house_value' not found"
    ):
        preprocess_housing_data(csv_path)


@patch("analytics.preprocessor.logger")
def test_preprocess_housing_data_missing_features(mock_logger, tmpdir):
    # Create a CSV file with missing features
    csv_path = os.path.join(tmpdir, "missing_features.csv")
    data = {
        "median_house_value": [452600.0],
        "longitude": [-122.23],
    }
    pd.DataFrame(data).to_csv(csv_path, index=False)

    # Run the preprocessor
    X, y = preprocess_housing_data(csv_path)

    # Check that missing features are added with default values
    for col in Config.EXPECTED_FEATURES:
        assert col in X.columns
        if col not in data:
            assert (X[col] == 0).all()
