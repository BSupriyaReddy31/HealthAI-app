# Importing Libraries
import streamlit as st
from langchain_ibm import WatsonxLLM
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
from datetime import datetime, timedelta
from fpdf import FPDF
import json
import random
import plotly.express as px
import pandas as pd

# Page config
st.set_page_config(page_title="🩺 Health Assistant", layout="wide", page_icon="🩺")

# Custom CSS - Violet and Pink Theme
st.markdown("""
<style>
    * {box-sizing: border-box; margin: 0; padding: 0;}
    body {
        background: linear-gradient(to right bottom, #f5e6fa, #ffe5f5);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: #2c3e50;
        line-height: 1.6;
        padding: 20px;
    }
    h1,h2,h3,h4,h5,h6 {color: #8e44ad; font-weight: 600; margin-bottom: 10px;}
    p {font-size: 16px; color: #34495e;}
    a {color: #8e44ad; text-decoration: none;} a:hover {text-decoration: underline;}
    .main {
        background-color: #ffffffcc;
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 30px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.1);
        max-width: 1200px;
        margin: auto;
        animation: fadeIn 0.5s ease-in-out;
    }
    @keyframes fadeIn {from {opacity: 0; transform: translateY(10px);} to {opacity: 1; transform: translateY(0);}}
    .card {
        background-color: #fff;
        border-left: 6px solid #8e44ad;
        border-radius: 12px;
        padding: 25px;
        margin: 20px 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    } 
    .card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.1);
    }
    .navbar {
        display: flex;
        justify-content: center;
        gap: 20px;
        padding: 15px 0;
        background: linear-gradient(to right, #8e44ad, #ec7063);
        border-radius: 12px;
        margin-bottom: 30px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.15);
        position: sticky;
        top: 0;
        z-index: 999;
        transition: all 0.3s ease;
    }
    .nav-button {
        background-color: #ffffff;
        color: #8e44ad;
        border: none;
        width: 60px;
        height: 60px;
        font-size: 24px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .nav-button:hover {
        background-color: #f9ebf7;
        transform: scale(1.1);
    }
    .nav-button:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }
    label {
        font-weight: bold;
        color: #34495e;
        display: block;
        margin-top: 15px;
        margin-bottom: 6px;
    }
    input,select,textarea,.stTextInput input,.stNumberInput input,.stDateInput input {
        border-radius: 8px;
        border: 1px solid #ccc;
        padding: 12px 14px;
        width: 100%;
        font-size: 14px;
        outline: none;
        transition: all 0.3s ease;
    }
    input:focus,select:focus,textarea:focus,.stTextInput input:focus,.stNumberInput input:focus,.stDateInput input:focus {
        border-color: #8e44ad;
        box-shadow: 0 0 0 2px rgba(142,68,173,0.2);
    }
    button {
        background-color: #8e44ad;
        color: white;
        border: none;
        padding: 12px 20px;
        font-size: 14px;
        border-radius: 8px;
        cursor: pointer;
        transition: background-color 0.3s ease, transform 0.2s ease;
    }
    button:hover {
        background-color: #732d91;
        transform: translateY(-2px);
    }
    button:active {
        transform: translateY(0);
    }
</style>
""", unsafe_allow_html=True)

