import streamlit as st
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
import os

# --- 設定とタイトル ---
st.set_page_config(page_title="AI Tech News Summarizer", page_icon="🤖")
st.title("🤖 AI Tech News Summarizer")
st.markdown("### 最新の技術記事を3行で要約 & インサイト抽出")

# --- サイドバー: APIキー設定 ---
st.sidebar.header("⚙️ Settings")

# 1. シークレットからキーを取得（設定されていれば）
try:
    api_key_env = st.secrets["OPENAI_API_KEY"]
except:
    api_key_env = None

# 2. シークレットがない場合は入力欄を表示
if api_key_env:
    api_key = api_key_env
    st.sidebar.success("✅ API Key loaded from Secrets")
else:
    api_key = st.sidebar.text_input("OpenAI API Key", type="password", help="ここにOpenAIのAPIキー（sk-...）を入力してください")

if not api_key:
    st.warning("⚠️ 左側のサイドバーにAPIキーを入力すると機能が有効になります")

# --- スクレイピング関数 ---
def get_article_content(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 記事本文の抽出 (pタグを中心に取得)
        paragraphs = soup.find_all('p')
        content = "\n".join([p.get_text() for p in paragraphs])
        
        # 文字数制限（トークン節約のため先頭5000文字）
        if len(content) > 5000:
            content = content[:5000] + "..."
        return content
    except Exception as e:
        return f"Error: {str(e)}"

# --- AI分析関数 ---
def analyze_article_with_ai(content, key):
    client = OpenAI(api_key=key)
    
    prompt = f"""
    以下の技術記事の内容を読み、以下のフォーマットで出力してください。
    
    ## 📝 3行要約
    - (要点1)
    - (要点2)
    - (要点3)

    ## 🛠️ 使用技術・キーワード
    (カンマ区切りで列挙)

    ## 💡 ビジネス・開発への影響
    (一言で簡潔に)

    ## 😊 記事のトーン分析
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

# --- メインUI ---
url = st.text_input("🔗 要約したい記事のURLを入力 (Qiita, Zenn, Techブログ等)", placeholder="https://example.com/article")

if st.button("🚀 AIで分析開始"):
    if not api_key:
        st.error("まずはサイドバーにOpenAI APIキーを入力してください！")
    elif not url:
        st.error("URLを入力してください！")
    else:
        with st.spinner("🔍 記事を読み込んでAIが分析中... (数秒お待ちください)"):
            # 1. 記事取得
            article_text = get_article_content(url)
            
            if "Error:" in article_text:
                st.error(f"記事の取得に失敗しました。\n{article_text}")
            else:
                # 2. AI分析
                result = analyze_article_with_ai(article_text, api_key)
                
                if "AI Error:" in result:
                    st.error(f"AI分析中にエラーが発生しました。\n{result}")
                else:
                    st.success("分析完了！")
                    st.markdown("---")
                    st.markdown(result)

# --- フッター ---
st.markdown("---")
st.caption("Powered by Streamlit & OpenAI API | Developed by You")
