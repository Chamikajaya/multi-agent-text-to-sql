"""
Error Corrector Agent

Automatically fixes SQL errors by analyzing error messages and regenerating queries.
Implements retry logic with a maximum attempt limit.
"""

from src.models.state import GraphState
from src.models.responses import ErrorCorrectionResponse
from src.database.schema import SCHEMA_DEFINITION
from src.config import MAX_SQL_RETRY_ATTEMPTS
from src.utils.llm import get_llm


def error_correction_agent(state: GraphState) -> GraphState:
    """
    Attempt to automatically fix SQL errors by analyzing the error message.
    
    This function:
    1. Analyzes the SQL error message and failed query
    2. Uses the schema definition to understand what went wrong
    3. Generates a corrected SQL query
    4. Implements retry logic with a maximum of MAX_SQL_RETRY_ATTEMPTS
    5. Returns an apology message if all retries fail
    
    Args:
        state: Current graph state containing error_message and failed SQL query
        
    Returns:
        Updated state with corrected query or final_answer if max retries exceeded
    """
    error_message = state["error_message"]
    failed_sql_query = state["sql_query_generated"]
    user_query = state["user_query"]
    iteration = state.get("curr_iteration", 0)
    llm = get_llm()
    
    # Check if maximum retry limit exceeded
    if iteration > MAX_SQL_RETRY_ATTEMPTS:
        state["final_answer"] = (
            f"I apologize, but I'm unable to generate a correct SQL query for your question after {MAX_SQL_RETRY_ATTEMPTS} attempts. "
            f"The error encountered was: {error_message}\n\n"
            "Please try rephrasing your question or contact support for assistance."
        )
        return state
    
    # Construct the error correction prompt
    prompt = f"""You are an expert SQL debugger. A SQL query has failed and you need to fix it.

{SCHEMA_DEFINITION}

ORIGINAL USER QUESTION: "{user_query}"

FAILED SQL QUERY:
{failed_sql_query}

ERROR MESSAGE:
{error_message}

COMMON SQL ERRORS AND FIXES:

1. COLUMN NOT FOUND:
   - Check spelling of column names against schema
   - Ensure table aliases match the columns being referenced
   - Use table.column notation for ambiguous columns

2. TABLE NOT FOUND:
   - Verify table name spelling matches schema exactly
   - Check for typos (e.g., 'order_item' vs 'order_items')

3. SYNTAX ERRORS:
   - Missing commas between column names
   - Unmatched parentheses in subqueries
   - Missing ON clause in JOIN statements
   - Incorrect GROUP BY usage (all non-aggregated columns must be in GROUP BY)

4. AGGREGATION ERRORS:
   - Ensure all non-aggregated columns appear in GROUP BY
   - Use HAVING for filtering aggregated results, WHERE for row-level filters
   - Don't mix aggregated and non-aggregated columns incorrectly

5. JOIN ERRORS:
   - Ensure foreign key relationships are correct
   - Use proper join types (INNER vs LEFT JOIN)
   - Include ON clause with valid join conditions

DEBUGGING STEPS:
1. Identify the exact error from the error message
2. Locate the problematic part of the query
3. Reference the schema to find correct column/table names
4. Fix the issue while preserving the original query intent
5. Ensure the corrected query still answers the user's question

Generate a corrected SQL query. No markdown formatting, no explanations in the query itself.

Corrected SQL Query:"""
    
    # Get structured response from LLM
    structured_llm = llm.with_structured_output(ErrorCorrectionResponse)
    response = structured_llm.invoke(prompt)
    
    # Clean the corrected SQL query
    corrected_query = response.corrected_sql_query.strip()
    corrected_query = corrected_query.replace("```sql", "").replace("```", "").strip()
    
    # Update state with corrected query
    state["sql_query_generated"] = corrected_query
    state["error_message"] = ""  # Clear error to trigger retry
    state["curr_iteration"] = iteration + 1  # Increment retry counter
    
    return state
