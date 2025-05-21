"""
Note Models

This module provides Pydantic models for note data validation and serialization.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime

class NoteBase(BaseModel):
    """Base model for note operations"""
    content: str = Field(..., description="The content of the note")
    
class NoteCreate(NoteBase):
    """Model for creating a new note"""
    tags: Optional[List[str]] = Field(default=None, description="Optional tags for the note")

class NoteUpdate(BaseModel):
    """Model for updating an existing note"""
    content: Optional[str] = Field(default=None, description="Updated content of the note")
    tags: Optional[List[str]] = Field(default=None, description="Updated tags for the note")

class NoteRead(NoteBase):
    """Model for reading note data"""
    id: str = Field(..., description="Unique identifier for the note")
    created_at: str = Field(..., description="Timestamp when the note was created")
    updated_at: Optional[str] = Field(default=None, description="Timestamp when the note was last updated")
    tags: Optional[List[str]] = Field(default=None, description="Tags associated with the note")
    
    class Config:
        """Pydantic configuration"""
        from_attributes = True
