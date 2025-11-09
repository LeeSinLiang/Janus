# Documentation for Commit 2d49cf3

**Commit Hash:** 2d49cf3bd8878dd3de476db68eb7f99706b45842
**Commit Message:** feat(campaign): enable background A/B content and media generation with db concurrency fixes
**Generated:** Sat Nov  8 20:48:26 EST 2025
**Repository:** aiatl

---

# Technical Documentation: Automated A/B Content Generation and Campaign Status Monitoring

## 1. Summary

This comprehensive update introduces an automated, asynchronous pipeline for generating A/B content variants and associated media assets for marketing campaigns. Following strategy planning, the system now automatically triggers AI agents to create diverse content and images for each post, transitioning the campaign through new `content_creation` and `scheduled` phases. The backend is enhanced with robust database lock handling for SQLite, while the frontend gains a real-time campaign status bar to reflect these new phases.

## 2. Changes

### 2.1. Backend Enhancements (`backend/src/agents/views.py`)

*   **Asynchronous A/B Content & Media Generation:**
    *   **`generate_ab_content_background` function:** A new background task that orchestrates the generation of two content variants (A/B) and corresponding AI-generated images for all posts within a campaign.
    *   **AI Agent Integration:** Utilizes `create_content_creator` and `create_media_creator` (Gemini-2.5-flash-image) to produce textual content and visual assets.
    *   **Campaign Phase Transitions:** Automatically updates the `Campaign` phase from `planning` to `content_creation` (during generation) and then to `scheduled` (upon completion). In case of errors, it attempts to revert to `planning`.
    *   **Thread-Safe Database Handling:** Explicitly closes and manages database connections within the background thread (`connection.close()`) to prevent issues with Django's ORM in multi-threaded environments.
*   **Database Lock Retry Mechanism:**
    *   **`retry_on_db_lock` function:** A new utility function that retries database operations with exponential backoff if an `OperationalError` indicating a database lock (common in SQLite) occurs. This ensures robustness for concurrent writes.
*   **Strategy Planning API (`StrategyPlanningAPIView`):**
    *   Now triggers `generate_ab_content_background` in a new `threading.Thread` after successfully creating campaign posts. This makes content generation non-blocking for the API response.
*   **New Model Import:** `ContentVariant` is now imported and used to store A/B content and their associated media.

### 2.2. Database Configuration (`backend/src/janus/settings.py`)

*   **SQLite Enhancements:**
    *   `DATABASES['default']['OPTIONS']['timeout']`: Increased to 20 seconds to allow more time for concurrent operations.
    *   `DATABASES['default']['CONN_MAX_AGE']`: Set to `0`, ensuring database connections are closed immediately after each request. This is crucial for preventing SQLite locking issues in a multi-threaded Django application.

### 2.3. Metrics API (`backend/src/metrics/views.py`)

*   **Campaign-Specific Data:** The `/nodesJson/` endpoint now accepts an optional `campaign_id` query parameter to filter posts and metrics for a specific campaign.
*   **Campaign Info in Response:** The API response now includes a `campaign` object containing `campaign_id`, `name`, `phase`, and `description` for the requested campaign.

### 2.4. Frontend UI & State Management (`frontend/janus/`)

*   **New `CampaignStatusBar` Component:** (`src/components/CampaignStatusBar.tsx`)
    *   A dedicated UI component to display the current `Campaign` phase (e.g., "Planning", "Generating Content", "Scheduled") with dynamic styling, descriptions, and animated indicators for active processes.
*   **Canvas Integration (`src/components/CanvasWithPolling.tsx`):**
    *   Integrates the `CampaignStatusBar` at the top-center of the `node-editor` view.
    *   Adjusts the position of the `PhaseBar` to accommodate the new status bar.
    *   Passes the `campaignId` to the `useGraphData` hook.
*   **Graph Data Hook (`src/hooks/useGraphData.ts`):**
    *   Now accepts an optional `campaignId` to fetch campaign-specific data.
    *   Returns the `campaign` object from the backend API response, updating the frontend state.
