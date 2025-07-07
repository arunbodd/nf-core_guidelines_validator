# nf-core Validator
![My Logo](https://raw.githubusercontent.com/arunbodd/nf-core_guidelines_validator/refs/heads/dev/docs/Architecture_Diagram.svg)

An AI-powered agent for validating nf-core pipeline compliance. This tool analyzes Nextflow pipelines against the official nf-core guidelines and provides detailed recommendations for improving compliance.

## Features

- **Documentation-Based Validation**: Uses the latest nf-core guidelines directly from the official documentation
- **Comprehensive Analysis**: Checks modules, workflows, and subworkflows against all relevant requirements
- **Detailed Reports**: Generates comprehensive reports with specific recommendations for each component
- **AI-Powered**: Leverages large language models to understand complex requirements and provide context-aware suggestions
- **Interactive Chat**: Query the nf-core documentation directly with natural language questions
- **Categorized Results**: View validation results and chat responses organized by documentation category
- **Anthropic Claude 4 Opus**: Powered by the latest Claude 4 Opus model for superior validation accuracy
- **No API Key for Harvesting**: Uses HuggingFace embeddings with no API key requirement for harvesting
- **Excel Template Option**: Can use Excel templates with structured guidelines as an alternative to web-based guidelines
- **Multiple Report Formats**: Generate reports in JSON, Markdown, and XML formats

## Installation

### Prerequisites

- Python 3.8 or higher
- An Anthropic API key (required only for validate and chat commands, not for harvest)

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

Before validating pipelines, you need to harvest the nf-core documentation. You have two options:

#### Option A: Web-based Guidelines

Harvest guidelines directly from the nf-core website:

```bash
# Using HuggingFace embeddings (no API key required)
nfcore-validator harvest
```

#### Option B: Excel Template

Use a structured Excel template containing pipeline requirements:

```bash
# Using Excel template (no API key required)
nfcore-validator harvest --excel-template path/to/guidelines.xlsx
```

The harvest command will create a vector store in different default locations depending on the source:
- Web-based harvesting: `nfcore_vectorstore/` 
- Excel-based harvesting: `excel_vectorstore/`

You can specify a custom output location with the `--output` parameter:
```bash
nfcore-validator harvest --excel-template path/to/guidelines.xlsx --output custom_vectorstore
```

Either method will create a vector store of nf-core guidelines in the current directory.

### 2. Validate a Pipeline

```bash
# Validate a pipeline using Anthropic Claude 4 Opus
nfcore-validator validate /path/to/your/pipeline --format markdown --api-key $ANTHROPIC_API_KEY

# Validate using Excel template as the requirements source
nfcore-validator validate /path/to/your/pipeline --excel-template path/to/guidelines.xlsx --format markdown --api-key $ANTHROPIC_API_KEY
```

This will:
1. Analyze all components in the pipeline
2. Check them against relevant nf-core guidelines
3. Generate a detailed compliance report

### 3. Chat with nf-core Documentation

You can also directly query the nf-core documentation using natural language:

```bash
# Start the chat interface with Anthropic Claude 4 Opus
nfcore-validator chat --api-key $ANTHROPIC_API_KEY

# Show sources for answers
nfcore-validator chat --show-sources --api-key $ANTHROPIC_API_KEY

# Increase context size for more comprehensive answers
nfcore-validator chat --context-size 15 --api-key $ANTHROPIC_API_KEY
```

The `--show-sources` flag displays the source documents used to generate the answer, organized by documentation category.

## Report Formats

The tool generates three types of reports:

1. **JSON Report**: Contains all validation details in a structured format
2. **Markdown Report**: Human-readable summary with component details and recommendations
3. **XML Report**: Compliance report in XML format for integration with other tools

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
# No API key required for harvest
nfcore-validator harvest --output /path/to/vectorstore

# Anthropic API key required for validate
nfcore-validator validate /path/to/pipeline --vectorstore /path/to/vectorstore --api-key $ANTHROPIC_API_KEY
```

### Rate Limit Handling

The validator automatically handles API rate limits by:
- Processing components gradually
- Waiting and retrying when rate limits are hit
- Adding small delays between API calls

You can also reduce parallelism to further avoid rate limits:

```bash
python -m nfcore_validator.cli.main validate /path/to/pipeline --max-workers 2 --api-key $ANTHROPIC_API_KEY
```

### Categorized Chat

The chat interface categorizes information by documentation section:

```bash
# Anthropic API key required
nfcore-validator chat --show-sources --api-key $ANTHROPIC_API_KEY
```

This will display sources grouped by categories like:
- Module Guidelines
- Subworkflow Guidelines
- Pipeline Structure
- Test Data Guidelines

## System Architecture

The nf-core validator consists of several components working together:

1. **Documentation Harvester**: Scrapes the nf-core documentation website and creates embeddings
2. **Excel Harvester**: Alternative approach that loads guidelines from an Excel template
3. **Pipeline Scanner**: Identifies and organizes pipeline components for validation
4. **Validator**: LLM-based system that checks components against guidelines
5. **Chat Interface**: Interactive Q&A system for nf-core documentation
6. **Report Generator**: Creates formatted reports in JSON, Markdown, and XML

The system uses:
- Anthropic's Claude 4 Opus for LLM-based analysis (validate/chat)
- HuggingFace embeddings for harvesting documentation and creating vector embeddings

For detailed technical information, see [How It Works](docs/how_it_works.md).

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
