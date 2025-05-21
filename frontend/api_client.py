"""
API Client

This module provides a client for communicating with the Noterer backend API.
"""
import aiohttp
import asyncio
import json
from typing import Dict, List, Any, Optional, Union

class APIClient:
    """Client for the Noterer backend API"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        """
        Initialize the API client
        
        Args:
            base_url: Base URL of the Noterer backend API
        """
        self.base_url = base_url
        self.session = None
        
    async def _ensure_session(self) -> None:
        """Ensure that an HTTP session exists"""
        if self.session is None:
            self.session = aiohttp.ClientSession()
            
    async def close(self) -> None:
        """Close the HTTP session"""
        if self.session:
            await self.session.close()
            self.session = None
            
    async def _request(self, method: str, endpoint: str, 
                      data: Optional[Dict[str, Any]] = None,
                      params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make a request to the API
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (without base URL)
            data: Optional JSON data for the request body
            params: Optional query parameters
            
        Returns:
            Response data as a dictionary
        """
        await self._ensure_session()
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with self.session.request(
                method=method,
                url=url,
                json=data,
                params=params
            ) as response:
                if response.status == 204:  # No content
                    return {}
                    
                response_data = await response.json()
                if not response.ok:
                    error_msg = response_data.get("detail", "Unknown error")
                    raise Exception(f"API Error ({response.status}): {error_msg}")
                    
                return response_data
                
        except Exception as e:
            # In a real app, we'd want better error handling and retry logic
            print(f"API request error: {str(e)}")
            return {"error": str(e)}
            
    # Note-related API methods
    
    async def create_note(self, content: str, tags: Optional[List[str]] = None) -> Dict[str, Any]:
        """Create a new note"""
        data = {"content": content}
        if tags:
            data["tags"] = tags
        return await self._request("POST", "/notes/", data=data)
        
    async def get_notes(self, limit: int = 10, skip: int = 0) -> List[Dict[str, Any]]:
        """Get all notes with pagination"""
        return await self._request("GET", "/notes/", params={"limit": limit, "skip": skip})
        
    async def get_note(self, note_id: str) -> Dict[str, Any]:
        """Get a specific note by ID"""
        return await self._request("GET", f"/notes/{note_id}")
        
    async def update_note(self, note_id: str, content: Optional[str] = None, 
                         tags: Optional[List[str]] = None) -> Dict[str, Any]:
        """Update a note"""
        data = {}
        if content is not None:
            data["content"] = content
        if tags is not None:
            data["tags"] = tags
        return await self._request("PUT", f"/notes/{note_id}", data=data)
        
    async def delete_note(self, note_id: str) -> Dict[str, Any]:
        """Delete a note"""
        return await self._request("DELETE", f"/notes/{note_id}")
        
    # AI-related API methods
    
    async def query_ai(self, prompt: str, context_ids: Optional[List[str]] = None,
                      include_graph_context: bool = True) -> Dict[str, Any]:
        """Query the AI with a prompt"""
        data = {
            "prompt": prompt,
            "include_graph_context": include_graph_context
        }
        if context_ids:
            data["context_ids"] = context_ids
        return await self._request("POST", "/ai/query", data=data)
        
    async def process_note(self, note_content: str) -> Dict[str, Any]:
        """Process a note with AI to extract concepts and categories"""
        return await self._request("POST", "/ai/process-note", data={"content": note_content})
