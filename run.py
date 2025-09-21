import uvicorn
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("\n" + "="*60)
    print("LEAD SCORER APPLICATION")
    print("="*60)
    print("\nStarting server...")
    print("Open your browser and navigate to: http://localhost:8000")
    print("\nPress CTRL+C to stop the server\n")
    print("="*60 + "\n")

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )