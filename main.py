from fastapi import FastAPI
from routes.routes import router
import uvicorn
from config import logger, Config

app = FastAPI()

# Include routes
try:
    app.include_router(router, prefix="/api")
    logger.info("Routes included successfully.")
except Exception as e:
    logger.error(f"Failed to include routes: {e}")
    raise


@app.get("/")
async def root():
    logger.info("Root endpoint accessed.")
    return {"message": "Welcome to the Housing Data API!"}


if __name__ == "__main__":
    try:
        logger.info("Starting the application...")
        uvicorn.run(app, host=Config.ENV_LOCAL_DOCKER, port=8000)
    except Exception as e:
        logger.error(f"Application failed to start: {e}")