*   **API Service (`src/services/api.ts`):**
    *   `fetchGraphDataV1` now supports passing `campaignId` as a query parameter to the backend.
    *   The `GraphResponse` interface is updated to include `campaign?: CampaignInfo | null`.
*   **Type Definitions (`src/types/api.ts`):**
    *   Introduced `CampaignInfo` interface to define the structure of campaign data.
*   **`.gitignore`:** Added `media/content_variants/*` to ignore generated media files.

### 2.5. Testing & Demo Scripts

*   **`backend/test_db_lock_fix.py` (New):** A dedicated script to test the `retry_on_db_lock` function and verify concurrent database operations, crucial for SQLite stability.
*   **`backend/test_strategy_api.py`:**
    *   Includes a new `monitor_campaign_phase_transitions` function to observe and verify the campaign's phase changes (planning -> content_creation -> scheduled) triggered by the background task.
    *   The `main` function now calls this monitor after initiating strategy planning.

## 3. Impact

*   **Automated Content Creation:** Significantly reduces manual effort by automating the generation of A/B content and media, accelerating the campaign setup process.
*   **Enhanced System Robustness:** The `retry_on_db_lock` mechanism and adjusted SQLite settings drastically improve stability and prevent common database locking issues in concurrent operations, especially critical for background tasks.
*   **Real-time Campaign Visibility:** The new `CampaignStatusBar` provides immediate visual feedback on the campaign's current phase, improving user experience and transparency during automated processes.
*   **Improved Scalability (SQLite):** While SQLite is not ideal for high-concurrency, the connection management and retry logic make it more resilient for background tasks within a single-process, multi-threaded setup.
*   **Better Data Organization:** The `nodesJSON` endpoint now supports filtering by `campaign_id`, allowing for more targeted data retrieval and display.

## 4. Usage

### 4.1. Triggering Automated Content Generation

*   **Via API:** Send a `POST` request to `/api/strategy/plan/` with your campaign details. Upon successful strategy planning, the A/B content and media generation will automatically start in the background.
*   **Via Frontend:** Use the frontend UI to create a new campaign strategy. The system will automatically proceed to content generation.

### 4.2. Monitoring Campaign Status

*   **Via Frontend:** Navigate to the campaign's canvas view. A new `CampaignStatusBar` at the top will display the current phase (e.g., "Generating Content" with a pulsing indicator) and transition as content is created and the campaign becomes "Scheduled".
*   **Via Backend API:**
    *   To get campaign-specific posts and its status:
        ```
        GET /api/nodesJson/?campaign_id=<your_campaign_id>
        ```
        The response will include a `campaign` object with the current `phase`.

### 4.3. Database Lock Handling

*   The `retry_on_db_lock` function is internally used by background tasks. For any custom Django ORM operations that might experience SQLite locking, consider wrapping them with this utility:
    ```python
    from agents.views import retry_on_db_lock
    # ...
    def my_db_operation():
        with transaction.atomic():
            # ... database logic ...
    
    result = retry_on_db_lock(my_db_operation)
    ```

## 5. Breaking Changes

*   The `/api/nodesJson/` endpoint's response structure now includes an optional `campaign` object. Existing clients consuming this endpoint should be aware of this addition, though it's an additive change and should not break existing functionality if not explicitly relied upon.

## 6. Migration Notes

*   **Database Settings:** Ensure your `DATABASES` configuration for SQLite in `settings.py` includes the `timeout` and `CONN_MAX_AGE` options as specified in the diff to leverage the improved concurrency handling.
*   **New Models:** If running migrations for the first time or after a significant schema change, ensure `python manage.py makemigrations` and `python manage.py migrate` are run to create the `ContentVariant` model and any related fields.
*   **Frontend Dependencies:** No specific migration steps are required beyond ensuring `npm install` or `yarn install` is run to pick up any new component dependencies.