# Language support
LANGUAGES = {
    "en": {
        "title": "🩺 Health Assistant",
        "subtitle": "Ask about symptoms, treatments, diagnostics, and wellness.",
        "welcome": "🩺 Welcome to Your Personalized Health Assistant",
        "chat": "🤖 AI Chatbot",
        "symptoms": "🧠 Symptom Checker",
        "treatment": "💊 Treatment Planner",
        "diseases": "🫀 Chronic Disease Management",
        "reports": "📈 Progress Reports",
        "settings": "⚙️ Settings & Preferences",
        "footer": "© 2025 MyHospital Health Assistant | Built with ❤️ using Streamlit & Watsonx",
        "save_profile": "Save Profile",
        "generate_ai_report": "Generate AI Report Summary",
        "export_pdf": "📄 Export Report as PDF"
    },
    "es": {
        "title": "🩺 Asistente de Salud",
        "subtitle": "Pregunte sobre síntomas, tratamientos y bienestar general.",
        "welcome": "🩺 Bienvenido a su Asistente de Salud Personalizado",
        "chat": "🤖 Chatbot con IA",
        "symptoms": "🧠 Revisión de Síntomas",
        "treatment": "💊 Plan de Tratamiento",
        "diseases": "🫀 Manejo de Enfermedades Crónicas",
        "reports": "📈 Informes de Progreso",
        "settings": "⚙️ Configuración y Preferencias",
        "footer": "© 2025 Asistente de Salud | Hecho con ❤️ usando Streamlit & Watsonx",
        "save_profile": "Guardar Perfil",
        "generate_ai_report": "Generar Informe con IA",
        "export_pdf": "📄 Exportar Informe como PDF"
    },
    "fr": {
        "title": "🩺 Assistant Santé",
        "subtitle": "Posez des questions sur les symptômes, traitements et bien-être.",
        "welcome": "🩺 Bienvenue dans votre Assistant Santé Personnel",
        "chat": "🤖 Chatbot avec IA",
        "symptoms": "🧠 Analyse des Symptômes",
        "treatment": "💊 Plan de Traitement",
        "diseases": "🫀 Suivi des Maladies Chroniques",
        "reports": "📈 Rapports de Suivi",
        "settings": "⚙️ Paramètres et Préférences",
        "footer": "© 2025 Assistant Santé | Réalisé avec ❤️ en utilisant Streamlit & Watsonx",
        "save_profile": "Enregistrer le Profil",
        "generate_ai_report": "Générer un Résumé IA",
        "export_pdf": "📄 Exporter le Rapport en PDF"
    }
}

# Initialize session state
if "profile_complete" not in st.session_state:
    st.session_state.profile_complete = False
if "profile_data" not in st.session_state:
    st.session_state.profile_data = {}
if "current_section" not in st.session_state:
    st.session_state.current_section = "profile"
if "messages" not in st.session_state:
    st.session_state.messages = []
if "language" not in st.session_state:
    st.session_state.language = "en"
if "analytics_data" not in st.session_state:
    st.session_state.analytics_data = {
        "dates": [],
        "heart_rates": [],
        "glucose_levels": [],
        "peak_flow": [],
        "hba1c": []
    }

# Header
lang = st.session_state.language
st.markdown(f'<h1 style="text-align:center;">{LANGUAGES[lang]["title"]}</h1>', unsafe_allow_html=True)
st.markdown(f'<p style="text-align:center; font-size:16px;">{LANGUAGES[lang]["subtitle"]}</p>', unsafe_allow_html=True)

# Navigation bar
def render_navbar():
    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
    with col1:
        if st.button("챗", key="btn_chat", use_container_width=True, disabled=not st.session_state.profile_complete):
            st.session_state.current_section = "chat"
    with col2:
        if st.button("🧠", key="btn_symptoms", use_container_width=True, disabled=not st.session_state.profile_complete):
            st.session_state.current_section = "symptoms"
    with col3:
        if st.button("💊", key="btn_treatment", use_container_width=True, disabled=not st.session_state.profile_complete):
            st.session_state.current_section = "treatment"
    with col4:
        if st.button("🫀", key="btn_diseases", use_container_width=True, disabled=not st.session_state.profile_complete):
            st.session_state.current_section = "diseases"
    with col5:
        if st.button("📊", key="btn_reports", use_container_width=True, disabled=not st.session_state.profile_complete):
            st.session_state.current_section = "reports"
    with col6:
        if st.button("🧾", key="btn_profile", use_container_width=True):
            st.session_state.current_section = "profile"
    with col7:
        if st.button("⚙️", key="btn_settings", use_container_width=True):
            st.session_state.current_section = "settings"

render_navbar()

