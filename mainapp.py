from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://magic-prompt-generator.netlify.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PromptPayload(BaseModel):
    idea: str
    models: list

def send_ai_request(prompt, model_name, api_key, api_url):
    print(f"\nSending AI request to {api_url} with model {model_name}")
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 500
    }
    response = requests.post(api_url, headers=headers, json=payload)
    print(f"API raw response: {response.text}\n")
    result = response.json()
    return result.get("choices", [{}])[0].get("message", {}).get("content", "Prompt generation failed.")

def generate_prompt_for_idea(idea):
    return f"""
Act as a world-class expert prompt engineer.
Given the following raw idea: \"{idea}\"
Your job is to craft a fully structured, actionable AI prompt including:
- A professional role for the AI.
- Clear context.
- Step-by-step strategy.
- Instructions and constraints.
- Preferred tone and format.
- Length guidance if relevant.
Return only the final prompt.
"""

@app.post("/generate/{slug}")
async def generate_magic_prompt(slug: str, payload: PromptPayload):
    print(f"\n📥 Received API request with slug: {slug}, idea: {payload.idea}, models: {payload.models}")

    results = {}
    openai_api_key = os.getenv("OPENAI_KEY")
    openrouter_key = os.getenv("OPENROUTER_KEY")  # Example additional keys
    gemini_key = os.getenv("GEMINI_KEY")

    for model in payload.models:
        prompt_text = generate_prompt_for_idea(payload.idea)

        if model == "gpt-3.5":
            result = send_ai_request(prompt_text, "gpt-3.5-turbo", openai_api_key, "https://api.openai.com/v1/chat/completions")
            results[model] = result
        elif model == "openrouter-free":
            result = send_ai_request(prompt_text, "openrouter-free", openrouter_key, "https://api.openrouter.ai/v1/chat/completions")
            results[model] = result
        elif model == "google-gemini-free":
            result = send_ai_request(prompt_text, "gemini-pro", gemini_key, "https://api.gemini.com/v1/chat/completions")
            results[model] = result
        elif model == "mistral-7b-open":
            result = send_ai_request(prompt_text, "mistral-7b-open", openrouter_key, "https://api.openrouter.ai/v1/chat/completions")
            results[model] = result
        else:
            results[model] = "Unsupported model or config missing."

    print(f"📤 Returning API response: {results}\n")

    return {
        "slug": slug,
        "idea": payload.idea,
        "models": payload.models,
        "magic_prompt": results
    }

@app.get("/")
def read_root():
    return {"message": "Prompt API is running! 🎉"}
