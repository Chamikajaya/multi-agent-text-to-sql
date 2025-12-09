"""
Streaming Utilities

Provides async streaming functionality for real-time updates in Chainlit.
"""

from typing import AsyncGenerator, Dict, Any

from src.graph.workflow import create_text2sql_graph


async def process_question_stream(user_query: str) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Process a natural language question and stream node execution events.
    
    This async generator streams events from the LangGraph workflow execution,
    allowing for real-time updates in the Chainlit UI.
    
    Args:
        user_query: The natural language question from the user
        
    Yields:
        dict: Event dictionaries with structure:
            - type: 'node_start', 'node_end', 'error', or 'final'
            - node: Name of the agent node
            - data: Relevant state/output data
            
    Event Types:
        - node_start: When an agent node begins execution
        - node_end: When an agent node completes execution
        - final: When the entire workflow completes
        - error: When an exception occurs
    """
    # Initialize the graph state
    initial_state = {
        "user_query": user_query,
        "is_question_relavant": False,
        "sql_query_generated": "",
        "result_for_sql_query": "",
        "final_answer": "",
        "error_message": "",
        "curr_iteration": 0,
        "needs_plotly_figure": False,
        "type_of_plotly_figure": "none",
        "plotly_figure_json_string": "",
        "messages": []  # Required by MessagesState
    }
    
    # Get the compiled graph
    graph = create_text2sql_graph()
    
    try:
        # Stream events from the compiled graph
        async for event in graph.astream_events(
            initial_state,
            config={"recursion_limit": 50},
            version="v2"  # Use v2 for better event streaming
        ):
            event_type = event.get("event")
            event_name = event.get("name", "")
            
            # Node execution start
            if event_type == "on_chain_start":
                # Filter for our agent nodes
                if event_name in [
                    "guardrails_agent",
                    "sql_generation_agent", 
                    "execute_sql",
                    "error_correction_agent",
                    "analysis_agent",
                    "decide_visualization_agent",
                    "visualization_agent"
                ]:
                    yield {
                        "type": "node_start",
                        "node": event_name,
                        "timestamp": event.get("timestamp")
                    }
            
            # Node execution end
            elif event_type == "on_chain_end":
                if event_name in [
                    "guardrails_agent",
                    "sql_generation_agent",
                    "execute_sql", 
                    "error_correction_agent",
                    "analysis_agent",
                    "decide_visualization_agent",
                    "visualization_agent"
                ]:
                    # Extract output from event data
                    output = event.get("data", {}).get("output", {})
                    
                    yield {
                        "type": "node_end",
                        "node": event_name,
                        "output": output,
                        "timestamp": event.get("timestamp")
                    }
        
        # Get final state
        final_state = await graph.ainvoke(initial_state)
        
        yield {
            "type": "final",
            "result": final_state
        }
        
    except Exception as e:
        yield {
            "type": "error",
            "error": str(e),
            "error_type": type(e).__name__
        }
