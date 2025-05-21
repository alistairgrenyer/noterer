"""
Conversation Service

This module provides services for interacting with the Conversation API
and implementing the confirmation-driven flow in the frontend.
"""
import aiohttp
from typing import Dict, Any, Optional

class ConversationService:
    """Service for conversation-based interactions with the backend"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        """
        Initialize the conversation service
        
        Args:
            base_url: Base URL of the backend API
        """
        self.base_url = base_url
        self.session = None
        self.active_conversation_id = None
        
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
                      data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make a request to the API
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (without base URL)
            data: Optional JSON data for the request body
            
        Returns:
            Response data as a dictionary
        """
        await self._ensure_session()
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with self.session.request(
                method=method,
                url=url,
                json=data
            ) as response:
                response_data = await response.json()
                if not response.ok:
                    error_msg = response_data.get("detail", "Unknown error")
                    raise Exception(f"API Error ({response.status}): {error_msg}")
                    
                return response_data
                
        except Exception as e:
            print(f"API request error: {str(e)}")
            return {"error": str(e)}
    
    async def start_conversation(self) -> Dict[str, Any]:
        """
        Start a new conversation
        
        Returns:
            Dictionary with the conversation ID and status
        """
        result = await self._request("POST", "/conversation/start")
        if "conversation_id" in result:
            self.active_conversation_id = result["conversation_id"]
        return result
    
    async def send_message(self, message: str, 
                         include_graph_context: bool = True) -> Dict[str, Any]:
        """
        Send a message in the active conversation
        
        Args:
            message: The message text to send
            include_graph_context: Whether to include graph context in processing
            
        Returns:
            Dictionary with the AI response and proposed actions
        """
        if not self.active_conversation_id:
            await self.start_conversation()
            
        data = {
            "text": message,
            "include_graph_context": include_graph_context
        }
        
        endpoint = f"/conversation/input/{self.active_conversation_id}"
        return await self._request("POST", endpoint, data)
    
    async def confirm_actions(self, confirmed: bool = True) -> Dict[str, Any]:
        """
        Confirm or reject proposed actions
        
        Args:
            confirmed: Whether to confirm (True) or reject (False) the actions
            
        Returns:
            Dictionary with the result of the confirmation
        """
        if not self.active_conversation_id:
            raise ValueError("No active conversation")
            
        data = {
            "confirmed": confirmed
        }
        
        endpoint = f"/conversation/confirm/{self.active_conversation_id}"
        return await self._request("POST", endpoint, data)
    
    async def end_conversation(self) -> Dict[str, Any]:
        """
        End the active conversation
        
        Returns:
            Dictionary with the status of the ended conversation
        """
        if not self.active_conversation_id:
            raise ValueError("No active conversation")
            
        endpoint = f"/conversation/{self.active_conversation_id}"
        result = await self._request("DELETE", endpoint)
        
        if result.get("status") == "ended":
            self.active_conversation_id = None
            
        return result
