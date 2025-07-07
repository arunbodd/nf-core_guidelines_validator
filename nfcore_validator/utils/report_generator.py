"""
Report generator for nf-core validator
"""
import os
import json
from typing import Dict, Any, List
from collections import Counter
import datetime
from pathlib import Path
import xml.dom.minidom as md
import xml.etree.ElementTree as ET

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
            
    def _generate_excel_table_markdown(self, data: Dict[str, Any]) -> str:
        """Generate Excel-style table report for pipeline-wide validation"""
        md = []
        
        # Title and summary
        md.append(f"# nf-core Pipeline Compliance Report")
        md.append(f"**Pipeline:** {data.get('pipeline_path', 'Unknown')}")
        md.append(f"**Generated:** {data.get('timestamp', 'Unknown')}")
        md.append("")
        
        # Overall summary
        summary = data.get('summary', {})
        compliance_score = summary.get('compliance_score', 0)
        total_requirements = summary.get('total_requirements', 0)
        passed_requirements = summary.get('passed_requirements', 0)
        
        md.append("## Summary")
        md.append(f"- **Overall Compliance Score:** {compliance_score:.1f}%")
        md.append(f"- **Requirements Met:** {passed_requirements}/{total_requirements}")
        md.append(f"- **Requirements Failed:** {total_requirements - passed_requirements}/{total_requirements}")
        md.append("")
        
        # Requirements table
        md.append("## Requirements Validation Results")
        md.append("")
        
        # Get results from the single component (pipeline-wide validation)
        components = data.get('components', [])
        if components:
            results = components[0].get('results', [])
            
            if results:
                # Table header
                md.append("| # | Requirement | Met | Score | Reason | Evidence |")
                md.append("|---|-------------|-----|-------|--------|----------|")
                
                # Table rows
                for i, result in enumerate(results, 1):
                    req_id = result.get('id', 'Unknown')[:50]  # Truncate long IDs
                    description = result.get('description', 'No description')[:100]  # Truncate long descriptions
                    meets_req = result.get('meets_requirement', False)
                    score = result.get('score', 0)
                    reason = result.get('reason', '')[:80]  # Truncate long reasons
                    evidence = result.get('evidence', '')[:80]  # Truncate long evidence
                    
                    # Format boolean as Yes/No
                    meets_display = "✅ Yes" if meets_req else "❌ No"
                    
                    # Escape pipe characters in content
                    req_id = req_id.replace('|', '\|')
                    description = description.replace('|', '\|')
                    reason = reason.replace('|', '\|')
                    evidence = evidence.replace('|', '\|')
                    
                    md.append(f"| {i} | {description} | {meets_display} | {score} | {reason} | {evidence} |")
                
                md.append("")
                
                # Summary statistics
                met_count = sum(1 for r in results if r.get('meets_requirement', False))
                not_met_count = len(results) - met_count
                
                md.append("## Detailed Statistics")
                md.append(f"- **Total Requirements Evaluated:** {len(results)}")
                md.append(f"- **Requirements Met:** {met_count}")
                md.append(f"- **Requirements Not Met:** {not_met_count}")
                md.append(f"- **Compliance Percentage:** {(met_count/len(results)*100):.1f}%")
                
            else:
                md.append("No validation results found.")
        else:
            md.append("No components found for validation.")
        
        return "\n".join(md)

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
        
        # Classification Compliance Table
        md.append("## Classification Compliance Breakdown\n")
        md.append("| Classification | Definition | Category | Subcategory | Files not passing the definition |\n")
        md.append("|---------------|------------|----------|-------------|----------------------------------|\n")
        
        # Group failed requirements by classification/category/subcategory
        classification_failures = {}
        for component in components:
            component_path = component.get('component_path', 'Unknown')
            for req in component.get('requirements', []):
                if req.get('status') == 'failed':
                    classification = req.get('classification', 'Unknown')
                    category = req.get('category', 'Unknown') 
                    subcategory = req.get('subcategory', 'Unknown')
                    definition = req.get('description', 'No description')
                    
                    # Create unique key for this requirement
                    key = f"{classification}|{category}|{subcategory}|{definition}"
                    
                    if key not in classification_failures:
                        classification_failures[key] = {
                            'classification': classification,
                            'definition': definition,
                            'category': category,
                            'subcategory': subcategory,
                            'failed_files': []
                        }
                    
                    # Add the failed file
                    filename = os.path.basename(component_path)
                    if filename not in classification_failures[key]['failed_files']:
                        classification_failures[key]['failed_files'].append(filename)
        
        # Sort by classification, then category, then subcategory
        sorted_failures = sorted(classification_failures.values(), 
                               key=lambda x: (x['classification'], x['category'], x['subcategory']))
        
        for failure in sorted_failures:
            classification = failure['classification'] or 'Unknown'
            definition = failure['definition'][:100] + '...' if len(failure['definition']) > 100 else failure['definition']
            category = failure['category'] or 'Unknown'
            subcategory = failure['subcategory'] or 'Unknown'
            failed_files = ', '.join(failure['failed_files'])
            
            md.append(f"| {classification} | {definition} | {category} | {subcategory} | {failed_files} |\n")
        
        md.append("\n")
        
        # Component type breakdown
        md.append("## Component Type Breakdown\n")
        md.append("| Component Type | Count | Avg. Compliance |\n")
        md.append("|---------------|-------|----------------|\n")
        
        for component_type, components_list in components_by_type.items():
            # Calculate average compliance for this component type
            total_score = 0
            for component in components_list:
                component_summary = component.get('summary', {})
                if component_summary:
                    # Old format with summary object
                    total_score += component_summary.get('compliance_score', 0)
                else:
                    # New format with direct fields
                    passed_count = component.get('passed', 0)
                    total_count = component.get('total', 0)
                    compliance_score = (passed_count / total_count * 100) if total_count > 0 else 0
                    total_score += compliance_score
            
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
            def get_compliance_score(c):
                summary = c.get('summary', {})
                if summary:
                    return summary.get('compliance_score', 0)
                else:
                    passed = c.get('passed', 0)
                    total = c.get('total', 0)
                    return (passed / total * 100) if total > 0 else 0
            
            sorted_components = sorted(
                components_list, 
                key=get_compliance_score
            )
            
            for component in sorted_components:
                component_path = component.get('component_path', 'Unknown')
                
                # Handle both summary format and direct fields format
                component_summary = component.get('summary', {})
                if component_summary:
                    # Old format with summary object
                    compliance_score = component_summary.get('compliance_score', 0)
                    passed_count = component_summary.get('passed', 0)
                    failed_count = component_summary.get('failed', 0)
                else:
                    # New format with direct fields
                    passed_count = component.get('passed', 0)
                    total_count = component.get('total', 0)
                    failed_count = total_count - passed_count
                    compliance_score = (passed_count / total_count * 100) if total_count > 0 else 0
                
                md.append(f"#### {os.path.basename(component_path)}\n")
                md.append(f"- **Path:** `{component_path}`\n")
                md.append(f"- **Compliance Score:** {compliance_score:.1f}%\n")
                md.append(f"- **Passed:** {passed_count} requirements\n")
                md.append(f"- **Failed:** {failed_count} requirements\n")
                
                # Requirements grouped by status - handle both 'requirements' and 'results'
                passed_reqs = []
                failed_reqs = []
                
                requirements = component.get('requirements', []) or component.get('results', [])
                for req in requirements:
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
        
        # Check if this is pipeline-wide validation (single component with requirements from vectorstore)
        components = self.report.get('components', [])
        is_pipeline_wide = (len(components) == 1 and 
                           len(components[0].get('results', [])) > 5 and  # More than 5 requirements suggests pipeline-wide
                           components[0].get('component_path') == self.report.get('pipeline_path'))  # Component path matches pipeline path
        
        with open(output_path, 'w') as f:
            if is_pipeline_wide:
                # Use Excel table format for pipeline-wide validation
                f.write(self._generate_excel_table_markdown(self.report))
            else:
                # Use traditional component-wise format
                f.write(self._generate_markdown(self.report))
            
        return output_path

    def generate_xml_report(self, output_path: str = None) -> str:
        """Generate an XML compliance report based on the specified format
        
        Args:
            output_path: Path to save the report
            
        Returns:
            Path to the saved report
        """
        if output_path is None:
            output_path = f"{os.path.basename(self.report.get('pipeline_path', 'unknown'))}_compliance_report.xml"
        
        # Create root element
        root = ET.Element("compliance_report")
        
        # Extract components and group by category from Excel template
        components = self.report.get("components", [])
        categories = {}
        
        # Group requirements by category and subcategory
        for component in components:
            for req in component.get("requirements", []):
                req_id = req.get("id", "unknown")
                # Check if this is a category.subcategory format ID (e.g., "5.2")
                parts = req_id.split('.')
                
                # Try to determine category and subcategory
                if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                    category = f"Section {parts[0]}"
                    subcategory = f"{parts[0]}.{parts[1]}"
                else:
                    # Use component type as fallback category
                    category = component.get("component_type", "other").replace("_", " ").title()
                    subcategory = req_id
                
                if category not in categories:
                    categories[category] = {}
                    
                if subcategory not in categories[category]:
                    categories[category][subcategory] = {
                        "requirements": [],
                        "components": set()
                    }
                
                # Add component path to affected components
                categories[category][subcategory]["components"].add(component.get("path", ""))
                
                # Only add requirement if not already present
                req_exists = False
                for existing_req in categories[category][subcategory]["requirements"]:
                    if existing_req["description"] == req.get("description", ""):
                        req_exists = True
                        # Update affected components info
                        if component.get("path") not in existing_req.get("affected_components", []):
                            existing_req.setdefault("affected_components", []).append(component.get("path"))
                        break
                
                if not req_exists:
                    # Create a copy with affected components
                    req_copy = req.copy()
                    req_copy["affected_components"] = [component.get("path")]
                    categories[category][subcategory]["requirements"].append(req_copy)
        
        # Create XML structure
        for category, subcategories in categories.items():
            for subcategory, data in subcategories.items():
                for req in data["requirements"]:
                    req_element = ET.SubElement(root, "requirement")
                    
                    # Name element (using ID and description)
                    name_element = ET.SubElement(req_element, "name")
                    name_element.text = f"{req.get('id', 'Unknown')} - {req.get('description', '')}"
                    
                    # Met element (Yes/No)
                    met_element = ET.SubElement(req_element, "met")
                    met_element.text = "Yes" if req.get("status") == "passed" else "No"
                    
                    # Notes element
                    notes_element = ET.SubElement(req_element, "notes")
                    
                    # Build notes content
                    notes_content = ""
                    
                    # If requirement failed, add affected components and fixes
                    if req.get("status") != "passed":
                        # Add affected components
                        notes_content += "Non-compliant components:\n"
                        for comp_path in req.get("affected_components", []):
                            notes_content += f"- {os.path.basename(comp_path)} ({comp_path})\n"
                        
                        # Add reason for non-compliance
                        notes_content += "\nReason for non-compliance:\n"
                        notes_content += f"- {req.get('description', 'Not specified')}\n"
                        
                        # Add suggestion for compliance
                        notes_content += "\nSuggestion for achieving compliance:\n"
                        notes_content += f"- {req.get('fix', 'Not specified')}\n"
                    else:
                        notes_content = "This requirement is met."
                        
                    notes_element.text = notes_content
        
        # Check if this is a non-pipeline format
        is_pipeline_format = any(c.get("component_type") == "main_workflow" for c in components)
        
        # Add non-compliant check for empty self.report
        if not self.report:
            raise ValueError("No report data available")
            
        if not is_pipeline_format:
            # Add non-pipeline format section
            non_pipeline = ET.SubElement(root, "non_pipeline_format")
            
            # Find script files
            script_files = []
            for component in components:
                path = component.get("path", "")
                if path.endswith(('.sh', '.py', '.pl', '.R')):
                    script_files.append(path)
            
            # Build content for non-pipeline format
            content = "This workflow is not in the standard nf-core pipeline format.\n\n"
            
            # List existing scripts
            content += "Script files found:\n"
            for script in script_files:
                content += f"- {os.path.basename(script)} ({script})\n"
                
            # Instructions for converting
            content += "\nTo convert to nf-core pipeline format:\n"
            content += "1. Create a standard nf-core pipeline structure using nf-core tools:\n"
            content += "   nf-core create -n [pipeline_name]\n\n"
            content += "2. Organize scripts into proper modules:\n"
            content += "   - Move processing scripts to modules/local/\n"
            content += "   - Create proper Nextflow modules with inputs, outputs, and documentation\n\n"
            content += "3. Create a main workflow (main.nf) that imports and runs the modules\n\n"
            content += "4. Add proper configuration (nextflow.config, modules.config)\n\n"
            content += "5. Add documentation (README.md, CITATION.md)\n\n"
            content += "6. Add proper testing (tests directory)"
            
            non_pipeline.text = content
        
        # Format the XML with pretty printing
        xml_str = ET.tostring(root, encoding='unicode')
        pretty_xml = md.parseString(xml_str).toprettyxml(indent="  ")
        
        # Write to file
        with open(output_path, "w") as f:
            f.write(pretty_xml)
            
        return output_path
