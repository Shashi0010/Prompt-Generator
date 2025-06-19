from fastapi import FastAPI, Body
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

# Helper: Send AI request
def send_ai_request(prompt, model_name, api_key, api_url):
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 500
    }
    response = requests.post(api_url, headers=headers, json=payload)
    result = response.json()
    return result["choices"][0]["message"]["content"]

# Helper: Build prompt
def process_prompt_flow(idea, api_key, model_name, url):
    context_instruction = f"You are a senior AI prompt engineer. Define a strategic context for: '{idea}'"
    objective_instruction = f"You are a senior AI strategist. Define an actionable objective for: '{idea}'"

    context_result = send_ai_request(context_instruction, model_name, api_key, url)
    objective_result = send_ai_request(objective_instruction, model_name, api_key, url)

    final_magic_prompt = f"""
        You are an expert AI Prompt Engineer. Decide an appropriate number of years of experience for yourself based on the complexity and depth of the following task and mention it naturally in the prompt:
        {context_result}
        Your task is to {objective_result}
        Ensure the content is precise, engaging, outcome-focused, and contextually sound.
        """

    final_output = send_ai_request(final_magic_prompt, model_name, api_key, url)
    return final_output


# ✅ POST endpoint with random slug
@app.post("/generate/{slug}")
async def generate_magic_prompt(slug: str, payload: PromptPayload):
    openai_api_key = os.getenv("OPENAI_KEY")
    deepseek_api_key = os.getenv("DEEPSEEK_KEY")

    results = {}

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

# Optional: root path test
@app.get("/")
def read_root():
    return {"message": "Prompt API is running! 🎉"}
