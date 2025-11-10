"""
Complete Qwen3-Omni Backend
- Internet search (Brave API)
- Website browsing
- Persistent context/notes (SQLite)
- Conversation history
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import aiohttp
from bs4 import BeautifulSoup
import sqlite3
import json
from pathlib import Path
from datetime import datetime
import os
from typing import Optional, List

app = FastAPI(
    title="Qwen3-Omni Enhanced Backend",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
VLLM_URL = os.getenv("VLLM_API_URL", "http://vllm:8000")
BRAVE_API_KEY = os.getenv("BRAVE_API_KEY", "")
ENABLE_SEARCH = os.getenv("ENABLE_SEARCH", "true").lower() == "true"
DB_PATH = Path("/app/data/qwen_context.db")

# Initialize database
def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            role TEXT,
            content TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            metadata JSON
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            tags TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS context (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            value TEXT NOT NULL,
            category TEXT,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

init_db()

# Models
class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"
    enable_search: bool = False
    max_tokens: int = 1000

class Note(BaseModel):
    title: str
    content: str
    tags: Optional[str] = ""

class Context(BaseModel):
    key: str
    value: str
    category: str = "general"

# Helper Functions
async def search_brave(query: str, count: int = 5) -> List[dict]:
    """Search using Brave Search API"""
    if not BRAVE_API_KEY:
        return []
    
    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                "Accept": "application/json",
                "X-Subscription-Token": BRAVE_API_KEY
            }
            async with session.get(
                f"https://api.search.brave.com/res/v1/web/search",
                params={"q": query, "count": count},
                headers=headers,
                timeout=10
            ) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
                results = data.get("web", {}).get("results", [])
                return [{
                    "title": r.get("title", ""),
                    "description": r.get("description", ""),
                    "url": r.get("url", "")
                } for r in results[:count]]
    except Exception as e:
        print(f"Search error: {e}")
        return []

async def fetch_url_content(url: str, max_chars: int = 5000) -> str:
    """Fetch and parse webpage content"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as resp:
                if resp.status != 200:
                    return ""
                html = await resp.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                for script in soup(["script", "style", "nav", "footer"]):
                    script.decompose()
                
                text = soup.get_text(separator='\n', strip=True)
                return text[:max_chars]
    except Exception as e:
        print(f"URL fetch error: {e}")
        return ""

async def call_qwen(messages: list, max_tokens: int = 1000) -> str:
    """Call Qwen3-Omni via vLLM"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{VLLM_URL}/v1/chat/completions",
                json={
                    "model": "qwen3-omni",
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": 0.7
                },
                timeout=300
            ) as resp:
                if resp.status != 200:
                    raise HTTPException(status_code=resp.status, detail="vLLM error")
                data = await resp.json()
                return data["choices"][0]["message"]["content"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def save_to_db(table: str, data: dict):
    """Generic save to database"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    columns = ", ".join(data.keys())
    placeholders = ", ".join(["?" for _ in data])
    
    c.execute(
        f"INSERT INTO {table} ({columns}) VALUES ({placeholders})",
        tuple(data.values())
    )
    
    conn.commit()
    conn.close()

