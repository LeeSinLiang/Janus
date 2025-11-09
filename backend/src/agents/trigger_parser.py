"""
Trigger Parser Agent - Parses natural language trigger prompts into structured trigger configurations.

Uses modern LangChain structured output with response_format for parsing user prompts like:
"less than 5 within 3600, make it in cartoon style post"

Outputs:
- value: int (threshold value for trigger)
- comparison: Literal['<', '=', '>'] (comparison operator)
- duration: int (minimum elapsed time in seconds before trigger fires)
- prompt: str (action prompt when trigger is activated)
"""

import os
from typing import Literal
from pydantic import BaseModel, Field
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()


class TriggerConfig(BaseModel):
    """Structured output schema for trigger configuration."""

    value: int = Field(
        description="The numeric threshold value for the trigger condition (e.g., 5 for 'less than 5 likes')"
    )
    comparison: Literal['<', '=', '>'] = Field(
        description="The comparison operator: '<' for less than, '=' for equals, '>' for greater than"
    )
    duration: int = Field(
        description="Minimum elapsed time in seconds before trigger can fire (e.g., 3600 for 1 hour, 7200 for 2 hours)"
    )
    prompt: str = Field(
        description="The action prompt/instruction to execute when the trigger is activated (e.g., 'make it in cartoon style post', 'focus on emotional engagement')"
    )


class TriggerParserAgent:
    """Agent that parses natural language trigger prompts into structured configurations."""

    def __init__(self, model_name: str = "gemini-2.5-flash"):
        """
        Initialize the trigger parser agent.

        Args:
            model_name: The model to use for parsing (default: gemini-2.5-flash)
        """
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")

        # Initialize model with temperature=0 for consistent structured output
        model = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=0,
            google_api_key=api_key
        )

        system_prompt = """You are a trigger configuration parser. Your job is to parse natural language trigger prompts into structured data.

The user will provide a prompt in the format:
"COMPARISON VALUE within DURATION, ACTION_PROMPT"

Examples:
- "less than 5 within 3600, make it in cartoon style post"
  → value=5, comparison='<', duration=3600, prompt='make it in cartoon style post'

- "greater than 10 within 7200, create celebratory follow-up post"
  → value=10, comparison='>', duration=7200, prompt='create celebratory follow-up post'

- "equals 0 within 1800, pivot strategy immediately"
  → value=0, comparison='=', duration=1800, prompt='pivot strategy immediately'

- "under 3 within 600, improve engagement tactics"
  → value=3, comparison='<', duration=600, prompt='improve engagement tactics'

IMPORTANT:
- Extract the numeric threshold value (e.g., 5 from "less than 5")
- Map comparison words to operators: 'less than'/'under'/'<' → '<', 'greater than'/'over'/'>' → '>', 'equals'/'=' → '='
- Extract the duration in seconds (number after "within")
- Extract the action prompt (everything after the comma)
- Be flexible with natural language variations
- Duration is ALWAYS required and must be in seconds
"""

        # Create agent with structured output using response_format
        self.agent = create_agent(
            model=model,
            tools=[],
            system_prompt=system_prompt,
            response_format=TriggerConfig
        )

    def parse(self, condition: str, user_prompt: str) -> TriggerConfig:
        """
        Parse a natural language trigger prompt into structured configuration.

        Args:
            condition: The metric condition being monitored (e.g., 'likes', 'retweets')
            user_prompt: Natural language prompt (e.g., 'less than 5 within 3600, make it in cartoon style')

        Returns:
            TriggerConfig with parsed value, comparison, duration, and prompt

        Example:
            >>> agent = TriggerParserAgent()
            >>> config = agent.parse('likes', 'less than 5 within 3600, make it in cartoon style')
            >>> print(config.value)  # 5
            >>> print(config.comparison)  # '<'
            >>> print(config.duration)  # 3600
            >>> print(config.prompt)  # 'make it in cartoon style'
        """
        # Invoke agent with the user's prompt
        result = self.agent.invoke({
            "messages": [
                {
                    "role": "user",
                    "content": f"Parse this trigger for {condition}: {user_prompt}"
                }
            ]
        })

        # Access structured output via 'structured_response' key (modern LangChain v1.0)
        trigger_config = result["structured_response"]

        return trigger_config

def create_trigger_parser(model_name: str = "gemini-2.5-flash-lite") -> TriggerParserAgent:
    """
    Factory function to create a TriggerParserAgent instance. Use lite for fast parsing.

    Args:
        model_name: The model to use for parsing

    Returns:
        Initialized TriggerParserAgent
    """
    return TriggerParserAgent(model_name=model_name)


# CLI test function
if __name__ == "__main__":
    print("🔍 Testing TriggerParserAgent\n")

    # Test cases
    test_cases = [
        ("likes", "less than 5 within 3600 seconds, make it in cartoon style post"),
        ("retweets", "greater than 10 within 7200, create celebratory follow-up post"),
        ("impressions", "equals 0 within 1800 seconds, pivot strategy immediately"),
        ("comments", "under 3 within 600, improve engagement tactics"),
    ]

    agent = create_trigger_parser()

    for condition, prompt in test_cases:
        print(f"📝 Input: condition='{condition}', prompt='{prompt}'")
        result = agent.parse(condition, prompt)
        print(f"✅ Output: value={result.value}, comparison='{result.comparison}', duration={result.duration}, prompt='{result.prompt}'")
        print()
