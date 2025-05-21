# AI Integration Strategy

## Overview

Noterer leverages AI to enhance note-taking through intelligent processing, concept extraction, and philosophical categorization. This document outlines our approach to AI integration, including model selection, prompt engineering, graph integration, and our confirmation-driven conversational interaction model.

## AI Architecture

```
AI System
├── AIManager (Core Interface)
├── Conversational Flow Controller
├── Prompt Templates
├── Response Processors
│   ├── Intent Analyzer
│   ├── Change Summarizer
│   └── Confirmation Handler
├── Graph Integration
└── Philosophical Framework
```

## Model Selection

### Current Implementation

- **Primary Model**: GPT-4o (via OpenAI API)
- **Rationale**: Advanced reasoning capabilities, superior context understanding, and ability to work with complex philosophical concepts.

### Considerations for Alternative Models

- **Local Models**: Potential future support for local LLMs like Llama 3 for privacy-conscious users
- **Specialized Models**: Domain-specific fine-tuned models for philosophical reasoning
- **Multi-Model Approach**: Different models for different tasks (e.g., concept extraction vs. query answering)

## Conversational Interaction Flow

Noterer implements a confirmation-driven conversational interaction model that emphasizes transparency and user control while maintaining a natural dialogue experience. This model has been fully implemented in the backend and frontend components.

### Control Flow

1. **User Input Phase**
   - User provides input as part of an ongoing conversation via the ConversationView UI
   - Input is processed by the ConversationController and sent to the AIManager
   - System determines the user's intent and potential actions through prompt analysis

2. **Analysis Phase**
   - AI analyzes input against existing notes and graph context retrieved from Neo4j
   - The AIManager determines proposed changes using structured prompts
   - Identifies related actions for graph updates (notes, concepts, relationships)
   - Results are returned to the ConversationController for processing

3. **Confirmation Phase**
   - AI generates a clear summary of intended changes and actions
   - The frontend ConversationView presents a confirmation dialog with proposed actions
   - User can review and choose to confirm or reject the proposed changes as a whole

4. **Execution Phase**
   - Upon confirmation, the ConversationController executes actions using the GraphManager
   - Changes are applied to the Neo4j knowledge graph in a transaction
   - Results are returned to the frontend with feedback on executed actions

5. **Feedback Loop**
   - Results are added to conversation context and displayed in the UI
   - ConversationController maintains stateful context for ongoing conversations
   - User can continue the conversation with refined inputs

### Conversation Flow Diagram

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  User Input  │────>│  AI Analysis │────>│ Confirmation │────>│  Execution  │
└─────────────┘     │  & Summary   │     │   Request   │     │  of Actions │
      ^             └─────────────┘     └─────────────┘     └─────────────┘
      │                                        │                    │
      │                                        │                    │
      └────────────────────────────────────────┴────────────────────┘
                       Conversation Continues
```

## Prompt Engineering

### Key Prompt Categories

1. **Concept Extraction Prompts**
   - Extract key concepts from note content
   - Identify relationships between concepts
   - Map concepts to existing knowledge graph

2. **Philosophical Categorization Prompts**
   - Categorize concepts according to philosophical frameworks
   - Assign confidence scores to categorizations
   - Apply rule-based weighting systems

3. **Query Response Prompts**
   - Ground responses in existing notes/concepts
   - Maintain philosophical coherence
   - Provide context-aware responses
   - Generate clear summaries of intended changes
   - Request confirmation before executing actions

### Prompt Structure

All prompts follow a consistent structure:
- System context (role and capabilities)
- Specific task instructions
- Input data (note content, conversation history, context)
- Output format specification
- Reasoning steps (for complex tasks)
- **Confirmation guidelines** (for action-oriented tasks)

### Example Prompt Templates

#### Concept Extraction with Confirmation

```
You are an AI assistant specialized in philosophical note analysis.

Task: Extract key concepts from the following note and categorize them according to philosophical frameworks. Then, present a summary to the user for confirmation before proceeding.

Conversation history:
{conversation_history}

Note content:
{note_content}

Please follow these steps:

1. Analyze the note to identify:
   - Main concepts (nouns or phrases representing distinct ideas)
   - Philosophical categories that apply to each concept
   - Relationships between concepts

2. Generate a user-friendly summary of your findings, including:
   - Key concepts you've identified
   - Philosophical categorizations and their significance
   - Relationships you've discovered
   - Any actions you recommend (creating new concepts, updating relationships)

3. Ask the user for confirmation before proceeding with these changes.

First provide your internal analysis as a structured JSON object:
{
  "concepts": [
    {
      "name": "string",
      "description": "string",
      "categories": [{"name": "string", "confidence": float}]
    }
  ],
  "relationships": [
    {
      "source": "string",
      "target": "string",
      "type": "string",
      "properties": {"weight": float}
    }
  ]
}

