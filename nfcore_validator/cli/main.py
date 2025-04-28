"""
Command-line interface for nf-core validator
"""
import os
import sys
import argparse
from typing import List, Optional

from ..harvester.docs_harvester import NfCoreDocsHarvester
from ..scanner.pipeline_scanner import PipelineScanner
from ..utils.report_generator import ReportGenerator
from ..chat.chat_interface import NfCoreDocChat


def harvest_command(args: argparse.Namespace) -> None:
    """Handle the harvest command
    
    Args:
        args: Command line arguments
    """
    harvester = NfCoreDocsHarvester(openai_api_key=args.api_key)
    harvester.harvest(vectorstore_path=args.output)
    print(f"Documentation harvested and saved to {args.output}")


def validate_command(args: argparse.Namespace) -> None:
    """Handle the validate command
    
    Args:
        args: Command line arguments
    """
    scanner = PipelineScanner(
        pipeline_path=args.pipeline_path,
        vectorstore_path=args.vectorstore,
        openai_api_key=args.api_key
    )
    
    report_path = scanner.generate_report(output_path=args.output)
    
    if args.format == 'markdown':
        md_path = os.path.splitext(report_path)[0] + '.md'
        report_gen = ReportGenerator()
        report_gen.json_to_markdown(report_path, md_path)
        print(f"Markdown report saved to {md_path}")


def chat_command(args: argparse.Namespace) -> None:
    """Handle the chat command
    
    Args:
        args: Command line arguments
    """
    chat = NfCoreDocChat(
        vectorstore_path=args.vectorstore,
        openai_api_key=args.api_key
    )
    
    print("\nNf-core Documentation Chat")
    print("Type 'exit' or 'quit' to end the session")
    print("Type 'clear' to clear chat history\n")
    
    while True:
        try:
            question = input("\nYour question: ")
            
            if question.lower() in ['exit', 'quit']:
                print("Goodbye!")
                break
                
            if question.lower() == 'clear':
                chat.clear_history()
                print("Chat history cleared")
                continue
                
            if not question.strip():
                continue
                
            response = chat.ask(question, k=args.context_size)
            
            print("\nAnswer:")
            print(response["answer"])
            
            if args.show_sources:
                # Group sources by category
                sources_by_category = {}
                for source in response["sources"]:
                    category = source.get("category", "Other")
                    if category not in sources_by_category:
                        sources_by_category[category] = []
                    sources_by_category[category].append(source)
                
                print("\nSources by Category:")
                for category, sources in sources_by_category.items():
                    print(f"\n{category}:")
                    print("=" * len(category))
                    
                    for i, source in enumerate(sources):
                        print(f"\n  Source {i+1}:")
                        print(f"  URL: {source.get('url', 'Unknown')}")
                        print("  " + "-" * 38)
                        content = source["content"]
                        # Show a reasonable snippet of content
                        if len(content) > 300:
                            content = content[:300] + "..."
                        
                        # Format content with indentation
                        formatted_content = "\n".join(f"  {line}" for line in content.split("\n"))
                        print(formatted_content)
                    
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {str(e)}")


def main(argv: Optional[List[str]] = None) -> int:
    """Main entry point
    
    Args:
        argv: Command line arguments
        
    Returns:
        Exit code
    """
    parser = argparse.ArgumentParser(
        description="nf-core pipeline validator",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # Global options
    parser.add_argument(
        "--api-key", 
        help="OpenAI API key (defaults to OPENAI_API_KEY environment variable)"
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Harvest command
    harvest_parser = subparsers.add_parser(
        "harvest", 
        help="Harvest nf-core documentation"
    )
    harvest_parser.add_argument(
        "--output", 
        default="nfcore_vectorstore",
        help="Output path for vector store"
    )
    
    # Validate command
    validate_parser = subparsers.add_parser(
        "validate", 
        help="Validate a pipeline"
    )
    validate_parser.add_argument(
        "pipeline_path",
        help="Path to the pipeline to validate"
    )
    validate_parser.add_argument(
        "--vectorstore",
        default="nfcore_vectorstore",
        help="Path to the vector store"
    )
    validate_parser.add_argument(
        "--output",
        help="Output path for report (defaults to <pipeline_name>_compliance_report.json)"
    )
    validate_parser.add_argument(
        "--format",
        choices=["json", "markdown"],
        default="json",
        help="Report format"
    )
    
    # Chat command
    chat_parser = subparsers.add_parser(
        "chat", 
        help="Chat with nf-core documentation"
    )
    chat_parser.add_argument(
        "--vectorstore",
        default="nfcore_vectorstore",
        help="Path to the vector store"
    )
    chat_parser.add_argument(
        "--context-size",
        type=int,
        default=10,
        help="Number of context documents to consider"
    )
    chat_parser.add_argument(
        "--show-sources",
        action="store_true",
        help="Show sources for the answer"
    )
    
    args = parser.parse_args(argv)
    
    # Check for required command
    if not args.command:
        parser.print_help()
        return 1
    
    # Check for OpenAI API key
    if not args.api_key and not os.environ.get("OPENAI_API_KEY"):
        print("Error: OpenAI API key is required. Set OPENAI_API_KEY environment variable or use --api-key.")
        return 1
    
    # Handle commands
    try:
        if args.command == "harvest":
            harvest_command(args)
        elif args.command == "validate":
            validate_command(args)
        elif args.command == "chat":
            chat_command(args)
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
        
    return 0


if __name__ == "__main__":
    sys.exit(main())
