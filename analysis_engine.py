import os
import json
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

def load_raw_research():
    """Load raw research data from raw_research_data.json."""
    file_path = 'raw_research_data.json'
    if not os.path.exists(file_path):
        raise FileNotFoundError("raw_research_data.json not found. Run the research engine first.")
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_profile(profile_path):
    """Load the target CV/Profile data."""
    if not os.path.exists(profile_path):
        raise FileNotFoundError(f"Profile '{profile_path}' not found.")
    with open(profile_path, 'r', encoding='utf-8') as f:
        return f.read()

def run_analysis(profile_path='my_profil.txt'):
    print("=" * 60)
    print("🧠 STARTING PROFILE-SPECIFIC ANALYSIS ENGINE (Incremental Matcher) 🧠")
    print("=" * 60)
    
    # Ensure profiles directory exists
    os.makedirs('profiles', exist_ok=True)
    
    # Derive clean profile ID
    profile_filename = os.path.basename(profile_path)
    profile_id = os.path.splitext(profile_filename)[0]
    if profile_id == 'my_profil':
        profile_id = 'robin_erb'
        
    print(f"Active Profile: '{profile_filename}' | ID: '{profile_id}'")
    
    companies = load_raw_research()
    user_profile = load_profile(profile_path)
    
    # Try to load existing cached analysis for this profile
    cache_path = f'profiles/dashboard_data_{profile_id}.json'
    cached_companies_flat = []
    
    if os.path.exists(cache_path):
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)
                # Flatten the clustered dictionary
                for cluster_list in cached_data.values():
                    cached_companies_flat.extend(cluster_list)
            print(f"Loaded {len(cached_companies_flat)} pre-existing matches from cache '{cache_path}'.")
        except Exception as e:
            print(f"⚠️ Warning loading profile cache: {e}. Starting fresh.")
            cached_companies_flat = []
            
    # Determine the delta (companies in raw research that have not been analyzed for this CV yet)
    cached_names = [c.get("name", "").lower() for c in cached_companies_flat]
    delta_companies = [c for c in companies if c.get("name", "").lower() not in cached_names]
    
    print(f"Total raw companies: {len(companies)} | Already cached: {len(cached_companies_flat)}")
    
    new_analyses = []
    if len(delta_companies) > 0:
        print(f"🔄 Calculating matches for {len(delta_companies)} NEW companies...")
        
        model = "gemini-flash-latest"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        headers = {"Content-Type": "application/json"}
        
        system_instruction = (
            "You are an expert senior career advisor, technical recruiter, and executive matchmaker in Deep Tech and Machine Learning. "
            "Your task is to perform an exceptionally deep, objective compatibility analysis between a candidate profile and a list of companies. "
            "Output a single, valid JSON object only. Do not wrap the JSON output in markdown backticks (e.g. ```json)."
        )
        
        prompt = f"""
        Below is the candidate profile:
        
        CANDIDATE PROFILE:
        {user_profile}
        
        And here is the list of new companies to match against:
        {json.dumps(delta_companies, indent=2)}
        
        Compare the candidate's academic, technical, and professional background with each company's product, engineering stack, location, and salary benchmarks.
        
        For EACH company in the list, calculate and provide:
        1. **compatibility_score (0-100)**: Quantitative compatibility percentage. Weight match against CV's specific tech stacks, tools, and background.
        2. **strategic_cluster**: Assign to exactly one of these domains based on their focus:
           - "Machine Learning & AI Consultancy"
           - "Computer Vision & Robotics"
           - "NLP & Generative AI"
           - "Embedded ML & IoT"
           - "Data Science & FinTech"
           - "High-Tech Manufacturing AI"
        3. **fit_reasoning**: A highly personalized, crisp 2-3 sentence explanation (in English) linking the candidate's specific technical skills directly to the company's real-world product domain.
        4. **roadmap_9m**: Exactly 4-5 highly specific, actionable prep steps (in English) for the candidate to prepare for this specific company. Avoid generic suggestions like \"learn Python\".
        
        Return a valid JSON object with the following format:
        {{
          "analyses": [
            {{
              "name": "Exact Company Name",
              "compatibility_score": 85,
              "strategic_cluster": "NLP & Generative AI",
              "fit_reasoning": "Personalized fit details.",
              "roadmap_9m": ["step1", "step2", "step3", "step4"]
            }},
            ...
          ]
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
                
                # Parse analysis
                analysis_dict = json.loads(result_text)
                analyses_list = analysis_dict.get("analyses", [])
                
                # Create lookup map
                analyses_map = {a.get("name").lower(): a for a in analyses_list}
                
                for comp in delta_companies:
                    name_key = comp.get("name").lower()
                    analysis = analyses_map.get(name_key)
                    if not analysis:
                        # Fuzzy match fallback
                        for k, val in analyses_map.items():
                            if k in name_key or name_key in k:
                                analysis = val
                                break
                                
                    if not analysis:
                        print(f"⚠️ Warning: No analysis returned for '{comp.get('name')}'. Using defaults.")
                        analysis = {
                            "compatibility_score": 70,
                            "strategic_cluster": "Machine Learning & AI Consultancy",
                            "fit_reasoning": "Solid academic pedigree and analytical foundations align with their engineering core.",
                            "roadmap_9m": [
                                "Familiarize with the company's product offering.",
                                "Acquire basic exposure to their listed tech stacks.",
                                "Follow their engineering announcements on LinkedIn."
                            ]
                        }
                        
                    enriched_comp = {**comp, **analysis}
                    new_analyses.append(enriched_comp)
                print(f"✅ Finished scoring {len(new_analyses)} new companies.")
            else:
                print(f"❌ Error: Gemini API returned status code {response.status_code}")
                print(response.json())
                raise Exception("Failed to query Gemini API.")
        except Exception as e:
            print(f"❌ Error during batch analysis: {e}")
            raise e
    else:
        print("✅ All companies are already scored and cached. Skipping LLM calls.")

    # Reconstruct full catalog (cache + new)
    # Ensure no duplicates by keeping track of company names
    merged_companies = []
    seen_names = set()
    
    # Add new analyses first to ensure they override any old cache if applicable
    for comp in new_analyses:
        name_key = comp.get("name", "").lower()
        if name_key not in seen_names:
            merged_companies.append(comp)
            seen_names.add(name_key)
            
    # Add old cached companies
    for comp in cached_companies_flat:
        name_key = comp.get("name", "").lower()
        # Only add if it's still present in the master raw list and not already added
        is_in_raw = any(r.get("name", "").lower() == name_key for r in companies)
        if is_in_raw and name_key not in seen_names:
            merged_companies.append(comp)
            seen_names.add(name_key)
            
    # Group all by Strategic Cluster
    clustered_data = {}
    for comp in merged_companies:
        cluster = comp.get("strategic_cluster", "Machine Learning & AI Consultancy")
        if cluster not in clustered_data:
            clustered_data[cluster] = []
        clustered_data[cluster].append(comp)
        
    # Sort companies within each cluster by compatibility_score descending
    for cluster in clustered_data:
        clustered_data[cluster] = sorted(clustered_data[cluster], key=lambda x: x.get("compatibility_score", 0), reverse=True)
        
    # 1. Save profile-specific cache in profiles/
    with open(cache_path, 'w', encoding='utf-8') as f:
        json.dump(clustered_data, f, indent=2, ensure_ascii=False)
    print(f"💾 Profile cache saved successfully to '{cache_path}'.")
    
    # 2. Overwrite main dashboard_data.json in root (active dataset loaded by Streamlit)
    with open('dashboard_data.json', 'w', encoding='utf-8') as f:
        json.dump(clustered_data, f, indent=2, ensure_ascii=False)
    print("💾 Active dataset synchronized to 'dashboard_data.json'.")
    
    # 3. Generate high-fidelity markdown report
    report_content = f"""# 📊 IT-Market Research & Deep Match Analysis

