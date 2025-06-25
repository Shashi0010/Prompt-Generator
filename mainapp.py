from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PromptPayload(BaseModel):
    idea: str
    models: list

def send_ai_request(prompt, model_name, api_key, api_url, is_huggingface=False):
    print(f"\n➡️ Sending AI request to {api_url} with model {model_name}")
    headers = {"Authorization": f"Bearer {api_key}"}
    if is_huggingface:
        payload = {"inputs": prompt}
    else:
        headers["Content-Type"] = "application/json"
        payload = {
            "model": model_name,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 500
        }

    response = requests.post(api_url, headers=headers, json=payload)
    print(f"Raw response: {response.text}")

    try:
        result = response.json()
        if is_huggingface:
            return result[0]['generated_text']
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"❌ Error: {e}")
        return "Prompt generation failed."

def generate_prompt_for_idea(idea):
    return f"""
Act as a world-class AI prompt engineer.

Given the idea: "{idea}"

Craft a fully structured prompt including:
- Role for AI
- Context setting
- Approach
- Specific instructions
- Tone & format
- Word limit if needed

Return only the final prompt text.
"""

def process_prompt_flow(idea, api_key, model_name, url, is_huggingface=False):
    try:
        final_prompt = generate_prompt_for_idea(idea)
        return send_ai_request(final_prompt, model_name, api_key, url, is_huggingface)
    except Exception as e:
        print(f"❌ Error during prompt processing: {e}")
        return "Prompt generation failed."

@app.post("/generate/{slug}")
async def generate_magic_prompt(slug: str, payload: PromptPayload):
    results = {}
    print(f"\n📥 API request: slug={slug}, idea={payload.idea}, models={payload.models}")

    for model in payload.models:
        if model == "gpt-3.5":
            output = process_prompt_flow(payload.idea, os.getenv("OPENAI_KEY"), "gpt-3.5-turbo", "https://api.openai.com/v1/chat/completions")
            results[model] = output

        elif model == "openrouter-free":
            output = process_prompt_flow(payload.idea, os.getenv("OPENROUTER_KEY"), "gpt-3.5-turbo", "https://openrouter.ai/api/v1/chat/completions")
            results[model] = output

        elif model == "google-gemini-free":
            output = process_prompt_flow(payload.idea, os.getenv("OPENROUTER_KEY"), "google/gemini-pro", "https://openrouter.ai/api/v1/chat/completions")
            results[model] = output

        elif model == "mistral-7b-open":
            output = process_prompt_flow(payload.idea, os.getenv("HUGGINGFACE_KEY"), "mistralai/Mistral-7B-v0.1", "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-v0.1", True)
            results[model] = output

    print(f"📤 Returning API response: {results}\n")
    return {"slug": slug, "idea": payload.idea, "models": payload.models, "magic_prompt": results}

@app.get("/")
def read_root():
    return {"message": "Prompt API is running 🚀"}
