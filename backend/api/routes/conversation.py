"""
Conversation API Routes

This module provides API endpoints for conversation-based interactions using
the confirmation-driven flow model.
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import Dict, Any

from backend.ai.manager import AIManager
from backend.ai.conversation_controller import ConversationalFlowController, Conversation
from backend.db.graph_manager import GraphManager

# Create router
router = APIRouter()

# In-memory store for active conversations (in a real app, would use a database)
active_conversations = {}

# Action handlers for different action types
async def handle_create_note(action: Dict[str, Any], graph_manager: GraphManager) -> Dict[str, Any]:
    """Handle the create_note action"""
    content = action.get("content", "")
    concepts = action.get("concepts", [])
    
    # Create the note
    note = graph_manager.create_note(content)
    
    # Process concepts and relationships if provided
    for concept_name in concepts:
        # Create or get concept
        concept = graph_manager.create_concept(concept_name)
        
        # Create relationship from note to concept
        graph_manager.create_relationship(
            note["id"], 
            concept["id"], 
            "ABOUT"
        )
    
    return {
        "note_id": note["id"],
        "created": True
    }

async def handle_create_concept(action: Dict[str, Any], graph_manager: GraphManager) -> Dict[str, Any]:
    """Handle the create_concept action"""
    name = action.get("name", "")
    description = action.get("description", "")
    categories = action.get("categories", [])
    
    # Create the concept
    concept = graph_manager.create_concept(name, description, categories)
    
    return {
        "concept_id": concept["id"],
        "created": True
    }

async def handle_create_relationship(action: Dict[str, Any], graph_manager: GraphManager) -> Dict[str, Any]:
    """Handle the create_relationship action"""
    source_id = action.get("source", "")
    target_id = action.get("target", "")
    relationship_type = action.get("relationship_type", "RELATES_TO")
    properties = action.get("properties", {})
    
    # Create the relationship
    graph_manager.create_relationship(
        source_id, 
        target_id, 
        relationship_type, 
        properties
    )
    
    return {
        "source_id": source_id,
        "target_id": target_id,
        "created": True
    }

# Helper function to get dependencies
def get_ai_manager():
    """Get AI manager instance"""
    return AIManager()

def get_graph_manager():
    """Get graph manager instance"""
    return GraphManager()

def get_conversation_controller(ai_manager: AIManager = Depends(get_ai_manager)):
    """Get conversation controller instance"""
    return ConversationalFlowController(ai_manager)

@router.post("/start")
async def start_conversation(
    background_tasks: BackgroundTasks,
    ai_manager: AIManager = Depends(get_ai_manager)
) -> Dict[str, Any]:
    """Start a new conversation"""
    # Create a new conversation with a unique ID
    import uuid
    conversation_id = str(uuid.uuid4())
    conversation = Conversation(conversation_id)
    
    # Store in active conversations
    active_conversations[conversation_id] = conversation
    
    return {
        "conversation_id": conversation_id,
        "status": "started"
    }

@router.post("/input/{conversation_id}")
async def process_user_input(
    conversation_id: str,
    user_input: Dict[str, Any],
    conversation_controller: ConversationalFlowController = Depends(get_conversation_controller),
    graph_manager: GraphManager = Depends(get_graph_manager)
) -> Dict[str, Any]:
    """Process user input in a conversation"""
    # Get the active conversation or return error
    if conversation_id not in active_conversations:
        raise HTTPException(
            status_code=404,
            detail=f"Conversation with ID {conversation_id} not found"
        )
    
    conversation = active_conversations[conversation_id]
    
    # Get graph context
    context = []
    if user_input.get("include_graph_context", True):
        # In a real implementation, we would query the graph database for relevant context
        # For now, just a placeholder
        pass
    
    # Process the user input
    result = await conversation_controller.process_user_input(
        conversation,
        user_input["text"],
        context
    )
    
    return {
        "conversation_id": conversation_id,
        "response": result["response"],
        "requires_confirmation": result["requires_confirmation"],
        "proposed_actions": result.get("proposed_actions", []),
        "conversation_state": result["conversation_state"]
    }

@router.post("/confirm/{conversation_id}")
async def process_confirmation(
    conversation_id: str,
    confirmation: Dict[str, bool],
    conversation_controller: ConversationalFlowController = Depends(get_conversation_controller),
    graph_manager: GraphManager = Depends(get_graph_manager)
) -> Dict[str, Any]:
    """Process user confirmation for proposed actions"""
    # Get the active conversation or return error
    if conversation_id not in active_conversations:
        raise HTTPException(
            status_code=404,
            detail=f"Conversation with ID {conversation_id} not found"
        )
    
    conversation = active_conversations[conversation_id]
    
    # Set up action handlers
    action_handlers = {
        "create_note": lambda action: handle_create_note(action, graph_manager),
        "create_concept": lambda action: handle_create_concept(action, graph_manager),
        "create_relationship": lambda action: handle_create_relationship(action, graph_manager)
    }
    
    # Process the confirmation
    result = await conversation_controller.process_confirmation(
        conversation,
        confirmation.get("confirmed", False),
        action_handlers
    )
    
    return {
        "conversation_id": conversation_id,
        "confirmed": result["confirmed"],
        "response": result["response"],
        "executed_actions": result["executed_actions"],
        "conversation_state": result["conversation_state"]
    }

@router.get("/{conversation_id}")
async def get_conversation(conversation_id: str) -> Dict[str, Any]:
    """Get the current state of a conversation"""
    # Get the active conversation or return error
    if conversation_id not in active_conversations:
        raise HTTPException(
            status_code=404,
            detail=f"Conversation with ID {conversation_id} not found"
        )
    
    conversation = active_conversations[conversation_id]
    
    return {
        "conversation_id": conversation_id,
        "state": conversation.state.value,
        "turns": len(conversation.turns),
        "has_current_turn": conversation.current_turn is not None
    }

@router.delete("/{conversation_id}")
async def end_conversation(conversation_id: str) -> Dict[str, Any]:
    """End and remove a conversation"""
    # Get the active conversation or return error
    if conversation_id not in active_conversations:
        raise HTTPException(
            status_code=404,
            detail=f"Conversation with ID {conversation_id} not found"
        )
    
    # Remove from active conversations
    del active_conversations[conversation_id]
    
    return {
        "conversation_id": conversation_id,
        "status": "ended"
    }