# Load Watsonx credentials
try:
    from streamlit.secrets import Secrets
    credentials = {
        "url": st.secrets["WATSONX_URL"],
        "apikey": st.secrets["WATSONX_APIKEY"]
    }
    project_id = st.secrets["WATSONX_PROJECT_ID"]
    
    model_map = {
        "chat": "ibm/granite-13b-instruct-v2",
        "symptoms": "ibm/granite-13b-instruct-v2",
        "treatment": "ibm/granite-13b-instruct-v2",
        "diseases": "ibm/granite-13b-instruct-v2",
        "reports": "ibm/granite-13b-instruct-v2"
    }

    def get_llm(model_name):
        return WatsonxLLM(
            model_id=model_map[model_name],
            url=credentials.get("url"),
            apikey=credentials.get("apikey"),
            project_id=project_id,
            params={
                GenParams.DECODING_METHOD: "greedy",
                GenParams.TEMPERATURE: 0.7,
                GenParams.MIN_NEW_TOKENS: 5,
                GenParams.MAX_NEW_TOKENS: 300,
                GenParams.STOP_SEQUENCES: ["Human:", "Observation"],
            },
        )
except KeyError:
    st.warning("⚠️ Watsonx credentials missing.")
    st.stop()
except Exception as e:
    st.error(f"🚨 Error initializing LLM: {str(e)}")
    st.stop()

# Save profile function
def save_profile(name, age, gender, height, weight):
    st.session_state.profile_data = {
        "name": name,
        "age": age,
        "gender": gender,
        "height": height,
        "weight": weight,
        "bmi": round(weight / ((height / 100) ** 2), 1)
    }
    st.session_state.profile_complete = True
    st.success("✅ Profile saved successfully!")

# Reset profile function
def reset_profile():
    st.session_state.profile_complete = False
    st.session_state.profile_data = {}
    st.session_state.messages = []
    st.session_state.analytics_data = {
        "dates": [],
        "heart_rates": [],
        "glucose_levels": [],
        "peak_flow": [],
        "hba1c": []
    }
    st.rerun()

# Export report as PDF
def export_health_report(ai_summary=""):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.set_fill_color(200, 220, 255)
    pdf.cell(0, 15, txt="Health Report Summary", ln=True, align='C', fill=True)
    pdf.ln(10)
    # Patient Info
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "👤 Patient Profile", ln=True)
    pdf.set_font("Arial", size=12)
    for k, v in st.session_state.profile_data.items():
        if v:
            pdf.cell(0, 8, f"• {k.capitalize()}: {v}", ln=True)
    pdf.ln(10)
    # Latest metrics
    dates = st.session_state.analytics_data.get("dates", [])
    heart_rates = st.session_state.analytics_data.get("heart_rates", [])
    glucose_levels = st.session_state.analytics_data.get("glucose_levels", [])
    pdf.cell(0, 10, "📊 Latest Metrics", ln=True)
    pdf.cell(0, 8, f"• Date: {dates[-1] if len(dates) > 0 else 'N/A'}", ln=True)
    pdf.cell(0, 8, f"• Heart Rate: {heart_rates[-1] if len(heart_rates) > 0 else 'N/A'} bpm", ln=True)
    pdf.cell(0, 8, f"• Blood Glucose: {glucose_levels[-1] if len(glucose_levels) > 0 else 'N/A'} mg/dL", ln=True)
    pdf.ln(10)
    # AI Insights
    if ai_summary:
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "🧠 AI Report Summary", ln=True)
        pdf.set_font("Arial", size=12)
        for line in ai_summary.split('\n'):
            if line.strip():
                pdf.multi_cell(0, 8, line.strip())
        pdf.ln(10)
    # Footer
    pdf.set_y(-30)
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(0, 10, "Generated by Health Analytics Dashboard © All rights reserved", align='C')
    return pdf.output(dest='S').encode('latin-1')

# Functionality Sections
if st.session_state.current_section == "profile":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h2>🧾 Complete Your Profile</h2>', unsafe_allow_html=True)
    name = st.text_input("Full Name")
    age = st.number_input("Age", min_value=0, max_value=120)
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    height = st.number_input("Height (cm)", min_value=50, max_value=250)
    weight = st.number_input("Weight (kg)", min_value=10, max_value=300)
    if st.button("Save Profile"):
        if name and age > 0 and height > 0 and weight > 0:
            save_profile(name, age, gender, height, weight)
        else:
            st.error("❌ Please fill in all fields.")
    if st.session_state.profile_complete:
        st.markdown('<br>', unsafe_allow_html=True)
        if st.button("🔄 Reset Profile"):
            reset_profile()
    st.markdown('</div>')

