"""
Concept Models

This module provides Pydantic models for concept data validation and serialization.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict

class ConceptBase(BaseModel):
    """Base model for concept operations"""
    name: str = Field(..., description="The name of the concept")
    description: Optional[str] = Field(default=None, description="Description of the concept")
    
class ConceptCreate(ConceptBase):
    """Model for creating a new concept"""
    categories: Optional[List[str]] = Field(default=None, description="Philosophical categories this concept belongs to")

class ConceptUpdate(BaseModel):
    """Model for updating an existing concept"""
    name: Optional[str] = Field(default=None, description="Updated name of the concept")
    description: Optional[str] = Field(default=None, description="Updated description of the concept")
    categories: Optional[List[str]] = Field(default=None, description="Updated philosophical categories")

class ConceptRead(ConceptBase):
    """Model for reading concept data"""
    id: str = Field(..., description="Unique identifier for the concept")
    categories: Optional[List[Dict[str, float]]] = Field(
        default=None, 
        description="Philosophical categories with confidence weights"
    )
    
    class Config:
        """Pydantic configuration"""
        from_attributes = True
