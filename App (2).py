import streamlit as st
from pytrends.request import TrendReq
import pandas as pd
from PIL import Image

# -------------------- Config --------------------
st.set_page_config(page_title="Trendlyzer", layout="centered", page_icon="🔍")

# -------------------- Styling --------------------
st.markdown("""
    <style>
        .stApp {
            background-color: #0f1117;
            color: #ffffff;
            font-family: 'Segoe UI', sans-serif;
        }
        .section {
            background-color: #1c1e26;
            padding: 1.5rem;
            border-radius: 12px;
            margin-bottom: 2rem;
            box-shadow: 0 4px 10px rgba(0,0,0,0.5);
        }
        .section-title {
            font-size: 1.5rem;
            font-weight: 700;
            margin-bottom: 1rem;
            color: #4fc3f7;
        }
        .chip {
            display: inline-block;
            background-color: #283046;
            border-radius: 20px;
            padding: 0.4rem 1rem;
            margin: 0.25rem;
            color: #ffffff;
            font-size: 0.85rem;
        }
    </style>
""", unsafe_allow_html=True)

# -------------------- Title --------------------
st.markdown("""
    <h1 style='text-align:center;'>Welcome to <span style='color:#36cfff;'>Trendlyzer</span></h1>
    <p style='text-align:center; color:#bbb;'>Visualize trending keywords, track interest over time, and discover related topics in one click.</p>
""", unsafe_allow_html=True)

# -------------------- Sidebar --------------------
st.sidebar.image("logo.png", width=120)
st.sidebar.header("📅 Keyword Setup")
keywords_input = st.sidebar.text_input("Enter keywords (comma-separated):", "AI, Blockchain, Data Science")
country = st.sidebar.selectbox("Select country:", ["Worldwide", "India", "United States", "United Kingdom", "Australia"], index=0)
time_range = st.sidebar.selectbox("Select time range:", ["today 3-m", "today 12-m", "today 5-y", "all"], index=0)

# Mapping country to geo codes
country_codes = {
    "Worldwide": "",
    "India": "IN",
    "United States": "US",
    "United Kingdom": "GB",
    "Australia": "AU"
}
geo = country_codes[country]

keywords = [kw.strip() for kw in keywords_input.split(",") if kw.strip()]

# -------------------- Connect to Pytrends --------------------
pytrends = TrendReq(hl='en-US', tz=330)

if keywords:
    with st.spinner("🔍 Fetching Google Trends data..."):
        try:
            pytrends.build_payload(keywords, cat=0, timeframe=time_range, geo=geo)
            interest_data = pytrends.interest_over_time()

            # --- Keyword Chips ---
            st.markdown(f"<div class='section'><div class='section-title'>🔑 Keywords Selected</div>", unsafe_allow_html=True)
            for kw in keywords:
                st.markdown(f"<span class='chip'>{kw}</span>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

            # --- Quick Stats ---
            st.markdown("### 📊 Quick Summary")
            st.metric(label="Top Keyword", value=keywords[0].title())
            st.metric(label="Total Keywords", value=len(keywords))
            st.metric(label="Time Range", value=time_range.replace('today ', '').replace('-', ' '))

            # --- Interest Over Time ---
            if not interest_data.empty:
                st.markdown("<div class='section'><div class='section-title'>📈 Interest Over Time</div>", unsafe_allow_html=True)
                st.line_chart(interest_data[keywords])
                st.dataframe(interest_data.drop(columns='isPartial'), use_container_width=True)
                csv = interest_data.to_csv().encode('utf-8')
                st.download_button("📂 Download Data", csv, file_name="interest_data.csv", mime="text/csv")
                st.markdown("</div>", unsafe_allow_html=True)

            # --- Trending Today ---
            try:
                trending_today = pytrends.today_searches(pn=geo if geo else 'US')
                if not trending_today.empty:
                    st.markdown("<div class='section'><div class='section-title'>🌍 Trending Searches Today</div>", unsafe_allow_html=True)
                    st.dataframe(trending_today, use_container_width=True)
                    st.markdown("</div>", unsafe_allow_html=True)
            except:
                pass  # Silent fail

            # --- Related Queries ---
            try:
                related_queries = pytrends.related_queries()
                has_queries = any((related_queries.get(kw, {}).get("top") is not None) for kw in keywords)
                if has_queries:
                    st.markdown("<div class='section'><div class='section-title'>🔎 Related Queries</div>", unsafe_allow_html=True)
                    for kw in keywords:
                        top = related_queries.get(kw, {}).get("top")
                        rising = related_queries.get(kw, {}).get("rising")
                        if top is not None and not top.empty:
                            st.markdown(f"**🔹 {kw} - Top Queries:**")
                            st.dataframe(top.head(), use_container_width=True)
                        if rising is not None and not rising.empty:
                            st.markdown(f"**🌟 {kw} - Rising Queries:**")
                            st.dataframe(rising.head(), use_container_width=True)
                    st.markdown("</div>", unsafe_allow_html=True)
            except:
                pass

        except Exception as e:
            st.error("An error occurred while fetching data. Please check your inputs or try again.")
else:
    st.info("Enter some keywords in the sidebar to get started.")
