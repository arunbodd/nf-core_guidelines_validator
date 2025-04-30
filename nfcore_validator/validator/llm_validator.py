"""
LLM-based validator for nf-core pipeline components
"""
import os
import json
from typing import Dict, Any, List, Optional

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# Import model clients only when needed
from langchain_community.chat_models import ChatOpenAI, ChatAnthropic
import anthropic  # Direct import of the anthropic library

class NfCoreValidator:
    """LLM-based validator for nf-core pipeline components"""
    
    def __init__(self, vectorstore_path: str = "nfcore_vectorstore", openai_api_key: str = None, 
                 model_provider: str = "openai", anthropic_api_key: str = None):
        """Initialize the validator
        
        Args:
            vectorstore_path: Path to the vector store with nf-core documentation
            openai_api_key: OpenAI API key for LLM (required only if model_provider is 'openai')
            model_provider: Which model provider to use ('openai' or 'anthropic')
            anthropic_api_key: Anthropic API key for Claude models (required only if model_provider is 'anthropic')
        """
        self.model_provider = model_provider.lower()
        self.llm = None
        self.anthropic_client = None
        
        # Set up the appropriate model based on provider
        if self.model_provider == "openai":
            self.openai_api_key = openai_api_key or os.environ.get("OPENAI_API_KEY")
            
            if not self.openai_api_key:
                raise ValueError("OpenAI API key is required for OpenAI models. Set OPENAI_API_KEY environment variable or pass it directly.")
                
            self.llm = ChatOpenAI(
                temperature=0, 
                model="gpt-4",
                openai_api_key=self.openai_api_key
            )
            
        elif self.model_provider == "anthropic":
            self.anthropic_api_key = anthropic_api_key or os.environ.get("ANTHROPIC_API_KEY")
            
            if not self.anthropic_api_key:
                raise ValueError("Anthropic API key is required for Claude models. Set ANTHROPIC_API_KEY environment variable or pass it directly.")
            
            # Create a direct Anthropic client
            print("Using direct Anthropic API integration")
            self.anthropic_client = anthropic.Anthropic(api_key=self.anthropic_api_key)
            
            # Use the correct Claude model name
            self.anthropic_model = "claude-3-7-sonnet-20250219"
                
        else:
            raise ValueError(f"Unsupported model provider: {model_provider}. Choose from 'openai' or 'anthropic'")
        
        # Always use HuggingFace embeddings for vectorstore
        print(f"Loading vector store from {vectorstore_path} with HuggingFace embeddings")
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        # Load the vector store with allow_dangerous_deserialization flag
        self.vectorstore = FAISS.load_local(
            vectorstore_path, 
            self.embeddings, 
            allow_dangerous_deserialization=True
        )
        
        self.system_prompt = """You are an nf-core pipeline compliance expert. Your task is to analyze the provided pipeline component against the official nf-core guidelines.

Follow these steps:
1. Identify the component type (module, workflow, subworkflow, pipeline file, config file, test data)
2. Check the component against all relevant nf-core requirements
3. For each requirement, determine if it passes or fails
4. For failed requirements, provide specific fixes

For modules, check against module specifications (naming, I/O, documentation, etc.)
For subworkflows, check against subworkflow guidelines
For workflows, check against workflow standards
For pipeline files, check against pipeline structure requirements
For config files, check against configuration standards
For test data, check against test data requirements

Return your analysis in this exact JSON format:
{
  "component_type": "module|workflow|subworkflow|pipeline_file|config_file|test_data",
  "path": "original_path",
  "requirements": [
    {
      "id": "requirement_id",
      "description": "requirement_description",
      "status": "passed|failed",
      "fix": "suggestion_if_failed"
    }
  ],
  "summary": {
    "passed": number_of_passed_requirements,
    "failed": number_of_failed_requirements,
    "compliance_score": percentage_score
  }
}

Be thorough and check against ALL relevant nf-core requirements for the component type."""

    def validate_component(self, component_path: str) -> Dict[str, Any]:
        """Validate a single pipeline component
        
        Args:
            component_path: Path to the component file
            
        Returns:
            Dictionary with validation results
        """
        try:
            # Determine file type for specialized handling
            file_type = self._determine_component_type(component_path)
            
            # Read file content
            if os.path.isdir(component_path):
                # For directories (like test directories), get a listing
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
        except Exception as e:
            return {
                "error": f"Failed to read file: {str(e)}",
                "path": component_path
            }
        
        # Get relevant guidelines from vector store
        docs = self.vectorstore.similarity_search(
            f"{file_type} {os.path.basename(component_path)} {code[:500]}", 
            k=5
        )
        guidelines = "\n".join([d.page_content for d in docs])
        
        # Prepare prompt for LLM
        prompt = f"""
        Component Path: {component_path}
        Component Type: {file_type}
        
        Component Content:
        ```
        {code[:8000]}  # Limit code size to avoid token limits
        ```
        
        Relevant Guidelines:
        {guidelines}
        """
        
        # Query LLM based on provider
        if self.model_provider == "anthropic":
            response_content = self._query_anthropic(self.system_prompt, prompt)
        else:
            # Use standard LangChain interface for OpenAI
            from langchain.schema import SystemMessage, HumanMessage
            response = self.llm([
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=prompt)
            ])
            response_content = response.content
        
        # Parse response
        try:
            result = json.loads(response_content)
            result["path"] = component_path  # Ensure path is included
            result["component_type"] = file_type  # Add component type for reporting
            return result
        except json.JSONDecodeError:
            return {
                "error": "Failed to parse LLM response as JSON",
                "raw_response": response_content,
                "path": component_path,
                "component_type": file_type
            }
    
    def _query_anthropic(self, system_prompt, user_prompt):
        """Call the Anthropic API with the given prompts
        
        Args:
            system_prompt: System prompt
            user_prompt: User prompt
            
        Returns:
            Response content as string
        """
        try:
            response = self.anthropic_client.messages.create(
                model=self.anthropic_model,
                max_tokens=4000,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            return response.content[0].text
        except Exception as e:
            raise ValueError(f"Error calling Anthropic API: {str(e)}")

    def _determine_component_type(self, path: str) -> str:
        """Determine the type of component based on path
        
        Args:
            path: Path to the component
            
        Returns:
            Component type string
        """
        if os.path.isdir(path):
            if path.endswith('/tests'):
                return "test_data"
            return "directory"
            
        filename = os.path.basename(path)
        if '/modules/' in path and filename == 'main.nf':
            return "module"
        elif '/subworkflows/' in path and filename.endswith('.nf'):
            return "subworkflow"
        elif '/workflows/' in path and filename.endswith('.nf'):
            return "workflow"
        elif filename == 'main.nf':
            return "main_workflow"
        elif filename == 'nextflow.config':
            return "nextflow_config"
        elif filename.endswith('.config'):
            return "config_file"
        elif filename == 'nextflow_schema.json':
            return "schema_file"
        elif filename in ['README.md', 'CHANGELOG.md', 'CITATIONS.md', 'LICENSE']:
            return "documentation_file"
        else:
            return "other_file"
