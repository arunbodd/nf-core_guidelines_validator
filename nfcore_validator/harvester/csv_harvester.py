"""
CSV-based harvester for nf-core guidelines
"""
import os
import pandas as pd
from typing import List, Dict, Any
from pathlib import Path

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document

class CSVGuidelinesHarvester:
    """Harvests nf-core guidelines from a CSV file and creates a vector store for retrieval"""
    
    def __init__(self, csv_path: str, anthropic_api_key: str = None):
        """Initialize the harvester
        
        Args:
            csv_path: Path to the CSV file
            anthropic_api_key: Anthropic API key (optional, not used for harvesting which uses HuggingFace embeddings)
        """
        self.csv_path = os.path.abspath(csv_path)
        
        # Store API key for compatibility - not used for harvesting which uses HuggingFace embeddings
        self.anthropic_api_key = anthropic_api_key or os.environ.get("ANTHROPIC_API_KEY")
        
        if not os.path.exists(self.csv_path):
            raise ValueError(f"CSV file does not exist: {self.csv_path}")

    def _load_csv_data(self) -> pd.DataFrame:
        """Load data from CSV file
        
        Returns:
            DataFrame containing requirements from CSV
        """
        try:
            # Try with utf-8 encoding first
            df = pd.read_csv(self.csv_path, encoding='utf-8')
            # Clean up data - replace NaNs with empty strings
            df = df.fillna("")
            return df
        except Exception as e:
            # Try alternate encoding if default fails
            try:
                df = pd.read_csv(self.csv_path, encoding='latin1')
                df = df.fillna("")
                return df
            except Exception as e2:
                # Last resort, try with default settings
                try:
                    df = pd.read_csv(self.csv_path)
                    df = df.fillna("")
                    return df
                except Exception as e3:
                    raise ValueError(f"Failed to load CSV file. Errors: {str(e)}, {str(e2)}, {str(e3)}")

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
            # Skip rows without a Definition
            if not row.get('Definition'):
                continue
                
            # Build the content with Classification for better context
            content = f"""
Classification: {row.get('Classification', '')}
Category: {row.get('Category', '')}
Subcategory: {row.get('Subcategory', '')}
Definition: {row.get('Definition', '')}
            """
            
            # Create metadata
            metadata = {
                "source": f"csv:{self.csv_path}:{index}",
                "classification": row.get('Classification', ''),
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

    def harvest(self, vectorstore_path: str = "csv_vectorstore") -> FAISS:
        """Harvest requirements from CSV and create vector store
        
        Args:
            vectorstore_path: Path to save the vector store
            
        Returns:
            FAISS vector store with document embeddings
        """
        print(f"Harvesting nf-core guidelines from CSV file: {self.csv_path}")
        
        # Load CSV data
        df = self._load_csv_data()
        print(f"Loaded {len(df)} rows from CSV file")
        
        # Process requirements into documents
        documents = self._process_requirements(df)
        print(f"Created {len(documents)} documents from CSV requirements")
        
        # Create vector embeddings using HuggingFace (consistent with other harvesters)
        print("Creating vector embeddings using HuggingFace (this may take a while)...")
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            
        vectorstore = FAISS.from_documents(documents, embeddings)
        
        print(f"Saving vector store to {vectorstore_path}")
        vectorstore.save_local(vectorstore_path)
        return vectorstore
