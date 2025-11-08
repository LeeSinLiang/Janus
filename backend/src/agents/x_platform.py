"""
X Platform Agent
Handles X (Twitter) specific operations: posting, scheduling, and formatting.
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from . import tools
import os


class XPlatformAgent:
    """
    Agent specialized in X (Twitter) platform operations.
    Handles posting, scheduling, validation, and X-specific best practices.
    """

    def __init__(self, model_name: str = "gemini-2.5-flash", temperature: float = 0.3):
        """
        Initialize the X Platform Agent.

        Args:
            model_name: Google Gemini model name (e.g., "gemini-2.5-flash")
            temperature: Lower temperature for more precise operations
        """
        # Initialize model using ChatGoogleGenerativeAI
        self.model = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temperature
        )

        # Define available tools for this agent
        self.tools = [
            tools.post_tweet,
            tools.schedule_tweet,
            tools.validate_tweet_format,
            tools.generate_hashtags,
            tools.get_optimal_posting_time
        ]

        # Create the agent
        self.agent = create_agent(
            self.model,
            tools=self.tools,
            system_prompt=self._get_system_prompt()
        )

    def _get_system_prompt(self) -> str:
        """Get the system prompt for X Platform operations"""
        return """You are an expert X (Twitter) platform specialist.

Your responsibilities:
1. Post and schedule tweets following X best practices
2. Validate tweet format and content
3. Optimize posting times for maximum engagement
4. Ensure content meets X requirements (280 char limit, proper formatting)
5. Suggest improvements for better engagement

X PLATFORM RULES:
- Maximum 280 characters per tweet
- URLs are auto-shortened to ~23 characters
- Images/videos don't count toward character limit
- 1-3 hashtags perform best
- Emojis increase engagement
- Best posting times: 10am, 2pm, 6pm on weekdays

WORKFLOW:
1. Always VALIDATE tweet format first
2. Check optimal posting time if scheduling
3. Post or schedule the tweet
4. Confirm success and provide tweet ID

Be precise, helpful, and ensure all X platform requirements are met."""

    def post(
        self,
        content: str,
        validate_first: bool = True
    ) -> Dict[str, Any]:
        """
        Post a tweet immediately.

        Args:
            content: Tweet content
            validate_first: Whether to validate before posting

        Returns:
            Result dictionary with status and tweet_id
        """
        input_text = f"Post this tweet: {content}"
        if validate_first:
            input_text = f"First validate, then post this tweet: {content}"

        result = self.agent.invoke({
            "messages": [{"role": "user", "content": input_text}]
        })

        # Extract output
        output = self._extract_output(result)
        return {"output": output, "raw_result": result}

    def schedule(
        self,
        content: str,
        scheduled_time: Optional[str] = None,
        optimize_time: bool = True
    ) -> Dict[str, Any]:
        """
        Schedule a tweet for future posting.

        Args:
            content: Tweet content
            scheduled_time: ISO format datetime, or None to auto-optimize
            optimize_time: Whether to optimize posting time

        Returns:
            Result dictionary with schedule confirmation
        """
        if scheduled_time:
            input_text = f"Schedule this tweet for {scheduled_time}: {content}"
        else:
            input_text = f"Find the optimal posting time and schedule this tweet: {content}"

        result = self.agent.invoke({
            "messages": [{"role": "user", "content": input_text}]
        })

        # Extract output
        output = self._extract_output(result)
        return {"output": output, "raw_result": result}

    def validate_and_improve(self, content: str) -> Dict[str, Any]:
        """
        Validate tweet content and suggest improvements.

        Args:
            content: Tweet content to validate

        Returns:
            Validation result and suggestions
        """
        input_text = f"Validate this tweet and suggest improvements if needed: {content}"

        result = self.agent.invoke({
            "messages": [{"role": "user", "content": input_text}]
        })

        # Extract output
        output = self._extract_output(result)
        return {"output": output, "raw_result": result}

    def _extract_output(self, result: Dict[str, Any]) -> str:
        """Helper to extract output from agent result"""
        if "messages" in result:
            last_message = result["messages"][-1]
            if hasattr(last_message, 'content'):
                return last_message.content
            elif isinstance(last_message, dict):
                return last_message.get('content', str(last_message))
        return str(result)

    def post_variant(
        self,
        variant_data: Dict[str, Any],
        schedule: bool = False,
        scheduled_time: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Post a content variant (from Content Creator Agent).

        Args:
            variant_data: Variant data from Content Creator (must have 'content' key)
            schedule: Whether to schedule instead of posting immediately
            scheduled_time: When to schedule (if schedule=True)

        Returns:
            Posting result
        """
        content = variant_data.get("content", "")
        hashtags = variant_data.get("hashtags", "")

        # Combine content with hashtags if they fit
        full_content = f"{content} {hashtags}".strip()

        if schedule:
            return self.schedule(full_content, scheduled_time)
        else:
            return self.post(full_content)

    def post_ab_variants(
        self,
        variant_a: Dict[str, Any],
        variant_b: Dict[str, Any],
        schedule_both: bool = True,
        time_gap_hours: int = 2
    ) -> Dict[str, Any]:
        """
        Post both A/B variants with time spacing for testing.

        Args:
            variant_a: First variant data
            variant_b: Second variant data
            schedule_both: Whether to schedule or post immediately
            time_gap_hours: Hours between variant A and B posting

        Returns:
            Results for both variants
        """
        results = {
            "variant_a": None,
            "variant_b": None
        }

        # Post/schedule variant A
        if schedule_both:
            # Calculate optimal time
            now = datetime.now()
            time_a = (now + timedelta(hours=1)).isoformat()
            time_b = (now + timedelta(hours=1 + time_gap_hours)).isoformat()

            results["variant_a"] = self.post_variant(
                variant_a,
                schedule=True,
                scheduled_time=time_a
            )
            results["variant_b"] = self.post_variant(
                variant_b,
                schedule=True,
                scheduled_time=time_b
            )
        else:
            # Post A immediately, schedule B for later
            results["variant_a"] = self.post_variant(variant_a, schedule=False)

            from datetime import datetime, timedelta
            time_b = (datetime.now() + timedelta(hours=time_gap_hours)).isoformat()
            results["variant_b"] = self.post_variant(
                variant_b,
                schedule=True,
                scheduled_time=time_b
            )

        return results


# =====================
# Convenience Functions
# =====================

def create_x_platform_agent(api_key: Optional[str] = None) -> XPlatformAgent:
    """
    Factory function to create an X Platform Agent.

    Args:
        api_key: Google API key (uses GOOGLE_API_KEY env var if not provided)

    Returns:
        Initialized XPlatformAgent
    """
    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key

    return XPlatformAgent()


# =====================
# Example Usage
# =====================

if __name__ == "__main__":
    # Example: Post a tweet
    agent = create_x_platform_agent()

    # Post immediately
    result = agent.post(
        content="Excited to launch Janus - AI-powered GTM OS for technical founders! 🚀",
        validate_first=True
    )

    print("Post Result:")
    print(result)

    # Schedule a tweet
    result = agent.schedule(
        content="Check out our new features for marketing automation!",
        optimize_time=True
    )

    print("\nSchedule Result:")
    print(result)
