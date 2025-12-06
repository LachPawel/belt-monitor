"""Belt Monitor - Web UI (Streamlit)"""
import os
import requests
import streamlit as st
import pandas as pd

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Belt Monitor",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 Belt Monitor - Monitoring Taśmy Przenośnika")

# Sidebar configuration
st.sidebar.header("Konfiguracja")
min_width = st.sidebar.slider("Min. szerokość (px)", 50, 500, 100)
max_width = st.sidebar.slider("Max. szerokość (px)", 500, 3000, 2000)
seam_threshold = st.sidebar.slider("Czułość detekcji szwów", 0.1, 1.0, 0.3)
sample_rate = st.sidebar.slider("Sample rate", 1, 30, 1)

# File upload
st.header("📤 Załaduj plik do analizy")
uploaded_file = st.file_uploader(
    "Wybierz plik wideo lub obraz",
    type=["mp4", "avi", "mov", "jpg", "jpeg", "png"]
)

if uploaded_file:
    if st.button("🚀 Rozpocznij analizę", type="primary"):
        with st.spinner("Analizuję..."):
            try:
                files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
                params = {
                    "min_width_threshold": min_width,
                    "max_width_threshold": max_width,
                    "seam_threshold": seam_threshold,
                    "sample_rate": sample_rate
                }
                response = requests.post(
                    f"{API_URL}/api/v1/analyze",
                    files=files,
                    params=params,
                    timeout=300
                )
                
                if response.status_code == 200:
                    result = response.json()
                    st.success(f"✅ Analiza zakończona! ID: {result['analysis_id']}")
                    st.session_state["result"] = result
                else:
                    st.error(f"Błąd: {response.text}")
            except Exception as e:
                st.error(f"Błąd połączenia: {e}")

# Display results
if "result" in st.session_state:
    result = st.session_state["result"]
    
    st.header("📊 Wyniki analizy")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Segmenty", result["total_segments"])
    col2.metric("Klatki", result["total_frames"])
    col3.metric("FPS", f"{result['fps']:.1f}")
    col4.metric("Alerty", len(result["alerts"]))
    
    # Segments table
    if result["segments"]:
        st.subheader("📋 Segmenty")
        df = pd.DataFrame(result["segments"])
        df.columns = ["ID", "Start", "Koniec", "Min (px)", "Max (px)", "Śr. (px)", "Pomiary"]
        st.dataframe(df, use_container_width=True)
        
        # Chart
        st.subheader("📈 Wykres szerokości")
        chart_df = pd.DataFrame({
            "Segment": [s["segment_id"] for s in result["segments"]],
            "Min": [s["min_width_px"] for s in result["segments"]],
            "Max": [s["max_width_px"] for s in result["segments"]],
            "Średnia": [s["avg_width_px"] for s in result["segments"]]
        })
        st.line_chart(chart_df.set_index("Segment"))
    
    # Alerts
    if result["alerts"]:
        st.subheader("⚠️ Alerty")
        for alert in result["alerts"]:
            st.warning(f"[{alert['severity']}] Klatka {alert.get('frame', 'N/A')}: {alert['message']}")
    
    # Download buttons
    st.subheader("📥 Pobierz raporty")
    col1, col2, col3 = st.columns(3)
    
    analysis_id = result["analysis_id"]
    col1.markdown(f"[📊 Excel]({API_URL}/api/v1/reports/{analysis_id}/excel)")
    col2.markdown(f"[📄 CSV]({API_URL}/api/v1/reports/{analysis_id}/csv)")
    col3.markdown(f"[📋 JSON]({API_URL}/api/v1/reports/{analysis_id}/json)")

# Footer
st.divider()
st.caption("Belt Monitor v1.0 - JSW IT Systems Hackathon")
