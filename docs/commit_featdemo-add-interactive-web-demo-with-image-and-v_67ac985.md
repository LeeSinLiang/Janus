# Documentation for Commit 67ac985

**Commit Hash:** 67ac9850a80c393267bb1497c1f829cf8b008ecd
**Commit Message:** feat(demo): add interactive web demo with image and video generation capabilities
**Generated:** Sat Nov  8 17:55:09 EST 2025
**Repository:** aiatl

---

## Documentation: AI Media Generation & Web Demo Integration

### Summary
This update significantly enhances the Janus GTM OS by introducing AI-powered media generation (images and videos) for A/B content variants. These new capabilities are seamlessly integrated into the content creation workflow and showcased through a new interactive Flask-based web demo.

### Changes

*   **AI Media Generation (`backend/src/agents/media_creator.py`)**:
    *   A new `MediaCreatorAgent` class is added, providing methods to generate images using `gemini-2.5-flash-image` and videos using `veo-3.1-generate-preview` from text prompts.
    *   `create_image` returns base64 encoded image data, while `create_video` downloads and saves the generated video to a local file.
*   **Enhanced Content Creation (`backend/src/agents/content_creator.py`)**:
    *   A `VideoContentOutput` BaseModel and `VideoContentCreatorAgent` are introduced. This specialized agent generates A/B content where Variant B includes a detailed, cinematic video caption, distinct from Variant A's static image caption.
*   **Django Model & Admin Updates**:
    *   The `ContentVariant` model (`backend/src/agents/models.py`) now includes an `asset` `FileField` to store generated media files (images or videos).
    *   A new migration (`0007_contentvariant_asset.py`) adds this field to the database.
    *   The Django Admin interface (`backend/src/agents/admin.py`) for `ContentVariant` is updated to display and manage the new `asset` field.
*   **Interactive Web Demo (`backend/web_demo.py`, `backend/templates/demo.html`)**:
    *   A new Flask application (`web_demo.py`) provides a user-friendly web interface (`demo.html`) to run the GTM OS demo.
    *   Users can input product descriptions and GTM goals, and optionally enable video generation for Variant B.
    *   The demo visualizes the generated campaign strategy, A/B content, and the associated AI-generated images/videos directly in the browser.
*   **Demo Script Enhancements (`backend/demo.py`)**:
    *   The existing sequential `demo.py` script is updated to integrate image generation and saving for A/B variants.
    *   A `display_image_in_terminal` utility is added to provide ASCII art previews of generated images in the console.
    *   Scenario 3 (metrics analysis) is temporarily commented out.
*   **New Example Scripts**: `backend/nano_banana.py` demonstrates direct Gemini image generation, and `backend/video_demo_example.py` illustrates how to generate and save videos to a Django `ContentVariant`.
*   **Dependencies (`backend/requirements.txt`)**: `Flask` is added. `Pillow` (for image processing in `demo.py`) and `google-genai` (for direct API calls in `media_creator.py` and examples) are now implicitly required.

### Impact
*   **New Capabilities**: The system can now generate rich, dynamic media (images and videos) directly from AI prompts, significantly enhancing the quality and diversity of marketing content.
*   **Interactive Showcase**: The new web demo provides a powerful, user-friendly way to demonstrate the full GTM OS workflow, including the new media generation features.
*   **Increased Dependencies**: New Python packages are required, notably `Flask`, `Pillow`, and `google-genai`.
*   **API Key Requirement**: `MEDIA_GEMINI_API_KEY` is now required for media generation models, in addition to the existing `GOOGLE_API_KEY` used for general LLM interactions.

### Usage
#### Running the Web Demo
1.  **Install dependencies**: `pip install -r backend/requirements.txt` (ensure `Pillow` and `google-genai` are also installed).
2.  **Set API Keys**: Ensure `GOOGLE_API_KEY` and `MEDIA_GEMINI_API_KEY` are configured in your `.env` file.
3.  **Run**: Navigate to the `backend` directory and execute: `python web_demo.py`
4.  Open your browser to `http://localhost:5000`.

#### Using `MediaCreatorAgent`
```python
from agents.media_creator import create_media_creator

# For image generation
image_agent = create_media_creator(model_name='models/gemini-2.5-flash-image')
image_data = image_agent.create_image(prompt="A minimalist logo for an AI startup")
# image_data['data'] is base64 string, image_data['mime_type'] is e.g. 'image/png'

# For video generation (requires 'models/veo-3.1-generate-preview')
video_agent = create_media_creator(model_name='models/veo-3.1-generate-preview')
video_info = video_agent.create_video(prompt="A short clip of a rocket launching into space", output_path="my_rocket.mp4")
# video_info includes 'file_path', 'mime_type', 'size_bytes'
```

### Breaking Changes
None. This update introduces new features and capabilities without altering existing core functionalities in a backward-incompatible way.

### Migration Notes
1.  **Run Django Migrations**: Apply the new migration to add the `asset` `FileField` to the `ContentVariant` model:
    `python manage.py makemigrations agents` (if not already done)
    `python manage.py migrate`
2.  **Update Dependencies**: Ensure `Flask`, `Pillow`, and `google-genai` are installed in your environment.
3.  **API Keys**: Add `MEDIA_GEMINI_API_KEY` to your `.env` file.