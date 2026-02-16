import streamlit as st
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
import os

# --- ページ設定 ---
st.set_page_config(
    page_title="AI Tech News Summarizer",
    page_icon="🤖",
    layout="centered"
)

# --- カスタムCSS (おしゃれ化) ---
st.markdown("""
<style>
    /* 全体のフォントと背景調整 */
    .stApp {
        background-color: #f8f9fa;
    }
    .main_title {
        font-size: 3em;
        font-weight: bold;
        background: -webkit-linear-gradient(45deg, #007CF0, #00DFD8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 10px;
    }
    .sub_title {
        text-align: center;
        color: #666;
        margin-bottom: 30px;
        font-size: 1.2em;
    }
    /* カード風デザイン */
    .result-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    /* 読み込み中のスピナー */
    .stSpinner > div {
        border-color: #007CF0 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- ヘッダー ---
st.markdown('<div class="main_title">AI Tech News Summarizer</div>', unsafe_allow_html=True)
st.markdown('<div class="sub_title">最新の技術記事を瞬時に要約 & インサイト抽出 🚀</div>', unsafe_allow_html=True)

# --- サイドバー: APIキー設定 ---
with st.sidebar:
    st.header("⚙️ Settings")
    st.markdown("OpenAIのAPIキーを設定してください。")
    
    # 1. シークレットからキーを取得
    try:
        api_key_env = st.secrets["OPENAI_API_KEY"]
    except:
        api_key_env = None

    # 2. キー入力制御
    if api_key_env:
        api_key = api_key_env
        st.success("✅ API Key loaded safely")
    else:
        api_key = st.text_input("API Key", type="password", placeholder="sk-...")
        if not api_key:
            st.warning("⚠️ APIキーを入力してください")
    
    st.markdown("---")
    st.markdown("### 使い方")
    st.markdown("1. 気になる技術記事のURLをコピー\n2. 入力欄にペースト\n3. ボタンを押して分析開始！")

# --- スクレイピング関数 ---
def get_article_content(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 本文抽出ロジック（pタグメイン）
        paragraphs = soup.find_all('p')
        content = "\n".join([p.get_text() for p in paragraphs])
        
        # 不要な空白除去
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
    あなたは優秀な技術コンサルタントです。以下の技術記事を読み、指定されたフォーマットで出力してください。
    出力は必ず日本語で行ってください。

    ## 📝 3行要約
    - (要点1: 簡潔に)
    - (要点2: 簡潔に)
    - (要点3: 簡潔に)

    ## 🛠️ キーワード・技術スタック
    (関連する技術用語を5つ程度、カンマ区切りで)

    ## 💡 ビジネス・開発へのインサイト
    (この記事の内容を実務でどう活かせるか、またはどういう影響があるか、プロの視点で一言)

    ## 😊 記事のトーン
    (ポジティブ / ニュートラル / ネガティブ)

    ---
    記事本文の一部:
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

# --- メインエリア ---
input_container = st.container()

with input_container:
    url = st.text_input("🔗 記事のURLを入力", placeholder="https://zenn.dev/...", help="Web上の技術記事のURLを貼り付けてください")
    analyze_btn = st.button("✨ AIで分析する", type="primary", use_container_width=True)

if analyze_btn:
    if not api_key:
        st.error("まずはサイドバーでAPIキーを設定してください！")
    elif not url:
        st.error("URLを入力してください！")
    else:
        progress_text = "Searching and Analyzing..."
        my_bar = st.progress(0, text=progress_text)

        # 1. スクレイピング
        my_bar.progress(30, text="🔍 記事を取得中...")
        article_text = get_article_content(url)
        
        if "Error:" in article_text:
            my_bar.empty()
            st.error(f"記事の取得に失敗しました。\n{article_text}")
        else:
            # 2. AI分析
            my_bar.progress(70, text="🧠 AIが思考中...")
            result = analyze_article_with_ai(article_text, api_key)
            my_bar.progress(100, text="完了！")
            my_bar.empty()
            
            if "AI Error:" in result:
                st.error(f"AI分析中にエラーが発生しました。\n{result}")
            else:
                st.success("分析が完了しました！")
                
                # 結果表示エリア（カード風）
                st.markdown('<div class="result-card">', unsafe_allow_html=True)
                st.markdown(result)
                st.markdown('</div>', unsafe_allow_html=True)

# --- フッター ---
st.markdown("---")
st.markdown('<div style="text-align: center; color: #aaa; font-size: 0.8em;">Powered by Streamlit & OpenAI | 2024 Portfolio</div>', unsafe_allow_html=True)
