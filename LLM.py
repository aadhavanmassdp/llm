from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uuid
import time

app = FastAPI(title="Multi-Modal AI Assistant Platform")

# ----------------------------
# Data Models
# ----------------------------

class UserMessage(BaseModel):
    message: str
    session_id: Optional[str] = None

class AssistantResponse(BaseModel):
    reply: str
    session_id: str
    generated_content: Optional[Dict[str, Any]] = None
    generator_used: Optional[str] = None

# ----------------------------
# In-Memory Session Store (Use Redis/DB in production)
# ----------------------------

SESSIONS: Dict[str, Dict] = {}

def get_or_create_session(session_id: Optional[str] = None) -> str:
    if session_id and session_id in SESSIONS:
        return session_id
    new_id = str(uuid.uuid4())
    SESSIONS[new_id] = {
        "history": [],
        "created_at": time.time(),
        "last_active": time.time()
    }
    return new_id

# ----------------------------
# Mock Generator Services
# ----------------------------

async def generate_code(prompt: str) -> str:
    # In real app: call OpenAI, CodeLlama, etc.
    return f"# Generated Python code based on: '{prompt}'\n\ndef example_function():\n    return 'Hello from AI!'"

async def generate_image(prompt: str) -> str:
    # Return mock image URL or base64 (real: Stability AI, DALL·E)
    return "https://example.com/generated_image.png"

async def generate_audio(prompt: str) -> str:
    # Return mock audio URL (real: Suno, MusicGen)
    return "https://example.com/generated_audio.mp3"

# ----------------------------
# Intent Classifier (Rule-Based — Replace with NLP Model)
# ----------------------------

def classify_intent(message: str) -> str:
    msg_lower = message.lower()
    
    if any(kw in msg_lower for kw in ["code", "function", "script", "write a", "program", "implement"]):
        return "code"
    elif any(kw in msg_lower for kw in ["image", "picture", "draw", "art", "logo", "visual", "paint"]):
        return "image"
    elif any(kw in msg_lower for kw in ["music", "audio", "sound", "song", "melody", "track", "compose"]):
        return "audio"
    else:
        return "conversation"

# ----------------------------
# Assistant Endpoint
# ----------------------------

@app.post("/api/v1/assistant/chat", response_model=AssistantResponse)
async def chat_with_assistant(user_msg: UserMessage):
    session_id = get_or_create_session(user_msg.session_id)
    session = SESSIONS[session_id]
    
    # Update last active time
    session["last_active"] = time.time()
    
    # Classify intent
    intent = classify_intent(user_msg.message)
    
    generated_content = None
    generator_used = None
    reply = ""
    
    try:
        if intent == "code":
            code = await generate_code(user_msg.message)
            generated_content = {"code": code, "language": "python"}
            generator_used = "code"
            reply = "I've generated the code you requested!"
            
        elif intent == "image":
            image_url = await generate_image(user_msg.message)
            generated_content = {"image_url": image_url}
            generator_used = "image"
            reply = "Here’s the image I created for you!"
            
        elif intent == "audio":
            audio_url = await generate_audio(user_msg.message)
            generated_content = {"audio_url": audio_url}
            generator_used = "audio"
            reply = "Your audio has been generated!"
            
        else:  # conversation
            # In production: call LLM like GPT-4
            reply = "I understand! How else can I assist you today?"
            generator_used = "conversation"
        
        # Save to history
        session["history"].append({
            "role": "user",
            "content": user_msg.message,
            "timestamp": time.time()
        })
        session["history"].append({
            "role": "assistant",
            "content": reply,
            "generator": generator_used,
            "timestamp": time.time()
        })
        
        return AssistantResponse(
            reply=reply,
            session_id=session_id,
            generated_content=generated_content,
            generator_used=generator_used
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


curl -X POST "http://localhost:8000/api/v1/assistant/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "Write a Python function to reverse a string"}'
