import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from crewai.tools import tool
from langchain_community.tools.tavily_search import TavilySearchResults
from crewai_tools import ScrapeWebsiteTool

load_dotenv()

@tool("search_tool")
def search_tool(query: str):
    """Search internet for strategic pivots and tech stacks."""
    search = TavilySearchResults(k=5)
    return search.run(query)

scrape_tool = ScrapeWebsiteTool()

researcher = Agent(
    role='Deep Tech Market Researcher',
    goal='Analyze EU tech companies for core mission, tech stacks, and pivots in English.',
    backstory='Senior tech analyst. You find hard technical facts. All output must be strictly in English.',
    tools=[search_tool, scrape_tool],
    verbose=True
)

structurer = Agent(
    role='Knowledge Graph Architect',
    goal='Transform research into valid JSON.',
    backstory='Data modeling expert. Output RAW JSON only. All content must be in English.',
    verbose=True
)

# Task 1: Research with salary extraction
task_research = Task(
    description='''Research 3 innovative European companies in Machine Learning or Data Science.
    Find:
    1. Core Business/Mission (1-2 sentences in English).
    2. Exact Tech-Stack.
    3. Strategic Pivot.
    4. Network (competitors/integrations).
    5. Location and hiring status.
    6. Realistic entry salary for an M.Sc. graduate and salary after 3-5 years (in English).''',
    expected_output='Detailed profile of 3 companies in English including salary data.',
    agent=researcher
)

# Task 2: JSON formatting with new salary field
task_json = Task(
    description='''Convert research into EXACT JSON structure. RAW JSON only. MUST be in English:
    {
      "Machine Learning & AI": [
        {
          "name": "Company Name",
          "description": "Crisp 1-2 sentence summary of their product in English.",
          "location": "City, Country",
          "status": "Hiring / Stable",
          "salary": "Entry: ~X EUR | Senior: ~Y EUR",
          "tech_stack": ["Tech1", "Tech2"],
          "pivot": "Short sentence about strategic shift.",
          "network": "Short sentence about competitors/partners."
        }
      ]
    }''',
    expected_output='Raw JSON in English including salary.',
    agent=structurer,
    output_file='dashboard_data.json'
)

crew = Crew(agents=[researcher, structurer], tasks=[task_research, task_json], process=Process.sequential)

if __name__ == "__main__":
    crew.kickoff()
    print("Research complete. Data saved to dashboard_data.json")