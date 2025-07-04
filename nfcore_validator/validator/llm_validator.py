"""
LLM-based validator for nf-core pipeline components
"""
import os
import json
from typing import Dict, Any, List, Optional
import re

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import anthropic  # Direct Anthropic API client

class NfCoreValidator:
    """LLM-based validator for nf-core pipeline components"""
    
    def __init__(self, vectorstore_path: str = "nfcore_vectorstore", anthropic_api_key: str = None):
        """Initialize the validator with Anthropic Claude 4 Opus
        
        Args:
            vectorstore_path: Path to the vector store with nf-core documentation
            anthropic_api_key: Anthropic API key for Claude models (required)
        """
        # Token usage tracking
        self.total_tokens_used = 0
        self.total_requests = 0
        
        # Initialize Anthropic client
        self.anthropic_api_key = anthropic_api_key or os.environ.get("ANTHROPIC_API_KEY")
        
        if not self.anthropic_api_key:
            raise ValueError("Anthropic API key is required. Set ANTHROPIC_API_KEY environment variable or pass it directly.")
        
        self.anthropic_model = "claude-opus-4-20250514"  # Claude 4 Opus model
        self.anthropic_client = anthropic.Anthropic(api_key=self.anthropic_api_key)
        
        print(f"🤖 Using Anthropic model: {self.anthropic_model}")
        
        # Always use HuggingFace embeddings for vectorstore
        print(f"Loading vector store from {vectorstore_path} with HuggingFace embeddings")
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        # Load the vector store with allow_dangerous_deserialization flag
        self.vectorstore = FAISS.load_local(
            vectorstore_path, 
            self.embeddings, 
            allow_dangerous_deserialization=True
        )
        
        self.system_prompt = """You are an expert nf-core pipeline validator. Your task is to analyze pipeline components and check them against ONLY the relevant nf-core guidelines for that specific component type.

IMPORTANT: You must respond with a valid JSON object only. Do not include any text before or after the JSON.

CRITICAL: Only apply guidelines that are relevant to the specific component type:
- For modules (.nf files in modules/): Apply ONLY module-specific requirements (naming, I/O, documentation, etc.)
- For subworkflows (.nf files in subworkflows/): Apply ONLY subworkflow guidelines  
- For workflows (.nf files in workflows/): Apply ONLY workflow standards
- For main.nf files: Apply ONLY main workflow/pipeline requirements
- For config files (*.config): Apply ONLY configuration standards
- For documentation files (README.md, CHANGELOG.md): Apply ONLY documentation requirements
- For test data: Apply ONLY test data requirements

DO NOT apply workflow requirements to modules, or module requirements to config files, etc.

Follow these steps:
1. Identify the component type based on file path and name
2. Check ONLY against guidelines that are specifically relevant to that component type
3. Ignore any guidelines that don't apply to this component type
4. For each relevant requirement, determine if it passes or fails
5. For failed requirements, provide specific fixes

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

Be thorough and check against ALL relevant nf-core requirements for the component type. Ensure your response is a valid JSON object."""

    def validate_component(self, component_path: str) -> Dict[str, Any]:
        """Validate a single pipeline component
        
        Args:
            component_path: Path to the component file
            
        Returns:
            Dictionary with validation results
        """
        print(f"🔍 Starting validation of: {component_path}")
        
        try:
            # Determine file type for specialized handling
            file_type = self._determine_component_type(component_path)
            print(f"   Component type detected: {file_type}")
            
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
                print(f"   File content length: {len(code)} characters")
        except Exception as e:
            print(f"   ❌ Error reading file: {str(e)}")
            return {
                "error": f"Failed to read file: {str(e)}",
                "path": component_path
            }
        
        print(f"   📚 Searching vectorstore for relevant guidelines for {file_type}...")
        
        # Define component type to category mapping based on Excel structure
        component_category_mapping = {
            "module": ["module", "modules", "general"],
            "subworkflow": ["subworkflow", "subworkflows", "general"], 
            "workflow": ["workflow", "workflows", "general", "pipeline"],
            "main_workflow": ["workflow", "workflows", "pipeline", "general"],
            "nextflow_config": ["config", "configuration", "pipeline", "general"],
            "config_file": ["config", "configuration", "general"],
            "schema_file": ["schema", "pipeline", "general"],
            "documentation_file": ["documentation", "docs", "readme", "general"],
            "test_data": ["test", "testing", "test_data", "general"],
            "other_file": ["general", "pipeline"]
        }
        
        # Get relevant categories for this component type
        relevant_categories = component_category_mapping.get(file_type, ["general"])
        
        print(f"   🎯 Looking for guidelines in categories: {relevant_categories}")
        
        # Use targeted search strategies with category filtering
        all_docs = []
        
        # Search 1: Direct category-based search
        for category in relevant_categories:
            category_docs = self.vectorstore.similarity_search(
                f"{category} requirements guidelines standards", 
                k=20  # Reduced from 50 to get more focused results
            )
            # Filter by metadata if available
            filtered_docs = []
            for doc in category_docs:
                doc_category = doc.metadata.get('category', '').lower()
                doc_subcategory = doc.metadata.get('subcategory', '').lower()
                
                # Check if document category matches component type
                if (any(cat.lower() in doc_category for cat in relevant_categories) or
                    any(cat.lower() in doc_subcategory for cat in relevant_categories) or
                    category.lower() in doc_category or
                    category.lower() in doc_subcategory):
                    filtered_docs.append(doc)
            
            all_docs.extend(filtered_docs[:10])  # Limit to top 10 per category
        
        # Search 2: Component-specific search (only if we have few results)
        if len(all_docs) < 15:
            specific_docs = self.vectorstore.similarity_search(
                f"nf-core {file_type} validation requirements", 
                k=15
            )
            all_docs.extend(specific_docs)
        
        # Search 3: Filename-based search (only for specific file types)
        filename = os.path.basename(component_path)
        if filename in ['main.nf', 'nextflow.config', 'nextflow_schema.json', 'README.md']:
            filename_docs = self.vectorstore.similarity_search(
                f"{filename} requirements standards", 
                k=10
            )
            all_docs.extend(filename_docs)
        
        # Remove duplicates while preserving order and relevance
        seen = set()
        unique_docs = []
        for doc in all_docs:
            # Use a more robust deduplication key
            doc_key = hash(doc.page_content[:200])  # Hash first 200 chars
            if doc_key not in seen:
                seen.add(doc_key)
                unique_docs.append(doc)
        
        # Instead of limiting documents, limit the content length per document
        # This allows us to use ALL relevant guidelines while staying within token limits
        guidelines_parts = []
        total_chars = 0
        max_total_chars = 15000  # Allow more comprehensive guidelines
        
        for doc in unique_docs:
            # Extract key parts of each guideline (first 300 chars which usually contain the main rule)
            doc_content = doc.page_content[:300] + "..." if len(doc.page_content) > 300 else doc.page_content
            
            # Check if adding this would exceed our limit
            if total_chars + len(doc_content) > max_total_chars:
                break
                
            guidelines_parts.append(doc_content)
            total_chars += len(doc_content)
        
        guidelines = "\n---\n".join(guidelines_parts)  # Use separator for clarity
        
        print(f"   Found {len(unique_docs)} unique guideline documents")
        print(f"   Using {len(guidelines_parts)} guidelines ({total_chars:,} chars) for comprehensive validation")
        
        # Debug: Show what types of guidelines were retrieved
        if unique_docs:
            doc_sources = [doc.metadata.get('source', 'unknown') for doc in unique_docs[:10] if hasattr(doc, 'metadata')]
            print(f"   📋 Top guideline sources: {doc_sources[:5]}...")  # Show first 5 sources
        
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
        
        print(f"   🤖 Querying Anthropic Claude 4 Opus model...")
        # Query Anthropic LLM
        response_content = self._query_anthropic(self.system_prompt, prompt)
        
        print(f"   📝 Received response, parsing JSON...")
        # Parse response
        try:
            result = json.loads(response_content)
            result["path"] = component_path  # Ensure path is included
            result["component_type"] = file_type  # Add component type for reporting
            
            # Add metadata from retrieved documents to each requirement
            if 'requirements' in result:
                for req in result['requirements']:
                    # Find the most relevant document for this requirement
                    req_id = req.get('id', '')
                    req_desc = req.get('description', '')
                    
                    # Match requirement to document based on content similarity
                    best_match_doc = None
                    best_score = 0
                    
                    for doc in unique_docs:
                        # Simple matching based on keyword overlap
                        doc_content = doc.page_content.lower()
                        req_content = (req_id + ' ' + req_desc).lower()
                        
                        # Count common words
                        doc_words = set(doc_content.split())
                        req_words = set(req_content.split())
                        common_words = doc_words.intersection(req_words)
                        
                        if len(common_words) > best_score:
                            best_score = len(common_words)
                            best_match_doc = doc
                    
                    # Add metadata from best matching document
                    if best_match_doc and hasattr(best_match_doc, 'metadata'):
                        req['classification'] = best_match_doc.metadata.get('classification', '')
                        req['category'] = best_match_doc.metadata.get('category', '')
                        req['subcategory'] = best_match_doc.metadata.get('subcategory', '')
                    else:
                        req['classification'] = ''
                        req['category'] = ''
                        req['subcategory'] = ''
            
            print(f"   ✅ Successfully validated component")
            
            # Apply rule-based validation overrides
            result = self._apply_rule_based_validation(component_path, file_type, result)
            
            return result
        except json.JSONDecodeError as e:
            print(f"   ❌ Failed to parse LLM response as JSON: {str(e)}")
            print(f"   📄 Raw response (first 500 chars): {response_content[:500]}")
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
            print(f"Querying Anthropic API with model: {self.anthropic_model}")
            with self.anthropic_client.messages.stream(
                model=self.anthropic_model,
                max_tokens=4000,
                temperature=0,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            ) as stream:
                response_text = ""
                for text in stream.text_stream:
                    response_text += text
                
                # Track usage for Anthropic (approximate token count)
                self.total_requests += 1
                # Rough token estimation (4 chars per token average)
                estimated_tokens = (len(system_prompt) + len(user_prompt) + len(response_text)) // 4
                self.total_tokens_used += estimated_tokens
                
                print(f"📊 Request #{self.total_requests} - Estimated tokens: ~{estimated_tokens}")
                print(f"📈 Running total: ~{self.total_tokens_used} tokens across {self.total_requests} requests")
                print(f"Received response length: {len(response_text)}")
                
                return response_text
        except Exception as e:
            print(f"Error querying Anthropic API: {str(e)}")
            print(f"Exception type: {type(e).__name__}")
            raise
    
    def _apply_rule_based_validation(self, component_path: str, file_type: str, llm_result: dict) -> dict:
        """Apply rule-based validation to correct LLM false positives/negatives"""
        
        # Define path-based rules that can be checked programmatically
        path_rules = {
            # General pipeline requirements - fundamental files every pipeline must have
            "pipeline_general_main_nf": {
                "applies_to": ["workflow", "main_workflow", "general"],
                "rule": lambda path: (
                    path.endswith("/main.nf") and 
                    # Should be at pipeline root
                    path.count("/") <= 3
                ),
                "description": "Pipeline must have a main.nf file at the root directory"
            },
            
            "pipeline_general_nextflow_config": {
                "applies_to": ["nextflow_config", "config_file", "general"],
                "rule": lambda path: (
                    path.endswith("/nextflow.config") and 
                    # Should be at pipeline root
                    path.count("/") <= 3
                ),
                "description": "Pipeline must have a nextflow.config file at the root directory"
            },
            
            "pipeline_general_readme": {
                "applies_to": ["documentation_file", "general"],
                "rule": lambda path: (
                    path.endswith("/README.md") and 
                    # Should be at pipeline root
                    path.count("/") <= 3
                ),
                "description": "Pipeline must have a README.md file at the root directory"
            },
            
            "pipeline_general_schema": {
                "applies_to": ["schema_file", "general"],
                "rule": lambda path: (
                    path.endswith("/nextflow_schema.json") and 
                    # Should be at pipeline root
                    path.count("/") <= 3
                ),
                "description": "Pipeline must have a nextflow_schema.json file at the root directory"
            },
            
            "pipeline_general_changelog": {
                "applies_to": ["documentation_file", "general"],
                "rule": lambda path: (
                    path.endswith("/CHANGELOG.md") and 
                    # Should be at pipeline root
                    path.count("/") <= 3
                ),
                "description": "Pipeline must have a CHANGELOG.md file at the root directory"
            },
            
            "pipeline_general_license": {
                "applies_to": ["documentation_file", "general"],
                "rule": lambda path: (
                    path.endswith("/LICENSE") and 
                    # Should be at pipeline root
                    path.count("/") <= 3
                ),
                "description": "Pipeline must have a LICENSE file at the root directory"
            },
            
            "pipeline_general_code_of_conduct": {
                "applies_to": ["documentation_file", "general"],
                "rule": lambda path: (
                    (path.endswith("/CODE_OF_CONDUCT.md") or path.endswith("/code-of-conduct.md")) and 
                    # Should be at pipeline root
                    path.count("/") <= 3
                ),
                "description": "Pipeline must have a CODE_OF_CONDUCT.md file at the root directory"
            },
            
            "pipeline_general_citations": {
                "applies_to": ["documentation_file", "general"],
                "rule": lambda path: (
                    path.endswith("/CITATIONS.md") and 
                    # Should be at pipeline root
                    path.count("/") <= 3
                ),
                "description": "Pipeline should have a CITATIONS.md file at the root directory"
            },
            
            # Module-specific rules
            "module_general_storage": {
                "applies_to": ["module"],
                "rule": lambda path: (
                    "/modules/" in path and path.endswith("/main.nf")
                ) or (
                    # Allow local modules but they should still follow structure
                    "/modules/local/" in path and path.endswith(".nf")
                ),
                "description": "Modules should be stored in the modules dir, and local modules should follow the same dir structure and naming conventions as nf-core modules"
            },
            "module_naming_conventions": {
                "applies_to": ["module"],
                "rule": lambda path: (
                    # Standard nf-core modules: modules/nf-core/tool/subtool/main.nf
                    bool(re.match(r'.*/modules/[^/]+/[a-z0-9_]+(/[a-z0-9_]+)?/main\.nf$', path)) or
                    # Local modules: modules/local/toolname.nf
                    bool(re.match(r'.*/modules/local/[a-z0-9_]+\.nf$', path))
                ),
                "description": "Directory structure for the module name must be all lowercase, and without punctuation"
            },
            
            # Subworkflow-specific rules
            "subworkflow_storage": {
                "applies_to": ["subworkflow"],
                "rule": lambda path: "/subworkflows/" in path and path.endswith("/main.nf"),
                "description": "Subworkflows should be stored in the subworkflows directory"
            },
            
            # Workflow-specific rules
            "workflow_storage": {
                "applies_to": ["workflow", "main_workflow"],
                "rule": lambda path: (
                    path.endswith("/main.nf") and "/workflows/" in path
                ) or (
                    # Main workflow can be at root
                    path.endswith("/main.nf") and path.count("/") <= 3
                ),
                "description": "Workflows should be in workflows directory or main.nf at pipeline root"
            },
            
            # Config file rules
            "config_location": {
                "applies_to": ["nextflow_config"],
                "rule": lambda path: (
                    path.endswith("/nextflow.config") and 
                    # Should be at pipeline root or in conf/ directory
                    (path.count("/") <= 3 or "/conf/" in path)
                ),
                "description": "nextflow.config should be at pipeline root or in conf/ directory"
            },
            
            # Documentation rules
            "readme_location": {
                "applies_to": ["documentation_file"],
                "rule": lambda path: (
                    # README should be at pipeline root
                    (path.endswith("/README.md") and path.count("/") <= 3) or
                    # Or in docs/ directory
                    ("/docs/" in path and path.endswith(".md")) or
                    # Other docs can be anywhere
                    not path.endswith("/README.md")
                ),
                "description": "README.md should be at pipeline root, other docs can be in docs/ directory"
            },
            
            # Schema file rules
            "schema_location": {
                "applies_to": ["schema_file"],
                "rule": lambda path: (
                    path.endswith("/nextflow_schema.json") and 
                    # Should be at pipeline root
                    path.count("/") <= 3
                ),
                "description": "nextflow_schema.json should be at pipeline root"
            },
            
            # Test data rules
            "test_data_location": {
                "applies_to": ["test_data"],
                "rule": lambda path: (
                    "/test" in path.lower() or 
                    "/data" in path.lower() or
                    "/assets" in path.lower()
                ),
                "description": "Test data should be in test/, data/, or assets/ directories"
            },
            
            # General pipeline structure rules
            "pipeline_structure_compliance": {
                "applies_to": ["module", "subworkflow", "workflow", "main_workflow", "nextflow_config", "schema_file"],
                "rule": lambda path: (
                    # Check if this looks like a standard nf-core structure
                    any(standard_dir in path for standard_dir in [
                        "/modules/", "/subworkflows/", "/workflows/", "/conf/", "/bin/", "/lib/"
                    ]) or
                    # Or if it's a main pipeline file at root
                    (path.endswith("/main.nf") and path.count("/") <= 3) or
                    (path.endswith("/nextflow.config") and path.count("/") <= 3) or
                    (path.endswith("/nextflow_schema.json") and path.count("/") <= 3)
                ),
                "description": "Components should follow nf-core pipeline directory structure"
            }
        }
        
        # Get pipeline root to help with structure validation
        pipeline_root = self._get_pipeline_root(component_path)
        
        # Check each requirement in the LLM result
        if "requirements" in llm_result:
            for req in llm_result["requirements"]:
                req_id = req.get("id", "")
                
                # Apply rule-based validation if we have a rule for this requirement
                if req_id in path_rules:
                    rule_info = path_rules[req_id]
                    
                    # Check if this rule applies to this component type
                    if file_type in rule_info["applies_to"]:
                        # Apply the rule
                        rule_passes = rule_info["rule"](component_path)
                        
                        # Override LLM result if it conflicts with rule-based result
                        original_status = req["status"]
                        new_status = "passed" if rule_passes else "failed"
                        
                        if original_status != new_status:
                            print(f"   🔧 Rule-based override for {req_id}: {original_status} → {new_status}")
                            req["status"] = new_status
                            
                            if new_status == "failed":
                                req["fix"] = f"Path validation failed: {rule_info['description']}. Current path: {component_path}"
                            else:
                                req["fix"] = None
                
                # Special handling for structure-related requirements
                elif any(keyword in req_id.lower() for keyword in ["structure", "location", "directory", "storage"]):
                    # This is likely a structure requirement - be more conservative
                    if req["status"] == "passed" and not self._looks_like_nfcore_structure(component_path):
                        print(f"   ⚠️  Structure requirement {req_id} marked as passed but path doesn't follow nf-core conventions")
                        print(f"      Path: {component_path}")
                        # Don't auto-override these - just warn for now
        
        # Recalculate summary after rule-based corrections
        if "requirements" in llm_result:
            passed = sum(1 for req in llm_result["requirements"] if req["status"] == "passed")
            failed = sum(1 for req in llm_result["requirements"] if req["status"] == "failed")
            total = passed + failed
            
            llm_result["summary"] = {
                "passed": passed,
                "failed": failed,
                "compliance_score": round((passed / total * 100) if total > 0 else 0, 2)
            }
        
        return llm_result
    
    def _get_pipeline_root(self, component_path: str) -> str:
        """Try to determine the pipeline root directory"""
        # Look for common pipeline indicators going up the directory tree
        path_parts = component_path.split("/")
        for i in range(len(path_parts) - 1, 0, -1):
            potential_root = "/".join(path_parts[:i])
            # Check if this directory contains pipeline indicators
            if any(indicator in os.listdir(potential_root) if os.path.exists(potential_root) else [] 
                   for indicator in ["main.nf", "nextflow.config", "nextflow_schema.json"]):
                return potential_root
        return "/".join(path_parts[:-1])  # Fallback to parent directory
    
    def _looks_like_nfcore_structure(self, component_path: str) -> bool:
        """Check if the component path follows nf-core conventions"""
        return any(standard_dir in component_path for standard_dir in [
            "/modules/", "/subworkflows/", "/workflows/", "/conf/", "/bin/", "/lib/", "/docs/"
        ]) or (
            # Or main files at root level
            component_path.endswith(("/main.nf", "/nextflow.config", "/nextflow_schema.json")) 
            and component_path.count("/") <= 3
        )
    
    def get_usage_summary(self):
        """Get a summary of token usage and costs for Anthropic Claude 4 Opus"""
        # Claude 4 Opus pricing: roughly $15 per 1M input tokens, $75 per 1M output tokens
        # Using average of $45 per 1M tokens for estimation
        estimated_cost = (self.total_tokens_used / 1_000_000) * 45.0
        return {
            "model": self.anthropic_model,
            "total_requests": self.total_requests,
            "total_tokens_estimated": self.total_tokens_used,
            "estimated_cost_usd": round(estimated_cost, 4)
        }
        
    def print_usage_summary(self):
        """Print a formatted usage summary"""
        summary = self.get_usage_summary()
        print("\n" + "="*50)
        print("🏁 VALIDATION COMPLETE - USAGE SUMMARY")
        print("="*50)
        print(f"Model: {summary.get('model', 'Unknown')}")
        print(f"Total Requests: {summary['total_requests']}")
        if 'total_tokens' in summary:
            print(f"Total Tokens: {summary['total_tokens']:,}")
        else:
            print(f"Total Tokens (estimated): {summary['total_tokens_estimated']:,}")
        print(f"Estimated Cost: ${summary['estimated_cost_usd']:.4f} USD")
        print("="*50)
    
    def _determine_component_type(self, path: str) -> str:
        """Determine the type of component based on path
        
        Args:
            path: Path to the component
            
        Returns:
            Component type string
        """
        if os.path.isdir(path):
            if 'test_data' in path.lower() or path.endswith('/tests'):
                return "test_data"
            return "directory"
            
        filename = os.path.basename(path)
        path_lower = path.lower()
        
        # Check for specific file types first
        if filename == 'main.nf':
            if '/modules/' in path or '/local/' in path:
                return "module"
            else:
                return "main_workflow"
        elif filename == 'nextflow.config':
            return "nextflow_config"
        elif filename.endswith('.config'):
            return "config_file"
        elif filename == 'nextflow_schema.json':
            return "schema_file"
        elif filename in ['README.md', 'CHANGELOG.md', 'CITATIONS.md', 'LICENSE']:
            return "documentation_file"
        
        # For .nf files, be more inclusive in classification
        elif filename.endswith('.nf'):
            if '/modules/' in path:
                return "module"
            elif '/subworkflows/' in path:
                return "subworkflow"
            elif '/workflows/' in path:
                return "workflow"
            elif '/local/' in path:
                return "module"  # Local modules
            elif 'test' in path_lower:
                return "test_data"
            else:
                # Any other .nf file is likely a module or workflow component
                return "module"  # Default .nf files to module for validation
        else:
            return "other_file"
