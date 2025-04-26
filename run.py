"""
Script to run the Cruxz Transcript API application.
"""
import os
import uvicorn
from app.core.config import settings

def main():
    """
    Run the application with Uvicorn.
    """
    port = settings.PORT
    
    print(f"Starting Cruxz Transcript API on port {port}...")
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=(settings.ENVIRONMENT == "development")
    )

if __name__ == "__main__":
    main() 