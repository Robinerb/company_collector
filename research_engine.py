import os
import json
import requests
from dotenv import load_dotenv
from langchain_community.tools.tavily_search import TavilySearchResults

# Load environment variables
load_dotenv("/Users/robin/Lokal/Programmieren/company_collector/.env")
api_key = os.getenv("GOOGLE_API_KEY")

def run_research():
    print("=" * 60)
    print("🚀 STARTING INCREMENTAL RESEARCH ENGINE (Tavily + Gemini 2.5 Flash-Lite) 🚀")
    print("=" * 60)
    
    # 1. Load existing company database if present
    existing_companies = []
    existing_names = []
    file_path = 'raw_research_data.json'
    
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                existing_companies = json.load(f)
                existing_names = [c.get("name") for c in existing_companies if c.get("name")]
            print(f"Loaded {len(existing_companies)} existing companies from '{file_path}'.")
            print("Existing companies to avoid:", ", ".join(existing_names))
        except Exception as e:
            print(f"⚠️ Warning loading existing database: {e}. Starting fresh.")
            existing_companies = []
            existing_names = []
            
    # Determine how many companies to discover
    is_incremental = len(existing_companies) > 0
    num_to_discover = 5 if is_incremental else 10
    print(f"Goal: Discover and validate exactly {num_to_discover} { 'NEW' if is_incremental else 'SEED' } companies.")

    # 2. Programmatic Web Searches with Tavily
    print("Performing programmatic search for DACH-NL ML/AI companies...")
    search = TavilySearchResults(k=8) # Increased search breadth to find more candidates
    
    search_queries = [
        "Top Machine Learning and AI startups Germany Berlin Munich Hamburg DACH",
        "Innovative deep tech AI startups Amsterdam Netherlands NL",
        "Helsing AI Munich, Aleph Alpha Heidelberg, Black Forest Labs Freiburg, dida Machine Learning, Celonis, Pruna AI, Mindpeak Hamburg, Noah Labs",
        "Machine Learning Engineer entry senior salary Germany DACH Glassdoor Kununu trends"
    ]
    
    aggregated_search_results = []
    for idx, query in enumerate(search_queries):
        print(f"Running Tavily Search {idx+1}/{len(search_queries)}: '{query}'...")
        try:
            results = search.run(query)
            aggregated_search_results.append({
                "query": query,
                "results": results
            })
        except Exception as e:
            print(f"⚠️ Search error for query '{query}': {e}")
            
    # 3. Package and send search data to Gemini 2.5 Flash-Lite in JSON mode
    print("\nProcessing gathered data with Gemini 2.5 Flash-Lite...")
    model = "gemini-2.5-flash-lite"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    
    system_instruction = (
        "You are an elite technology scout and strict data validator specializing in Deep Tech, Machine Learning, and AI. "
        "Your task is to analyze raw search data, filter out marketing fluff, and discover new active companies "
        "in the DACH-NL region specializing in Machine Learning, Deep Tech, or AI. "
        "You must strictly avoid recommending any companies that are already in the list of existing companies. "
        "Generate only valid raw JSON. Do not include markdown code block wrappers (e.g. ```json) in your final response."
    )
    
    avoid_list_str = ", ".join([f'"{name}"' for name in existing_names])
    
    prompt = f"""
    Based on the aggregated search results below, compile exactly {num_to_discover} distinct, active companies working in Machine Learning, AI, or Deep Tech in Germany, Austria, Switzerland (DACH), or the Netherlands (NL).
    
    CRITICAL CONSTRAINT:
    Do NOT discover, recommend, or include any of the following companies as they are ALREADY in our database: [{avoid_list_str}].
    You must find {num_to_discover} brand NEW companies that are not in this list.
    
    AGGREGATED SEARCH RESULTS:
    {json.dumps(aggregated_search_results, indent=2)}
    
    Ensure your research meets these strict criteria:
    1. Descriptions must be highly concrete, technical, and detailed (2-3 sentences in English). Avoid generic buzzwords.
    2. Tech stacks must be specific (e.g. PyTorch, TensorFlow, GCP, Kubernetes, Docker, Scikit-learn, Embedded C, Unity) and verified from the company search snippets.
    3. Salary ranges must represent realistic German/DACH/NL ML Engineer standards specifically for entry-level M.Sc. graduates (e.g. ~55,000 - 65,000 EUR) and senior roles with 3-5 years experience (e.g. ~85,000 - 105,000 EUR). Format exactly as \"Entry: ~X EUR | Senior: ~Y EUR\".
    4. Provide specific engineering blogs, Github pages, or verification URLs in the \"sources\" field.
    5. Each company must contain details for:
       - name (string)
       - description (string)
       - location (string: City, Country)
       - status (string: \"Hiring\" or \"Stable\")
       - salary (string: \"Entry: ~X EUR | Senior: ~Y EUR\")
       - tech_stack (array of strings)
       - pivot (string describing strategic shifts, recent funding, or business pivots)
       - network (string describing competitors or key partners)
       - sources (array of strings representing valid verification links)

    Return a valid JSON array of exactly {num_to_discover} elements matching this schema:
    [
      {{
        "name": "Company Name",
        "description": "Concrete technical product details.",
        "location": "City, Country",
        "status": "Hiring / Stable",
        "salary": "Entry: ~X EUR | Senior: ~Y EUR",
        "tech_stack": ["Tech1", "Tech2", "Tech3"],
        "pivot": "Strategic shift or recent funding.",
        "network": "Competitor/partner network context.",
        "sources": ["https://blog.company.com/verified-url", "https://kununu.com/company-url"]
      }}
    ]
    """
    
    data = {
        "systemInstruction": {
            "parts": [{"text": system_instruction}]
        },
        "contents": [{
            "role": "user",
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.2
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            result_text = response.json().get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text')
            
            # Clean up potential markdown wrappers
            result_text = result_text.strip()
            if result_text.startswith("```json"):
                result_text = result_text[7:]
            if result_text.endswith("```"):
                result_text = result_text[:-3]
            result_text = result_text.strip()
            
            # Verify valid JSON
            new_companies = json.loads(result_text)
            
            if not isinstance(new_companies, list) or len(new_companies) < 1:
                raise ValueError("Response is not a valid list of companies.")
                
            # Deduplicate just in case
            unique_new_companies = []
            for nc in new_companies:
                name = nc.get("name")
                if not name:
                    continue
                # Double check against avoid list and current new additions
                if name.lower() not in [n.lower() for n in existing_names] and name.lower() not in [u.get("name", "").lower() for u in unique_new_companies]:
                    unique_new_companies.append(nc)
                    
            print(f"Deduplicated discoveries: Found {len(unique_new_companies)} genuinely new companies out of {len(new_companies)} proposed.")
            
            # Merge and save
            full_list = existing_companies + unique_new_companies
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(full_list, f, indent=2, ensure_ascii=False)
                
            print(f"✅ Success! Researched and validated {len(unique_new_companies)} new companies.")
            print(f"Master database now contains {len(full_list)} companies.")
            print("Raw research saved to raw_research_data.json.")
        else:
            print(f"❌ Error: Gemini API returned status code {response.status_code}")
            print(response.json())
            raise Exception(f"Failed to query Gemini API: {response.text}")
    except Exception as e:
        print(f"❌ Error during research extraction: {e}")
        raise e

if __name__ == "__main__":
    run_research()
