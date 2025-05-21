"""
Note Processor

This module handles the processing, analysis, and categorization of notes.
It extracts concepts, assigns philosophical categories, and manages the
creation of graph relationships.
"""
from typing import Dict, List, Any, Optional
import asyncio

from backend.ai.manager import AIManager
from backend.db.graph_manager import GraphManager

class NoteProcessor:
    """
    Processes notes to extract concepts, assign categories, and create graph relationships
    """
    
    def __init__(self, ai_manager: AIManager, graph_manager: GraphManager):
        """
        Initialize the note processor
        
        Args:
            ai_manager: Instance of AIManager for AI processing
            graph_manager: Instance of GraphManager for database operations
        """
        self.ai_manager = ai_manager
        self.graph_manager = graph_manager
        
    async def process_note(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a note - extract concepts, assign categories, and store in graph
        
        Args:
            content: The note content to process
            metadata: Optional metadata for the note
            
        Returns:
            Dictionary with the processed note data including extracted concepts and categories
        """
        # Create the note in the graph database
        note = self.graph_manager.create_note(content, metadata)
        
        # Extract concepts and categories using AI
        extraction_result = await self._extract_concepts_and_categories(content)
        
        # Create concepts and relationships in the graph
        await self._create_graph_entities(note["id"], extraction_result)
        
        # Return the complete result
        return {
            "note": note,
            "concepts": extraction_result.get("concepts", []),
            "categories": extraction_result.get("categories", []),
            "relationships": extraction_result.get("relationships", [])
        }
        
    async def _extract_concepts_and_categories(self, content: str) -> Dict[str, Any]:
        """
        Use AI to extract concepts and categories from note content
        
        Args:
            content: The note content to analyze
            
        Returns:
            Dictionary with extracted concepts, categories, and suggested relationships
        """
        # Construct a prompt for the AI to extract concepts and categories
        prompt = f"""
        Analyze the following note and extract:
        1. Key concepts (nouns or noun phrases that represent distinct ideas)
        2. Philosophical categories that apply (from: Teleology, Causality, Epistemology, Ontology, Axiology, Phenomenology, Temporality)
        3. Suggested relationships between concepts and categories
        
        Note: {content}
        
        Format your response as JSON with these keys:
        - concepts: array of strings
        - categories: array of objects with 'name' and 'confidence' (0-1)
        - relationships: array of objects with 'source', 'target', and 'type'
        """
        
        # Query the AI
        result = await self.ai_manager.query(prompt)
        
        # In a real implementation, we would parse the JSON from the AI response
        # For now, we'll return a placeholder result
        return {
            "concepts": ["concept1", "concept2"],
            "categories": [
                {"name": "Epistemology", "confidence": 0.8},
                {"name": "Ontology", "confidence": 0.5}
            ],
            "relationships": [
                {"source": "note_id", "target": "concept1", "type": "ABOUT"},
                {"source": "concept1", "target": "Epistemology", "type": "BELONGS_TO"}
            ]
        }
        
    async def _create_graph_entities(self, note_id: str, extraction_result: Dict[str, Any]) -> None:
        """
        Create concepts, categories, and relationships in the graph based on extraction results
        
        Args:
            note_id: ID of the note being processed
            extraction_result: Result from concept/category extraction
        """
        # Create concepts and track their IDs
        concept_ids = {}
        for concept_name in extraction_result.get("concepts", []):
            concept = self.graph_manager.create_concept(concept_name)
            concept_ids[concept_name] = concept["id"]
            
            # Create relationship from note to concept
            self.graph_manager.create_relationship(
                note_id, 
                concept["id"], 
                "ABOUT", 
                {}
            )
        
        # Create categories and relationships
        for category in extraction_result.get("categories", []):
            # Create category relationship with confidence weight
            for concept_name, concept_id in concept_ids.items():
                self.graph_manager.create_relationship(
                    concept_id,
                    category["name"],  # Using name as ID for categories
                    "BELONGS_TO",
                    {"weight": category["confidence"]}
                )
