"""
Helper Functions

Contains routing logic and conditional functions for the LangGraph workflow.
"""

from src.models.state import GraphState


def check_relevance(state: GraphState) -> str:
    """
    Check if question is relevant to proceed with SQL generation.
    
    Determines the next route after guardrails validation:
    - If final_answer is set (greeting or out-of-scope), end workflow
    - If question is relevant, proceed to SQL generation
    - Otherwise, end workflow
    
    Args:
        state: Current graph state
        
    Returns:
        Route decision: "relevant" or "end"
    """
    
    # If final_answer is already set by guardrails, it's either greeting or out-of-scope
    if state.get("final_answer"):
        return "end"
    
    # Check if question is relevant
    if state.get("is_question_relavant", False):
        return "relevant"
    
    return "end"


def should_retry(state: GraphState) -> str:
    """
    Decide whether to retry SQL execution after an error.
    
    Evaluates the error state and retry count to determine if the query
    should be corrected and retried, or if the workflow should continue
    with error handling.
    
    Args:
        state: Current graph state
        
    Returns:
        Route decision: "success", "retry", or "end"
    """
    # Check if there's an error
    if state.get("error_message"):
        iteration = state.get("curr_iteration", 0)
        
        # Retry if under the limit
        if iteration <= 3:
            return "retry"
        else:
            # Max retries exceeded, proceed to analysis with error
            return "end"
    
    # No error, proceed successfully
    return "success"


def should_visualize(state: GraphState) -> str:
    """
    Decide whether to generate a visualization.
    
    Checks if visualization was requested and a valid chart type was selected.
    
    Args:
        state: Current graph state
        
    Returns:
        Route decision: "visualize" or "skip"
    """
    # Check if visualization is needed and chart type is valid
    if state.get("needs_plotly_figure", False) and state.get("type_of_plotly_figure") != "none":
        return "visualize"
    
    return "skip"
