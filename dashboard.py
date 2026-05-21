import streamlit as st
import json
import os
import glob
import shutil
import pandas as pd
import urllib.parse
import textwrap
from openai import OpenAI
from dotenv import load_dotenv

# Ensure profiles directory exists
os.makedirs('profiles', exist_ok=True)
if not os.path.exists('profiles/my_profil.txt') and os.path.exists('my_profil.txt'):
    shutil.copy('my_profil.txt', 'profiles/my_profil.txt')

# Load env variables and init OpenAI-compatible Gemini client for Advisor Chat
load_dotenv()
client = OpenAI(
    api_key=os.getenv("GOOGLE_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

st.set_page_config(
    page_title="DACH-NL AI & Deep Tech Landscape",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Premium CSS for Rich Aesthetics & Infographic Progress-Bar Table
st.markdown("""
<style>
    /* Google Font Import */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Premium High-Density Table Styling */
    .infographic-table {
        width: 100%;
        border-collapse: collapse;
        margin: 20px 0;
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        overflow: hidden;
    }
    .infographic-table th {
        background: rgba(255, 255, 255, 0.06);
        color: #ffffff;
        text-align: left;
        padding: 14px 20px;
        font-weight: 600;
        font-size: 0.95rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }
    .infographic-table td {
        padding: 12px 20px;
        color: #dfe6e9;
        font-size: 0.9rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        vertical-align: middle;
    }
    .infographic-table tr:hover {
        background: rgba(255, 255, 255, 0.05);
    }
    
    /* Company Squircle Logo */
    .company-logo-img {
        width: 32px;
        height: 32px;
        border-radius: 8px;
        background: rgba(255, 255, 255, 0.08);
        margin-right: 12px;
        vertical-align: middle;
        object-fit: contain;
        padding: 4px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        display: inline-block;
    }
    
    .company-logo-fallback {
        width: 32px;
        height: 32px;
        border-radius: 8px;
        background: linear-gradient(135deg, #00B4DB, #0083B0);
        color: white;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 0.9rem;
        margin-right: 12px;
        vertical-align: middle;
        box-shadow: 0 4px 10px rgba(0, 180, 219, 0.3);
    }
    
    /* Progress Track (Horizontal Slider Handle Mimic) */
    .progress-track {
        background: rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        height: 10px;
        width: 150px;
        position: relative;
        display: inline-block;
        vertical-align: middle;
        margin-right: 15px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    .progress-fill-high {
        background: linear-gradient(90deg, #00c6ff, #0072ff);
        border-radius: 10px;
        height: 100%;
        position: relative; /* Fixed positioning boundary constraints */
    }
    .progress-fill-med {
        background: linear-gradient(90deg, #f1c40f, #f39c12);
        border-radius: 10px;
        height: 100%;
        position: relative; /* Fixed */
    }
    .progress-fill-low {
        background: linear-gradient(90deg, #e74c3c, #c0392b);
        border-radius: 10px;
        height: 100%;
        position: relative; /* Fixed */
    }
    .progress-handle-high {
        position: absolute;
        right: -7px; /* Centered precisely at completion boundary */
        top: -3px;
        width: 14px;
        height: 14px;
        border-radius: 50%;
        background: #000;
        border: 3px solid #00c6ff;
        box-shadow: 0 0 8px #00c6ff;
    }
    .progress-handle-med {
        position: absolute;
        right: -7px;
        top: -3px;
        width: 14px;
        height: 14px;
        border-radius: 50%;
        background: #000;
        border: 3px solid #f1c40f;
        box-shadow: 0 0 8px #f1c40f;
    }
    .progress-handle-low {
        position: absolute;
        right: -7px;
        top: -3px;
        width: 14px;
        height: 14px;
        border-radius: 50%;
        background: #000;
        border: 3px solid #e74c3c;
        box-shadow: 0 0 8px #e74c3c;
    }
    
    /* Subdomain Badges */
    .subdomain-tag {
        background: rgba(255, 255, 255, 0.08);
        color: #b2bec3;
        padding: 4px 10px;
        border-radius: 50px;
        font-size: 0.8rem;
        font-weight: 500;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* Company Card */
    .company-card {
        background: rgba(255, 255, 255, 0.06);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.15);
        transition: all 0.3s ease-in-out;
    }
    .company-card:hover {
        transform: translateY(-4px);
        border: 1px solid rgba(255, 255, 255, 0.25);
        box-shadow: 0 12px 40px 0 rgba(0, 180, 219, 0.15);
    }
    
    /* Tags */
    .tech-tag {
        background: rgba(255, 255, 255, 0.1);
        color: #f1f2f6;
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 0.78rem;
        margin-right: 5px;
        margin-bottom: 5px;
        display: inline-block;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* Chat Popover Styling */
    div[data-testid="stPopoverBody"] {
        background-color: #0e1117 !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        border-radius: 12px !important;
        box-shadow: 0 10px 40px rgba(0,0,0,0.5) !important;
        min-width: 420px !important;
    }
</style>
""", unsafe_allow_html=True)

# Helper function to extract or infer clean company base domain
def get_company_domain(name, sources=None):
    name_clean = "".join([c for c in name.lower() if c.isalnum() or c.isspace()]).strip()
    
    mapping = {
        "helsing": "helsing.ai",
        "aleph alpha": "aleph-alpha.com",
        "black forest labs": "blackforestlabs.ai",
        "dida": "dida.do",
        "celonis": "celonis.com",
        "mindpeak": "mindpeak.ai",
        "noah labs": "noah-labs.com",
        "hyperai": "hyper.ai",
        "aidence": "aidence.com",
        "weaviate": "weaviate.io"
    }
    for key, domain in mapping.items():
        if key in name_clean or name_clean in key:
            return domain
            
    if sources:
        for url in sources:
            try:
                parsed = urllib.parse.urlparse(url)
                netloc = parsed.netloc.lower()
                if netloc.startswith("www."):
                    netloc = netloc[4:]
                if any(agg in netloc for agg in ["omnius.so", "appliedai", "biopharmiq", "wearebrain", "linkedin", "observer.com", "glassdoor", "kununu", "github"]):
                    continue
                if netloc:
                    return netloc
            except:
                pass
                
    guess = name_clean.replace(" ", "")
    return f"{guess}.com"

# Helper to parse salary ranges from string representation
def parse_salary(salary_str):
    entry = 60000
    senior = 95000
    try:
        parts = salary_str.split("|")
        for p in parts:
            if "entry" in p.lower():
                val = "".join([c for c in p if c.isdigit()])
                if val:
                    entry = int(val)
            elif "senior" in p.lower():
                val = "".join([c for c in p if c.isdigit()])
                if val:
                    senior = int(val)
    except:
        pass
    return entry, senior

# --- Dynamic CV/Profile Scanning (Accepts TXT and PDF Resumes) ---
with st.sidebar:
    st.header("👤 Candidate Profiles")
    
    # Scan for profiles in profiles/ folder
    profile_paths = glob.glob("profiles/*.txt")
    available_profiles = {}
    
    for path in profile_paths:
        fname = os.path.basename(path)
        pid = os.path.splitext(fname)[0]
        if pid == "my_profil" or pid == "robin_erb":
            available_profiles["Robin Erb (Primary)"] = path
        else:
            display_name = fname.replace("_", " ").replace(".txt", "").title()
            available_profiles[display_name] = path
            
    if not available_profiles:
        st.warning("No profiles found. Please upload a CV below to start!")
        active_name = None
        active_path = None
    else:
        active_name = st.selectbox("Select Active Candidate:", list(available_profiles.keys()))
        active_path = available_profiles[active_name]
        
    st.markdown("---")
    st.header("📤 Upload Candidate Resume")
    uploaded_file = st.file_uploader("Upload CV (.txt, .pdf)", type=["txt", "pdf"])
    
    if uploaded_file is not None:
        filename = uploaded_file.name
        safe_filename = "".join([c if c.isalnum() or c in ['.', '_', '-'] else '_' for c in filename])
        
        # Consistent text extension for analysis engine processing
        txt_filename = os.path.splitext(safe_filename)[0] + ".txt"
        save_path = os.path.join("profiles", txt_filename)
        
        cv_content = None
        # Handle PDF uploads directly via pypdf
        if filename.lower().endswith(".pdf"):
            try:
                import pypdf
                reader = pypdf.PdfReader(uploaded_file)
                text = ""
                for page in reader.pages:
                    t = page.extract_text()
                    if t:
                        text += t + "\n"
                cv_content = text.encode("utf-8")
            except Exception as e:
                st.sidebar.error(f"Error parsing PDF file: {e}")
        else:
            cv_content = uploaded_file.getbuffer()
            
        if cv_content:
            with open(save_path, "wb") as f:
                f.write(cv_content)
            st.success(f"Uploaded and parsed {filename}!")
            
            # Trigger analysis matching engine automatically for new uploads
            profile_id = os.path.splitext(txt_filename)[0]
            cache_path = f'profiles/dashboard_data_{profile_id}.json'
            
            if not os.path.exists(cache_path):
                with st.spinner("Analyzing candidate & matching ecosystem (Gemini 2.5 Flash-Lite)..."):
                    try:
                        from analysis_engine import run_analysis
                        run_analysis(save_path)
                        st.success("Successfully generated match scores!")
                    except Exception as e:
                        st.error(f"Error calculating matches: {e}")
            st.rerun()

# Ensure active profile path is loaded
if not active_path:
    st.info("👈 Please upload a candidate resume to unlock the IT-Market Deep Tech Finder.")
    st.stop()

# Derive active profile details
profile_id = os.path.splitext(os.path.basename(active_path))[0]
if profile_id == 'my_profil':
    profile_id = 'robin_erb'

# Load active cached analyses
cache_data_path = f'profiles/dashboard_data_{profile_id}.json'
if not os.path.exists(cache_data_path):
    with st.spinner("Generating match index..."):
        from analysis_engine import run_analysis
        run_analysis(active_path)
        
with open(cache_data_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Load profile text for chatbot context
with open(active_path, 'r', encoding='utf-8') as f:
    active_profile_text = f.read()

# --- Flatten and extract filter metadata ---
flat_companies = []
for cluster, comp_list in data.items():
    flat_companies.extend(comp_list)
flat_companies = sorted(flat_companies, key=lambda x: x.get("compatibility_score", 0), reverse=True)

# Build unique metadata for filters
all_techs = sorted(list(set([tech for c in flat_companies for tech in c.get("tech_stack", [])])))
all_countries = sorted(list(set([c.get("location", "").split(",")[-1].strip() for c in flat_companies if "," in c.get("location")])))

# --- Header Section with FLOATING AI Career Advisor Dialog ---
col_head_title, col_head_chat = st.columns([3, 1])
with col_head_title:
    st.title("🗄️ DACH-NL AI & Deep Tech Landscape")
    st.markdown(f"Evaluating the European AI Market for: **{active_name}**")
with col_head_chat:
    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
    # A beautiful top-right floating collapsible chat popover button
    chat_popover = st.popover("💬 Ask AI Advisor", use_container_width=True)
    with chat_popover:
        st.markdown(f"### 💬 AI Recruiter & Advisor")
        st.markdown(f"Ask deep questions about **{active_name}**'s skill relevance, salary fits, or tech match analysis.")
        
        chat_key = f"messages_{profile_id}"
        if chat_key not in st.session_state:
            context_str = json.dumps(data)
            system_msg = f"""You are a professional senior career advisor and expert deep tech recruiter. 
            You have three sources of truth:
            1. Enriched DACH-NL Startup Market Data: {context_str}
            2. Match analysis reasonings for companies: {context_str}
            3. The Active Candidate Resume Profile: {active_profile_text}
            
            Always answer candidate-specific questions in professional English, using details from their profile to explain their fit score.
            Provide highly strategic, realistic insights."""
            st.session_state[chat_key] = [{"role": "system", "content": system_msg}]

        # Render chat logs
        for msg in st.session_state[chat_key][1:]:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # Handle message queries
        if prompt := st.chat_input("Ask about fits, stacks, or preparation...", key=f"chat_input_{profile_id}"):
            st.session_state[chat_key].append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                with st.spinner("Processing..."):
                    try:
                        response = client.chat.completions.create(
                            model="gemini-2.5-flash-lite",
                            messages=st.session_state[chat_key]
                        ).choices[0].message.content
                        st.markdown(response)
                        st.session_state[chat_key].append({"role": "assistant", "content": response})
                    except Exception as e:
                        st.error(f"Chatbot service down: {e}")

# Interactive Filter Bar
col_filt1, col_filt2, col_filt3 = st.columns([2, 1, 1])
search_query = col_filt1.text_input("🔍 Search Company, Description, or Technology Stack:", "")
selected_techs = col_filt2.multiselect("🛠️ Filter by Technology:", all_techs)
selected_countries = col_filt3.multiselect("📍 Filter by Country/Region:", all_countries)

# Apply Filter logic
filtered_companies = []
for c in flat_companies:
    match_search = (
        search_query.lower() in c.get("name", "").lower() or
        search_query.lower() in c.get("description", "").lower() or
        any(search_query.lower() in t.lower() for t in c.get("tech_stack", []))
    )
    match_tech = not selected_techs or any(t in c.get("tech_stack", []) for t in selected_techs)
    
    country = c.get("location", "").split(",")[-1].strip() if "," in c.get("location") else ""
    match_country = not selected_countries or country in selected_countries
    
    if match_search and match_tech and match_country:
        filtered_companies.append(c)

# Top KPI Metrics
if filtered_companies:
    total_count = len(filtered_companies)
    top_score = max([c.get("compatibility_score", 0) for c in filtered_companies])
    avg_score = sum([c.get("compatibility_score", 0) for c in filtered_companies]) / total_count
    
    col_stat1, col_stat2, col_stat3 = st.columns(3)
    col_stat1.metric("🔍 Matching Discoveries", f"{total_count} Companies")
    st.markdown(
        f"""
        <style>
            [data-testid="stMetricValue"] {{
                font-size: 1.8rem;
                font-weight: 700;
            }}
        </style>
        """,
        unsafe_allow_html=True
    )
    col_stat2.metric("🏆 Top Compatibility Fit", f"{top_score}%")
    col_stat3.metric("📈 Average Match", f"{int(avg_score)}%")

st.markdown("---")

# CSV Export Button
if filtered_companies:
    csv_data = []
    for c in filtered_companies:
        csv_data.append({
            "Name": c.get("name"),
            "Compatibility": f"{c.get('compatibility_score')}%",
            "Cluster": c.get("strategic_cluster"),
            "Location": c.get("location"),
            "Salary Insights": c.get("salary"),
            "Tech Stack": ", ".join(c.get("tech_stack", []))
        })
    df = pd.DataFrame(csv_data)
    csv_bytes = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Export Matches to CSV",
        data=csv_bytes,
        file_name=f"market_matches_{profile_id}.csv",
        mime="text/csv"
    )

# --- Dashboard Tab Layout ---
tab_overview, tab_deep_dive, tab_analytics = st.tabs([
    "📋 Landscape Overview", 
    "🗂️ Strategic Cluster Deep-Dives",
    "📊 Market Intelligence & Skill Analytics"
])

# ================= TAB 1: LANDSCAPE OVERVIEW =================
with tab_overview:
    if not filtered_companies:
        st.warning("No companies match your filters.")
    else:
        st.markdown("### 📊 Active AI Startup Leaderboard")
        
        # Build the HTML Table Rows - Fixed Indentation formatting bug via textwrap.dedent
        table_rows_html = ""
        for idx, comp in enumerate(filtered_companies):
            score = comp.get("compatibility_score", 0)
            
            # Color and Handle Styling based on Score bounds
            if score >= 85:
                progress_class = "progress-fill-high"
                handle_class = "progress-handle-high"
            elif score >= 65:
                progress_class = "progress-fill-med"
                handle_class = "progress-handle-med"
            else:
                progress_class = "progress-fill-low"
                handle_class = "progress-handle-low"
                
            # Country Emojis
            loc = comp.get("location", "").lower()
            if "germany" in loc or "de" in loc:
                flag = "🇩🇪 Germany"
            elif "netherlands" in loc or "nl" in loc or "amsterdam" in loc:
                flag = "🇳🇱 Netherlands"
            elif "switzerland" in loc or "ch" in loc:
                flag = "🇨🇭 Switzerland"
            elif "austria" in loc or "at" in loc:
                flag = "🇦🇹 Austria"
            else:
                flag = "🇪🇺 Europe"
                
            # Short Domain tags (non-generic)
            subdomain = comp.get("strategic_cluster", "AI Software")
            subdomain = subdomain.replace(" Consultancy", "").replace(" & ", " & ")
            
            # Fetch high-res logo with smart extractor and fallback
            domain = get_company_domain(comp.get("name"), comp.get("sources", []))
            initial = comp.get("name", "?")[0]
            
            logo_html = f"""
            <img src="https://logo.clearbit.com/{domain}" onerror="this.onerror=null; this.parentNode.innerHTML='<div class=\\'company-logo-fallback\\'>{initial}</div>';" class="company-logo-img" />
            """
            
            # Raw string row build (Zero internal markdown tabs to prevent code block parsing)
            row_raw = f"""<tr>
<td><strong>{idx+1}</strong></td>
<td>
<div style="display: flex; align-items: center;">
<div style="min-width: 44px; display: inline-block;">{logo_html}</div>
<span style="font-weight:600; font-size:1.02rem; color:#fff;">{comp.get('name')}</span>
</div>
</td>
<td>
<div class="progress-track">
<div class="{progress_class}" style="width: {score}%;">
<div class="{handle_class}"></div>
</div>
</div>
</td>
<td><strong style="color:#00B4DB; font-size:1.05rem;">{score}%</strong></td>
<td>{flag}</td>
<td><span class="subdomain-tag">{subdomain}</span></td>
</tr>"""
            table_rows_html += row_raw
            
        # Complete HTML Table Injection (Cleaned columns, removed Hiring Status)
        table_html = f"""
        <table class="infographic-table">
            <thead>
                <tr>
                    <th style="width: 5%">#</th>
                    <th style="width: 30%">Company</th>
                    <th style="width: 25%">Compatibility Metric</th>
                    <th style="width: 10%">Match Score</th>
                    <th style="width: 15%">Location</th>
                    <th style="width: 15%">Strategic Focus</th>
                </tr>
            </thead>
            <tbody>
                {table_rows_html}
            </tbody>
        </table>
        """
        
        # Strip all margin space lines to guarantee it renders as HTML
        st.markdown(textwrap.dedent(table_html), unsafe_allow_html=True)
        
        # Selectbox drill down details
        st.markdown("---")
        st.markdown("### 🔍 Select Company for Detailed Fit Analysis")
        select_names = [c.get("name") for c in filtered_companies]
        selected_comp_name = st.selectbox("Choose a company to inspect:", select_names)
        
        selected_comp = next((c for c in filtered_companies if c.get("name") == selected_comp_name), None)
        if selected_comp:
            st.markdown(f"## 🏢 {selected_comp.get('name')}")
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                st.markdown(f"**📍 Location:** {selected_comp.get('location')}")
                st.markdown(f"**💰 Glassdoor/Kununu Salary Benchmarks:** `{selected_comp.get('salary')}`")
                
                st.markdown("**🛠️ Technical Stack:**")
                tech_tags_html = ""
                for t in selected_comp.get("tech_stack", []):
                    tech_tags_html += f'<span class="tech-tag">{t}</span>'
                st.markdown(tech_tags_html, unsafe_allow_html=True)
                
            with col_d2:
                st.markdown(f"**🎯 Strategic Match Analysis:**\n{selected_comp.get('fit_reasoning')}")
                st.markdown(f"**🔄 Strategic Pivot Context:**\n{selected_comp.get('pivot')}")
                st.markdown(f"**🕸️ Competitors & Integration Network:**\n{selected_comp.get('network')}")
                
            # Personalization Roadmap: ONLY shown for primary profile "Robin Erb"
            if profile_id == 'robin_erb':
                st.markdown("---")
                st.markdown("**🗺️ Personal 9-Month Transition Roadmap:**")
                for step in selected_comp.get("roadmap_9m", []):
                    st.markdown(f"- [ ] {step}")
            else:
                st.markdown("---")
                st.info("💡 **Company Finder Mode**: Candidate-specific prep roadmaps are configured exclusively for the primary profile (Robin Erb).")
                
            st.markdown("**🔗 Verification Sources:**")
            for s in selected_comp.get("sources", []):
                st.markdown(f"- [{s}]({s})")

# ================= TAB 2: STRATEGIC CLUSTER DEEP-DIVES =================
with tab_deep_dive:
    # Regroup currently filtered companies by cluster
    clustered_filtered = {}
    for c in filtered_companies:
        cluster = c.get("strategic_cluster", "AI Software")
        if cluster not in clustered_filtered:
            clustered_filtered[cluster] = []
        clustered_filtered[cluster].append(c)
        
    if not clustered_filtered:
        st.warning("No companies match the filters.")
    else:
        for cluster_name, comp_list in clustered_filtered.items():
            st.markdown(f"### 📍 {cluster_name} ({len(comp_list)} Companies)")
            
            # Render inside columns
            cluster_cols = st.columns(3)
            for c_idx, comp in enumerate(comp_list):
                with cluster_cols[c_idx % 3]:
                    score = comp.get("compatibility_score", 0)
                    if score >= 85:
                        badge_html = f'<div style="background: linear-gradient(135deg, #00c6ff, #0072ff); color: white; padding: 4px 12px; border-radius: 50px; font-weight: 600; font-size: 0.82rem; display: inline-block;">🔥 High Fit: {score}%</div>'
                    elif score >= 65:
                        badge_html = f'<div style="background: linear-gradient(135deg, #f1c40f, #f39c12); color: white; padding: 4px 12px; border-radius: 50px; font-weight: 600; font-size: 0.82rem; display: inline-block;">⚡ Good Fit: {score}%</div>'
                    else:
                        badge_html = f'<div style="background: linear-gradient(135deg, #e74c3c, #c0392b); color: white; padding: 4px 12px; border-radius: 50px; font-weight: 600; font-size: 0.82rem; display: inline-block;">⚠️ Moderate: {score}%</div>'
                        
                    card_html = f"""
                    <div class="company-card">
                        <h4 style="margin-top:0; margin-bottom:4px; font-weight:700; color:#fff;">{comp.get('name')}</h4>
                        <p style="color:#b2bec3; font-size:0.85rem; margin-bottom:12px;">📍 {comp.get('location')}</p>
                        {badge_html}
                        <p style="margin-top:16px; font-style:italic; line-height:1.4; color:#dfe6e9; font-size:0.88rem;">"{comp.get('description')}"</p>
                    </div>
                    """
                    st.markdown(card_html, unsafe_allow_html=True)
                    
                    with st.expander("🔍 Match Deep-Dive & Details", expanded=False):
                        st.markdown(f"**💰 Salaries:** `{comp.get('salary')}`")
                        
                        st.markdown("**🛠️ Tech Tags:**")
                        tags_html = ""
                        for t in comp.get("tech_stack", []):
                            tags_html += f'<span class="tech-tag">{t}</span>'
                        st.markdown(tags_html, unsafe_allow_html=True)
                        
                        st.markdown(f"**🎯 Strategic Fit:**\n{comp.get('fit_reasoning')}")
                        
                        # 9-Month Checklist ONLY for Robin Erb
                        if profile_id == 'robin_erb':
                            st.markdown("**🗺️ 9-Month Preparation Checklist:**")
                            for step in comp.get("roadmap_9m", []):
                                st.markdown(f"- [ ] {step}")
                        
                        st.markdown(f"**🔄 Pivot:**\n{comp.get('pivot')}")
                        st.markdown(f"**🕸️ Network Logic:**\n{comp.get('network')}")
                        
                        sources = comp.get("sources", [])
                        if sources:
                            st.markdown("**🔗 Verification Sources:**")
                            for s in sources:
                                st.markdown(f"- [{s}]({s})")
            st.markdown("---")

# ================= TAB 3: MARKET INTELLIGENCE & SKILL ANALYTICS =================
with tab_analytics:
    st.markdown("### 📊 Landscape Intelligence & Skills Match Analytics")
    st.markdown("Compare your developer pedigree against the aggregate tech stack demands, locations, and salaries across the DACH-NL AI sector.")
    
    col_an1, col_an2 = st.columns(2)
    
    with col_an1:
        st.markdown("#### 🛠️ Tech Stack Demand Frequency")
        # Compute frequency of tech stack tools across all discovered companies
        tech_counts = {}
        for c in flat_companies:
            for tech in c.get("tech_stack", []):
                tech_counts[tech] = tech_counts.get(tech, 0) + 1
        
        # Sort and take top 12 technologies
        sorted_techs = sorted(tech_counts.items(), key=lambda x: x[1], reverse=True)[:12]
        if sorted_techs:
            tech_df = pd.DataFrame(sorted_techs, columns=["Technology", "Mentions in Landscape"])
            st.bar_chart(tech_df.set_index("Technology"), color="#00c6ff")
        else:
            st.info("No technology stacks found in the current landscape.")
            
    with col_an2:
        st.markdown("#### 🎯 Personal Skill Match Matrix")
        # Extract skills from active candidate profile
        profile_lower = active_profile_text.lower()
        skills_to_check = [
            "pytorch", "tensorflow", "scikit-learn", "python", "c++", "java", 
            "kubernetes", "docker", "gcp", "aws", "sql", "pandas", "ros", 
            "edge computing", "embedded ml", "data analytics", "unity"
        ]
        
        candidate_skills = []
        for s in skills_to_check:
            if s in profile_lower or s.replace(" ", "") in profile_lower:
                candidate_skills.append(s)
                
        # Build comparison grid against top demanded technologies
        skills_comparison = []
        for tech, count in sorted_techs:
            has_skill = "✅ Match" if tech.lower() in [c_s.lower() for c_s in candidate_skills] else "❌ Learn / Prep Needed"
            skills_comparison.append({
                "Technology Requirement": tech,
                "Ecosystem Demand (Firms)": count,
                "Your Resume Match": has_skill
            })
            
        if skills_comparison:
            comp_df = pd.DataFrame(skills_comparison)
            st.dataframe(comp_df, hide_index=True, use_container_width=True)
            
            # Show overall matching score KPI
            total_reqs = len(sorted_techs)
            matching_reqs = sum(1 for item in skills_comparison if "✅" in item["Your Resume Match"])
            skills_pct = int((matching_reqs / total_reqs) * 100) if total_reqs > 0 else 0
            
            st.markdown(f"✨ **Candidate Technology Alignment Rating**: `{skills_pct}%` compatibility with top aggregate demands.")
        else:
            st.info("No skill comparison calculated.")

    st.markdown("---")
    
    col_an3, col_an4 = st.columns(2)
    
    with col_an3:
        st.markdown("#### 💰 Salary Distribution by Location")
        salary_data = []
        for c in flat_companies:
            entry_sal, senior_sal = parse_salary(c.get("salary", ""))
            city = c.get("location", "").split(",")[0].strip()
            salary_data.append({
                "Company": c.get("name"),
                "Location": city,
                "Entry Salary (k€)": entry_sal / 1000.0,
                "Senior Salary (k€)": senior_sal / 1000.0
            })
            
        if salary_data:
            sal_df = pd.DataFrame(salary_data)
            st.scatter_chart(
                sal_df,
                x="Location",
                y="Entry Salary (k€)",
                color="Company",
                size="Senior Salary (k€)",
                use_container_width=True
            )
            st.caption("ℹ️ Bubble sizes represent Senior salary potentials. Y-axis values represent Entry compensation benchmarks (in thousands EUR).")
        else:
            st.info("No salary distributions calculated.")
            
    with col_an4:
        st.markdown("#### 🕸️ Competitor & Partner Networks")
        network_data = []
        for c in flat_companies:
            network_data.append({
                "Company": c.get("name"),
                "Strategic Domain": c.get("strategic_cluster"),
                "Corporate Pivot Focus": c.get("pivot", "Stable market segment"),
                "Competitors & Collaborators": c.get("network", "Ecosystem integration")
            })
        if network_data:
            net_df = pd.DataFrame(network_data)
            st.dataframe(net_df, hide_index=True, use_container_width=True)
        else:
            st.info("No network dynamics detected.")