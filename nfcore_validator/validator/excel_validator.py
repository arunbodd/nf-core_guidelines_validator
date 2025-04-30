"""
Excel-based validator for nf-core pipeline components
"""
import os
import json
import pandas as pd
from typing import Dict, Any, List, Optional

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# Import model clients only when needed

class ExcelValidator:
    """Excel-based validator for nf-core pipeline components"""
    
    def __init__(self, excel_path: str, vectorstore_path: str = None, openai_api_key: str = None,
                 model_provider: str = "openai", anthropic_api_key: str = None):
        """Initialize the Excel-based validator
        
        Args:
            excel_path: Path to the Excel template
            vectorstore_path: Path to the vector store (optional)
            openai_api_key: OpenAI API key (required only if model_provider is 'openai')
            model_provider: Which model provider to use ('openai' or 'anthropic')
            anthropic_api_key: Anthropic API key for Claude models (required only if model_provider is 'anthropic')
        """
        self.excel_path = os.path.abspath(excel_path)
        self.vectorstore_path = vectorstore_path
        self.model_provider = model_provider.lower()
        self.openai_api_key = openai_api_key or os.environ.get("OPENAI_API_KEY")
        self.anthropic_api_key = anthropic_api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.llm = None
        self.anthropic_client = None
        
        # Check that the Excel file exists
        if not os.path.exists(self.excel_path):
            raise ValueError(f"Excel template does not exist: {self.excel_path}")
            
        # Load Excel template
        self.requirements_df = self._load_excel_template()
        
        # Set up LLM for validation - only when needed based on provider
        if self.model_provider == "openai":
            if not self.openai_api_key:
                raise ValueError("OpenAI API key is required for OpenAI models. Set OPENAI_API_KEY environment variable or pass it directly.")
                
            # Import only when needed
            from langchain.chat_models import ChatOpenAI
            self.llm = ChatOpenAI(
                temperature=0, 
                model="gpt-4",
                openai_api_key=self.openai_api_key
            )
        elif self.model_provider == "anthropic":
            if not self.anthropic_api_key:
                raise ValueError("Anthropic API key is required for Claude models. Set ANTHROPIC_API_KEY environment variable or pass it directly.")
                
            # Import only when needed
            import anthropic
            self.anthropic_client = anthropic.Anthropic(api_key=self.anthropic_api_key)
            self.anthropic_model = "claude-3-7-sonnet-20250219"
        else:
            raise ValueError(f"Unsupported model provider: {model_provider}. Choose from 'openai' or 'anthropic'")
            
        # Load vector store if it exists - always use HuggingFace embeddings
        if os.path.exists(self.vectorstore_path):
            print(f"Loading vector store from {self.vectorstore_path} with HuggingFace embeddings")
            self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            self.vectorstore = FAISS.load_local(self.vectorstore_path, self.embeddings)
        else:
            self.vectorstore = None
            print(f"Warning: Vector store not found at {self.vectorstore_path}. RAG functionality will be limited.")

    def _load_excel_template(self) -> pd.DataFrame:
        """Load the Excel template with requirements
        
        Returns:
            DataFrame containing requirements
        """
        try:
            # Load the Excel file
            df = pd.read_excel(self.excel_path)
            
            # Clean up the DataFrame
            df = df.fillna("")
            
            return df
        except Exception as e:
            raise ValueError(f"Failed to load Excel template: {str(e)}")

    def _determine_component_type(self, path: str) -> str:
        """Determine the type of component based on file path
        
        Args:
            path: Path to the component
            
        Returns:
            Component type string
        """
        if os.path.isdir(path):
            return "directory"
            
        basename = os.path.basename(path)
        dirname = os.path.dirname(path)
        
        if "modules" in dirname and path.endswith(".nf"):
            return "module"
        elif "subworkflows" in dirname and path.endswith(".nf"):
            return "subworkflow"
        elif "workflows" in dirname and path.endswith(".nf"):
            return "workflow"
        elif basename == "main.nf":
            return "main_workflow"
        elif basename == "nextflow.config":
            return "nextflow_config"
        elif basename == "nextflow_schema.json":
            return "schema_file"
        elif basename.endswith(".config"):
            return "config_file"
        elif basename in ["README.md", "CHANGELOG.md", "CITATIONS.md"]:
            return "documentation_file"
        else:
            return "other_file"

    def _get_relevant_requirements(self, component_type: str) -> List[Dict[str, Any]]:
        """Get relevant requirements from Excel template for a component type
        
        Args:
            component_type: Type of component
            
        Returns:
            List of requirement dictionaries
        """
        # Map component types to Excel template categories
        category_map = {
            "module": "Module",
            "subworkflow": "Subworkflow",
            "workflow": "Workflow",
            "main_workflow": "Workflow",
            "nextflow_config": "Configuration",
            "schema_file": "Schema",
            "config_file": "Configuration",
            "documentation_file": "Documentation",
            "other_file": None  # Will check all categories
        }
        
        category = category_map.get(component_type)
        
        # Filter requirements by category
        if category:
            filtered_df = self.requirements_df[self.requirements_df["Category"] == category]
        else:
            # For other_file, include all requirements
            filtered_df = self.requirements_df
        
        # Convert to list of dictionaries
        requirements = []
        for _, row in filtered_df.iterrows():
            if not row.get("Definition"):
                continue
                
            requirements.append({
                "id": f"{row.get('Category')}-{row.get('Subcategory')}",
                "category": row.get("Category", ""),
                "subcategory": row.get("Subcategory", ""),
                "description": row.get("Definition", ""),
                "notes": row.get("Notes", "")
            })
            
        return requirements

    def validate_component(self, component_path: str) -> Dict[str, Any]:
        """Validate a single pipeline component
        
        Args:
            component_path: Path to the component file
            
        Returns:
            Dictionary with validation results
        """
        try:
            # Determine component type
            component_type = self._determine_component_type(component_path)
            
            # Read file content
            if os.path.isdir(component_path):
                # For directories, get a listing
                code = f"Directory structure:\n"
                for root, dirs, files in os.walk(component_path, topdown=True):
                    level = root.replace(component_path, '').count(os.sep)
                    indent = ' ' * 4 * level
                    code += f"{indent}{os.path.basename(root)}/\n"
                    sub_indent = ' ' * 4 * (level + 1)
                    for f in files:
                        code += f"{sub_indent}{f}\n"
                        if len(code) > 7500:  # Avoid token limits
                            code += "... (directory listing truncated)"
                            break
            else:
                # For regular files, read content
                with open(component_path, 'r') as f:
                    code = f.read()
                    
            # Get relevant requirements from Excel
            requirements = self._get_relevant_requirements(component_type)
            
            # Check each requirement
            validation_results = []
            for req in requirements:
                # Create prompt for LLM
                prompt = self._create_validation_prompt(component_path, component_type, code, req)
                
                # Query LLM
                if self.model_provider == "anthropic":
                    response_content = self._query_anthropic(prompt)
                else:
                    # Import only when needed
                    from langchain.schema import HumanMessage
                    response = self.llm([HumanMessage(content=prompt)])
                    response_content = response.content
                
                # Parse response
                validation = self._parse_validation_response(response_content, req)
                validation_results.append(validation)
            
            # Count passed and failed requirements
            passed = sum(1 for r in validation_results if r.get("status") == "passed")
            failed = len(validation_results) - passed
            compliance_score = 0
            if len(validation_results) > 0:
                compliance_score = round((passed / len(validation_results)) * 100, 2)
            
            # Construct result dictionary
            result = {
                "component_type": component_type,
                "path": component_path,
                "requirements": validation_results,
                "summary": {
                    "passed": passed,
                    "failed": failed,
                    "compliance_score": compliance_score
                }
            }
            
            return result
            
        except Exception as e:
            return {
                "error": f"Validation failed: {str(e)}",
                "path": component_path
            }

    def _create_validation_prompt(self, component_path: str, component_type: str, 
                                 code: str, requirement: Dict[str, Any]) -> str:
        """Create a prompt for validating a single requirement
        
        Args:
            component_path: Path to the component
            component_type: Type of component
            code: Component code content
            requirement: Requirement to validate
            
        Returns:
            Validation prompt
        """
        # Find related guidelines from vector store if available
        related_guidelines = ""
        if self.vectorstore:
            try:
                search_query = f"{component_type} {requirement['category']} {requirement['subcategory']} {requirement['description']}"
                docs = self.vectorstore.similarity_search(search_query, k=2)
                related_guidelines = "\n\n".join([d.page_content for d in docs])
            except Exception as e:
                print(f"Warning: Failed to retrieve from vector store: {str(e)}")
        
        prompt = f"""You are an nf-core pipeline validator. You need to check if the following component complies with a specific requirement.

Component Path: {component_path}
Component Type: {component_type}

Component Content (limited to first 8000 chars):
```
{code[:8000]}
```

Requirement to Check:
Category: {requirement['category']}
Subcategory: {requirement['subcategory']}
Definition: {requirement['description']}
Notes: {requirement.get('notes', '')}

{f'Related Guidelines: {related_guidelines}' if related_guidelines else ''}

Task: Determine if this component PASSES or FAILS the requirement. If it fails, provide a specific fix.

Respond in this exact JSON format:
{{
  "status": "passed|failed",
  "reason": "Explanation of why it passed or failed",
  "fix": "Specific fix suggestion if failed, or N/A if passed"
}}

Be specific and precise. Focus only on the given requirement."""
        
        return prompt

    def _query_anthropic(self, prompt: str) -> str:
        """Query Claude via Anthropic API
        
        Args:
            prompt: Prompt to send
            
        Returns:
            Response content
        """
        try:
            response = self.anthropic_client.messages.create(
                model=self.anthropic_model,
                max_tokens=1000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text
        except Exception as e:
            raise ValueError(f"Error calling Anthropic API: {str(e)}")

    def _parse_validation_response(self, response: str, requirement: Dict[str, Any]) -> Dict[str, Any]:
        """Parse validation response from LLM
        
        Args:
            response: LLM response
            requirement: Original requirement
            
        Returns:
            Validation result
        """
        try:
            # Extract JSON from response (handle cases where there might be extra text)
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start >= 0 and json_end > 0:
                response_json = response[json_start:json_end]
                result = json.loads(response_json)
            else:
                # Fallback when JSON parsing fails
                result = {
                    "status": "failed",
                    "reason": "Could not parse validator response",
                    "fix": "Manual validation required"
                }
                
            # Add requirement details to result
            result["id"] = requirement["id"]
            result["description"] = requirement["description"]
            
            return result
        except Exception as e:
            # Return error result
            return {
                "id": requirement["id"],
                "description": requirement["description"],
                "status": "failed",
                "reason": f"Error parsing validation: {str(e)}",
                "fix": "Manual validation required"
            } 