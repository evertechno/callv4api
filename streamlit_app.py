import streamlit as st
import requests
import json

# Flask API URL (Replace with your deployed API endpoint)
API_URL = "https://your-api.onrender.com/analyze_email"

st.set_page_config(page_title="Advanced Email AI", page_icon="📧", layout="wide")
st.title("📨 Advanced Email AI Analysis & Insights")
st.write("Extract insights, generate professional responses, and analyze emails with AI.")

email_content = st.text_area("📩 Paste your email content here:", height=200)

# Process Email When Button Clicked
if email_content and st.button("🔍 Generate Insights"):
    try:
        # Send POST request to Flask API
        response = requests.post(API_URL, json={"email_content": email_content})
        
        if response.status_code == 200:
            analysis_data = response.json()

            st.subheader("📌 Email Summary")
            st.write(analysis_data.get("summary", "N/A"))

            st.subheader("✉️ Suggested Response")
            st.write(analysis_data.get("response", "N/A"))

            st.subheader("🎭 Email Tone")
            st.write(analysis_data.get("tone", "N/A"))

            st.subheader("⚠️ Urgency Level")
            st.write(analysis_data.get("urgency", "N/A"))

            st.subheader("📖 Readability Score")
            st.write(f"{analysis_data.get('readability', 'N/A')} / 10")

            st.subheader("💬 Sentiment Analysis")
            st.write(f"Sentiment: {analysis_data.get('sentiment', {}).get('label')} (Polarity: {analysis_data.get('sentiment', {}).get('polarity')})")

        else:
            st.error(f"Error: {response.json().get('error')}")

    except Exception as e:
        st.error(f"❌ Error: {e}")
