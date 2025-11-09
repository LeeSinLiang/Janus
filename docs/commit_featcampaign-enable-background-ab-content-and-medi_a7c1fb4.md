# Documentation for Commit a7c1fb4

**Commit Hash:** a7c1fb4842548e6aadcda7e924619b2603ce5af8
**Commit Message:** feat(campaign): enable background A/B content and media generation with db concurrency fixes
**Generated:** Sat Nov  8 20:51:23 EST 2025
**Repository:** aiatl

---

This documentation analyzes the provided git diff, detailing the introduction of automated A/B content generation, enhanced database concurrency, and real-time campaign status monitoring.

---

# Technical Documentation: Automated A/B Content Generation & Concurrency Fixes

## 1. Summary

This update introduces an automated, asynchronous pipeline for generating A/B content variants and associated media assets for marketing campaigns. Post-strategy planning, AI agents now automatically create diverse content and images for each post, transitioning the campaign through new `content_creation` and `scheduled` phases. The backend features robust database lock handling for SQLite, while the frontend gains a real-time campaign status bar to reflect these new phases.

## 2. Changes

### 2.1. Backend (`backend/src/`)

*   **`agents/views.py`**:
    *   **New `retry_on_db_lock` function**: Implements exponential backoff for database operations encountering SQLite `OperationalError` (database locked). Essential for concurrent writes.
    *   **New `generate_ab_content_background` function**: A dedicated background task triggered by `StrategyPlanningAPIView`.
        *   Manages Django database connections for thread safety (`connection.close()`).
        *   Updates `Campaign` phase: `planning` → `content_creation` → `scheduled` (or `planning` on error).
        *   Utilizes `create_content_creator` and `create_media_creator` (Gemini-2.5-flash-image) to generate A/B content and corresponding images.
        *   Creates `ContentVariant` objects for each generated variant and saves media assets.
        *   All database interactions within this function are wrapped with `retry_on_db_lock`.
    *   `StrategyPlanningAPIView`: Now spawns a `threading.Thread` to execute `generate_ab_content_background` after initial campaign strategy creation, making content generation asynchronous.
    *   **Imports**: Added `base64`, `threading`, `time`, `connection`, `OperationalError`, `ContentFile`, and `ContentVariant` model.
*   **`janus/settings.py`**:
    *   **SQLite Configuration**: Increased `DATABASES['default']['OPTIONS']['timeout']` to 20 seconds and set `DATABASES['default']['CONN_MAX_AGE']` to `0` for better multi-threaded SQLite handling.
*   **`metrics/views.py`**:
    *   `nodesJSON` endpoint: Now accepts an optional `campaign_id` query parameter to filter data.
    *   Response includes a `campaign` object with `campaign_id`, `name`, `phase`, and `description`.
*   **`test_db_lock_fix.py` (New)**: A new script to specifically test the `retry_on_db_lock` function and concurrent database operations, ensuring robustness.
*   **`test_strategy_api.py`**:
    *   Added `monitor_campaign_phase_transitions` function to observe and verify campaign phase changes (e.g., `planning` → `content_creation` → `scheduled`) in integration tests.

### 2.2. Frontend (`frontend/janus/`)

*   **`.gitignore`**: Added `media/content_variants/*` to ignore generated image files.
*   **`src/components/CampaignStatusBar.tsx` (New)**: A UI component to display the current campaign phase with dynamic styling, descriptions, and animated indicators for active processes.
*   **`src/components/CanvasWithPolling.tsx`**: Integrates `CampaignStatusBar` at the top-center and adjusts `PhaseBar` positioning. Passes `campaignId` to the data hook.
*   **`src/hooks/useGraphData.ts`**: Now accepts an optional `campaignId` and returns the `campaign` object from the API response, updating frontend state.
*   **`src/services/api.ts`**: `fetchGraphDataV1` now supports passing `campaignId` as a query parameter. `GraphResponse` interface updated to include `campaign?: CampaignInfo | null`.
*   **`src/types/api.ts`**: New `CampaignInfo` interface defined for campaign data.

## 3. Impact

*   **Automated Content Creation**: Streamlines the campaign setup by automatically generating A/B content and media, reducing manual effort.
*   **Enhanced System Robustness**: The `retry_on_db_lock` mechanism and adjusted SQLite settings significantly improve stability and prevent database locking issues in concurrent operations.
*   **Real-time Campaign Visibility**: The new `CampaignStatusBar` provides immediate visual feedback on the campaign's current phase, improving user experience and transparency.
*   **Asynchronous Processing**: Content generation runs in a background thread, preventing the API from blocking and improving response times for strategy planning.
*   **Improved Testability**: Dedicated test script for database concurrency ensures reliability.

## 4. Usage

*   **Triggering Automated Content Generation**:
    *   **Via API**: Send a `POST` request to `/api/strategy/plan/` with campaign details. Content generation will start asynchronously.
    *   **Via Frontend**: Create a new campaign strategy through the UI; content generation will automatically follow.
*   **Monitoring Campaign Status**:
    *   **Via Frontend**: Navigate to the campaign's canvas view. The `CampaignStatusBar` will display the current phase (e.g., "Generating Content" with a pulsing indicator).
    *   **Via Backend API**: `GET /api/nodesJson/?campaign_id=<your_campaign_id>`. The response will include the `campaign` object with its current `phase`.
*   **Using `retry_on_db_lock`**: For custom Django ORM operations prone to SQLite locks, wrap them:
    ```python
    from agents.views import retry_on_db_lock
    def my_db_operation():
        with transaction.atomic():
            # ... database logic ...
    result = retry_on_db_lock(my_db_operation)
    ```

## 5. Breaking Changes

*   The `/api/nodesJson/` endpoint's response structure now includes an optional `campaign` object. Existing clients consuming this endpoint should be aware of this addition, though it is an additive change and should not break existing functionality unless strict schema validation is in place.

## 6. Migration Notes

*   **Database Settings**: Update your `DATABASES` configuration for SQLite in `settings.py` with the `timeout` and `CONN_MAX_AGE` options.
*   **Database Migrations**: Run `python manage.py makemigrations` and `python manage.py migrate` to create the `ContentVariant` model and any related schema changes.
*   **Frontend Dependencies**: Ensure `npm install` or `yarn install` is run to pick up new component dependencies.