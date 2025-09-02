
"""Research Utilities and Tools.

This module provides search and content processing utilities for the research agent,
including web search capabilities and content summarization tools.
"""

import logging
from pathlib import Path
from datetime import datetime
from typing_extensions import Annotated, List, Literal

from langchain.chat_models import init_chat_model 
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool, InjectedToolArg
from ddgs import DDGS

from deep_research_from_scratch.state_research import Summary
from deep_research_from_scratch.prompts import summarize_webpage_prompt

# Set up logger for this module
logger = logging.getLogger("deep_research.utils")

# ===== UTILITY FUNCTIONS =====

def get_today_str() -> str:
    """Get current date in a human-readable format."""
    return datetime.now().strftime("%a %b %-d, %Y")

def get_current_dir() -> Path:
    """Get the current directory of the module.

    This function is compatible with Jupyter notebooks and regular Python scripts.

    Returns:
        Path object representing the current directory
    """
    try:
        return Path(__file__).resolve().parent
    except NameError:  # __file__ is not defined
        return Path.cwd()

# ===== CONFIGURATION =====

summarization_model = init_chat_model(model="ollama:granite3.3:2b")
ddgs_client = DDGS()

# ===== SEARCH FUNCTIONS =====

def ddgs_search_multiple(
    search_queries: List[str], 
    max_results: int = 3, 
    region: str = "us-en",
    safesearch: str = "moderate",
) -> List[dict]:
    """Perform search using DDGS API for multiple queries.

    Args:
        search_queries: List of search queries to execute
        max_results: Maximum number of results per query
        region: Region for search results (e.g., "us-en", "uk-en")
        safesearch: Safe search setting ("on", "moderate", "off")

    Returns:
        List of search result dictionaries
    """
    logger.info(f"Starting DDGS search for {len(search_queries)} queries: {search_queries}")
    
    # Execute searches sequentially
    search_docs = []
    for i, query in enumerate(search_queries):
        try:
            logger.debug(f"Searching query {i+1}/{len(search_queries)}: {query}")
            
            # Use DDGS text search
            results = list(ddgs_client.text(
                query,
                max_results=max_results,
                region=region,
                safesearch=safesearch
            ))
            
            logger.debug(f"Found {len(results)} results for query: {query}")
            
            # Convert DDGS results to expected format
            formatted_results = {
                'results': []
            }
            
            for result in results:
                formatted_results['results'].append({
                    'title': result.get('title', ''),
                    'url': result.get('href', ''),
                    'content': result.get('body', ''),
                    'raw_content': result.get('body', '')  # DDGS doesn't provide separate raw content
                })
            
            search_docs.append(formatted_results)
            logger.debug(f"Formatted {len(formatted_results['results'])} results for query: {query}")
            
        except Exception as e:
            logger.error(f"Error searching for '{query}': {str(e)}", exc_info=True)
            # Return empty results on error
            search_docs.append({'results': []})

    total_results = sum(len(doc['results']) for doc in search_docs)
    logger.info(f"DDGS search completed. Total results across all queries: {total_results}")
    return search_docs

def summarize_webpage_content(webpage_content: str) -> str:
    """Summarize webpage content using the configured summarization model.

    Args:
        webpage_content: Raw webpage content to summarize

    Returns:
        Formatted summary with key excerpts
    """
    logger.debug(f"Summarizing webpage content of length: {len(webpage_content)} characters")
    
    try:
        # Set up structured output model for summarization
        structured_model = summarization_model.with_structured_output(Summary)

        # Generate summary
        summary = structured_model.invoke([
            HumanMessage(content=summarize_webpage_prompt.format(
                webpage_content=webpage_content, 
                date=get_today_str()
            ))
        ])

        # Format summary with clear structure
        formatted_summary = (
            f"<summary>\n{summary.summary}\n</summary>\n\n"
            f"<key_excerpts>\n{summary.key_excerpts}\n</key_excerpts>"
        )

        logger.debug(f"Successfully summarized content. Summary length: {len(formatted_summary)} characters")
        return formatted_summary

    except Exception as e:
        logger.error(f"Failed to summarize webpage: {str(e)}", exc_info=True)
        fallback_content = webpage_content[:1000] + "..." if len(webpage_content) > 1000 else webpage_content
        logger.debug(f"Using fallback content of length: {len(fallback_content)} characters")
        return fallback_content

