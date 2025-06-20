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
    print(f"API response for {model_name}: {result}")
    return result["choices"][0]["message"]["content"]

# Helper: Build prompt flow with debug logs
def process_prompt_flow(idea, api_key, model_name, url):
    print(f"\nProcessing idea: {idea} with {model_name} at {url}")

    try:
        context_instruction = f"You are a senior AI prompt engineer. Define a strategic context for: '{idea}'"
        context_result = send_ai_request(context_instruction, model_name, api_key, url)
        print(f"Context result: {context_result}")

        objective_instruction = f"You are a senior AI strategist. Define an actionable objective for: '{idea}'"
        objective_result = send_ai_request(objective_instruction, model_name, api_key, url)
        print(f"Objective result: {objective_result}")
        print(f"Processing prompt for model: {model_name}, API key present: {bool(api_key)}")
        final_magic_prompt = f"""
        You are an expert AI Prompt Engineer. Decide an appropriate number of years of experience for yourself based on the complexity and depth of the following task and mention it naturally in the prompt:
        {context_result}
        Your task is to {objective_result}
        Ensure the content is precise, engaging, outcome-focused, and contextually sound.
        """
        final_output = send_ai_request(final_magic_prompt, model_name, api_key, url)
        print(f"Final magic prompt result: {final_output}\n")

        return final_output

    except Exception as e:
        print(f"Error during prompt processing: {e}")
        return "Prompt generation failed."

# POST endpoint with random slug
@app.post("/generate/{slug}")
async def generate_magic_prompt(slug: str, payload: PromptPayload):
    openai_api_key = os.getenv("OPENAI_KEY")
    deepseek_api_key = os.getenv("DEEPSEEK_KEY")

    print(f"🔑 OPENAI_KEY: {openai_api_key}")
    print(f"🔑 DEEPSEEK_KEY: {deepseek_api_key}")

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

    print(f"Returning API response: {results}")

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
