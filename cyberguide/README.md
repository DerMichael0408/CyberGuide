# 🛡️ CyberGuide

CyberGuide is an interactive cybersecurity assistant that provides expert guidance and information using locally run AI models through [Ollama](https://ollama.com/) with a user-friendly interface built with [Streamlit](https://streamlit.io).

## Features

- **Interactive Cybersecurity Expert**: Get guidance on cybersecurity topics through a chat interface
- **Local Model Execution**: Run AI models locally for privacy and security using Ollama
- **RAG Implementation**: Leverages Retrieval-Augmented Generation with cybersecurity knowledge base
- **Real-time Responses**: Receive instant cybersecurity advice directly in the UI

## Installation

Before running CyberGuide, ensure you have Python installed on your machine. Then, follow these steps:

```bash
cd cyberguide
```

```bash
pip install -r requirements.txt
```

### Additional Setup

1. Install [Ollama](https://ollama.com/) on your system
2. Pull a compatible language model using Ollama CLI:

```bash
ollama pull llama2 # or another model of your choice
```

3. Make sure you have the required cybersecurity knowledge base files:
   - Place `Petra_logistics.pdf` in your project root
   - Place `CybersecurityScenarios.json` in your project root

## Usage

To start CyberGuide, run the following command in your terminal:

```bash
streamlit run 01_CyberGuide\ Expert.py
```

Navigate to the URL provided by Streamlit in your browser (typically http://localhost:8501) to interact with CyberGuide.

### How to Use CyberGuide

1. **Select a Model**: Choose from available local models in the dropdown menu
2. **Ask Security Questions**: Type your cybersecurity queries in the chat input
3. **Review Retrieved Information**: CyberGuide will display the most relevant information it found in its knowledge base
4. **Get Expert Guidance**: The AI will provide cybersecurity advice based on its model and the retrieved information

## Members

