# nf-core Validator

An AI-powered agent for validating nf-core pipeline compliance. This tool analyzes Nextflow pipelines against the official nf-core guidelines and provides detailed recommendations for improving compliance.

## Features

- **Documentation-Based Validation**: Uses the latest nf-core guidelines directly from the official documentation
- **Comprehensive Analysis**: Checks modules, workflows, and subworkflows against all relevant requirements
- **Detailed Reports**: Generates comprehensive reports with specific recommendations for each component
- **AI-Powered**: Leverages large language models to understand complex requirements and provide context-aware suggestions
- **Interactive Chat**: Query the nf-core documentation directly with natural language questions
- **Categorized Results**: View validation results and chat responses organized by documentation category

## Installation

### Prerequisites

- Python 3.8 or higher
- OpenAI API key

### Install from source

```bash
# Clone the repository
git clone https://github.com/arunbodd/nf-core_guidelines_validator
cd nf-core_guidelines_validator

# Install the package
pip install -e .
```

## Usage

### 1. Harvest nf-core Documentation

Before validating pipelines, you need to harvest the nf-core documentation:

```bash
# Set your OpenAI API key
export OPENAI_API_KEY="your-api-key"

# Harvest documentation
nfcore-validator harvest
```

This will create a vector store of nf-core guidelines in the current directory.

### 2. Validate a Pipeline

```bash
# Validate a pipeline
nfcore-validator validate /path/to/your/pipeline --format markdown
```

This will:
1. Analyze all components in the pipeline
2. Check them against relevant nf-core guidelines
3. Generate a detailed compliance report

### 3. Chat with nf-core Documentation

You can also directly query the nf-core documentation using natural language:

```bash
# Start the chat interface
nfcore-validator chat

# Show sources for answers
nfcore-validator chat --show-sources

# Increase context size for more comprehensive answers
nfcore-validator chat --context-size 15
```

## Report Format

The tool generates two types of reports:

1. **JSON Report**: Contains all validation details in a structured format
2. **Markdown Report**: Human-readable summary with component details and recommendations

The enhanced markdown report includes:

- **Component Type Breakdown**: Shows compliance by component type
- **Detailed Violations**: Descriptions and example fixes for each violation type
- **Organized Components**: Grouped by type with failed requirements highlighted
- **Actionable Recommendations**: Prioritized list of improvements with affected components

Example markdown report:

```markdown
# nf-core Pipeline Compliance Report

**Pipeline:** `rnaseq`
**Path:** `/path/to/pipeline`
**Date:** 2025-04-28 00:11:25

## Summary
- **Components Analyzed:** 25
- **Requirements Checked:** 143
- **Passed Requirements:** 128
- **Failed Requirements:** 15
- **Compliance Score:** 89.5%

## Component Type Breakdown
| Component Type | Count | Avg. Compliance |
|---------------|-------|----------------|
| module | 15 | 92.33% |
| workflow | 5 | 85.60% |
...
```

## Advanced Usage

### Custom Vector Store Location

```bash
nfcore-validator harvest --output /path/to/vectorstore
nfcore-validator validate /path/to/pipeline --vectorstore /path/to/vectorstore
```

### Rate Limit Handling

The validator automatically handles OpenAI API rate limits by:
- Processing components gradually
- Waiting and retrying when rate limits are hit
- Adding small delays between API calls

You can also reduce parallelism to further avoid rate limits:

```bash
python -m nfcore_validator.cli.main validate /path/to/pipeline --max-workers 2
```

### Categorized Chat

The chat interface categorizes information by documentation section:

```bash
nfcore-validator chat --show-sources
```

This will display sources grouped by categories like:
- Module Guidelines
- Subworkflow Guidelines
- Pipeline Structure
- Test Data Guidelines

## How It Works

1. **Documentation Harvesting**: The tool extracts all guidelines from the official nf-core documentation website
2. **Vector Embedding**: Guidelines are converted to vector embeddings for semantic search
3. **Component Analysis**: For each pipeline component, the tool retrieves relevant guidelines
4. **AI Validation**: An LLM analyzes the component against the guidelines and generates recommendations
5. **Report Generation**: Results are compiled into comprehensive reports

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
