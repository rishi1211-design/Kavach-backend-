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

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")

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
    return {"status": "Kavach AGI Brain is Online 🚀", "version": "2.0"}

@app.post("/api/think")
def think(request: UserRequest):
    if not GROQ_API_KEY:
        raise HTTPException(status_code=500, detail="Groq API Key missing in environment")

    try:
        if supabase:
            try:
                supabase.table("kavach_memory").insert({"user_id": request.user_id, "prompt": request.prompt, "role": "user"}).execute()
            except:
                pass 

        system_instruction = "You are Kavach, an advanced AGI assistant."
        ai_thought = ""

        # --- PLAN A: Groq Engine ---
        groq_url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        payload = {
            "model": "llama3-8b-8192",
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": request.prompt}
            ]
        }

        groq_res = requests.post(groq_url, headers=headers, json=payload)

        if groq_res.status_code == 200:
            ai_thought = groq_res.json()['choices'][0]['message']['content']
        else:
            # --- PLAN B: Fallback to Gemini ---
            if not GEMINI_API_KEY:
                raise HTTPException(status_code=500, detail=f"Groq Error: {groq_res.text} | Gemini Key is missing")
            
            gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
            gemini_payload = {
                "contents": [{"parts": [{"text": f"{system_instruction}\n\nUser: {request.prompt}"}]}]
            }
            
            gemini_res = requests.post(gemini_url, json=gemini_payload)
            
            if gemini_res.status_code == 200:
                ai_thought = gemini_res.json()['candidates'][0]['content']['parts'][0]['text']
            else:
                # YE LINE BATAEGI ASLI ERROR KYA HAI
                error_msg = f"Groq Error: {groq_res.text} || Gemini Error: {gemini_res.text}"
                raise HTTPException(status_code=500, detail=error_msg)

        if supabase:
            try:
                supabase.table("kavach_memory").insert({"user_id": request.user_id, "prompt": ai_thought, "role": "assistant"}).execute()
            except:
                pass

        return {"status": "success", "mode_used": request.mode, "response": ai_thought}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/voice")
def generate_voice(request: VoiceRequest):
    if not ELEVENLABS_API_KEY:
        raise HTTPException(status_code=500, detail="ElevenLabs Key missing")
    
    try:
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
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.7}
        }

        res = requests.post(url, json=payload, headers=headers)

        if res.status_code == 200:
            return Response(content=res.content, media_type="audio/mpeg")
        else:
            raise HTTPException(status_code=500, detail="ElevenLabs Error")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
