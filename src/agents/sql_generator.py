"""
SQL Generator Agent

Converts natural language questions into valid SQLite queries.
Uses schema knowledge and best practices to generate optimized SQL.
"""

from src.models.state import GraphState
from src.models.responses import SQLGenerationResponse
from src.database.schema import SCHEMA_DEFINITION
from src.utils.llm import get_llm


def sql_generation_agent(state: GraphState) -> GraphState:
    """
    Generate SQL query from natural language question.
    
    Takes the user's natural language query and converts it into a valid
    SQLite query using the database schema definition. Applies SQL best
    practices and optimization techniques.
    
    Args:
        state: Current graph state containing user_query
        
    Returns:
        Updated state with sql_query_generated and incremented curr_iteration
    """
    user_query = state["user_query"]
    iteration = state.get("curr_iteration", 0)
    llm = get_llm()
    
    # Construct the SQL generation prompt
    prompt = f"""You are an expert SQL developer specializing in SQLite databases. Convert the user's natural language question into a valid, optimized SQLite query.

{SCHEMA_DEFINITION}

QUERY GENERATION RULES:

1. SCHEMA COMPLIANCE:
   - Use ONLY tables and columns defined in the schema above
   - Respect data types (TEXT, INTEGER, REAL, TIMESTAMP)
   - Follow foreign key relationships for JOINs

2. SQL BEST PRACTICES:
   - Use explicit JOIN syntax (INNER JOIN, LEFT JOIN) with ON clauses
   - Apply WHERE filters before aggregations
   - Use meaningful table aliases (p for products, u for users, o for orders)
   - Add ORDER BY for ranked results
   - Include LIMIT 10 unless user specifies a different number

3. AGGREGATIONS & ANALYTICS:
   - Use COUNT, SUM, AVG, MIN, MAX appropriately
   - GROUP BY required columns when using aggregates
   - Use HAVING for post-aggregation filters
   - Calculate revenue using order_items.sale_price (NOT products.retail_price)

4. DATE HANDLING:
   - Dates are stored as TEXT in ISO format (YYYY-MM-DD HH:MM:SS)
   - Use DATE() function for date comparisons
   - Use strftime() for date formatting and extraction

5. REVENUE CALCULATIONS:
   - Always use order_items.sale_price for actual revenue
   - Join with orders table to filter by status (exclude 'Cancelled', 'Returned')
   - Consider order status when calculating metrics

6. COMMON PATTERNS:
   - Top N queries: ORDER BY ... DESC LIMIT N
   - Trend analysis: GROUP BY strftime('%Y-%m', created_at)
   - Customer segmentation: JOIN users with orders/order_items
   - Product analytics: JOIN products with order_items

User Question: "{user_query}"

Generate a single, executable SQL query. No markdown formatting, no explanations in the query itself.

SQL Query:"""
    
    # Get structured response from LLM
    structured_llm = llm.with_structured_output(SQLGenerationResponse)
    response = structured_llm.invoke(prompt)
    
    # Clean the SQL query (remove any markdown formatting)
    sql_query = response.sql_query.strip()
    sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
    
    # Update state
    state["sql_query_generated"] = sql_query
    state["curr_iteration"] = iteration + 1
    
    return state
