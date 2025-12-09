"""
Agentic Text-to-SQL Chainlit Application

A production-ready multi-agent system for converting natural language queries
into SQL, executing them against an e-commerce database, and presenting results
with optional visualizations.

This application uses:
- Google Gemini for natural language understanding
- LangGraph for multi-agent workflow orchestration
- Chainlit for the interactive chat interface
- Plotly for data visualizations
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

Ask me anything about the e-commerce database, and I'll help you find the answer.

**You can ask questions like:**
- What are the top 10 selling products?
- Show me monthly revenue trends for 2023
- How many users are from California?
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
    Process user messages through the LangGraph workflow.
    
    - Extracts user query
    - Executes the multi-agent workflow
    - Streams progress updates
    - Displays SQL query and results
    - Renders visualizations if generated
    
    Args:
        message: The user's message from Chainlit
    """
    user_query = message.content
    graph = cl.user_session.get("graph")
    
    if not graph:
        await cl.Message(
            content="❌ System not initialized. Please refresh the page.",
            author="System"
        ).send()
        return
    
    # Create a message to show progress
    progress_msg = cl.Message(content="🤔 Processing your question...", author="Agent")
    await progress_msg.send()
    
    # Initialize state
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
        "messages": []
    }
    
    try:
        # Track which agents have executed
        executed_agents = []
        
        # Execute the workflow
        final_state = await graph.ainvoke(
            initial_state,
            config={"recursion_limit": 50}
        )
        
        # Update progress with executed agents
        progress_msg.content = "✅ Processing complete!"
        await progress_msg.update()
        
        # Display SQL query if generated
        if final_state.get("sql_query_generated"):
            sql_query = final_state["sql_query_generated"]
            await cl.Message(
                content=f"**🔍 Generated SQL Query:**\n```sql\n{sql_query}\n```",
                author="SQL Generator"
            ).send()
        
        # Display the final answer
        final_answer = final_state.get("final_answer", "I couldn't generate an answer.")
        await cl.Message(
            content=final_answer,
            author="Analyst"
        ).send()
        
        # Display visualization if generated
        if final_state.get("plotly_figure_json_string"):
            try:
                # Parse the Plotly figure JSON and reconstruct the Figure object
                fig_dict = json.loads(final_state["plotly_figure_json_string"])
                
                # Reconstruct the Plotly Figure from the dictionary
                # Chainlit requires a plotly.graph_objects.Figure, not a dict
                fig = go.Figure(fig_dict)
                
                # Create Plotly element for Chainlit
                fig_element = cl.Plotly(
                    name="visualization",
                    figure=fig,
                    display="inline"
                )
                
                await cl.Message(
                    content=f"**📊 Visualization ({final_state['type_of_plotly_figure'].upper()} chart):**",
                    elements=[fig_element],
                    author="Visualizer"
                ).send()
                
            except Exception as e:
                print(f"Error displaying visualization: {e}")
        
        # Display error if present
        if final_state.get("error_message"):
            await cl.Message(
                content=f"⚠️ **Note:** {final_state['error_message']}",
                author="System"
            ).send()
    
    except Exception as e:
        await cl.Message(
            content=f"❌ An error occurred: {str(e)}\n\nPlease try rephrasing your question.",
            author="System"
        ).send()


# ============================================================================
# RUN APPLICATION
# ============================================================================

if __name__ == "__main__":
    # This is handled by Chainlit CLI
    # Run with: chainlit run app.py
    pass
