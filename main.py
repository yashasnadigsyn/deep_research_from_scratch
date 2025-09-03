#!/usr/bin/env python3
"""
Deep Research Agent - Main Entry Point

This script provides a command-line interface to run the deep research agent.
The agent can perform comprehensive research on any topic using web search
and multi-agent coordination.

Usage:
    # Interactive mode
    python main.py
    
    # Command line mode with query
    python main.py "What are the best coffee shops in San Francisco?"
    python main.py "Compare OpenAI vs Anthropic AI approaches"
    
    # With requirements file
    python main.py --requirements requirements.txt
    python main.py --requirements requirements.pdf "Analyze these requirements"
    python main.py -r requirements.txt "What are the key technical challenges?"
"""

import asyncio
import sys
import logging
import os
import argparse
from datetime import datetime

from langchain_core.messages import HumanMessage

from deep_research_from_scratch.research_agent_full import agent

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
    print(banner)

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
        print(f"\nStarting research on: {query}")
        print("This may take a few minutes...\n")
        
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
        print(f"Error during research: {str(e)}")
        return f"Error: {str(e)}"

def display_report(report: str):
    """Display the research report in a formatted way."""
    if report.startswith("Error:"):
        print(f"Error: {report}")
        return
        
    print("\n" + "="*80)
    print("Research Report")
    print("="*80)
    
    # Display the report (plain text)
    print(report)
    
    print("\n" + "="*80)
    print("Research completed successfully!")

async def interactive_mode():
    """Run the agent in interactive mode."""
    logger.info("Starting interactive mode")
    print_banner()
    
    session_count = 0
    
    while True:
        try:
            # Get user input
            query = input("\nEnter your research question (or 'quit' to exit): ")
            
            if query.lower() in ['quit', 'exit', 'q']:
                logger.info(f"Interactive session ended. Total queries processed: {session_count}")
                print("Goodbye!")
                break
                
            if not query.strip():
                print("Please enter a valid research question.")
                continue
            
            session_count += 1
            logger.info(f"Processing query #{session_count} in interactive mode")
            
            # Run research
            report = await run_research(query)
            display_report(report)
            
        except KeyboardInterrupt:
            logger.info(f"Interactive session interrupted. Total queries processed: {session_count}")
            print("\nGoodbye!")
            break
        except Exception as e:
            logger.error(f"Unexpected error in interactive mode: {str(e)}", exc_info=True)
            print(f"Unexpected error: {str(e)}")

def read_requirements_file(file_path: str) -> str:
    """Read requirements from a text or PDF file."""
    import os
    from pathlib import Path
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Requirements file not found: {file_path}")
    
    file_ext = Path(file_path).suffix.lower()
    
    if file_ext == '.txt':
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    elif file_ext == '.pdf':
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(file_path)
            text = ""
            for page_num in range(doc.page_count):                                                                                                                                                                                                                                                                                                                                                                                                                              
                page = doc[page_num]
                text += page.get_text() + "\n"
            doc.close()
            return text
        except ImportError:
            raise ImportError("PyMuPDF is required to read PDF files. Install it with: pip install PyMuPDF")
    else:
        raise ValueError(f"Unsupported file format: {file_ext}. Supported formats: .txt, .pdf")

async def main():
    """Main entry point."""
    logger.info("Deep Research Agent starting up")
    
    parser = argparse.ArgumentParser(description="Deep Research Agent - Comprehensive research system")
    parser.add_argument("query", nargs="*", help="Research question or topic")
    parser.add_argument("--requirements", "-r", help="Path to requirements file (.txt or .pdf)")
    parser.add_argument("--interactive", "-i", action="store_true", help="Run in interactive mode")
    
    args = parser.parse_args()
    
    if args.requirements:                                                                                                                                                                                                       
        # Read requirements from file
        logger.info(f"Reading requirements from file: {args.requirements}")
        try:
            requirements_content = read_requirements_file(args.requirements)
            logger.info(f"Successfully read {len(requirements_content)} characters from requirements file")
            
            # Combine requirements with query if provided
            if args.query:
                query = f"Requirements from {args.requirements}:\n\n{requirements_content}\n\nResearch question: {' '.join(args.query)}"
            else:
                query = f"Please research and analyze the following requirements:\n\n{requirements_content}"
            
            print_banner()
            report = await run_research(query)
            display_report(report)
            
        except Exception as e:
            logger.error(f"Error reading requirements file: {str(e)}", exc_info=True)
            print(f"Error reading requirements file: {str(e)}")
            sys.exit(1)
            
    elif args.query:
        # Command line mode - single query
        query = " ".join(args.query)
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
        print("\nGoodbye!")
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        sys.exit(1)
