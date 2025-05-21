"""
AI Manager

This module manages interactions with the AI system, including prompt construction,
response processing, and integration with the graph database.
"""
import os
import json
from openai import OpenAI
from typing import List, Dict, Any, Optional

class AIManager:
    """Manager for AI interactions"""
    
    def __init__(self, model_name: str = "gpt-4o"):
        """Initialize the AI manager with API key and model configuration"""
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model_name = model_name
        self.system_prompts = {
            "general": "You are an intelligent assistant for the Noterer application. You help with note-taking, concept extraction, and philosophical organization.",
            "analysis": "You are an analytical assistant for the Noterer application. Extract concepts, categorize content philosophically, and identify relationships between ideas.",
            "confirmation": "You are a helpful assistant for the Noterer application. Your task is to clearly explain proposed changes and ask for user confirmation before proceeding."
        }
    
    async def query(self, prompt: str, context: Optional[List[Dict[str, Any]]] = None, 
                prompt_type: str = "general", structured_output: bool = False) -> Dict[str, Any]:
        """
        Query the AI with a prompt and optional context
        
        Args:
            prompt: The user's prompt or question
            context: Optional list of context items (notes, concepts, etc.)
            prompt_type: Type of system prompt to use (general, analysis, confirmation)
            structured_output: Whether to request structured JSON output
            
        Returns:
            Dictionary containing the AI response and metadata
        """
        # Construct the full prompt with context if provided
        full_prompt = self._build_prompt(prompt, context, structured_output)
        
        try:
            # Get the appropriate system prompt
            system_prompt = self.system_prompts.get(prompt_type, self.system_prompts["general"])
            
            # Construct messages array
            messages = [
                {"role": "system", "content": system_prompt}
            ]
            
            # Add conversation history messages if present in context
            if context:
                for item in context:
                    if item.get("type") == "conversation_history":
                        # Parse conversation history into separate messages
                        history_lines = item["content"].strip().split('\n')
                        current_role = None
                        current_content = []
                        
                        for line in history_lines:
                            if line.startswith("User: "):
                                # Add previous message if exists
                                if current_role and current_content:
                                    messages.append({
                                        "role": current_role,
                                        "content": "\n".join(current_content)
                                    })
                                # Start new user message
                                current_role = "user"
                                current_content = [line[6:]]
                            elif line.startswith("AI: "):
                                # Add previous message if exists
                                if current_role and current_content:
                                    messages.append({
                                        "role": current_role,
                                        "content": "\n".join(current_content)
                                    })
                                # Start new assistant message
                                current_role = "assistant"
                                current_content = [line[4:]]
                            elif current_content:
                                # Continue current message
                                current_content.append(line)
                        
                        # Add final message if exists
                        if current_role and current_content:
                            messages.append({
                                "role": current_role,
                                "content": "\n".join(current_content)
                            })
            
            # Add the current prompt as a user message
            messages.append({"role": "user", "content": full_prompt})
            
            # Call the OpenAI API
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                response_format={"type": "json_object"} if structured_output else {"type": "text"}
            )
            
            # Process and return the response
            result = {
                "response": response.choices[0].message.content,
                "source_notes": self._extract_sources(response.choices[0].message.content, context),
                "concepts_referenced": self._extract_concepts(response.choices[0].message.content)
            }
            
            # Parse structured output if requested
            if structured_output:
                try:
                    result["structured_data"] = json.loads(response.choices[0].message.content)
                except json.JSONDecodeError:
                    result["structured_data"] = None
                    result["parse_error"] = "Failed to parse JSON response"
            
            return result
            
        except Exception as e:
            # Handle API errors
            return {
                "error": str(e),
                "response": f"An error occurred: {str(e)}"
            }
    
    def _build_prompt(self, prompt: str, context: Optional[List[Dict[str, Any]]], 
                      structured_output: bool = False) -> str:
        """
        Build a complete prompt with context for the AI
        
        Args:
            prompt: The base prompt text
            context: Optional list of context items
            structured_output: Whether to request structured JSON output
            
        Returns:
            Complete prompt string
        """
        # Skip conversation history items as they'll be added as separate messages
        if context:
            filtered_context = [
                item for item in context 
                if item.get("type") != "conversation_history"
            ]
        else:
            filtered_context = []
            
        # If no relevant context items after filtering, return just the prompt
        if not filtered_context:
            return prompt
            
        # Build context section
        context_text = "\n\n### CONTEXT:\n"
        for item in filtered_context:
            if "type" in item and "content" in item:
                context_text += f"\n{item['type'].upper()}:\n{item['content']}\n"
        
        # Add structured output instructions if needed
        output_instructions = ""
        if structured_output:
            output_instructions = "\n\n### OUTPUT FORMAT:\nProvide your response in valid JSON format.\n"
            
        return f"{context_text}\n\n### QUERY:\n{prompt}{output_instructions}"
    
    def _extract_sources(self, response: str, context: Optional[List[Dict[str, Any]]]) -> List[str]:
        """Extract source note IDs from context that were likely used in the response"""
        if not context:
            return []
            
        # Placeholder implementation - in a real system, this would use more
        # sophisticated NLP techniques to determine which sources were used
        return [item.get("id") for item in context if item.get("type") == "note"]
    
    def _extract_concepts(self, response: str) -> List[str]:
        """Extract concepts mentioned in the AI response"""
        # Placeholder implementation - in a real system, this would use NLP
        # techniques to extract concepts from the response
        return []
        
    async def analyze_note(self, content: str, context: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Analyze a note to extract concepts, categories, and relationships
        
        Args:
            content: The note content to analyze
            context: Optional additional context
            
        Returns:
            Dictionary with extraction results
        """
        prompt = f"""
        Analyze the following note and extract:
        1. Key concepts (nouns or noun phrases that represent distinct ideas)
        2. Philosophical categories that apply (from: Teleology, Causality, Epistemology, Ontology, Axiology, Phenomenology, Temporality)
        3. Suggested relationships between concepts and categories
        
        Note content:
        {content}
        
        For each concept, determine:
        - A brief description
        - Which philosophical categories apply (with confidence scores from 0.0 to 1.0)
        
        For each relationship, specify:
        - Source entity (concept or note)
        - Target entity (concept or category)
        - Relationship type
        - Weight or confidence score
        """
        
        result = await self.query(
            prompt, 
            context,
            prompt_type="analysis",
            structured_output=True
        )
        
        # Extract and format the results
        return result
    
    async def generate_confirmation_request(self, 
                                          proposed_actions: List[Dict[str, Any]], 
                                          user_input: str,
                                          conversation_history: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a user-friendly confirmation request for proposed actions
        
        Args:
            proposed_actions: List of actions to be confirmed
            user_input: The original user input that led to these actions
            conversation_history: Optional conversation history for context
            
        Returns:
            Dictionary with confirmation request text
        """
        # Format the proposed actions as a string
        actions_str = json.dumps(proposed_actions, indent=2)
        
        prompt = f"""
        The user has requested: "{user_input}"
        
        Based on this request, the system proposes the following actions:
        {actions_str}
        
        Please generate a clear, user-friendly summary of these proposed actions.
        Explain what changes will be made and why they align with the user's request.
        Use plain language that emphasizes the philosophical aspects where relevant.
        End with a polite confirmation request asking if the user would like to proceed with these actions.
        """
        
        context = []
        if conversation_history:
            context.append({
                "type": "conversation_history",
                "content": conversation_history
            })
            
        result = await self.query(
            prompt,
            context,
            prompt_type="confirmation"
        )
        
        return result
