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
def send_ai_request(prompt, model_name, api_key, api_url):
    print(f"\nSending AI request to {api_url} with model {model_name}")
    print(f"Prompt content: {prompt}\n")
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 500
    }

    response = requests.post(api_url, headers=headers, json=payload)
    print(f"API raw response: {response.text}\n")

    result = response.json()
    print(f"API response JSON: {result}")
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
def process_prompt_flow(idea, api_key, model_name, url):
    try:
        base_prompt = generate_prompt_for_idea(idea)
        final_output = send_ai_request(base_prompt, model_name, api_key, url)
        print(f"Final generated prompt: {final_output}\n")
        return final_output
    except Exception as e:
        print(f"Error during prompt processing: {e}")
        return "Prompt generation failed."

# POST endpoint with random slug
@app.post("/generate/{slug}")
async def generate_magic_prompt(slug: str, payload: PromptPayload):
    openai_api_key = os.getenv("OPENAI_KEY")
    deepseek_api_key = os.getenv("DEEPSEEK_KEY")

    print(f"\n📥 Received API request with slug: {slug}, idea: {payload.idea}, model: {payload.model}")
    print(f"🔑 OPENAI_KEY present: {bool(openai_api_key)}")
    print(f"🔑 DEEPSEEK_KEY present: {bool(deepseek_api_key)}")

    results = {}
    model = payload.model.lower()

    if model in ["gpt-3.5", "both"]:
        openai_output = process_prompt_flow(
            payload.idea, openai_api_key, "gpt-3.5-turbo", "https://api.openai.com/v1/chat/completions"
        )
        results["openai"] = openai_output

    if model in ["deepseek", "both"]:
        deepseek_output = process_prompt_flow(
            payload.idea, deepseek_api_key, "deepseek-chat", "https://api.deepseek.com/v1/chat/completions"
        )
        results["deepseek"] = deepseek_output

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
