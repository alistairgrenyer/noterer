# Noterer: AI-Powered Graph-Based Note Taker

**Project Vision:** To create an intelligent note-taking desktop application that leverages an AI agent to capture, process, and organize information into a Neo4j graph database. This novel structure will enable the AI to maintain long-term context and facilitate intuitive interaction with historical conversation data.

**Core Technologies:**
*   **Backend:** Python with FastAPI
*   **Database:** Neo4j (Graph Database)
*   **User Interface:** Python-based desktop application with CustomTkinter
*   **AI Integration:** OpenAI GPT-4o via API

**Key Features (High-Level):**
1.  **Intelligent AI Agent Interaction with Confirmation Flow:**
    *   Users interact with an AI that proactively summarizes information and asks clarifying questions.
    *   The AI recalls and references past notes, hedging against redundancy by intelligently updating existing notes or creating new, related entries.
    *   **Confirmation-Driven Interaction:** The AI proposes changes and actions for explicit user approval before execution, ensuring transparency and user control.
2.  **Philosophically-Informed Graph Organization:**
    *   AI responses and user inputs are structured and stored as nodes and relationships in Neo4j.
    *   Notes are organized using deeper conceptual and philosophical categories (e.g., Teleology, Causality, Epistemology, Ontology, Axiology, Phenomenology, Temporality) to enhance semantic meaning and guide AI decision-making.
    *   **Graph Schema (Conceptual):**
        *   Nodes: `:Note` (a single note or user/AI utterance), `:Concept` (abstract topics), `:Category` (philosophical categories).
        *   Relationships: Examples include `(:Note)-[:ABOUT]->(:Concept)`, `(:Note)-[:EMBODIES {weight: float}]->(:Category)`, `(:Note)-[:RELATES_TO {type: string, weight: float}]->(:Note)`, `(:Concept)-[:BELONGS_TO]->(:Category)`.
3.  **Weighted Contextual Retrieval & Decision Making:**
    *   The graph structure, enriched with philosophical categories, allows the AI to access and utilize historical context effectively for retrieval and decision-making (e.g., when to update vs. create new notes).
    *   A rule-based weighting system (considering relationship types, category relevance, and recency) guides graph traversal and AI reasoning.
    *   *Example Rule Logic (Conceptual):*
        ```yaml
        rules:
          priority_order: [Teleology, Causality, Epistemology] # Defines preferred reasoning paths
          category_weights: {Teleology: 1.2, Causality: 1.0, Epistemology: 0.8} # Boosts relevance
          relationship_weights:
            RELATES_TO: {causal: 1.0, temporal: 0.6, contrast: 0.4}
            EMBODIES: 0.8
          recency_decay: # Example: function: exp(-age_in_days / 30)
        ```
4.  **Desktop Application:** A user-friendly interface for note-taking and interaction with the AI and graph data.

**Project Architecture:**

*   **Decoupled Architecture Design:**
    *   The application follows a clear separation between backend (core logic, AI, database) and frontend (UI) components.
    *   Communication between layers happens through well-defined APIs, allowing different frontend implementations to utilize the same backend services.

*   **Backend Implementation:**
    *   **Core Components:**
        *   `AIManager`: Interfaces with the chosen LLM (local or API-based), handles prompt construction, and processes responses.
        *   `GraphManager`: Manages all Neo4j operations (connections, transactions, query execution).
        *   `NoteProcessor`: Processes notes, extracts concepts, and applies philosophical categorization.
        *   `BackendAPI`: Provides a clean interface for frontend components (implemented as a RESTful API using FastAPI).
    *   **Implementation:**
        *   Python-based microservices architecture with dedicated modules for each responsibility.
        *   Dependency injection patterns to ensure testability and flexibility.
        *   Asynchronous design where appropriate (especially for API and database interactions).

*   **Frontend Implementation:**
    *   **Initial UI (Desktop):**
        *   Built with CustomTkinter for a modern, responsive desktop experience.
        *   Clear separation of UI components (views) from application logic (controllers).
        *   Asynchronous communication with the backend API to maintain UI responsiveness.
    *   **Future Extensibility:**
        *   The decoupled nature allows for alternative frontends (web, mobile) using the same backend API.

*   **Database Implementation:**
    *   Neo4j graph database accessed through the official Python driver.
    *   Predefined Cypher query templates for common operations.
    *   Optimized indexing strategy for concept and category retrieval.
    *   Transaction management to ensure data integrity.

