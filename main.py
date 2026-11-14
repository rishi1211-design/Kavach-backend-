from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel
import requests
import os
from supabase import create_client, Client

app = FastAPI(title="Kavach AGI Brain", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. Saari API Keys Render Server se nikalna
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")

# 2. Supabase (Memory) Database Connection
supabase: Client = None
if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

class UserRequest(BaseModel):
    prompt: str
    mode: str = "General Intelligence"
    user_id: str = "user_123"

class VoiceRequest(BaseModel):
    text: str

@app.get("/")
def home():
    return {"status": "Kavach AGI Brain (Groq + Memory + Voice) is Online 🟢", "version": "2.0"}

# --- TEXT & MEMORY API ---
@app.post("/api/think")
def think(request: UserRequest):
    if not GROQ_API_KEY:
        raise HTTPException(status_code=500, detail="Groq API Key missing!")
        
    try:
        # User ka message memory me save karna
        if supabase:
            try:
                supabase.table("kavach_memory").insert({"user_id": request.user_id, "message": request.prompt, "role": "user"}).execute()
            except:
                pass # Agar database me table nahi bani toh app crash nahi hogi
                
        system_instruction = "You are Kavach, an advanced AGI assistant."
        
        # Groq Engine Fast Response
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
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
            
            # AI ka jawaab memory me save karna
            if supabase:
                try:
                    supabase.table("kavach_memory").insert({"user_id": request.user_id, "message": ai_thought, "role": "kavach"}).execute()
                except:
                    pass
                
            return {"status": "success", "mode_used": request.mode, "response": ai_thought}
        else:
            raise HTTPException(status_code=500, detail=f"Groq API Error: {res.text}")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- VOICE GENERATION API ---
@app.post("/api/voice")
def generate_voice(request: VoiceRequest):
    if not ELEVENLABS_API_KEY:
        raise HTTPException(status_code=500, detail="ElevenLabs Key missing!")
        
    try:
        # Adam Voice ID (Best for Story/Horror/Deep Voice)
        voice_id = "pNInz6obpgDQGcFmaJcg" 
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": ELEVENLABS_API_KEY
        }
        
        payload = {
            "text": request.text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
        }
        
        res = requests.post(url, json=payload, headers=headers)
        
        if res.status_code == 200:
            # Seedha audio file return karega jo app me play hogi
            return Response(content=res.content, media_type="audio/mpeg")
        else:
            raise HTTPException(status_code=500, detail=f"ElevenLabs Error: {res.text}")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
