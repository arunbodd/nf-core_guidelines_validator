"""
Report generator for nf-core validator
"""
import os
import json
from typing import Dict, Any, List
from collections import Counter
import datetime

class ReportGenerator:
    """Generate reports from validation results"""
    
    def __init__(self, report: Dict[str, Any] = None):
        """Initialize the report generator
        
        Args:
            report: Report dictionary (optional)
        """
        self.report = report
    
    def json_to_markdown(self, json_path: str, markdown_path: str) -> None:
        """Convert JSON report to Markdown
        
        Args:
            json_path: Path to JSON report
            markdown_path: Path to output Markdown file
        """
        with open(json_path, 'r') as f:
            report = json.load(f)
            
        with open(markdown_path, 'w') as f:
            f.write(self._generate_markdown(report))
            
    def _generate_markdown(self, report: Dict[str, Any]) -> str:
        """Generate Markdown report
        
        Args:
            report: Report dictionary
            
        Returns:
            Markdown report
        """
        pipeline_path = report.get('pipeline_path', 'Unknown')
        summary = report.get('summary', {})
        components = report.get('components', [])
        
        # Generate violation statistics
        violations = []
        for component in components:
            for req in component.get('requirements', []):
                if req.get('status') == 'failed':
                    violations.append(req)
                    
        violation_types = Counter([v.get('id', 'unknown') for v in violations])
        top_violations = violation_types.most_common(10)  # Show top 10 instead of 5
        
        # Group components by type
        components_by_type = {}
        for component in components:
            component_type = component.get('component_type', 'unknown')
            if component_type not in components_by_type:
                components_by_type[component_type] = []
            components_by_type[component_type].append(component)
        
        # Build markdown
        md = []
        
        # Header with more details
        md.append("# nf-core Pipeline Compliance Report\n")
        md.append(f"**Pipeline:** `{os.path.basename(pipeline_path)}`\n")
        md.append(f"**Path:** `{pipeline_path}`\n")
        md.append(f"**Date:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        md.append(f"**nf-core Validator Version:** {self._get_version()}\n\n")
        
        # Summary with more metrics
        md.append("## Summary\n")
        md.append(f"- **Components Analyzed:** {summary.get('total_components', 0)}\n")
        md.append(f"- **Requirements Checked:** {summary.get('total_requirements', 0)}\n")
        md.append(f"- **Passed Requirements:** {summary.get('passed_requirements', 0)}\n")
        md.append(f"- **Failed Requirements:** {summary.get('total_requirements', 0) - summary.get('passed_requirements', 0)}\n")
        md.append(f"- **Compliance Score:** {summary.get('compliance_score', 0)}%\n\n")
        
        # Component type breakdown
        md.append("## Component Type Breakdown\n")
        md.append("| Component Type | Count | Avg. Compliance |\n")
        md.append("|---------------|-------|----------------|\n")
        
        for component_type, components_list in components_by_type.items():
            # Calculate average compliance for this component type
            total_score = 0
            for component in components_list:
                component_summary = component.get('summary', {})
                total_score += component_summary.get('compliance_score', 0)
            
            avg_score = total_score / len(components_list) if components_list else 0
            md.append(f"| {component_type} | {len(components_list)} | {avg_score:.2f}% |\n")
        
        md.append("\n")
        
        # Top violations with more context
        if violations:
            md.append("## Top Violations\n")
            for violation_id, count in top_violations:
                # Find an example of this violation to show the description
                example = next((v for v in violations if v.get('id') == violation_id), {})
                description = example.get('description', 'No description available')
                
                md.append(f"- **{violation_id}:** {count} occurrences\n")
                md.append(f"  - *Description:* {description}\n")
                if example.get('fix'):
                    md.append(f"  - *Example fix:* {example.get('fix')}\n")
                md.append("\n")
        
        # Component details by type
        md.append("## Component Details\n")
        
        for component_type, components_list in sorted(components_by_type.items()):
            md.append(f"### {component_type.title()} Components\n")
            
            # Sort components by compliance score (worst first)
            sorted_components = sorted(
                components_list, 
                key=lambda c: c.get('summary', {}).get('compliance_score', 0)
            )
            
            for component in sorted_components:
                component_path = component.get('path', 'Unknown')
                component_summary = component.get('summary', {})
                
                md.append(f"#### {os.path.basename(component_path)}\n")
                md.append(f"- **Path:** `{component_path}`\n")
                md.append(f"- **Compliance Score:** {component_summary.get('compliance_score', 0)}%\n")
                md.append(f"- **Passed:** {component_summary.get('passed', 0)} requirements\n")
                md.append(f"- **Failed:** {component_summary.get('failed', 0)} requirements\n")
                
                # Requirements grouped by status
                passed_reqs = []
                failed_reqs = []
                
                for req in component.get('requirements', []):
                    if req.get('status') == 'passed':
                        passed_reqs.append(req)
                    else:
                        failed_reqs.append(req)
                
                # Show failed requirements first
                if failed_reqs:
                    md.append("\n##### Failed Requirements\n")
                    for req in failed_reqs:
                        md.append(f"- ❌ **{req.get('id', 'Unknown')}:** {req.get('description', 'No description')}\n")
                        if req.get('fix'):
                            md.append(f"  - **Fix:** {req.get('fix')}\n")
                
                # Show passed requirements (collapsible)
                if passed_reqs:
                    md.append("\n##### Passed Requirements\n")
                    for req in passed_reqs:
                        md.append(f"- ✅ **{req.get('id', 'Unknown')}:** {req.get('description', 'No description')}\n")
                
                md.append("\n")
        
        # Add recommendations section
        md.append("## Recommendations\n")
        md.append("Based on the validation results, here are the top recommendations to improve compliance:\n\n")
        
        # Get top 5 most common violations
        top_recommendations = violation_types.most_common(5)
        for i, (violation_id, count) in enumerate(top_recommendations):
            # Find examples of this violation
            examples = [v for v in violations if v.get('id') == violation_id]
            if examples:
                example = examples[0]
                md.append(f"{i+1}. **Fix {violation_id} violations** ({count} occurrences)\n")
                md.append(f"   - *Issue:* {example.get('description', 'No description')}\n")
                if example.get('fix'):
                    md.append(f"   - *Recommendation:* {example.get('fix')}\n")
                
                # List affected components
                affected_components = set(os.path.basename(v.get('component_path', 'Unknown')) 
                                     for v in examples if 'component_path' in v)
                if affected_components:
                    md.append(f"   - *Affected components:* {', '.join(sorted(affected_components))}\n")
                md.append("\n")
        
        return "\n".join(md)
        
    def _get_version(self):
        """Get the version of the nf-core validator"""
        try:
            from .. import __version__
            return __version__
        except ImportError:
            return "0.1.0"
            
    def generate_json_report(self, output_path: str = None) -> str:
        """Generate a JSON report
        
        Args:
            output_path: Path to save the report (JSON)
            
        Returns:
            Path to the saved report
        """
        if not self.report:
            raise ValueError("No report data available")
            
        if output_path is None:
            pipeline_name = os.path.basename(self.report.get('pipeline_path', 'unknown'))
            output_path = f"{pipeline_name}_compliance_report.json"
            
        with open(output_path, "w") as f:
            json.dump(self.report, f, indent=2)
            
        return output_path
    
    def generate_markdown_report(self, output_path: str = None) -> str:
        """Generate a Markdown report
        
        Args:
            output_path: Path to save the report (Markdown)
            
        Returns:
            Path to the saved report
        """
        if not self.report:
            raise ValueError("No report data available")
            
        if output_path is None:
            pipeline_name = os.path.basename(self.report.get('pipeline_path', 'unknown'))
            output_path = f"{pipeline_name}_compliance_report.md"
            
        with open(output_path, 'w') as f:
            f.write(self._generate_markdown(self.report))
            
        return output_path
