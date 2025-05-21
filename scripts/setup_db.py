"""
Neo4j Database Setup Script

This script initializes the Neo4j database with the required schema for Noterer,
creating constraints and indexes for optimal performance.
"""
import os
import sys
import time
from dotenv import load_dotenv
from neo4j import GraphDatabase, exceptions

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load environment variables
load_dotenv()

# Neo4j connection parameters
URI = os.getenv("NEO4J_URI", "neo4j://localhost:7687")
USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

def setup_database():
    """Set up the Neo4j database with schema, constraints, and indexes"""
    print(f"Connecting to Neo4j database at {URI}...")
    
    try:
        # Create driver
        driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))
        
        # Test connection
        with driver.session() as session:
            result = session.run("RETURN 1 AS num")
            assert result.single()["num"] == 1
            print("Connection successful!")
            
        # Create schema constraints and indexes
        with driver.session() as session:
            # Create constraints
            print("Creating constraints...")
            
            # Ensure uniqueness for Note IDs
            session.run("""
            CREATE CONSTRAINT note_id_unique IF NOT EXISTS
            FOR (n:Note) REQUIRE n.id IS UNIQUE
            """)
            
            # Ensure uniqueness for Concept names
            session.run("""
            CREATE CONSTRAINT concept_name_unique IF NOT EXISTS
            FOR (c:Concept) REQUIRE c.name IS UNIQUE
            """)
            
            # Ensure uniqueness for Category names
            session.run("""
            CREATE CONSTRAINT category_name_unique IF NOT EXISTS
            FOR (cat:Category) REQUIRE cat.name IS UNIQUE
            """)
            
            # Create indexes
            print("Creating indexes...")
            
            # Index for Note content search
            session.run("""
            CREATE TEXT INDEX note_content_index IF NOT EXISTS
            FOR (n:Note) ON (n.content)
            """)
            
            # Index for Note created_at timestamp
            session.run("""
            CREATE INDEX note_timestamp_index IF NOT EXISTS
            FOR (n:Note) ON (n.created_at)
            """)
            
            # Create philosophical categories
            print("Creating philosophical categories...")
            categories = [
                "Teleology",
                "Causality", 
                "Epistemology", 
                "Ontology", 
                "Axiology", 
                "Phenomenology", 
                "Temporality"
            ]
            
            for category in categories:
                session.run("""
                MERGE (c:Category {name: $name})
                RETURN c
                """, name=category)
                
            # Create sample data if running in test mode
            if "--with-samples" in sys.argv:
                print("Creating sample data...")
                
                # Sample note
                session.run("""
                CREATE (n:Note {
                    id: randomUUID(),
                    content: "Philosophy is the study of fundamental questions about existence, knowledge, values, reason, mind, and language.",
                    created_at: datetime(),
                    updated_at: datetime()
                })
                RETURN n
                """)
                
                # Sample concepts
                session.run("""
                MERGE (c1:Concept {name: "Philosophy"})
                MERGE (c2:Concept {name: "Knowledge"})
                MERGE (c3:Concept {name: "Existence"})
                
                WITH c1, c2, c3
                
                MATCH (n:Note) WHERE n.content CONTAINS "Philosophy"
                MATCH (e:Category {name: "Epistemology"})
                MATCH (o:Category {name: "Ontology"})
                
                MERGE (n)-[:ABOUT]->(c1)
                MERGE (n)-[:ABOUT]->(c2)
                MERGE (n)-[:ABOUT]->(c3)
                MERGE (c2)-[:BELONGS_TO {weight: 0.9}]->(e)
                MERGE (c3)-[:BELONGS_TO {weight: 0.8}]->(o)
                """)
                
            print("Database setup complete!")
            
    except exceptions.AuthError:
        print("Authentication error. Please check your Neo4j username and password.")
        return False
    except exceptions.ServiceUnavailable:
        print("Neo4j database is not available. Please ensure it's running.")
        return False
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return False
    finally:
        if 'driver' in locals():
            driver.close()
            
    return True

if __name__ == "__main__":
    setup_database()
