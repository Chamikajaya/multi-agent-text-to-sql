"""
SQL Executor Agent

Executes SQL queries against the database and formats results.
Handles multiple queries and provides detailed error messages.
"""

import sqlite3
import pandas as pd

from src.models.state import GraphState
from src.database.db_manager import get_connection


def execute_sql(state: GraphState) -> GraphState:
    """
    Execute the generated SQL query and handle multiple queries if present.
    
    This function:
    1. Splits the SQL query into individual statements (separated by semicolons)
    2. Executes each statement sequentially
    3. Formats results as DataFrames for readability
    4. Handles errors gracefully
    5. Stores results in state for downstream processing
    
    Args:
        state: Current graph state containing sql_query_generated
        
    Returns:
        Updated state with result_for_sql_query or error_message
    """
    sql_query = state["sql_query_generated"]
    
    try:
        # Establish database connection
        conn = get_connection()
        cursor = conn.cursor()
        
        # Split multiple SQL statements (separated by semicolons)
        # Filter out empty statements and strip whitespace
        queries = [q.strip() for q in sql_query.split(";") if q.strip()]
        
        all_results = []
        
        # Execute each statement separately
        for idx, query in enumerate(queries):
            cursor.execute(query)
            
            # Fetch results for this statement
            results = cursor.fetchall()
            
            if results:
                # Get column names from cursor description
                column_names = [description[0] for description in cursor.description]
                
                # Convert to DataFrame for better readability
                df = pd.DataFrame(results, columns=column_names)
                
                # Format result with query number if multiple queries exist
                if len(queries) > 1:
                    result_text = f"Query {idx + 1}:\n{query}\n\nResult:\n{df.to_string(index=False)}"
                else:
                    result_text = df.to_string(index=False)
                
                all_results.append(result_text)
            else:
                # Handle queries that return no rows (e.g., CREATE, INSERT, UPDATE)
                if len(queries) > 1:
                    all_results.append(
                        f"Query {idx + 1}:\n{query}\n\nResult: No rows returned"
                    )
                else:
                    all_results.append("No results found.")
        
        # Close the database connection
        conn.close()
        
        # Store formatted results in state
        if all_results:
            state["result_for_sql_query"] = "\n\n" + "=" * 80 + "\n\n".join(all_results)
        else:
            state["result_for_sql_query"] = (
                "Query executed successfully but returned no results."
            )
        
        # Clear any previous error
        state["error_message"] = ""
        
    except sqlite3.Error as e:
        # Handle SQLite-specific errors
        state["error_message"] = f"SQL Execution Error: {str(e)}"
        state["result_for_sql_query"] = ""
        
    except Exception as e:
        # Handle unexpected errors
        state["error_message"] = f"Unexpected Error: {str(e)}"
        state["result_for_sql_query"] = ""
        
    finally:
        # Ensure connection is closed even if an error occurs
        if 'conn' in locals():
            conn.close()
    
    return state
