import streamlit as st
import pandas as pd
from PIL import Image
import os

# Page setup
st.set_page_config(page_title="YouTube & Reddit Sentiment Explorer", layout="wide")

# Custom CSS for margins
st.markdown("""
    <style>
    .main {
        max-width: 1000px;
        margin: 0 auto;
        padding: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Social Media Sentiment Dashboard")
st.markdown("This dashboard displays trending topics from YouTube and their sentiment analysis across YouTube and Reddit.")

# Load data
os.makedirs("data", exist_ok=True)

yt_df = pd.read_csv("data/youtube_data.csv")
llm_df = pd.read_csv("data/llm_insights.csv")

# Show sentiment plot
st.subheader("🎯 Sentiment Distribution: YouTube vs Reddit")
image = Image.open("data/sentiment_distribution.png")
st.image(image, caption="KDE Plot of Sentiment Scores", use_container_width=True)

# Show trending topics
st.subheader("🔥 Trending Topics")
top_topics = yt_df['video_title'].value_counts().head(10).index.tolist()
selected_topic = st.selectbox("Select a topic to explore insights:", top_topics)

# Show LLM analysis
filtered_llm = llm_df[llm_df['topic'] == selected_topic]

if not filtered_llm.empty:
    st.markdown("### 💡 LLM Summary & Insights")
    st.write(filtered_llm['llm_analysis'].values[0])
else:
    st.warning("No insights found for this topic.")