import os
import time
from typing import Literal
from google import genai
from google.genai import types
from langchain.messages import AIMessage

from langchain_google_genai import ChatGoogleGenerativeAI


class MediaCreatorAgent:
	def __init__(self, model_name: Literal['models/gemini-2.5-flash-image', 'models/gemini-2.0-flash-preview-image-generation', 'models/veo-3.1-generate-preview']):
		self.model_name = model_name
		self.llm = ChatGoogleGenerativeAI(
			model=self.model_name,
			google_api_key=os.environ.get("MEDIA_GEMINI_API_KEY"),
		)
		self.client = genai.Client(
			api_key=os.environ.get("MEDIA_GEMINI_API_KEY"),
		)
	
	def _get_image_data(self, response: AIMessage) -> dict:
		"""Extract image data from response.

		Returns:
			dict with 'mime_type' and 'data' (base64 string without prefix)
		"""
		image_block = next(
			block
			for block in response.content
			if isinstance(block, dict) and block.get("image_url")
		)
		# URL format: data:image/png;base64,<base64data>
		url = image_block["image_url"].get("url")

		# Split to get format and data
		if ';base64,' in url:
			format_part, base64_data = url.split(';base64,', 1)
			mime_type = format_part.replace('data:', '')
		else:
			# Fallback if format is different
			mime_type = 'image/png'
			base64_data = url.split(',')[-1]

		return {
			'mime_type': mime_type,
			'data': base64_data
		}


	def create_image(self, prompt: str) -> dict:
		"""Generate an image from a text prompt.

		Args:
			prompt: Text description of the image to generate

		Returns:
			dict with 'mime_type' (e.g., 'image/png') and 'data' (base64 string)
		"""
		if (self.model_name != 'models/gemini-2.5-flash-image' and self.model_name != 'models/gemini-2.0-flash-preview-image-generation'):
			raise ValueError("Model must be 'models/gemini-2.5-flash-image' or 'models/gemini-2.0-flash-preview-image-generation' for image generation.")

		response = self.llm.invoke(
			[
				{
					"role": "user",
					"content": f"Generate an image for the following prompt: {prompt}."
				}
			],
			generation_config=dict(response_modalities=["TEXT", "IMAGE"])
		)
		return self._get_image_data(response)
	
	def create_video(self, prompt: str, output_path: str = None) -> dict:
		"""Generate a video from a text prompt.

		Args:
			prompt: Text description of the video to generate
			output_path: Optional path to save the video. If not provided, saves to 'generated_videos/' directory

		Returns:
			dict with 'mime_type', 'file_path', and 'size_bytes'
		"""
		if self.model_name != 'models/veo-3.1-generate-preview':
			raise ValueError("Model must be 'models/veo-3.1-generate-preview' for video generation.")

		print(f"🎬 Generating video: {prompt[:60]}...")

		operation = self.client.models.generate_videos(
			model="veo-3.1-generate-preview",
			prompt=prompt,
		)

		# Wait for video generation to complete
		elapsed_time = 0
		while not operation.done:
			print(f"⏳ Waiting for video generation... ({elapsed_time}s elapsed)")
			time.sleep(10)
			elapsed_time += 10
			operation = self.client.operations.get(operation)

		print("✅ Video generation complete!")

		# Download the generated video
		generated_video = operation.response.generated_videos[0]
		video_file = generated_video.video

		# Determine output path
		if output_path is None:
			# Create generated_videos directory if it doesn't exist
			import os
			os.makedirs("generated_videos", exist_ok=True)

			# Generate filename with timestamp
			timestamp = int(time.time())
			output_path = f"generated_videos/video_{timestamp}.mp4"

		# Download and save
		print(f"💾 Saving video to: {output_path}")
		self.client.files.download(file=video_file)
		video_file.save(output_path)

		# Get file size
		import os
		file_size = os.path.getsize(output_path)

		print(f"✅ Video saved: {output_path} ({file_size / 1024 / 1024:.2f} MB)")

		return {
			'mime_type': 'video/mp4',
			'file_path': output_path,
			'size_bytes': file_size
		}



def create_media_creator(model_name: Literal['models/gemini-2.5-flash-image', 'models/gemini-2.0-flash-preview-image-generation', 'models/veo-3.1-generate-preview']) -> MediaCreatorAgent:
	return MediaCreatorAgent(model_name=model_name)
