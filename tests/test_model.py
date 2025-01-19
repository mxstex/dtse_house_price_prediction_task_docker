def test_model_predictions():
    from models.model import load_model, predict
    import pandas as pd
    import numpy as np

    # Load the model
    model = load_model("models/model.joblib")

    # Debug: Check the model type
    print(f"Loaded model: {type(model)}")

    # Define sample inputs with the correct feature structure
    feature_columns = [
        "longitude",
        "latitude",
        "housing_median_age",
        "total_rooms",
        "total_bedrooms",
        "population",
        "households",
        "median_income",
        "ocean_proximity_<1H OCEAN",
        "ocean_proximity_INLAND",
        "ocean_proximity_ISLAND",
        "ocean_proximity_NEAR BAY",
        "ocean_proximity_NEAR OCEAN",
    ]

    # Create a DataFrame with the correct structure
    test_cases = [
        {
            "input": [
                -122.64,
                38.01,
                36.0,
                1336.0,
                258.0,
                678.0,
                249.0,
                5.5789,
                0,
                0,
                0,
                0,
                1,
            ],  # One-hot-encoded "NEAR OCEAN"
            "expected_output": 320201.58554044,
        },
        {
            "input": [
                -115.73,
                33.35,
                23.0,
                1586.0,
                448.0,
                338.0,
                182.0,
                1.2132,
                0,
                1,
                0,
                0,
                0,
            ],  # One-hot-encoded "INLAND"
            "expected_output": 58815.45033765,
        },
        {
            "input": [
                -117.96,
                33.89,
                24.0,
                1332.0,
                252.0,
                625.0,
                230.0,
                4.4375,
                1,
                0,
                0,
                0,
                0,
            ],  # One-hot-encoded "<1H OCEAN"
            "expected_output": 192575.77355635,
        },
    ]

    # Tolerance for prediction accuracy
    tolerance = 1e-2

    for case in test_cases:
        # Convert input to a DataFrame
        sample_features = pd.DataFrame([case["input"]], columns=feature_columns)

        # Debug: Check the input structure
        print(f"Sample features:\n{sample_features}")

        # Generate prediction
        prediction = predict(sample_features, model)

        # Debug: Print the prediction
        print(f"Prediction: {prediction}")

        # Validate prediction
        assert len(prediction) == 1, "Prediction size mismatch"
        assert prediction[0] > 0, "Prediction value should be positive"
        assert abs(prediction[0] - case["expected_output"]) < tolerance, (
            f"Prediction value {prediction[0]} deviates from expected "
            f"{case['expected_output']} by more than {tolerance}"
        )


def test_model_invalid_file():
    from models.model import load_model

    invalid_file = "non_existent_model.joblib"
    try:
        load_model(invalid_file)
        assert False, "Model loading should fail for invalid file"
    except FileNotFoundError:
        pass
