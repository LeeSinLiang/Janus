"""
Orchestrator/Supervisor Agent
Coordinates all specialized sub-agents and manages the multi-agent workflow.
"""

from typing import Dict, Any, List
from langchain_core.tools import tool
from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from .content_creator import ContentCreatorAgent
from .x_platform import XPlatformAgent
from .metrics_analyzer import MetricsAnalyzerAgent
from .strategy_planner import StrategyPlannerAgent
from .state import state
import json


class OrchestratorAgent:
    """
    Supervisor agent that coordinates all specialized sub-agents.

    Implements the LangChain supervisor pattern:
    - Layer 1: Low-level tools (in tools.py)
    - Layer 2: Specialized sub-agents (wrapped as tools)
    - Layer 3: This supervisor (routes and orchestrates)
    """

    def __init__(
        self,
        model_name: str = "gemini-2.5-flash",
        temperature: float = 0.5,
    ):
        """
        Initialize the Orchestrator Agent.

        Args:
            model_name: Google Gemini model name (e.g., "gemini-2.5-flash")
            temperature: Balanced temperature for routing decisions
        """
        # Initialize model using ChatGoogleGenerativeAI
        self.model = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temperature
        )

        # Initialize all sub-agents
        self.strategy_planner = StrategyPlannerAgent()
        self.content_creator = ContentCreatorAgent()
        self.x_platform = XPlatformAgent()
        self.metrics_analyzer = MetricsAnalyzerAgent()

        # Wrap sub-agents as tools
        self.tools = self._create_agent_tools()

        # Create the agent with correct pattern
        self.agent = create_agent(
            self.model,
            tools=self.tools,
            system_prompt=self._get_system_prompt()
        )

    def _create_agent_tools(self) -> List:
        """
        Wrap sub-agents as tools for the supervisor.

        This is the key pattern: each specialized agent becomes a tool
        that the supervisor can invoke.
        """

        @tool
        def create_marketing_strategy(request: str) -> str:
            """
            Create a marketing strategy and campaign plan.

            Use this when you need to:
            - Plan a new marketing campaign
            - Create a go-to-market strategy
            - Design campaign phases and timelines
            - Generate Mermaid diagrams for visualization

            Args:
                request: Strategy request in format "product: X, goal: Y, context: Z"

            Returns:
                Strategy with phases, Mermaid diagram, and success metrics
            """
            try:
                # Parse request
                parts = {}
                for item in request.split(','):
                    if ':' in item:
                        key, value = item.split(':', 1)
                        parts[key.strip()] = value.strip()

                product_info = parts.get('product', request)
                campaign_goal = parts.get('goal', 'Increase awareness and acquisition')
                context = {k: v for k, v in parts.items() if k not in ['product', 'goal']}

                result = self.strategy_planner.create_strategy(
                    product_info=product_info,
                    campaign_goal=campaign_goal,
                    context=context if context else None
                )

                return json.dumps(result, indent=2)
            except Exception as e:
                return f"Error creating strategy: {str(e)}"

        @tool
        def generate_content(request: str) -> str:
            """
            Generate marketing content with A/B variants.

            Use this when you need to:
            - Create tweets or social media posts
            - Generate A/B test variants
            - Create content for specific campaign phases

            Args:
                request: Content request (e.g., "Create tweet about product launch")

            Returns:
                Two content variants (A and B) with hooks, reasoning, and hashtags
            """
            try:
                result = self.content_creator.create_content(request=request)
                return json.dumps(result, indent=2)
            except Exception as e:
                return f"Error generating content: {str(e)}"

        @tool
        def post_to_x(request: str) -> str:
            """
            Post or schedule content to X (Twitter).

            Use this when you need to:
            - Post a tweet immediately
            - Schedule a tweet for later
            - Validate tweet format
            - Post A/B variants

            Args:
                request: Posting request (e.g., "Post: <content>" or "Schedule for 2pm: <content>")

            Returns:
                Confirmation with tweet ID and status
            """
            try:
                # Simple parsing for demo
                if "schedule" in request.lower():
                    content = request.split(":")[-1].strip()
                    result = self.x_platform.schedule(content, optimize_time=True)
                else:
                    content = request.replace("post:", "").replace("Post:", "").strip()
                    result = self.x_platform.post(content)

                return json.dumps(result, indent=2)
            except Exception as e:
                return f"Error posting to X: {str(e)}"

        @tool
        def analyze_metrics(request: str) -> str:
            """
            Analyze marketing metrics and provide insights.

            Use this when you need to:
            - Analyze tweet performance
            - Compare A/B test results
            - Get platform insights
            - Identify optimization opportunities
            - Generate performance reports

            Args:
                request: Analysis request (e.g., "Analyze tweet_001" or "Compare A/B results")

            Returns:
                Metrics analysis with insights and recommendations
            """
            try:
                # Determine what kind of analysis
                if "platform" in request.lower() or "insights" in request.lower():
                    result = self.metrics_analyzer.get_platform_insights()
                elif "compare" in request.lower() and "tweet_" in request:
                    # Extract tweet IDs
                    import re
                    tweet_ids = re.findall(r'tweet_\w+', request)
                    if len(tweet_ids) >= 2:
                        result = self.metrics_analyzer.compare_ab_variants(
                            tweet_ids[0],
                            tweet_ids[1]
                        )
                    else:
                        result = {"error": "Need two tweet IDs to compare"}
                elif "tweet_" in request:
                    # Extract tweet ID
                    import re
                    match = re.search(r'tweet_\w+', request)
                    if match:
                        result = self.metrics_analyzer.analyze_tweet(match.group())
                    else:
                        result = {"error": "No valid tweet ID found"}
                else:
                    result = self.metrics_analyzer.get_platform_insights()

                return json.dumps(result, indent=2)
            except Exception as e:
                return f"Error analyzing metrics: {str(e)}"

        @tool
        def update_strategy(request: str) -> str:
            """
            Update an existing marketing strategy based on metrics or feedback.

            Use this when you need to:
            - Adjust strategy based on performance
            - Update campaign phases
            - Modify tactics based on metrics

            Args:
                request: Update request in format "campaign_id: X, updates: Y"

            Returns:
                Updated strategy with new Mermaid diagram
            """
            try:
                # Parse request
                parts = {}
                for item in request.split(',', 1):
                    if ':' in item:
                        key, value = item.split(':', 1)
                        parts[key.strip()] = value.strip()

                campaign_id = parts.get('campaign_id', '')
                updates = parts.get('updates', request)

                if not campaign_id:
                    return json.dumps({"error": "campaign_id required"})

                result = self.strategy_planner.update_strategy(
                    campaign_id=campaign_id,
                    updates=updates
                )

                return json.dumps(result, indent=2)
            except Exception as e:
                return f"Error updating strategy: {str(e)}"

        return [
            create_marketing_strategy,
            generate_content,
            post_to_x,
            analyze_metrics,
            update_strategy
        ]

    def _get_system_prompt(self) -> str:
        """Get the system prompt for the orchestrator"""
        return """You are Janus, an AI-powered Go-To-Market (GTM) orchestrator for technical founders.

You coordinate specialized agents to help founders plan, execute, and optimize their marketing campaigns.

YOUR ROLE:
You are the central coordinator that breaks down user requests and routes them to specialized agents:
- Strategy Planner: Creates campaign strategies and Mermaid diagrams
- Content Creator: Generates A/B content variants
- X Platform Agent: Posts and schedules tweets
- Metrics Analyzer: Analyzes performance and provides insights

WORKFLOW APPROACH:
1. Understand the user's high-level goal
2. Break it down into agent tasks
3. Execute tasks in logical order
4. Synthesize results into coherent responses

COMMON WORKFLOWS:

**New Campaign Launch:**
1. create_marketing_strategy: Get campaign plan and phases
2. generate_content: Create content for first phase
3. post_to_x: Post or schedule the content
4. analyze_metrics: Monitor and optimize

**Content Creation & Testing:**
1. generate_content: Get A/B variants
2. post_to_x: Post both variants (scheduled)
3. analyze_metrics: Compare performance
4. update_strategy: Adjust based on results

**Performance Optimization:**
1. analyze_metrics: Get current performance
2. update_strategy: Adjust campaign based on insights
3. generate_content: Create improved content
4. post_to_x: Deploy improvements

BEST PRACTICES:
- Always start campaigns with strategy planning
- Generate A/B variants for testing
- Monitor metrics regularly
- Update strategies based on data
- Provide clear, actionable recommendations
- Think step-by-step through complex requests

USER PERSONA:
Your users are technical founders who:
- Are new to marketing
- Prefer data-driven approaches
- Want fine-grained control
- Need rapid iteration
- Value efficiency and ROI

Be helpful, concise, and always explain your reasoning."""

    def execute(self, user_input: str) -> Dict[str, Any]:
        """
        Execute a user request by coordinating sub-agents.

        Args:
            user_input: User's request or instruction

        Returns:
            Result from the orchestrated workflow
        """
        # Add to conversation history
        state.add_to_conversation("user", user_input)

        # Execute the request using correct message format
        result = self.agent.invoke({
            "messages": [{"role": "user", "content": user_input}]
        })

        # Extract the output from the result
        output = ""
        if "messages" in result:
            # Get the last message
            last_message = result["messages"][-1]
            if hasattr(last_message, 'content'):
                output = last_message.content
            elif isinstance(last_message, dict):
                output = last_message.get('content', str(last_message))
        else:
            output = str(result)

        # Add to state
        state.add_to_conversation("assistant", output)

        return {
            "output": output,
            "raw_result": result
        }

    def run_campaign_workflow(
        self,
        product_info: str,
        campaign_goal: str,
        execute_immediately: bool = False
    ) -> Dict[str, Any]:
        """
        Run a complete campaign workflow from strategy to execution.

        Args:
            product_info: Product information
            campaign_goal: Campaign goal
            execute_immediately: Whether to post content immediately or just plan

        Returns:
            Complete campaign workflow results
        """
        workflow_results = {
            "strategy": None,
            "content": None,
            "posting": None,
            "analysis": None
        }

        # Step 1: Create strategy
        strategy_request = f"product: {product_info}, goal: {campaign_goal}"
        strategy_result = self.execute(f"Create a marketing strategy for {strategy_request}")
        workflow_results["strategy"] = strategy_result

        # Step 2: Generate content for first phase
        content_request = f"Create content for campaign about {product_info}"
        content_result = self.execute(content_request)
        workflow_results["content"] = content_result

        # Step 3: Post if requested
        if execute_immediately:
            posting_result = self.execute("Post the content variant A to X")
            workflow_results["posting"] = posting_result

        # Step 4: Get platform insights
        analysis_result = self.execute("Analyze platform metrics and provide insights")
        workflow_results["analysis"] = analysis_result

        return workflow_results

    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get the conversation history"""
        return state.get_conversation_history()


# =====================
# Convenience Functions
# =====================

def create_orchestrator() -> OrchestratorAgent:
    """
    Factory function to create an Orchestrator Agent.

    Args:
        api_key: Google API key (uses GOOGLE_API_KEY env var if not provided)

    Returns:
        Initialized OrchestratorAgent
    """
    return OrchestratorAgent()


# =====================
# Example Usage
# =====================

if __name__ == "__main__":
    # Example: Run a complete workflow
    orchestrator = create_orchestrator()

    print("=== Janus Orchestrator Demo ===\n")

    # Example 1: Create a campaign
    print("1. Creating campaign strategy...")
    result = orchestrator.execute(
        "Create a marketing strategy for Janus, an AI-powered GTM OS for technical founders. "
        "Goal is to launch and get first 100 users in 4 weeks."
    )
    print(f"Result: {result.get('output', '')[:200]}...\n")

    # Example 2: Generate content
    print("2. Generating content...")
    result = orchestrator.execute(
        "Generate tweet content announcing our product launch with A/B variants"
    )
    print(f"Result: {result.get('output', '')[:200]}...\n")

    # Example 3: Analyze metrics
    print("3. Analyzing metrics...")
    result = orchestrator.execute(
        "Analyze platform insights and recommend optimal posting times"
    )
    print(f"Result: {result.get('output', '')[:200]}...\n")

    print("=== Demo Complete ===")
