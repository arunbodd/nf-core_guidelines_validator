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
from datetime import datetime
from pathlib import Path

from ..validator.llm_validator import NfCoreValidator
from ..validator.excel_validator import ExcelValidator

class PipelineScanner:
    """Scanner for nf-core pipeline compliance"""
    
    def __init__(self, pipeline_path: str, vectorstore_path: str = "nfcore_vectorstore", 
                 anthropic_api_key: str = None, excel_template: str = None):
        """Initialize the scanner with Anthropic Claude 4 Opus
        
        Args:
            pipeline_path: Path to the pipeline to scan
            vectorstore_path: Path to the vector store with nf-core documentation
            anthropic_api_key: Anthropic API key for Claude 4 Opus
            excel_template: Path to Excel template with requirements (optional)
        """
        self.pipeline_path = os.path.abspath(pipeline_path)
        
        # Set up the appropriate validator based on whether Excel template is provided
        if excel_template:
            self.validator = ExcelValidator(
                excel_path=excel_template,
                vectorstore_path=vectorstore_path,
                anthropic_api_key=anthropic_api_key
            )
            print(f"Using Excel-based validator with template: {excel_template}")
        else:
            self.validator = NfCoreValidator(
                vectorstore_path=vectorstore_path, 
                anthropic_api_key=anthropic_api_key
            )
            print("Using LLM-based validator with Anthropic Claude 4 Opus")
        
        if not os.path.exists(self.pipeline_path):
            raise ValueError(f"Pipeline path does not exist: {self.pipeline_path}")
    
    def find_components(self) -> List[str]:
        """Find all components in the pipeline
        
        Returns:
            List of component file paths
        """
        components = []
        
        print(f"🔍 Scanning pipeline directory: {self.pipeline_path}")
        
        # Find ALL .nf files recursively (not just in standard locations)
        all_nf_files = glob.glob(f"{self.pipeline_path}/**/*.nf", recursive=True)
        components.extend(all_nf_files)
        print(f"Found {len(all_nf_files)} Nextflow (.nf) files")
        
        # Find ALL .config files recursively
        all_config_files = glob.glob(f"{self.pipeline_path}/**/*.config", recursive=True)
        components.extend(all_config_files)
        print(f"Found {len(all_config_files)} config files")
        
        # Find main workflow (could be in root or subdirectories)
        main_workflows = glob.glob(f"{self.pipeline_path}/**/main.nf", recursive=True)
        for main_workflow in main_workflows:
            if main_workflow not in components:
                components.append(main_workflow)
        
        # Find nextflow.config files (could be in multiple locations)
        nextflow_configs = glob.glob(f"{self.pipeline_path}/**/nextflow.config", recursive=True)
        for config in nextflow_configs:
            if config not in components:
                components.append(config)
                
        # Add pipeline-level files for validation (check root directory)
        pipeline_files = [
            f"{self.pipeline_path}/nextflow_schema.json",
            f"{self.pipeline_path}/README.md",
            f"{self.pipeline_path}/CHANGELOG.md",
            f"{self.pipeline_path}/LICENSE",
            f"{self.pipeline_path}/CITATIONS.md",
            f"{self.pipeline_path}/CONTRIBUTING.md",
            f"{self.pipeline_path}/CODE_OF_CONDUCT.md",
            f"{self.pipeline_path}/code-of-conduct.md"  # Alternative naming
        ]
        
        for file_path in pipeline_files:
            if os.path.exists(file_path) and file_path not in components:
                components.append(file_path)
                
        # Find Docker and container files
        container_files = [
            f"{self.pipeline_path}/Dockerfile",
            f"{self.pipeline_path}/Dockerfile.*",
            f"{self.pipeline_path}/.dockerignore"
        ]
        
        for pattern in container_files:
            matching_files = glob.glob(pattern)
            for file_path in matching_files:
                if os.path.exists(file_path) and file_path not in components:
                    components.append(file_path)
        
        # Find additional Docker files with glob patterns
        docker_files = glob.glob(f"{self.pipeline_path}/Dockerfile*")
        for docker_file in docker_files:
            if docker_file not in components:
                components.append(docker_file)
                
        # Find test directories and files
        test_patterns = [
            f"{self.pipeline_path}/tests/**/*",
            f"{self.pipeline_path}/test/**/*",
            f"{self.pipeline_path}/**/test_data/**/*"
        ]
        
        for pattern in test_patterns:
            test_files = glob.glob(pattern, recursive=True)
            for test_file in test_files:
                if os.path.isfile(test_file) and test_file not in components:
                    components.append(test_file)
        
        # Find workflow and process definition files
        workflow_patterns = [
            f"{self.pipeline_path}/**/workflows/**/*.nf",
            f"{self.pipeline_path}/**/processes/**/*.nf",
            f"{self.pipeline_path}/**/modules/**/*.nf",
            f"{self.pipeline_path}/**/subworkflows/**/*.nf"
        ]
        
        for pattern in workflow_patterns:
            workflow_files = glob.glob(pattern, recursive=True)
            for workflow_file in workflow_files:
                if workflow_file not in components:
                    components.append(workflow_file)
        
        # Remove duplicates and sort
        components = list(set(components))
        components.sort()
        
        print(f"📊 Total components found: {len(components)}")
        print("📁 Component types breakdown:")
        
        # Count by file type
        nf_count = len([c for c in components if c.endswith('.nf')])
        config_count = len([c for c in components if c.endswith('.config')])
        md_count = len([c for c in components if c.endswith('.md')])
        docker_count = len([c for c in components if 'Dockerfile' in os.path.basename(c) or c.endswith('.dockerignore')])
        other_count = len(components) - nf_count - config_count - md_count - docker_count
        
        print(f"   • Nextflow files (.nf): {nf_count}")
        print(f"   • Config files (.config): {config_count}")
        print(f"   • Documentation (.md): {md_count}")
        print(f"   • Container files: {docker_count}")
        print(f"   • Other files: {other_count}")
        
        return components
    
    def validate_pipeline_structure(self) -> Dict[str, Any]:
        """Validate overall pipeline structure for required files
        
        Returns:
            Dictionary with pipeline structure validation results
        """
        print("🏗️  Validating overall pipeline structure...")
        
        # Required files for every nf-core pipeline
        required_files = {
            "main.nf": "Main workflow file",
            "nextflow.config": "Pipeline configuration file", 
            "README.md": "Pipeline documentation",
            "nextflow_schema.json": "Parameter schema file",
            "CHANGELOG.md": "Change log documentation",
            "LICENSE": "License file"
        }
        
        # Optional but recommended files
        recommended_files = {
            "CODE_OF_CONDUCT.md": "Code of conduct",
            "code-of-conduct.md": "Code of conduct (alternative name)",
            "CITATIONS.md": "Citations file"
        }
        
        results = []
        pipeline_root = Path(self.pipeline_path)
        
        # Check required files
        for filename, description in required_files.items():
            file_path = pipeline_root / filename
            exists = file_path.exists()
            
            results.append({
                "id": f"pipeline_general_{filename.lower().replace('.', '_')}",
                "description": f"Pipeline must have {filename} - {description}",
                "status": "passed" if exists else "failed",
                "fix": f"Create {filename} file at pipeline root" if not exists else "",
                "file_path": str(file_path),
                "required": True
            })
        
        # Check recommended files
        for filename, description in recommended_files.items():
            file_path = pipeline_root / filename
            exists = file_path.exists()
            
            # For CODE_OF_CONDUCT, check both variants
            if filename.startswith("CODE_OF_CONDUCT"):
                alt_path = pipeline_root / "code-of-conduct.md"
                exists = exists or alt_path.exists()
                file_path = file_path if file_path.exists() else alt_path
            
            results.append({
                "id": f"pipeline_general_{filename.lower().replace('.', '_').replace('-', '_')}",
                "description": f"Pipeline should have {filename} - {description}",
                "status": "passed" if exists else "warning",
                "fix": f"Consider adding {filename} file at pipeline root" if not exists else "",
                "file_path": str(file_path),
                "required": False
            })
        
        # Calculate compliance
        total_required = sum(1 for r in results if r["required"])
        passed_required = sum(1 for r in results if r["required"] and r["status"] == "passed")
        compliance_score = (passed_required / total_required * 100) if total_required > 0 else 0
        
        print(f"   📊 Pipeline structure compliance: {compliance_score:.1f}% ({passed_required}/{total_required} required files)")
        
        return {
            "component_type": "pipeline_structure",
            "path": self.pipeline_path,
            "requirements": results,
            "summary": {
                "passed": sum(1 for r in results if r["status"] == "passed"),
                "failed": sum(1 for r in results if r["status"] == "failed"),
                "warnings": sum(1 for r in results if r["status"] == "warning"),
                "compliance_score": compliance_score
            }
        }
    
    def scan_pipeline(self, max_workers: int = 4) -> Dict[str, Any]:
        """Scan the pipeline for compliance
        
        Args:
            max_workers: Maximum number of parallel workers
            
        Returns:
            Dictionary with scan results
        """
        # First, validate overall pipeline structure
        pipeline_structure_result = self.validate_pipeline_structure()
        
        components = self.find_components()
        print(f"Found {len(components)} components to validate")
        
        # Debug: Show component types being detected
        print("\n🔍 Component type analysis:")
        component_types = {}
        for component in components:
            if hasattr(self.validator, '_determine_component_type'):
                comp_type = self.validator._determine_component_type(component)
                component_types[comp_type] = component_types.get(comp_type, 0) + 1
                print(f"  {component} -> {comp_type}")
        
        print(f"\n📊 Component type summary:")
        for comp_type, count in component_types.items():
            print(f"  {comp_type}: {count}")
        
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
        
        # Calculate overall compliance score
        # Include pipeline structure validation in results
        all_results = [pipeline_structure_result] + results
        
        if all_results:
            # Calculate compliance based on individual component scores
            total_score = 0
            components_with_scores = 0
            
            for result in all_results:
                # Get compliance score from component summary
                component_summary = result.get('summary', {})
                component_score = component_summary.get('compliance_score', 0)
                
                # Only count components that actually have requirements
                if 'requirements' in result and result['requirements']:
                    total_score += component_score
                    components_with_scores += 1
            
            # Calculate overall compliance as average of component scores
            overall_compliance = total_score / components_with_scores if components_with_scores > 0 else 0.0
            
            # Calculate additional summary statistics
            total_requirements = 0
            passed_requirements = 0
            
            for result in all_results:
                if 'requirements' in result:
                    reqs = result['requirements']
                    total_requirements += len(reqs)
                    passed_requirements += sum(1 for req in reqs if req.get('status') == 'passed')
        else:
            overall_compliance = 0.0
            total_requirements = 0
            passed_requirements = 0
        
        print(f"\nValidation completed. Overall compliance score: {overall_compliance:.2f}%")
        
        # Print usage summary if using LLM validator
        if hasattr(self.validator, 'print_usage_summary'):
            self.validator.print_usage_summary()
        
        # Return data structure that matches ReportGenerator expectations
        return {
            "pipeline_path": self.pipeline_path,
            "summary": {
                "total_components": len(all_results),
                "compliance_score": overall_compliance,
                "total_requirements": total_requirements,
                "passed_requirements": passed_requirements
            },
            "components": all_results,  # Include pipeline structure + component results
            "overall_compliance_score": overall_compliance,  # Keep for backward compatibility
            "total_components": len(all_results),  # Keep for backward compatibility
            "results": all_results,  # Keep for backward compatibility
            "timestamp": datetime.now().isoformat()
        }
        
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
        print(f"Overall compliance score: {report['overall_compliance_score']:.2f}%")
        
        return output_path