elif st.session_state.current_section == "chat":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h2>🤖 Enhanced Health Assistant Chatbot</h2>', unsafe_allow_html=True)
    for role, content in st.session_state.messages:
        bubble_class = "user-bubble" if role == "user" else "bot-bubble"
        st.markdown(f'<div class="{bubble_class}"><b>{role.capitalize()}:</b> {content}</div>', unsafe_allow_html=True)
    with st.form(key='chat_form', clear_on_submit=True):
        user_input = st.text_input("Your question:")
        submit_button = st.form_submit_button(label="Send")
    if submit_button and user_input:
        st.session_state.messages.append(("user", user_input))
        profile_info = "\n".join([f"{k.capitalize()}: {v}" for k, v in st.session_state.profile_data.items()])
        query_lower = user_input.lower()
        category = "general"
        if any(word in query_lower for word in ["symptom", "pain", "ache", "fever", "headache"]):
            category = "symptoms"
        elif any(word in query_lower for word in ["treat", "medication", "therapy", "prescribe"]):
            category = "treatment"
        elif any(word in query_lower for word in ["glucose", "blood sugar", "insulin", "bp", "pressure"]):
            category = "diseases"
        elif any(word in query_lower for word in ["ai", "report", "analyze", "summary"]):
            category = "reports"
        prompt = f"""
You are a professional medical assistant AI helping a patient with their health queries.
Use the following guidelines:
- Be empathetic, informative, and clear.
- Always mention that you're not a substitute for real medical advice.
- If unsure, recommend consulting a physician.
Patient Profile:
{profile_info}
Chat History:
{''.join([f'{r.capitalize()}: {c}\n' for r, c in st.session_state.messages[-6:]])}
User Question: "{user_input}"
Based on the question category ("{category}"), provide a detailed response that includes:
1. Medical interpretation of the query
2. Possible causes or implications
3. Suggested actions or precautions
4. When to consult a doctor
Answer:
"""
        try:
            llm = get_llm("chat")
            response = llm.invoke(prompt).strip()
            st.session_state.messages.append(("assistant", response))
            st.rerun()
        except Exception as e:
            st.session_state.messages.append(("assistant", f"🚨 Error: {str(e)}"))
            st.rerun()
    st.markdown('</div>')

elif st.session_state.current_section == "symptoms":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h2>🧠 Symptom Checker</h2>', unsafe_allow_html=True)
    symptom_description = st.text_area("Describe your symptoms...")
    if st.button("Check Symptoms") and symptom_description.strip():
        prompt = f"""
You are a medical AI assistant. Based on the following symptoms, list the most likely conditions.
Patient Profile: {json.dumps(st.session_state.profile_data)}
Symptoms: {symptom_description}
Provide:
1. Most likely condition
2. Alternative possibilities
3. Likelihood percentages
4. Recommended next steps
Keep it concise.
"""
        try:
            llm = get_llm("symptoms")
            response = llm.invoke(prompt).strip()
            st.markdown(f"🩺 Diagnosis Results:\n{response}")
        except Exception as e:
            st.error(f"🚨 Error: {str(e)}")
    st.markdown('</div>')

elif st.session_state.current_section == "treatment":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h2>💊 Personalized Treatment Suggestions</h2>', unsafe_allow_html=True)
    condition = st.text_input("Condition or Diagnosis")
    duration = st.selectbox("Duration", ["Acute", "Chronic"])
    if st.button("Generate Treatment Plan") and condition:
        prompt = f"""
Based on this profile and condition:
Name: {st.session_state.profile_data.get('name', 'Unknown')}
Age: {st.session_state.profile_data.get('age', 'Unknown')}
Gender: {st.session_state.profile_data.get('gender', 'Unknown')}
BMI: {st.session_state.profile_data.get('bmi', 'Unknown')}
Condition: {condition}
Duration: {duration}
Include:
1. Medications
2. Lifestyle changes
3. Follow-up care
4. Complications to monitor
"""
        try:
            llm = get_llm("treatment")
            response = llm.invoke(prompt).strip()
            st.markdown(f"💡 Plan:\n{response}")
        except Exception as e:
            st.error(f"🚨 Error: {str(e)}")
    st.markdown('</div>')

