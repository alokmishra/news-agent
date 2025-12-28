from fasthtml.common import *
from db import Database
from mailer import EmailSender
import random
import os
import json
from dotenv import load_dotenv
import asyncio

load_dotenv()

# Initialize Singletons
db = Database()
config = {
    'sender_email': os.getenv('SENDER_EMAIL'),
    'google_api_key': os.getenv('GOOGLE_API_KEY') # Not needed for mailer but might be for other things
}
mailer = EmailSender(config)

app, rt = fast_app()

def generate_otp():
    return str(random.randint(100000, 999999))

@rt('/')
def get():
    css = """
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f0f2f5; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }
        .container { background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); width: 100%; max-width: 400px; }
        h1 { color: #1a1a1a; font-size: 1.5rem; margin-bottom: 0.5rem; text-align: center; }
        p { color: #666; font-size: 0.9rem; text-align: center; margin-bottom: 2rem; }
        form { display: flex; flex-direction: column; gap: 1rem; }
        label { font-weight: 500; font-size: 0.9rem; color: #333; margin-bottom: 0.25rem; display: block; }
        input { width: 100%; padding: 0.75rem; border: 1px solid #ddd; border-radius: 6px; font-size: 1rem; transition: border-color 0.2s; box-sizing: border-box; }
        input:focus { border-color: #2563eb; outline: none; }
        button { background-color: #2563eb; color: white; padding: 0.75rem; border: none; border-radius: 6px; font-size: 1rem; font-weight: 600; cursor: pointer; transition: background-color 0.2s; }
        button:hover { background-color: #1d4ed8; }
        .error { color: #dc2626; font-size: 0.875rem; text-align: center; }
        .success { color: #16a34a; font-size: 0.875rem; text-align: center; }
    """
    return (
        Title("News Agent Subscription"),
        Head(Style(css)),
        Body(
            Div(
                H1("Daily News Digest"),
                P("Curated news and analysis delivered to your inbox."),
                Form(
                    Div(Label("Topic 1"), Input(type="text", name="topic1", required=True, placeholder="e.g. Artificial Intelligence")),
                    Div(Label("Topic 2"), Input(type="text", name="topic2", required=True, placeholder="e.g. Climate Change")),
                    Div(Label("Topic 3"), Input(type="text", name="topic3", required=True, placeholder="e.g. Global Economy")),
                    Div(Label("Email Address"), Input(type="email", name="email", required=True, placeholder="you@example.com")),
                    Button("Subscribe", type="submit"),
                    hx_post="/subscribe",
                    hx_target="#content",
                    hx_swap="innerHTML"
                ),
                id="content",
                cls="container"
            )
        )
    )

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

# Initialize Validator Model
# Using flash model for speed if available, or just standard pro
validator_model = ChatGoogleGenerativeAI(model="gemini-3-pro-preview", api_key=os.getenv("GOOGLE_API_KEY"))

async def validate_topic(topic: str) -> bool:
    try:
        msg = HumanMessage(content=f"Is the text '{topic}' a valid, meaningful topic for a news research agent? It must be a real word or concept in English, not random junk characters, gibberish, or spam. Respond with only 'VALID' or 'INVALID'.")
        response = await validator_model.ainvoke([msg])
        return response.text.strip().upper()
    except Exception as e:
        print(f"Validation error for {topic}: {e}")
        # Fallback to len check if LLM fails
        return len(topic) > 2

@rt('/subscribe')
async def post(topic1: str, topic2: str, topic3: str, email: str):
    raw_topics = [t.strip() for t in [topic1, topic2, topic3] if t.strip()]
    if len(raw_topics) < 1:
        return P("Please provide at least one topic.", style="color: red;")
    
    # 1. Deduplicate
    topics = list(set(raw_topics))
    
    # 2. Validate Topics via LLM
    # Run keys in parallel for speed
    results = await asyncio.gather(*[validate_topic(t) for t in topics])
    
    invalid_topics = [t for t, is_valid in zip(topics, results) if is_valid != "VALID"]
    print(invalid_topics)
    if invalid_topics:
        return Div(
            P(f"The following topics appear to be invalid or gibberish: {', '.join(invalid_topics)}", style="color: red; font-weight: bold;"),
            P("Please enter valid English topics or concepts.", style="color: #666;"),
            Form(
                Div(Label("Topic 1", Input(type="text", name="topic1", value=topic1, required=True)),
                    cls="error-field" if topic1 in invalid_topics else ""),
                Div(Label("Topic 2", Input(type="text", name="topic2", value=topic2, required=True)),
                    cls="error-field" if topic2 in invalid_topics else ""),
                Div(Label("Topic 3", Input(type="text", name="topic3", value=topic3, required=True)),
                    cls="error-field" if topic3 in invalid_topics else ""),
                Div(Label("Email Address", Input(type="email", name="email", value=email, required=True))),
                Button("Try Again", type="submit"),
                hx_post="/subscribe",
                hx_target="#content",
                hx_swap="innerHTML"
            ),
            cls="container"
        )

    otp = generate_otp()
    
    # Save to UserDB (pending verification)
    db.upsert_user(email, json.dumps(topics), otp)
    
    # Send OTP Email
    try:
        html_content = mailer.render_otp_template(otp)
        await mailer.send_email("Your Verification Code", html_content, to_email=email)
    except Exception as e:
        return P(f"Error sending email: {e}", style="color: red;")

    return Div(
        H2("Verify your Email"),
        P(f"We sent a verification code to {email}."),
        Form(
            Input(type="hidden", name="email", value=email),
            Label("Enter OTP", Input(type="text", name="otp", required=True)),
            Button("Verify", type="submit"),
            hx_post="/verify",
            hx_target="#content",
            hx_swap="innerHTML"
        )
    )

@rt('/verify')
def post(email: str, otp: str):
    # Verify OTP
    record = db.get_user_otp(email)
    if not record:
        return P("User not found.", style="color: red;")
    
    stored_otp, created_at = record
    if stored_otp != otp:
        return Div(
            P("Invalid OTP. Please try again.", style="color: red;"),
            Form(
                Input(type="hidden", name="email", value=email),
                Label("Enter OTP", Input(type="text", name="otp", required=True)),
                Button("Verify", type="submit"),
                hx_post="/verify",
                hx_target="#content",
                hx_swap="innerHTML"
            )
        )
    
    # Mark Verified
    db.verify_user(email)
    
    return Div(
        H2("Subscription Successful!"),
        P("You have successfully subscribed to the daily digest."),
        P("You will receive your first email tomorrow morning.")
    )

serve()
