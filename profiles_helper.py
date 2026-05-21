import os
import json
import requests
from dotenv import load_dotenv

# Load environmental variables
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

def extract_profile_metadata(cv_text):
    """
    Extracts the full name, a concise career direction (2-4 words), and whether the candidate
    is in a computer science/tech engineering field from candidate CV text.
    """
    if not api_key:
        return {"name": "Unknown Candidate", "direction": "Deep Tech Specialist", "is_tech": True}

    print("🔮 Querying Gemini to extract candidate name, career direction, and domain type...")
    model = "gemini-flash-latest"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    
    system_instruction = (
        "You are an elite talent scout. Your task is to analyze candidate resumes "
        "and extract: 1) Their full name, 2) A highly accurate, concise, premium 2-4 word professional title/direction "
        "(e.g., 'NLP & Generative AI Specialist', 'B2B Sales Representative', 'Biochemistry Research Assistant'), "
        "3) A boolean 'is_tech' indicating if their core field is Computer Science, Data Science, AI, or Deep Tech Engineering. "
        "Return a valid JSON object ONLY. Do not use markdown code block formatting."
    )
    
    prompt = f"""
    Analyze the following candidate resume text:
    
    RESUME TEXT:
    {cv_text[:6000]}
    
    Return a valid JSON object in exactly this format:
    {{
      "name": "Full Name",
      "direction": "Concise 2-4 word professional direction",
      "is_tech": true or false
    }}
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
            "temperature": 0.1
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=15)
        if response.status_code == 200:
            result_text = response.json().get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text')
            result_text = result_text.strip()
            if result_text.startswith("```json"):
                result_text = result_text[7:]
            if result_text.endswith("```"):
                result_text = result_text[:-3]
            result_text = result_text.strip()
            
            meta = json.loads(result_text)
            if isinstance(meta, list):
                if len(meta) > 0:
                    meta = meta[0]
                else:
                    meta = {}
            if not isinstance(meta, dict):
                meta = {}
                
            if not meta.get("name") or meta.get("name") == "Full Name":
                meta["name"] = "Candidate Profile"
            if not meta.get("direction"):
                meta["direction"] = "Deep Tech Specialist"
            if "is_tech" not in meta:
                meta["is_tech"] = True
            return meta
    except Exception as e:
        print(f"⚠️ Error extracting metadata: {e}")
        
    return {"name": "Candidate Profile", "direction": "Deep Tech Specialist", "is_tech": True}

def discover_5_targeted_companies(cv_text, direction, is_tech=True):
    """
    Finds 5 real startups in the DACH-NL region specific to the candidate's CV and direction.
    If is_tech is True, discovers tech/AI companies. If False, discovers companies tailored to their non-CS focus.
    Appends them to raw_research_data.json if they don't already exist.
    """
    if not api_key:
        print("⚠️ GOOGLE_API_KEY is not configured.")
        return []

    print(f"🔍 Starting targeted company discovery for career direction: '{direction}' (is_tech={is_tech})...")
    
    # 1. Load existing company names to avoid duplicates
    existing_companies = []
    existing_names = []
    file_path = 'raw_research_data.json'
    
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                existing_companies = json.load(f)
                existing_names = [c.get("name") for c in existing_companies if c.get("name")]
        except Exception as e:
            print(f"⚠️ Error loading database: {e}")

    # 2. Run Tavily Search
    search_results = []
    try:
        from langchain_community.tools.tavily_search import TavilySearchResults
        search = TavilySearchResults(k=6)
        if is_tech:
            query = f"Top Machine Learning deep tech AI startups in Germany DACH Netherlands working on {direction}"
        else:
            query = f"Top active fast growing startups in Germany DACH Netherlands hiring for {direction}"
        print(f"Running Tavily Search for: '{query}'...")
        search_results = search.run(query)
    except Exception as e:
        print(f"⚠️ Tavily Search skipped or failed: {e}. Falling back to Gemini's internal knowledge base.")
        search_results = []

    # 3. Call Gemini to compile 5 startups
    model = "gemini-flash-latest"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    
    if is_tech:
        system_instruction = (
            "You are an elite deep tech research scout. Your task is to discover exactly 5 real, active technology startups "
            "or companies in the DACH-NL region (Germany, Austria, Switzerland, Netherlands) that specialize in "
            "a specific career direction and perfectly match a candidate's background. "
            "Ensure the startups proposed are real, with detailed tech stacks and realistic DACH-NL salary levels "
            "(e.g., Entry: ~60,000 EUR | Senior: ~95,000 EUR). "
            "Avoid any companies already present in our database. "
            "Return a valid JSON array ONLY. Do not use markdown code block formatting."
        )
        
        prompt_intro = f"Discover exactly 5 real, active Deep Tech / AI companies or startups in DACH-NL suited for this career focus:\nCAREER FOCUS: {direction}"
        prompt_fallback = "If the Tavily search results do not provide enough matching companies, use your own internal pre-trained knowledge base to discover 5 real, high-quality deep tech / AI startups in DACH-NL working on or near this field."
        tech_stack_desc = '["Tech1", "Tech2", "Tech3"]'
        desc_spec = "Concrete technical product details (2-3 sentences in English)."
    else:
        system_instruction = (
            "You are an elite talent acquisition scout. Your task is to discover exactly 5 real, active startups "
            "or companies in the DACH-NL region (Germany, Austria, Switzerland, Netherlands) where the candidate's "
            "specific professional pedigree and career focus (e.g. Sales, Marketing, Biology, HR, Finance, etc.) is highly relevant and valuable. "
            "Target fast-growing startups (SaaS, FinTech, BioTech, HealthTech, E-commerce, HR-Tech, etc.) hiring for this profile. "
            "Ensure the startups proposed are real, with detailed stacks of business/technical tools used (e.g. Salesforce, Excel, CRM systems) "
            "and realistic DACH-NL salary levels (e.g., Entry: ~50,000 EUR | Senior: ~85,000 EUR depending on the role). "
            "Avoid any companies already present in our database. "
            "Return a valid JSON array ONLY. Do not use markdown code block formatting."
        )
        
        prompt_intro = f"Discover exactly 5 real, active startups or companies in DACH-NL (SaaS, FinTech, BioTech, HR-Tech, etc.) suited for this career focus:\nCAREER FOCUS: {direction}"
        prompt_fallback = "If the Tavily search results do not provide enough matching companies, use your own internal pre-trained knowledge base to discover 5 real, high-quality startups in DACH-NL where this candidate's specific background and skillset are highly sought after. DO NOT recommend AI/deep tech companies for a non-tech profile unless they are hiring for their specific non-CS role."
        tech_stack_desc = '["Tool1", "Tool2", "Tool3"] (e.g., Salesforce, HubSpot, Excel, SPSS, or specific professional tools)'
        desc_spec = "Concrete details of the product/service and how the candidate's specific skillset fits in (2-3 sentences in English)."

    avoid_list_str = ", ".join([f'"{name}"' for name in existing_names])
    
    prompt = f"""
    {prompt_intro}
    
    CANDIDATE CV DETAILS:
    {cv_text[:4000]}
    
    TAVILY RESEARCH SEARCH RESULTS:
    {json.dumps(search_results, indent=2)}
    
    CRITICAL CONSTRAINT:
    Do NOT recommend or include any of the following companies, as they are ALREADY in our database: [{avoid_list_str}].
    {prompt_fallback}
    Make sure the description, tech/tool stack, pivot, and network fields reflect their actual field and are NOT generic computer science/AI engineering descriptions.
    
    Return a valid JSON array of exactly 5 elements matching this schema:
    [
      {{
        "name": "Exact Startup Name",
        "description": "{desc_spec}",
        "location": "City, Country",
        "status": "Hiring / Stable",
        "salary": "Entry: ~X EUR | Senior: ~Y EUR",
        "tech_stack": {tech_stack_desc},
        "pivot": "Strategic shift, recent funding, or business development focus.",
        "network": "Competitors, partners, or corporate ecosystem context.",
        "sources": ["https://www.company.com", "https://kununu.com/company-url"]
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
        response = requests.post(url, headers=headers, json=data, timeout=25)
        if response.status_code == 200:
            result_text = response.json().get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text')
            result_text = result_text.strip()
            if result_text.startswith("```json"):
                result_text = result_text[7:]
            if result_text.endswith("```"):
                result_text = result_text[:-3]
            result_text = result_text.strip()
            
            new_companies = json.loads(result_text)
            
            if isinstance(new_companies, list) and len(new_companies) > 0:
                # Deduplicate and save
                unique_new = []
                for comp in new_companies:
                    name = comp.get("name")
                    if not name:
                        continue
                    if name.lower() not in [n.lower() for n in existing_names] and name.lower() not in [u.get("name", "").lower() for u in unique_new]:
                        unique_new.append(comp)
                
                print(f"Successfully discovered {len(unique_new)} new targeted companies.")
                
                full_list = existing_companies + unique_new
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(full_list, f, indent=2, ensure_ascii=False)
                
                return unique_new
            else:
                print("⚠️ No valid companies array returned from Gemini.")
        else:
            print(f"❌ Gemini discovery failed with status {response.status_code}: {response.text}")
    except Exception as e:
        print(f"❌ Error during company discovery: {e}")
        
    return []