This report maps the DACH-NL technology landscape against the candidate profile: **{profile_filename}**. It provides verified salary ranges, validated technical stacks, and personalized compatibility scores and roadmaps.

---

## 🚀 Top Career Fits & Compatibility Rankings

"""
    all_flat = sorted(merged_companies, key=lambda x: x.get("compatibility_score", 0), reverse=True)
    for idx, comp in enumerate(all_flat):
        score_emoji = "🟢" if comp.get("compatibility_score", 0) >= 85 else ("🟡" if comp.get("compatibility_score", 0) >= 65 else "🔴")
        report_content += f"### {idx+1}. {comp.get('name')} | {score_emoji} Match Score: {comp.get('compatibility_score')}%\n"
        report_content += f"- **Cluster**: `{comp.get('strategic_cluster')}`\n"
        report_content += f"- **Location**: {comp.get('location')} | **Hiring Status**: {comp.get('status')}\n"
        report_content += f"- **Verified Tech Stack**: {', '.join([f'`{t}`' for t in comp.get('tech_stack', [])])}\n"
        report_content += f"- **Kununu/Glassdoor Salary Insights**: {comp.get('salary')}\n\n"
        
        report_content += f"#### 🔍 Why it fits:\n"
        report_content += f"{comp.get('fit_reasoning')}\n\n"
        
        report_content += f"#### 🗺️ Personal 9-Month Transition Roadmap:\n"
        for step in comp.get('roadmap_9m', []):
            report_content += f"- [ ] {step}\n"
        
        sources = comp.get('sources', [])
        if sources:
            report_content += f"\n- **Sources**: {', '.join([f'[Source]({s})' for s in sources])}\n"
            
        report_content += "\n---\n\n"
        
    # Save to both profile report and root report
    profile_report_path = f'profiles/marktanalyse_db_{profile_id}.md'
    with open(profile_report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    with open('marktanalyse_db.md', 'w', encoding='utf-8') as f:
        f.write(report_content)
        
    print(f"✅ Generated profile report '{profile_report_path}' and synchronized root 'marktanalyse_db.md'.")
    print("=" * 60)

if __name__ == "__main__":
    run_analysis()
