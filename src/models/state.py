"""
Graph State Definition

Defines the state structure that flows through the LangGraph workflow.
Each agent node can read from and write to this state.
"""

from langgraph.graph import MessagesState


class GraphState(MessagesState):
    """
    State structure for the Text-to-SQL LangGraph workflow.
    
    Extends MessagesState to include conversation history while adding
    custom fields for tracking query processing, SQL generation, results,
    and visualization data.
    
    Attributes:
        messages: List of chat messages (inherited from MessagesState)
        is_question_relavant: Whether the user's question is relevant to the database
        user_query: The original natural language question from the user
        sql_query_generated: The SQL query generated from the natural language
        result_for_sql_query: The results from executing the SQL query
        final_answer: The natural language answer to present to the user
        error_message: Any error that occurred during processing
        curr_iteration: Current retry iteration for error correction
        needs_plotly_figure: Whether visualization should be generated
        type_of_plotly_figure: Type of chart (bar, line, pie, scatter, none)
        plotly_figure_json_string: JSON representation of the Plotly figure
    """
    
    # Guardrails output
    is_question_relavant: bool = False
    
    # User input
    user_query: str = ""
    
    # SQL generation output
    sql_query_generated: str = ""
    
    # SQL execution output
    result_for_sql_query: str = ""
    
    # Final response
    final_answer: str = ""
    
    # Error handling
    error_message: str = ""
    curr_iteration: int = 0
    
    # Visualization
    needs_plotly_figure: bool = False
    type_of_plotly_figure: str = "none"
    plotly_figure_json_string: str = ""
