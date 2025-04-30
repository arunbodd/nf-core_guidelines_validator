"""
Excel-based harvester for nf-core guidelines
"""
import os
import pandas as pd
from typing import List, Dict, Any
from pathlib import Path

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document

class ExcelGuidelinesHarvester:
    """Harvests nf-core guidelines from an Excel template and creates a vector store for retrieval"""
    
    def __init__(self, excel_path: str, openai_api_key: str = None, anthropic_api_key: str = None):
        """Initialize the harvester
        
        Args:
            excel_path: Path to the Excel template file
            openai_api_key: OpenAI API key for embeddings (optional, not used with default HuggingFace embeddings)
            anthropic_api_key: Anthropic API key (optional, not used with default HuggingFace embeddings)
        """
        self.excel_path = os.path.abspath(excel_path)
        
        # Store API keys but only for compatibility - not used for harvesting
        # which uses HuggingFace embeddings by default
        self.openai_api_key = openai_api_key or os.environ.get("OPENAI_API_KEY")
        self.anthropic_api_key = anthropic_api_key or os.environ.get("ANTHROPIC_API_KEY")
        
        if not os.path.exists(self.excel_path):
            raise ValueError(f"Excel template does not exist: {self.excel_path}")

    def _load_excel_data(self) -> pd.DataFrame:
        """Load data from Excel template
        
        Returns:
            DataFrame containing requirements from Excel
        """
        try:
            # Assuming the Excel has one sheet with requirements
            df = pd.read_excel(self.excel_path)
            
            # Clean up data - replace NaNs with empty strings
            df = df.fillna("")
            
            return df
        except Exception as e:
            raise ValueError(f"Failed to load Excel template: {str(e)}")

    def _process_requirements(self, df: pd.DataFrame) -> List[Document]:
        """Process requirements from DataFrame into documents
        
        Args:
            df: DataFrame containing requirements
            
        Returns:
            List of Document objects
        """
        documents = []
        
        # Create a document for each requirement
        for index, row in df.iterrows():
            # Skip rows without a definition
            if not row.get('Definition'):
                continue
                
            # Build the content
            content = f"""
Category: {row.get('Category', '')}
Subcategory: {row.get('Subcategory', '')}
Definition: {row.get('Definition', '')}
            """
            
            # Add additional notes if available
            if row.get('Notes'):
                content += f"\nNotes: {row.get('Notes')}"
            
            # Create metadata
            metadata = {
                "source": f"excel_template:{index}",
                "category": row.get('Category', ''),
                "subcategory": row.get('Subcategory', '')
            }
            
            # Create document
            doc = Document(
                page_content=content.strip(),
                metadata=metadata
            )
            
            documents.append(doc)
        
        return documents

    def harvest(self, vectorstore_path: str = "excel_vectorstore") -> FAISS:
        """Harvest requirements from Excel and create vector store
        
        Args:
            vectorstore_path: Path to save the vector store
            
        Returns:
            FAISS vector store with document embeddings
        """
        print("Harvesting nf-core guidelines from Excel template...")
        
        # Load Excel data
        df = self._load_excel_data()
        print(f"Loaded {len(df)} rows from Excel template")
        
        # Process requirements into documents
        documents = self._process_requirements(df)
        print(f"Created {len(documents)} documents from Excel requirements")
        
        # Create vector embeddings using HuggingFace
        print("Creating vector embeddings using HuggingFace (this may take a while)...")
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        vectorstore = FAISS.from_documents(documents, embeddings)
        
        print(f"Saving vector store to {vectorstore_path}")
        vectorstore.save_local(vectorstore_path)
        return vectorstore 