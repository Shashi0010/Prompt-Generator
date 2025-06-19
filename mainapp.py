from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import requests

app = FastAPI()

# CORS config to allow your Netlify frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://magic-prompt-generator.netlify.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request body schema
class PromptPayload(BaseModel):
    idea: str
    model: str

# Helper: call the AI API
def send_ai_request(prompt, model_name, api_key, api_url):
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 500
    }
    response = requests.post(api_url, headers=headers, json=payload)
    response.raise_for_status()  # to catch HTTP errors cleanly
    result = response.json()
    return result["choices"][0]["message"]["content"]

# Helper: build the full prompt
def process_prompt_flow(idea, api_key, model_name, url):
    context_instruction = f"You are a senior AI prompt engineer. Define a strategic context for: '{idea}'"
    objective_instruction = f"You are a senior AI strategist. Define an actionable objective for: '{idea}'"

    context_result = send_ai_request(context_instruction, model_name, api_key, url)
    objective_result = send_ai_request(objective_instruction, model_name, api_key, url)

    final_magic_prompt = f"""
    You are an expert AI Prompt Engineer. Choose your years of experience based on the task complexity:
    {context_result}
    Your task is to {objective_result}
    Ensure the content is precise, engaging, outcome-focused, and contextually sound.
    """

    return send_ai_request(final_magic_prompt, model_name, api_key, url)

# POST endpoint
@app.post("/generate/{slug}")
async def generate_magic_prompt(slug: str, payload: PromptPayload):
    openai_api_key = os.getenv("OPENAI_KEY")
    deepseek_api_key = os.getenv("DEEPSEEK_KEY")

    # Initialize result keys to prevent undefined in frontend
    results = {
        "openai": None,
        "deepseek": None
    }

    if payload.model in ["OpenAI GPT-3.5", "Both"]:
        openai_output = process_prompt_flow(
            payload.idea, openai_api_key, "gpt-3.5-turbo", "https://api.openai.com/v1/chat/completions"
        )
        results["openai"] = openai_output

    if payload.model in ["DeepSeek", "Both"]:
        deepseek_output = process_prompt_flow(
            payload.idea, deepseek_api_key, "deepseek-chat", "https://api.deepseek.com/v1/chat/completions"
        )
        results["deepseek"] = deepseek_output

    return {
        "slug": slug,
        "idea": payload.idea,
        "model": payload.model,
        "magic_prompt": results
    }

# Root route test
@app.get("/")
def read_root():
    return {"message": "Prompt API is running! 🎉"}
