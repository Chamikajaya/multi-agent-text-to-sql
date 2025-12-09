"""
Agentic Text-to-SQL Chainlit Application

A production-ready multi-agent system for converting natural language queries
into SQL, executing them against an e-commerce database, and presenting results
with optional visualizations.

"""

import chainlit as cl
import json
from pathlib import Path
from dotenv import load_dotenv
import plotly.graph_objects as go

from src.graph.workflow import create_text2sql_graph
from src.database.db_manager import initialize_database, verify_database
from src.config import DB_PATH


# Load environment variables from .env file
load_dotenv()


# ============================================================================
# APPLICATION STARTUP
# ============================================================================

@cl.on_chat_start
async def start():
    """
    Initialize the application when a new chat session starts.
    
    - Displays welcome message
    - Initializes database if needed
    - Creates the LangGraph workflow
    - Stores workflow in session
    """
    # Display welcome message
    await cl.Message(
        content="""# 🚀 Welcome to Agentic Text-to-SQL!

Ask me anything about the Looker e-commerce database, and I'll help you find the answer.

**You can ask questions like:**
- What are the top 10 selling products?
- How many users are from Atlanta?
- What is the average order value by product category?

I'll generate SQL queries, execute them, analyze the results, and even create visualizations when appropriate!
""",
        author="System"
    ).send()
    
    # Initialize database if it doesn't exist
    if not DB_PATH.exists():
        await cl.Message(
            content="🔨 Initializing database for the first time...",
            author="System"
        ).send()
        
        try:
            initialize_database()
            table_counts = verify_database()
            
            summary_lines = ["✅ Database initialized successfully!\n"]
            summary_lines.append("**Tables loaded:**")
            for table_name, count in table_counts.items():
                summary_lines.append(f"- {table_name}: {count:,} rows")
            
            await cl.Message(
                content="\n".join(summary_lines),
                author="System"
            ).send()
            
        except Exception as e:
            await cl.Message(
                content=f"❌ Error initializing database: {str(e)}",
                author="System"
            ).send()
            return
    
    # Create the LangGraph workflow
    try:
        graph = create_text2sql_graph()
        cl.user_session.set("graph", graph)
        
        await cl.Message(
            content="✅ System ready! Ask me a question about the data.",
            author="System"
        ).send()
        
    except Exception as e:
        await cl.Message(
            content=f"❌ Error initializing workflow: {str(e)}",
            author="System"
        ).send()


# ============================================================================
# MESSAGE HANDLING
# ============================================================================

