# Documentation for Commit 31d732d

**Commit Hash:** 31d732d0cbadbb64d0cb0fea7ed40eaf16a803c7
**Commit Message:** feat(strategy-regeneration): introduce phase-based strategy regeneration and versioning
**Generated:** Wed Nov 12 13:42:19 EST 2025
**Repository:** aiatl

---

This update introduces a powerful "Strategy Regeneration" feature, enabling dynamic pivots in marketing campaigns from a specific phase onwards. The system now incorporates comprehensive versioning, soft-deletion of old posts, and intelligent generation of new, interconnected posts with many-to-many relationships. This significantly enhances campaign adaptability and provides a robust historical record.

---

### Summary

The core functionality of the AI-powered GTM OS has been extended to allow partial regeneration of campaign strategies. Users can now issue a chat command or API call to regenerate phases from a specified point, preserving earlier phases. This involves significant updates to the backend AI agent, new API endpoints, database schema modifications for versioning, and frontend integration.

### Key Features

*   **Phase-Based Regeneration**: Regenerate strategy starting from any phase (e.g., Phase 2 onwards), while preserving earlier phases and their connections.
*   **Campaign Versioning**: Campaigns now track `current_version`, and individual posts track their `version` and `is_active` status.
*   **Soft Delete for Posts**: Old posts from regenerated phases are marked `is_active=False` (archived) rather than deleted, enabling future version history UIs.
*   **Many-to-Many Connections**: The strategy planner supports complex branching (one old post connects to multiple new posts) and merging (multiple old posts connect to one new post).
*   **Dynamic Node Count**: New phases can generate between 2-5 posts, allowing for richer and more nuanced strategies.
*   **Automated Content Generation**: Background tasks automatically generate A/B content variants and media for newly created posts.

### Changes

#### Backend
1.  **New API Endpoint**: `POST /api/agents/regenerate-strategy/`
    *   Accepts `campaign_id`, `phase_num` (to start regeneration from), and `new_direction`.
    *   Orchestrates the entire regeneration workflow: validation, post archiving, version increment, AI strategy generation, new post creation, and linking.
    *   Launches asynchronous content and media generation for new posts.
2.  **Database Schema Updates**:
    *   `Campaign` model: Added `current_version` (IntegerField, default=1) to track the active strategy version.
    *   `Post` model: Added `version` (IntegerField, default=1) to link posts to a specific strategy version, and `is_active` (BooleanField, default=True, db_index=True) for soft-deletion.
    *   A new Django migration (`0012_...py`) introduces these fields and an index on `Post` for `campaign` and `is_active`.
3.  **Strategy Planner Agent (`strategy_planner.py`)**:
    *   Introduced `execute_from_phase()` method, which takes existing posts as context and a `new_direction` prompt.
    *   A specialized `_get_regeneration_system_prompt()` guides the LLM to preserve existing phases, generate 2-5 nodes per new phase, and create many-to-many connections.
4.  **Views & Background Tasks (`views.py`)**:
    *   Implemented `RegenerateStrategyAPIView` to handle the API logic.
    *   Added `regenerate_content_background()` for parallel content/media generation for new posts.
    *   Existing data retrieval views (`getMetricsDB`, `checkTrigger`, `nodesJSON`, `approveAllNodes`) are updated to filter `Post` objects by `is_active=True`, ensuring only current strategy posts are displayed or processed.
5.  **Mermaid Parser (`mermaid_parser.py`)**: Modified to normalize phase names by stripping "(Existing)" or "(New)" labels, ensuring consistent backend processing.
6.  **Logging (`settings.py`)**: New Django logging configuration filters out noisy frontend polling requests (e.g., `/nodesJson/`) from console output for improved developer experience.

#### Frontend
1.  **Chat Command Integration (`ChatBox.tsx`)**:
    *   A new chat command `!regenerate phase X <prompt>` is recognized.
    *   Parses the command, validates `phase X`, and dispatches the request to the backend API.
2.  **API Service (`api.ts`)**: Added `regenerateStrategy()` function to provide a client-side interface for the new backend endpoint.

### Impact

*   **Enhanced Campaign Agility**: Users can now easily pivot strategies based on performance data or market changes without losing earlier campaign history.
*   **Improved Data Integrity**: The versioning system provides a clear audit trail of strategy evolution.
*   **Developer Experience**: Cleaner logs aid in debugging, and a dedicated test suite ensures reliability.
*   **Future-Proofing**: The versioning foundation paves the way for advanced features like version comparison and restoration (outlined in `VERSIONING_ROADMAP.md`).

### Usage

#### Chat Command
On the campaign canvas page, type into the chatbox:
```
!regenerate phase 2 pivot to developer-first strategy with technical demos
```
This command will trigger the system to:
1.  Keep Phase 1 posts active and unchanged.
2.  Archive all existing posts from Phase 2 onwards (`is_active=False`).
3.  Generate new Phase 2 and subsequent phases based on the provided direction.
4.  Connect Phase 1 posts to the new Phase 2 posts.
5.  Automatically generate A/B content for all newly created posts in the background.

#### API Endpoint
Developers can directly interact with the API:
```bash
curl -X POST http://localhost:8000/api/agents/regenerate-strategy/ \
  -H "Content-Type: application/json" \
  -d '{
    "campaign_id": "campaign_001",
    "phase_num": 2,
    "new_direction": "Focus on ProductHunt launch with developer communities"
  }'
```

### Breaking Changes

None. This feature is additive and maintains backward compatibility with existing functionality.

### Migration Notes

*   **Database Migration**: A new Django migration is required to add the `current_version`, `version`, and `is_active` fields to the `Campaign` and `Post` models, respectively.
    ```bash
    python manage.py makemigrations agents
    python manage.py migrate
    ```
    Existing `Campaign` objects will default `current_version` to 1. Existing `Post` objects will default `version` to 1 and `is_active` to `True`.

### New Documentation Files

*   `VERSIONING_ROADMAP.md`: Outlines the strategic vision and future enhancements for campaign versioning.
*   `backend/API_REGENERATION.md`: Comprehensive API reference for the new regeneration endpoint.
*   `backend/REGENERATION_SUMMARY.md`: A quick reference guide summarizing the feature, implementation, and best practices.
*   `backend/STRATEGY_REGENERATION.md`: A detailed feature guide explaining the core agent logic and usage.
*   `backend/VERIFICATION_REPORT.md`: An internal report detailing the verification of all requirements and tests.
*   `backend/test_strategy_regeneration.py`: A dedicated test suite for the new regeneration feature.