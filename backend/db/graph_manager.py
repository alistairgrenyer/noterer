"""
Graph Manager

This module provides a manager for Neo4j graph database operations.
"""
import os
from neo4j import GraphDatabase, Driver, AsyncDriver, basic_auth
from neo4j.exceptions import Neo4jError
from typing import Dict, List, Any, Optional, Union, Tuple

class GraphManager:
    """Manager for Neo4j graph database operations"""
    
    def __init__(self, uri: str = None, username: str = None, password: str = None):
        """
        Initialize the Neo4j connection
        
        Args:
            uri: Neo4j connection URI (default: from environment variable)
            username: Neo4j username (default: from environment variable)
            password: Neo4j password (default: from environment variable)
        """
        self.uri = uri or os.getenv("NEO4J_URI", "neo4j://localhost:7687")
        self.username = username or os.getenv("NEO4J_USERNAME", "neo4j")
        self.password = password or os.getenv("NEO4J_PASSWORD", "password")
        self.driver = GraphDatabase.driver(
            self.uri, 
            auth=basic_auth(self.username, self.password)
        )
        # Test connection on initialization
        self._test_connection()
    
    def _test_connection(self) -> None:
        """Test the Neo4j connection"""
        with self.driver.session() as session:
            # Simple query to test connection
            result = session.run("RETURN 1 AS num")
            assert result.single()["num"] == 1
            
    def close(self) -> None:
        """Close the Neo4j connection"""
        self.driver.close()
    
    # Note CRUD operations
    
    def create_note(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a new note in the graph database
        
        Args:
            content: The content of the note
            metadata: Optional metadata for the note
            
        Returns:
            Dictionary with the created note data
        """
        with self.driver.session() as session:
            result = session.write_transaction(
                self._create_note_tx, content, metadata or {}
            )
            return result
    
    def _create_note_tx(self, tx, content: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Transaction function for creating a note"""
        query = """
        CREATE (n:Note {
            id: randomUUID(),
            content: $content,
            created_at: datetime(),
            updated_at: datetime()
        })
        SET n += $metadata
        RETURN n
        """
        result = tx.run(query, content=content, metadata=metadata)
        record = result.single()
        if record:
            return dict(record["n"])
        return {}
    
    def get_note(self, note_id: str) -> Optional[Dict[str, Any]]:
        """Get a note by ID"""
        with self.driver.session() as session:
            result = session.read_transaction(self._get_note_tx, note_id)
            return result
    
    def _get_note_tx(self, tx, note_id: str) -> Optional[Dict[str, Any]]:
        """Transaction function for getting a note"""
        query = """
        MATCH (n:Note {id: $note_id})
        RETURN n
        """
        result = tx.run(query, note_id=note_id)
        record = result.single()
        if record:
            return dict(record["n"])
        return None
    
    def get_notes(self, limit: int = 10, skip: int = 0) -> List[Dict[str, Any]]:
        """Get multiple notes with pagination"""
        with self.driver.session() as session:
            result = session.read_transaction(self._get_notes_tx, limit, skip)
            return result
    
    def _get_notes_tx(self, tx, limit: int, skip: int) -> List[Dict[str, Any]]:
        """Transaction function for getting multiple notes"""
        query = """
        MATCH (n:Note)
        RETURN n
        ORDER BY n.created_at DESC
        SKIP $skip
        LIMIT $limit
        """
        result = tx.run(query, limit=limit, skip=skip)
        return [dict(record["n"]) for record in result]
    
    def update_note(self, note_id: str, content: Optional[str] = None, 
                   metadata: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Update a note by ID"""
        with self.driver.session() as session:
            result = session.write_transaction(
                self._update_note_tx, note_id, content, metadata or {}
            )
            return result
    
    def _update_note_tx(self, tx, note_id: str, content: Optional[str], 
                       metadata: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Transaction function for updating a note"""
        # Build dynamic SET clause
        set_clauses = ["n.updated_at = datetime()"]
        params = {"note_id": note_id, "metadata": metadata}
        
        if content is not None:
            set_clauses.append("n.content = $content")
            params["content"] = content
            
        for key in metadata:
            set_clauses.append(f"n.{key} = $metadata.{key}")
            
        set_clause = ", ".join(set_clauses)
        
        query = f"""
        MATCH (n:Note {{id: $note_id}})
        SET {set_clause}
        RETURN n
        """
        result = tx.run(query, **params)
        record = result.single()
        if record:
            return dict(record["n"])
        return None
    
    def delete_note(self, note_id: str) -> bool:
        """Delete a note by ID"""
        with self.driver.session() as session:
            result = session.write_transaction(self._delete_note_tx, note_id)
            return result
    
    def _delete_note_tx(self, tx, note_id: str) -> bool:
        """Transaction function for deleting a note"""
        query = """
        MATCH (n:Note {id: $note_id})
        DETACH DELETE n
        RETURN count(n) as deleted_count
        """
        result = tx.run(query, note_id=note_id)
        record = result.single()
        return record and record["deleted_count"] > 0
    
    # Concept operations
    
    def create_concept(self, name: str, description: Optional[str] = None,
                      categories: Optional[List[str]] = None) -> Dict[str, Any]:
        """Create a new concept in the graph database"""
        with self.driver.session() as session:
            result = session.write_transaction(
                self._create_concept_tx, name, description, categories or []
            )
            return result
    
    def _create_concept_tx(self, tx, name: str, description: Optional[str],
                          categories: List[str]) -> Dict[str, Any]:
        """Transaction function for creating a concept"""
        query = """
        CREATE (c:Concept {
            id: randomUUID(),
            name: $name,
            description: $description
        })
        RETURN c
        """
        result = tx.run(query, name=name, description=description)
        record = result.single()
        concept = dict(record["c"])
        
        # Create relationships to categories if provided
        if categories:
            for category in categories:
                tx.run("""
                MATCH (c:Concept {id: $concept_id})
                MERGE (cat:Category {name: $category})
                MERGE (c)-[:BELONGS_TO]->(cat)
                """, concept_id=concept["id"], category=category)
        
        return concept
    
    # Relationship operations
    
    def create_relationship(self, source_id: str, target_id: str, 
                           relationship_type: str, properties: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a relationship between two nodes"""
        with self.driver.session() as session:
            result = session.write_transaction(
                self._create_relationship_tx, source_id, target_id, relationship_type, properties or {}
            )
            return result
    
    def _create_relationship_tx(self, tx, source_id: str, target_id: str,
                              relationship_type: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Transaction function for creating a relationship"""
        # Determine node labels based on IDs
        query = f"""
        MATCH (source {{id: $source_id}}), (target {{id: $target_id}})
        MERGE (source)-[r:{relationship_type} {{created_at: datetime()}}]->(target)
        SET r += $properties
        RETURN source, r, target
        """
        result = tx.run(query, source_id=source_id, target_id=target_id, properties=properties)
        record = result.single()
        if record:
            return {
                "source": dict(record["source"]),
                "relationship": dict(record["r"]),
                "target": dict(record["target"]),
            }
        return {}
