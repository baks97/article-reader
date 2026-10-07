import streamlit as st
import trafilatura

# ----------------------------------------------------------------------
# Налаштування сторінки (має бути першою командою Streamlit)
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

# Функція для очищення тексту в session_state
def clear_text():
    st.session_state["url_input"] = ""

# Поле введення посилання
url = st.text_input(
    "Посилання на статтю:", 
    key="url_input", 
    placeholder="https://..."
)

# Кнопка очищення
st.button("Очистити поле", on_click=clear_text)

# ----------------------------------------------------------------------
# Логіка завантаження та витягування тексту
# ----------------------------------------------------------------------
if url:
    with st.spinner("Збираємо текст та зображення..."):
        # Додаємо заголовки, щоб сайти не блокували запити з хмари (Streamlit Cloud)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        # Отримуємо контент через trafilatura
        downloaded = trafilatura.fetch_url(url, no_ssl=True)
        
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

                # Відображення основного вмісту
                st.markdown(article_html, unsafe_allow_html=True)

            else:
                st.error(
                    "Не вдалося витягти текст із цієї сторінки. Можливо, сайт використовує складні скрипти або блокує парсинг."
                )
        else:
            st.error(
                "Не вдалося завантажити сторінку. Перевірте правильність посилання або спробуйте пізніше."
            )
