# Search_Engine_Agent
# PolicyBot API – FastAPI + Gemini + Google Search Integration

This project is a FastAPI-based microservice designed to handle **MCP stream requests** for answering queries related to Indian government and private policies, with a focus on social good and development.  
It uses:
- **Google Custom Search API** for web results
- **Gemini 2.5 Pro API** for summarizing and answering user queries using contextual knowledge

---

## 🔧 Features

- FastAPI backend endpoint: `/mcp/stream`
- MCP-compatible request handler
- Web search using Google Programmable Search Engine
- Text generation and summarization using Gemini 2.5 Pro
- Response includes recent contextual policy details with URLs

---

## 🚀 API Endpoint

### `POST /mcp/stream`

Accepts a JSON-RPC 2.0 request of the following structure:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "fetch_bank_transactions",
    "arguments": {
      "query": "Latest AI policy developments in India"
    }
  }
}
