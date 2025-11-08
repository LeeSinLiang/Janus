"""
Content Creator Agent
Generates marketing content with A/B variants for testing.
"""

from typing import List, Dict, Any, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field


# =====================
# Output Schema
# =====================

class ContentVariant(BaseModel):
    """Schema for a single content variant"""
    variant_id: str = Field(description="Variant identifier (A or B)")
    content: str = Field(description="The actual tweet content (max 280 chars)")
    hook: str = Field(description="The hook or angle used")
    reasoning: str = Field(description="Why this variant might perform well")
    hashtags: str = Field(description="Suggested hashtags")


class ContentOutput(BaseModel):
    """Schema for content creation output with A/B variants"""
    topic: str = Field(description="The topic or theme")
    variants: List[ContentVariant] = Field(description="Two variants (A and B)")
    recommendation: str = Field(description="Which variant to test first and why")


# =====================
# Content Creator Agent
# =====================

class ContentCreatorAgent:
    """
    Agent specialized in creating marketing content with A/B variants.
    Generates 2 variants for every content request, optimized for engagement.
    """

    def __init__(self, model_name: str = "gemini-2.5-flash", temperature: float = 0.7):
        """
        Initialize the Content Creator Agent.

        Args:
            model_name: Google Gemini model to use
            temperature: Creativity level (0.0-1.0)
        """
        self.model = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temperature
        )

        # Set up structured output parser
        self.parser = JsonOutputParser(pydantic_object=ContentOutput)

        # Create the prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self._get_system_prompt()),
            ("user", "{request}")
        ])

        # Create the chain
        self.chain = self.prompt | self.model | self.parser

    def _get_system_prompt(self) -> str:
        """Get the system prompt for content creation"""
        return """You are an expert marketing content creator specializing in social media for technical founders and SaaS products.

Your task is to create engaging tweet content with A/B variants for testing.

RULES:
1. Generate EXACTLY 2 variants (A and B) for every request
2. Each tweet MUST be under 280 characters
3. Variants should test different angles/hooks:
   - Variant A: More direct/professional approach
   - Variant B: More casual/engaging with emojis
4. Focus on what resonates with technical founders, developers, and startup owners
5. Include relevant hashtags (2-3 max)
6. Consider optimal engagement patterns:
   - Medium length (100-200 chars) performs best
   - Emojis increase engagement by 45%
   - Questions and threads get more replies
   - Clear value propositions get more clicks

OUTPUT FORMAT:
Return a JSON object with this exact structure:
{{
  "topic": "brief description of the topic",
  "variants": [
    {{
      "variant_id": "A",
      "content": "the tweet text (max 280 chars)",
      "hook": "the angle/hook used (e.g., 'pain point', 'social proof', 'curiosity')",
      "reasoning": "why this variant might perform well",
      "hashtags": "suggested hashtags"
    }},
    {{
      "variant_id": "B",
      "content": "alternative tweet text (max 280 chars)",
      "hook": "different angle/hook",
      "reasoning": "why this variant might perform well",
      "hashtags": "suggested hashtags"
    }}
  ],
  "recommendation": "which variant to test first and why"
}}

IMPORTANT: Ensure ALL content is under 280 characters including hashtags!"""

    def create_content(self, request: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create content with A/B variants.

        Args:
            request: Content request (e.g., "Create a tweet announcing our product launch")
            context: Optional context (campaign info, brand voice, previous performance)

        Returns:
            Dictionary with content variants and metadata
        """
        # Build the full request with context if provided
        full_request = request
        if context:
            full_request += f"\n\nContext: {context}"

        # Generate content
        result = self.chain.invoke({"request": full_request})

        return result

    def create_thread_content(
        self,
        topic: str,
        num_tweets: int = 3,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a Twitter thread with A/B variants for each tweet.

        Args:
            topic: Thread topic
            num_tweets: Number of tweets in the thread
            context: Optional context

        Returns:
            Dictionary with thread content and variants
        """
        request = f"""Create a Twitter thread about: {topic}

The thread should have {num_tweets} tweets.
For EACH tweet in the thread, generate 2 variants (A and B).

Structure the thread to:
1. Hook (grab attention)
2. Value/Information (deliver key points)
3. Call-to-action (end with engagement prompt)

Return all tweets with their A/B variants."""

        if context:
            request += f"\n\nContext: {context}"

        # For threads, we'll make multiple calls
        # For now, return a simplified version
        result = self.chain.invoke({"request": request})

        return result

    def refine_variant(
        self,
        original_content: str,
        feedback: str,
        metrics: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Refine a content variant based on feedback or metrics.

        Args:
            original_content: The original tweet content
            feedback: Feedback or improvement direction
            metrics: Optional metrics from previous similar content

        Returns:
            Refined content with variants
        """
        request = f"""Refine this tweet content: "{original_content}"

Feedback/Direction: {feedback}"""

        if metrics:
            request += f"\n\nPrevious metrics: {metrics}"

        request += "\n\nGenerate 2 improved variants (A and B) based on the feedback."

        result = self.chain.invoke({"request": request})

        return result


# =====================
# Convenience Functions
# =====================

def create_content_creator() -> ContentCreatorAgent:
    """
    Factory function to create a Content Creator Agent.

    Returns:
        Initialized ContentCreatorAgent
    """
    return ContentCreatorAgent()


# =====================
# Example Usage
# =====================

if __name__ == "__main__":
    # Example: Create content
    agent = create_content_creator()

    result = agent.create_content(
        request="Create a tweet announcing our AI-powered marketing automation tool for technical founders",
        context={
            "brand_voice": "helpful, technical, friendly",
            "target_audience": "technical founders, developers",
            "product": "Janus - AI GTM OS"
        }
    )

    print("Content Creation Result:")
    print(f"Topic: {result['topic']}")
    print("\n--- Variant A ---")
    print(f"Content: {result['variants'][0]['content']}")
    print(f"Hook: {result['variants'][0]['hook']}")
    print(f"Hashtags: {result['variants'][0]['hashtags']}")
    print(f"Reasoning: {result['variants'][0]['reasoning']}")
    print("\n--- Variant B ---")
    print(f"Content: {result['variants'][1]['content']}")
    print(f"Hook: {result['variants'][1]['hook']}")
    print(f"Hashtags: {result['variants'][1]['hashtags']}")
    print(f"Reasoning: {result['variants'][1]['reasoning']}")
    print(f"\nRecommendation: {result['recommendation']}")
