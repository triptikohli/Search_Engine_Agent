from fastapi import FastAPI, Request, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import requests
import google.generativeai as genai
from typing import List, Dict, Optional
import json

# Configuration
GOOGLE_API_KEY = "AIzaSyDYPRZRkn5Dgmez17Krqket5a8IOY1OLkE"
SEARCH_ENGINE_ID = "a56d28eb5509e451c"
GEMINI_API_KEY = "AIzaSyDPCjJaJQUwjtFbTOCM_Yxali_hl5a4IR8"

genai.configure(api_key=GEMINI_API_KEY)

# FastAPI App
app = FastAPI()

class CallParams(BaseModel):
    name: str
    arguments: Dict = {}

class MCPRequest(BaseModel):
    jsonrpc: str
    id: int
    method: str
    params: CallParams

def web_search(query: str) -> List[Dict[str, str]]:
    try:
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": GOOGLE_API_KEY,
            "cx": SEARCH_ENGINE_ID,
            "q": query,
            "num": 3
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        results = response.json().get("items", [])
        return [
            {
                "title": r.get("title", ""),
                "snippet": r.get("snippet", ""),
                "url": r.get("link", "")
            } for r in results
        ]
    except Exception as e:
        return [{"title": "Error", "snippet": str(e), "url": ""}]

def call_gemini(prompt: str, context: str, history: str) -> str:
    try:
        model = genai.GenerativeModel("gemini-2.5-pro")
        full_prompt = (
            f"You are an expert on Indian government and private policies realted to social good and development "
            f"Conversation history:\n{history}\n\n"
            f"Current query: {prompt}\n\n"
            f"Web search context:\n{context}\n\n"
            f"Provide a concise, accurate answer focusing on recent Indian policies or developments "
            f"related to intelligent chat-based systems. If the context lacks policy details, "
            f"state that and provide a general answer based on your knowledge. Cite URLs from the context if relevant."
        )
        response = model.generate_content(full_prompt)
        return response.text.strip()
    except Exception as e:
        return f"Gemini API error: {str(e)}"

@app.post("/mcp/stream")
async def handle_mcp(request: Request, mcp_session_id: Optional[str] = Header(None)):
    body = await request.json()
    parsed = MCPRequest(**body)

    if parsed.method != "tools/call" or parsed.params.name != "fetch_bank_transactions":
        return JSONResponse(status_code=400, content={"error": "Invalid method or tool name"})

    user_prompt = parsed.params.arguments.get("query", "What are the latest AI policy developments in India?")
    search_results = web_search(user_prompt)
    context = "\n\n".join([
        f"Title: {r['title']}\nSnippet: {r['snippet']}\nURL: {r['url']}" for r in search_results
    ])
    answer = call_gemini(user_prompt, context, history="")

    return {
        "jsonrpc": "2.0",
        "id": parsed.id,
        "result": {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps({"bankTransactions": [{"bank": "PolicyBot", "txns": [["-", answer, "Now", "info", "web", "-"]]}]})
                }
            ]
        }
    }
