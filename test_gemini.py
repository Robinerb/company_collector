import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

test_models = [
    "gemini-2.5-flash",
    "gemini-2.5-pro",
    "gemini-2.0-flash",
    "gemini-flash-latest",
    "gemini-pro-latest",
    "gemini-1.5-flash",
    "gemini-1.5-pro"
]

for model in test_models:
    print(f"Testing model: {model}...")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{"parts": [{"text": "Say hello!"}]}]
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        print("  Status Code:", response.status_code)
        if response.status_code == 200:
            print("  ✅ SUCCESS!")
            print("  Response:", response.json().get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text'))
            break
        else:
            print("  ❌ Failed:", response.json().get('error', {}).get('message'))
    except Exception as e:
        print("  Error:", e)
