
"""
Full Multi-Agent Domain Knowledge Research System

This module integrates all components of the domain knowledge research system:
- Automatic analysis and research brief generation  
- Multi-agent domain knowledge research coordination
- Final domain knowledge base generation

The system orchestrates the complete domain knowledge research workflow from initial user
input through final domain knowledge base delivery for UI design decision-making.
"""

import logging
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END

from deep_research_from_scratch.utils import get_today_str, get_ollama_model
from deep_research_from_scratch.prompts import final_report_generation_prompt
from deep_research_from_scratch.state_scope import AgentState, AgentInputState
from deep_research_from_scratch.research_agent_scope import write_research_brief
from deep_research_from_scratch.multi_agent_supervisor import supervisor_agent

# Set up logger for this module
logger = logging.getLogger("deep_research.full_agent")

# ===== Config =====

writer_model = get_ollama_model(max_tokens=32000)

# ===== FINAL REPORT GENERATION =====

async def final_report_generation(state: AgentState):
    """
    Final report generation node.

    Synthesizes all research findings into a comprehensive final report
    """
    logger.info("Starting final report generation")
    
    notes = state.get("notes", [])
    research_brief = state.get("research_brief", "")
    
    logger.debug(f"Processing {len(notes)} research notes for final report")
    logger.debug(f"Research brief length: {len(research_brief)} characters")

    try:
        findings = "\n".join(notes)
        logger.debug(f"Combined findings length: {len(findings)} characters")

        final_report_prompt = final_report_generation_prompt.format(
            research_brief=research_brief,
            findings=findings,
            date=get_today_str()
        )

        logger.debug("Invoking writer model for final report generation")
        final_report = await writer_model.ainvoke([HumanMessage(content=final_report_prompt)])

        final_report_content = final_report.content
        logger.info("Final report generated successfully")
        logger.info(f"Final report length: {len(final_report_content)} characters")

        return {
            "final_report": final_report_content, 
            "messages": ["Here is the final report: " + final_report_content],
        }
        
    except Exception as e:
        logger.error(f"Error in final report generation: {str(e)}", exc_info=True)
        error_report = f"Error generating final report: {str(e)}"
        return {
            "final_report": error_report, 
            "messages": [error_report],
        }

# ===== GRAPH CONSTRUCTION =====
# Build the overall workflow
deep_researcher_builder = StateGraph(AgentState, input_schema=AgentInputState)

# Add workflow nodes
deep_researcher_builder.add_node("write_research_brief", write_research_brief)
deep_researcher_builder.add_node("supervisor_subgraph", supervisor_agent)
deep_researcher_builder.add_node("final_report_generation", final_report_generation)

# Add workflow edges
deep_researcher_builder.add_edge(START, "write_research_brief")
deep_researcher_builder.add_edge("write_research_brief", "supervisor_subgraph")
deep_researcher_builder.add_edge("supervisor_subgraph", "final_report_generation")
deep_researcher_builder.add_edge("final_report_generation", END)

# Compile the full workflow
agent = deep_researcher_builder.compile()
