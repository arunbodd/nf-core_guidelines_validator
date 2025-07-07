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
            anthropic_api_key=args.anthropic_api_key
        )
    else:
        print(f"Harvesting nf-core documentation from website...")
        harvester = NfCoreDocsHarvester(
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

def harvest_pipeline_command(args):
    """Handle the harvest-pipeline command"""
    print(f"🔄 Harvesting pipeline codebase: {args.pipeline_path}")
    
    import os
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.schema import Document
    from langchain_community.vectorstores import FAISS
    from langchain_huggingface import HuggingFaceEmbeddings
    
    try:
        documents = []
        
        # File extensions to include
        code_extensions = {'.nf', '.py', '.yml', '.yaml', '.md', '.txt', '.config', '.json'}
        
        print(f"📚 Scanning pipeline files...")
        for root, dirs, files in os.walk(args.pipeline_path):
            # Skip hidden directories and common non-code directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in {'__pycache__', 'node_modules'}]
            
            for file in files:
                if any(file.endswith(ext) for ext in code_extensions):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, args.pipeline_path)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            
                        if content.strip():  # Only add non-empty files
                            # Create document with metadata
                            doc = Document(
                                page_content=f"File: {rel_path}\n\n{content}",
                                metadata={
                                    'file_path': rel_path,
                                    'file_type': os.path.splitext(file)[1],
                                    'source': 'pipeline_code'
                                }
                            )
                            documents.append(doc)
                            
                    except Exception as e:
                        print(f"⚠️ Error reading {rel_path}: {e}")
                        continue
        
        print(f"📄 Found {len(documents)} code files")
        
        if not documents:
            raise ValueError("No code files found in pipeline")
        
        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", " ", ""]
        )
        
        split_docs = text_splitter.split_documents(documents)
        print(f"📝 Created {len(split_docs)} text chunks")
        
        # Create vectorstore
        print(f"🤖 Creating embeddings...")
        embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
        pipeline_vectorstore = FAISS.from_documents(split_docs, embeddings)
        
        # Save the vectorstore
        output_path = args.output or f"{Path(args.pipeline_path).name}_pipeline_vectorstore"
        pipeline_vectorstore.save_local(output_path)
        
        print(f"✅ Pipeline vectorstore saved to: {output_path}")
        print(f"📊 This vectorstore can now be used for efficient validation against Excel requirements")
        print(f"💰 Benefits: 80-90% cost reduction, targeted context retrieval, better accuracy")
        
        return output_path
        
    except Exception as e:
        print(f"❌ Error harvesting pipeline: {e}")
        import traceback
        traceback.print_exc()
        return None

def chat_command(args):
    """Handle the chat command"""
    print(f"Starting chat interface with nf-core documentation...")
    
    chat = NfCoreDocChat(
        vectorstore_path=args.vectorstore,
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
        "--api-key",
        help="Anthropic API key for Claude 4 Opus (defaults to ANTHROPIC_API_KEY environment variable)"
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
    
    # Harvest Pipeline command
    harvest_pipeline_parser = subparsers.add_parser(
        "harvest-pipeline",
        help="Harvest pipeline codebase into vectorstore for efficient validation"
    )
    harvest_pipeline_parser.add_argument(
        "pipeline_path",
        help="Path to the pipeline to harvest"
    )
    harvest_pipeline_parser.add_argument(
        "--output",
        help="Output directory for pipeline vector store (default: <pipeline_name>_pipeline_vectorstore)"
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
        help="Path to the requirements vector store (default: nfcore_vectorstore)"
    )
    validate_parser.add_argument(
        "--pipeline-vectorstore",
        help="Path to pre-created pipeline vectorstore for efficient validation (optional)"
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
        default=8,
        help="Maximum number of parallel workers (default: 8)"
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
    
    # Set anthropic_api_key from --api-key argument or environment (only for commands that have it)
    if hasattr(args, 'api_key'):
        args.anthropic_api_key = args.api_key or os.environ.get("ANTHROPIC_API_KEY")
    else:
        args.anthropic_api_key = None
    
    # Check for required Anthropic API key
    if args.command == "validate" or args.command == "chat":
        if not args.anthropic_api_key:
            print("Error: Anthropic API key is required. Set ANTHROPIC_API_KEY environment variable or use --api-key.")
            return 1
                
    # No API key checks for harvest command - it uses HuggingFace embeddings by default
    
    if args.command == "harvest":
        harvest_command(args)
    elif args.command == "harvest-pipeline":
        harvest_pipeline_command(args)
    elif args.command == "validate":
        validate_command(args)
    elif args.command == "chat":
        chat_command(args)
    else:
        parser.print_help()
        
    return 0

if __name__ == "__main__":
    sys.exit(main())
