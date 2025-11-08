"""
Metrics Analyzer Agent
Analyzes engagement metrics, provides insights, and recommends optimizations.
"""

from typing import Dict, Any, Optional, List
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from . import tools
import os


# =====================
# Output Schemas
# =====================

class MetricsInsight(BaseModel):
    """Schema for metrics analysis insights"""
    metric_type: str = Field(description="Type of metric analyzed")
    current_value: float = Field(description="Current metric value")
    benchmark: float = Field(description="Industry benchmark or target")
    performance: str = Field(description="Performance assessment (excellent/good/average/poor)")
    recommendation: str = Field(description="Actionable recommendation")


class AnalysisOutput(BaseModel):
    """Schema for complete metrics analysis"""
    summary: str = Field(description="Overall summary of metrics")
    insights: List[MetricsInsight] = Field(description="Detailed insights")
    top_recommendations: List[str] = Field(description="Top 3 recommendations")
    predicted_improvements: Dict[str, str] = Field(description="Predicted improvements if recommendations followed")


# =====================
# Metrics Analyzer Agent
# =====================

class MetricsAnalyzerAgent:
    """
    Agent specialized in analyzing marketing metrics and providing insights.
    Focuses on engagement rates, audience behavior, and content performance.
    """

    def __init__(self, model_name: str = "gemini-2.5-flash", temperature: float = 0.4):
        """
        Initialize the Metrics Analyzer Agent.

        Args:
            model_name: Google Gemini model name (e.g., "gemini-2.5-flash")
            temperature: Medium temperature for balanced analysis
        """
        # Initialize model using ChatGoogleGenerativeAI
        self.model = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temperature
        )

        # Define available tools for metrics analysis
        self.tools = [
            tools.get_tweet_metrics,
            tools.fetch_platform_metrics,
            tools.calculate_engagement_rate,
            tools.get_content_performance_insights,
            tools.analyze_audience_sentiment,
            tools.get_optimal_posting_time
        ]

        # Create the agent
        self.agent = create_agent(
            self.model,
            tools=self.tools,
            system_prompt=self._get_system_prompt()
        )

    def _get_system_prompt(self) -> str:
        """Get the system prompt for metrics analysis"""
        return """You are an expert marketing metrics analyst specializing in social media analytics.

Your responsibilities:
1. Analyze engagement metrics (views, likes, retweets, replies, engagement rate)
2. Identify patterns and trends in content performance
3. Provide actionable insights to improve marketing effectiveness
4. Recommend optimal posting times and content strategies
5. Analyze audience sentiment and feedback
6. Compare performance against industry benchmarks

KEY METRICS TO FOCUS ON:
- Engagement Rate: (likes + retweets + replies) / views * 100
  - Excellent: ≥3.5%
  - Good: 2.5-3.5%
  - Average: 1.5-2.5%
  - Poor: <1.5%
- Click-through Rate (CTR)
- Sentiment Analysis (positive/neutral/negative)
- Peak Engagement Times
- Content Format Performance

ANALYSIS APPROACH:
1. Gather relevant metrics using available tools
2. Calculate derived metrics (engagement rate, etc.)
3. Compare against benchmarks
4. Identify patterns and anomalies
5. Provide clear, actionable recommendations
6. Predict potential improvements

Be data-driven, specific, and always provide actionable insights."""

    def analyze_tweet(self, tweet_id: str) -> Dict[str, Any]:
        """
        Analyze a specific tweet's performance.

        Args:
            tweet_id: The ID of the tweet to analyze

        Returns:
            Comprehensive analysis of the tweet
        """
        input_text = f"""Analyze the performance of tweet ID: {tweet_id}

Please:
1. Get the tweet metrics
2. Calculate the engagement rate
3. Analyze audience sentiment
4. Compare performance to benchmarks
5. Provide specific recommendations for future content"""

        result = self.agent.invoke({
            "messages": [{"role": "user", "content": input_text}]
        })

        # Extract output
        output = self._extract_output(result)
        return {"output": output, "raw_result": result}

    def analyze_campaign(
        self,
        tweet_ids: List[str],
        campaign_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze multiple tweets as a campaign.

        Args:
            tweet_ids: List of tweet IDs in the campaign
            campaign_name: Optional campaign name for context

        Returns:
            Campaign-level analysis
        """
        campaign_context = f" for campaign '{campaign_name}'" if campaign_name else ""
        input_text = f"""Analyze these tweets{campaign_context}: {', '.join(tweet_ids)}

Please provide:
1. Overall campaign performance summary
2. Best and worst performing tweets
3. Average engagement rate across all tweets
4. Common patterns in high-performing content
5. Recommendations for next phase of the campaign"""

        result = self.agent.invoke({
            "messages": [{"role": "user", "content": input_text}]
        })

        # Extract output
        output = self._extract_output(result)
        return {"output": output, "raw_result": result}

    def get_platform_insights(self) -> Dict[str, Any]:
        """
        Get overall platform insights and recommendations.

        Returns:
            Platform-level insights and best practices
        """
        input_text = """Analyze the overall platform performance and provide insights:

1. Get platform metrics
2. Identify best posting times
3. Review content performance patterns
4. Provide recommendations for content strategy
5. Suggest optimal content formats and topics"""

        result = self.agent.invoke({
            "messages": [{"role": "user", "content": input_text}]
        })

        # Extract output
        output = self._extract_output(result)
        return {"output": output, "raw_result": result}

    def compare_ab_variants(
        self,
        variant_a_id: str,
        variant_b_id: str
    ) -> Dict[str, Any]:
        """
        Compare A/B test variants.

        Args:
            variant_a_id: Tweet ID for variant A
            variant_b_id: Tweet ID for variant B

        Returns:
            Comparison analysis with winner and insights
        """
        input_text = f"""Compare these A/B test variants:
- Variant A: {variant_a_id}
- Variant B: {variant_b_id}

Please:
1. Get metrics for both variants
2. Calculate engagement rates
3. Analyze sentiment for both
4. Determine the winner and by what margin
5. Explain why the winner performed better
6. Provide lessons learned for future content"""

        result = self.agent.invoke({
            "messages": [{"role": "user", "content": input_text}]
        })

        # Extract output
        output = self._extract_output(result)
        return {"output": output, "raw_result": result}

    def detect_optimization_opportunities(
        self,
        current_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Detect opportunities for optimization based on current metrics.

        Args:
            current_metrics: Current campaign or tweet metrics

        Returns:
            Optimization opportunities and recommendations
        """
        input_text = f"""Based on these current metrics: {current_metrics}

Identify optimization opportunities:
1. What's underperforming and why?
2. What quick wins can improve engagement?
3. What posting time optimizations are available?
4. What content format changes would help?
5. What audience targeting adjustments are needed?

Provide specific, actionable recommendations ranked by impact."""

        result = self.agent.invoke({
            "messages": [{"role": "user", "content": input_text}]
        })

        # Extract output
        output = self._extract_output(result)
        return {"output": output, "raw_result": result}

    def generate_performance_report(
        self,
        time_period: str = "week"
    ) -> Dict[str, Any]:
        """
        Generate a performance report for a time period.

        Args:
            time_period: Time period to analyze (e.g., "week", "month")

        Returns:
            Comprehensive performance report
        """
        input_text = f"""Generate a performance report for the past {time_period}:

Include:
1. Overall performance metrics
2. Top performing content
3. Engagement trends
4. Audience insights
5. Best and worst posting times
6. Key recommendations for next {time_period}

Make it comprehensive but actionable."""

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


# =====================
# Convenience Functions
# =====================

def create_metrics_analyzer(api_key: Optional[str] = None) -> MetricsAnalyzerAgent:
    """
    Factory function to create a Metrics Analyzer Agent.

    Args:
        api_key: Google API key (uses GOOGLE_API_KEY env var if not provided)

    Returns:
        Initialized MetricsAnalyzerAgent
    """
    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key

    return MetricsAnalyzerAgent()


# =====================
# Example Usage
# =====================

if __name__ == "__main__":
    # Example: Analyze a tweet
    agent = create_metrics_analyzer()

    # Analyze single tweet
    result = agent.analyze_tweet("tweet_001")
    print("Tweet Analysis:")
    print(result)

    # Get platform insights
    insights = agent.get_platform_insights()
    print("\nPlatform Insights:")
    print(insights)

    # Compare A/B variants
    comparison = agent.compare_ab_variants("tweet_001", "tweet_002")
    print("\nA/B Comparison:")
    print(comparison)
