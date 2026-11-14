from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import os

app = FastAPI(title="Kavach AGI Brain", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

class UserRequest(BaseModel):
    prompt: str
    mode: str = "General Intelligence"

@app.get("/")
def home():
    return {"status": "Kavach AGI Brain (Groq Engine) is Online 🟢", "version": "1.0"}

@app.post("/api/think")
def think(request: UserRequest):
    if not GROQ_API_KEY:
        raise HTTPException(status_code=500, detail="Groq API Key missing on server!")
        
    try:
        system_instruction = "You are Kavach, an advanced AGI assistant."
        if "Image" in request.mode:
            system_instruction = "You are an expert AI visual artist."
        elif "Code" in request.mode:
            system_instruction = "You are an elite software architect and coder."
            
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "llama3-8b-8192", 
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": request.prompt}
            ]
        }
        
        res = requests.post(url, headers=headers, json=payload)
        
        if res.status_code == 200:
            ai_thought = res.json()['choices'][0]['message']['content']
            return {
                "status": "success",
                "mode_used": request.mode,
                "response": ai_thought
            }
        else:
            raise HTTPException(status_code=500, detail=f"Groq API Error: {res.text}")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
