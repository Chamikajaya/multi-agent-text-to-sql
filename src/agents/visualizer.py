"""
Visualizer Agent

Generates Plotly visualization code from query results and executes it
to create charts for the Chainlit UI.
"""

import json
import pandas as pd

from src.models.state import GraphState
from src.models.responses import PlotlyCodeResponse
from src.utils.llm import get_llm


def visualization_agent(state: GraphState) -> GraphState:
    """
    Generate Plotly visualization code from query results.
    
    This function:
    1. Takes the query results and chart type
    2. Generates Python code using Plotly
    3. Executes the code to create a figure
    4. Exports the figure as JSON for rendering
    
    Args:
        state: Current graph state with results and chart type
        
    Returns:
        Updated state with plotly_figure_json_string or error handling
    """
    user_query = state["user_query"]
    query_result = state["result_for_sql_query"]
    chart_type = state["type_of_plotly_figure"]
    llm = get_llm()
    
    try:
        # Construct the visualization code generation prompt
        prompt = f"""Generate Python code using Plotly to create a {chart_type} chart for this data.

USER QUESTION: "{user_query}"

QUERY RESULTS:
{query_result}

REQUIREMENTS:
1. Use plotly.graph_objects (as 'go') or plotly.express (as 'px')
2. Data is available as a pandas DataFrame named 'df'
3. Create a {chart_type} chart
4. Add proper title, labels, and formatting
5. Variable must be named 'fig'
6. NO import statements (already imported)
7. NO fig.show() or display commands
8. Limit to top 20 data points if there are many rows
9. Use appropriate colors and styling
10. Add hover information

EXAMPLE STRUCTURE:
```python
# Parse data from results
df = pd.DataFrame({{
    'column1': [values],
    'column2': [values]
}})

# Create figure
fig = go.Figure(...)
# or
fig = px.{chart_type}(df, ...)

# Update layout
fig.update_layout(
    title='Chart Title',
    xaxis_title='X Label',
    yaxis_title='Y Label'
)
```

Generate the complete Plotly code:"""
        
        # Get structured response from LLM
        structured_llm = llm.with_structured_output(PlotlyCodeResponse)
        response = structured_llm.invoke(prompt)
        
        # Clean the plotly code
        plotly_code = response.plotly_code.strip()
        plotly_code = plotly_code.replace("```python", "").replace("```", "").strip()
        
        # Prepare execution environment
        exec_globals = {
            'pd': pd,
            'json': json
        }
        
        # Import Plotly
        import plotly.graph_objects as go
        import plotly.express as px
        exec_globals['go'] = go
        exec_globals['px'] = px
        
        # Execute the generated code
        exec(plotly_code, exec_globals)
        
        # Get the figure
        fig = exec_globals.get('fig')
        
        if fig is None:
            raise ValueError("Generated code did not create a 'fig' variable")
        
        # Convert to JSON
        state["plotly_figure_json_string"] = fig.to_json()
    
    except Exception as e:
        # If visualization fails, just log and continue without viz
        print(f"Visualization generation error: {e}")
        state["plotly_figure_json_string"] = ""
        state["needs_plotly_figure"] = False
    
    return state
