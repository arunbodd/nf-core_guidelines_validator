"""
Chat interface for nf-core documentation
"""
import os
from typing import Dict, List, Any, Optional
import json

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# Import model clients only when needed
from langchain.schema import SystemMessage, HumanMessage, AIMessage

class NfCoreDocChat:
    """Chat interface for nf-core documentation"""
    
    def __init__(self, vectorstore_path: str = "nfcore_vectorstore", openai_api_key: str = None,
                 model_provider: str = "openai", anthropic_api_key: str = None):
        """Initialize the chat interface
        
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
                
            # Import only when needed
            from langchain_community.chat_models import ChatOpenAI
            self.llm = ChatOpenAI(
                temperature=0, 
                model="gpt-4",
                openai_api_key=self.openai_api_key
            )
            
        elif self.model_provider == "anthropic":
            self.anthropic_api_key = anthropic_api_key or os.environ.get("ANTHROPIC_API_KEY")
            
            if not self.anthropic_api_key:
                raise ValueError("Anthropic API key is required for Claude models. Set ANTHROPIC_API_KEY environment variable or pass it directly.")
            
            # Import only when needed
            import anthropic
            # Create a direct Anthropic client
            print("Using direct Anthropic API integration")
            self.anthropic_client = anthropic.Anthropic(api_key=self.anthropic_api_key)
            self.anthropic_model = "claude-3-7-sonnet-20250219"
                
        else:
            raise ValueError(f"Unsupported model provider: {model_provider}. Choose from 'openai' or 'anthropic'")
        
        # Always use HuggingFace embeddings for vector search
        print(f"Loading vector store from {vectorstore_path} with HuggingFace embeddings")
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        # Load the vector store with allow_dangerous_deserialization flag
        self.vectorstore = FAISS.load_local(
            vectorstore_path, 
            self.embeddings,
            allow_dangerous_deserialization=True
        )
        
        # Initialize chat history
        self.chat_history = []
        
        # System prompt
        self.system_prompt = """You are an nf-core documentation assistant. You help users understand nf-core guidelines, best practices, and requirements for Nextflow pipelines.

Answer questions based ONLY on the provided documentation. If you don't know the answer or if it's not covered in the documentation, say so.

For each answer:
1. Be concise and accurate
2. Cite specific guidelines when relevant (e.g., "According to module guideline 2.1...")
3. Provide practical examples when helpful
4. Organize information clearly with markdown formatting

