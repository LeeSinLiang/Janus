"""
Content Creator Agent
Generates marketing content with A/B variants for testing.
"""

import os
from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from pydantic import BaseModel, Field


# =====================
# Output Schema
# =====================

class ContentOutput(BaseModel):
    """Schema for A/B content variants"""
    A: str = Field(description="Variant A - Professional/direct approach")
    B: str = Field(description="Variant B - Casual/engaging with emojis")


# =====================
# Content Creator Agent
# =====================

class ContentCreatorAgent:
    """
    Agent specialized in creating marketing content with A/B variants.
    Generates 2 variants for every content request, optimized for X platform.
    """

    def __init__(self, model_name: str = None, temperature: float = 0):
        """
        Initialize the Content Creator Agent.

        Args:
            model_name: Google Gemini model to use (defaults to GEMINI_MODEL_CODE env var)
            temperature: Creativity level (default: 0)
        """
        if model_name is None:
            model_name = os.getenv("GEMINI_MODEL_CODE", "gemini-2.5-flash")

        # Initialize base model
        base_model = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temperature
        )

        # Create the agent with structured output using response_format
        # This allows LangChain to automatically select the best strategy
        # (ProviderStrategy for models with native support, ToolStrategy otherwise)
        self.agent = create_agent(
            base_model,
            tools=[],  # No tools needed for content generation
            system_prompt=self._get_system_prompt(),
            response_format=ContentOutput  # Pass schema directly for automatic strategy selection
        )

    def _get_system_prompt(self) -> str:
        """Get the system prompt for content creation"""
        return """You are an expert marketing content creator specializing in social media for technical founders and SaaS products.

Your task is to create engaging tweet content with A/B variants for testing on X platform.

RULES:
1. Generate EXACTLY 2 variants (A and B) for every request
2. Each tweet MUST be under 280 characters (X platform limit)
3. Return PLAIN TEXT ONLY - NO markdown, NO formatting, NO code blocks
4. Variant A: Professional/direct approach - clear, authoritative, value-focused
5. Variant B: Casual/engaging with emojis - friendly, relatable, conversation-starter
6. Focus on what resonates with technical founders, developers, and startup owners
7. Consider optimal engagement patterns:
   - Medium length (100-200 chars) performs best
   - Emojis increase engagement by 45%
   - Questions and threads get more replies
   - Clear value propositions get more clicks

OUTPUT FORMAT:
Return structured output with fields "A" and "B" containing plain text tweet content.

IMPORTANT:
- Each variant must be under 280 characters
- NO markdown formatting in the content
- NO asterisks, NO bold, NO italics, NO code blocks
- Just plain text tweets ready to post"""

    def execute(self, title: str, description: str, product_info: str) -> ContentOutput:
        """
        Generate A/B content variants.

        Args:
            title: Content title/topic
            description: Content description
            product_info: Product information

        Returns:
            ContentOutput with A and B variants
        """
        request = f"""Create two tweet variants for:

Title: {title}
Description: {description}
Product Info: {product_info}

Generate variant A (professional/direct) and variant B (casual/engaging with emojis).
Each variant must be plain text under 280 characters."""

        result = self.agent.invoke({
            "messages": [{"role": "user", "content": request}]
        })

        # Extract the structured output
        output = self._extract_output(result)
        return output

    def execute_with_metrics(
        self,
        title: str,
        description: str,
        product_info: str,
        old_content: str,
        analyzed_report: str
    ) -> ContentOutput:
        """
        Generate improved A/B content variants based on metrics analysis (Scenario 3).

        Args:
            title: Content title/topic
            description: Content description
            product_info: Product information
            old_content: Previous content that was tested
            analyzed_report: Metrics analysis report with insights

        Returns:
            ContentOutput with improved A and B variants based on metrics
        """
        request = f"""Create two IMPROVED tweet variants based on metrics analysis:

Title: {title}
Description: {description}
Product Info: {product_info}

PREVIOUS CONTENT:
{old_content}

METRICS ANALYSIS:
{analyzed_report}

Based on the metrics analysis above, generate improved variants:
- Variant A (professional/direct): Apply insights to create a more effective professional variant
- Variant B (casual/engaging with emojis): Apply insights to create a more engaging casual variant

Each variant must be plain text under 280 characters.
Use the analyzed report to understand what worked and what didn't, then create better versions."""

        result = self.agent.invoke({
            "messages": [{"role": "user", "content": request}]
        })

        # Extract the structured output
        output = self._extract_output(result)
        return output

    def _extract_output(self, result: Dict[str, Any]) -> ContentOutput:
        """
        Extract ContentOutput from agent result.

        According to LangChain docs, structured output appears in the
        'structured_response' key of the agent's final state.

        Args:
            result: Agent invocation result

        Returns:
            ContentOutput object
        """
        # First, check for structured_response key (LangChain's standard location)
        if "structured_response" in result:
            structured_response = result["structured_response"]

            # If it's already a ContentOutput, return it
            if isinstance(structured_response, ContentOutput):
                return structured_response

            # If it's a dict, create ContentOutput
            if isinstance(structured_response, dict):
                return ContentOutput(**structured_response)

        # Fallback: Check messages array (for backward compatibility)
        messages = result.get("messages", [])
        if messages:
            last_message = messages[-1]

            # If it's already a ContentOutput, return it
            if isinstance(last_message, ContentOutput):
                return last_message

            # If it has content, try to parse it
            if hasattr(last_message, 'content'):
                content = last_message.content

                # If content is already a ContentOutput instance
                if isinstance(content, ContentOutput):
                    return content

                # If content is a dict, create ContentOutput
                if isinstance(content, dict):
                    return ContentOutput(**content)

                # If content is a string, try to parse as JSON
                if isinstance(content, str):
                    import json
                    try:
                        data = json.loads(content)
                        return ContentOutput(**data)
                    except:
                        pass  # Continue to fallback

        # Fallback if no structured output found
        return ContentOutput(
            A="Error: No output generated for variant A",
            B="Error: No output generated for variant B"
        )


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
    # Example 1: Basic content creation
    print("="*60)
    print("Example 1: Basic Content Creation")
    print("="*60)

    agent = create_content_creator()

    result = agent.execute(
        title="AI Marketing Automation Launch",
        description="Announcing our AI-powered marketing automation tool",
        product_info="Janus - AI GTM OS for technical founders"
    )

    print("\n--- Variant A (Professional/Direct) ---")
    print(f"Length: {len(result.A)} chars")
    print(result.A)

    print("\n--- Variant B (Casual/Engaging) ---")
    print(f"Length: {len(result.B)} chars")
    print(result.B)

    # Example 2: Content with metrics-based improvement
    print("\n" + "="*60)
    print("Example 2: Metrics-Based Content Improvement (Scenario 3)")
    print("="*60)

    result_with_metrics = agent.execute_with_metrics(
        title="Product Update Announcement",
        description="New feature release with AI capabilities",
        product_info="Janus - AI GTM OS",
        old_content="Variant A: Just shipped a major update to Janus. Check it out.\nVariant B: 🚀 New Janus update is live! You're gonna love this 💪",
        analyzed_report="""Analysis Summary:
- Variant B performed 3x better (45% engagement rate vs 15% for variant A)
- Emojis and enthusiasm drove significantly higher engagement
- Key weakness: Neither variant clearly stated what the update includes
- Recommendation: Keep casual tone and emojis, but add specific value proposition"""
    )

    print("\n--- Improved Variant A (Professional/Direct) ---")
    print(f"Length: {len(result_with_metrics.A)} chars")
    print(result_with_metrics.A)

    print("\n--- Improved Variant B (Casual/Engaging) ---")
    print(f"Length: {len(result_with_metrics.B)} chars")
    print(result_with_metrics.B)
