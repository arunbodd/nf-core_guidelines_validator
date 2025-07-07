```mermaid
graph TD
    %% Define styles
    classDef dataSources fill:#d4f1f9,stroke:#05a,stroke-width:1px
    classDef harvester fill:#baffc9,stroke:#085,stroke-width:1px
    classDef vectorStore fill:#ffffba,stroke:#cc8,stroke-width:1px
    classDef embeddings fill:#e6ccff,stroke:#85c,stroke-width:1px
    classDef components fill:#f5d5d5,stroke:#c55,stroke-width:1px
    classDef validator fill:#ffcc99,stroke:#f73,stroke-width:1px
    classDef llmModel fill:#ff9999,stroke:#c55,stroke-width:1px
    classDef apiKey fill:#ffcceb,stroke:#c5c,stroke-width:1px
    classDef noApiKey fill:#ccffcc,stroke:#5c5,stroke-width:1px
    classDef report fill:#d6c3a9,stroke:#862,stroke-width:1px
    classDef interface fill:#d4d4d4,stroke:#555,stroke-width:1px
    classDef guidelines fill:#e6f3ff,stroke:#0080ff,stroke-width:1px

    %% Data Sources
    W["nf-core Documentation Website"] -->|Scrapes| DH["Docs Harvester"]
    E["Excel Template"] -->|Loads| EH["Excel Harvester"]
    
    %% Harvesting - Both use HuggingFace Embeddings
    DH -->|Creates| VS["FAISS Vector Store"]
    EH -->|Creates| VS2["Excel Vector Store"]
    DH -->|Uses| HF["HuggingFace Embeddings"]
    EH -->|Uses| HF
    
    %% Pipeline Component Analysis
    PS["Pipeline Scanner"] -->|Finds| PC["Pipeline Components"]
    PS -->|Chooses Validator| CHOICE{"Excel Template?"}
    
    %% Validator Selection
    CHOICE -->|Yes| EV["Excel Validator"]
    CHOICE -->|No| LV["LLM Validator"]
    
    %% LLM Validator Flow
    LV -->|Uses| VS
    LV -->|Component Type Detection| CTD["Component Type Detection"]
    LV -->|Internal Rule Correction| RBC["Rule-Based Correction"]
    LV -->|Powered by| AC["Anthropic Claude 4 Opus"]
    
    %% Excel Validator Flow  
    EV -->|Uses| VS2
    EV -->|Gets Requirements from| E
    EV -->|Powered by| AC
    
    %% Component Type Detection (LLM Validator only)
    CTD -->|Module Guidelines| MG["Module Guidelines"]
    CTD -->|Workflow Guidelines| WG["Workflow Guidelines"]
    CTD -->|Config Guidelines| CG["Config Guidelines"]
    CTD -->|Documentation Guidelines| DG["Documentation Guidelines"]
    
    %% API Key Requirements
    AC -->|Requires| AAK["Anthropic API Key"]
    HF -->|No API Key Required| NKR["Local Execution"]
    
    %% Report Generation
    LV -->|Generates| RG["Report Generator"]
    EV -->|Generates| RG
    RG -->|Formats| JSON["JSON Report"]
    RG -->|Formats| MD["Markdown Report"]
    RG -->|Formats| XML["XML Report"]
    
    %% Chat Interface
    CI["Chat Interface"] -->|Queries| VS
    CI -->|Powered by| AC
    
    %% Component Types Found
    subgraph "Pipeline Components"
        PC1["Modules (*.nf)"]
        PC2["Workflows (*.nf)"]
        PC3["Subworkflows (*.nf)"]
        PC4["Configs (*.config)"]
        PC5["Main Workflow (main.nf)"]
        PC6["Documentation (*.md)"]
        PC7["Schema (*.json)"]
    end
    
    PC --> PC1
    PC --> PC2
    PC --> PC3
    PC --> PC4
    PC --> PC5
    PC --> PC6
    PC --> PC7
    
    %% CLI Commands
    subgraph "CLI Commands"
        CMD1["harvest - No API Key Required"]
        CMD2["validate - Anthropic API Key Required"]
        CMD3["chat - Anthropic API Key Required"]
    end
    
    %% CLI Interface
    CLI["Command Line Interface"] -->|harvest| DH
    CLI -->|harvest| EH
    CLI -->|validate| PS
    CLI -->|chat| CI
    
    %% Apply Styling
    class W,E dataSources
    class DH,EH harvester
    class VS,VS2 vectorStore
    class HF embeddings
    class PS,LV,EV validator
    class AC llmModel
    class AAK apiKey
    class NKR,CMD1 noApiKey
    class CMD2,CMD3 apiKey
    class RG report
    class JSON,MD,XML report
    class CI,CLI interface
    class PC,PC1,PC2,PC3,PC4,PC5,PC6,PC7 components
    class MG,WG,CG,DG guidelines
```

*Note: To view this diagram, you need a Markdown viewer that supports Mermaid diagrams, such as GitHub or VS Code with the Mermaid extension.*
