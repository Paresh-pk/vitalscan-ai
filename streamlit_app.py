import streamlit as st
import pandas as pd
import time
import uuid
import sys
import os

# Ensure project root is in Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set Page Config (Must be first Streamlit command)
st.set_page_config(
    page_title="VITALSCAN AI",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import Core Logic
# We wrap imports in try-except to handle potential path issues if run from different dirs
try:
    from app.core.risk_engine import MLRiskEngine
    from app.core.llm_service import LLMService
    from app.models.schemas import ClinicalInput
except ImportError:
    st.error("Could not import application modules. Make sure you are running this from the project root.")
    st.stop()

# --- Custom CSS ---
st.markdown("""
<style>
    .reportview-container {
        background: #0f172a;
    }
    .sidebar .sidebar-content {
        background: #1e293b;
    }
    h1, h2, h3 {
        color: #38bdf8 !important;
    }
    .stButton>button {
        background: linear-gradient(135deg, #38bdf8, #2dd4bf);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: bold;
    }
    .div[data-testid="stMetricValue"] {
        color: #38bdf8;
    }
</style>
""", unsafe_allow_html=True)

# --- State Management ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "assessment_id" not in st.session_state:
    st.session_state.assessment_id = str(uuid.uuid4())
if "risks" not in st.session_state:
    st.session_state.risks = None

# --- Resource Loading ---
@st.cache_resource
def load_engines():
    return MLRiskEngine(), LLMService()

import traceback

try:
    risk_engine, llm_service = load_engines()
except Exception as e:
    st.error(f"Failed to load engines: {e}")
    st.code(traceback.format_exc())
    st.stop()

# --- Sidebar: Health Input ---
with st.sidebar:
    st.title("🩺 Health Profile")
    st.markdown("---")
    
    # 1. Vitals
    st.subheader("Biological Stats")
    age = st.slider("Age", 18, 90, 30)
    bmi = st.slider("BMI", 15.0, 50.0, 24.0)
    systolic_bp = st.number_input("Systolic BP (mmHg)", 90, 200, 120)
    diastolic_bp = st.number_input("Diastolic BP (mmHg)", 60, 130, 80)
    
    # 2. Labs (Optional-ish in UI, but needed for model)
    st.subheader("Lab Values (Est.)")
    cholesterol = st.number_input("Total Cholesterol (mg/dL)", 100, 300, 180)
    hba1c = st.number_input("HbA1c (%)", 4.0, 15.0, 5.5)
    fasting_glucose = st.number_input("Fasting Glucose (mg/dL)", 70, 200, 90)
    
    # 3. Lifestyle
    st.subheader("Lifestyle")
    activity_level = st.select_slider(
        "Activity Level",
        options=["Sedentary", "Lightly Active", "Moderately Active", "Very Active"]
    )
    smoking_status = st.selectbox("Smoking Status", ["Never", "Former", "Current"])
    alcohol_intake = st.selectbox("Alcohol Consumption", ["None", "Occasional", "Moderate", "Heavy"])
    
    # 4. Habits
    st.subheader("Digital & Sleep")
    sleep_hours = st.slider("Sleep Hours", 4, 12, 7)
    screen_time = st.slider("Screen Time (Hours)", 0, 16, 6)
    
    analyze_btn = st.button("Analyze Health Risks 🚀", use_container_width=True)

# --- Main Content ---

# Header
col1, col2 = st.columns([3, 1])
with col1:
    st.title("VITALSCAN AI")
    st.markdown("### Next-Gen Predictive Health Analytics")
with col2:
    st.image("https://img.icons8.com/color/96/medical-doctor.png", width=80) 

# Logic: Run Analysis
if analyze_btn:
    with st.spinner("Processing bio-markers..."):
        # Map inputs to Schema
        input_data = ClinicalInput(
            age=age,
            bmi=bmi,
            systolic_bp=int(systolic_bp),
            diastolic_bp=int(diastolic_bp),
            cholesterol_total=int(cholesterol),
            hba1c=hba1c,
            fasting_glucose=int(fasting_glucose),
            smoking_status=smoking_status.lower(),
            physical_activity_level=activity_level.split(" ")[0].lower(),
            alcohol_consumption=alcohol_intake.lower(),
            family_history_diabetes=False,  # Simplified for UI
            family_history_hypertension=False,
            sleep_hours=sleep_hours,
            daily_screen_time=screen_time
        )
        
        # Get Risks
        risks = risk_engine.assess(input_data)
        st.session_state.risks = risks
        
        # Reset Chat on new analysis
        st.session_state.messages = []
        st.session_state.messages.append({"role": "assistant", "content": f"I've analyzed your profile. I see potential risks for {', '.join([r.disease for r in risks if r.probability > 0.3])}. How can I help you understand these results?"})

# Display Results if available
if st.session_state.risks:
    st.divider()
    st.header("🔍 Risk Assessment Results")
    
    # Create rows of 3 metrics
    cols = st.columns(3)
    for i, risk in enumerate(st.session_state.risks):
        with cols[i % 3]:
            # Color logic
            color = "green"
            if risk.risk_level.value == "High": color = "red"
            elif risk.risk_level.value == "Moderate": color = "orange"
            
            st.markdown(f"""
            <div style="padding: 1rem; border-radius: 10px; border: 1px solid rgba(255,255,255,0.1); background: rgba(255,255,255,0.05);">
                <h4 style="margin:0;">{risk.disease}</h4>
                <p style="color:{color}; font-weight:bold; font-size: 1.2rem;">{risk.risk_level.value}</p>
                <div style="background:#334155; height:8px; border-radius:4px; margin-top:0.5rem;">
                    <div style="width:{risk.probability*100}%; background:{color}; height:100%; border-radius:4px;"></div>
                </div>
                <p style="font-size:0.8rem; margin-top:0.5rem; color:#94a3b8;">
                    Drivers: {', '.join(risk.contributing_factors[:2])}
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Helper for chatbot context
            with st.expander(f"See Recommendations for {risk.disease}"):
                for step in risk.prevention_steps:
                    st.write(f"• {step}")

# --- AI Chatbot Section ---
st.divider()
st.header("💬 AI Health Assistant")

# Display history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User Input
if prompt := st.chat_input("Ask about your health risks..."):
    # 1. Show User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
        
    # 2. Generate AI Response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # Prepare context from risks if available
            context_str = ""
            if st.session_state.risks:
                context_str = f"Assessment Context: User has risks: {', '.join([r.disease + ' (' + r.risk_level.value + ')' for r in st.session_state.risks])}."
            
            # Call LLM Service
            # Note: We pass the history excluding the last user message which is appended by the service, 
            # but here we manage history explicitly. The service expects a list of dicts.
            # We'll adapt the wrapper to match what the service likely expects or just pass the message.
            
            # The LLMService.chat method expects: user_message, conversation_history
            # We need to convert st.session_state.messages to list of dicts if they aren't already (they are).
            
            full_prompt = prompt
            if context_str:
                full_prompt = f"{context_str}\n\nUser Question: {prompt}"
                
            response_text = llm_service.chat(
                user_message=prompt, # The service appends this to history, so we pass just the prompt
                conversation_history=st.session_state.messages[:-1] # Pass history distinct from current prompt
            )
            
            st.markdown(response_text)
            st.session_state.messages.append({"role": "assistant", "content": response_text})
