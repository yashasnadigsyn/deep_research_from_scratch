
"""User Clarification and Research Brief Generation.

This module implements the scoping phase of the research workflow, where we:
1. Assess if the user's request needs clarification
2. Generate a detailed research brief from the conversation

The workflow uses structured output to make deterministic decisions about
whether sufficient context exists to proceed with research.
"""

import logging
from datetime import datetime
from typing_extensions import Literal

from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, AIMessage, get_buffer_string
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command

from deep_research_from_scratch.prompts import clarify_with_user_instructions, transform_messages_into_research_topic_prompt
from deep_research_from_scratch.state_scope import AgentState, ClarifyWithUser, ResearchQuestion, AgentInputState

# Set up logger for this module
logger = logging.getLogger("deep_research.scope")

# ===== UTILITY FUNCTIONS =====

def get_today_str() -> str:
    """Get current date in a human-readable format."""
    return datetime.now().strftime("%a %b %-d, %Y")

# ===== CONFIGURATION =====

# Initialize model
model = init_chat_model(model="ollama:qwen3:0.6b-q8_0", temperature=0.0)

# ===== WORKFLOW NODES =====

def clarify_with_user(state: AgentState) -> Command[Literal["write_research_brief", "__end__"]]:
    """
    Determine if the user's request contains sufficient information to proceed with research.

    Uses structured output to make deterministic decisions and avoid hallucination.
    Routes to either research brief generation or ends with a clarification question.
    """
    logger.info("Starting user clarification process")
    logger.debug(f"Analyzing {len(state.get('messages', []))} messages for clarification needs")

    try:
        # Set up structured output model
        structured_output_model = model.with_structured_output(ClarifyWithUser)

        # Invoke the model with clarification instructions
        response = structured_output_model.invoke([
            HumanMessage(content=clarify_with_user_instructions.format(
                messages=get_buffer_string(messages=state["messages"]), 
                date=get_today_str()
            ))
        ])

        # Route based on clarification need
        if response.need_clarification:
            logger.info("User clarification needed - ending with question")
            logger.debug(f"Clarification question: {response.question[:100]}...")
            return Command(
                goto=END, 
                update={"messages": [AIMessage(content=response.question)]}
            )
        else:
            logger.info("Sufficient information provided - proceeding to research brief generation")
            logger.debug(f"Verification message: {response.verification[:100]}...")
            return Command(
                goto="write_research_brief", 
                update={"messages": [AIMessage(content=response.verification)]}
            )
            
    except Exception as e:
        logger.error(f"Error in clarify_with_user: {str(e)}", exc_info=True)
        # Fallback to asking for clarification
        fallback_question = "I need more information to help you with your research. Could you please provide more details about what you're looking for?"
        logger.info("Using fallback clarification question due to error")
        return Command(
            goto=END, 
            update={"messages": [AIMessage(content=fallback_question)]}
        )

def write_research_brief(state: AgentState):
    """
    Transform the conversation history into a comprehensive research brief.

    Uses structured output to ensure the brief follows the required format
    and contains all necessary details for effective research.
    """
    logger.info("Starting research brief generation")
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

        # Update state with generated research brief and pass it to the supervisor
        return {
            "research_brief": research_brief,
            "supervisor_messages": [HumanMessage(content=f"{research_brief}.")]
        }
        
    except Exception as e:
        logger.error(f"Error in write_research_brief: {str(e)}", exc_info=True)
        # Fallback brief
        fallback_brief = "Research brief generation failed. Please try again with more specific information."
        logger.info("Using fallback research brief due to error")
        return {
            "research_brief": fallback_brief,
            "supervisor_messages": [HumanMessage(content=f"{fallback_brief}.")]
        }

# ===== GRAPH CONSTRUCTION =====

# Build the scoping workflow
deep_researcher_builder = StateGraph(AgentState, input_schema=AgentInputState)

# Add workflow nodes
deep_researcher_builder.add_node("clarify_with_user", clarify_with_user)
deep_researcher_builder.add_node("write_research_brief", write_research_brief)

# Add workflow edges
deep_researcher_builder.add_edge(START, "clarify_with_user")
deep_researcher_builder.add_edge("write_research_brief", END)

# Compile the workflow
scope_research = deep_researcher_builder.compile()
