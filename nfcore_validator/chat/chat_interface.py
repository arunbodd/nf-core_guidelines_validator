"""
Chat interface for querying nf-core documentation
"""
import os
from typing import List, Dict, Any, Optional

from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS

class NfCoreDocChat:
    """Chat interface for querying nf-core documentation"""
    
    def __init__(self, vectorstore_path: str = "nfcore_vectorstore", openai_api_key: str = None):
        """Initialize the chat interface
        
        Args:
            vectorstore_path: Path to the vector store with nf-core documentation
            openai_api_key: OpenAI API key for LLM and embeddings
        """
        self.openai_api_key = openai_api_key or os.environ.get("OPENAI_API_KEY")
        
        if not self.openai_api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass it directly.")
            
        self.llm = ChatOpenAI(
            temperature=0, 
            model="gpt-4",
            openai_api_key=self.openai_api_key
        )
        
        self.embeddings = OpenAIEmbeddings(openai_api_key=self.openai_api_key)
        self.vectorstore = FAISS.load_local(vectorstore_path, self.embeddings)
        
        self.system_prompt = """You are an expert on nf-core pipeline guidelines and best practices. 
Your task is to answer questions about nf-core documentation, guidelines, and requirements.
Always base your answers on the official nf-core documentation. 
If you're not sure about something, say so rather than making up information.
Include specific references to the documentation when possible."""
        
        self.chat_history = []
    
    def ask(self, question: str, k: int = 5) -> Dict[str, Any]:
        """Ask a question about nf-core documentation
        
        Args:
            question: The question to ask
            k: Number of relevant documents to retrieve
            
        Returns:
            Dictionary with answer and sources
        """
        # Retrieve relevant documents
        docs = self.vectorstore.similarity_search(question, k=k)
        
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
        
        return {
            "answer": response.content,
            "sources": sources,
            "categories": self._get_unique_categories(sources)
        }
        
    def _categorize_sources(self, docs):
        """Categorize sources by documentation section
        
        Args:
            docs: List of documents
            
        Returns:
            Dictionary with categories as keys and lists of documents as values
        """
        categorized = {}
        for doc in docs:
            source = doc.metadata.get('source', 'Unknown')
            category = self._determine_doc_category(source)
            
            if category not in categorized:
                categorized[category] = []
                
            categorized[category].append(doc)
            
        return categorized
        
    def _determine_doc_category(self, source_url):
        """Determine the category of a document based on its URL
        
        Args:
            source_url: URL of the document
            
        Returns:
            Category string
        """
        if not source_url or source_url == "Unknown":
            return "General"
            
        # Map URL patterns to categories
        category_patterns = {
            "modules": "Module Guidelines",
            "subworkflows": "Subworkflow Guidelines",
            "test_data": "Test Data Guidelines",
            "pipeline_file_structure": "Pipeline Structure",
            "pipelines/overview": "Pipeline Overview",
            "pipelines/nextflow_schema": "Nextflow Schema",
            "pipelines/linting": "Linting Guidelines",
            "pipelines/ci_testing": "CI Testing",
            "pipelines/release": "Release Guidelines"
        }
        
        for pattern, category in category_patterns.items():
            if pattern in source_url:
                return category
                
        return "Other Guidelines"
        
    def _get_unique_categories(self, sources):
        """Get unique categories from sources
        
        Args:
            sources: List of source dictionaries
            
        Returns:
            List of unique categories
        """
        return sorted(list(set(source.get("category", "Other") for source in sources)))
    
    def clear_history(self):
        """Clear chat history"""
        self.chat_history = []
