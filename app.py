import streamlit as st
import trafilatura
import requests

# ----------------------------------------------------------------------
# Налаштування сторінки
# ----------------------------------------------------------------------
st.set_page_config(
    page_title="Універсальний читач статей", 
    page_icon="📖", 
    layout="centered"
)

st.title("📖 Універсальний читач статей")
st.write(
    "Введіть посилання на будь-яку статтю, і застосунок сформує чисту читалку без зайвих блоків."
)

def clear_text():
    st.session_state["url_input"] = ""

url = st.text_input(
    "Посилання на статтю:", key="url_input", placeholder="https://..."
)

st.button("Очистити поле", on_click=clear_text)

# ----------------------------------------------------------------------
# Функція завантаження сторінки з імітацією браузера
# ----------------------------------------------------------------------
def fetch_content(target_url):
    # Спосіб 1: Через requests з повноцінними браузерними заголовками
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7",
    }
    
    try:
        response = requests.get(target_url, headers=headers, timeout=12)
        if response.status_code == 200:
            return response.text
    except Exception:
        pass

    # Спосіб 2: Резервний варіант через саму trafilatura
    return trafilatura.fetch_url(target_url, no_ssl=True)


# ----------------------------------------------------------------------
# Основна логіка
# ----------------------------------------------------------------------
if url:
    with st.spinner("Збираємо текст та зображення..."):
        downloaded = fetch_content(url)

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
                    st.markdown(
                        f"<h1 style='font-size: 26px;'>{metadata.title}</h1>",
                        unsafe_allow_html=True,
                    )

                if metadata and metadata.date:
                    st.caption(f"Дата публікації: {metadata.date}")

                st.divider()
                st.markdown(article_html, unsafe_allow_html=True)

            else:
                st.error(
                    "Не вдалося витягти текст із цієї сторінки. Можливо, сайт використовує складний JavaScript."
                )
        else:
            st.error(
                "Не вдалося завантажити сторінку. Сайт блокує хмарні IP-адреси або посилання недійсне."
            )