Then provide a natural language summary and confirmation request for the user.
```

#### Conversational Action Prompt

```
You are an AI assistant that helps manage notes and related tasks in Noterer.

Task: Analyze the user's request, determine necessary actions, and present a summary for confirmation.

Conversation history:
{conversation_history}

Current user input:
{user_input}

Relevant context from knowledge graph:
{graph_context}

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
```

## Response Processing

### Processing Pipeline

1. **Raw Response Parsing**
   - Extract JSON or structured content
   - Validate against expected schema
   - Handle malformed responses

2. **Intent Analysis**
   - Identify user's primary intent
   - Determine required actions and changes
   - Generate structured action plan

3. **Change Summarization**
   - Create user-friendly summary of proposed changes
   - Translate technical details into clear explanations
   - Highlight philosophical implications

4. **Confirmation Management**
   - Present change summary to user
   - Process user confirmation or rejection
   - Handle partial confirmations or clarifications

5. **Concept Validation**
   - Check for duplicate concepts
   - Validate against existing concept database
   - Merge similar concepts

6. **Graph Integration**
   - Create new nodes for novel concepts
   - Establish relationships
   - Update weights and properties

### Confidence Scoring

All AI-derived categorizations include confidence scores (0.0-1.0) that:
- Influence the weight of relationships in the graph
- Help with ranking and retrieving relevant notes
- Provide transparency about AI certainty
- Inform the level of detail in confirmation summaries (more details for lower confidence actions)

## Philosophical Framework Integration

The AI system incorporates understanding of several philosophical frameworks:

1. **Epistemological Framework** (knowledge origins and validity)
   - Empiricism, Rationalism, Constructivism
   - Applied to concept validity and certainty

2. **Ontological Framework** (nature of reality and being)
   - Categories of existence and properties
   - Applied to concept hierarchies and relationships

3. **Teleological Framework** (purpose and goal-orientation)
   - Intentionality and purpose
   - Applied to notes about objectives, plans, and projects

4. **Categorical Weighting System**

```yaml
category_weights:
  Teleology: 1.2   # Prioritizes goal-oriented concepts
  Causality: 1.0   # Standard weight for cause-effect relationships
  Epistemology: 0.8 # Knowledge-related concepts
  Ontology: 0.9    # Reality/being concepts
  Axiology: 0.7    # Value-related concepts
  Phenomenology: 0.8 # Experience-related concepts
  Temporality: 0.6  # Time-related concepts
```

## Context Management

### Graph-Based Context

- AI queries leverage the Neo4j graph for contextual information
- Traversal algorithms provide relevant notes and concepts
- Temporal context considers recency and relevance

### Conversation Memory

- Maintain complete memory of the current conversation
- Track confirmed and rejected actions for learning
- Store user preferences and interaction patterns
- Identify recurring themes across conversation sessions

### Context Window Strategy

- Optimize token usage by selecting most relevant prior notes and conversation turns
- Apply rule-based context selection (recency, relevance, explicit references, confirmation status)
- Support multi-turn refinement of actions and concepts
- Maintain coherence across confirmation/rejection cycles

## Challenges and Mitigations

1. **Hallucination Management**
   - Ground responses in existing notes and concepts
   - Explicit citation of source notes
   - Confidence scoring for uncertain responses
   - **User confirmation before executing actions prevents implementation of hallucinated concepts**

2. **Philosophical Bias**
   - Balanced representation of philosophical traditions
   - Transparency about categorical assumptions
   - User configuration of preferred philosophical frameworks
   - Clear explanations of philosophical reasoning in confirmation requests

3. **Context Limitations**
   - Smart context selection algorithms
   - Summarization of lengthy context
   - Hierarchical context retrieval based on graph relationships

4. **Confirmation Friction**
   - Batch related changes for single confirmation (avoid confirmation fatigue)
   - Adapt detail level based on user preferences and action significance
   - Provide easy ways to modify proposed actions without starting over
   - Learn from confirmation patterns to improve future suggestions

## Future Directions

1. **Fine-tuning**
   - Domain-specific fine-tuning for philosophical note-taking
   - Few-shot learning for improved concept extraction
   - Training on confirmation data to improve action prediction

2. **Multi-modal Support**
   - Processing images with philosophical significance
   - Audio note transcription and analysis
   - Visual confirmation interfaces (showing graph changes)

3. **Reinforcement Learning**
   - Improve responses based on confirmation/rejection patterns
   - Adapt to individual user's philosophical preferences and writing style
   - Optimize confirmation requests to minimize user friction

4. **Advanced Conversation Management**
   - Multi-session memory for long-term projects
   - Proactive suggestion refinement based on rejection patterns
   - Adaptive detail level in confirmations based on user expertise