def deduplicate_search_results(search_results: List[dict]) -> dict:
    """Deduplicate search results by URL to avoid processing duplicate content.

    Args:
        search_results: List of search result dictionaries

    Returns:
        Dictionary mapping URLs to unique results
    """
    unique_results = {}

    for response in search_results:
        for result in response['results']:
            url = result['url']
            if url not in unique_results:
                unique_results[url] = result

    return unique_results

def process_search_results(unique_results: dict) -> dict:
    """Process search results by summarizing content where available.

    Args:
        unique_results: Dictionary of unique search results

    Returns:
        Dictionary of processed results with summaries
    """
    summarized_results = {}

    for url, result in unique_results.items():
        # Use existing content if no raw content for summarization
        if not result.get("raw_content"):
            content = result['content']
        else:
            # Summarize raw content for better processing
            content = summarize_webpage_content(result['raw_content'])

        summarized_results[url] = {
            'title': result['title'],
            'content': content
        }

    return summarized_results

def format_search_output(summarized_results: dict) -> str:
    """Format search results into a well-structured string output.

    Args:
        summarized_results: Dictionary of processed search results

    Returns:
        Formatted string of search results with clear source separation
    """
    if not summarized_results:
        return "No valid search results found. Please try different search queries or use a different search API."

    formatted_output = "Search results: \n\n"

    for i, (url, result) in enumerate(summarized_results.items(), 1):
        formatted_output += f"\n\n--- SOURCE {i}: {result['title']} ---\n"
        formatted_output += f"URL: {url}\n\n"
        formatted_output += f"SUMMARY:\n{result['content']}\n\n"
        formatted_output += "-" * 80 + "\n"

    return formatted_output

# ===== RESEARCH TOOLS =====

@tool(parse_docstring=True)
def ddgs_search(
    query: str,
    max_results: Annotated[int, InjectedToolArg] = 3,
    region: Annotated[str, InjectedToolArg] = "us-en",
    safesearch: Annotated[str, InjectedToolArg] = "moderate",
) -> str:
    """Fetch results from DDGS search API with content summarization.

    Args:
        query: A single search query to execute
        max_results: Maximum number of results to return
        region: Region for search results (e.g., "us-en", "uk-en")
        safesearch: Safe search setting ("on", "moderate", "off")

    Returns:
        Formatted string of search results with summaries
    """
    logger.info(f"DDGS search tool called with query: '{query}', max_results: {max_results}")
    
    # Execute search for single query
    search_results = ddgs_search_multiple(
        [query],  # Convert single query to list for the internal function
        max_results=max_results,
        region=region,
        safesearch=safesearch,
    )

    # Deduplicate results by URL to avoid processing duplicate content
    unique_results = deduplicate_search_results(search_results)
    logger.debug(f"After deduplication: {len(unique_results)} unique results")

    # Process results with summarization
    summarized_results = process_search_results(unique_results)
    logger.debug(f"After summarization: {len(summarized_results)} processed results")

    # Format output for consumption
    formatted_output = format_search_output(summarized_results)
    logger.info(f"DDGS search tool completed. Output length: {len(formatted_output)} characters")
    return formatted_output

@tool(parse_docstring=True)
def think_tool(reflection: str) -> str:
    """Tool for strategic reflection on research progress and decision-making.

    Use this tool after each search to analyze results and plan next steps systematically.
    This creates a deliberate pause in the research workflow for quality decision-making.

    When to use:
    - After receiving search results: What key information did I find?
    - Before deciding next steps: Do I have enough to answer comprehensively?
    - When assessing research gaps: What specific information am I still missing?
    - Before concluding research: Can I provide a complete answer now?

    Reflection should address:
    1. Analysis of current findings - What concrete information have I gathered?
    2. Gap assessment - What crucial information is still missing?
    3. Quality evaluation - Do I have sufficient evidence/examples for a good answer?
    4. Strategic decision - Should I continue searching or provide my answer?

    Args:
        reflection: Your detailed reflection on research progress, findings, gaps, and next steps

    Returns:
        Confirmation that reflection was recorded for decision-making
    """
    logger.debug(f"Think tool called with reflection of length: {len(reflection)} characters")
    logger.debug(f"Reflection content: {reflection[:200]}...")  # Log first 200 chars
    return f"Reflection recorded: {reflection}"
