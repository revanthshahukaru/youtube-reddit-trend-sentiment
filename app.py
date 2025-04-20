import streamlit as st
import pandas as pd
from PIL import Image
import os
import re
import time
from openai import OpenAI
from dotenv import load_dotenv

# Load API keys
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Page setup
st.set_page_config(page_title="YouTube & Reddit Sentiment Explorer", layout="wide")

# Custom CSS for layout
st.markdown("""
    <style>
    .block-container {
        max-width: 1000px;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar options
view = st.sidebar.radio("Select View", ["📊 Dashboard", "🔍 Reddit Search", "🎥 Combined YouTube + Reddit"])

# Common utility functions
def extract_video_id(url):
    match = re.search(r"v=([^&]+)", url)
    return match.group(1) if match else None

def get_llm_summary(prompt, system_message):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt.strip()}
        ],
        temperature=0.7
    )
    return response.choices[0].message.content

# Main dashboard
if view == "📊 Dashboard":
    st.title("📊 Social Media Sentiment Dashboard")
    st.markdown("This dashboard displays trending topics from YouTube and their sentiment analysis across YouTube and Reddit.")

    # Load data
    os.makedirs("data", exist_ok=True)
    yt_df = pd.read_csv("data/youtube_data.csv")
    llm_df = pd.read_csv("data/llm_insights.csv")

    unique_videos = yt_df[['video_title', 'channel', 'video_url']].drop_duplicates()
    video_titles = unique_videos['video_title'].tolist()

    st.subheader("🔥 Trending Topics")
    selected_topic = st.selectbox("Select a topic to explore insights:", video_titles)
    selected_video = unique_videos[unique_videos['video_title'] == selected_topic].iloc[0]

    st.subheader("▶️ YouTube Video")
    if pd.notna(selected_video['video_url']):
        st.video(selected_video['video_url'])
    else:
        st.info("No video URL available for this topic.")

    st.subheader("💡 LLM Summary & Insights")
    filtered_llm = llm_df[llm_df['topic'] == selected_topic]
    if not filtered_llm.empty:
        st.markdown(filtered_llm['llm_analysis'].values[0], unsafe_allow_html=True)
    else:
        st.warning("No insights found for this topic.")

    st.subheader("📈 Overall Sentiment Distribution: YouTube vs Reddit")
    image_path = "data/sentiment_distribution.png"
    if os.path.exists(image_path):
        image = Image.open(image_path)
        st.image(image, caption="KDE Plot of Sentiment Scores", use_container_width=True)
    else:
        st.warning("Sentiment plot image not found.")

# Reddit search interface
elif view == "🔍 Reddit Search":
    st.title("🔍 Custom Reddit Search")
    query = st.text_input("Enter your search topic:")
    if st.button("Search Reddit") and query:
        from praw import Reddit
        reddit = Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            user_agent="streamlit-app"
        )

        st.info("🔄 Loading posts and comments...")
        post_data = []
        posts = reddit.subreddit("all").search(query, limit=5, time_filter='month')
        post_count = 0
        comment_count = 0

        for post in posts:
            post_count += 1
            post.comments.replace_more(limit=0)
            comments = post.comments[:5]
            for comment in comments:
                comment_count += 1
                post_data.append(f"Post: {post.title}\nComment: {comment.body}\n")
            with st.spinner(f"Loaded {post_count} posts, {comment_count} comments..."):
                time.sleep(0.5)

        full_prompt = "\n".join(post_data)
        system_message = f"You are an assistant summarizing Reddit discussions for the topic: {query}. Give the user useful context, key opinions, and highlight any links or resources from the discussion."
        summary = get_llm_summary(full_prompt, system_message)
        st.subheader("💬 LLM Summary")
        st.markdown(summary, unsafe_allow_html=True)

# Combined YouTube + Reddit Search
elif view == "🎥 Combined YouTube + Reddit":
    st.title("🎥📕 YouTube + Reddit Sentiment Fusion")
    topic_input = st.text_input("Enter a topic to search both platforms:")

    if st.button("Analyze Topic") and topic_input:
        st.info("Searching YouTube and Reddit. Please wait...")
        from youtube_transcript_api import YouTubeTranscriptApi
        from googleapiclient.discovery import build
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

        analyzer = SentimentIntensityAnalyzer()
        youtube = build("youtube", "v3", developerKey=os.getenv("YOUTUBE_API_KEY"))
        yt_comments = []
        request = youtube.search().list(q=topic_input, part="snippet", type="video", maxResults=3)
        response = request.execute()

        for item in response['items']:
            video_id = item['id']['videoId']
            title = item['snippet']['title']
            try:
                transcript = YouTubeTranscriptApi.get_transcript(video_id)
                full_transcript = " ".join([t['text'] for t in transcript])
            except:
                full_transcript = ""
            yt_comments.append(f"YouTube: {title}\nTranscript: {full_transcript[:1000]}\n")

        from praw import Reddit
        reddit = Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            user_agent="streamlit-app"
        )
        reddit_comments = []
        posts = reddit.subreddit("all").search(topic_input, limit=3, time_filter='month')
        for post in posts:
            post.comments.replace_more(limit=0)
            for comment in post.comments[:3]:
                reddit_comments.append(f"Reddit Post: {post.title}\nComment: {comment.body}\n")

        prompt = "\n\n".join(yt_comments + reddit_comments)
        system_message = f"Analyze this topic '{topic_input}' based on YouTube video content and Reddit discussions. Provide key takeaways, sentiment contrast, and link out useful examples if needed."
        result = get_llm_summary(prompt, system_message)

        st.subheader("🧠 Combined LLM Analysis")
        st.markdown(result, unsafe_allow_html=True)
