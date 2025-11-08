"""
Metrics Analyzer Agent
Analyzes engagement metrics from X API, provides insights, and recommends optimizations.
"""

from typing import Dict, Any, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
import os
import json


# =====================
# Output Schema
# =====================

class MetricsAnalysis(BaseModel):
    """Schema for metrics analysis output"""
    analyzed_report: str = Field(description="Detailed analysis report with insights and recommendations")


# =====================
# Metrics Analyzer Agent
# =====================

class MetricsAnalyzerAgent:
    """
    Agent specialized in analyzing X (Twitter) API metrics and providing insights.
    Focuses on engagement rates, sentiment analysis, and content performance.
    """

    def __init__(
        self,
        model_name: Optional[str] = None,
        temperature: float = 0.0
    ):
        """
        Initialize the Metrics Analyzer Agent.

        Args:
            model_name: Google Gemini model name (defaults to GEMINI_MODEL_CODE env var)
            temperature: Temperature for analysis (default: 0.0 for consistent analysis)
        """
        # Get model from environment or use provided
        if model_name is None:
            model_name = os.getenv("GEMINI_MODEL_CODE", "gemini-2.5-flash")

        # Initialize model using ChatGoogleGenerativeAI
        self.model = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temperature
        )

        # Set up structured output parser
        self.parser = JsonOutputParser(pydantic_object=MetricsAnalysis)

        # Create the prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self._get_system_prompt()),
            ("user", "{metrics_input}")
        ])

        # Create the chain
        self.chain = self.prompt | self.model | self.parser

    def _get_system_prompt(self) -> str:
        """Get the system prompt for metrics analysis"""
        return """You are an expert marketing analytics specialist focused on X (Twitter) API metrics analysis.

Your task is to analyze engagement metrics from X API responses (JSON format) and provide actionable insights.

ANALYSIS FRAMEWORK:

1. ENGAGEMENT METRICS:
   - Views: Total impressions
   - Likes: User appreciation signals
   - Retweets: Content amplification
   - Replies: Direct engagement and conversation
   - Engagement Rate: (likes + retweets + replies) / views × 100

   BENCHMARKS:
   - Excellent: ≥3.5%
   - Good: 2.5-3.5%
   - Average: 1.5-2.5%
   - Poor: <1.5%

2. SENTIMENT ANALYSIS:
   - Analyze reply sentiment (positive, neutral, negative)
   - Identify controversial or polarizing content
   - Detect community response patterns

3. PERFORMANCE INSIGHTS:
   - Time-based performance (posting time effectiveness)
   - Content format performance (text, images, videos, threads)
   - Hook effectiveness and opening strength
   - Call-to-action effectiveness
   - Hashtag impact

4. A/B VARIANT COMPARISON (if multiple posts):
   - Compare engagement rates between variants
   - Identify winning variant and explain why
   - Statistical significance of differences
   - Lessons learned for future content

5. SPECIFIC RECOMMENDATIONS:
   - Quick wins for immediate improvement
   - Content format optimizations
   - Posting time adjustments
   - Messaging and tone refinements
   - Hashtag strategy improvements
   - Audience targeting suggestions

INPUT FORMAT:
You will receive X API metrics in JSON format containing:
- Post metadata (id, text, created_at)
- Engagement metrics (views, likes, retweets, replies, quotes, bookmarks)
- Author information
- Media attachments (if any)
- For A/B tests: multiple post objects with variant labels

OUTPUT REQUIREMENTS:
Generate a comprehensive analysis report that includes:

1. EXECUTIVE SUMMARY (2-3 sentences)
   - Overall performance assessment
   - Key finding or standout metric

2. DETAILED METRICS BREAKDOWN
   - Calculate and interpret engagement rate
   - Break down each metric component
   - Compare to benchmarks

3. PERFORMANCE INSIGHTS
   - What worked well and why
   - What underperformed and why
   - Patterns and trends identified

4. A/B COMPARISON (if applicable)
   - Winner declaration with margin
   - Statistical analysis
   - Key differentiators between variants
   - Hypothesis validation

5. ACTIONABLE RECOMMENDATIONS (prioritized)
   - Immediate action items (quick wins)
   - Medium-term optimizations
   - Long-term strategy adjustments
   - Specific content/format suggestions

6. PREDICTED IMPACT
   - Expected improvement percentages
   - Confidence levels in recommendations

FORMATTING:
- Use clear section headers with markdown
- Include specific numbers and percentages
- Be data-driven and objective
- Provide concrete examples
- Keep recommendations specific and actionable

OUTPUT FORMAT:
Return a JSON object with this exact structure:
{{
  "analyzed_report": "your comprehensive markdown-formatted analysis report here"
}}

IMPORTANT: Be thorough but concise. Focus on actionable insights over generic observations."""

    def execute(self, metrics_data: Dict[str, Any]) -> MetricsAnalysis:
        """
        Analyze metrics data from X API and generate insights.

        Args:
            metrics_data: Dictionary containing X API metrics in standard format.
                         Can be a single post or multiple posts for A/B comparison.
                         Expected format follows X API v2 response structure with
                         engagement metrics (views, likes, retweets, replies, etc.)

        Returns:
            MetricsAnalysis object with analyzed_report containing detailed
            insights, recommendations, and A/B comparison (if applicable)

        Example metrics_data format:
            {
                "posts": [
                    {
                        "id": "123...",
                        "text": "Tweet content...",
                        "metrics": {
                            "views": 10000,
                            "likes": 250,
                            "retweets": 45,
                            "replies": 12
                        },
                        "variant": "A"  # optional for A/B testing
                    }
                ]
            }
        """
        # Convert metrics_data to formatted JSON string for the prompt
        metrics_json = json.dumps(metrics_data, indent=2)

        # Build the input
        metrics_input = f"""Analyze the following X API metrics data:

```json
{metrics_json}
```

Provide a comprehensive analysis with insights and specific recommendations."""

        # Generate analysis
        result = self.chain.invoke({"metrics_input": metrics_input})

        # Return as MetricsAnalysis object
        return MetricsAnalysis(**result)


