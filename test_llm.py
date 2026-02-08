import os
from openai import OpenAI
from dotenv import load_dotenv

# Force load .env
load_dotenv()

api_key = os.getenv("HF_TOKEN")
print(f"Loaded Token: {api_key[:5]}...{api_key[-5:] if api_key else 'None'}")

if not api_key:
    print("ERROR: No Token Found")
    exit(1)

client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=api_key,
)

try:
    print("Sending request to Hugging Face...")
    completion = client.chat.completions.create(
        model="Qwen/Qwen2.5-Coder-32B-Instruct",
        messages=[
            {"role": "system", "content": "You are a knowledgeable and empathetic health assistant for VITALSCAN, an AI-powered preventive health platform. Your role is to provide evidence-based, actionable health advice. NEVER diagnose medical conditions."},
            {"role": "user", "content": "I have high blood pressure and diabetes. what should I do?"}
        ],
        temperature=0.7,
        max_tokens=1000
    )
    print("Response received:")
    print(completion.choices[0].message.content)

except Exception as e:
    print(f"API CALL FAILED: {e}")
