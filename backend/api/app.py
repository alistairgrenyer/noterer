"""
Noterer API Server

This module provides the FastAPI application that serves as the backend API
for the Noterer application.
"""
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI app
app = FastAPI(
    title="Noterer API",
    description="API for the Noterer AI-powered Graph-Based Note Taker",
    version="0.1.0"
)

# Add CORS middleware to allow frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, this should be restricted
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import route modules
from backend.api.routes import notes, concepts, graph, ai, conversation

# Include routers from route modules
app.include_router(notes.router, prefix="/notes", tags=["notes"])
app.include_router(concepts.router, prefix="/concepts", tags=["concepts"])
app.include_router(graph.router, prefix="/graph", tags=["graph"])
app.include_router(ai.router, prefix="/ai", tags=["ai"])
app.include_router(conversation.router, prefix="/conversation", tags=["conversation"])

@app.get("/")
async def root():
    """Root endpoint that provides API information"""
    return {
        "application": "Noterer API",
        "version": "0.1.0",
        "status": "running",
        "documentation": "/docs"
    }