@cl.on_message
async def main(message: cl.Message):
    """
    Process user messages through the LangGraph workflow with real-time visualization.
    
    Shows each agent's execution as an expandable step with detailed output.
    """
    user_query = message.content
    graph = cl.user_session.get("graph")
    
    if not graph:
        await cl.Message(
            content="❌ System not initialized. Please refresh the page.",
            author="System"
        ).send()
        return
    
    # Create main workflow step that shows all agent activity
    async with cl.Step(name="🤖 Agent Workflow", type="llm") as workflow_step:
        
        # Dictionary to hold step references for each agent
        node_steps = {}
        final_result = None
        
        # Agent display names with icons
        node_display_names = {
            "guardrails_agent": "🛡️ Guardrails Agent",
            "sql_generation_agent": "📝 SQL Generation Agent",
            "execute_sql": "⚙️ Execute SQL Query",
            "error_correction_agent": "🔧 Error Correction Agent",
            "analysis_agent": "💬 Analysis Agent",
            "decide_visualization_agent": "📊 Decide Graph Need",
            "visualization_agent": "📈 Generate Visualization"
        }
        
        try:
            # Import streaming function
            from src.graph.streaming import process_question_stream
            
            # Stream through the agent execution
            async for event in process_question_stream(user_query):
                event_type = event.get("type")
                
                # Handle node start - create a step for this agent
                if event_type == "node_start":
                    node_name = event["node"]
                    display_name = node_display_names.get(node_name, node_name)
                    
                    # Create a collapsible step for this agent
                    node_step = cl.Step(
                        name=display_name,
                        type="tool",
                        parent_id=workflow_step.id
                    )
                    await node_step.send()
                    node_steps[node_name] = node_step
                
                # Handle node end - update step with output
                elif event_type == "node_end":
                    node_name = event["node"]
                    state = event.get("state", {})
                    
                    if node_name in node_steps:
                        node_step = node_steps[node_name]
                        output_text = ""
                        
                        # Format output based on agent type
                        if node_name == "guardrails_agent":
                            if state.get("final_answer") and not state.get("is_question_relavant"):
                                output_text = f"**Decision:** Question handled\n\n{state['final_answer']}"
                            elif state.get("is_question_relavant"):
                                output_text = "✅ **Decision:** Question is relevant - proceeding to SQL generation"
                            else:
                                output_text = "✅ **Validation:** Question passed guardrails check"
                        
                        elif node_name == "sql_generation_agent":
                            sql = state.get("sql_query_generated", "")
                            if sql:
                                output_text = f"**Generated SQL Query:**\n```sql\n{sql}\n```"
                            else:
                                output_text = "⚠️ No SQL generated"
                        
                        elif node_name == "execute_sql":
                            if state.get("error_message"):
                                output_text = f"❌ **Error:**\n```\n{state['error_message']}\n```"
                            else:
                                result = state.get("result_for_sql_query", "")
                                # Truncate long results for display
                                if len(result) > 500:
                                    result = result[:500] + "\n... (truncated)"
                                output_text = f"✅ **Query Executed Successfully**\n\n**Results Preview:**\n```\n{result}\n```"
                        
                        elif node_name == "error_correction_agent":
                            corrected = state.get("sql_query_generated", "")
                            iteration = state.get("curr_iteration", 0)
                            output_text = f"**Corrected SQL (Attempt {iteration}):**\n```sql\n{corrected}\n```"
                        
                        elif node_name == "analysis_agent":
                            answer = state.get("final_answer", "")
                            if answer:
                                # Show a preview of the answer
                                preview = answer[:200] + "..." if len(answer) > 200 else answer
                                output_text = f"✅ **Analysis Complete**\n\n**Answer Preview:**\n{preview}"
                            else:
                                output_text = "⚠️ No answer generated"
                        
                        elif node_name == "decide_visualization_agent":
                            needs_viz = state.get("needs_plotly_figure", False)
                            viz_type = state.get("type_of_plotly_figure", "")
                            if needs_viz and viz_type != "none":
                                output_text = f"✅ **Visualization Recommended:** {viz_type.upper()} chart"
                            else:
                                output_text = "ℹ️ **No visualization needed** for this query"
                        
                        elif node_name == "visualization_agent":
                            has_viz = bool(state.get("plotly_figure_json_string"))
                            if has_viz:
                                output_text = "✅ **Visualization generated successfully**"
                            else:
                                output_text = "⚠️ Visualization generation skipped or failed"
                        
                        # Update the step with formatted output
                        node_step.output = output_text
                        await node_step.update()
                
                # Handle final result
                elif event_type == "final":
                    final_result = event["result"]
                
                # Handle errors in streaming
                elif event_type == "error":
                    error_msg = event["error"]
                    workflow_step.output = f"❌ **Error:** {error_msg}"
                    await workflow_step.update()
                    return
            
            # Mark workflow as complete
            workflow_step.output = "✅ Workflow completed successfully"
            await workflow_step.update()
        
        except Exception as e:
            workflow_step.output = f"❌ **Unexpected Error:** {str(e)}"
            await workflow_step.update()
            raise
    
    # Send final response outside the workflow step
    if final_result:
        # Only show SQL query if it exists and is not empty
        if final_result.get('sql_query_generated') and final_result['sql_query_generated'].strip():
            response_content = f"""**🔍 Generated SQL Query:**
```sql
{final_result['sql_query_generated']}
```

**💬 Answer:**
{final_result['final_answer']}
"""
        else:
            # For greetings or out-of-scope messages
            response_content = final_result['final_answer']
        
        # Include error if present
        if final_result.get('error_message'):
            response_content += f"\n\n⚠️ **Note:** {final_result['error_message']}"
        
        # Send text response
        await cl.Message(content=response_content).send()
        
        # Send visualization if available
        if final_result.get('needs_plotly_figure') and final_result.get('plotly_figure_json_string'):
            try:
                # Reconstruct the Plotly figure
                fig_dict = json.loads(final_result['plotly_figure_json_string'])
                fig = go.Figure(fig_dict)
                
                graph_element = cl.Plotly(
                    name=f"{final_result.get('type_of_plotly_figure', 'chart')}_visualization",
                    figure=fig,
                    display="inline"
                )
                
                await cl.Message(
                    content=f"📊 **Interactive Visualization ({final_result.get('type_of_plotly_figure', 'chart').title()} Chart)**\n\n*Hover over the chart for details, zoom, and pan!*",
                    elements=[graph_element]
                ).send()
            
            except Exception as e:
                print(f"Error displaying visualization: {e}")


# ============================================================================
# RUN APPLICATION
# ============================================================================

if __name__ == "__main__":
    # This is handled by Chainlit CLI
    # Run with: chainlit run app.py
    pass
