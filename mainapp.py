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
    model: str

def send_ai_request(prompt, model_name, api_key, api_url):
    print(f"Sending AI request to {model_name} with prompt:\n{prompt}\n")
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 500
    }
    response = requests.post(api_url, headers=headers, json=payload)
    print("Raw API Response:", response.status_code, response.text)
    result = response.json()
    return result["choices"][0]["message"]["content"]

def process_prompt_flow(idea, api_key, model_name, url):
    print(f"Processing prompt flow for {model_name}...")
    context_instruction = f"You are a senior AI prompt engineer. Define a strategic context for: '{idea}'"
    objective_instruction = f"You are a senior AI strategist. Define an actionable objective for: '{idea}'"

    context_result = send_ai_request(context_instruction, model_name, api_key, url)
    print(f"Context result: {context_result}")

    objective_result = send_ai_request(objective_instruction, model_name, api_key, url)
    print(f"Objective result: {objective_result}")

    final_magic_prompt = f"""
You are an expert AI Prompt Engineer. Decide an appropriate number of years of experience for yourself based on the complexity and depth of the following task:
{context_result}
Your task is to {objective_result}
Ensure content is precise, engaging, outcome-focused, and contextually sound.
"""
    final_output = send_ai_request(final_magic_prompt, model_name, api_key, url)
    print(f"Final generated prompt: {final_output}")
    return final_output

@app.post("/generate/{slug}")
async def generate_magic_prompt(slug: str, payload: PromptPayload):
    print(f"Received API request with slug: {slug}, idea: {payload.idea}, model: {payload.model}")
    openai_api_key = os.getenv("OPENAI_KEY")
    deepseek_api_key = os.getenv("DEEPSEEK_KEY")

    results = {}

    if payload.model in ["OpenAI GPT-3.5", "Both"]:
        results["openai"] = process_prompt_flow(
            payload.idea, openai_api_key, "gpt-3.5-turbo", "https://api.openai.com/v1/chat/completions"
        )

    if payload.model in ["DeepSeek", "Both"]:
        results["deepseek"] = process_prompt_flow(
            payload.idea, deepseek_api_key, "deepseek-chat", "https://api.deepseek.com/v1/chat/completions"
        )

    print("Returning API response:", results)

    return {
        "slug": slug,
        "idea": payload.idea,
        "model": payload.model,
        "magic_prompt": results
    }

@app.get("/")
def read_root():
    return {"message": "Prompt API is running! 🎉"}