elif st.session_state.current_section == "diseases":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h2>🫀 Chronic Disease Management</h2>', unsafe_allow_html=True)
    condition = st.selectbox("Select Chronic Condition", ["Diabetes", "Hypertension", "Asthma"])
    tab1, tab2 = st.tabs(["➕ Log New Entry", "📊 View Trends"])
    with tab1:
        if condition == "Diabetes":
            glucose = st.number_input("Blood Glucose Level (mg/dL)", min_value=40, max_value=400, step=5)
            date = st.date_input("Measurement Date", value=datetime.today())
            if st.button("✅ Log Glucose Reading"):
                st.session_state.analytics_data.setdefault("glucose_log", []).append({"value": glucose, "date": date.strftime("%Y-%m-%d")})
                st.success(f"✅ Logged: {glucose} mg/dL on {date.strftime('%Y-%m-%d')}")
        elif condition == "Hypertension":
            systolic = st.number_input("Systolic BP", min_value=90, max_value=200)
            diastolic = st.number_input("Diastolic BP", min_value=60, max_value=130)
            date = st.date_input("Measurement Date", value=datetime.today())
            if st.button("✅ Log Blood Pressure"):
                st.session_state.analytics_data.setdefault("bp_log", []).append({
                    "systolic": systolic,
                    "diastolic": diastolic,
                    "date": date.strftime("%Y-%m-%d")
                })
                st.success(f"✅ Logged: {systolic}/{diastolic} mmHg on {date.strftime('%Y-%m-%d')}")
        elif condition == "Asthma":
            triggers = st.text_area("Triggers Today")
            severity = st.slider("Severity (1-10)", 1, 10)
            date = st.date_input("Episode Date", value=datetime.today())
            if st.button("✅ Log Asthma Episode"):
                st.session_state.analytics_data.setdefault("asthma_log", []).append({
                    "triggers": triggers,
                    "severity": severity,
                    "date": date.strftime("%Y-%m-%d")
                })
                st.success(f"✅ Episode logged on {date.strftime('%Y-%m-%d')}")
    with tab2:
        if condition == "Diabetes" and st.session_state.analytics_data.get("glucose_log"):
            df = pd.DataFrame(st.session_state.analytics_data["glucose_log"])
            fig = px.line(df, x='date', y='value', title='Glucose Levels Over Time')
            st.plotly_chart(fig, use_container_width=True)
        elif condition == "Hypertension" and st.session_state.analytics_data.get("bp_log"):
            df = pd.DataFrame(st.session_state.analytics_data["bp_log"])
            fig = px.line(df, x='date', y='systolic', title='Systolic BP Trend')
            st.plotly_chart(fig, use_container_width=True)
        elif condition == "Asthma" and st.session_state.analytics_data.get("asthma_log"):
            df = pd.DataFrame(st.session_state.analytics_data["asthma_log"])
            fig = px.bar(df, x='date', y='severity', color='triggers', title='Asthma Severity by Trigger')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("ℹ️ No data yet.")
    st.markdown('</div>')

