# app.py - Sustainable Smart City Assistant
import streamlit as st
from langchain_ibm import WatsonxLLM
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
from datetime import datetime
from fpdf import FPDF
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import os
import json

# Page config
st.set_page_config(page_title="🌍 Sustainable Smart City Assistant", layout="wide", page_icon="🌍")

# Custom CSS
st.markdown("""
<style>
body {
    background-color: #f9f9f9;
    font-family: Arial, sans-serif;
}
.container {
    padding: 20px;
    max-width: 1200px;
    margin: auto;
}
.card {
    background: white;
    border-radius: 10px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    padding: 20px;
    margin-bottom: 20px;
}
h2 {
    color: #2c3e50;
    border-left: 5px solid #3498db;
    padding-left: 10px;
}
button {
    background-color: #3498db;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 5px;
    cursor: pointer;
}
button:hover {
    background-color: #2980b9;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "feedback_logs" not in st.session_state:
    st.session_state.feedback_logs = []

# Load Watsonx credentials
try:
    credentials = {
        "url": os.getenv("WATSONX_URL"),
        "apikey": os.getenv("WATSONX_APIKEY")
    }
    project_id = os.getenv("PROJECT_ID")
except Exception as e:
    st.warning("⚠️ Missing Watsonx credentials in environment.")
    st.stop()

# IBM Watsonx Granite LLM Setup
def get_llm():
    return WatsonxLLM(
        model_id="ibm/granite-13b-instruct-v2",
        url=credentials["url"],
        apikey=credentials["apikey"],
        project_id=project_id,
        params={
            "decoding_method": "greedy",
            "min_new_tokens": 50,
            "max_new_tokens": 300
        },
    )

# PDF Exporter
def export_city_report(summary):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, txt="Smart City Report Summary", ln=True, align='C')
    pdf.ln(10)
    pdf.multi_cell(0, 10, txt=summary)
    return pdf.output(dest='S').encode('latin-1')

# Sidebar Menu
st.sidebar.title("🧭 Navigation")
menu = st.sidebar.radio("Go to", [
    "Home",
    "Policy Summarizer",
    "Chat Assistant",
    "KPI Forecasting",
    "Citizen Feedback",
    "Eco Tips",
    "Anomaly Detection"
])

# Home Page
if menu == "Home":
    st.title("🌍 Sustainable Smart City Assistant")
    st.subheader("AI-Powered Platform for Urban Sustainability")
    st.markdown("""
    Welcome to the Sustainable Smart City Assistant!
    
    This platform empowers urban planners, administrators, and citizens to collaborate on sustainable city development.
    
    ### 🧭 Navigate Using the Sidebar to:
    - Upload policy documents for summarization
    - Chat with the AI assistant
    - Forecast KPIs using machine learning
    - Submit citizen feedback
    - Get eco-tips
    - Detect anomalies in data
    """)
    st.image("https://images.unsplash.com/photo-1573164713714-0b99ae3f1ffd?ixlib=rb-4.0.3&auto=format&fit=crop&w=1950&q=80", use_column_width=True)

# Policy Summarizer
elif menu == "Policy Summarizer":
    st.title("📄 Policy Document Summarizer")
    uploaded_file = st.file_uploader("Upload a policy document (.txt)", type="txt")
    if uploaded_file:
        content = uploaded_file.read().decode("utf-8")
        llm = get_llm()
        prompt = f"Summarize this policy document:\n\n{content}"
        summary = llm.invoke(prompt)
        st.markdown("### 📝 Summary")
        st.write(summary)
        pdf_data = export_city_report(summary)
        st.download_button("📥 Download as PDF", data=pdf_data, file_name="policy_summary.pdf", mime="application/pdf")

# Chat Assistant
elif menu == "Chat Assistant":
    st.title("🤖 City Assistant Chatbot")
    user_input = st.text_area("Ask anything about sustainability or city planning:")
    if st.button("Send"):
        with st.spinner("🧠 Thinking..."):
            llm = get_llm()
            prompt = f"You are a smart city assistant. Answer the following query:\n{user_input}"
            response = llm.invoke(prompt)
            st.markdown(f"**Assistant:** {response}")

# KPI Forecasting
elif menu == "KPI Forecasting":
    st.title("📈 KPI Forecasting Tool")
    st.markdown("Enter historical KPI values to forecast future trends.")
    values = st.text_input("Historical KPI Values (comma-separated)")
    if st.button("Predict"):
        try:
            kpi_values = list(map(float, values.split(",")))
            X = np.arange(len(kpi_values)).reshape(-1, 1)
            y = np.array(kpi_values).reshape(-1, 1)
            model = LinearRegression()
            model.fit(X, y)
            future_X = np.array(range(len(kpi_values), len(kpi_values) + 5)).reshape(-1, 1)
            predictions = model.predict(future_X).flatten()
            st.markdown("### 🔮 Predicted Future Values")
            st.write(predictions.tolist())
            df = pd.DataFrame({
                "Time": list(range(len(kpi_values))) + list(range(len(kpi_values), len(kpi_values)+5)),
                "Value": kpi_values + predictions.tolist()
            })
            fig = px.line(df, x="Time", y="Value", title="KPI Trend Forecast")
            st.plotly_chart(fig)
        except Exception as e:
            st.error("🚨 Invalid input format.")

# Citizen Feedback
elif menu == "Citizen Feedback":
    st.title("📢 Citizen Feedback Reporting")
    issue = st.text_area("Describe the issue")
    category = st.selectbox("Category", ["Water", "Energy", "Transport", "Waste", "Other"])
    if st.button("Submit Feedback"):
        st.session_state.feedback_logs.append({
            "issue": issue,
            "category": category,
            "timestamp": datetime.now().isoformat()
        })
        st.success("✅ Feedback submitted successfully!")

    if st.checkbox("Show All Submissions"):
        st.markdown("### 📋 Submitted Feedback")
        for log in st.session_state.feedback_logs:
            st.markdown(f"- [{log['category']}] {log['issue']}")

# Eco Tips
elif menu == "Eco Tips":
    st.title("🌱 Eco-Tip Generator")
    keywords = st.text_input("Enter keywords (e.g., 'plastic', 'solar')")
    if st.button("Get Tips"):
        llm = get_llm()
        prompt = f"Generate actionable eco-tips related to '{keywords}'"
        response = llm.invoke(prompt)
        st.markdown(f"💡 **Tips for '{keywords}':**\n{response}")

# Anomaly Detection
elif menu == "Anomaly Detection":
    st.title("🔍 Energy Usage Anomaly Detector")
    st.markdown("Upload monthly energy consumption data (CSV) to detect anomalies.")
    uploaded_file = st.file_uploader("Upload CSV", type="csv")
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.markdown("### 📊 Uploaded Data")
        st.dataframe(df.head())
        st.markdown("### 📈 Line Chart")
        st.line_chart(df)
        st.markdown("### ⚠️ Detected Anomalies")
        mean = df.mean(numeric_only=True)
        std = df.std(numeric_only=True)
        z_scores = (df - mean) / std
        anomalies = df[(z_scores > 3).any(axis=1)]
        if not anomalies.empty:
            st.warning("🚨 Anomalies detected!")
            st.write(anomalies)
        else:
            st.success("✅ No anomalies found.")

# Footer
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>© 2025 Sustainable Smart City Assistant | Built with ❤️ using Streamlit & IBM Watsonx</p>", unsafe_allow_html=True)

