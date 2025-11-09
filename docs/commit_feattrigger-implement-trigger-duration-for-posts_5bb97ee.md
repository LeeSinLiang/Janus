# Documentation for Commit 5bb97ee

**Commit Hash:** 5bb97ee35558a152fb7ef868d2d0e5ab0a98f3e6
**Commit Message:** feat(trigger): implement trigger duration for posts
**Generated:** Sun Nov  9 07:21:15 EST 2025
**Repository:** aiatl

---

This documentation outlines the changes introduced by the recent commit, focusing on the new `trigger_duration` feature.

---

# Trigger Duration Feature Documentation

## 1. Summary

This update introduces a `trigger_duration` field to the `Post` model, enabling time-based conditions for automated triggers. Triggers can now be configured to only fire after a specified minimum duration has elapsed since the post was created. This enhances control over trigger activation, preventing premature actions and allowing metrics to stabilize.

## 2. Changes

### `backend/src/agents/migrations/0011_post_trigger_duration.py` (New File)
*   A new Django migration is added to introduce the `trigger_duration` field to the `Post` model.
*   The field is an `IntegerField`, `blank=True`, and `null=True`, with a `help_text` explaining its purpose.

### `backend/src/agents/models.py`
*   The `Post` model now includes a new field:
    ```python
    trigger_duration = models.IntegerField(
        blank=True,
        null=True,
        help_text="Minimum elapsed time in seconds before trigger can fire"
    )
    ```

### `backend/src/agents/trigger_parser.py`
*   **Docstrings and Examples**: Updated to reflect the inclusion of `duration` in trigger prompts and outputs.
*   **`TriggerConfig` Model**: The `TriggerConfig` Pydantic model now includes a `duration` field:
    ```python
    duration: int = Field(
        description="Minimum elapsed time in seconds before trigger can fire (e.g., 3600 for 1 hour, 7200 for 2 hours)"
    )
    ```
*   **`TriggerParserAgent` System Prompt**: The internal system prompt for the LangChain agent is updated to instruct it on parsing the "within DURATION" clause from natural language prompts.
    *   New example format: `"COMPARISON VALUE within DURATION, ACTION_PROMPT"`
    *   Explicitly states: "Duration is ALWAYS required and must be in seconds."
*   **`parse` Method**: The docstring and example for the `parse` method are updated to demonstrate how `duration` is now extracted and returned in the `TriggerConfig`.
*   **Test Cases**: The `if __name__ == "__main__":` block's test cases and output formatting are updated to include `duration`.

### `backend/src/metrics/views.py`
*   **`parseTrigger` View**:
    *   When a trigger prompt is parsed, the extracted `trigger_config.duration` is now saved to `post.trigger_duration`.
    *   The API response for `parseTrigger` now includes the `duration` field.
*   **`checkTrigger` View**:
    *   The initial queryset for `Post` objects now filters for `trigger_duration__isnull=False` to ensure only posts with a defined duration are considered for time-based checks.
    *   A new check is introduced:
        ```python
        if post.trigger_duration is not None:
            if elapsed_time < post.trigger_duration:
                # Not enough time has passed, skip this post
                continue
        ```
        This ensures that if `trigger_duration` is set, the trigger evaluation only proceeds if the `elapsed_time` since `posted_time` meets or exceeds this duration.
    *   The `triggered_posts` response now includes `trigger_duration`.

## 3. Impact

*   **Enhanced Trigger Control**: Triggers can now be configured with a minimum waiting period, preventing immediate activation and allowing for more nuanced, time-sensitive automation.
*   **API Changes**: The `/metrics/parseTrigger/` and `/metrics/checkTrigger/` API endpoints now include `trigger_duration` in their request/response payloads.
*   **Database Schema Change**: The `Post` table now has an additional `trigger_duration` column.
*   **Trigger Parsing Logic**: The `TriggerParserAgent` is now capable of understanding and extracting duration from natural language prompts.

## 4. Usage

To utilize the new `trigger_duration` feature, include the `within DURATION` clause in your trigger prompts, where `DURATION` is the minimum elapsed time in seconds.

**Example Prompt:**
`"less than 5 within 3600, make it in cartoon style post"`

**API Request (to `/metrics/parseTrigger/`):**
```json
{
    "post_id": "your_post_id",
    "condition": "likes",
    "prompt": "less than 5 within 3600, make it in cartoon style post"
}
```

**API Response (from `/metrics/parseTrigger/`):**
```json
{
    "status": "success",
    "trigger_config": {
        "condition": "likes",
        "value": 5,
        "comparison": "<",
        "duration": 3600,
        "prompt": "make it in cartoon style post"
    }
}
```

The system will then only evaluate this trigger after at least 3600 seconds (1 hour) have passed since the post's `posted_time`.

## 5. Breaking Changes

There are no direct breaking changes. Existing triggers that do not specify a `duration` in their prompt will continue to function as before, effectively having no minimum duration requirement (as `trigger_duration` will remain `null`). However, if you intend for existing triggers to have a time-based constraint, their prompts must be updated to include the `within DURATION` clause.

## 6. Migration Notes

A new database migration `0011_post_trigger_duration.py` has been added. To apply this schema change to your database, run the following Django management command:

```bash
python manage.py migrate agents
```