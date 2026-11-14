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

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

class UserRequest(BaseModel):
    prompt: str
    mode: str = "General Intelligence"

@app.get("/")
def home():
    return {"status": "Kavach AGI Brain is Online 🟢", "version": "1.0"}

@app.post("/api/think")
def think(request: UserRequest):
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="Gemini API Key missing on server!")
        
    try:
        system_instruction = "You are Kavach, an advanced AGI assistant."
        if "Image" in request.mode:
            system_instruction = "You are an expert AI visual artist."
        elif "Code" in request.mode:
            system_instruction = "You are an elite software architect and coder."
            
        full_prompt = f"{system_instruction}\n\nUser Query: {request.prompt}"
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key={GEMINI_API_KEY}"
        payload = {"contents": [{"parts": [{"text": full_prompt}]}]}
        
        res = requests.post(url, json=payload)
        
        if res.status_code == 200:
            ai_thought = res.json()['candidates'][0]['content']['parts'][0]['text']
            return {
                "status": "success",
                "mode_used": request.mode,
                "response": ai_thought
            }
        else:
            raise HTTPException(status_code=500, detail=f"AI Provider Error: {res.text}")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
      
