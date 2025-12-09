"""
Guardrails Agent

Validates user input to ensure questions are relevant to the e-commerce database.
Filters out greetings, off-topic questions, and inappropriate requests.
"""

from src.models.state import GraphState
from src.models.responses import GuardrailsResponse
from src.utils.llm import get_llm


def guardrails_agent(state: GraphState) -> GraphState:
    """
    Validate if user query is relevant to the e-commerce database.
    
    This agent acts as the first line of defense, ensuring that only
    relevant questions proceed through the workflow. It handles:
    - Greetings (returns friendly response)
    - Out-of-scope questions (rejects politely)
    - Relevant questions (allows to proceed)
    
    Args:
        state: Current graph state containing user_query
        
    Returns:
        Updated state with is_question_relavant flag and potentially final_answer
    """
    user_query = state["user_query"]
    llm = get_llm()
    
    # Construct the guardrails prompt
    prompt = f"""You are a guardrails agent for an e-commerce SQL query system. Analyze if the user's question can be answered using the available database.

DATABASE SCOPE:
The system has access to an e-commerce database containing:
- Products: catalog, pricing, categories, brands, departments
- Users: customer demographics, locations, registration info
- Orders: transactions, status tracking, delivery timestamps
- Order Items: line-level details, revenue data
- Inventory Items: stock levels, warehouse tracking
- Distribution Centers: warehouse locations
- Events: user behavior, web analytics, session tracking

CLASSIFICATION RULES:

1. GREETING - Casual conversational starters:
   - "Hi", "Hello", "Hey there"
   - "Good morning/afternoon/evening"
   - "How are you doing?"
   
2. IN-SCOPE - Questions answerable with database:
   - Sales analytics: "What was total revenue in 2022?"
   - Product queries: "Which brand has highest sales?"
   - Customer analysis: "How many users from Texas?"
   - Inventory questions: "Show products out of stock"
   - Trend analysis: "Monthly order trends"
   - Behavioral insights: "What pages do users visit most?"
   
3. OUT-OF-SCOPE - Cannot be answered with this database:
   - Personal information: "What's my order history?" (no authentication context)
   - Future predictions: "What will sell next month?" (no ML capability)
   - External data: "Compare our prices to competitors"
   - General knowledge: "How does e-commerce work?"
   - Unrelated topics: "Tell me a joke", "Weather forecast"
   - Real-time data: "Current inventory right now" (data is historical)

User Question: "{user_query}"

Guidelines:
- If greeting: set is_greeting=true, is_question_relavant=false
- If ambiguous but potentially answerable: mark is_question_relavant=true
- Be permissive - favor is_question_relavant=true when uncertain"""
    
    # Get structured response from LLM
    structured_llm = llm.with_structured_output(GuardrailsResponse)
    response = structured_llm.invoke(prompt)
    
    # Update state based on response
    state["is_question_relavant"] = response.is_question_relavant
    is_greeting = response.is_greeting
    
    # Handle greetings
    if is_greeting:
        state["final_answer"] = (
            "Hello! How can I assist you with e-commerce data today?"
        )
        return state
    
    # Handle out-of-scope questions
    if not state["is_question_relavant"]:
        state["final_answer"] = (
            "I'm sorry, but your question is outside the scope of the e-commerce database I have access to. "
            "Please ask something related to products, users, orders, inventory, or sales analytics."
        )
        return state
    
    return state
