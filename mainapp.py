from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import os

app = FastAPI()
openai_api_key = os.getenv("OPENAI_KEY")
deepseek_api_key = os.getenv("DEEPSEEK_KEY")

# CORS for local dev + Netlify frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://magic-prompt-generator.netlify.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
)

class PromptRequest(BaseModel):
    idea: str
    model: str

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

def process_prompt_flow(idea, api_key, model_name, url):
    context_instruction = f"You are a senior AI prompt engineer. Define a strategic context for: '{idea}'"
    objective_instruction = f"You are a senior AI strategist. Define an actionable objective for: '{idea}'"

    context_result = send_ai_request(context_instruction, model_name, api_key, url)
    objective_result = send_ai_request(objective_instruction, model_name, api_key, url)

    final_magic_prompt = f"""
You are an expert AI Prompt Engineer with 10+ years experience.
{context_result}
Your task is to {objective_result}
Keep it precise, engaging, and outcome-focused.
"""

    final_output = send_ai_request(final_magic_prompt, model_name, api_key, url)
    return final_output

@app.get("/")
def read_root():
    return {"message": "Prompt API is running! 🎉"}

@app.get("/generate")
def generate_magic_prompt(idea: str = Query(...), model: str = Query(...)):
    openai_api_key = os.getenv("OPENAI_KEY")
    deepseek_api_key = os.getenv("DEEPSEEK_KEY")

    results = {}

    if model in ["OpenAI GPT-3.5", "Both"]:
        openai_output = process_prompt_flow(
            idea, openai_api_key, "gpt-3.5-turbo", "https://api.openai.com/v1/chat/completions"
        )
        results["openai"] = openai_output

    if model in ["DeepSeek", "Both"]:
        deepseek_output = process_prompt_flow(
            idea, deepseek_api_key, "deepseek-chat", "https://api.deepseek.com/v1/chat/completions"
        )
        results["deepseek"] = deepseek_output

    return {"idea": idea, "model": model, "magic_prompt": results}
