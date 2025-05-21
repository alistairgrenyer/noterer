"""
Noterer: AI-Powered Graph-Based Note Taker
Main application entry point

This script launches both the backend API server and frontend application.
"""
import sys
import uvicorn
import multiprocessing
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def start_backend():
    """Start the FastAPI backend server"""
    from backend.api.app import app
    uvicorn.run(app, host="127.0.0.1", port=8000)

def start_frontend():
    """Start the desktop UI application"""
    from frontend.app import NotererApp
    app = NotererApp()
    app.run()

if __name__ == "__main__":
    # Determine if we should start only the backend, only the frontend, or both
    start_mode = sys.argv[1] if len(sys.argv) > 1 else "all"
    
    if start_mode == "backend" or start_mode == "all":
        # Start backend in a separate process
        backend_process = multiprocessing.Process(target=start_backend)
        backend_process.start()
        print("Backend API server started at http://127.0.0.1:8000")
    
    if start_mode == "frontend" or start_mode == "all":
        # Start frontend (in main process)
        print("Starting Noterer frontend application...")
        start_frontend()
        
        # If we started the backend, clean up when frontend exits
        if start_mode == "all" and 'backend_process' in locals():
            backend_process.terminate()
            backend_process.join()
