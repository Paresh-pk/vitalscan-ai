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
        model="HuggingFaceH4/zephyr-7b-beta",
        messages=[
            {"role": "system", "content": "You are a helper."},
            {"role": "user", "content": "Say 'Health Check Passed' if you can hear me."}
        ],
        temperature=0.7,
        max_tokens=50
    )
    print("Response received:")
    print(completion.choices[0].message.content)

except Exception as e:
    print(f"API CALL FAILED: {e}")
