# content.py

import os
import requests
import json
from dotenv import load_dotenv

# Load API key from .env
load_dotenv()
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")


def generate_content(mode, user_need, subject=None, recipient_name=None, complexity='medium'):
    if not PERPLEXITY_API_KEY:
        return "[ERROR] Missing Perplexity API key in environment."

    name = recipient_name or "Student"

    # User-facing prompt
    user_prompt = (
        f"A university councelling team on {subject}. "
        f"They want to {user_need}. "
        f"Generate a {mode.upper()} message addressed to {name}, using {complexity} complexity. "
        f"Keep it friendly and professional. End with a follow-up offer for support and detailed info about university."
    )

    # Prepare API request
    url = "https://api.perplexity.ai/chat/completions"
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "sonar-pro",  # ✅ Use valid model
        "messages": [
            {"role": "system", "content": "You are a helpful assistant for university counseling team to student about admission opened."},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.7
    }


    try:
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 400:
            print("\n[ERROR] 400 Bad Request")
            try:
                error_info = response.json()
                print(json.dumps(error_info, indent=2))
            except Exception:
                print(response.text)
            return "[ERROR] Bad Request. Check model name or input."

        response.raise_for_status()

        data = response.json()
        return data["choices"][0]["message"]["content"]

    except requests.exceptions.RequestException as e:
        print(f"[ERROR] API request failed: {e}")
        return f"[ERROR] Request failed: {e}"


if __name__ == "__main__":
    mode = "email"
    university = "MIT"
    user_need = "ask about scholarship options and the admission process"
    recipient_name = "Admissions Team"
    complexity = "medium"

    result = generate_content(mode, university, user_need, recipient_name, complexity)
    print("\n[RESULT]")
    print(result)

























# import os
# from dotenv import load_dotenv
# from langchain.chains import LLMChain
# from langchain.prompts import PromptTemplate
# from langchain.chat_models import ChatOpenAI  # Use if Perplexity is OpenAI-compatible

# # Load env variables
# load_dotenv()
# PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")

# def generate_content_lc(mode, university, user_need, recipient_name=None, complexity='medium'):
#     if not PERPLEXITY_API_KEY:
#         return "[ERROR] Missing Perplexity API key."

#     name = recipient_name or "Student"

#     # Construct prompt using LangChain's PromptTemplate
#     template = (
#         "You are a helpful university counseling assistant at {university}. "
#         "You are preparing a {mode} to {recipient_name}. "
#         "The goal is to {user_need}. "
#         "Use a {complexity} level of language. "
#         "Keep the tone friendly and professional. "
#         "End with an offer for further support and additional university details."
#     )

#     prompt = PromptTemplate(
#         input_variables=["university", "mode", "user_need", "recipient_name", "complexity"],
#         template=template,
#     )

#     # Use the OpenAI-compatible wrapper for Perplexity
#     llm = ChatOpenAI(
#         model="sonar-pro",
#         temperature=0.7,
#         openai_api_key=PERPLEXITY_API_KEY,
#         base_url="https://api.perplexity.ai",  # required if it's not the default OpenAI endpoint
#     )

#     chain = LLMChain(llm=llm, prompt=prompt)

#     # Run the chain
#     result = chain.run({
#         "university": university,
#         "mode": mode,
#         "user_need": user_need,
#         "recipient_name": name,
#         "complexity": complexity,
#     })

#     return result


# if __name__ == "__main__":
#     mode = "email"
#     university = "MIT"
#     user_need = "ask about scholarship options and the admission process"
#     recipient_name = "Admissions Team"
#     complexity = "medium"

#     response = generate_content_lc(mode, university, user_need, recipient_name, complexity)
#     print("\n[RESULT]")
#     print(response)
