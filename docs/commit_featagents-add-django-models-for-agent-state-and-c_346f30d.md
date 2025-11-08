# Documentation for Commit 346f30d

**Commit Hash:** 346f30dab1c97a45dbfd6ab9e05fee24951be3df
**Commit Message:** feat(agents): add Django models for agent state and campaign management
**Generated:** Sat Nov  8 00:19:29 EST 2025
**Repository:** aiatl

---

## Technical Documentation: Git Diff Analysis

### 1. Summary

This significant refactor transitions the Janus Multi-Agent System's state and data management from an implicit/in-memory approach to a robust, persistent database-driven architecture using Django ORM. Key components like campaigns, posts, content variants, agent memory, and conversation history are now explicitly modeled and stored in a database, enhancing reliability, scalability, and data integrity.

### 2. Changes

*   **Deletion of `backend/src/agents/__init__.py` Exports**: The `__init__.py` file in the `agents` package has been emptied. This removes direct package-level imports for all agents (`OrchestratorAgent`, `StrategyPlannerAgent`, etc.) and state management classes (`AgentState`, `Campaign`, `Post`, `ContentVariant`, `state`).
*   **Introduction of Django Models for State Management**:
    *   **`AgentMemory`**: A new model to store persistent context and history for individual agents using JSON fields.
    *   **`Campaign`**: Models marketing campaigns with `campaign_id`, `name`, `description`, `phase`, `strategy` (Mermaid diagram), `metadata`, and `insights`.
    *   **`Post`**: Models individual posts within a campaign, including `post_id`, `campaign` (ForeignKey), `phase`, `status`, `selected_variant`, and `metrics`.
    *   **`ContentVariant`**: Models A/B content variants for a `Post`, with `variant_id`, `content`, `platform` (now a choice field, default 'X'), and `metadata`.
    *   **`ConversationMessage`**: Stores chat history, linking messages to a `Campaign` with `role`, `content`, and `metadata`.
*   **Database Migrations**: Two new Django migration files (`0001_initial.py` and `0002_alter_contentvariant_platform.py`) have been added to create these new database tables and indexes.
*   **`ContentVariant.platform` Field Update**: The `platform` field in the `ContentVariant` model (`backend/src/agents/models.py`) is now a `CharField` with `choices=[('X', 'X')]` and a default of `'X'`, enforcing specific platform values.

### 3. Impact

*   **Persistent State**: All critical data (campaigns, posts, agent memory, conversations) is now durable and survives application restarts.
*   **Enhanced Reliability**: Reduces data loss risk and improves system stability.
*   **Improved Scalability**: The database backend is better suited for managing larger volumes of data and concurrent agent operations.
*   **Standardized Data Access**: Agents and other modules will now interact with data via Django ORM, ensuring consistent data handling.
*   **Decoupled Agent Logic**: Agents are no longer tightly coupled to an in-memory state object, promoting cleaner architecture.

### 4. Usage

To interact with the new persistent data models:

```python
from agents.models import Campaign, AgentMemory, Post, ContentVariant, ConversationMessage

# Create a new campaign
campaign = Campaign.objects.create(
    campaign_id="my-first-campaign-123",
    name="Launch SaaS Product",
    description="Marketing campaign for new SaaS",
    phase="planning"
)

# Access or update agent memory
agent_mem, created = AgentMemory.objects.get_or_create(agent_name="OrchestratorAgent")
agent_mem.update_context({"last_task": "strategy_planning"})

# Create a post and content variants
post = Post.objects.create(
    post_id="post-001",
    campaign=campaign,
    phase="content_creation",
    status="draft"
)
variant_a = ContentVariant.objects.create(
    post=post,
    variant_id="A",
    content="Check out our new SaaS!",
    platform="X"
)
```

### 5. Breaking Changes

*   Any code directly importing agent classes or state management objects from `backend.src.agents` (e.g., `from agents import Campaign`) will now fail.
*   Existing in-memory or file-based state management logic for campaigns, posts, and agent memory is no longer supported and must be replaced with Django ORM interactions.

### 6. Migration Notes

1.  **Run Database Migrations**: Apply the new database schema changes.
    ```bash
    python manage.py makemigrations agents # Only if models.py was changed manually before migrations
    python manage.py migrate
    ```
2.  **Update Imports**: Change all imports of agent classes and state objects to explicitly reference their respective modules (e.g., `from agents.models import Campaign` or `from agents.supervisor import create_orchestrator`).
3.  **Refactor State Management**: Update agent logic to use the new `AgentMemory`, `Campaign`, `Post`, `ContentVariant`, and `ConversationMessage` Django models for all data persistence and retrieval.