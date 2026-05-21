import sys
from dotenv import load_dotenv

# Load environmental variables
load_dotenv()

def main():
    print("=" * 60)
    print("🚀 STARTING HIGH-FIDELITY KNOWLEDGE GRAPH PIPELINE 🚀")
    print("=" * 60)
    
    # 1. Run CrewAI Research Engine
    try:
        from research_engine import run_research
        run_research()
    except Exception as e:
        print(f"❌ Error during research phase: {e}")
        sys.exit(1)
        
    print("\n" + "=" * 60)
    print("🧠 RUNNING LLM ANALYSIS ENGINE (COMPATIBILITY & ROADMAPS) 🧠")
    print("=" * 60)
    
    # 2. Run LLM Analysis Engine
    try:
        from analysis_engine import run_analysis
        run_analysis()
    except Exception as e:
        print(f"❌ Error during analysis phase: {e}")
        sys.exit(1)
        
    print("\n" + "=" * 60)
    print("🎉 PIPELINE COMPLETED SUCCESSFULLY! 🎉")
    print("Researched data saved to raw_research_data.json.")
    print("Enriched data saved to dashboard_data.json.")
    print("Beautiful market analysis report written to marktanalyse_db.md.")
    print("=" * 60)

if __name__ == "__main__":
    main()