"""
Visualization Decision Agent

Determines if visualization would enhance data understanding and selects
the appropriate chart type.
"""

from src.models.state import GraphState
from src.models.responses import VisualizationDecisionResponse
from src.utils.llm import get_llm


def decide_visualization_agent(state: GraphState) -> GraphState:
    """
    Determine if visualization would enhance data understanding.
    
    This function:
    1. Analyzes the query results and question type
    2. Decides if a chart would add value
    3. Selects the most appropriate chart type
    4. Provides reasoning for the decision
    
    Args:
        state: Current graph state with user_query and result_for_sql_query
        
    Returns:
        Updated state with needs_plotly_figure and type_of_plotly_figure
    """
    user_query = state["user_query"]
    query_result = state["result_for_sql_query"]
    llm = get_llm()
    
    # Skip if no results or already has error
    if not query_result or "No results found" in query_result or state.get("error_message"):
        state["needs_plotly_figure"] = False
        state["type_of_plotly_figure"] = "none"
        return state
    
    # Construct the visualization decision prompt
    prompt = f"""You are a data visualization expert. Analyze whether a chart would enhance understanding of this data.

USER QUESTION: "{user_query}"

QUERY RESULTS (first 500 chars):
{query_result[:500]}

VISUALIZATION DECISION RULES:

1. BAR CHART - Use for:
   - Comparing categories (top products, sales by region)
   - Ranking items (top 10 customers)
   - Discrete comparisons

2. LINE CHART - Use for:
   - Trends over time (monthly revenue, daily orders)
   - Time series data
   - Sequential patterns

3. PIE CHART - Use for:
   - Proportions/percentages (market share, category distribution)
   - Part-to-whole relationships
   - Maximum 5-7 categories

4. SCATTER PLOT - Use for:
   - Correlations between two variables
   - Distribution patterns
   - Outlier detection

5. NO VISUALIZATION - When:
   - Single value answers ("total: 42")
   - Simple yes/no responses
   - Text-heavy results
   - Already clear from numbers alone

Determine if visualization would add value and select the best chart type."""
    
    # Get structured response from LLM
    structured_llm = llm.with_structured_output(VisualizationDecisionResponse)
    response = structured_llm.invoke(prompt)
    
    # Update state
    state["needs_plotly_figure"] = response.needs_visualization
    state["type_of_plotly_figure"] = response.visualization_type
    
    return state
