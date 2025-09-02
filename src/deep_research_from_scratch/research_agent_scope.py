
"""Automatic Research Brief Generation.

This module implements the scoping phase of the research workflow, where we:
1. Automatically analyze the user's request without clarification
2. Generate a detailed domain knowledge research brief from the conversation

The workflow uses structured output to automatically infer domain context
and create comprehensive research briefs for domain knowledge aggregation.
"""

import logging
from datetime import datetime

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, AIMessage, get_buffer_string
from langgraph.graph import StateGraph, START, END

from deep_research_from_scratch.prompts import transform_messages_into_research_topic_prompt
from deep_research_from_scratch.state_scope import AgentState, ResearchQuestion, AgentInputState

# Set up logger for this module
logger = logging.getLogger("deep_research.scope")

# ===== UTILITY FUNCTIONS =====

def get_today_str() -> str:
    """Get current date in a human-readable format."""
    return datetime.now().strftime("%a %b %-d, %Y")

# ===== CONFIGURATION =====

# Initialize model
model = init_chat_model(model="ollama:granite3.3:2b", temperature=0.0)

# ===== WORKFLOW NODES =====



def write_research_brief(state: AgentState):
    """
    Automatically analyze the user's request and transform it into a comprehensive domain knowledge research brief.

    Uses structured output to ensure the brief follows the required format
    and contains all necessary details for effective domain knowledge research.
    """
    logger.info("Starting automatic research brief generation")
    logger.debug(f"Processing {len(state.get('messages', []))} messages for brief generation")

    try:
        # Set up structured output model
        structured_output_model = model.with_structured_output(ResearchQuestion)

        # Generate research brief from conversation history
        response = structured_output_model.invoke([
            HumanMessage(content=transform_messages_into_research_topic_prompt.format(
                messages=get_buffer_string(state.get("messages", [])),
                date=get_today_str()
            ))
        ])

        research_brief = response.research_brief
        logger.info("Research brief generated successfully")
        logger.debug(f"Research brief length: {len(research_brief)} characters")
        logger.debug(f"Research brief preview: {research_brief[:200]}...")

        # Create confirmation message for the user
        confirmation_message = "I've analyzed your request and will now begin comprehensive domain knowledge research to build a knowledge base for your UI design project."

        # Update state with generated research brief and pass it to the supervisor
        return {
            "research_brief": research_brief,
            "supervisor_messages": [HumanMessage(content=f"{research_brief}.")],
            "messages": [AIMessage(content=confirmation_message)]
        }
        
    except Exception as e:
        logger.error(f"Error in write_research_brief: {str(e)}", exc_info=True)
        # Fallback brief
        fallback_brief = "I'll begin domain knowledge research based on your request. Let me gather comprehensive information about the domain you've specified."
        logger.info("Using fallback research brief due to error")
        return {
            "research_brief": fallback_brief,
            "supervisor_messages": [HumanMessage(content=f"{fallback_brief}.")],
            "messages": [AIMessage(content="I'll begin domain knowledge research based on your request.")]
        }

# ===== GRAPH CONSTRUCTION =====

# Build the scoping workflow
deep_researcher_builder = StateGraph(AgentState, input_schema=AgentInputState)

# Add workflow nodes
deep_researcher_builder.add_node("write_research_brief", write_research_brief)

# Add workflow edges
deep_researcher_builder.add_edge(START, "write_research_brief")
deep_researcher_builder.add_edge("write_research_brief", END)

# Compile the workflow
scope_research = deep_researcher_builder.compile()
