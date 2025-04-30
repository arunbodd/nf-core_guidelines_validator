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
    classDef command fill:#c2f0c2,stroke:#282,stroke-width:1px
    classDef interface fill:#d4d4d4,stroke:#555,stroke-width:1px

    %% Data Sources
    W[nf-core Documentation Website] -->|Scrapes| DH[Docs Harvester]
    E[Excel Template] -->|Loads| EH[Excel Harvester]
    
    %% Harvesting
    DH -->|Creates| VS[FAISS Vector Store]
    EH -->|Creates| VS
    
    %% Embedding Options
    DH -->|Default| HF[HuggingFace Embeddings]
    %% OpenAI embeddings support preserved but no longer used directly
    DH -.->|Legacy Support| OE[OpenAI Embeddings]
    
    %% Pipeline Component Analysis
    PS[Pipeline Scanner] -->|Finds| PC[Pipeline Components]
    PS -->|Uses| V[Validator]
    
    %% Validation Types
    V -->|Option 1| LV[LLM Validator]
    V -->|Option 2| EV[Excel Validator]
    
    %% LLM Provider Options
    LV -->|Uses| VS
    LV -->|OpenAI Option| OA[OpenAI GPT-4]
    LV -->|Anthropic Option| AC[Anthropic Claude]
    
    %% API Key Requirements
    OA -->|Requires| OAK[OpenAI API Key]
    AC -->|Requires| AAK[Anthropic API Key]
    HF -->|No API Key Required| NKR[Local Execution]
    
    %% Report Generation
    V -->|Generates| RG[Report Generator]
    RG -->|Formats| JSON[JSON Report]
    RG -->|Formats| MD[Markdown Report]
    RG -->|Formats| XML[XML Report]
    
    %% Chat Interface
    CI[Chat Interface] -->|Queries| VS
    CI -->|OpenAI Option| OA
    CI -->|Anthropic Option| AC
    
    %% Component Grouping
    subgraph Pipeline Components
        PC1[Modules]
        PC2[Workflows]
        PC3[Subworkflows]
        PC4[Configs]
        PC5[Main Workflow]
        PC6[Pipeline Files]
        PC7[Test Data]
    end
    
    PC --> PC1
    PC --> PC2
    PC --> PC3
    PC --> PC4
    PC --> PC5
    PC --> PC6
    PC --> PC7
    
    %% Command Dependencies
    subgraph Commands
        CMD1[harvest (No API Key Required)]
        CMD2[validate (API Key Required)]
        CMD3[chat (API Key Required)]
    end
    
    %% CLI Interface
    CLI[Command Line Interface] -->|harvest| DH
    CLI -->|validate| PS
    CLI -->|chat| CI
    
    %% Apply styles
    W:::dataSources
    E:::dataSources
    DH:::harvester
    EH:::harvester
    VS:::vectorStore
    HF:::embeddings
    OE:::embeddings
    PS:::validator
    V:::validator
    LV:::validator
    EV:::validator
    OA:::llmModel
    AC:::llmModel
    OAK:::apiKey
    AAK:::apiKey
    NKR:::noApiKey
    RG:::report
    JSON:::report
    MD:::report
    XML:::report
    CI:::interface
    CLI:::interface
    PC:::components
    PC1:::components
    PC2:::components
    PC3:::components
    PC4:::components
    PC5:::components
    PC6:::components
    PC7:::components
    CMD1:::noApiKey
    CMD2:::apiKey
    CMD3:::apiKey
```

*Note: To view this diagram, you need a Markdown viewer that supports Mermaid diagrams, such as GitHub or VS Code with the Mermaid extension.*
