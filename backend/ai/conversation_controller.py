"""
Conversation Controller

This module manages the conversational flow for AI interactions, implementing
the confirmation-driven interaction model described in our strategy.
"""
import json
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum

from backend.ai.manager import AIManager

class ConversationState(Enum):
    """States in the conversation flow"""
    INITIAL = "initial"
    AWAITING_USER_INPUT = "awaiting_user_input"
    ANALYZING = "analyzing"
    AWAITING_CONFIRMATION = "awaiting_confirmation"
    EXECUTING = "executing"
    ERROR = "error"

class ActionStatus(Enum):
    """Status of proposed or executed actions"""
    PROPOSED = "proposed"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"
    EXECUTED = "executed"
    FAILED = "failed"

class ConversationTurn:
    """Represents a single turn in the conversation"""
    
    def __init__(self, 
                 user_input: Optional[str] = None,
                 ai_response: Optional[str] = None,
                 proposed_actions: Optional[List[Dict[str, Any]]] = None,
                 confirmed: bool = False,
                 executed_actions: Optional[List[Dict[str, Any]]] = None):
        """
        Initialize a conversation turn
        
        Args:
            user_input: The user's input for this turn
            ai_response: The AI's response
            proposed_actions: List of actions proposed by the AI
            confirmed: Whether the user confirmed the proposed actions
            executed_actions: List of actions that were executed
        """
        self.user_input = user_input
        self.ai_response = ai_response
        self.proposed_actions = proposed_actions or []
        self.confirmed = confirmed
        self.executed_actions = executed_actions or []
        self.timestamp = None  # Will be set when added to conversation
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "user_input": self.user_input,
            "ai_response": self.ai_response,
            "proposed_actions": self.proposed_actions,
            "confirmed": self.confirmed,
            "executed_actions": self.executed_actions,
            "timestamp": self.timestamp
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversationTurn':
        """Create from dictionary representation"""
        turn = cls(
            user_input=data.get("user_input"),
            ai_response=data.get("ai_response"),
            proposed_actions=data.get("proposed_actions", []),
            confirmed=data.get("confirmed", False),
            executed_actions=data.get("executed_actions", [])
        )
        turn.timestamp = data.get("timestamp")
        return turn

