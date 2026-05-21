import os
from dotenv import load_dotenv
from langchain_community.tools.tavily_search import TavilySearchResults

load_dotenv()
print("Tavily API Key:", os.getenv("Tavily_API_KEY") or os.getenv("TAVILY_API_KEY"))

try:
    search = TavilySearchResults(k=3)
    results = search.run("Machine learning companies Germany")
    print("Search results:")
    print(results)
except Exception as e:
    print("Error:", e)
