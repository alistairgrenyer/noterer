"""
AI Models

This module provides Pydantic models for AI interaction data validation and serialization.
"""
from pydantic import BaseModel, Field
from typing import Optional, List

class AIQuery(BaseModel):
    """Model for AI query requests"""
    prompt: str = Field(..., description="The user's prompt or question to the AI")
    context_ids: Optional[List[str]] = Field(default=None, description="IDs of notes to include as context")
    include_graph_context: bool = Field(default=True, description="Whether to include graph-derived context")
    
class AIResponse(BaseModel):
    """Model for AI query responses"""
    response: str = Field(..., description="The AI's response to the query")
    source_notes: Optional[List[str]] = Field(default=None, description="IDs of notes used as sources")
    concepts_referenced: Optional[List[str]] = Field(default=None, description="Concepts referenced in the response")
    
    class Config:
        """Pydantic configuration"""
        from_attributes = True
