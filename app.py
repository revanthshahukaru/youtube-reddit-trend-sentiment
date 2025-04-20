import streamlit as st
import pandas as pd
from PIL import Image
import os
import re

# Page setup
st.set_page_config(page_title="YouTube & Reddit Sentiment Explorer", layout="wide")

# Custom CSS for margins
st.markdown("""
    <style>
    .block-container {
        max-width: 1000px;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Social Media Sentiment Dashboard")
st.markdown("This dashboard displays trending topics from YouTube and their sentiment analysis across YouTube and Reddit.")

# Ensure data folder exists
os.makedirs("data", exist_ok=True)

# Load data
yt_df = pd.read_csv("data/youtube_data.csv")
llm_df = pd.read_csv("data/llm_insights.csv")

# Get unique video list for dropdown
unique_videos = yt_df[['video_title', 'channel', 'video_url']].drop_duplicates()
video_titles = unique_videos['video_title'].tolist()

# Select topic
st.subheader("🔥 Trending Topics")
selected_topic = st.selectbox("Select a topic to explore insights:", video_titles)
selected_video = unique_videos[unique_videos['video_title'] == selected_topic].iloc[0]

# Embed video
st.subheader("▶️ YouTube Video")
if pd.notna(selected_video['video_url']):
    st.video(selected_video['video_url'])
else:
    st.info("No video URL available for this topic.")

# Show sentiment plot
st.subheader("📈 Sentiment Distribution: YouTube vs Reddit")
image_path = "data/sentiment_distribution.png"
if os.path.exists(image_path):
    image = Image.open(image_path)
    st.image(image, caption="KDE Plot of Sentiment Scores", use_container_width=True)
else:
    st.warning("Sentiment plot image not found.")

# Show LLM insight
st.subheader("💡 LLM Summary & Insights")
filtered_llm = llm_df[llm_df['topic'] == selected_topic]

if not filtered_llm.empty:
    st.markdown(filtered_llm['llm_analysis'].values[0])
else:
    st.warning("No insights found for this topic.")
