
"""Automatic Research Brief Generation.

This module implements the scoping phase of the research workflow, where we:
1. Automatically analyze the user's request without clarification
2. Generate a detailed domain knowledge research brief from the conversation

The workflow uses structured output to automatically infer domain context
and create comprehensive research briefs for domain knowledge aggregation.
"""

import logging


from langchain_core.messages import HumanMessage, AIMessage, get_buffer_string
from langgraph.graph import StateGraph, START, END

from deep_research_from_scratch.prompts import transform_messages_into_research_topic_prompt
from deep_research_from_scratch.state_scope import AgentState, ResearchQuestion, AgentInputState
from deep_research_from_scratch.utils import get_today_str, get_ollama_model

# Set up logger for this module
logger = logging.getLogger("deep_research.scope")

# ===== UTILITY FUNCTIONS =====

# ===== CONFIGURATION =====

# Initialize model
model = get_ollama_model(temperature=0.0)

# ===== WORKFLOW NODES =====



def write_research_brief(state: AgentState):
    """
    Automatically analyze the user's request and transform it into a comprehensive domain knowledge research brief.

    Uses structured output with fallback parsing to ensure the brief follows the required format
    and contains all necessary details for effective domain knowledge research.
    """
    logger.info("Starting automatic research brief generation")
    logger.debug(f"Processing {len(state.get('messages', []))} messages for brief generation")

    # Prepare the prompt
    prompt_content = transform_messages_into_research_topic_prompt.format(
        messages=get_buffer_string(state.get("messages", [])),
        date=get_today_str()
    )

    # Try structured output first
    try:
        logger.debug("Attempting structured output generation")
        structured_output_model = model.with_structured_output(ResearchQuestion)
        response = structured_output_model.invoke([HumanMessage(content=prompt_content)])
        research_brief = response.research_brief
        logger.info("Research brief generated successfully with structured output")
        
    except Exception as structured_error:
        logger.warning(f"Structured output failed: {str(structured_error)}")
        logger.info("Attempting fallback text generation with manual JSON parsing")
        
        try:
            # Try with a simpler prompt first
            messages_text = get_buffer_string(state.get("messages", []))
            simple_prompt = f"""Based on the following conversation, create a comprehensive UI/UX design research brief:

{messages_text}

Today's date is {get_today_str()}.

Please provide a detailed research brief that covers:
1. The specific industry/domain (e.g., gas turbines, power plants, etc.)
2. The type of UI/interface being designed (dashboards, control panels, etc.)
3. Key stakeholders and users
4. UI/UX design patterns to research
5. Specific design requirements and challenges

Return your response as a JSON object with this exact structure:
{{"research_brief": "Your comprehensive research brief here"}}

Do not include any additional text outside the JSON object."""

            response = model.invoke([HumanMessage(content=simple_prompt)])
            raw_content = response.content.strip()
            logger.debug(f"Raw model response: {raw_content[:500]}...")
            
            # Try to extract JSON from the response
            import json
            import re
            
            # Multiple approaches to extract JSON
            research_brief = ""
            
            # Approach 1: Look for complete JSON object
            json_match = re.search(r'\{[^{}]*"research_brief"[^{}]*\}', raw_content, re.DOTALL)
            if json_match:
                try:
                    json_str = json_match.group(0)
                    parsed_json = json.loads(json_str)
                    research_brief = parsed_json.get("research_brief", "")
                except:
                    pass
            
            # Approach 2: Look for JSON with code blocks
            if not research_brief:
                code_block_match = re.search(r'```(?:json)?\s*(\{.*?"research_brief".*?\})\s*```', raw_content, re.DOTALL)
                if code_block_match:
                    try:
                        json_str = code_block_match.group(1)
                        parsed_json = json.loads(json_str)
                        research_brief = parsed_json.get("research_brief", "")
                    except:
                        pass
            
            # Approach 3: Look for any JSON-like structure
            if not research_brief:
                json_like_match = re.search(r'\{[^{}]*"research_brief"[^{}]*\}', raw_content, re.DOTALL)
                if json_like_match:
                    try:
                        json_str = json_like_match.group(0)
                        # Clean up common JSON issues
                        json_str = json_str.replace('\n', ' ').replace('\r', ' ')
                        parsed_json = json.loads(json_str)
                        research_brief = parsed_json.get("research_brief", "")
                    except:
                        pass
            
            # Approach 4: If no JSON found, use the entire response as the brief
            if not research_brief:
                research_brief = raw_content
                
            logger.info("Research brief generated successfully with fallback parsing")
            
        except Exception as fallback_error:
            logger.error(f"Fallback parsing also failed: {str(fallback_error)}")
            # Final fallback
            research_brief = "I'll begin comprehensive UI/UX design research based on your request. Let me gather detailed information about the interface design patterns and user experience considerations for your specified domain."
            logger.info("Using final fallback research brief")

    logger.debug(f"Research brief length: {len(research_brief)} characters")
    logger.debug(f"Research brief preview: {research_brief[:200]}...")

    # Create confirmation message for the user
    confirmation_message = "I've analyzed your request and will now begin comprehensive UI/UX design research to build a knowledge base for your interface design project."

    # Update state with generated research brief and pass it to the supervisor
    return {
        "research_brief": research_brief,
        "supervisor_messages": [HumanMessage(content=f"{research_brief}.")],
        "messages": [AIMessage(content=confirmation_message)]
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
