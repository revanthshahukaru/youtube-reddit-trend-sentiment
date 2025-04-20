import streamlit as st
import pandas as pd
import os
from PIL import Image
import re
import time
from openai import OpenAI
from dotenv import load_dotenv

# ========== SETUP ========== #
st.set_page_config(page_title="YouTube & Reddit Sentiment Explorer", layout="wide")

# CSS for layout improvement
st.markdown("""
    <style>
    .block-container {
        max-width: 1000px;
        margin: 0 auto;
        padding: 1rem;
    }
    #llm-summary { scroll-margin-top: 100px; }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Social Media Sentiment Dashboard")
st.markdown("This dashboard compares YouTube and Reddit sentiment for trending topics using NLP and GPT-based analysis.")

# ========== ENV + OPENAI CLIENT ========== #
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ========== Load Files ========== #
yt_path = "../data/youtube_data.csv"
llm_path = "../data/llm_insights.csv"
plot_path = "../data/sentiment_distribution.png"

if not os.path.exists(yt_path) or not os.path.exists(llm_path):
    st.error("🚨 Required data files not found. Please run the YouTube and LLM notebooks to generate them.")
    st.stop()

yt_df = pd.read_csv(yt_path)
llm_df = pd.read_csv(llm_path)
unique_videos = yt_df[['video_title', 'channel', 'video_url']].drop_duplicates()
video_titles = unique_videos['video_title'].tolist()

# ========== Main Interface ========== #
st.subheader("🔥 Trending Topics")
selected_topic = st.selectbox("Select a topic to explore:", video_titles)
selected_video = unique_videos[unique_videos['video_title'] == selected_topic].iloc[0]

# Embedded video
st.subheader("▶️ YouTube Video")
if pd.notna(selected_video['video_url']):
    st.video(selected_video['video_url'])
else:
    st.info("No video URL available for this topic.")

# Sentiment Distribution Plot
st.subheader("📈 Sentiment Distribution")
if os.path.exists(plot_path):
    st.image(Image.open(plot_path), caption="KDE Plot: YouTube vs Reddit", use_container_width=True)
else:
    st.warning("Plot not found.")

# LLM Jump Button
if st.button("💬 View LLM Summary for this Topic"):
    st.markdown("<script>document.getElementById('llm-summary').scrollIntoView({behavior: 'smooth'});</script>", unsafe_allow_html=True)

# LLM Summary
st.markdown('<div id="llm-summary"></div>', unsafe_allow_html=True)
st.subheader("💡 LLM Summary & Insights")
llm_row = llm_df[llm_df['topic'] == selected_topic]
if not llm_row.empty:
    st.markdown(llm_row['llm_analysis'].values[0])
else:
    st.info("No summary available yet for this topic.")

# ========== Custom Trend Search ========== #
st.divider()
st.subheader("🔍 Search Your Own Trend or YouTube Video")

custom_query = st.text_input("Enter a custom topic or video title:")
if st.button("Run Live Analysis") and custom_query:
    with st.spinner("Fetching data from YouTube and Reddit..."):
        # 🔁 Simulate fetch (replace this section with real API logic)
        time.sleep(3)

        yt_comments = ["This is amazing!", "Didn't expect this at all.", "Super helpful and fun."]
        rd_comments = ["Saw this on Reddit too!", "Redditors love it.", "Interesting breakdowns."]

        prompt = f"""
Topic: {custom_query}

YouTube Comments:
{yt_comments}

Reddit Comments:
{rd_comments}
        """

        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You're a sentiment analyst. Provide a summary based on the comments."},
                    {"role": "user", "content": prompt.strip()}
                ]
            )
            llm_result = response.choices[0].message.content
        except Exception as e:
            llm_result = f"⚠️ Error generating summary: {str(e)}"

    st.subheader("💡 Live Summary")
    st.markdown(llm_result)