def query_db(query: str, params: tuple = ()) -> list:
    """Generic database query"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(query, params)
    rows = c.fetchall()
    conn.close()
    return rows

# API Endpoints

@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

@app.post("/api/v1/chat")
async def chat(request: ChatRequest):
    """
    Enhanced chat with optional search and context
    """
    # Get conversation history
    history = query_db(
        "SELECT role, content FROM conversations WHERE session_id = ? ORDER BY timestamp DESC LIMIT 10",
        (request.session_id,)
    )
    
    # Build messages
    messages = []
    
    # Add system context if available
    context_items = query_db(
        "SELECT key, value FROM context ORDER BY updated_at DESC LIMIT 5"
    )
    if context_items:
        context_str = "\n".join([f"- {k}: {v}" for k, v in context_items])
        messages.append({
            "role": "system",
            "content": f"Relevant context:\n{context_str}"
        })
    
    # Add conversation history (reversed to maintain order)
    for role, content in reversed(history):
        messages.append({"role": role, "content": content})
    
    # Perform search if enabled and needed
    search_results = []
    if request.enable_search and ENABLE_SEARCH and BRAVE_API_KEY:
        search_keywords = ["latest", "current", "recent", "news", "what is", "who is"]
        should_search = any(kw in request.message.lower() for kw in search_keywords)
        
        if should_search:
            search_results = await search_brave(request.message)
            
            if search_results:
                search_context = "Search Results:\n"
                for i, r in enumerate(search_results, 1):
                    search_context += f"{i}. {r['title']}\n{r['description']}\n{r['url']}\n\n"
                
                messages.append({
                    "role": "system",
                    "content": search_context
                })
    
    # Add user message
    messages.append({
        "role": "user",
        "content": request.message
    })
    
    # Get response from Qwen
    response = await call_qwen(messages, request.max_tokens)
    
    # Save conversation
    save_to_db("conversations", {
        "session_id": request.session_id,
        "role": "user",
        "content": request.message,
        "metadata": json.dumps({"search_used": len(search_results) > 0})
    })
    
    save_to_db("conversations", {
        "session_id": request.session_id,
        "role": "assistant",
        "content": response
    })
    
    return {
        "response": response,
        "session_id": request.session_id,
        "search_used": len(search_results) > 0,
        "sources": [r["url"] for r in search_results] if search_results else []
    }

@app.post("/api/v1/browse")
async def browse(url: str, question: Optional[str] = None):
    """Browse URL and optionally answer question about it"""
    content = await fetch_url_content(url)
    
    if not content:
        raise HTTPException(status_code=400, detail="Could not fetch URL")
    
    prompt = f"Based on this webpage content:\n\n{content}\n\n"
    if question:
        prompt += f"Question: {question}"
    else:
        prompt += "Provide a concise summary of the main points."
    
    messages = [{"role": "user", "content": prompt}]
    response = await call_qwen(messages, 1000)
    
    return {
        "url": url,
        "response": response
    }

@app.get("/api/v1/conversations/{session_id}")
async def get_conversation(session_id: str, limit: int = 50):
    """Get conversation history"""
    rows = query_db(
        "SELECT role, content, timestamp FROM conversations WHERE session_id = ? ORDER BY timestamp DESC LIMIT ?",
        (session_id, limit)
    )
    
    return {
        "session_id": session_id,
        "messages": [
            {"role": r[0], "content": r[1], "timestamp": r[2]}
            for r in reversed(rows)
        ]
    }

@app.post("/api/v1/notes")
async def create_note(note: Note):
    """Create a note"""
    save_to_db("notes", {
        "title": note.title,
        "content": note.content,
        "tags": note.tags
    })
    return {"status": "created"}

@app.get("/api/v1/notes")
async def list_notes(tag: Optional[str] = None, limit: int = 50):
    """List notes"""
    if tag:
        rows = query_db(
            "SELECT id, title, content, tags, created_at FROM notes WHERE tags LIKE ? LIMIT ?",
            (f"%{tag}%", limit)
        )
    else:
        rows = query_db(
            "SELECT id, title, content, tags, created_at FROM notes ORDER BY updated_at DESC LIMIT ?",
            (limit,)
        )
    
    return {
        "notes": [
            {"id": r[0], "title": r[1], "content": r[2], "tags": r[3], "created_at": r[4]}
            for r in rows
        ]
    }

@app.get("/api/v1/notes/search")
async def search_notes(q: str):
    """Search notes"""
    rows = query_db(
        "SELECT id, title, content, tags FROM notes WHERE title LIKE ? OR content LIKE ? LIMIT 20",
        (f"%{q}%", f"%{q}%")
    )
    
    return {
        "results": [
            {"id": r[0], "title": r[1], "content": r[2], "tags": r[3]}
            for r in rows
        ]
    }

@app.post("/api/v1/context")
async def save_context(context: Context):
    """Save context/memory"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT OR REPLACE INTO context (key, value, category, updated_at) VALUES (?, ?, ?, CURRENT_TIMESTAMP)",
        (context.key, context.value, context.category)
    )
    conn.commit()
    conn.close()
    return {"status": "saved"}

@app.get("/api/v1/context")
async def list_context(category: Optional[str] = None):
    """List context"""
    if category:
        rows = query_db("SELECT key, value, category FROM context WHERE category = ?", (category,))
    else:
        rows = query_db("SELECT key, value, category FROM context")
    
    return {
        "context": [
            {"key": r[0], "value": r[1], "category": r[2]}
            for r in rows
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
