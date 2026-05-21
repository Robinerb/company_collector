import os
from dotenv import load_dotenv
from crewai import LLM

load_dotenv()
try:
    llm = LLM(
        model="gemini/gemini-3.5-flash",
        api_key=os.getenv("GOOGLE_API_KEY")
    )
    print("CrewAI LLM initialized successfully natively:", llm)
except Exception as e:
    print("Error:", e)
