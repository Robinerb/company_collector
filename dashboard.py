import streamlit as st
import json
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load env variables and init OpenAI client
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(page_title="IT Company Dashboard", layout="wide")

def load_data():
    """Load JSON data or return fallback dictionary."""
    file_path = 'dashboard_data.json'
    if not os.path.exists(file_path):
        return {"Waiting for Agent": [{"name": "No Data", "description": "Run job_agent.py first to fetch data.", "location": "-", "status": "-", "salary": "-", "tech_stack": [], "pivot": "-", "network": "-"}]}
    with open(file_path, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {"Parsing Error": [{"name": "Invalid JSON", "description": "Error reading the JSON file.", "location": "-", "status": "-", "salary": "-", "tech_stack": [], "pivot": "-", "network": "-"}]}

def load_profile():
    """Load the user's CV/Profile data."""
    file_path = 'my_profil.txt'
    if not os.path.exists(file_path):
        return "No profile data available. Please create my_profil.txt."
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

data = load_data()
user_profile = load_profile()

# --- Sidebar: Chat interface ---
with st.sidebar:
    st.header("💬 Advisor Chat")
    
    # Init chat history and system prompt with BOTH Market Data and User Profile
    if "messages" not in st.session_state:
        context_str = json.dumps(data)
        system_msg = f"""You are a senior career advisor. 
        You have two sources of truth:
        1. Market Data (Companies & Salaries): {context_str}
        2. The User's Profile/CV: {user_profile}
        
        Use BOTH to answer questions. If the user asks for a fit, compare their specific skills from the profile to the tech stacks in the market data.
        Always answer in English."""
        
        st.session_state.messages = [{"role": "system", "content": system_msg}]

    # Render previous messages (skip system prompt)
    for msg in st.session_state.messages[1:]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Handle new user input
    if prompt := st.chat_input("Ask about your fit, salaries, or skills..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Fetch and show AI response
        with st.chat_message("assistant"):
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=st.session_state.messages
            ).choices[0].message.content
            st.markdown(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})

# --- Main: Dashboard layout ---
st.title("🗄️ IT-Company Knowledge Graph")

clusters = list(data.keys())
if clusters:
    selected_cluster = st.selectbox("Select strategic cluster:", clusters)
    st.markdown("---")

    companies = data[selected_cluster]
    cols = st.columns(3)

    for idx, comp in enumerate(companies):
        with cols[idx % 3]:
            st.subheader(comp.get("name", "Unknown"))
            st.caption(f"📍 {comp.get('location', 'N/A')} | {comp.get('status', 'N/A')}")
            st.markdown(f"*{comp.get('description', 'No description available.')}*")
            
            with st.expander("🔍 Deep-Dive & Details"):
                # NEW: Render Salary
                st.markdown(f"**💰 Salary:**\n{comp.get('salary', 'N/A')}")
                
                st.markdown("**Tech-Stack:**")
                tech_stack = comp.get("tech_stack", [])
                tags = " ".join([f"`{t}`" for t in tech_stack]) if tech_stack else "`Not specified`"
                st.markdown(tags)
                st.markdown(f"**🔄 Strategic Pivot:**\n{comp.get('pivot', 'N/A')}")
                st.markdown(f"**🕸️ Network Logic:**\n{comp.get('network', 'N/A')}")
else:
    st.warning("No clusters found in data.")