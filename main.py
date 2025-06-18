import streamlit as st
import requests
import os
import time

# Set page config
st.set_page_config(page_title="Prompt Sorcery Studio", page_icon="🎆", layout="centered")

# Custom CSS for glass morph, banner background, typewriter animation and styling
st.markdown("""
    <style>
    .main {
        background: linear-gradient(to right, #e0eafc, #cfdef3);
        background-attachment: fixed;
    }
    .banner {
        background-image: url('https://raw.githubusercontent.com/your-repo-path/your-banner.jpg');
        background-size: cover;
        background-position: center;
        border-radius: 16px;
        padding: 60px 20px;
        text-align: center;
        color: white;
        animation: fadeIn 2s ease;
    }
    @keyframes fadeIn {
        from {opacity: 0;}
        to {opacity: 1;}
    }
    .typewriter {
        overflow: hidden;
        border-right: .15em solid #fff;
        white-space: nowrap;
        margin: 0 auto;
        letter-spacing: .1em;
        animation:
          typing 3.5s steps(40, end),
          blink-caret .75s step-end infinite;
    }
    @keyframes typing {
      from { width: 0 }
      to { width: 100% }
    }
    @keyframes blink-caret {
      from, to { border-color: transparent }
      50% { border-color: white; }
    }
    .glass-card {
        background: rgba(255, 255, 255, 0.25);
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        backdrop-filter: blur(8px);
        -webkit-backdrop-filter: blur(8px);
    }
    .feedback-form input, .feedback-form textarea {
        width: 100%;
        padding: 8px;
        margin: 6px 0 12px;
        border: 1px solid #ccc;
        border-radius: 8px;
    }
    .coffee-btn {
        display: inline-block;
        background: #ffdd00;
        color: #333;
        padding: 10px 20px;
        border-radius: 50px;
        text-decoration: none;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# App Banner and Heading
st.markdown("""
<div class='banner'>
  <h1>🪄 Prompt Sorcery Studio 🪄</h1>
  <h4 class='typewriter'>Your ideas are vague. Our AI makes them Vogue.</h4>
</div>
""", unsafe_allow_html=True)

# Input Card Container
with st.container():
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)

    idea = st.text_area("💡 Enter your casual idea:")
    model_choice = st.selectbox("Select AI Model", ["OpenAI GPT-3.5", "DeepSeek", "Both"])

    if st.button("✨ Tailor My Magic Prompt"):
        if idea.strip() == "":
            st.warning("Please enter an idea first.")
        else:
            with st.spinner("Casting your prompt sorcery... 🧙‍♂️✨"):
                time.sleep(2.5)

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

                openai_api_key = st.secrets["OPENAI_KEY"]
                deepseek_api_key = st.secrets["DEEPSEEK_KEY"]

                def process_prompt_flow(api_key, model_name, url):
                    context_instruction = f"""
You are a senior AI prompt engineer and strategy consultant.
Infer and define a clear, strategic context.
Return one smart sentence.
Idea: "{idea}"
"""
                    objective_instruction = f"""
You are a senior AI prompt engineer and creative strategist.
Infer and define a clear, actionable objective.
Return one smart sentence.
Idea: "{idea}"
"""
                    context_result = send_ai_request(context_instruction, model_name, api_key, url)
                    objective_result = send_ai_request(objective_instruction, model_name, api_key, url)
                    final_magic_prompt = f"""
You are an expert AI Prompt Engineer with 10+ years of experience working with global brands.
{context_result}
Your task is to {objective_result}
Make the content precise, engaging, and outcome-focused.
"""
                    final_output = send_ai_request(final_magic_prompt, model_name, api_key, url)
                    return final_output

                if model_choice in ["OpenAI GPT-3.5", "Both"]:
                    openai_output = process_prompt_flow(openai_api_key, "gpt-3.5-turbo", "https://api.openai.com/v1/chat/completions")
                    st.subheader("🎯 Magic Prompt by OpenAI")
                    st.write(openai_output)

                if model_choice in ["DeepSeek", "Both"]:
                    deepseek_output = process_prompt_flow(deepseek_api_key, "deepseek-chat", "https://api.deepseek.com/v1/chat/completions")
                    st.subheader("🎯 Magic Prompt by DeepSeek")
                    st.write(deepseek_output)

    st.markdown("</div>", unsafe_allow_html=True)

# Feedback Form
st.markdown("""
    <h4 style='text-align: center;'>📢 Feedback & Suggestions</h4>
    <div class='glass-card feedback-form'>
        <form action="https://formsubmit.co/YOUR_EMAIL" method="POST">
            <input type="text" name="name" placeholder="Your Name" required>
            <input type="email" name="email" placeholder="Your Email" required>
            <textarea name="message" placeholder="Your feedback here..." rows="4" required></textarea>
            <button type="submit" style="background-color: #ff7b00; color: white; padding: 8px 16px; border-radius: 8px; border: none;">Send Feedback</button>
        </form>
    </div>
""", unsafe_allow_html=True)

# Buy Me a Coffee button
st.markdown("""
    <div style='text-align: center; padding-top: 16px;'>
        <a class='coffee-btn' href='https://www.buymeacoffee.com/yourprofile' target='_blank'>☕ Buy Me a Coffee ($1)</a>
    </div>
""", unsafe_allow_html=True)
