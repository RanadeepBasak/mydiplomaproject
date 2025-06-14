from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, List, Dict
import base64
import httpx
import os
from dotenv import load_dotenv ## added

load_dotenv()

AIPIPE_TOKEN = os.getenv("AIPIPE_TOKEN")
AIPIPE_URL = "https://aipipe.org/openrouter/v1/chat/completions"
IMAGE_FILE_PATH = "uploaded_image.webp" # File to temporarily save the image

app = FastAPI()

class QARequest(BaseModel):
    question: str
    image: Optional[str] = None

class QAResponse(BaseModel):
    answer: str
    links: List[Dict[str, str]]

@app.post("/api/", response_model=QAResponse)
def answer_question(payload: QARequest):
    if payload.image:
        try:
            with open(IMAGE_FILE_PATH, "wb") as f:
                f.write(base64.b64decode(payload.image))
        except Exception as e:
            return {"answer": f"Failed to decode image: {str(e)}", "links": []}

    # Replace this with your actual retrieval logic
    retrieved_context = "The relevant content from TDS course or Discourse goes here."

    # Build messages
    messages = [
        {"role": "system", "content": "You are a helpful TA for the TDS course at IITM."},
        {"role": "user", "content": f"{payload.question}\n\nContext:\n{retrieved_context}"}
    ]

    # Call AIPipe
    headers = {
        "Authorization": f"Bearer {AIPIPE_TOKEN}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "openai/gpt-3.5-turbo",  # or "openai/gpt-3.5-turbo" #openai/gpt-4o-mini
        "messages": messages
    }

    response = httpx.post(AIPIPE_URL, headers=headers, json=data, timeout=60.0)
    response.raise_for_status()

    reply = response.json()['choices'][0]['message']['content']

    return {
        "answer": reply.strip(),
        "links": [
            {
                "url": "https://discourse.onlinedegree.iitm.ac.in/t/example-post",
                "text": "Relevant discussion link"
            }
        ]
    }