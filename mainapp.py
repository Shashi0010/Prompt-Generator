from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import requests

app = FastAPI()

# CORS config to allow frontend on Netlify
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://magic-prompt-generator.netlify.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic model for expected POST body
class PromptPayload(BaseModel):
    idea: str
    model: str

# Helper: Send AI request with debug logs
def send_ai_request(prompt, api_key, api_url, model_name=None):
    print(f"\nSending AI request to {api_url}")
    print(f"Prompt content: {prompt}\n")

    headers = {"Authorization": f"Bearer {api_key}"}

    if "huggingface" in api_url:
        headers["Content-Type"] = "application/json"
        payload = {"inputs": prompt}
    else:  # Groq API (OpenAI-compatible)
        headers["Content-Type"] = "application/json"
        payload = {
            "model": model_name,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 500
        }

    response = requests.post(api_url, headers=headers, json=payload)
    print(f"API raw response: {response.text}\n")

    result = response.json()

    if "huggingface" in api_url:
        return result[0]["generated_text"] if isinstance(result, list) else result
    else:
        return result["choices"][0]["message"]["content"]

# Helper: Build full structured magic prompt
def generate_prompt_for_idea(idea):
    return f"""
Act as a world-class expert prompt engineer.

Given the following raw idea: \"{idea}\"

Your job is to craft a fully structured, actionable AI prompt that includes:

- A professional role for the AI to assume.
- Clear context setting.
- Step-by-step approach or strategy.
- Specific instructions and constraints.
- Preferred tone and format.
- Word count or length guidelines if relevant.

Ensure the prompt is clear, detailed, and actionable.
Only return the final AI prompt — no commentary or extra text.
"""

# Process flow
def process_prompt_flow(idea, api_key, api_url, model_name=None):
    try:
        base_prompt = generate_prompt_for_idea(idea)
        final_output = send_ai_request(base_prompt, api_key, api_url, model_name)
        print(f"Final generated prompt: {final_output}\n")
        return final_output
    except Exception as e:
        print(f"Error during prompt processing: {e}")
        return "Prompt generation failed."

# POST endpoint with random slug
@app.post("/generate/{slug}")
async def generate_magic_prompt(slug: str, payload: PromptPayload):
    huggingface_api_key = os.getenv("HUGGINGFACE_KEY")
    groq_api_key = os.getenv("GROQ_KEY")

    print(f"\n📥 Received API request with slug: {slug}, idea: {payload.idea}, model: {payload.model}")

    results = {}
    model = payload.model.lower()

    if model == "huggingface":
        output = process_prompt_flow(
            payload.idea, huggingface_api_key,
            "https://api-inference.huggingface.co/models/gpt2"
        )
        results["huggingface"] = output

    if model == "groq":
        output = process_prompt_flow(
            payload.idea, groq_api_key,
            "https://api.groq.com/openai/v1/chat/completions", "llama3-8b-8192"
        )
        results["groq"] = output

    print(f"📤 Returning API response: {results}\n")

    return {
        "slug": slug,
        "idea": payload.idea,
        "model": payload.model,
        "magic_prompt": results
    }

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Prompt API is running! 🎉"}
