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

class PipelineScanner:
    """Scanner for nf-core pipeline compliance"""
    
    def __init__(self, pipeline_path: str, vectorstore_path: str = "nfcore_vectorstore", 
                 anthropic_api_key: str = None, excel_template: str = None):
        """Initialize the scanner with Anthropic Claude 3.5 Sonnet
        
        Args:
            pipeline_path: Path to the pipeline to scan
            vectorstore_path: Path to the vector store with nf-core documentation
            anthropic_api_key: Anthropic API key for Claude 3.5 Sonnet
        """
        self.pipeline_path = os.path.abspath(pipeline_path)
        
        # Always use NfCoreValidator with vectorstore for RAG-based validation
        # Excel templates should be converted to vectorstore using harvest command first
        self.validator = NfCoreValidator(
            vectorstore_path=vectorstore_path, 
            anthropic_api_key=anthropic_api_key
        )
        print("Using LLM-based validator with Anthropic Claude 3.5 Sonnet")
        
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
        """Scan the pipeline for compliance against all requirements in vectorstore
        
        Args:
            max_workers: Maximum number of parallel workers (not used in new approach)
            
        Returns:
            Dictionary with scan results
        """
        print(f"\n🚀 Starting pipeline-wide validation against all requirements")
        print(f"Pipeline path: {self.pipeline_path}")
        
        # Use the new pipeline-wide validation method
        validation_result = self.validator.validate_pipeline_against_requirements(self.pipeline_path)
        
        if 'error' in validation_result:
            return {
                'pipeline_path': self.pipeline_path,
                'error': validation_result['error'],
                'compliance_score': 0,
                'total_requirements': 0,
                'requirements_met': 0,
                'results': []
            }
        
        # Extract results
        total_requirements = validation_result.get('total_requirements', 0)
        requirements_met = validation_result.get('requirements_met', 0)
        compliance_score = validation_result.get('compliance_score', 0)
        results = validation_result.get('results', [])
        
        print(f"\n✅ Validation complete!")
        print(f"📊 Requirements met: {requirements_met}/{total_requirements}")
        print(f"🎯 Compliance score: {compliance_score:.1f}%")
        
        # Print usage summary if using LLM validator
        if hasattr(self.validator, 'print_usage_summary'):
            self.validator.print_usage_summary()
        
        # Return data structure that matches ReportGenerator expectations
        return {
            "pipeline_path": self.pipeline_path,
            "summary": {
                "total_components": 1,  # Single pipeline validation
                "compliance_score": compliance_score,
                "total_requirements": total_requirements,
                "passed_requirements": requirements_met
            },
            "components": [{
                "component_path": self.pipeline_path,
                "passed": requirements_met,
                "total": total_requirements,
                "results": results
            }],
            "overall_compliance_score": compliance_score,
            "total_components": 1,
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
