# Documentation for Commit 9bfc9e4

**Commit Hash:** 9bfc9e4a069d6fcd964fe141f584c732b896a569
**Commit Message:** feat(triggers): implement AI-powered natural language trigger parsing and evaluation
**Generated:** Sun Nov  9 02:15:41 EST 2025
**Repository:** aiatl

---

This documentation outlines the significant overhaul of the trigger system, introducing AI-powered natural language parsing and structured trigger configurations.

## Summary
This update introduces a robust, AI-powered natural language trigger parsing system, replacing the previous simplistic trigger mechanism. The `Post` model now supports structured trigger conditions, values, comparisons, and action prompts, enabling more sophisticated automated responses based on post performance metrics. A new `TriggerParserAgent` leverages generative AI to interpret user-defined trigger prompts.

## Changes

### 1. Backend: `Post` Model & Database Schema
-   **Removed**: The single `trigger` `CharField` from the `Post` model.
-   **Added**:
    -   `posted_time` (DateTimeField): Records when a post was published.
    -   `trigger_condition` (CharField, choices: `likes`, `retweets`, `impressions`, `comments`): The metric to monitor.
    -   `trigger_value` (IntegerField): The numeric threshold for the trigger.
    -   `trigger_comparison` (CharField, choices: `<`, `=`, `>`): The comparison operator.
    -   `trigger_prompt` (TextField): A natural language instruction for an AI agent when the trigger activates.
-   **Migrations**: New migration files (`0009_remove_post_trigger_post_posted_time_and_more.py` and `0010_alter_postmetrics_tweet_id.py`) are introduced to apply these schema changes.

### 2. Backend: TriggerParserAgent
-   **New Agent**: `backend/src/agents/trigger_parser.py` introduces `TriggerParserAgent`.
-   **Functionality**: This agent uses a `ChatGoogleGenerativeAI` model (default `gemini-2.5-flash-lite`) to parse natural language input (e.g., "less than 5, generate new strategy") into a structured `TriggerConfig` object (containing `value`, `comparison`, `prompt`).
-   **Integration**: Exposed via `create_trigger_parser` factory function.

### 3. Backend: API Endpoints & Logic
-   **Deprecation**: The `/api/setTrigger/` endpoint is deprecated and now returns an error, advising the use of the new endpoint.
-   **New Endpoint**: `/api/parseTrigger/` (POST) is added. It accepts `pk` (Post ID), `condition` (metric type), and `prompt` (natural language trigger). It uses `TriggerParserAgent` to parse the prompt and saves the structured trigger data to the `Post` model.
-   **Enhanced `checkTrigger`**: The `/api/checkTrigger/` endpoint is refactored to:
    -   Filter for published posts with configured structured triggers.
    -   Dynamically retrieve metric values based on `trigger_condition`.
    -   Evaluate triggers using `trigger_value` and `trigger_comparison`.
    -   Return detailed information about triggered posts, including the `trigger_prompt` for subsequent AI agent actions.
-   **`posted_time` Assignment**: `createXPost` and `approveAllNodes` now set the `post.posted_time` upon successful publication.

### 4. Admin Interface
-   The Django Admin for the `Post` model is updated to reflect the new structured trigger fields, organized under a collapsible "Trigger Configuration" fieldset. The `posted_time` field is added to the "Metrics & Publishing" fieldset.

### 5. Frontend (`ChatBox.tsx`, `api.ts`)
-   **API Service**: `frontend/janus/src/services/api.ts` deprecates `sendTrigger` and introduces `parseTrigger` to interact with the new `/api/parseTrigger/` endpoint.
-   **ChatBox Interaction**: The `ChatBox` component is updated to:
    -   Support a new input format for setting triggers: `**NodeTitle** **condition** prompt` (e.g., `**My Post Title** **likes** less than 10, create a follow-up post`).
    -   Update command options for trigger conditions (`likes`, `retweets`, `impressions`, `comments`).
    -   Call the new `parseTrigger` API function.

## Impact
-   **Enhanced Automation**: Enables more sophisticated, metric-driven automated responses and strategies for social media posts.
-   **Improved User Experience**: Users can define triggers using natural language, which is then parsed into a structured format.
-   **Database Schema Change**: Requires running database migrations.
-   **API Change**: Old trigger setting API is deprecated.

## Usage

### Setting a Trigger (Frontend)
In the chatbox, use the format: `**[Post Title]** **[condition]** [natural language prompt]`

**Example:**
`**My Latest Campaign Post** **likes** less than 10, create a follow-up post with a question to increase engagement.`

This will parse into:
-   `post_pk`: ID of "My Latest Campaign Post"
-   `trigger_condition`: "likes"
-   `trigger_value`: 10
-   `trigger_comparison`: "<"
-   `trigger_prompt`: "create a follow-up post with a question to increase engagement."

### Checking Triggers (Backend)
The `/api/checkTrigger/` endpoint can be called to identify posts that have met their configured trigger conditions.

**Example Request:**
`GET /api/checkTrigger/`

**Example Response (partial):**
```json
{
  "triggered_posts": [
    {
      "post_pk": 123,
      "post_title": "My Latest Campaign Post",
      "trigger_condition": "likes",
      "trigger_value": 10,
      "trigger_comparison": "<",
      "current_value": 8,
      "elapsed_time_seconds": 3600,
      "trigger_prompt": "create a follow-up post with a question to increase engagement."
    }
  ],
  "count": 1
}
```

## Breaking Changes
-   The `trigger` field on the `Post` model has been removed. Any code directly accessing `post.trigger` will fail.
-   The `/api/setTrigger/` API endpoint is deprecated and no longer functions as before. Frontend clients must switch to `/api/parseTrigger/`.

## Migration Notes
1.  **Run Database Migrations**: After pulling the changes, apply the new database migrations:
    ```bash
    python manage.py makemigrations agents metrics
    python manage.py migrate
    ```
2.  **Update Frontend Clients**: Ensure all frontend components that previously used `sendTrigger` or directly manipulated trigger strings are updated to use the new `parseTrigger` function and the new trigger input format.
3.  **Review Existing Data**: Any existing `Post` objects will have their old `trigger` field removed. If you had critical data in this field, it will be lost unless manually migrated before applying these changes.