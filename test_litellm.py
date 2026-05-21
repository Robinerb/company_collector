import os
import litellm
from dotenv import load_dotenv

load_dotenv()
os.environ["GEMINI_API_KEY"] = os.getenv("GOOGLE_API_KEY")

print("Gemini API Key:", os.environ["GEMINI_API_KEY"][:10])

try:
    response = litellm.completion(
        model="gemini/gemini-1.5-flash",
        messages=[{"role": "user", "content": "say hello"}]
    )
    print("Response:")
    print(response.choices[0].message.content)
except Exception as e:
    print("Error:", e)