class Conversation:
    """Manages the entire conversation context and history"""
    
    def __init__(self, conversation_id: Optional[str] = None):
        """
        Initialize a conversation
        
        Args:
            conversation_id: Optional ID for the conversation
        """
        self.conversation_id = conversation_id
        self.turns: List[ConversationTurn] = []
        self.state = ConversationState.INITIAL
        self.current_turn: Optional[ConversationTurn] = None
        self.metadata: Dict[str, Any] = {}
        
    def start_new_turn(self, user_input: str) -> ConversationTurn:
        """
        Start a new conversation turn with user input
        
        Args:
            user_input: The user's input text
            
        Returns:
            The new conversation turn
        """
        # Complete any previous turn
        if self.current_turn:
            self.turns.append(self.current_turn)
            
        # Create a new turn
        self.current_turn = ConversationTurn(user_input=user_input)
        self.state = ConversationState.ANALYZING
        return self.current_turn
    
    def set_proposed_actions(self, 
                            ai_response: str, 
                            proposed_actions: List[Dict[str, Any]]) -> None:
        """
        Set the AI response and proposed actions for the current turn
        
        Args:
            ai_response: The AI's response text
            proposed_actions: List of actions proposed by the AI
        """
        if not self.current_turn:
            raise ValueError("No active conversation turn")
            
        self.current_turn.ai_response = ai_response
        self.current_turn.proposed_actions = proposed_actions
        self.state = ConversationState.AWAITING_CONFIRMATION
    
    def set_confirmation(self, confirmed: bool) -> None:
        """
        Set the user's confirmation status for proposed actions
        
        Args:
            confirmed: Whether the user confirmed the proposed actions
        """
        if not self.current_turn:
            raise ValueError("No active conversation turn")
            
        self.current_turn.confirmed = confirmed
        if confirmed:
            self.state = ConversationState.EXECUTING
        else:
            # If rejected, we start a new turn awaiting user input
            self.turns.append(self.current_turn)
            self.current_turn = None
            self.state = ConversationState.AWAITING_USER_INPUT
    
    def set_executed_actions(self, executed_actions: List[Dict[str, Any]]) -> None:
        """
        Set the actions that were executed after confirmation
        
        Args:
            executed_actions: List of actions that were executed
        """
        if not self.current_turn:
            raise ValueError("No active conversation turn")
            
        self.current_turn.executed_actions = executed_actions
        self.turns.append(self.current_turn)
        self.current_turn = None
        self.state = ConversationState.AWAITING_USER_INPUT
    
    def get_context_for_ai(self, max_turns: int = 5) -> str:
        """
        Get formatted conversation history for AI context
        
        Args:
            max_turns: Maximum number of past turns to include
            
        Returns:
            Formatted conversation history
        """
        # Get recent turns
        recent_turns = self.turns[-max_turns:] if len(self.turns) > 0 else []
        
        # Format conversation history
        history = ""
        for i, turn in enumerate(recent_turns):
            history += f"Turn {i+1}:\n"
            history += f"User: {turn.user_input}\n"
            if turn.ai_response:
                history += f"AI: {turn.ai_response}\n"
            if turn.confirmed:
                history += "User confirmed actions.\n"
            else:
                history += "User rejected actions.\n"
            history += "\n"
            
        # Add current turn if exists
        if self.current_turn and self.current_turn.user_input:
            history += f"Current Turn:\nUser: {self.current_turn.user_input}\n"
            
        return history
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert conversation to dictionary representation"""
        return {
            "conversation_id": self.conversation_id,
            "state": self.state.value,
            "turns": [turn.to_dict() for turn in self.turns],
            "current_turn": self.current_turn.to_dict() if self.current_turn else None,
            "metadata": self.metadata
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Conversation':
        """Create conversation from dictionary representation"""
        conversation = cls(conversation_id=data.get("conversation_id"))
        conversation.state = ConversationState(data.get("state", ConversationState.INITIAL.value))
        conversation.turns = [ConversationTurn.from_dict(turn) for turn in data.get("turns", [])]
        conversation.current_turn = ConversationTurn.from_dict(data["current_turn"]) if data.get("current_turn") else None
        conversation.metadata = data.get("metadata", {})
        return conversation

class ConversationalFlowController:
    """
    Controls the conversation flow using the confirmation-driven interaction model
    """
    
    def __init__(self, ai_manager: AIManager):
        """
        Initialize the conversational flow controller
        
        Args:
            ai_manager: Instance of AIManager for AI interactions
        """
        self.ai_manager = ai_manager
        self.active_conversations: Dict[str, Conversation] = {}
        
    def get_or_create_conversation(self, conversation_id: Optional[str] = None) -> Conversation:
        """
        Get an existing conversation or create a new one
        
        Args:
            conversation_id: Optional ID for the conversation
            
        Returns:
            Conversation instance
        """
        if conversation_id and conversation_id in self.active_conversations:
            return self.active_conversations[conversation_id]
            
        # Create a new conversation
        conversation = Conversation(conversation_id)
        if conversation_id:
            self.active_conversations[conversation_id] = conversation
            
        return conversation
    
    async def process_user_input(self, 
                                conversation: Conversation,
                                user_input: str,
                                context: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Process user input and generate a response with proposed actions
        
        Args:
            conversation: The conversation instance
            user_input: The user's input text
            context: Optional additional context (notes, concepts, etc.)
            
        Returns:
            Dictionary with AI response and proposed actions
        """
        # Start a new turn with user input
        conversation.start_new_turn(user_input)
        
        # Get conversation history for context
        conversation_history = conversation.get_context_for_ai()
        
        # Create the analysis prompt
        prompt = self._create_analysis_prompt(user_input, conversation_history)
        
        # Merge additional context
        merged_context = context or []
        if conversation_history:
            merged_context.append({
                "type": "conversation_history",
                "content": conversation_history
            })
        
        # Query the AI
        result = await self.ai_manager.query(prompt, merged_context)
        
        # Extract proposed actions from the response
        response_text, proposed_actions = self._extract_actions_from_response(result["response"])
        
        # Update the conversation with the AI response and proposed actions
        conversation.set_proposed_actions(response_text, proposed_actions)
        
        return {
            "response": response_text,
            "proposed_actions": proposed_actions,
            "requires_confirmation": len(proposed_actions) > 0,
            "conversation_state": conversation.state.value
        }
    
    async def process_confirmation(self,
                                 conversation: Conversation,
                                 confirmed: bool,
                                 action_handlers: Optional[Dict[str, callable]] = None) -> Dict[str, Any]:
        """
        Process user confirmation and execute actions if confirmed
        
        Args:
            conversation: The conversation instance
            confirmed: Whether the user confirmed the proposed actions
            action_handlers: Dictionary of handler functions for different action types
            
        Returns:
            Dictionary with results of confirmation processing
        """
        # Update the conversation with confirmation status
        conversation.set_confirmation(confirmed)
        
        # If not confirmed, return early
        if not confirmed:
            return {
                "confirmed": False,
                "executed_actions": [],
                "response": "Actions cancelled as requested.",
                "conversation_state": conversation.state.value
            }
        
        # If confirmed, execute the actions
        executed_actions = []
        errors = []
        
        if conversation.current_turn and conversation.current_turn.proposed_actions:
            for action in conversation.current_turn.proposed_actions:
                try:
                    # Execute the action using the appropriate handler
                    action_type = action.get("type", "unknown")
                    if action_handlers and action_type in action_handlers:
                        result = await action_handlers[action_type](action)
                        executed_action = {**action, "status": ActionStatus.EXECUTED.value, "result": result}
                    else:
                        # No handler available
                        executed_action = {**action, "status": ActionStatus.FAILED.value, "error": "No handler available"}
                        errors.append(f"No handler available for action type: {action_type}")
                except Exception as e:
                    # Handle execution errors
                    executed_action = {**action, "status": ActionStatus.FAILED.value, "error": str(e)}
                    errors.append(f"Error executing {action.get('type', 'unknown')} action: {str(e)}")
                
                executed_actions.append(executed_action)
        
        # Update the conversation with executed actions
        conversation.set_executed_actions(executed_actions)
        
        # Generate response based on execution results
        if errors:
            response = f"Some actions could not be completed: {'; '.join(errors)}"
        else:
            response = "All actions were completed successfully."
        
        return {
            "confirmed": True,
            "executed_actions": executed_actions,
            "response": response,
            "conversation_state": conversation.state.value
        }
    
    def _create_analysis_prompt(self, user_input: str, conversation_history: str) -> str:
        """Create a prompt for analyzing user input and generating proposed actions"""
        return f"""
        You are an AI assistant that helps manage notes and related tasks in Noterer.

        Task: Analyze the user's request, determine necessary actions, and present a summary for confirmation.

        Conversation history:
        {conversation_history}

        Current user input:
        {user_input}

        Please follow these steps:

        1. Analyze the user's intent and determine required actions (note creation/modification, event scheduling, concept linking, etc.)

        2. For each action, determine:
           - Specific changes to be made
           - Philosophical implications and categorizations
           - Impact on the existing knowledge graph

        3. Generate a clear summary of all proposed actions in user-friendly language

        4. Ask for user confirmation before proceeding

        Your response should include:
        1. A brief analysis of the user's request
        2. A clear summary of all proposed actions
        3. A request for confirmation

        For machine processing, include a JSON block with proposed actions in this format:
        ```json
        {
          "proposed_actions": [
            {
              "type": "create_note",
              "content": "note content",
              "concepts": ["concept1", "concept2"],
              "categories": [{"name": "category", "confidence": 0.9}]
            },
            {
              "type": "create_relationship",
              "source": "source_id",
              "target": "target_id",
              "relationship_type": "RELATES_TO",
              "properties": {"weight": 0.8}
            }
          ]
        }
        ```
        """
    
    def _extract_actions_from_response(self, response: str) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Extract proposed actions from AI response
        
        Args:
            response: Raw AI response text
            
        Returns:
            Tuple of (user-friendly response text, list of proposed actions)
        """
        # Default empty actions list
        proposed_actions = []
        
        # Look for JSON block in the response
        try:
            # Find JSON block within markdown code blocks
            json_start = response.find("```json")
            if json_start != -1:
                json_end = response.find("```", json_start + 6)
                if json_end != -1:
                    json_str = response[json_start + 7:json_end].strip()
                    action_data = json.loads(json_str)
                    if "proposed_actions" in action_data:
                        proposed_actions = action_data["proposed_actions"]
                        
                    # Remove the JSON block from the response for user-friendly output
                    user_response = response[:json_start] + response[json_end + 3:]
                    return user_response.strip(), proposed_actions
        except Exception:
            # If extraction fails, return the original response
            pass
            
        return response, proposed_actions
