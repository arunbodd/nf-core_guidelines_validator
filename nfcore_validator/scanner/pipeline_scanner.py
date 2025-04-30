"""
Pipeline scanner for nf-core compliance
"""
import os
import glob
import json
from typing import Dict, List, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import re

from ..validator.llm_validator import NfCoreValidator
from ..validator.excel_validator import ExcelValidator

class PipelineScanner:
    """Scanner for nf-core pipeline compliance"""
    
    def __init__(self, pipeline_path: str, vectorstore_path: str = "nfcore_vectorstore", 
                 openai_api_key: str = None, model_provider: str = "openai", 
                 anthropic_api_key: str = None, excel_template: str = None):
        """Initialize the scanner
        
        Args:
            pipeline_path: Path to the pipeline to scan
            vectorstore_path: Path to the vector store with nf-core documentation
            openai_api_key: OpenAI API key for LLM and embeddings
            model_provider: Which model provider to use ('openai' or 'anthropic')
            anthropic_api_key: Anthropic API key for Claude models
            excel_template: Path to Excel template with requirements (optional)
        """
        self.pipeline_path = os.path.abspath(pipeline_path)
        
        # Set up the appropriate validator based on whether Excel template is provided
        if excel_template:
            self.validator = ExcelValidator(
                excel_path=excel_template,
                vectorstore_path=vectorstore_path,
                openai_api_key=openai_api_key,
                model_provider=model_provider,
                anthropic_api_key=anthropic_api_key
            )
            print(f"Using Excel-based validator with template: {excel_template}")
        else:
            self.validator = NfCoreValidator(
                vectorstore_path=vectorstore_path, 
                openai_api_key=openai_api_key,
                model_provider=model_provider,
                anthropic_api_key=anthropic_api_key
            )
            print("Using LLM-based validator with nf-core documentation")
        
        if not os.path.exists(self.pipeline_path):
            raise ValueError(f"Pipeline path does not exist: {self.pipeline_path}")
    
    def find_components(self) -> List[str]:
        """Find all components in the pipeline
        
        Returns:
            List of component file paths
        """
        components = []
        
        # Find modules
        module_paths = glob.glob(f"{self.pipeline_path}/modules/**/*.nf", recursive=True)
        components.extend(module_paths)
        
        # Find workflows
        workflow_paths = glob.glob(f"{self.pipeline_path}/workflows/*.nf", recursive=True)
        components.extend(workflow_paths)
        
        # Find subworkflows
        subworkflow_paths = glob.glob(f"{self.pipeline_path}/subworkflows/**/*.nf", recursive=True)
        components.extend(subworkflow_paths)
        
        # Find main workflow
        main_workflow = f"{self.pipeline_path}/main.nf"
        if os.path.exists(main_workflow):
            components.append(main_workflow)
            
        # Add pipeline-level files for validation
        pipeline_files = [
            f"{self.pipeline_path}/nextflow.config",
            f"{self.pipeline_path}/nextflow_schema.json",
            f"{self.pipeline_path}/README.md",
            f"{self.pipeline_path}/CHANGELOG.md",
            f"{self.pipeline_path}/LICENSE",
            f"{self.pipeline_path}/CITATIONS.md"
        ]
        
        for file_path in pipeline_files:
            if os.path.exists(file_path):
                components.append(file_path)
                
        # Add config directory files
        conf_dir = f"{self.pipeline_path}/conf"
        if os.path.exists(conf_dir):
            conf_files = glob.glob(f"{conf_dir}/*.config")
            components.extend(conf_files)
            
        # Add test data directories
        test_dir = f"{self.pipeline_path}/tests"
        if os.path.exists(test_dir):
            components.append(test_dir)
            
        return components
    
    def scan_pipeline(self, max_workers: int = 4) -> Dict[str, Any]:
        """Scan the pipeline for compliance
        
        Args:
            max_workers: Maximum number of parallel workers
            
        Returns:
            Dictionary with scan results
        """
        components = self.find_components()
        print(f"Found {len(components)} components to validate")
        
        results = []
        total_requirements = 0
        passed_requirements = 0
        
        # Process components with rate limiting
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Schedule all component validation tasks at once
            future_to_component = {executor.submit(self.validator.validate_component, component): component for component in components}
            for future in as_completed(future_to_component):
                component = future_to_component[future]
                try:
                    result = future.result()
                    results.append(result)
                    
                    # Update counters
                    if "requirements" in result:
                        for req in result["requirements"]:
                            total_requirements += 1
                            if req.get("status") == "passed":
                                passed_requirements += 1
                                
                except Exception as e:
                    error_msg = str(e)
                    print(f"Error processing {component}: {error_msg}")
                    
                    # If rate limited, wait and retry
                    if "Rate limit reached" in error_msg:
                        wait_time = 15  # Default wait time
                        # Try to extract wait time from error message
                        match = re.search(r"Please try again in (\d+\.\d+)s", error_msg)
                        if match:
                            wait_time = float(match.group(1)) + 1  # Add a buffer
                            
                        print(f"Rate limited. Waiting {wait_time} seconds before continuing...")
                        time.sleep(wait_time)
                        
                        # Retry this component
                        try:
                            result = self.validator.validate_component(component)
                            results.append(result)
                        except Exception as retry_e:
                            print(f"Retry failed for {component}: {str(retry_e)}")
                            results.append({
                                "error": str(retry_e),
                                "path": component
                            })
                    else:
                        results.append({
                            "error": error_msg,
                            "path": component
                        })
                
                print(f"Processed component: {component}")
                
                # Add a small delay to avoid rate limiting
                time.sleep(0.5)
        
        # Calculate compliance score
        compliance_score = 0
        if total_requirements > 0:
            compliance_score = round((passed_requirements / total_requirements) * 100, 2)
            
        # Build report
        report = {
            "pipeline_path": self.pipeline_path,
            "components": results,
            "summary": {
                "total_components": len(components),
                "total_requirements": total_requirements,
                "passed_requirements": passed_requirements,
                "compliance_score": compliance_score
            }
        }
        
        return report
        
    def generate_report(self, output_path: str = None) -> str:
        """Generate a compliance report
        
        Args:
            output_path: Path to save the report (JSON)
            
        Returns:
            Path to the saved report
        """
        report = self.scan_pipeline()
        
        if output_path is None:
            pipeline_name = os.path.basename(self.pipeline_path)
            output_path = f"{pipeline_name}_compliance_report.json"
            
        with open(output_path, "w") as f:
            json.dump(report, f, indent=2)
            
        print(f"Compliance report saved to {output_path}")
        print(f"Overall compliance score: {report['summary']['compliance_score']}%")
        
        return output_path
