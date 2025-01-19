# House Price Prediction

## Overview
This project provides a comprehensive pipeline for predicting house prices using a combination of modern technologies. It facilitates uploading raw datasets, preprocessing data, and making predictions using trained models. Predictions and raw data are stored in efficient databases for further analysis.

### Key Features
- **Upload Datasets**: Upload raw CSV files for analysis.
- **Data Preprocessing**: Automatically preprocess raw data to extract meaningful features.
- **Database Integration**: 
  - MongoDB: Stores raw data.
  - PostgreSQL/TimescaleDB: Stores prediction results.
- **Prediction Models**: Utilize trained models for real-time predictions.
- **API Integration**: FastAPI is used for efficient API calls to interact with the system.

## Project Structure
```
House_price_prediction/
├── analytics/          # Analytical tools and scripts
├── data/               # Data files (input/output)
├── database_handler/   # Database interaction logic
├── models/             # Machine learning models and scripts
├── routes/             # FastAPI route definitions
├── tests/              # Test scripts and cases
├── config.py           # Project configuration
├── main.py             # Main application entry point
├── requirements.txt    # Python dependencies
├── schema.mermaid      # Mermaid schema for system visualization
├── dockerfile-mongoDB  # Dockerfile for MongoDB
├── dockerfile-TimescaleDB # Dockerfile for TimescaleDB
└── README.md           # Project documentation
```

## Installation
### Prerequisites
- Python 3.8+
- Docker & Docker Compose
- MongoDB & TimescaleDB

### Steps
1. **Clone the Repository**:
   ```bash
   git clone <repository_url>
   cd House_price_prediction
   ```
2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Set Up Databases**:
   - MongoDB:
     ```bash
     docker build -t mongodb -f dockerfile-mongoDB .
     docker run -d -p 27017:27017 mongodb
     ```
   - TimescaleDB:
     ```bash
     docker build -t timescaledb -f dockerfile-TimescaleDB .
     docker run -d -p 5432:5432 timescaledb
     ```
4. **Run the Application**:
   ```bash
   python main.py
   ```

## Usage
- **Upload Data**: Use the `/upload` API endpoint to upload a CSV file.
- **Process Data**: Call the `/process` endpoint to preprocess uploaded data.
- **Make Predictions**: Use `/predict` to get predictions for preprocessed data.
- **Health Check**: Confirm service availability with `/health`.

## Mermaid Schema
The system architecture is visualized in `schema.mermaid`:
```
flowchart TD
    User -->|Uploads Data| API[FastAPI]
    API -->|Stores Raw Data| MongoDB
    API -->|Saves Predictions| TimescaleDB
    API -->|Triggers| MLModel[Trained ML Model]
```

## Testing
Run tests using Pytest:
```bash
pytest
```

## Contribution
1. Fork the repository.
2. Create a feature branch: `git checkout -b feature-name`.
3. Commit changes: `git commit -m 'Add new feature'`.
4. Push to the branch: `git push origin feature-name`.
5. Create a pull request.

## License
This project is licensed under the MIT License.
