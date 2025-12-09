"""
Workflow Module

Creates and configures the LangGraph workflow for Text-to-SQL processing.
"""

from langgraph.graph import StateGraph, END

from src.models.state import GraphState
from src.agents.guardrails import guardrails_agent
from src.agents.sql_generator import sql_generation_agent
from src.agents.sql_executor import execute_sql
from src.agents.error_corrector import error_correction_agent
from src.agents.analyzer import analysis_agent
from src.agents.viz_decision import decide_visualization_agent
from src.agents.visualizer import visualization_agent
from src.graph.helpers import check_relevance, should_retry, should_visualize


def create_text2sql_graph():
    """
    Create the LangGraph workflow for Text-to-SQL with visualization.
    
    This function builds the complete agent workflow that handles:
    1. Input validation (guardrails)
    2. SQL generation from natural language
    3. Query execution
    4. Error correction with retries
    5. Result analysis
    6. Visualization decision and generation
    
    Returns:
        Compiled LangGraph workflow ready for execution
        
    Workflow Flow:
        START
         ↓
        Guardrails Agent → (greeting/out-of-scope) → END
         ↓ (relevant)
        SQL Generation Agent
         ↓
        Execute SQL
         ↓
        ├─ (success) → Analysis Agent
         ├─ (error) → Error Correction Agent → Execute SQL (retry)
         └─ (max retries) → Analysis Agent
         ↓
        Decide Visualization Agent
         ↓
        ├─ (needs viz) → Visualization Agent → END
         └─ (no viz) → END
    """
    # Create the state graph
    workflow = StateGraph(GraphState)
    
    # ========================================================================
    # ADD AGENT NODES
    # ========================================================================
    
    workflow.add_node("guardrails_agent", guardrails_agent)
    workflow.add_node("sql_generation_agent", sql_generation_agent)
    workflow.add_node("execute_sql", execute_sql)
    workflow.add_node("error_correction_agent", error_correction_agent)
    workflow.add_node("analysis_agent", analysis_agent)
    workflow.add_node("decide_visualization_agent", decide_visualization_agent)
    workflow.add_node("visualization_agent", visualization_agent)
    
    # ========================================================================
    # SET ENTRY POINT
    # ========================================================================
    
    workflow.set_entry_point("guardrails_agent")
    
    # ========================================================================
    # CONFIGURE EDGES
    # ========================================================================
    
    # Guardrails → SQL Generation (if relevant) or END (if greeting/out-of-scope)
    workflow.add_conditional_edges(
        "guardrails_agent",
        check_relevance,
        {"relevant": "sql_generation_agent", "end": END}
    )
    
    # SQL Generation → Execute SQL (always)
    workflow.add_edge("sql_generation_agent", "execute_sql")
    
    # Execute SQL → Analysis (success), Error Correction (retry), or Analysis (max retries)
    workflow.add_conditional_edges(
        "execute_sql",
        should_retry,
        {
            "success": "analysis_agent",
            "retry": "error_correction_agent",
            "end": "analysis_agent"
        }
    )
    
    # Error Correction → Execute SQL (retry with corrected query)
    workflow.add_edge("error_correction_agent", "execute_sql")
    
    # Analysis → Decide Visualization (always)
    workflow.add_edge("analysis_agent", "decide_visualization_agent")
    
    # Decide Visualization → Generate Visualization or END
    workflow.add_conditional_edges(
        "decide_visualization_agent",
        should_visualize,
        {"visualize": "visualization_agent", "skip": END}
    )
    
    # Visualization → END
    workflow.add_edge("visualization_agent", END)
    
    # ========================================================================
    # COMPILE AND RETURN
    # ========================================================================
    
    return workflow.compile()
