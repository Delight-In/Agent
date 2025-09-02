# content.py

import os
import requests
from dotenv import load_dotenv

load_dotenv()

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")


def generate_content(mode, recipient_name=None, perplexity='medium'):
    """
    Generates a message based on the communication mode and perplexity level.
    Personalizes the message using the recipient's name if available.
    """

    name_part = f"{recipient_name}, " if recipient_name else ""

    if mode == 'sms':
        if perplexity == 'low':
            return f"Hi {name_part}just a reminder about your appointment."
        elif perplexity == 'high':
            return f"Hello {name_part}this is a gentle reminder regarding your upcoming appointment. Please don’t hesitate to reach out if you need assistance."
        return f"Hi {name_part}this is a quick reminder about your upcoming appointment. Let us know if you have any questions."

    elif mode == 'email':
        if perplexity == 'low':
            return (
                f"Hi {recipient_name if recipient_name else 'there'},\n\n"
                "Just following up on your recent request. Let us know if you need help.\n\n"
                "Thanks,\nSupport Team"
            )
        elif perplexity == 'high':
            return (
                f"Dear {recipient_name if recipient_name else 'Customer'},\n\n"
                "We hope this message finds you well. We're writing to follow up on your recent inquiry. "
                "If there's anything further we can assist you with, please feel free to reach out at your convenience.\n\n"
                "Warm regards,\nSupport Team"
            )
        return (
            f"Dear {recipient_name if recipient_name else 'Customer'},\n\n"
            "We hope you're doing well. This is a follow-up email regarding your recent request. "
            "Please let us know how we can assist you further.\n\n"
            "Best regards,\nSupport Team"
        )

    elif mode == 'whatsapp':
        if perplexity == 'low':
            return f"Hey {name_part}everything good? Let us know if you need anything."
        elif perplexity == 'high':
            return f"Hello {name_part}just reaching out to ensure everything is going smoothly. We're here to assist with anything you may need."
        return f"Hey {name_part}just checking in! Let us know if you need any assistance or have any questions."

    elif mode == 'call':
        if perplexity == 'low':
            return f"Hi {name_part}this is a follow-up call. Call us back if needed."
        elif perplexity == 'high':
            return (
                f"Hello {name_part}this is an automated call from our customer service team. "
                "We're following up regarding your recent interaction. If you have any questions, please remain on the line to speak with a representative."
            )
        return (
            f"Hello {name_part}this is an automated call from our team. "
            "We wanted to follow up with you regarding your recent interaction. "
            "If you have any questions, please stay on the line to be connected with a representative."
        )

    else:
        return "Unsupported communication mode selected. Please choose SMS, Email, WhatsApp, or Call."


def generate_with_llm(mode, recipient_name=None, perplexity='medium'):
    """
    Generate a message using the Perplexity LLM API.
    Falls back to error message if API key is missing or request fails.
    """

    if not PERPLEXITY_API_KEY:
        return "[ERROR] Missing Perplexity API key in environment."

    name = recipient_name or "Customer"

    prompt = (
        f"Write a {perplexity} complexity message for a {mode.upper()} format. "
        f"Make it professional and friendly. Address the person as {name}. "
        f"Include a brief follow-up or support offer."
    )

    try:
        response = requests.post(
            "https://api.perplexity.ai/chat/completions",
            headers={
                "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "pplx-7b-online",  # You can also try 'pplx-70b-online'
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7
            }
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

    except requests.exceptions.RequestException as e:
        return f"[ERROR] Perplexity API request failed: {e}"
