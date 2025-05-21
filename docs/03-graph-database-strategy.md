# Graph Database Strategy

## Overview

Noterer uses Neo4j as its primary database, leveraging graph relationships to create a rich network of connected notes, concepts, and philosophical categories. This document outlines our graph data model, query patterns, and optimization strategies.

## Graph Data Model

### Node Types

```
Nodes
├── Note
│   ├── id: UUID
│   ├── content: String
│   ├── created_at: DateTime
│   ├── updated_at: DateTime
│   └── tags: String[]
├── Concept
│   ├── id: UUID
│   ├── name: String
│   └── description: String
└── Category
    ├── name: String
    └── description: String
```

### Relationship Types

```
Relationships
├── ABOUT
│   ├── From: Note
│   ├── To: Concept
│   └── Properties: {}
├── RELATES_TO
│   ├── From: Note
│   ├── To: Note
│   ├── Properties:
│   │   ├── type: String (causal, temporal, contrast, etc.)
│   │   └── weight: Float (0.0-1.0)
├── BELONGS_TO
│   ├── From: Concept
│   ├── To: Category
│   ├── Properties:
│   │   └── weight: Float (0.0-1.0)
└── EMBODIES
    ├── From: Note
    ├── To: Category
    ├── Properties:
    │   └── weight: Float (0.0-1.0)
```

### Data Model Diagram

```
(Note)-[:ABOUT]->(Concept)-[:BELONGS_TO]->(Category)
  |                  |
  |                  |
  v                  v
(Note)<-[:RELATES_TO]->(Note)
  |
  |
  v
(Category)<-[:EMBODIES]-(Note)
```

## Database Operations

### Core Operations

1. **Note Management**
   - Create, read, update, delete notes
   - Attach tags and metadata
   - Track creation and update timestamps

2. **Concept Management**
   - Extract and store concepts from notes
   - Link concepts to philosophical categories
   - Maintain relationships between concepts

3. **Relationship Management**
   - Create relationships between nodes
   - Assign relationship types and weights
   - Update relationship properties based on AI analysis

4. **Query and Traversal**
   - Find related notes and concepts
   - Traverse the graph based on philosophical categories
   - Apply weighted path algorithms for contextual relevance

### Cypher Query Patterns

#### Creating Notes and Concepts

```cypher
// Create a note
CREATE (n:Note {
    id: randomUUID(),
    content: $content,
    created_at: datetime(),
    updated_at: datetime()
})
RETURN n

// Create a concept and link to categories
MERGE (c:Concept {name: $name})
ON CREATE SET c.id = randomUUID(), c.description = $description
WITH c
UNWIND $categories AS category
MERGE (cat:Category {name: category})
MERGE (c)-[:BELONGS_TO {weight: $weight}]->(cat)
RETURN c
```

#### Establishing Relationships

```cypher
// Link note to concept
MATCH (n:Note {id: $note_id})
MATCH (c:Concept {id: $concept_id})
MERGE (n)-[:ABOUT]->(c)
RETURN n, c

// Create relationship between notes
MATCH (n1:Note {id: $source_id})
MATCH (n2:Note {id: $target_id})
MERGE (n1)-[r:RELATES_TO {
    type: $rel_type,
    weight: $weight,
    created_at: datetime()
}]->(n2)
RETURN n1, r, n2
```

#### Contextual Queries

```cypher
// Find contextually related notes with weighted paths
MATCH path = (n:Note {id: $note_id})-[:ABOUT|RELATES_TO*1..3]-(related:Note)
WITH related, relationships(path) AS rels,
     reduce(weight = 1.0, r IN relationships(path) | 
        weight * CASE 
                   WHEN type(r) = 'ABOUT' THEN 0.9
                   WHEN type(r) = 'RELATES_TO' THEN r.weight
                   ELSE 0.5
                 END
     ) AS path_weight
RETURN related, path_weight
ORDER BY path_weight DESC
LIMIT 10

// Find notes by philosophical category
MATCH (n:Note)-[:ABOUT]->(c:Concept)-[:BELONGS_TO]->(cat:Category {name: $category})
RETURN n
ORDER BY n.created_at DESC
LIMIT 20
```

## Optimization Strategies

### Indexing Strategy