Remember that you're helping users create compliant nf-core pipelines."""
        
    def ask(self, question: str, k: int = 5, show_sources: bool = False, context_size: int = 5) -> Dict[str, Any]:
        """Ask a question about nf-core documentation
        
        Args:
            question: The question to ask
            k: Number of relevant documents to retrieve
            show_sources: Whether to include sources in the response
            context_size: Number of documents to include in the context
            
        Returns:
            Dictionary with answer and sources
        """
        # Retrieve relevant documents
        docs = self.vectorstore.similarity_search(question, k=context_size or k)
        
        # Categorize sources by documentation section
        categorized_docs = self._categorize_sources(docs)
        
        # Format context with proper source attribution and categories
        context_parts = []
        for i, doc in enumerate(docs):
            source = doc.metadata.get('source', 'Unknown source')
            category = self._determine_doc_category(source)
            content = doc.page_content
            context_parts.append(f"Source ({i+1}) - {category} - {source}:\n{content}")
        
        context = "\n\n".join(context_parts)
        
        # Prepare chat history and new question
        messages = [SystemMessage(content=self.system_prompt)]
        
        # Add chat history for context
        for msg in self.chat_history[-3:]:  # Only use last 3 exchanges to avoid token limits
            messages.append(msg)
        
        # Add the new question with context
        query_with_context = f"""
        Question: {question}
        
        Relevant Documentation:
        {context}
        
        Please answer the question based on the provided documentation.
        Structure your answer by categories when information comes from different sections of the documentation.
        For each piece of information, mention which source and category it comes from.
        """
        messages.append(HumanMessage(content=query_with_context))
        
        # Get response
        if self.model_provider == "anthropic":
            # Use the custom method for calling the Anthropic API
            response = self._call_anthropic_api(messages)
        else:
            response = self.llm(messages)
        
        # Update chat history
        self.chat_history.append(HumanMessage(content=question))
        self.chat_history.append(response)
        
        # Extract sources with better metadata and categories
        sources = []
        for doc in docs:
            source_url = doc.metadata.get("source", "Unknown")
            category = self._determine_doc_category(source_url)
            sources.append({
                "content": doc.page_content,
                "source": source_url,
                "url": doc.metadata.get("url", source_url),
                "category": category
            })
        
        # Format the answer based on whether to show sources
        answer_text = response.content
        if show_sources:
            # Group sources by category
            categorized_sources = {}
            for source in sources:
                category = source["category"]
                if category not in categorized_sources:
                    categorized_sources[category] = []
                categorized_sources[category].append(source)
            
            # Add formatted sources to the answer
            answer_text += "\n\n## Sources\n"
            for category, category_sources in categorized_sources.items():
                answer_text += f"\n### {category}\n"
                for i, source in enumerate(category_sources):
                    answer_text += f"- **Source {i+1}:** {source['source']}\n"
                    if len(source['content']) > 200:
                        answer_text += f"  {source['content'][:200]}...\n"
                    else:
                        answer_text += f"  {source['content']}\n"
        
        return answer_text if show_sources else response.content
        
    def _call_anthropic_api(self, messages):
        """Call the Anthropic API directly
        
        Args:
            messages: List of LangChain message objects
            
        Returns:
            AIMessage with the response content
        """
        # Extract system message
        system_content = ""
        for msg in messages:
            if isinstance(msg, SystemMessage):
                system_content = msg.content
                break
        
        # Extract human and AI messages
        human_ai_messages = []
        for msg in messages:
            if isinstance(msg, HumanMessage):
                human_ai_messages.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                human_ai_messages.append({"role": "assistant", "content": msg.content})
        
        try:
            # Call Anthropic API
            response = self.anthropic_client.messages.create(
                model=self.anthropic_model,
                max_tokens=4000,
                system=system_content,
                messages=human_ai_messages
            )
            
            # Convert to LangChain AIMessage
            return AIMessage(content=response.content[0].text)
        except Exception as e:
            # Return error message
            return AIMessage(content=f"Error: {str(e)}")
            
    def _categorize_sources(self, docs):
        """Categorize sources by documentation section
        
        Args:
            docs: List of documents
            
        Returns:
            Dictionary of categorized documents
        """
        categorized = {}
        
        for doc in docs:
            source = doc.metadata.get('source', 'Unknown')
            category = self._determine_doc_category(source)
            
            if category not in categorized:
                categorized[category] = []
                
            categorized[category].append({
                "content": doc.page_content,
                "source": source
            })
            
        return categorized
            
    def _determine_doc_category(self, source_url):
        """Determine the category of a document based on its source URL
        
        Args:
            source_url: Source URL of the document
            
        Returns:
            Category string
        """
        if not source_url or source_url == "Unknown":
            return "Other"
            
        # Check for Excel source
        if source_url.startswith("excel_template:"):
            return "Excel Guidelines"
            
        # Extract category from URL
        url_parts = source_url.split("/")
        
        # Identify modules
        if "components/modules" in source_url:
            return "Modules"
        elif "components/subworkflows" in source_url:
            return "Subworkflows"
        elif "components/test_data" in source_url:
            return "Test Data"
        elif "pipeline_file_structure" in source_url:
            return "Pipeline Structure"
        elif "pipelines" in source_url:
            return "Pipeline Guidelines"
        elif "components" in source_url:
            return "Component Guidelines"
        else:
            return "General Guidelines"
            
    def _get_unique_categories(self, sources):
        """Get unique categories from sources
        
        Args:
            sources: List of source dictionaries
            
        Returns:
            List of unique categories
        """
        categories = set()
        for source in sources:
            categories.add(source.get("category", "Other"))
            
        return list(categories)
        
    def clear_history(self):
        """Clear chat history"""
        self.chat_history = []
        return "Chat history cleared."