*   **API Layer Design:**
    *   RESTful API built with FastAPI providing:
        *   `/notes` endpoints for CRUD operations on notes.
        *   `/concepts` endpoints for concept management.
        *   `/graph` endpoints for relationship queries and traversals.
        *   `/ai` endpoints for direct AI interactions.
        *   `/conversation` endpoints for confirmation-driven conversational flow.
    *   Asynchronous request handling.
    *   OpenAPI documentation generated automatically.
    *   Authentication and rate limiting for future multi-user scenarios.

*   **Project Directory Structure:**

```
noterer/
├── backend/
│   ├── api/                 # FastAPI implementation
│   │   ├── __init__.py
│   │   ├── app.py           # Main API application setup
│   │   ├── routes/          # API endpoints by resource
│   │   │   ├── __init__.py
│   │   │   ├── ai.py        # AI interaction endpoints
│   │   │   ├── concepts.py  # Concept management endpoints
│   │   │   ├── conversation.py # Conversation flow endpoints
│   │   │   ├── graph.py     # Graph query endpoints
│   │   │   └── notes.py     # Note CRUD endpoints
│   │   └── models/          # Pydantic models for request/response
│   ├── ai/                  # AI integration
│   │   ├── __init__.py
│   │   ├── manager.py       # AI interaction handling
│   │   ├── conversation_controller.py # Confirmation-driven conversation flow
│   │   └── note_processor.py # Note analysis and processing
│   ├── db/                  # Database operations
│   │   ├── __init__.py
│   │   ├── graph_manager.py # Neo4j connection and operations
│   │   ├── models.py        # Graph data models
│   │   └── queries/         # Cypher query templates
│   ├── core/                # Core business logic
│   │   └── __init__.py
│   └── utils/               # Shared utilities
├── frontend/
│   ├── __init__.py
│   ├── api_client.py       # Backend API client
│   ├── views/              # UI components
│   │   ├── __init__.py
│   │   ├── main_window.py  # Main application window
│   │   ├── note_editor.py  # Note editing interface
│   │   └── conversation_view.py # Conversation interface with confirmation UI
│   ├── services/           # Frontend services
│   │   ├── __init__.py
│   │   └── conversation_service.py # Service for conversation API interactions
│   ├── controllers/        # UI logic
│   │   ├── __init__.py
│   │   └── note_controller.py
│   └── assets/             # UI resources
├── docs/                   # Project documentation
│   ├── 01-architecture-overview.md   # Architecture documentation
│   ├── 02-ai-integration-strategy.md # AI strategy documentation
│   ├── 03-graph-database-strategy.md # Graph DB strategy
│   ├── 04-frontend-ui-strategy.md    # Frontend UI strategy
│   ├── 05-development-roadmap.md     # Development roadmap
│   ├── 06-confirmation_flow.md       # Confirmation flow documentation
│   └── implementation-summary.md     # Implementation summary
├── tests/                  # Unit and integration tests
│   ├── backend/
│   └── frontend/
├── config/                 # Configuration files
├── scripts/                # Utility scripts
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── .env.example           # Example environment variables
└── README.md
```

*   **Communication Flow:**
    1. User interacts with the frontend UI (note input, queries)
    2. Frontend controllers process user input and make API calls to the backend
    3. Backend API routes the request to appropriate core components
    4. Core components process the request, often involving AI and database operations
    5. Results flow back through the API to the frontend for display
    6. Graph data is continuously updated and maintained through this cycle

**Current Project Status:**
*   **Phase 1: Foundation (Completed)**
    *   [x] Define project vision and scope (README.md).
    *   [x] Set up project structure.
    *   [x] Initial Neo4j setup and connection testing.
    *   [x] Basic UI with CustomTkinter implementation.

*   **Phase 2: Core Functionality (Current)**
    *   [x] AI integration with OpenAI API.
    *   [x] Implement confirmation-driven conversational flow.
    *   [x] Graph database operations for notes and concepts.
    *   [ ] Complete note management functionality.
    *   [ ] Functional note editor with real-time saving.

**Future Phases (Outline):**
*   **Phase 3: Advanced Features**
    *   Philosophical categorization engine.
    *   Weighted graph traversal for context.
    *   Basic graph visualization UI.
    *   Advanced search with filtering options.
    *   Enhanced UI development.

*   **Phase 4: Refinement & Expansion**
    *   Performance optimization for large datasets.
    *   Advanced search and querying over the graph.
    *   Contextual summarization and insights from notes.
    *   User authentication and data security.
    *   Potential web or mobile interface prototypes.

**Roadmap & Milestones:**
*   **(To be defined)**

**How to Contribute:**
*   **(To be defined - for now, this is a solo project)**