```cypher
// Ensure uniqueness for Note IDs
CREATE CONSTRAINT note_id_unique IF NOT EXISTS
FOR (n:Note) REQUIRE n.id IS UNIQUE

// Ensure uniqueness for Concept names
CREATE CONSTRAINT concept_name_unique IF NOT EXISTS
FOR (c:Concept) REQUIRE c.name IS UNIQUE

// Ensure uniqueness for Category names
CREATE CONSTRAINT category_name_unique IF NOT EXISTS
FOR (cat:Category) REQUIRE cat.name IS UNIQUE

// Index for Note content search
CREATE TEXT INDEX note_content_index IF NOT EXISTS
FOR (n:Note) ON (n.content)

// Index for Note created_at timestamp
CREATE INDEX note_timestamp_index IF NOT EXISTS
FOR (n:Note) ON (n.created_at)
```

### Query Optimization

1. **Pattern-Based Optimization**
   - Use parameterized Cypher queries
   - Leverage MERGE for upsert operations
   - Apply LIMIT to constrain result sets

2. **Batch Processing**
   - Process large operations in batches
   - Use UNWIND for bulk operations
   - Implement transactions for data consistency

3. **Cache Strategy**
   - Cache frequently accessed nodes (categories, common concepts)
   - Implement application-level caching for query results
   - Use Neo4j's query caching capabilities

## Philosophical Weighting Mechanism

The graph database implements a philosophical weighting system that influences traversal and retrieval:

```yaml
rules:
  priority_order: [Teleology, Causality, Epistemology] # Defines preferred reasoning paths
  category_weights: {Teleology: 1.2, Causality: 1.0, Epistemology: 0.8} # Boosts relevance
  relationship_weights:
    RELATES_TO: {causal: 1.0, temporal: 0.6, contrast: 0.4}
    EMBODIES: 0.8
  recency_decay: # Example: function: exp(-age_in_days / 30)
```

These rules translate into Cypher query modifications that adjust path weights during traversal:

```cypher
// Apply philosophical weighting in traversal
MATCH path = (n:Note {id: $note_id})-[*1..3]-(related:Note)
WITH related, relationships(path) AS rels,
     // Calculate philosophical weight based on categories and relationship types
     reduce(weight = 1.0, r IN relationships(path) | 
        weight * CASE 
                   WHEN type(r) = 'EMBODIES' AND exists(r.category) THEN
                     CASE r.category
                       WHEN 'Teleology' THEN 1.2
                       WHEN 'Causality' THEN 1.0
                       WHEN 'Epistemology' THEN 0.8
                       ELSE 0.7
                     END
                   WHEN type(r) = 'RELATES_TO' AND exists(r.type) THEN
                     CASE r.type
                       WHEN 'causal' THEN 1.0
                       WHEN 'temporal' THEN 0.6
                       WHEN 'contrast' THEN 0.4
                       ELSE 0.5
                     END
                   ELSE 0.5
                 END
     ) AS phil_weight,
     // Apply recency decay
     exp(-(duration.inDays(datetime(), related.created_at).days) / 30) AS recency_factor
WITH related, phil_weight * recency_factor AS final_weight
RETURN related, final_weight
ORDER BY final_weight DESC
LIMIT 10
```

## Data Migration and Evolution

### Schema Evolution Strategy

1. **Backward Compatibility**
   - Ensure new schemas are compatible with existing data
   - Add properties incrementally with default values
   - Maintain compatibility with existing queries

2. **Migration Scripts**
   - Version-controlled migration scripts
   - Incremental node and relationship updates
   - Data validation during migrations

3. **Dataset Backups**
   - Regular database dumps
   - Point-in-time recovery capability
   - Test restores to verify backup integrity

## Graph Visualization

The database model supports visualization capabilities:

1. **Note Cluster Visualization**
   - Group related notes by concepts
   - Size nodes by importance or recency
   - Color-code by philosophical category

2. **Concept Maps**
   - Show concept relationships and hierarchies
   - Highlight frequently connected concepts
   - Visualize conceptual distance

3. **Category Distribution**
   - Analyze distribution of philosophical categories
   - Track evolution of categorical weighting over time
   - Identify dominant philosophical frameworks

## Future Directions

1. **Graph Algorithms**
   - Implement PageRank for concept importance
   - Apply community detection for note clustering
   - Use similarity measures for concept mapping

2. **Vector Integration**
   - Add vector embeddings to nodes
   - Support hybrid search (graph + vector similarity)
   - Enable semantic clustering of notes and concepts

3. **Temporal Analysis**
   - Track concept evolution over time
   - Analyze changing relationships between concepts
   - Implement temporal graph views
