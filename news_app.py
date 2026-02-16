import streamlit as st
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
import os

# --- ページ設定 (ワイドモード) ---
st.set_page_config(
    page_title="AI Info Agent",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed" # サイドバーを隠して没入感を高める
)

# --- 究極のUI (Custom CSS) ---
st.markdown("""
<style>
    /* Google Fonts Import */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;900&display=swap');

    /* 全体設定 */
    .stApp {
        background-color: #050505;
        background-image: 
            radial-gradient(at 50% 0%, #1a1a2e 0px, transparent 50%),
            radial-gradient(at 100% 0%, #290f1e 0px, transparent 50%);
        color: #FFFFFF;
        font-family: 'Inter', sans-serif;
    }

    /* タイトルセクション */
    .hero-container {
        text-align: center;
        padding: 80px 20px 40px 20px;
    }
    .hero-title {
        font-size: 6em;
        font-weight: 900;
        line-height: 1.1;
        background: linear-gradient(135deg, #FFF 30%, #44A6C6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0px 0px 40px rgba(68, 166, 198, 0.4);
        margin: 0;
        letter-spacing: -2px;
    }
    .hero-subtitle {
        font-size: 1.5em;
        color: #888;
        font-weight: 400;
        letter-spacing: 2px;
        margin-top: 10px;
        text-transform: uppercase;
    }

    /* 入力フォームの究極化 */
    .stTextInput > div > div > input {
        background-color: rgba(255, 255, 255, 0.05) !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 12px;
        padding: 20px;
        font-size: 18px;
        transition: all 0.3s;
    }
    .stTextInput > div > div > input:focus {
        border-color: #44A6C6 !important;
        background-color: rgba(255, 255, 255, 0.1) !important;
        box-shadow: 0 0 20px rgba(68, 166, 198, 0.3);
    }

    /* ボタンの究極化 */
    .stButton > button {
        width: 100%;
        background: linear-gradient(90deg, #44A6C6, #005F73);
        color: white;
        border: none;
        padding: 18px;
        font-size: 18px;
        font-weight: 700;
        border-radius: 12px;
        letter-spacing: 1px;
        box-shadow: 0 10px 30px rgba(0, 95, 115, 0.4);
        transition: all 0.3s;
    }
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 40px rgba(0, 95, 115, 0.6);
        color: #fff;
    }

    /* 結果カード */
    .result-section {
        margin-top: 50px;
        background: rgba(20, 20, 30, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 50px;
        backdrop-filter: blur(20px);
    }
    .section-header {
        font-size: 1.2em;
        font-weight: 600;
        color: #44A6C6;
        margin-bottom: 10px;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        border-bottom: 2px solid rgba(68, 166, 198, 0.2);
        padding-bottom: 10px;
        margin-top: 30px;
    }
    .content-text {
        font-size: 1.1em;
        line-height: 1.8;
        color: #E0E0E0;
    }

</style>
""", unsafe_allow_html=True)

# --- メインロジック ---

# HEROセクション
st.markdown("""
<div class="hero-container">
    <div class="hero-title">INTELLIGENCE<br>SUMMARIZER</div>
    <div class="hero-subtitle">Next-Gen Information Processing Agent</div>
</div>
""", unsafe_allow_html=True)

# 入力エリア（中央寄せレイアウト）
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    url = st.text_input("", placeholder="ここにURLをペースト (Paste Article URL Here)", label_visibility="collapsed")
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True) # スペーサー
    analyze_btn = st.button("EXECUTE ANALYSIS", use_container_width=True)

# --- 処理ロジック ---
def get_article_content_v2(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        paragraphs = soup.find_all(['p', 'h2', 'h3']) # Hタグも取得して精度向上
        content = "\n".join([p.get_text() for p in paragraphs])
        return content[:8000] # コンテキスト長を拡張
    except Exception as e:
        return f"Error: {str(e)}"

def analyze_ai_premium(content, key):
    client = OpenAI(api_key=key)
    # プロンプトもプロフェッショナル仕様に
    prompt = f"""
    Analyze the following technical article and generate a structured executive report.

    # 1. CORE INSIGHTS (3 Bullet Points)
    Summarize the most critical takeaways. Focus on "Novelty", "Impact", and "Implementation".

    # 2. TECHNOLOGY RADAR
    List key technologies, libraries, or concepts mentioned.

    # 3. STRATEGIC IMPLICATION
    Explain why this matters for a software engineer or business leader.
    
    (Output in JAPANESE for clarity)
    
    Article Context:
    {content}
    """
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI Error: {str(e)}"

# --- 実行 ---
if analyze_btn:
    # シークレットまたは入力からキー取得
    try:
        api_key = st.secrets["OPENAI_API_KEY"]
    except:
        api_key = st.session_state.get("api_key_input") 
        # (サイドバーを隠したので、もしシークレットがない場合のフォールバックは簡易的に警告)
    
    if not api_key:
        st.error("🔒 ACCESS DENIED: Please configure OpenAI API Key in Secrets.")
    elif not url:
        st.error("⚠️ URL MISSING: Please provide a valid URL.")
    else:
        with st.spinner("🔄 ESTABLISHING UPLINK & ANALYZING DATA..."):
            text = get_article_content_v2(url)
            if "Error" in text:
                st.error(f"CONNECTION FAILED: {text}")
            else:
                result = analyze_ai_premium(text, api_key)
                
                # 結果表示エリア
                st.markdown('<div class="result-section">', unsafe_allow_html=True)
                
                # 結果をセクションごとにパースして表示（簡易パーサー）
                st.markdown(result) # Markdownとして綺麗にレンダリングされるはず
                
                st.markdown('</div>', unsafe_allow_html=True)

# フッター
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("<div style='text-align: center; opacity: 0.3;'>SYSTEM READY ・ v2.0.4 PRO</div>", unsafe_allow_html=True)
