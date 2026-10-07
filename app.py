import streamlit as st
import trafilatura
import requests

st.set_page_config(page_title="Універсальний читач статей", page_icon="📖", layout="centered")

st.title("📖 Універсальний читач статей")
st.write("Введіть посилання на будь-яку статтю, і застосунок сформує чисту читалку без зайвих блоків.")

def clear_text():
    st.session_state["url_input"] = ""

url = st.text_input("Посилання на статтю:", key="url_input", placeholder="https://...")
st.button("Очистити поле", on_click=clear_text)

def fetch_with_jina(target_url):
    """
    Проганяє URL через Jina Reader, який обходить блокування IP та Cloudflare.
    """
    jina_url = f"https://r.jina.ai/{target_url}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "X-No-Cache": "true"
    }
    try:
        response = requests.get(jina_url, headers=headers, timeout=20)
        if response.status_code == 200:
            return response.text
    except Exception:
        pass
    return None

if url:
    with st.spinner("Збираємо текст та зображення..."):
        # 1. Спочатку пробуємо прямий запит
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        downloaded = None
        
        try:
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code == 200:
                downloaded = res.text
        except Exception:
            pass

        # 2. Якщо прямий запит заблоковано, використовуємо обхід через Jina
        if not downloaded:
            downloaded = fetch_with_jina(url)

        if downloaded:
            metadata = trafilatura.extract_metadata(downloaded)
            article_html = trafilatura.extract(
                downloaded,
                include_images=True,
                include_formatting=True,
                output_format="html",
            )

            if article_html:
                st.divider()
                if metadata and metadata.title:
                    st.markdown(f"<h1 style='font-size: 26px;'>{metadata.title}</h1>", unsafe_allow_html=True)
                if metadata and metadata.date:
                    st.caption(f"Дата публікації: {metadata.date}")
                st.divider()
                st.markdown(article_html, unsafe_allow_html=True)
            else:
                # Якщо trafilatura не спарсила HTML від Jina, виводимо сирий текст від Jina
                st.divider()
                st.markdown(downloaded)
        else:
            st.error("На жаль, сайт застосовує жорстке блокування або захист від ботів.")
