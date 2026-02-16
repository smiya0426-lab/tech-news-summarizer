import streamlit as st
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
import os

# --- ページ設定 ---
st.set_page_config(
    page_title="AI Tech News Summarizer",
    page_icon="⚡",
    layout="wide", # ワイド表示にしてギャラリー感を出す
    initial_sidebar_state="expanded"
)

# --- カスタムCSS (プレミアムダークモード) ---
st.markdown("""
<style>
    /* 全体背景 (ダーク) */
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    
    /* タイトル (HEROセクション風) */
    .hero-title {
        font-family: 'Helvetica Neue', sans-serif;
        font-size: 4em;
        font-weight: 900;
        text-align: center;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-top: 40px;
        margin-bottom: 10px;
        background: -webkit-linear-gradient(90deg, #FFFFFF, #999999);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0px 4px 10px rgba(255, 255, 255, 0.1);
    }
    
    .hero-subtitle {
        font-size: 1.2em;
        text-align: center;
        color: #888;
        letter-spacing: 5px;
        margin-bottom: 60px;
        text-transform: uppercase;
    }

    /* 入力エリアのカスタマイズ */
    .stTextInput > div > div > input {
        background-color: #262730;
        color: white;
        border: 1px solid #444;
        border-radius: 8px;
        padding: 10px;
    }
    
    /* ボタンのカスタマイズ */
    .stButton > button {
        background-color: white;
        color: black;
        border-radius: 30px;
        font-weight: bold;
        padding: 10px 30px;
        border: none;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #ddd;
        transform: scale(1.02);
    }

    /* 結果カード (Glassmorphism) */
    .result-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 40px;
        margin-top: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }
    
    .card-header {
        font-size: 1.5em;
        font-weight: bold;
        margin-bottom: 20px;
        border-bottom: 1px solid #444;
        padding-bottom: 10px;
        color: #fff;
    }
    
    /* サイドバー */
    .css-1d391kg {
        background-color: #111;
    }
</style>
""", unsafe_allow_html=True)

# --- ヘッダーエリア ---
st.markdown('<div class="hero-title">AI NEWS<br>SUMMARIZER</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle">DESIGNED FOR ENGINEERS</div>', unsafe_allow_html=True)

# --- サイドバー ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2583/2583166.png", width=50)
    st.markdown("### ⚡ Control Panel")
    
    # 1. シークレットからキーを取得
    try:
        api_key_env = st.secrets["OPENAI_API_KEY"]
    except:
        api_key_env = None

    if api_key_env:
        api_key = api_key_env
        st.success("API Key Active")
    else:
        api_key = st.text_input("OpenAI API Key", type="password", placeholder="sk-...")
        if not api_key:
            st.warning("Please enter API Key")

# --- メインコンテンツ（中央寄せ） ---
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    url = st.text_input("", placeholder="ここに記事のURLをペーストしてください...", label_visibility="collapsed")
    analyze_btn = st.button("ANALYZE / 分析開始", use_container_width=True)

# --- スクレイピング関数 ---
def get_article_content(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        paragraphs = soup.find_all('p')
        content = "\n".join([p.get_text() for p in paragraphs])
        content = content.replace("\n\n", "\n")
        
        if len(content) > 6000:
            content = content[:6000] + "..."
        return content
    except Exception as e:
        return f"Error: {str(e)}"

# --- AI分析関数 ---
def analyze_article_with_ai(content, key):
    client = OpenAI(api_key=key)
    
    prompt = f"""
    あなたはクリエイティブな技術編集者です。以下の記事を読み、指定されたJSONライクな構造で情報を抽出してください（出力はテキストで構いません）。

    ## ⚡ EXECUTIVE SUMMARY
    (3点に絞った要約)

    ## 🏗️ TECH STACK
    (技術スタックを英語でカンマ区切り)

    ## 🚀 IMPACT & INSIGHT
    (プロフェッショナルな視点でのインサイト)
    
    ---
    記事本文（抜粋）:
    {content}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI Error: {str(e)}"

# --- 結果表示 ---
if analyze_btn:
    if not api_key:
        st.error("⚠️ API Key is missing.")
    elif not url:
        st.error("⚠️ URL is missing.")
    else:
        with st.spinner("Processing..."):
            article_text = get_article_content(url)
            
            if "Error:" in article_text:
                st.error(f"Failed to fetch: {article_text}")
            else:
                result = analyze_article_with_ai(article_text, api_key)
                
                if "AI Error:" in result:
                    st.error(f"AI Failure: {result}")
                else:
                    st.markdown('<div class="result-card">', unsafe_allow_html=True)
                    st.markdown('<div class="card-header">ANALYSIS RESULT</div>', unsafe_allow_html=True)
                    st.markdown(result)
                    st.markdown('</div>', unsafe_allow_html=True)

# --- フッター ---
st.markdown("<br><br><br>", unsafe_allow_html=True)
st.markdown('<div style="text-align: center; color: #444; font-size: 0.8em; letter-spacing: 2px;">DESIGNED BY AI ENGINEER</div>', unsafe_allow_html=True)