elif st.session_state.current_section == "reports":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<h2>📈 Health Analytics Dashboard</h2>', unsafe_allow_html=True)
    range_type = st.selectbox("Select Range Type", ["By Day", "By Week", "By Month"])
    dates_to_add = []
    if range_type == "By Day":
        dr = st.date_input("Select Date Range", value=(datetime.today(), datetime.today()))
        if len(dr) == 2:
            start_date, end_date = dr
            delta = (end_date - start_date).days + 1
            dates_to_add = [(start_date + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(delta)]
    elif range_type == "By Week":
        start_week = st.date_input("Start of Week", value=datetime.today())
        weeks = st.number_input("Weeks", min_value=1, max_value=52, value=1)
        for week in range(weeks):
            base = start_week + timedelta(weeks=week)
            for i in range(7):
                dates_to_add.append((base + timedelta(days=i)).strftime("%Y-%m-%d"))
    elif range_type == "By Month":
        year = st.number_input("Year", 2000, 2100, datetime.now().year)
        month = st.slider("Month", 1, 12, datetime.now().month)
        first_day_next_month = datetime(year if month < 12 else year+1, (month % 12)+1 if month != 12 else 1, 1)
        last_day_of_month = (first_day_next_month - timedelta(days=1)).day
        dates_to_add = [f"{year}-{str(month).zfill(2)}-{str(day).zfill(2)}" for day in range(1, last_day_of_month+1)]

    default_data = pd.DataFrame({
        'Date': dates_to_add,
        'Heart Rate (bpm)': [''] * len(dates_to_add),
        'Blood Glucose (mg/dL)': [''] * len(dates_to_add),
        'Peak Flow (L/min)': [''] * len(dates_to_add),
        'HbA1c (%)': [''] * len(dates_to_add)
    })
    edited_df = st.data_editor(default_data, num_rows="dynamic")
    if st.button("➕ Add Bulk Metrics"):
        success_count = 0
        for _, row in edited_df.iterrows():
            try:
                hr = int(row['Heart Rate (bpm)']) if pd.notna(row['Heart Rate (bpm)']) else None
                gluc = int(row['Blood Glucose (mg/dL)']) if pd.notna(row['Blood Glucose (mg/dL)']) else None
                peak = float(row['Peak Flow (L/min)']) if pd.notna(row['Peak Flow (L/min)']) else None
                hba1c = float(row['HbA1c (%)']) if pd.notna(row['HbA1c (%)']) else None
                valid = True
                if hr is not None and not (40 <= hr <= 140): valid = False
                if gluc is not None and not (50 <= gluc <= 200): valid = False
                if peak is not None and not (100 <= peak <= 800): valid = False
                if hba1c is not None and not (4 <= hba1c <= 12): valid = False
                if valid:
                    st.session_state.analytics_data["dates"].append(row['Date'])
                    st.session_state.analytics_data["heart_rates"].append(hr)
                    st.session_state.analytics_data["glucose_levels"].append(gluc)
                    st.session_state.analytics_data["peak_flow"].append(peak)
                    st.session_state.analytics_data["hba1c"].append(hba1c)
                    success_count += 1
            except Exception as e:
                st.warning(f"⚠️ Error processing row: {str(e)}")
        if success_count > 0:
            st.success(f"✅ Added {success_count} metric(s)!")

    # Generate AI Summary
    ai_summary = ""
    if st.button("🧠 Generate Enhanced AI Report Summary"):
        profile_info = "\n".join([f"{k.capitalize()}: {v}" for k, v in st.session_state.profile_data.items()])
        recent_hr = ', '.join(map(str, st.session_state.analytics_data["heart_rates"][-7:]))
        recent_gluc = ', '.join(map(str, st.session_state.analytics_data["glucose_levels"][-7:]))
        prompt = f"""
You are a healthcare AI assistant. Provide a personalized health summary based on collected metrics.
Patient Profile:
{profile_info}
Recent Metrics:
Heart Rate: [{recent_hr}]
Blood Glucose: [{recent_gluc}]
Format:
- Trend Overview
- Health Implications
- Recommendations
- Important Notes
"""
        try:
            llm = get_llm("reports")
            ai_summary = llm.invoke(prompt).strip()
            st.markdown(f"🧠 **AI Report Summary:**\n{ai_summary}")
        except Exception as e:
            st.error(f"🚨 Error generating summary: {str(e)}")

    # Export PDF
    if st.session_state.profile_complete:
        pdf_data = export_health_report(ai_summary)
        st.download_button("📄 Export PDF", pdf_data, "health_report.pdf", "application/pdf")
    st.markdown('</div>')

elif st.session_state.current_section == "settings":
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown(f'<h2>⚙️ {LANGUAGES[lang]["settings"]}</h2>', unsafe_allow_html=True)
    language = st.selectbox("Language", ["en", "es", "fr"], format_func=lambda x: {"en": "English", "es": "Español", "fr": "Français"}[x])
    theme = st.selectbox("Color Theme", ["Light"], disabled=True)
    font_size = st.slider("Font Size", 12, 24, 16)
    if st.button("💾 Save Preferences"):
        st.session_state.language = language
        st.session_state.font_size = font_size
        st.success("✅ Preferences saved!")
    st.markdown('</div>')

# Footer
st.markdown(f'<p style="text-align:center; font-size:14px;">{LANGUAGES[lang]["footer"]}</p>', unsafe_allow_html=True)

# Debug Mode
with st.expander("🔧 Debug Mode"):
    st.write("Session State:", st.session_state)
