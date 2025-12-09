"""
Analysis Agent

Converts SQL query results into natural language answers with key insights.
Formats responses in a user-friendly, conversational manner.
"""

from typing import List

from src.models.state import GraphState
from src.models.responses import AnalysisResponse
from src.utils.llm import get_llm


def analysis_agent(state: GraphState) -> GraphState:
    """
    Convert SQL query results into natural language answers.
    
    This function:
    1. Takes the raw SQL results and the original user question
    2. Generates a human-readable explanation of the findings
    3. Identifies key insights from the data
    4. Determines if visualization would enhance understanding
    5. Formats the response in a clear, user-friendly manner
    
    Args:
        state: Current graph state with user_query, sql_query_generated, and results
        
    Returns:
        Updated state with final_answer and needs_plotly_figure flag
    """
    user_query = state["user_query"]
    sql_query = state["sql_query_generated"]
    query_result = state["result_for_sql_query"]
    llm = get_llm()
    
    # Construct the analysis prompt
    prompt = f"""You are a data analyst expert who explains database query results in clear, natural language.

ORIGINAL USER QUESTION: "{user_query}"

SQL QUERY EXECUTED:
{sql_query}

QUERY RESULTS:
{query_result}

ANALYSIS GUIDELINES:

1. ANSWER FORMAT:
   - Start with a direct answer to the user's question
   - Use clear, conversational language (avoid technical jargon)
   - Present numbers with proper formatting (e.g., "$1,234.56" for money, "1,234" for counts)
   
2. DATA PRESENTATION:
   - For single values: state them clearly (e.g., "The total revenue was $45,678")
   - For lists/rankings: use bullet points or numbered lists
   - For comparisons: highlight differences explicitly
   - For trends: describe the pattern observed

3. CONTEXT & INSIGHTS:
   - Explain what the numbers mean in business terms
   - Identify notable patterns or outliers
   - Provide 2-3 key takeaways from the data
   
4. MULTI-PART QUESTIONS:
   - Address each part of the question separately
   - Use clear section headers if needed
   - Maintain logical flow in the answer

5. VISUALIZATION CONSIDERATION:
   - Determine if a chart would help visualize the data
   - Consider visualization for: trends over time, comparisons, distributions, rankings

Generate a comprehensive, user-friendly answer based on the query results."""
    
    # Get structured response from LLM
    structured_llm = llm.with_structured_output(AnalysisResponse)
    response = structured_llm.invoke(prompt)
    
    # Format the final answer with insights
    final_answer_parts = [response.natural_language_answer]
    
    # Add key insights if available
    if response.key_insights:
        final_answer_parts.append("\n\n**Key Insights:**")
        for i, insight in enumerate(response.key_insights, 1):
            final_answer_parts.append(f"{i}. {insight}")
    
    # Update state
    state["final_answer"] = "\n".join(final_answer_parts)
    state["needs_plotly_figure"] = response.needs_visualization
    
    return state
