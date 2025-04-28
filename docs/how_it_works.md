# How the nf-core Validator Works

This document explains the architecture and workflow of the nf-core validator, a RAG-based AI agent that analyzes Nextflow pipelines for compliance with nf-core guidelines.

## Architecture Overview

The nf-core validator uses a Retrieval-Augmented Generation (RAG) architecture with three main components:

1. **Knowledge Base**: A vector database containing nf-core documentation
2. **Retrieval System**: Finds relevant guidelines for each pipeline component
3. **LLM Validator**: Analyzes code against retrieved guidelines

![Architecture Diagram](architecture.svg)

## Workflow

### 1. Documentation Harvesting

The first step is to harvest all nf-core guidelines from the official documentation:

```bash
nfcore-validator harvest
```

This process:
- Scrapes the nf-core documentation website
- Extracts guidelines for modules, workflows, and other components
- Chunks the text into manageable pieces
- Creates vector embeddings using OpenAI's embedding model
- Stores these embeddings in a FAISS vector database

### 2. Pipeline Analysis

When you validate a pipeline:

```bash
nfcore-validator validate /path/to/pipeline
```

The system:
1. Scans the pipeline directory structure
2. Identifies all components (modules, workflows, etc.)
3. For each component:
   - Reads the component code
   - Retrieves relevant guidelines from the vector database
   - Sends the code + guidelines to the LLM for analysis
   - Receives structured validation results

### 3. Report Generation

The validation results are compiled into comprehensive reports:

- **JSON Report**: Contains all validation details in a structured format
- **Markdown Report**: Human-readable summary with component details and recommendations

## Technical Details

### RAG Implementation

The RAG approach works as follows:

1. **Retrieval**: For each component, we find the most relevant guidelines:
   ```python
   docs = vectorstore.similarity_search(code, k=5)
   guidelines = "\n".join([d.page_content for d in docs])
   ```

2. **Augmentation**: We combine the code and guidelines in a prompt:
   ```python
   prompt = f"""
   Component Path: {component_path}
   Component Code: {code}
   Relevant Guidelines: {guidelines}
   """
   ```

3. **Generation**: The LLM analyzes the code against the guidelines:
   ```python
   response = llm([
       SystemMessage(content=system_prompt),
       HumanMessage(content=prompt)
   ])
   ```

### Benefits of RAG

This approach has several advantages:

1. **Knowledge-Bound**: The LLM only uses nf-core documentation as its knowledge source
2. **Up-to-Date**: The knowledge base can be refreshed when guidelines change
3. **Transparent**: Validation results can reference specific guidelines
4. **Context-Aware**: Each component is validated against relevant guidelines

## Component Validation

### Module Validation

When validating a module, the system checks:

1. **Naming Conventions**:
   - Directory structure (lowercase)
   - Process names (uppercase with underscores)
   - Parameter names (snake_case)
   - Function names (camelCase)

2. **Input/Output**:
   - Required input channels
   - Optional input channels
   - Output channel format

3. **Documentation**:
   - Presence of meta.yaml
   - Documentation of tools used
   - Documentation of input/output channels

4. **Testing**:
   - Test data availability
   - Test configurations

### Workflow Validation

For workflows, the system checks:

1. **Structure**:
   - Proper imports of modules
   - Channel connections
   - Error handling

2. **Documentation**:
   - Workflow purpose and usage
   - Parameter documentation

### Pipeline-Level Validation

At the pipeline level, the system checks:

1. **Configuration**:
   - nextflow.config structure
   - Resource specifications
   - Container definitions

2. **Documentation**:
   - README.md completeness
   - CHANGELOG.md format
   - LICENSE file

## Interactive Documentation Chat

The system also provides a chat interface for querying the nf-core documentation:

```bash
nfcore-validator chat
```

This uses the same RAG architecture:

1. User question is converted to a vector embedding
2. Relevant documentation chunks are retrieved
3. The LLM generates an answer based on the retrieved chunks
4. Sources are categorized by documentation section

## Rate Limit Handling

The system includes sophisticated rate limit handling:

1. **Controlled Parallelism**:
   - Components are processed in batches
   - Parallel workers can be adjusted

2. **Automatic Retry**:
   - Detects rate limit errors
   - Extracts wait time from error messages
   - Automatically retries after waiting

3. **Throttling**:
   - Adds small delays between API calls
   - Prevents overwhelming the API

## Extending the Validator

The validator can be extended in several ways:

1. **New Guidelines**: Re-run the harvester when nf-core updates their documentation
2. **Custom Rules**: Add pipeline-specific rules in your organization
3. **Integration**: Add the validator to CI/CD pipelines for automatic compliance checking