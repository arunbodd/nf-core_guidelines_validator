"""
Command-line interface for nf-core validator
"""
import os
import sys
import argparse
from typing import List, Optional
import json
import datetime
from pathlib import Path

from ..harvester.docs_harvester import NfCoreDocsHarvester
from ..harvester.excel_harvester import ExcelGuidelinesHarvester
from ..scanner.pipeline_scanner import PipelineScanner
from ..chat.chat_interface import NfCoreDocChat
from ..utils.report_generator import ReportGenerator

def harvest_command(args):
    """Handle the harvest command"""
    # Set the default output location based on harvest source
    if args.excel_template and not args.output_specified:
        args.output = "excel_vectorstore"
        print(f"Using default Excel vectorstore path: {args.output}")
        
    if args.excel_template:
        print(f"Harvesting nf-core guidelines from Excel template: {args.excel_template}")
        harvester = ExcelGuidelinesHarvester(
            args.excel_template, 
            openai_api_key=args.openai_api_key,
            anthropic_api_key=args.anthropic_api_key
        )
    else:
        print(f"Harvesting nf-core documentation from website...")
        harvester = NfCoreDocsHarvester(
            openai_api_key=args.openai_api_key,
            anthropic_api_key=args.anthropic_api_key
        )
    
    vectorstore = harvester.harvest(args.output)
    
    print(f"Documentation harvested and stored in {args.output}")
    
    return vectorstore

def validate_command(args):
    """Handle the validate command"""
    print(f"Validating pipeline: {args.pipeline_path}")
    
    scanner = PipelineScanner(
        args.pipeline_path, 
        args.vectorstore,
        openai_api_key=args.openai_api_key,
        model_provider=args.model_provider,
        anthropic_api_key=args.anthropic_api_key,
        excel_template=args.excel_template
    )
    
    report = scanner.scan_pipeline(max_workers=args.max_workers)
    
    # Generate reports
    report_generator = ReportGenerator(report)
    
    # JSON report
    json_path = report_generator.generate_json_report(args.output)
    print(f"JSON report saved to: {json_path}")
    
    # Markdown report if requested
    if args.format == "markdown" or args.format == "both":
        md_path = report_generator.generate_markdown_report(
            Path(json_path).with_suffix(".md")
        )
        print(f"Markdown report saved to: {md_path}")
    
    # XML report if requested
    if args.format == "xml" or args.format == "both":
        xml_path = report_generator.generate_xml_report(
            Path(json_path).with_suffix(".xml")
        )
        print(f"XML report saved to: {xml_path}")
        
    return report

def chat_command(args):
    """Handle the chat command"""
    print(f"Starting chat interface with nf-core documentation...")
    
    chat = NfCoreDocChat(
        vectorstore_path=args.vectorstore,
        openai_api_key=args.openai_api_key,
        model_provider=args.model_provider,
        anthropic_api_key=args.anthropic_api_key
    )
    
    print("Chat with nf-core documentation. Type 'exit' to quit.")
    print("You can ask questions about nf-core guidelines, modules, workflows, etc.")
    
    while True:
        try:
            user_input = input("\nYou: ")
            
            if user_input.lower() in ["exit", "quit", "q"]:
                print("Exiting chat...")
                break
                
            response = chat.ask(
                user_input, 
                show_sources=args.show_sources,
                context_size=args.context_size
            )
            
            print(f"\nnf-core: {response}")
            
        except KeyboardInterrupt:
            print("\nExiting chat...")
            break
        except Exception as e:
            print(f"Error: {str(e)}")
    
    return None

def main():
    """Main entry point for the CLI"""
    parser = argparse.ArgumentParser(description="nf-core validator CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Common arguments
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument(
        "--openai-api-key", 
        help="OpenAI API key (defaults to OPENAI_API_KEY environment variable)"
    )
    parent_parser.add_argument(
        "--model-provider",
        choices=["openai", "anthropic"],
        default="openai",
        help="Model provider to use (default: openai)"
    )
    parent_parser.add_argument(
        "--anthropic-api-key",
        help="Anthropic API key for Claude models (defaults to ANTHROPIC_API_KEY environment variable)"
    )
    
    # Harvest command
    harvest_parser = subparsers.add_parser(
        "harvest", 
        parents=[parent_parser],
        help="Harvest nf-core documentation"
    )
    harvest_parser.add_argument(
        "--output", 
        default="nfcore_vectorstore",
        help="Output directory for vector store (default depends on harvest source)"
    )
    harvest_parser.add_argument(
        "--excel-template",
        help="Path to Excel template with nf-core guidelines"
    )
    
    # Validate command
    validate_parser = subparsers.add_parser(
        "validate", 
        parents=[parent_parser],
        help="Validate a pipeline"
    )
    validate_parser.add_argument(
        "pipeline_path",
        help="Path to the pipeline to validate"
    )
    validate_parser.add_argument(
        "--vectorstore",
        default="nfcore_vectorstore",
        help="Path to the vector store (default: nfcore_vectorstore)"
    )
    validate_parser.add_argument(
        "--excel-template",
        help="Path to Excel template with nf-core guidelines"
    )
    validate_parser.add_argument(
        "--output",
        help="Output path for the report (default: <pipeline_name>_compliance_report.json)"
    )
    validate_parser.add_argument(
        "--format",
        choices=["json", "markdown", "xml", "both"],
        default="both",
        help="Report format (default: both - generates all formats)"
    )
    validate_parser.add_argument(
        "--max-workers",
        type=int,
        default=4,
        help="Maximum number of parallel workers (default: 4)"
    )
    
    # Chat command
    chat_parser = subparsers.add_parser(
        "chat",
        parents=[parent_parser],
        help="Chat with nf-core documentation"
    )
    chat_parser.add_argument(
        "--vectorstore",
        default="nfcore_vectorstore",
        help="Path to the vector store (default: nfcore_vectorstore)"
    )
    chat_parser.add_argument(
        "--show-sources",
        action="store_true",
        help="Show sources in chat responses"
    )
    chat_parser.add_argument(
        "--context-size",
        type=int,
        default=5,
        help="Number of documents to retrieve for context (default: 5)"
    )
    
    args = parser.parse_args()
    
    # Track whether output was explicitly specified
    if args.command == "harvest":
        # Check if --output was explicitly provided
        args.output_specified = "--output" in sys.argv
    
    # Check for required API keys based on model provider
    if args.command == "validate" or args.command == "chat":
        if args.model_provider == "openai":
            if not args.openai_api_key and not os.environ.get("OPENAI_API_KEY"):
                print("Error: OpenAI API key is required. Set OPENAI_API_KEY environment variable or use --openai-api-key.")
                return 1
        elif args.model_provider == "anthropic":
            if not args.anthropic_api_key and not os.environ.get("ANTHROPIC_API_KEY"):
                print("Error: Anthropic API key is required. Set ANTHROPIC_API_KEY environment variable or use --anthropic-api-key.")
                return 1
                
    # No API key checks for harvest command - it uses HuggingFace embeddings by default
    
    if args.command == "harvest":
        harvest_command(args)
    elif args.command == "validate":
        validate_command(args)
    elif args.command == "chat":
        chat_command(args)
    else:
        parser.print_help()
        
    return 0

if __name__ == "__main__":
    sys.exit(main())