# =====================
# Convenience Functions
# =====================

def create_metrics_analyzer(
    model_name: Optional[str] = None,
    temperature: float = 0.0
) -> MetricsAnalyzerAgent:
    """
    Factory function to create a Metrics Analyzer Agent.

    Args:
        model_name: Google Gemini model name (defaults to GEMINI_MODEL_CODE env var)
        temperature: Temperature for analysis (default: 0.0)

    Returns:
        Initialized MetricsAnalyzerAgent
    """
    return MetricsAnalyzerAgent(model_name=model_name, temperature=temperature)


# =====================
# Example Usage
# =====================

if __name__ == "__main__":
    # Example: Analyze metrics from X API
    agent = create_metrics_analyzer()

    # Sample metrics data (X API format)
    sample_metrics = {
        "posts": [
            {
                "id": "1234567890",
                "text": "Just shipped our new AI-powered marketing automation tool for technical founders! 🚀\n\nAutomates strategy, content creation, and A/B testing across social platforms.\n\n#SaaS #AI #Marketing",
                "created_at": "2025-11-08T10:00:00Z",
                "variant": "A",
                "metrics": {
                    "views": 15000,
                    "likes": 450,
                    "retweets": 78,
                    "replies": 23,
                    "quotes": 12,
                    "bookmarks": 89
                },
                "author": {
                    "username": "techfounder",
                    "followers": 5200
                }
            },
            {
                "id": "1234567891",
                "text": "We built an AI GTM OS that does your marketing strategy, content creation, and optimization automatically.\n\nTechnical founders: stop doing marketing manually.\n\n#AI #MarketingAutomation",
                "created_at": "2025-11-08T10:00:00Z",
                "variant": "B",
                "metrics": {
                    "views": 15200,
                    "likes": 380,
                    "retweets": 65,
                    "replies": 18,
                    "quotes": 8,
                    "bookmarks": 72
                },
                "author": {
                    "username": "techfounder",
                    "followers": 5200
                }
            }
        ]
    }

    # Analyze metrics
    result = agent.execute(sample_metrics)

    print("=" * 80)
    print("METRICS ANALYSIS REPORT")
    print("=" * 80)
    print(result.analyzed_report)
    print("=" * 80)
