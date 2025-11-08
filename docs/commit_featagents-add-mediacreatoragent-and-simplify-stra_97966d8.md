# Documentation for Commit 97966d8

**Commit Hash:** 97966d8bcc1a92eb2b5c7bf4981465133af1dc94
**Commit Message:** feat(agents): add MediaCreatorAgent and simplify strategy planning API
**Generated:** Sat Nov  8 15:22:13 EST 2025
**Repository:** aiatl

---

# Git Diff Documentation

## 1. Summary

This update introduces a new `MediaCreatorAgent` class, laying groundwork for future media generation capabilities. More significantly, it refactors the `StrategyPlanningAPIView` to standardize strategy generation, making database persistence mandatory for all created marketing strategies and simplifying campaign naming conventions. Additionally, minor code style adjustments (indentation) have been applied across `views.py`.

## 2. Changes

### 2.1. New Agent: `MediaCreatorAgent`

*   **File Added**: `backend/src/agents/media_creator.py`
*   **Description**: A new Python class `MediaCreatorAgent` has been introduced. This class is intended to encapsulate logic for creating media, likely utilizing AI models.
*   **Details**:
    *   Imports `typing.Literal`.
    *   The `__init__` method is defined, taking a `model_name` parameter. The default value `Literal['gemini-2.5-flash-lite']` appears to be a placeholder for a specific model type hint rather than an actual default string value, suggesting early development.

### 2.2. Strategy Planning API (`backend/src/agents/views.py`)

*   **Indentation Change**: The entire `views.py` file has been reformatted, changing indentation from 4 spaces to 1 tab for consistency.
*   **`StrategyPlanningAPIView.post` Method Modifications**:
    *   **Mandatory Database Persistence**: The `save_to_db` parameter from the request body is no longer processed. All generated marketing strategies are now *unconditionally saved* to the database as `Campaign` and `Post` objects.
    *   **Auto-generated Campaign Names**: The `campaign_name` parameter from the request body is no longer processed. Campaign names are now automatically generated in the format `campaign_X` (e.g., `campaign_1`, `campaign_2`), based on the current count of campaigns in the database.
    *   **Simplified Response Status**: The HTTP response status for successful strategy creation is now consistently `HTTP_201_CREATED`, reflecting the mandatory database creation. Previously, it could be `HTTP_200_OK` if `save_to_db` was `False`.
    *   **Simplified Success Message**: The success message no longer conditionally states whether the campaign was saved, as it is always saved.

## 3. Impact

*   **`MediaCreatorAgent`**: This is a foundational addition. While currently minimal, it signals future capabilities for automated media content generation within the system. It has no immediate functional impact on existing features.
*   **`StrategyPlanningAPIView`**:
    *   **Behavioral Shift**: All calls to the `/api/agents/strategy/` endpoint will now always create database records for campaigns and posts. This ensures full persistence of all generated strategies.
    *   **API Contract Change**: Clients interacting with this endpoint should be aware that `campaign_name` and `save_to_db` parameters in the request body are now effectively ignored. Their presence will not alter the behavior of the API.
    *   **Resource Usage**: Every strategy generation will now incur database write operations.

## 4. Usage

### 4.1. `MediaCreatorAgent`

This class is currently a stub. Direct external usage is not expected at this stage. It will likely be integrated into other agent workflows in future updates.

### 4.2. Strategy Planning API (`POST /api/agents/strategy/`)

The request body structure remains the same, but the `campaign_name` and `save_to_db` fields are now ignored.

**Example Request:**

```json
POST /api/agents/strategy/
Content-Type: application/json

{
    "product_description": "A new AI-powered task management app.",
    "gtm_goals": "Increase user sign-ups by 20% in Q3.",
    "campaign_name": "Ignored Custom Name",
    "save_to_db": false
}
```

**Example Response (Success):**

```json
HTTP/1.1 201 Created
Content-Type: application/json

{
    "success": true,
    "campaign_id": "campaign_X",
    "mermaid_diagram": "graph TB...",
    "nodes": [...],
    "connections": [...],
    "total_posts": 10,
    "message": "Strategy created successfully and saved as campaign campaign_X"
}
```

## 5. Breaking Changes

Yes, this update introduces breaking changes for clients that:
*   Relied on `save_to_db: false` to prevent database persistence of strategies. All strategies are now saved.
*   Expected to specify a custom `campaign_name` via the request body. Campaign names are now auto-generated.

## 6. Migration Notes

Clients consuming the `/api/agents/strategy/` endpoint should update their expectations regarding campaign persistence and naming. No code changes are strictly required on the client side if they continue to send the `campaign_name` and `save_to_db` fields, but they should be aware these parameters will no longer influence the API's behavior.