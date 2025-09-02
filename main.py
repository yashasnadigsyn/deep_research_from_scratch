#!/usr/bin/env python3
"""
Deep Research Agent - Main Entry Point

This script provides a command-line interface to run the deep research agent.
The agent can perform comprehensive research on any topic using web search
and multi-agent coordination.

Usage:
    python main.py "What are the best coffee shops in San Francisco?"
    python main.py "Compare OpenAI vs Anthropic AI approaches"
"""

import asyncio
import sys
import logging
import os
from datetime import datetime
from typing import Optional
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from langchain_core.messages import HumanMessage

from deep_research_from_scratch.research_agent_full import agent

# Initialize rich console for beautiful output
console = Console()

# Configure logging
def setup_logging():
    """Set up logging configuration for the application."""
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Generate timestamp for log file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"logs/deep_research_{timestamp}.log"
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set specific loggers
    logging.getLogger("deep_research").setLevel(logging.INFO)
    logging.getLogger("ddgs").setLevel(logging.WARNING)  # Reduce DDGS noise
    logging.getLogger("httpx").setLevel(logging.WARNING)  # Reduce HTTP noise
    
    return logging.getLogger("deep_research")

# Initialize logger
logger = setup_logging()

def print_banner():
    """Print the application banner."""
    banner = """
# Deep Research Agent

A comprehensive research system that uses multi-agent coordination
to perform deep research on any topic using web search and AI analysis.

Features:
- User clarification and scoping
- Multi-agent research coordination  
- Web search with DDGS (Dux Distributed Global Search)
- Comprehensive report generation
- Ollama integration for local AI processing
"""
    console.print(Panel(banner, title="🤖 Deep Research Agent", border_style="blue"))

async def run_research(query: str) -> str:
    """
    Run the deep research agent on a given query.
    
    Args:
        query: The research question or topic
        
    Returns:
        The final research report
    """
    logger.info(f"Starting research session for query: {query}")
    start_time = datetime.now()
    
    try:
        console.print(f"\n🔍 Starting research on: [bold cyan]{query}[/bold cyan]")
        console.print("⏳ This may take a few minutes...\n")
        
        logger.info("Invoking full research agent")
        # Run the full research agent
        result = await agent.ainvoke(
            {"messages": [HumanMessage(content=query)]},
            config={"configurable": {"thread_id": "main", "recursion_limit": 50}}
        )
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        logger.info(f"Research completed successfully in {duration:.2f} seconds")
        
        final_report = result.get("final_report", "No report generated")
        logger.info(f"Generated report length: {len(final_report)} characters")
        
        return final_report
        
    except Exception as e:
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        logger.error(f"Research failed after {duration:.2f} seconds: {str(e)}", exc_info=True)
        console.print(f"[red]Error during research: {str(e)}[/red]")
        return f"Error: {str(e)}"

def display_report(report: str):
    """Display the research report in a formatted way."""
    if report.startswith("Error:"):
        console.print(f"[red]{report}[/red]")
        return
        
    console.print("\n" + "="*80)
    console.print(Panel("📊 Research Report", style="bold green"))
    console.print("="*80)
    
    # Display the markdown report
    console.print(Markdown(report))
    
    console.print("\n" + "="*80)
    console.print("[green]✅ Research completed successfully![/green]")

async def interactive_mode():
    """Run the agent in interactive mode."""
    logger.info("Starting interactive mode")
    print_banner()
    
    session_count = 0
    
    while True:
        try:
            # Get user input
            query = Prompt.ask("\n[bold blue]Enter your research question[/bold blue] (or 'quit' to exit)")
            
            if query.lower() in ['quit', 'exit', 'q']:
                logger.info(f"Interactive session ended. Total queries processed: {session_count}")
                console.print("[yellow]Goodbye! 👋[/yellow]")
                break
                
            if not query.strip():
                console.print("[yellow]Please enter a valid research question.[/yellow]")
                continue
            
            session_count += 1
            logger.info(f"Processing query #{session_count} in interactive mode")
            
            # Run research
            report = await run_research(query)
            display_report(report)
            
        except KeyboardInterrupt:
            logger.info(f"Interactive session interrupted. Total queries processed: {session_count}")
            console.print("\n[yellow]Goodbye! 👋[/yellow]")
            break
        except Exception as e:
            logger.error(f"Unexpected error in interactive mode: {str(e)}", exc_info=True)
            console.print(f"[red]Unexpected error: {str(e)}[/red]")

async def main():
    """Main entry point."""
    logger.info("Deep Research Agent starting up")
    
    if len(sys.argv) > 1:
        # Command line mode - single query
        query = " ".join(sys.argv[1:])
        logger.info(f"Running in command line mode with query: {query}")
        print_banner()
        
        report = await run_research(query)
        display_report(report)
        
    else:
        # Interactive mode
        logger.info("Running in interactive mode")
        await interactive_mode()
    
    logger.info("Deep Research Agent shutting down")

if __name__ == "__main__":
    # Ensure we're in an async context
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]Goodbye! 👋[/yellow]")
    except Exception as e:
        console.print(f"[red]Fatal error: {str(e)}[/red]")
        sys.exit(1)
