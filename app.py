import streamlit as st
import trafilatura
import requests

st.set_page_config(page_title="Універсальний читач статей", page_icon="📖", layout="centered")

st.title("📖 Універсальний читач статей")

def clear_text():
    st.session_state["url_input"] = ""

url = st.text_input("Посилання на статтю:", key="url_input", placeholder="https://...")
st.button("Очистити поле", on_click=clear_text)

# Спроба витягнути секретний ключ з Streamlit Secrets або з поля
API_KEY = st.secrets.get("36c0c5c4bef81e270652dc8699e6e1fa", "")

def fetch_via_scraperapi(target_url, api_key):
    """
    Запит через ScraperAPI з увімкненим обходом Cloudflare (render=true)
    """
    payload = {
        'api_key': api_key,
        'url': target_url,
        'render': 'true',  # Обов'язково: рендерить JS і обходить Cloudflare
        'country_code': 'us'
    }
    try:
        response = requests.get('http://api.scraperapi.com', params=payload, timeout=35)
        if response.status_code == 200:
            return response.text
    except Exception as e:
        st.error(f"Помилка запиту: {e}")
    return None

if url:
    with st.spinner("Обходимо Cloudflare та витягуємо статтю..."):
        if not API_KEY:
            st.warning("⚠️ Не знайдено API-ключ ScraperAPI. Спробуємо прямий запит...")
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            try:
                res = requests.get(url, headers=headers, timeout=10)
                html_content = res.text if res.status_code == 200 else None
            except Exception:
                html_content = None
        else:
            html_content = fetch_via_scraperapi(url, API_KEY)

        if html_content and "Attention Required! | Cloudflare" not in html_content:
            metadata = trafilatura.extract_metadata(html_content)
            article_html = trafilatura.extract(
                html_content,
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
                st.error("Текст статті не вдалося розпарсити.")
        else:
            st.error("Сайт заблокував запит (Cloudflare 403). Потрібен робочий ScraperAPI Key.")
