"""
Pydantic Response Models

Defines structured output schemas for LLM responses from each agent.
These models ensure consistent and type-safe outputs from the language model.
"""

from pydantic import BaseModel, Field
from typing import List


class GuardrailsResponse(BaseModel):
    """
    Response model for the guardrails agent.
    
    Determines whether a user's question is relevant to the database
    and appropriate for processing.
    """
    
    is_question_relavant: bool = Field(
        description="Indicates if the user's query is relevant to the e-commerce database."
    )
    is_greeting: bool = Field(
        description="Indicates if the user's query is a greeting message."
    )
    reason: str = Field(
        description="Explanation for the classification decision."
    )


class SQLGenerationResponse(BaseModel):
    """
    Response model for the SQL generation agent.
    
    Contains the generated SQL query and a brief explanation.
    """
    
    sql_query: str = Field(
        description="The generated SQL query based on the user's question."
    )
    explanation: str = Field(
        description="Brief explanation of what the query does (max 30 words)."
    )


class ErrorCorrectionResponse(BaseModel):
    """
    Response model for the error correction agent.
    
    Contains the corrected SQL query and analysis of the error.
    """
    
    corrected_sql_query: str = Field(
        description="The fixed SQL query that should resolve the error."
    )
    error_analysis: str = Field(
        description="Brief explanation of what was wrong and how it was fixed (max 50 words)."
    )


class AnalysisResponse(BaseModel):
    """
    Response model for the analysis agent.
    
    Converts SQL results into natural language with key insights.
    """
    
    natural_language_answer: str = Field(
        description="Clear, concise natural language explanation of the query results."
    )
    key_insights: List[str] = Field(
        description="List of 2-3 key takeaways or insights from the data."
    )
    needs_visualization: bool = Field(
        description="Whether the data would benefit from a chart/graph visualization."
    )


class VisualizationDecisionResponse(BaseModel):
    """
    Response model for the visualization decision agent.
    
    Determines if and what type of visualization should be created.
    """
    
    needs_visualization: bool = Field(
        description="Whether the data would benefit from visualization."
    )
    visualization_type: str = Field(
        description="Type of chart: 'bar', 'line', 'pie', 'scatter', or 'none'."
    )
    reasoning: str = Field(
        description="Brief explanation for the decision (max 30 words)."
    )


class PlotlyCodeResponse(BaseModel):
    """
    Response model for the visualization agent.
    
    Contains Python code to generate a Plotly visualization.
    """
    
    plotly_code: str = Field(
        description="Python code to generate a Plotly visualization."
    )
    chart_title: str = Field(
        description="Title for the chart."
    )
