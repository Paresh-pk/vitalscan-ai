import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("HF_TOKEN")
if not api_key:
    print("❌ Error: HF_TOKEN not found in .env")
    exit(1)

client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=api_key,
)

models_to_test = [
    "HuggingFaceH4/zephyr-7b-beta",
    "mistralai/Mistral-7B-Instruct-v0.2",
    "google/gemma-1.1-7b-it",
    "meta-llama/Meta-Llama-3-8B-Instruct",
    "Qwen/Qwen2.5-7B-Instruct",
    "microsoft/Phi-3-mini-4k-instruct"
]

print(f"Token loaded: {api_key[:5]}...")

for model in models_to_test:
    print(f"\nTesting model: {model}...")
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": "Test."}
            ],
            max_tokens=10,
            temperature=0.1
        )
        print(f"SUCCESS! {model} is working.")
        print(f"Response: {completion.choices[0].message.content}")
        # Stop after finding the first working model to save time
        break
    except Exception as e:
        print(f"FAILED: {model}")
        print(f"Error: {e}")
