# Documentation for Commit bc7816a

**Commit Hash:** bc7816a6a8b8333b974cee0e999c0b60dd1e9cb7
**Commit Message:** feat(content-automation): implement automated content regeneration via metric triggers
**Generated:** Sun Nov  9 04:49:39 EST 2025
**Repository:** aiatl

---

This documentation outlines significant updates to the content generation and trigger-based automation system. The core enhancement is the introduction of an automated content regeneration workflow, allowing the system to intelligently respond to post performance triggers by generating improved content variants.

### Summary

This update introduces an intelligent, automated content regeneration system. It enables posts to have performance triggers that, when met, initiate a background process to analyze metrics, generate improved A/B content variants, create new media assets, and reset the post status to 'draft' for review. Key changes include modifications to the `ContentVariant` model to support multiple versions of A/B content over time, new AI agent capabilities for trigger-specific analysis and content generation, and a robust background task mechanism to handle regeneration.

### Changes

1.  **Automated Content Regeneration Workflow (`metrics/views.py`)**:
    *   **`checkTrigger` API View**: Now evaluates trigger conditions for *both* A/B variants of a published post. If *either* variant meets the condition, a content regeneration process is initiated. It also accepts an optional `campaign_id` query parameter for filtering.
    *   **Background Task (`regenerate_content_background`)**: Triggered posts now launch a `threading.Thread` to perform regeneration asynchronously. This task:
        *   Analyzes performance metrics using the new `MetricsAnalyzer.execute_trigger_analysis`.
        *   Generates new A/B content using `ContentCreator.execute_with_metrics`, incorporating insights from the analysis and previous content.
        *   Creates and attaches new media assets for the regenerated variants.
        *   Updates the post's status to `draft` and clears its trigger configuration.
        *   Includes `retry_on_db_lock` for robust database operations within the thread.

2.  **AI Agent Enhancements**:
    *   **`MetricsAnalyzer.execute_trigger_analysis` (New)**: A specialized method to analyze metrics when a trigger fires. It crafts a detailed prompt for the AI, focusing on root cause analysis, A/B comparison, and strategy for content regeneration based on the specific trigger condition and user prompt.
    *   **`ContentCreator.regenerate_content` (New)**: A method (whose core logic is integrated into `regenerate_content_background`) that outlines the steps for creating new content variants based on an analysis report, updating the post, and clearing triggers.

3.  **Content Variant Model (`agents/models.py`, `migrations/0010`)**:
    *   **Multiple Variants per Post**: The `unique_together = [['post', 'variant_id']]` constraint has been removed from the `ContentVariant` model. This allows a single post to have multiple versions of 'A' or 'B' variants over time, enabling historical tracking of regenerated content.
    *   **Ordering and Indexing**: `ContentVariant` now orders by `['-created_at', 'variant_id']` (newest first) and has a new index on `['post', 'variant_id', '-created_at']`.
    *   **`created_at` in Serializer**: The `ContentVariantSerializer` now includes the `created_at` field.

4.  **Database Robustness (`metrics/views.py`)**:
    *   **`retry_on_db_lock`**: A utility function to automatically retry database operations that fail due to `OperationalError` (e.g., "database is locked"), using exponential backoff. This is crucial for stability in concurrent operations, especially within background threads.

### Impact

*   **Automated Content Optimization**: The system can now automatically respond to underperforming content by generating new, optimized variants, reducing manual intervention.
*   **Historical Content Tracking**: All generated content variants are preserved, allowing for a historical view of content evolution for a given post.
*   **Improved System Reliability**: Background processing for regeneration prevents blocking the main API thread, and the `retry_on_db_lock` mechanism enhances database interaction stability.
*   **Data Retrieval Changes**: Existing code fetching `ContentVariant` objects must now explicitly retrieve the *latest* version if that's the desired behavior, as multiple variants with the same `variant_id` can exist. This has been updated in `createXPost`, `selectVariant`, and `approveAllNodes` views.

### Usage

To leverage the new regeneration feature:

1.  **Configure Triggers**: Ensure `Post` instances have `trigger_condition`, `trigger_value`, `trigger_comparison`, and `trigger_prompt` fields set.
2.  **Run `checkTrigger`**: Periodically call the `/api/check_trigger/` endpoint.
    *   Example: `GET /api/check_trigger/`
    *   To check triggers for a specific campaign: `GET /api/check_trigger/?campaign_id=your_campaign_uuid`
3.  **Monitor Regeneration**: When a trigger fires, the system will log the start of a background regeneration thread. The affected post's status will change to `draft`, and new `ContentVariant` records will be created. Users can then review the new `draft` content.

**Example of `execute_trigger_analysis` (internal agent usage):**
```python
from agents.metrics_analyzer import create_metrics_analyzer

metrics_agent = create_metrics_analyzer()
analysis = metrics_agent.execute_trigger_analysis(
    metrics_data={"variant_a_likes": 3, "variant_b_likes": 8},
    condition="likes",
    trigger_value=5,
    comparison="<",
    trigger_prompt="generate new strategy focused on emotional engagement",
    triggered_variants=["A"]
)
# analysis.analysis contains AI's detailed report
```

### Breaking Changes

*   The `ContentVariant` model no longer enforces uniqueness on `(post, variant_id)`. Code that assumes only one 'A' or 'B' variant exists for a given post without considering `created_at` will now need to be updated to explicitly fetch the latest variant (e.g., using `.order_by('-created_at').first()`).

### Migration Notes

1.  Apply the new database migration:
    ```bash
    python manage.py makemigrations agents
    python manage.py migrate
    ```
    This will create the `0010_alter_contentvariant_options_and_more.py` migration, which updates the `ContentVariant` model's ordering, removes the unique constraint, and adds a new index.

2.  **Review Existing Code**: Any custom code that queries `ContentVariant` objects should be reviewed. If you intend to retrieve the *currently active* or *latest* variant for a post and variant ID, ensure you use `ContentVariant.objects.filter(post=post, variant_id='A').order_by('-created_at').first()`.