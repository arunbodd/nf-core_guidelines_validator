"""
Documentation harvester for nf-core guidelines
"""
import os
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any

from langchain.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS

class NfCoreDocsHarvester:
    """Harvests nf-core documentation and creates a vector store for retrieval"""
    
    def __init__(self, openai_api_key: str = None):
        """Initialize the harvester
        
        Args:
            openai_api_key: OpenAI API key for embeddings
        """
        self.base_url = "https://nf-co.re/docs/guidelines/components"
        self.docs_dir = "nfcore_docs"
        self.openai_api_key = openai_api_key or os.environ.get("OPENAI_API_KEY")
        
        if not self.openai_api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass it directly.")
            
        os.makedirs(self.docs_dir, exist_ok=True)

    def _get_all_doc_urls(self) -> List[str]:
        """Extract all guideline URLs from the overview page"""
        response = requests.get(f"{self.base_url}/overview")
        soup = BeautifulSoup(response.text, 'html.parser')
        
        urls = []
        # Find all links to guidelines
        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.startswith('/docs/guidelines/components') or href.startswith('/docs/contributing/pipelines'):
                urls.append(f"https://nf-co.re{href}")
        
        # Add core URLs if they weren't found
        core_urls = [
            f"{self.base_url}/overview",
            f"{self.base_url}/modules",
            f"{self.base_url}/subworkflows",
            f"{self.base_url}/test_data",
            "https://nf-co.re/docs/contributing/pipelines/pipeline_file_structure",
            "https://nf-co.re/docs/guidelines/pipelines/overview",
            "https://nf-co.re/docs/guidelines/pipelines/nextflow_schema",
            "https://nf-co.re/docs/guidelines/pipelines/linting",
            "https://nf-co.re/docs/guidelines/pipelines/ci_testing",
            "https://nf-co.re/docs/guidelines/pipelines/release_checklist",
            "https://nf-co.re/docs/guidelines/pipelines/pipeline_file_structure"
        ]
        
        # Also crawl pipeline guidelines section
        try:
            pipeline_response = requests.get("https://nf-co.re/docs/guidelines/pipelines/overview")
            pipeline_soup = BeautifulSoup(pipeline_response.text, 'html.parser')
            for link in pipeline_soup.find_all('a', href=True):
                href = link['href']
                if href.startswith('/docs/guidelines/pipelines'):
                    pipeline_url = f"https://nf-co.re{href}"
                    if pipeline_url not in urls and pipeline_url not in core_urls:
                        core_urls.append(pipeline_url)
        except Exception as e:
            print(f"Warning: Could not crawl pipeline guidelines: {str(e)}")
        
        # Combine all URLs
        all_urls = urls + core_urls
        
        return list(set(all_urls))  # Remove duplicates

    def harvest(self, vectorstore_path: str = "nfcore_vectorstore") -> FAISS:
        """Harvest documentation and create vector store
        
        Args:
            vectorstore_path: Path to save the vector store
            
        Returns:
            FAISS vector store with document embeddings
        """
        print("Harvesting nf-core documentation...")
        urls = self._get_all_doc_urls()
        print(f"Found {len(urls)} documentation pages to process")
        
        # Use WebBaseLoader with metadata
        loader = WebBaseLoader(urls)
        loader.requests_kwargs = {'timeout': 10}
        
        # Add metadata to documents
        docs = loader.load()
        for doc in docs:
            if not doc.metadata.get('source'):
                doc.metadata['source'] = doc.metadata.get('url', 'Unknown')
        
        print(f"Loaded {len(docs)} documents")
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        splits = text_splitter.split_documents(docs)
        
        # Ensure each split has source metadata
        for split in splits:
            if not split.metadata.get('source'):
                split.metadata['source'] = split.metadata.get('url', 'Unknown')
        
        print(f"Split into {len(splits)} chunks")
        
        print("Creating vector embeddings (this may take a while)...")
        embeddings = OpenAIEmbeddings(openai_api_key=self.openai_api_key)
        vectorstore = FAISS.from_documents(splits, embeddings)
        
        print(f"Saving vector store to {vectorstore_path}")
        vectorstore.save_local(vectorstore_path)
        return vectorstore
